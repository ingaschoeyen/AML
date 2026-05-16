from pathlib import Path

from fastapi import APIRouter
from pydantic import BaseModel

from app.processing.index_builder_service import IndexBuilderService


router = APIRouter(prefix="/api/index", tags=["Index"])


class IndexBuildRequest(BaseModel):
    extraction_csv_path: str
    embeddings_pkl_path: str
    index_dir: str


@router.post("/build")
def build_index(request: IndexBuildRequest):
    index_builder = IndexBuilderService()

    result = index_builder.build_index(
        extraction_csv_path=request.extraction_csv_path,
        embeddings_pkl_path=request.embeddings_pkl_path,
        index_dir=request.index_dir,
    )

    return {
        "status": "completed",
        "message": "Search index built successfully.",
        **result,
    }