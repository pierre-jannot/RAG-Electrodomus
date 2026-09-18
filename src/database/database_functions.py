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
from src.services.embedding.docling_chunker import chunk_directory

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


def ingest_chunks(
    collection: chromadb.Collection,
    chunks_data: list[dict[str, Any]],
    batch_size: int = 100,
) -> None:
    """
    chunks_data : liste de dicts {"text": str, "metadata": dict, "id": str (optionnel)}
    """
    for i in range(0, len(chunks_data), batch_size):
        batch = chunks_data[i : i + batch_size]

        ids = [item.get("id") or str(uuid.uuid4()) for item in batch]
        documents = [item["text"] for item in batch]
        metadatas = [item["metadata"] for item in batch]

        collection.add(ids=ids, documents=documents, metadatas=metadatas)
        print(f"Lot {i // batch_size + 1} inséré : {len(batch)} chunks "
              f"({i + len(batch)}/{len(chunks_data)} au total)")


def populate_database():
    """
    Fonction permettant la récupération des documents,
    leur chunking et ajout dans la base de données.
    """
    collection = get_dense_collection()
    chunks_data = chunk_directory()
    ingest_chunks(collection=collection, chunks_data=chunks_data)


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
