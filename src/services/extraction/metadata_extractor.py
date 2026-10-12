"""
Script des fonctions de récupération des
metadata.
"""

from pathlib import Path

from docling_core.transforms.chunker import DocChunk

from src.core.config import load_settings
from src.services.extraction.regex_extractor import (
    resolve_date, resolve_errors, resolve_models, resolve_chunk_errors,
    resolve_chunk_models, resolve_chunk_page
    )
from src.utils.files import compute_signature


settings = load_settings()

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
    rel_path = Path(f"{settings.source_dir}/Documentation_Electrodomus/{'/'.join(path)}")
    signature = compute_signature(rel_path)

    return {
        "date": date,
        "models": models,
        "errors": errors,
        "signature": signature,
        }


def resolve_chunk_metadata(chunk: DocChunk,
                           document_metadata: dict,
                           enriched: str, path: list[str]
                           ) -> dict:
    """
    Récupérère les métadonnées du chunk.
    """
    date = document_metadata["date"]
    signature = document_metadata["signature"]
    models = resolve_chunk_models(chunk, enriched, document_metadata["models"], path)
    errors = resolve_chunk_errors(enriched, document_metadata["errors"])
    page = resolve_chunk_page(chunk)
    metadata = {
        "title": path[-1] if path else "",
        "path": path[:-1] if path else "",
        "signature": signature,
        "date": date,
        "page": page,
        "headings": chunk.meta.headings,
        "models": models,
        "errors": errors,
        "access": "private"
        }

    return clean_metadata(metadata)
