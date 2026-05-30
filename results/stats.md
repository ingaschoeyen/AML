# Metrics + results

- ingestion time
- embedding time
- retrieval time 
- retrieval quality 
    - given sentence from doc as query, is doc in top_k results
    - 


## Ingestion time

- for 3 roads (N338/301/326)

## Embedding time

- for 3 roads with bge-m3 - - 1h8m30s
- for 3 roads with e5-nl-small - 9m0.24s
- for 3 roads with e5-nl-base - 23m50s

## BM25

- 'road construction drawing', k=20: 39ms

## Semantic

| LLM | BGE-M3 | E5-NL |
| --- | --- | --- |
| emedding | | |
| retrieval | | |

- 'road construction drawing', k=20: 19.46s

## Hybrid

| LLM | BGE-M3 | E5-NL |
| --- | --- | --- |
| emedding | | |
| retrieval | | |


- 'road construction drawing', k=20: 5.98s