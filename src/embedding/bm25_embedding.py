"""
Script des fonctions d'embedding BM25.
"""

import bm25s
import snowballstemmer


FRENCH_STOPWORDS = [
    "le", "la", "les", "l", "un", "une", "des", "de", "du", "au", "aux",
    "et", "ou", "où", "à", "en", "dans", "sur", "sous", "avec", "sans", "pour",
    "par", "ce", "ces", "cet", "cette", "se", "sa", "son", "ses", "leur", "leurs",
    "ne", "pas", "plus", "que", "qui", "quoi", "dont", "il", "elle", "ils", "elles",
    "je", "tu", "nous", "vous", "on", "est", "sont", "être", "avoir", "a", "ont",
    "y", "si", "mais", "donc", "car", "ni", "comme", "quand", "aussi", "très",
]


FRENCH_STEMMER = snowballstemmer.stemmer("french")


def bm25_tokenize(documents: list[str]) -> bm25s.tokenization.Tokenized:
    """
    Tokenise un corpus de textes pour BM25 (stopwords + stemmer français).
    """
    return bm25s.tokenize(
        documents,
        stopwords=FRENCH_STOPWORDS,
        stemmer=FRENCH_STEMMER.stemWord,
    )


def build_bm25_index(documents: list[str]) -> bm25s.BM25:
    """
    Construit un index BM25 en mémoire à partir d'un corpus de textes.
    """
    retriever = bm25s.BM25()
    retriever.index(bm25_tokenize(documents))
    return retriever
