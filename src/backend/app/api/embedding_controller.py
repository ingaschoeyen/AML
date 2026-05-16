from pathlib import Path

from fastapi import APIRouter

from app.models.schemas import EmbeddingRequest, EmbeddingResponse
from app.processing.embedding_service import SemanticEmbedder


router = APIRouter(prefix="/api/embeddings", tags=["Embeddings"])


@router.post("/create", response_model=EmbeddingResponse)
def create_embeddings(request: EmbeddingRequest):
    embedder = SemanticEmbedder(
        model_name=request.model_name,
        recursive=request.recursive,
        merge_type=request.merge_type,
        chunk_size=request.chunk_size,
        chunk_overlap=request.chunk_overlap,
    )

    embeddings_df = embedder.run_from_csv(
        path_to_text=request.path_to_text,
        output_dir=request.output_dir,
        file_type=request.file_type,
    )

    extension = "pkl" if request.file_type == "pkl" else "csv"
    embeddings_path = Path(request.output_dir) / f"embeddings.{extension}"

    return {
        "status": "completed",
        "message": "Embeddings created successfully.",
        "path_to_text": request.path_to_text,
        "output_dir": request.output_dir,
        "embeddings_created": len(embeddings_df),
        "embeddings_path": str(embeddings_path),
    }