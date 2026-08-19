"""
Script python des fonctions permettant le découpage
du corpus en chunks.
"""

from docling.chunking import HybridChunker
from docling_core.transforms.chunker.tokenizer.huggingface import HuggingFaceTokenizer
from docling_core.types.doc import DoclingDocument
from transformers import AutoTokenizer

from core.config import load_settings
from src.extraction.regex_extraction import resolve_models, resolve_chunk_models, extract_document_date, resolve_errors, resolve_chunk_errors

settings = load_settings()


def build_tokenizer():
    """
    Script de création du tokenizer.
    """
    tokenizer = HuggingFaceTokenizer(
        tokenizer=AutoTokenizer.from_pretrained(settings.embed_model),
        max_tokens=settings.max_tokens,
    )
    return tokenizer


def build_chunker():
    """
    Script de création du chunker.
    """
    chunker = HybridChunker(
        tokenizer=build_tokenizer(),
        merge_peers=True,
    )
    return chunker


def compute_chunks(chunker: HybridChunker, document: DoclingDocument):
    """
    Fonction de séparation du document
    en chunks.
    """
    document_text = document.export_to_markdown()
    document_level_models = resolve_models(document_text)
    document_date = extract_document_date(document_text)
    document_level_errors = resolve_errors(document_text)
    raw_chunks = list(chunker.chunk(dl_doc=document))

    for i, chunk in enumerate(raw_chunks):
        enriched = chunker.contextualize(chunk=chunk)
        chunk_models = resolve_chunk_models(enriched, document_level_models)
        chunk_errors = resolve_chunk_errors(enriched, document_level_errors)
        print(f"--- Chunk {i} ---")
        print(f"- Modèle : {chunk_models} -")
        print(f"- Codes erreur : {chunk_errors} -")
        print(f"- Date : {document_date} -")
        print(enriched)
        print()
