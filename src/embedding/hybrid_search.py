"""
Script des fonctions d'hybrid search.
"""
 
from sentence_transformers import CrossEncoder
 
from src.database.database_functions import get_dense_collection
from src.embedding.bm25_embedding import build_bm25_index, bm25_tokenize
 
 
_reranker = CrossEncoder("BAAI/bge-reranker-v2-m3", max_length=512)
 
 
def rrf(ranked_lists: list[list[str]], k: int = 60) -> list[str]:
    """Fusionne plusieurs listes d'ids classées via Reciprocal Rank Fusion."""
    scores: dict[str, float] = {}
    for ranked_ids in ranked_lists:
        for rank, doc_id in enumerate(ranked_ids, start=1):
            scores[doc_id] = scores.get(doc_id, 0.0) + 1 / (k + rank)
    return sorted(scores, key=lambda doc_id: -scores[doc_id])
 
 
def dense_search(collection, question: str, where_clause: dict | None, n: int) -> list[str]:
    """Retourne les ids classés par similarité dense, filtrage par where_clause."""
    results = collection.query(query_texts=[question], where=where_clause, n_results=n)
    return results["ids"][0]
 
 
def bm25_search(collection, question: str, where_clause: dict | None, n: int) -> list[str]:
    """Retourne les ids classés par BM25, filtrage par where_clause."""
    candidates = collection.get(where=where_clause, include=["documents"])
    ids = candidates["ids"]
    documents = candidates["documents"]
 
    if not ids:
        return []
 
    retriever = build_bm25_index(documents)
    query_tokens = bm25_tokenize(question)
    results, scores = retriever.retrieve(query_tokens, k=min(n, len(ids)))
 
    return [ids[i] for i in results[0]]
 
 
def rerank(collection, question: str, candidate_ids: list[str], top_k: int) -> list[dict]:
    """Reranking cross-encoder sur les candidats sortants du premier reranking"""
    if not candidate_ids:
        return []
 
    candidates = collection.get(ids=candidate_ids, include=["documents", "metadatas"])
    id_to_doc = dict(zip(candidates["ids"], candidates["documents"]))
    id_to_meta = dict(zip(candidates["ids"], candidates["metadatas"]))
 
    pairs = [[question, id_to_doc[doc_id]] for doc_id in candidate_ids]
    scores = _reranker.predict(pairs)
 
    ranked = sorted(zip(candidate_ids, scores), key=lambda x: -x[1])[:top_k]
 
    return [
        {
            "id": doc_id,
            "score": float(score),
            "text": id_to_doc[doc_id],
            "metadata": id_to_meta[doc_id],
        }
        for doc_id, score in ranked
    ]
 
 
def hybrid_search(
    question: str,
    where_clause: dict | None = None,
    n_candidates: int = 30,
    top_k: int = 5,
) -> list[dict]:
    """
    Fonction d'exécution de l'hybrid search.
    """
    collection = get_dense_collection()
 
    dense_ids = dense_search(collection, question, where_clause, n=n_candidates)
    bm25_ids = bm25_search(collection, question, where_clause, n=n_candidates)
 
    fused_ids = rrf([dense_ids, bm25_ids])[:n_candidates]
 
    return rerank(collection, question, fused_ids, top_k=top_k)
