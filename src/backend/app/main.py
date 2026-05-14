from fastapi import FastAPI
from app.models.schemas import IngestionRequest, IngestionResponse
from app.pipeline.ingestion_pipeline import IngestionPipeline

# to run: cd src/backend and then uvicorn app.main:app --reload

app = FastAPI(title="Document Semantic Search API")


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