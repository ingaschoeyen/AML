from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.models.schemas import IngestionRequest, IngestionResponse
from app.pipeline.ingestion_pipeline import IngestionPipeline
from app.api.embedding_controller import router as embedding_router
from app.api.search_controller import router as search_router
# to run: cd src/backend and then uvicorn app.main:app --reload
from app.api.index_controller import router as index_router
from app.search import config
from app.processing.text_preprocessing_service import download_nltk_data, get_nlp_model


@asynccontextmanager
async def lifespan(app: FastAPI):
    download_nltk_data()
    get_nlp_model(config.NER_MODEL)
    yield


app = FastAPI(title="Document Semantic Search API", lifespan=lifespan)

# Enable CORS so browser clients can call the API from other origins.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(embedding_router)
app.include_router(search_router)
app.include_router(index_router)

@app.get("/")
def health_check():
    return {"status": "ok"}


@app.post("/api/ingestion/start", response_model=IngestionResponse)
def start_ingestion(request: IngestionRequest):
    pipeline = IngestionPipeline(
        root_folder=request.root_folder,
        output_dir=request.output_dir,
        tesseract_cmd=request.tesseract_cmd,
        min_direct_text_length=request.min_direct_text_length,
    )

    return pipeline.run()