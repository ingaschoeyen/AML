from pathlib import Path
import json

import numpy as np
import pandas as pd

from app.search.coordinates import extract_coordinates


class IndexBuilderService:
    def build_index(
        self,
        extraction_csv_path: str | Path,
        embeddings_pkl_path: str | Path,
        index_dir: str | Path,
    ) -> dict:
        extraction_csv_path = Path(extraction_csv_path)
        embeddings_pkl_path = Path(embeddings_pkl_path)
        index_dir = Path(index_dir)

        if not extraction_csv_path.exists():
            raise FileNotFoundError(f"Extraction CSV not found: {extraction_csv_path}")

        if not embeddings_pkl_path.exists():
            raise FileNotFoundError(f"Embeddings file not found: {embeddings_pkl_path}")

        index_dir.mkdir(parents=True, exist_ok=True)

        extraction_df = pd.read_csv(extraction_csv_path)
        embeddings_df = pd.read_pickle(embeddings_pkl_path)

        doc_store = []
        texts = []
        vectors = []

        for idx, row in embeddings_df.iterrows():
            file_id = row["file_id"]

            file_rows = extraction_df[extraction_df["file_id"] == file_id]

            if file_rows.empty:
                continue

            full_text = " ".join(
                file_rows["raw_text"]
                .dropna()
                .astype(str)
                .tolist()
            )

            first_row = file_rows.iloc[0]

            doc_store.append(
                {
                    "id": len(doc_store),
                    "file_id": file_id,
                    "file_name": row.get("file_name", first_row.get("file_name", "")),
                    "file_type": first_row.get("file_type", ""),
                    "source_path": first_row.get("source_path", ""),
                    "page_count": int(file_rows["page_number"].nunique())
                    if "page_number" in file_rows.columns
                    else None,
                    "coordinates": extract_coordinates(full_text),
                }
            )

            texts.append(full_text)
            vectors.append(np.asarray(row["file_embedding"], dtype=np.float32))

        with open(index_dir / "doc_store.json", "w", encoding="utf-8") as f:
            json.dump(doc_store, f, ensure_ascii=False, indent=2)

        with open(index_dir / "texts.json", "w", encoding="utf-8") as f:
            json.dump(texts, f, ensure_ascii=False, indent=2)

        np.save(index_dir / "embeddings.npy", np.vstack(vectors))

        return {
            "index_dir": str(index_dir),
            "documents_indexed": len(doc_store),
            "vectors_indexed": len(vectors),
        }