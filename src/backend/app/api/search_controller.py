from pathlib import Path
from fastapi import APIRouter
from pydantic import BaseModel
from app.search.semantic_search_service import Searcher
from app.search.coordinates import geocode_place
from app.processing.text_preprocessing_service import download_nltk_data


router = APIRouter(prefix="/api/search", tags=["Search"])


class SearchRequest(BaseModel):
    query: str
    index_dir: str = "../../results/index"
    mode: str = "hybrid"
    top_k: int = 10
    embedding_model: str | None = None
    # Road + hectometer filter
    road: str | None = None
    hm: float | None = None
    hm_radius: float = 1.0
    # Location filter — supply either a place name or explicit RD coordinates
    place_name: str | None = None
    place_x: int | None = None
    place_y: int | None = None
    place_radius_km: float = 2.0
    # Document filters
    file_type: str | None = None
    file_name: str | None = None
    year_from: int | None = None
    year_to: int | None = None


@router.post("")
def search(request: SearchRequest):
    download_nltk_data()

    # Resolve place_name to RD coords when raw coords are not supplied
    place_x, place_y = request.place_x, request.place_y
    if request.place_name and place_x is None:
        resolved = geocode_place(request.place_name)
        if resolved is None:
            return {"status": "error", "message": f"Could not geocode place '{request.place_name}'"}
        place_x, place_y = resolved

    filters = {
        "road": request.road,
        "hm": request.hm,
        "hm_radius": request.hm_radius,
        "place_x": place_x,
        "place_y": place_y,
        "place_radius": request.place_radius_km * 1000,
        "file_type": request.file_type,
        "file_name": request.file_name,
        "year_from": request.year_from,
        "year_to": request.year_to,
    }

    searcher = Searcher(Path(request.index_dir))


    if request.mode == "bm25":
        results = searcher.search_bm25(request.query, top_k=request.top_k, **filters)
    elif request.mode == "semantic":
        embedding_model = request.embedding_model or 'clips/e5-small-trm-nl'
        results = searcher.search_semantic(request.query, top_k=request.top_k, embedding_model=embedding_model, **filters)
    else:
        embedding_model = request.embedding_model or 'clips/e5-small-trm-nl'
        results = searcher.search_hybrid(request.query, top_k=request.top_k, embedding_model=embedding_model, **filters)

    return {
        "status": "completed",
        "query": request.query,
        "mode": request.mode,
        "results": results,
    }