"""
Script des fonctions d'hybrid search.
"""

from sentence_transformers import CrossEncoder

from src.core.config import load_settings
from src.database.database_functions import get_dense_collection, fetch_candidates
from src.services.embedding.bm25_embedding import build_bm25_index, bm25_tokenize


settings = load_settings()
_reranker = CrossEncoder("BAAI/bge-reranker-v2-m3", max_length=512)

collection = get_dense_collection()

def rrf(ranked_lists: list[list[str]], k: int = 60) -> list[str]:
    """Fusionne plusieurs listes d'ids classées via Reciprocal Rank Fusion."""
    scores: dict[str, float] = {}
    for ranked_ids in ranked_lists:
        for rank, doc_id in enumerate(ranked_ids, start=1):
            scores[doc_id] = scores.get(doc_id, 0.0) + 1 / (k + rank)
    return sorted(scores, key=lambda doc_id: -scores[doc_id])


def dense_search(chroma_collection, question: str, where_clause: dict | None, n: int) -> list[str]:
    """Retourne les ids classés par similarité dense, filtrage par where_clause."""
    results = chroma_collection.query(query_texts=[question], where=where_clause, n_results=n)
    return results["ids"][0]


def bm25_search(chroma_collection, question: str, where_clause: dict | None, n: int) -> list[str]:
    """Retourne les ids classés par BM25, filtrage par where_clause."""
    candidates = chroma_collection.get(where=where_clause, include=["documents"])
    ids = candidates["ids"]
    documents = candidates["documents"]

    if not ids:
        return []

    retriever = build_bm25_index(documents)
    query_tokens = bm25_tokenize(question)
    results, _ = retriever.retrieve(query_tokens, k=min(n, len(ids)))

    return [ids[i] for i in results[0]]


def rerank(question: str, candidates: list[dict], top_k: int) -> list[dict]:
    """Reranking cross-encoder sur des candidats déjà récupérés."""
    if not candidates:
        return []

    pairs = [[question, c["text"]] for c in candidates]
    scores = _reranker.predict(pairs)

    ranked = sorted(zip(candidates, scores), key=lambda x: -x[1])[:top_k]
    return [{**c, "score": float(score)} for c, score in ranked]


def hybrid_search(
    question: str,
    where_clause: dict | None = None,
    n_candidates: int = settings.n_candidates,
    rff_candidates: int = settings.rrf_candidates,
    rerank_candidates: int = settings.rerank_candidates,
    cross_encode: bool = settings.cross_encode,
) -> list[dict]:
    """
    Fonction d'exécution de l'hybrid search.
    """

    dense_ids = dense_search(collection, question, where_clause, n=n_candidates)
    bm25_ids = bm25_search(collection, question, where_clause, n=n_candidates)

    fused_ids = rrf([dense_ids, bm25_ids])[:rff_candidates]

    if cross_encode:
        candidates = fetch_candidates(fused_ids)
        return rerank(question, candidates, top_k=rerank_candidates)

    return fetch_candidates(fused_ids[:rerank_candidates])
