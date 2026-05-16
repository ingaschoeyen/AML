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

class EmbeddingRequest(BaseModel):
    path_to_text: str
    output_dir: str = "results"
    model_name: str = "clips/e5-small-trm-nl"
    recursive: bool = True
    merge_type: str = "mean"
    chunk_size: int = 1000
    chunk_overlap: int = 200
    file_type: str = "pkl"


class EmbeddingResponse(BaseModel):
    status: str
    message: str
    path_to_text: str
    output_dir: str
    embeddings_created: int
    embeddings_path: str