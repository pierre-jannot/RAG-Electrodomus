"""
Script des fonctions de récupération des
metadata.
"""

from docling_core.transforms.chunker import DocChunk

from src.extraction.regex_extractor import resolve_date, resolve_errors, resolve_models
from src.extraction.regex_extractor import resolve_chunk_errors, resolve_chunk_models, resolve_chunk_page


def clean_metadata(metadata: dict) -> dict:
    """
    Nettoie un dict de métadonnées pour Chroma :
    - supprime les clés dont la valeur est None
    - remplace les listes vides par une valeur scalaire vide (Chroma
      interdit les listes vides, mais accepte une chaîne vide)
    """
    cleaned = {}
    for key, value in metadata.items():
        if value is None:
            continue
        if isinstance(value, list) and len(value) == 0:
            continue
        cleaned[key] = value
    return cleaned


def resolve_metadata(text: str, path: list[str]) -> dict:
    """
    Récupérère les métadonnées du texte.
    """
    date = resolve_date(text)
    models = resolve_models(text, path)
    errors = resolve_errors(text)

    return {
        "date": date,
        "models": models,
        "errors": errors,
        }


def resolve_chunk_metadata(chunk: DocChunk,
                           document_metadata: dict,
                           enriched: str, path: list[str]
                           ) -> dict:
    """
    Récupérère les métadonnées du chunk.
    """
    date = document_metadata["date"]
    models = resolve_chunk_models(chunk, enriched, document_metadata["models"], path)
    errors = resolve_chunk_errors(enriched, document_metadata["errors"])
    page = resolve_chunk_page(chunk)
    metadata = {
        "title": path[-1],
        "path": path[:-1],
        "date": date,
        "page": page,
        "headings": chunk.meta.headings,
        "models": models,
        "errors": errors,
        }

    return clean_metadata(metadata)
