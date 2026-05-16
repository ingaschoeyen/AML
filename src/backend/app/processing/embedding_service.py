from pathlib import Path
import os
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer
from langchain_text_splitters import RecursiveCharacterTextSplitter


class VisualEmbedder:
    def __init__(self, params: dict | None = None):
        self.params = params or {}
        self.model = None
        print("Visual embedding model placeholder initialized")


class SemanticEmbedder:
    def __init__(
        self,
        model_name: str = "clips/e5-small-trm-nl",
        recursive: bool = True,
        merge_type: str = "mean",
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
    ):
        self.model_name = model_name
        self.recursive = recursive
        self.merge_type = merge_type
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

        self.model = SentenceTransformer(model_name)
        self.text_df: pd.DataFrame | None = None
        self.embeddings_df: pd.DataFrame | None = None
        self.missing_text_file_ids: list[str] = []

        print(f"Embedding model loaded: {model_name}")

    def load_files(self, path_to_csv: str | Path) -> pd.DataFrame:
        path_to_csv = Path(path_to_csv)

        if not path_to_csv.exists():
            raise FileNotFoundError(f"Text CSV not found: {path_to_csv}")

        df_in = pd.read_csv(path_to_csv)

        required_columns = {"file_id", "file_name", "raw_text"}
        missing_columns = required_columns - set(df_in.columns)

        if missing_columns:
            raise ValueError(
                f"Missing required columns in {path_to_csv}: {missing_columns}"
            )

        print(f"Number of rows in original dataframe: {len(df_in)}")

        df_no_na = df_in.dropna(subset=["raw_text"]).copy()
        df_no_na = df_no_na[df_no_na["raw_text"].astype(str).str.strip() != ""]

        df_na = df_in[~df_in.index.isin(df_no_na.index)].copy()

        print(f"Number of rows with raw_text: {len(df_no_na)}")
        print(f"Number of rows without raw_text: {len(df_na)}")

        self.missing_text_file_ids = df_na["file_id"].dropna().astype(str).tolist()

        df_no_na["text_sep"] = df_no_na["raw_text"].apply(
            lambda x: " ".join(str(x).splitlines()).strip()
        )

        grouped = (
            df_no_na[["file_id", "file_name", "text_sep"]]
            .groupby(["file_id", "file_name"], as_index=False)["text_sep"]
            .apply(list)
            .reset_index(drop=True)
        )

        self.text_df = grouped
        return grouped

    def _encode_text(self, text: str) -> np.ndarray:
        return self.model.encode(text, convert_to_numpy=True)

    def _embed_pages_without_recursive_chunking(self, pages: list[str]) -> list[np.ndarray]:
        return [self._encode_text(page) for page in pages if page.strip()]

    def _embed_pages_with_recursive_chunking(self, pages: list[str]) -> list[np.ndarray]:
        chunker = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
        )

        page_embeddings = []

        for page in pages:
            if not page.strip():
                continue

            chunks = chunker.split_text(page)

            if not chunks:
                continue

            chunk_embeddings = [self._encode_text(chunk) for chunk in chunks]
            page_embedding = self.merge_embeddings(chunk_embeddings)
            page_embeddings.append(page_embedding)

        return page_embeddings

    def merge_embeddings(self, embeddings: list[np.ndarray]) -> np.ndarray:
        if not embeddings:
            raise ValueError("Cannot merge empty embeddings list.")

        embeddings_array = np.vstack(embeddings)

        if self.merge_type == "mean":
            return np.mean(embeddings_array, axis=0)

        if self.merge_type == "max":
            return np.max(embeddings_array, axis=0)

        if self.merge_type == "min":
            return np.min(embeddings_array, axis=0)

        if self.merge_type == "weighted":
            raise NotImplementedError("Weighted merge not implemented yet.")

        raise ValueError(f"Invalid merge type: {self.merge_type}")

    def create_embeddings_from_dataframe(self, text_df: pd.DataFrame) -> pd.DataFrame:
        rows = []

        for _, row in text_df.iterrows():
            file_id = row["file_id"]
            file_name = row["file_name"]
            pages = row["text_sep"]

            if self.recursive:
                page_embeddings = self._embed_pages_with_recursive_chunking(pages)
            else:
                page_embeddings = self._embed_pages_without_recursive_chunking(pages)

            if not page_embeddings:
                continue

            file_embedding = self.merge_embeddings(page_embeddings)

            rows.append(
                {
                    "file_id": file_id,
                    "file_name": file_name,
                    "page_embedding": page_embeddings,
                    "file_embedding": file_embedding,
                    "embedding_model": self.model_name,
                    "merge_type": self.merge_type,
                }
            )

        self.embeddings_df = pd.DataFrame(rows)
        return self.embeddings_df

    def create_embeddings_from_csv(self, path_to_text: str | Path) -> pd.DataFrame:
        text_df = self.load_files(path_to_text)
        return self.create_embeddings_from_dataframe(text_df)

    def save_embeddings(self, output_dir: str | Path, file_type: str = "pkl") -> None:
        if self.embeddings_df is None:
            raise ValueError("No embeddings found. Run create_embeddings_from_csv() first.")

        if self.text_df is None:
            raise ValueError("No text dataframe found. Run load_files() first.")

        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        if file_type == "pkl":
            self.embeddings_df.to_pickle(output_dir / "embeddings.pkl")
            self.text_df.to_pickle(output_dir / "embedded_text.pkl")

        elif file_type == "csv":
            csv_df = self.embeddings_df.copy()
            csv_df["page_embedding"] = csv_df["page_embedding"].apply(
                lambda vectors: [vector.tolist() for vector in vectors]
            )
            csv_df["file_embedding"] = csv_df["file_embedding"].apply(
                lambda vector: vector.tolist()
            )

            csv_df.to_csv(output_dir / "embeddings.csv", index=False)
            self.text_df.to_csv(output_dir / "embedded_text.csv", index=False)

        else:
            raise ValueError("file_type must be either 'pkl' or 'csv'.")

    def run_from_csv(
        self,
        path_to_text: str | Path,
        output_dir: str | Path,
        file_type: str = "pkl",
    ) -> pd.DataFrame:
        embeddings_df = self.create_embeddings_from_csv(path_to_text)
        self.save_embeddings(output_dir, file_type=file_type)
        return embeddings_df


if __name__ == "__main__":
    embedder = SemanticEmbedder(
        model_name="clips/e5-small-trm-nl",
        recursive=True,
        merge_type="mean",
        chunk_size=1000,
        chunk_overlap=200,
    )

    embeddings = embedder.run_from_csv(
        path_to_text="../../../../results/page_extraction.csv",
        output_dir="../../../../results",
        file_type="pkl",
    )

    print(f"Created embeddings for {len(embeddings)} files.")