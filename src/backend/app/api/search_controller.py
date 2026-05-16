from pathlib import Path
from fastapi import APIRouter
from pydantic import BaseModel
from app.search.semantic_search_service import Searcher
from app.processing.text_preprocessing_service import download_nltk_data


router = APIRouter(prefix="/api/search", tags=["Search"])


class SearchRequest(BaseModel):
    query: str
    index_dir: str = "../../results/index"
    mode: str = "hybrid"
    top_k: int = 10
    road: str | None = None
    hm: float | None = None
    hm_radius: float = 1.0
    place_x: int | None = None
    place_y: int | None = None
    place_radius: float = 2000.0


@router.post("")
def search(request: SearchRequest):
    download_nltk_data()

    searcher = Searcher(Path(request.index_dir))

    filters = {
        "road": request.road,
        "hm": request.hm,
        "hm_radius": request.hm_radius,
        "place_x": request.place_x,
        "place_y": request.place_y,
        "place_radius": request.place_radius,
    }

    if request.mode == "bm25":
        results = searcher.search_bm25(
            request.query,
            top_k=request.top_k,
            **filters,
        )
    elif request.mode == "semantic":
        results = searcher.search_semantic(
            request.query,
            top_k=request.top_k,
        )
    else:
        results = searcher.search_hybrid(
            request.query,
            top_k=request.top_k,
            **filters,
        )

    return {
        "status": "completed",
        "query": request.query,
        "mode": request.mode,
        "results": results,
    }