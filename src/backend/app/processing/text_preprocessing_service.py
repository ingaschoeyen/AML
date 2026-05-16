"""
Dutch text preprocessing pipeline.

Applied identically at index time and query time so that lemmatized query
tokens can be matched against lemmatized index tokens.
"""

import re
import sys

import nltk
from nltk.corpus import stopwords


_stopwords: set[str] | None = None
_nlp = None


def download_nltk_data() -> None:
    for resource, path in [
        ("corpora/stopwords", "stopwords"),
    ]:
        try:
            nltk.data.find(resource)
        except LookupError:
            print(f"Downloading NLTK resource: {path}", file=sys.stderr)
            nltk.download(path, quiet=True)


def _get_stopwords() -> set[str]:
    global _stopwords
    if _stopwords is None:
        _stopwords = set(stopwords.words("dutch"))
    return _stopwords


def get_nlp_model(model_name: str):
    global _nlp
    if _nlp is None:
        import spacy
        print(f"Loading spaCy model '{model_name}' ...", file=sys.stderr)
        _nlp = spacy.load(model_name, disable=["parser", "senter"])
    return _nlp


def process_text(
    text: str,
    model_name: str,
    boost_types: set[str] | None = None,
    boost_factor: int = 1,
) -> list[str]:
    """
    Lemmatize Dutch text with spaCy, optionally boosting NER entity tokens.

    Runs a single spaCy pass for both lemmatization and NER so that
    documents are not processed twice. Tokens belonging to an entity type
    in boost_types are repeated boost_factor times in the output list,
    increasing their BM25 term frequency.

    Returns a list of lowercase lemma strings.
    """
    if not text or not text.strip():
        return []

    nlp = get_nlp_model(model_name)
    doc = nlp(text[:100_000])
    sw = _get_stopwords()

    boost_tokens: set[str] = set()
    if boost_types:
        for ent in doc.ents:
            if ent.label_ in boost_types:
                for tok in ent:
                    boost_tokens.add(tok.text.lower())

    result: list[str] = []
    for token in doc:
        if token.is_space or token.is_punct:
            continue
        lower = token.text.lower()
        if token.is_stop or lower in sw:
            continue
        if not re.search(r"[a-z0-9]", lower):
            continue
        lemma = token.lemma_.lower()
        if not re.search(r"[a-z0-9]", lemma):
            continue
        repeat = boost_factor if lower in boost_tokens else 1
        result.extend([lemma] * repeat)

    return result
