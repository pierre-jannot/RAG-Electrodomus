"""
Scripts des fonctions Python de création/mise à jour de la BDD.
"""

from pathlib import Path

from src.core.config import load_settings
from src.database import database_functions as db
from src.services.embedding.docling_chunker import get_chunker, chunk_document, chunk_directory
from src.services.extraction.docling_converter import get_converter
from src.utils.files import list_files, get_path_after, compute_signature


settings = load_settings()


def populate_database():
    """
    Fonction permettant la récupération des documents,
    leur chunking et ajout dans la base de données.
    """
    collection = db.get_dense_collection()
    chunks_data = chunk_directory()
    db.ingest_chunks(collection=collection, chunks_data=chunks_data)


def synchronize_database(
    root: Path = settings.source_dir,
) -> dict[str, int]:
    """Fonction de mise à jour de la base de données."""
    collection = db.get_dense_collection()
    indexed = db.get_indexed_signatures(collection)
    stats = {"added": 0, "updated": 0, "unchanged": 0, "deleted": 0}
    seen_files: set[str] = set()

    converter = get_converter()
    chunker = get_chunker()

    for file in list_files(root):
        title = get_path_after(file, settings.dir_name)[-1]
        seen_files.add(title)
        signature = compute_signature(file)
        known = indexed.get(title)

        if known == {signature}:
            stats["unchanged"] += 1
            continue
        stats["added" if known is None else "updated"] += 1

        chunks = chunk_document(chunker, converter, file)
        db.ingest_chunks(collection, chunks, upsert=True)

        if known:
            collection.delete(
                where={
                    "$and": [
                        {"title": title},
                        {"signature": {"$ne": signature}},
                    ]
                }
            )

    for orphan in set(indexed) - seen_files:
        collection.delete(where={"title": orphan})
        stats["deleted"] += 1

    return stats
