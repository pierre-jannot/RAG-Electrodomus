"""
Script de création ou récupération de la
base de données Chroma.
"""

from functools import lru_cache
from typing import Any
import uuid

import chromadb

from src.core.config import load_settings
from src.services.embedding.dense_embedding import ChromaDenseEmbeddingFunction

settings = load_settings()


@lru_cache(maxsize=1)
def get_dense_collection(
    persist_path: str = settings.db_dir,
    collection_name: str = settings.collection_name,
) -> chromadb.Collection:
    """
    Fonction de création/récupération de la base de données.
    """
    client = chromadb.PersistentClient(path=persist_path)
    try:
        return client.get_collection(name=collection_name)
    except Exception:
        return client.create_collection(
            name=collection_name,
            embedding_function=ChromaDenseEmbeddingFunction(),
            metadata={"hnsw:space": "cosine"},
        )


def get_indexed_signatures(collection, batch_size: int = 1000) -> dict[str, set[str]]:
    """Retourne {path: {signatures présentes dans l'index}}."""
    indexed: dict[str, set[str]] = {}
    offset = 0
    while True:
        batch = collection.get(include=["metadatas"], limit=batch_size, offset=offset)
        metadatas = batch["metadatas"] or []
        if not metadatas:
            break
        for meta in metadatas:
            if meta and "title" in meta and "signature" in meta:
                indexed.setdefault(meta["title"], set()).add(meta["signature"])
        offset += batch_size
    return indexed


def ingest_chunks(
    collection: chromadb.Collection,
    chunks_data: list[dict[str, Any]],
    batch_size: int = 100,
    upsert: bool = False,
) -> None:
    """
    chunks_data : liste de dicts {"text": str, "metadata": dict, "id": str (optionnel)}
    """
    write = collection.upsert if upsert else collection.add

    for i in range(0, len(chunks_data), batch_size):
        batch = chunks_data[i : i + batch_size]

        ids = [item.get("id") or str(uuid.uuid4()) for item in batch]
        documents = [item["text"] for item in batch]
        metadatas = [item["metadata"] for item in batch]

        write(ids=ids, documents=documents, metadatas=metadatas)
        print(f"Lot {i // batch_size + 1} inséré : {len(batch)} chunks "
              f"({i + len(batch)}/{len(chunks_data)} au total)")


def add_metadata_to_all(key: str, value, batch_size: int = 500) -> int:
    """
    Ajoute ou remplace une clé de métadonnée sur tous les chunks.
    """
    collection = get_dense_collection()
    result = collection.get(include=["metadatas"])

    ids = result["ids"]
    metadatas = [dict(meta or {}) for meta in result["metadatas"]]

    for meta in metadatas:
        meta[key] = value

    for i in range(0, len(ids), batch_size):
        collection.update(
            ids=ids[i:i + batch_size],
            metadatas=metadatas[i:i + batch_size],
        )


def add_metadata_by_title(filter_key: str, filter_value, key: str, value, batch_size: int = 500):
    """
    Ajoute ou remplace une clé de métadonnée sur les chunks dont la clé et la valeur
    correspondent à celles données.
    """
    collection = get_dense_collection()

    result = collection.get(
        where={filter_key: filter_value},
        include=["metadatas"],
    )

    ids = result["ids"]
    if not ids:
        return 0

    metadatas = [dict(meta or {}) for meta in result["metadatas"]]
    for meta in metadatas:
        meta[key] = value

    for i in range(0, len(ids), batch_size):
        collection.update(
            ids=ids[i:i + batch_size],
            metadatas=metadatas[i:i + batch_size],
        )


PRESERVED_KEYS = ("access",)


def get_existing_metadatas(collection, title: str) -> dict:
    """Lit les métadonnées à conserver sur les chunks actuels d'un document."""
    result = collection.get(where={"title": title}, include=["metadatas"])
    preserved: dict = {}
    for meta in result["metadatas"] or []:
        for key in PRESERVED_KEYS:
            if meta and key in meta and key not in preserved:
                preserved[key] = meta[key]
    return preserved


def fetch_candidates(candidate_ids: list[str]) -> list[dict]:
    """Récupère texte et métadonnées des candidats, dans l'ordre de candidate_ids."""
    if not candidate_ids:
        return []

    chroma_collection = get_dense_collection()

    data = chroma_collection.get(ids=candidate_ids, include=["documents", "metadatas"])
    id_to_doc = dict(zip(data["ids"], data["documents"]))
    id_to_meta = dict(zip(data["ids"], data["metadatas"]))

    return [
        {
            "id": doc_id,
            "score": None,
            "text": id_to_doc[doc_id],
            "metadata": id_to_meta[doc_id],
        }
        for doc_id in candidate_ids
        if doc_id in id_to_doc   # ignore un ID disparu entre-temps
    ]
