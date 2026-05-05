"""
Build and persist the BM25F-approximate index and BGE-M3 dense embeddings
from a directory of PDFs that already contain embedded text.
 
Scanned / image-only PDFs (character yield below MIN_CHARS_PER_PAGE) are
skipped and reported at the end.
 
Usage:
    python index_builder.py --pdf-dir ./pdfs --index-dir ./index
"""
 
import argparse
import json
import sys
from pathlib import Path
 
import bm25s
import numpy as np
import pypdf
 
import config
from coordinates import extract_coordinates
from preprocessing import download_nltk_data, process_text
 
 
# ---------------------------------------------------------------------------
# PDF helpers
# ---------------------------------------------------------------------------
 
MIN_CHARS_PER_PAGE = 50  # pages with fewer chars are treated as image-only
 
 
def extract_text_from_pdf(pdf_path: Path) -> tuple[str, bool]:
    """
    Extract all text from a PDF that already contains embedded text.
 
    Returns
    -------
    text : str
        Concatenated text from all pages.
    has_text : bool
        True when at least one page exceeds MIN_CHARS_PER_PAGE characters,
        meaning the PDF is not purely image-based.
    """
    try:
        reader = pypdf.PdfReader(str(pdf_path))
    except Exception as exc:
        print(f"  [WARN] Could not open {pdf_path.name}: {exc}", file=sys.stderr)
        return "", False
 
    page_texts: list[str] = []
    text_page_count = 0
 
    for page in reader.pages:
        page_text = (page.extract_text() or "").strip()
        if len(page_text) >= MIN_CHARS_PER_PAGE:
            text_page_count += 1
        page_texts.append(page_text)
 
    has_text = text_page_count > 0
    full_text = "\n".join(page_texts).strip()
    return full_text, has_text
 
 
def collect_pdf_docs(pdf_dir: Path) -> tuple[list[dict], list[Path]]:
    """
    Walk *pdf_dir* recursively, attempt text extraction from every PDF.
 
    Returns
    -------
    docs : list[dict]
        One entry per text-bearing PDF with keys:
        id, file_rel, file_abs, text.
    skipped : list[Path]
        PDFs that had no extractable text (image-only or corrupt).
    """
    pdf_paths = sorted(pdf_dir.rglob("*.pdf"))
    if not pdf_paths:
        print(f"[ERROR] No PDF files found under {pdf_dir}", file=sys.stderr)
        sys.exit(1)
 
    print(f"Found {len(pdf_paths)} PDF(s) under {pdf_dir}", file=sys.stderr)
 
    docs: list[dict] = []
    skipped: list[Path] = []
 
    for pdf_path in pdf_paths:
        text, has_text = extract_text_from_pdf(pdf_path)
        if not has_text:
            skipped.append(pdf_path)
            print(f"  [SKIP] {pdf_path.name}  (no extractable text)", file=sys.stderr)
            continue
 
        docs.append(
            {
                "id":       len(docs),
                "file_rel": str(pdf_path.relative_to(pdf_dir)),
                "file_abs": str(pdf_path.resolve()),
                "text":     text,
            }
        )
        print(
            f"  [OK]   {pdf_path.name}  ({len(text):,} chars)", file=sys.stderr
        )
 
    return docs, skipped
 
 
# ---------------------------------------------------------------------------
# BM25 index
# ---------------------------------------------------------------------------
 
def build_bm25_index(
    corpus_tokens: list[list[str]],
    index_dir: Path,
) -> None:
    retriever = bm25s.BM25()
    retriever.index(corpus_tokens)
    save_path = index_dir / "bm25_index"
    save_path.mkdir(parents=True, exist_ok=True)
    retriever.save(str(save_path), corpus=corpus_tokens)
    print(f"BM25 index saved to {save_path}", file=sys.stderr)
 
 
# ---------------------------------------------------------------------------
# BGE-M3 embeddings
# ---------------------------------------------------------------------------
 
