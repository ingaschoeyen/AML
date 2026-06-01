from pathlib import Path

# ---------------------------------------------------------------------------
# Paths (overridable via CLI args; these are the defaults)
# ---------------------------------------------------------------------------
CSV_PATH: Path = Path("data.csv")
INDEX_DIR: Path = Path("../../results/index")

# ---------------------------------------------------------------------------
# BM25F field weights
# Higher weight = field tokens are repeated more times before indexing,
# giving them proportionally more influence on BM25 scoring.
# ---------------------------------------------------------------------------
BM25_FIELD_WEIGHTS: dict[str, int] = {
    "besteksnummer": 3,
    "ordernummer":   3,
    "Onderdeel":     2,
    "project":       2,
    "opdrachtgever": 1,
    "tekst":         1,
}

# Fields concatenated (unweighted) for BGE-M3 semantic embedding
EMBED_FIELDS: list[str] = [
    "besteksnummer",
    "ordernummer",
    "project",
    "Onderdeel",
    "opdrachtgever",
    "tekst",
]

# ---------------------------------------------------------------------------
# BGE-M3
# ---------------------------------------------------------------------------
BGE_MODEL_NAME: str = "BAAI/bge-m3"
BGE_BATCH_SIZE: int = 32


# ---------------------------------------------------------------------------
# E5-NL 
# ---------------------------------------------------------------------------
E5_MODEL_NAME: str = "clips/e5-large-trm-nl"

# ---------------------------------------------------------------------------
# NER-based BM25 term boosting
# spaCy Dutch model detects named entities; tokens belonging to the listed
# entity types are repeated NER_BOOST_FACTOR times in the BM25 token list.
# Rebuild the index after changing these settings.
# Install: pip install spacy && python -m spacy download nl_core_news_lg
# ---------------------------------------------------------------------------
NER_MODEL: str = "nl_core_news_lg"
NER_BOOST_TYPES: set[str] = {"GPE", "LOC"}  # geopolitical & location entities
NER_BOOST_FACTOR: int = 3

# ---------------------------------------------------------------------------
# Search hyperparameters
# ---------------------------------------------------------------------------
RRF_K: int = 60          # Reciprocal Rank Fusion constant
DEFAULT_TOP_K: int = 10  # Default number of results to return
