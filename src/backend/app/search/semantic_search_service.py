"""
Load persisted indexes and run BM25, semantic, or hybrid search.
"""

import json
import sys
from pathlib import Path
import bm25s
import numpy as np

from app.search import config
from app.processing.text_preprocessing_service import process_text
from app.search.coordinates import rd_distance


def _matches_coord_filter(
    doc: dict,
    road: str | None,
    hm: float | None,
    hm_radius: float,
    place_x: int | None,
    place_y: int | None,
    place_radius: float,
    file_type: str | None = None,
    file_name: str | None = None,
    year_from: int | None = None,
    year_to: int | None = None,
) -> bool:
    """Return True when the doc passes all active filters."""
    if file_type is not None and doc.get("file_type", "").lower() != file_type.lower():
        return False

    if file_name is not None and file_name.lower() not in doc.get("file_name", "").lower():
        return False

    if year_from is not None or year_to is not None:
        years = doc.get("years", [])
        if not years:
            return False
        lo = year_from if year_from is not None else 0
        hi = year_to if year_to is not None else 9999
        if not any(lo <= y <= hi for y in years):
            return False

    coords = doc.get("coordinates", {})

    if road is not None:
        refs = coords.get("road_refs", [])
        if not any(
            ref["road"].upper() == road.upper()
            and (hm is None or ref["hm"] is None or abs(ref["hm"] - hm) <= hm_radius)
            for ref in refs
        ):
            return False

    if place_x is not None:
        rd_pts = coords.get("rd_coords", [])
        if not any(rd_distance(place_x, place_y, p["x"], p["y"]) <= place_radius for p in rd_pts):
            return False

    return True


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _cosine_similarity(query_vec: np.ndarray, matrix: np.ndarray) -> np.ndarray:
    """Return cosine similarity between a query vector and every row in matrix."""
    q = query_vec / (np.linalg.norm(query_vec) + 1e-10)
    norms = np.linalg.norm(matrix, axis=1, keepdims=True) + 1e-10
    return (matrix / norms) @ q


def rrf_fuse(ranked_lists: list[list[int]], k: int = config.RRF_K) -> list[int]:
    """
    Reciprocal Rank Fusion.

    Each element of ranked_lists is an ordered list of doc IDs (best first).
    Returns a merged list of doc IDs sorted by descending RRF score.
    """
    scores: dict[int, float] = {}
    for ranking in ranked_lists:
        for rank, doc_id in enumerate(ranking):
            scores[doc_id] = scores.get(doc_id, 0.0) + 1.0 / (k + rank + 1)
    return sorted(scores, key=lambda d: scores[d], reverse=True)


# ---------------------------------------------------------------------------
# Searcher
# ---------------------------------------------------------------------------

