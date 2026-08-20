"""
Script python des fonctions permettant le découpage
du corpus en chunks.
"""

from docling.chunking import HybridChunker
from docling_core.transforms.chunker.tokenizer.huggingface import HuggingFaceTokenizer
from docling_core.types.doc import DoclingDocument
from transformers import AutoTokenizer

from core.config import load_settings
from src.extraction.regex_extraction import resolve_metadata, resolve_chunk_metadata

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


def compute_chunks(chunker: HybridChunker, document: DoclingDocument, path: str):
    """
    Fonction de séparation du document
    en chunks.
    """
    document_text = document.export_to_markdown()
    metadata = resolve_metadata(document_text)
    raw_chunks = list(chunker.chunk(dl_doc=document))

    for i, chunk in enumerate(raw_chunks):
        enriched = chunker.contextualize(chunk=chunk)
        chunk_metadata = resolve_chunk_metadata(chunk, metadata, path)
        print(f"--------- Chunk {i} ---------")
        print(f"- Modèle(s) : {chunk_metadata["models"]} -")
        print(f"- Code(s) erreur : {chunk_metadata["errors"]} -")
        print(f"- Date : {chunk_metadata["date"]} -")
        print(f"- Path : {path} -")
        print(f"- Headings : {chunk.meta.headings} -")
        print(f"- Page : {chunk_metadata["page"]} -")
        print()
        print(enriched)
        print()
