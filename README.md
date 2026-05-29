# AML
code, writing, and results from the project "AI-powered search and analysis of infrastructure asset archives" for the Machine Learning Challenge '26

## API Setup

Below you can find explanations of the different endpoints and components of the project together with example body param values for the requetsts.

1. Full ingestion pipeline - Use this when you want to process files from the data folder.If files are unchanged, OCR/extraction is skipped !!!
Runs: file inventory → change detection → OCR/text extraction → embeddings → index build
Endpoint: POST http://localhost:8000/api/ingestion/start
Body:
{
  "root_folder": "../../data",
  "output_dir": "../../results",
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

## Retrieval Algorithm Setup


The following search functions are implemented:
- **search_bm25()**
- **search_semantic()**
- **search_hybrid()**

Here is an overview of the search filters:

| var_name | type | passed to|
| --- |--- |---- |
| *mode* | | |
| *top_k* | | |
| *road* | | |
| *hm* | | |
| *hm_radius* | | |
| *place_name* | | |
| *place_x* | | |
| *place_y* | | |
| *place_radius_km* | | |
| *file_type* | | |
| *file_name* | | |
| *year_from* | | |
| *year_to* | | |




## Frontend Setup


The frontend consists of
- a simple main page under [src/frontend/main.html](./src/frontend/main.html)
- the search page at [src/frontend/pages/searchPage.html](./src/frontend/pages/searchPage.html)
- the pdf viewer page at [src/frontend/pages/pdfViewer.html](./src/frontend/pages/pdfViewer.html)


The search page is structured into 
- a search bar at the top for query input
- search filters on the left
- the search output div on the right


The search function is implemented in [src/frontend/assets/js/search.js](./src/frontend/assets/js/search.js) and runs as follows
- the search button on the searchPage calls the async function **search()** which collects the query
- the search query is passed to the async function **searchRequest()** which additionally fetches the filter states and constructs the body of the request 
- the request is passed to the API using the **async fetch** method to the port of the API, specified with *apiURL*, and the response is returned to the **search()** function as json
- the **search()** function loads the resultsDiv from the search page and checks results content
  - if results is empty, it displays  'No results found' in the results div
  - if results is not empty, it loops over the results and passes them to the **createPreviewCard()** function
- the **createPreviewCard()** function loads 
  - the title
  - a content-snippet
  - the link to the pdf


