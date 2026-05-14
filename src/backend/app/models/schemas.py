from pydantic import BaseModel


class IngestionRequest(BaseModel):
    root_folder: str
    output_dir: str = "results"
    tesseract_cmd: str | None = None
    min_direct_text_length: int = 30


class IngestionResponse(BaseModel):
    status: str
    message: str | None = None
    inventory_path: str | None = None
    extraction_path: str | None = None
    files_discovered: int = 0
    files_processed: int = 0
    pages_extracted: int = 0
    new_files: int = 0
    modified_files: int = 0
    deleted_files: int = 0
    unchanged_files: int = 0