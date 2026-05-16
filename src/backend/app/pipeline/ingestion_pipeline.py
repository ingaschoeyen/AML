import pandas as pd
from pathlib import Path
from app.ingestion.content_extraction_service import ContentExtractor
from app.ingestion.file_classifier_service import FileClassifier
from app.ingestion.inventory_tracking_service import InventoryTrackingService
from app.storage.csv_repository import CSVRepository
from app.processing.embedding_service import SemanticEmbedder
from app.processing.index_builder_service import IndexBuilderService

class IngestionPipeline:
    def __init__(
        self,
        root_folder: str | Path,
        output_dir: str | Path = "results",
        tesseract_cmd: str | None = None,
        min_direct_text_length: int = 30,
    ):
        self.root_folder = Path(root_folder)
        self.output_dir = Path(output_dir)
        self.tesseract_cmd = tesseract_cmd
        self.min_direct_text_length = min_direct_text_length
        self.csv_repository = CSVRepository()
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def run(self) -> dict:
        inventory_path = self.output_dir / "inventory.csv"
        extraction_path = self.output_dir / "page_extraction.csv"
        embeddings_path = self.output_dir / "embeddings.pkl"

        classifier = FileClassifier(self.root_folder)
        inventory_df = classifier.discover_files()

        print("=== DEBUG ===")
        print("Root folder:", self.root_folder.resolve())
        print("Output dir:", self.output_dir.resolve())
        print("Inventory path:", inventory_path.resolve())
        print("Inventory exists BEFORE compare:", inventory_path.exists())
        print("Current discovered files:", len(inventory_df))

        tracker = InventoryTrackingService(inventory_path)
        changes = tracker.compare(inventory_df)

        files_to_process = pd.concat(
            [changes["new_files"], changes["modified_files"]],
            ignore_index=True
        )

        print("New:", len(changes["new_files"]))
        print("Modified:", len(changes["modified_files"]))
        print("Deleted:", len(changes["deleted_files"]))
        print("Unchanged:", len(changes["unchanged_files"]))
        print("Files to process:", len(files_to_process))

        # Save inventory ONLY AFTER comparison
        self.csv_repository.save_inventory(inventory_df, inventory_path)

        if files_to_process.empty:
            return {
                "status": "completed",
                "message": "No file changes detected. File extraction component skipped.",
                "inventory_path": str(inventory_path),
                "extraction_path": str(extraction_path),
                "files_discovered": len(inventory_df),
                "files_processed": 0,
                "pages_extracted": 0,
                "new_files": len(changes["new_files"]),
                "modified_files": len(changes["modified_files"]),
                "deleted_files": len(changes["deleted_files"]),
                "unchanged_files": len(changes["unchanged_files"]),
            }

        extractor = ContentExtractor(
            min_direct_text_length=self.min_direct_text_length,
            tesseract_cmd=self.tesseract_cmd,
        )

        extraction_df = extractor.process_inventory(files_to_process)
        self.csv_repository.save_extraction(extraction_df, extraction_path)

        embedder = SemanticEmbedder(
            model_name="clips/e5-small-trm-nl",
            recursive=True,
            merge_type="mean",
            chunk_size=1000,
            chunk_overlap=200,
        )

        embeddings_df = embedder.run_from_csv(
            path_to_text=extraction_path,
            output_dir=self.output_dir,
            file_type="pkl",
        )

        index_builder = IndexBuilderService()
        index_result = index_builder.build_index(
            extraction_csv_path=extraction_path,
            embeddings_pkl_path=self.output_dir / "embeddings.pkl",
            index_dir=self.output_dir / "index",
        )

        return {
            "status": "completed",
            "message": "Extraction completed.",
            "inventory_path": str(inventory_path),
            "extraction_path": str(extraction_path),
            "files_discovered": len(inventory_df),
            "files_processed": len(files_to_process),
            "pages_extracted": len(extraction_df),
            "new_files": len(changes["new_files"]),
            "modified_files": len(changes["modified_files"]),
            "deleted_files": len(changes["deleted_files"]),
            "unchanged_files": len(changes["unchanged_files"]),
            "embeddings_path": str(embeddings_path),
            "embeddings_created": len(embeddings_df),
            "index_dir": index_result["index_dir"],
            "documents_indexed": index_result["documents_indexed"],
            "vectors_indexed": index_result["vectors_indexed"],
        }