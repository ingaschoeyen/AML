# AML
code, writing, and results from the project "AI-powered search and analysis of infrastructure asset archives" for the Machine Learning Challenge '26

Below you can find explanations of the different endpoints and components of the project together with example body param values for the requetsts.

1. Full ingestion pipeline - Use this when you want to process files from the data folder.If files are unchanged, OCR/extraction is skipped !!!
Runs: file inventory → change detection → OCR/text extraction → embeddings → index build
Endpoint: POST http://localhost:8000/api/ingestion/start
Body:
{
  "root_folder": "../../test_inventory",
  "output_dir": "../../test_result",
  "tesseract_cmd": null,
  "min_direct_text_length": 30
}


2. Create embeddings separately - Use this when page_extraction.csv already exists and you only want to rebuild embeddings, for example with another embedding model.
Endpoint: POST http://localhost:8000/api/embeddings/create
Body:
{
  "path_to_text": "../../results/page_extraction.csv",
  "output_dir": "../../results",
  "model_name": "BAAI/bge-m3",
  "recursive": true,
  "merge_type": "mean",
  "chunk_size": 1000,
  "chunk_overlap": 200,
  "file_type": "pkl"
}

3. Build search index separately - Use this after rebuilding embeddings separately.This creates:

results/index/doc_store.json
results/index/texts.json
results/index/embeddings.npy

Endpoint: POST http://localhost:8000/api/index/build
Body:
{
  "extraction_csv_path": "../../results/page_extraction.csv",
  "embeddings_pkl_path": "../../results/embeddings.pkl",
  "index_dir": "../../results/index"
}

4. Search - Use this after the index exists.
Endpoint: POST http://localhost:8000/api/search
Body:
{
  "query": "road construction drawing",
  "index_dir": "../../results/index",
  "mode": "semantic",
  "top_k": 5
}