def build_embeddings(
    texts: list[str],
    index_dir: Path,
    model_name: str,
    batch_size: int,
) -> None:
    print(f"Loading BGE-M3 model '{model_name}' ...", file=sys.stderr)

    from sentence_transformers import SentenceTransformer
    import torch

    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = SentenceTransformer(model_name, device=device)

    print(f"Encoding {len(texts)} documents in batches of {batch_size} ...", file=sys.stderr)

    vectors = model.encode(
        texts,
        batch_size=batch_size,
        show_progress_bar=True,
        convert_to_numpy=True,
        normalize_embeddings=True  # important for retrieval!
    ).astype(np.float32)

    embed_path = index_dir / "embeddings.npy"
    np.save(str(embed_path), vectors)

    print(f"Embeddings saved to {embed_path}  shape={vectors.shape}", file=sys.stderr)
 
# ---------------------------------------------------------------------------
# Main build routine
# ---------------------------------------------------------------------------
 
def build_index(pdf_dir: Path, index_dir: Path, use_embeddings: bool) -> None:
    index_dir.mkdir(parents=True, exist_ok=True)
 
    # --- Collect text-bearing PDFs ---
    docs, skipped = collect_pdf_docs(pdf_dir)
 
    if not docs:
        print("[ERROR] No text-bearing PDFs found. Aborting.", file=sys.stderr)
        sys.exit(1)
 
    # Persist doc store (without the raw text to keep it lightweight)
    doc_store = [
        {**{k: v for k, v in doc.items() if k != "text"}, "coordinates": extract_coordinates(doc["text"])}
        for doc in docs
    ]
    doc_store_path = index_dir / "doc_store.json"
    with open(doc_store_path, "w", encoding="utf-8") as f:
        json.dump(doc_store, f, ensure_ascii=False, indent=2)
    print(
        f"Doc store saved to {doc_store_path}  ({len(doc_store)} entries)",
        file=sys.stderr,
    )
 
    # Persist skipped-file list for auditing
    if skipped:
        skipped_path = index_dir / "skipped_pdfs.txt"
        skipped_path.write_text(
            "\n".join(str(p) for p in skipped), encoding="utf-8"
        )
        print(
            f"Skipped {len(skipped)} image-only PDF(s) — see {skipped_path}",
            file=sys.stderr,
        )
 
    texts = [doc["text"] for doc in docs]

    texts_path = index_dir / "texts.json"
    with open(texts_path, "w", encoding="utf-8") as f:
        json.dump(texts, f, ensure_ascii=False)
    print(f"Raw texts saved to {texts_path}", file=sys.stderr)

    # --- BM25 ---
    print("Preprocessing documents for BM25 ...", file=sys.stderr)
    corpus_tokens: list[list[str]] = []
    for doc, t in zip(docs, texts):
        filename_text = Path(doc["file_rel"]).stem.replace("_", " ").replace("-", " ")
        corpus_tokens.append(
            process_text(filename_text, config.NER_MODEL)
            + process_text(t, config.NER_MODEL, config.NER_BOOST_TYPES, config.NER_BOOST_FACTOR)
        )
 
    build_bm25_index(corpus_tokens, index_dir)
 
    corpus_path = index_dir / "bm25_index" / "corpus_tokens.json"
    with open(corpus_path, "w", encoding="utf-8") as f:
        json.dump(corpus_tokens, f, ensure_ascii=False)
    print(f"Tokenized corpus saved to {corpus_path}", file=sys.stderr)
 
    # --- BGE-M3 ---
    if use_embeddings:
        print("Building dense embeddings ...", file=sys.stderr)
        build_embeddings(texts, index_dir, config.BGE_MODEL_NAME, config.BGE_BATCH_SIZE)
    else:
        print("Skipping dense embeddings (BM25 only mode)", file=sys.stderr)
 
    print(
        f"\nIndex build complete.  {len(docs)} document(s) indexed, "
        f"{len(skipped)} skipped.",
        file=sys.stderr,
    )
 
 
# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
 
def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Build BM25 + BGE-M3 index from text-bearing PDFs."
    )
    p.add_argument(
        "--pdf-dir",
        type=Path,
        default=getattr(config, "PDF_DIR", Path("./pdfs")),
        help="Directory (searched recursively) containing PDF files",
    )
    p.add_argument(
        "--index-dir",
        type=Path,
        default=config.INDEX_DIR,
        help="Directory to store index files",
    )   
    p.add_argument(
        "--use-embeddings",
        action="store_true",
        help="Build dense embeddings (BGE-M3) in addition to BM25",
    )
    return p.parse_args()
 
 
if __name__ == "__main__":
    download_nltk_data()
    args = parse_args()
    build_index(args.pdf_dir, args.index_dir, args.use_embeddings)
 