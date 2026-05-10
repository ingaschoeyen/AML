from pathlib import Path
from datetime import datetime
import pandas as pd


class FileClassifier:
    SUPPORTED_EXTENSIONS = {
        ".pdf", ".doc", ".docx",
        ".jpg", ".jpeg", ".png", ".tif", ".tiff", ".bmp"
    }

    def __init__(self, root_folder: str | Path):
        self.root = Path(root_folder)

        if not self.root.exists():
            raise FileNotFoundError(f"Root folder does not exist: {self.root}")

        if not self.root.is_dir():
            raise NotADirectoryError(f"Root path is not a directory: {self.root}")

    def discover_files(self) -> pd.DataFrame:
        rows = []
        file_counter = 1

        for path in self.root.rglob("*"):
            if not path.is_file():
                continue

            extension = path.suffix.lower()

            if extension not in self.SUPPORTED_EXTENSIONS:
                continue

            row = self._build_file_row(path, file_counter)
            if row is not None:
                rows.append(row)
                file_counter += 1

        df = pd.DataFrame(rows)

        if not df.empty:
            df = df.sort_values(
                by=["asset_folder", "relative_path"]
            ).reset_index(drop=True)

        return df

    def _get_file_type(self, extension: str) -> str:
        if extension == ".pdf":
            return "pdf"
        if extension in {".jpg", ".jpeg", ".png", ".tif", ".tiff", ".bmp"}:
            return "image"
        if extension == ".docx":
            return "docx"
        if extension == ".doc":
            return "doc"
        return "other"

    def _build_file_row(self, path: Path, file_counter: int) -> dict | None:
        try:
            stat = path.stat()
        except OSError as e:
            print(f"Could not read metadata for {path}: {e}")
            return None

        relative_path = path.relative_to(self.root)
        parts = relative_path.parts
        extension = path.suffix.lower()

        folder_parts = parts[:-1]
        folder_parts_lower = [p.lower() for p in folder_parts]

        return {
            "file_id": f"file_{file_counter:06d}",
            "file_name": path.name,
            "file_stem": path.stem,
            "extension": extension,
            "full_path": str(path.resolve()),
            "relative_path": str(relative_path),

            "asset_folder": parts[0] if len(parts) > 0 else "",
            "parent_folder": path.parent.name,
            "folder_depth": len(folder_parts),
            "folder_path_only": str(Path(*folder_parts)) if folder_parts else "",
            "in_doc_folder": "doc" in folder_parts_lower,
            "in_foto_folder": "foto" in folder_parts_lower,

            "file_size_bytes": stat.st_size,
            "modified_time": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "created_time": datetime.fromtimestamp(stat.st_ctime).isoformat(),

            "file_type": self._get_file_type(extension),
            "is_pdf": extension == ".pdf",
            "is_image": extension in {".jpg", ".jpeg", ".png", ".tif", ".tiff", ".bmp"},
            "is_word": extension in {".doc", ".docx"},
        }