class Searcher:
    def __init__(self, index_dir: Path) -> None:
        index_dir = Path(index_dir)

        # Doc store
        with open(index_dir / "doc_store.json", encoding="utf-8") as f:
            self._doc_store: list[dict] = json.load(f)

        # BM25 index + tokenized corpus
        # corpus_path = index_dir / "bm25_index" / "corpus_tokens.json"
        # with open(corpus_path, encoding="utf-8") as f:
        #     self._corpus_tokens: list[list[str]] = json.load(f)

        # self._bm25 = bm25s.BM25.load(str(index_dir / "bm25_index"), load_corpus=False)

        self._bm25 = None
        self._corpus_tokens = None

        bm25_dir = index_dir / "bm25_index"
        corpus_path = bm25_dir / "corpus_tokens.json"

        if bm25_dir.exists() and corpus_path.exists():
            with open(corpus_path, encoding="utf-8") as f:
                self._corpus_tokens = json.load(f)

            self._bm25 = bm25s.BM25.load(str(bm25_dir), load_corpus=False)

        # Raw texts for snippet extraction
        texts_path = index_dir / "texts.json"
        if texts_path.exists():
            with open(texts_path, encoding="utf-8") as f:
                self._texts: list[str] | None = json.load(f)
        else:
            self._texts = None

        # BGE-M3 embeddings (loaded lazily on first semantic search)
        self._embed_path = index_dir / "embeddings.npy"
        self._embeddings: np.ndarray | None = None
        self._bge_model = None

    # ------------------------------------------------------------------
    # Internal loaders
    # ------------------------------------------------------------------

    def _load_embeddings(self) -> np.ndarray:
        if self._embeddings is None:
            self._embeddings = np.load(str(self._embed_path)).astype(np.float32)
        return self._embeddings

    def _load_bge_model(self):
        if self._bge_model is None:
            print("Loading BGE-M3 model for query encoding ...", file=sys.stderr)
            from sentence_transformers import SentenceTransformer
            import torch
            device = "cuda" if torch.cuda.is_available() else "cpu"
            self._bge_model = SentenceTransformer(config.BGE_MODEL_NAME, device=device)
        return self._bge_model

    # ------------------------------------------------------------------
    # Snippet extraction
    # ------------------------------------------------------------------

    def _extract_snippets(
        self,
        doc_id: int,
        query_terms: list[str],
        window: int = 120,
        max_snippets: int = 3,
    ) -> list[str]:
        if self._texts is None or doc_id >= len(self._texts):
            return []
        text = self._texts[doc_id]
        text_lower = text.lower()
        # Find hit positions for any query term
        positions: list[int] = []
        for term in query_terms:
            term_lower = term.lower()
            start = 0
            while True:
                pos = text_lower.find(term_lower, start)
                if pos == -1:
                    break
                positions.append(pos)
                start = pos + 1
        if not positions:
            return []
        positions.sort()
        # Merge overlapping windows
        merged: list[tuple[int, int]] = []
        for pos in positions:
            lo = max(0, pos - window)
            hi = min(len(text), pos + len(query_terms[0]) + window)
            if merged and lo <= merged[-1][1]:
                merged[-1] = (merged[-1][0], max(merged[-1][1], hi))
            else:
                merged.append((lo, hi))
        snippets = []
        for lo, hi in merged[:max_snippets]:
            prefix = "…" if lo > 0 else ""
            suffix = "…" if hi < len(text) else ""
            snippets.append(prefix + text[lo:hi].strip() + suffix)
        return snippets

    # ------------------------------------------------------------------
    # BM25 search
    # ------------------------------------------------------------------

    def _search_bm25_inner(
        self,
        tokens: list[str],
        top_k: int,
        road, hm, hm_radius, place_x, place_y, place_radius,
        file_type, file_name, year_from, year_to,
    ) -> list[dict]:
        k = min(top_k, len(self._doc_store))
        k = max(1, k - 1)
        results, scores = self._bm25.retrieve([tokens], k=k)
        output = []
        for doc_id, s in zip(results[0], scores[0]):
            if not _matches_coord_filter(self._doc_store[doc_id], road, hm, hm_radius, place_x, place_y, place_radius, file_type, file_name, year_from, year_to):
                continue
            output.append({
                **self._doc_store[doc_id],
                "rank": len(output) + 1,
                "score": round(float(s), 6),
                "snippets": self._extract_snippets(doc_id, tokens),
            })
            if len(output) >= top_k:
                break
        return output

    def search_bm25(
        self,
        query: str,
        top_k: int = config.DEFAULT_TOP_K,
        road: str | None = None,
        hm: float | None = None,
        hm_radius: float = 1.0,
        place_x: int | None = None,
        place_y: int | None = None,
        place_radius: float = 2000.0,
        file_type: str | None = None,
        file_name: str | None = None,
        year_from: int | None = None,
        year_to: int | None = None,
    ) -> list[dict]:
        if self._bm25 is None or self._corpus_tokens is None:
            raise ValueError("BM25 index is not available. Build BM25 index first or use mode='semantic'.")
        tokens = process_text(query, config.NER_MODEL, config.NER_BOOST_TYPES, config.NER_BOOST_FACTOR)
        if not tokens:
            return []
        return self._search_bm25_inner(tokens, top_k, road, hm, hm_radius, place_x, place_y, place_radius, file_type, file_name, year_from, year_to)

    # ------------------------------------------------------------------
    # Semantic search
    # ------------------------------------------------------------------

    def _search_semantic_inner(
        self,
        query_vec: np.ndarray,
        tokens: list[str],
        top_k: int,
        road, hm, hm_radius, place_x, place_y, place_radius,
        file_type, file_name, year_from, year_to,
    ) -> list[dict]:
        embeddings = self._load_embeddings()
        if embeddings.shape[1] != query_vec.shape[0]:
            raise ValueError(f"Dimension mismatch: docs={embeddings.shape[1]}, query={query_vec.shape[0]}")
        sims = _cosine_similarity(query_vec, embeddings)
        ranked_indices = np.argsort(sims)[::-1]
        output = []
        for idx in ranked_indices:
            doc_id = int(idx)
            if not _matches_coord_filter(self._doc_store[doc_id], road, hm, hm_radius, place_x, place_y, place_radius, file_type, file_name, year_from, year_to):
                continue
            output.append({
                **self._doc_store[doc_id],
                "rank": len(output) + 1,
                "score": round(float(sims[idx]), 6),
                "snippets": self._extract_snippets(doc_id, tokens),
            })
            if len(output) >= top_k:
                break
        return output

    def search_semantic(
        self,
        query: str,
        top_k: int = config.DEFAULT_TOP_K,
        road: str | None = None,
        hm: float | None = None,
        hm_radius: float = 1.0,
        place_x: int | None = None,
        place_y: int | None = None,
        place_radius: float = 2000.0,
        file_type: str | None = None,
        file_name: str | None = None,
        year_from: int | None = None,
        year_to: int | None = None,
    ) -> list[dict]:
        model = self._load_bge_model()
        tokens = process_text(query, config.NER_MODEL, config.NER_BOOST_TYPES, config.NER_BOOST_FACTOR)
        query_vec: np.ndarray = model.encode(
            [query], batch_size=1, normalize_embeddings=True, convert_to_numpy=True
        )[0].astype(np.float32)
        return self._search_semantic_inner(query_vec, tokens, top_k, road, hm, hm_radius, place_x, place_y, place_radius, file_type, file_name, year_from, year_to)

    # ------------------------------------------------------------------
    # Hybrid search (BM25 + semantic, fused via RRF)
    # ------------------------------------------------------------------

    def search_hybrid(
        self,
        query: str,
        top_k: int = config.DEFAULT_TOP_K,
        road: str | None = None,
        hm: float | None = None,
        hm_radius: float = 1.0,
        place_x: int | None = None,
        place_y: int | None = None,
        place_radius: float = 2000.0,
        file_type: str | None = None,
        file_name: str | None = None,
        year_from: int | None = None,
        year_to: int | None = None,
    ) -> list[dict]:
        if self._bm25 is None:
            raise ValueError("Hybrid search requires BM25 index. Use mode='semantic' for now.")

        # Compute tokens and query vector once for both retrieval paths
        tokens = process_text(query, config.NER_MODEL, config.NER_BOOST_TYPES, config.NER_BOOST_FACTOR)
        model = self._load_bge_model()
        query_vec: np.ndarray = model.encode(
            [query], batch_size=1, normalize_embeddings=True, convert_to_numpy=True
        )[0].astype(np.float32)

        pool = min(top_k * 5, len(self._doc_store))

        bm25_results = self._search_bm25_inner(tokens, pool, road, hm, hm_radius, place_x, place_y, place_radius, file_type, file_name, year_from, year_to)
        sem_results  = self._search_semantic_inner(query_vec, tokens, pool, road, hm, hm_radius, place_x, place_y, place_radius, file_type, file_name, year_from, year_to)

        bm25_ids = [r["id"] for r in bm25_results]
        sem_ids  = [r["id"] for r in sem_results]

        fused_ids = rrf_fuse([bm25_ids, sem_ids])[:top_k]

        bm25_score = {r["id"]: r["score"] for r in bm25_results}
        sem_score  = {r["id"]: r["score"] for r in sem_results}
        bm25_rank  = {doc_id: i for i, doc_id in enumerate(bm25_ids)}
        sem_rank   = {doc_id: i for i, doc_id in enumerate(sem_ids)}

        rrf_k = config.RRF_K
        output = []
        for doc_id in fused_ids:
            entry = dict(self._doc_store[doc_id])
            entry["rank"]       = len(output) + 1
            entry["score_bm25"] = round(bm25_score.get(doc_id, 0.0), 6)
            entry["score_sem"]  = round(sem_score.get(doc_id, 0.0), 6)
            entry["score"]      = round(
                (1.0 / (rrf_k + bm25_rank[doc_id] + 1) if doc_id in bm25_rank else 0.0)
                + (1.0 / (rrf_k + sem_rank[doc_id] + 1) if doc_id in sem_rank else 0.0),
                8,
            )
            entry["snippets"] = self._extract_snippets(doc_id, tokens)
            output.append(entry)

        return output
