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

Running the frontend locally
----------------------------

1. Install the frontend dependencies (from the repository root):

  ```bash
  npm --prefix AML/src/frontend install
  ```

2. Start the frontend Express server (serves pages and PDF assets):

  ```bash
  npm --prefix AML/src/frontend start
  ```

  This will run a small Express server on `http://localhost:5500` that serves the frontend pages and the `public/data` PDF assets under `http://localhost:5500/data/...`.

3. Open the search page in your browser:

  - `http://localhost:5500/pages/searchPage.html`

Notes
-----
- The backend API runs on port `8000` and is contacted by the frontend at `http://localhost:8000/api/...`.
- The PDF preview in the search results fetches files from the frontend Express server (port `5500`) so the browser can access local PDF files via HTTP. Make sure the Express server is running when previewing PDFs.
- If you run a separate file server (e.g., Live Server) on `127.0.0.1:5501`, the backend CORS policy allows common dev origins but using `http://localhost:5500` for the frontend is recommended to match the configured paths.

PDF server and ports
--------------------

This project uses two local servers during development: the backend FastAPI server (search API) and a small Express server that serves the frontend pages and local PDF assets used for previewing. Below is a quick reference table and example commands to start each service.

| Port | Service | Access / Protocol | Notes / Start command |
| ---: | :------ | :---------------- | :-------------------- |
| 5500 | Frontend Express server | http://localhost:5500 (HTTP) | Serves frontend pages and PDF assets under `/data/...`.
|      | | | Start: `npm --prefix AML/src/frontend start` |
| 8000 | Backend API (FastAPI / uvicorn) | http://localhost:8000 (HTTP, JSON API) | Provides `/api/search`, `/api/index`, `/api/embeddings` endpoints. Start: `cd AML/src/backend && uvicorn app.main:app --reload --host 127.0.0.1 --port 8000` |
| 5501 | Optional dev file server (Live Server) | http://127.0.0.1:5501 (HTTP) | Alternative static server you might run from an editor; if used, ensure backend CORS allows this origin. |

Example PDF preview URL (served by the frontend Express server):

```
http://localhost:5500/data/N326/326023/DOC/326023_IR_2009.pdf
```

Notes
-----
- The frontend previewer constructs absolute URLs to the Express server (port `5500`) when loading PDFs. Always run the Express server if you want to preview files from search results.
- Backend CORS: the FastAPI app allows common local dev origins (`localhost:5500`, `localhost:5501`, `127.0.0.1:5500`, `127.0.0.1:5501`) so the frontend can call the API from typical dev servers. If you change ports, update the CORS allowlist in `src/backend/app/main.py`.
- To run everything quickly from the repo root:

```bash
# start backend (in one terminal)
cd AML/src/backend
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

# start frontend server (in another terminal)
npm --prefix AML/src/frontend start
```


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


