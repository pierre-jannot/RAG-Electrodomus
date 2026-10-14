"""
Script python des fonctions permettant le découpage
du corpus en chunks.
"""

from functools import lru_cache
from pathlib import Path

from docling.chunking import HybridChunker
from docling.document_converter import DocumentConverter
from docling_core.transforms.chunker import DocChunk
from docling_core.transforms.chunker.tokenizer.huggingface import HuggingFaceTokenizer
from transformers import AutoTokenizer

from src.core.config import load_path_settings, load_embedding_settings
from src.services.extraction.docling_converter import convert_file, get_converter
from src.services.extraction.metadata_extractor import resolve_metadata, resolve_chunk_metadata
from src.utils.files import list_files, get_path_after

path_settings = load_path_settings()
embedding_settings = load_embedding_settings()


def build_tokenizer():
    """
    Script de création du tokenizer.
    """
    tokenizer = HuggingFaceTokenizer(
        tokenizer=AutoTokenizer.from_pretrained(embedding_settings.embed_model),
        max_tokens=embedding_settings.max_tokens,
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


@lru_cache
def get_chunker() -> HybridChunker:
    """Fonction de récupération du chunker, avec cache."""
    return build_chunker()


def chunk_document(
        chunker: HybridChunker,
        converter: DocumentConverter,
        file: Path
        ) -> list[DocChunk]:
    """
    Fonction de séparation du document
    en chunks.
    """
    document = convert_file(file, converter=converter)
    path = get_path_after(file, path_settings.dir_name)
    document_text = document.export_to_markdown()
    metadata = resolve_metadata(document_text, path)
    raw_chunks = list(chunker.chunk(dl_doc=document))
    chunks = []

    for index, chunk in enumerate(raw_chunks):
        enriched = chunker.contextualize(chunk=chunk)
        chunk_metadata = resolve_chunk_metadata(chunk, metadata, enriched, path)
        final_chunk = {
            "text": enriched,
            "metadata": chunk_metadata,
            "id": f"{chunk_metadata["title"]}::chunk_{index:04d}",
        }
        chunks.append(final_chunk)

    return chunks


def chunk_directory(path: Path = path_settings.source_dir) -> list[DocChunk]:
    """
    Fonction de séparation de tous les documents
    du directory en chunks.
    """
    converter = get_converter()
    chunker = get_chunker()
    files = list_files(path)
    chunks = []

    for file in files:
        doc_chunks = chunk_document(chunker, converter, file)
        chunks.extend(doc_chunks)
        print(f"Document {file} traité en {len(doc_chunks)} chunk(s).")

    print(f"Chunking fini. {len(chunks)} chunks produits.")
    return chunks
