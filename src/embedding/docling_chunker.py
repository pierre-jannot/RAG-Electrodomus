"""
Script python des fonctions permettant le découpage
du corpus en chunks.
"""

from pathlib import Path

from docling.chunking import HybridChunker
from docling_core.transforms.chunker.tokenizer.huggingface import HuggingFaceTokenizer
from docling_core.transforms.chunker import DocChunk
from docling_core.types.doc import DoclingDocument
from transformers import AutoTokenizer

from src.core.config import load_settings
from src.extraction.docling_converter import convert_file, build_converter
from src.extraction.metadata_extractor import resolve_metadata, resolve_chunk_metadata
from src.utils.files import list_files, get_path_after

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


def chunk_document(chunker: HybridChunker, document: DoclingDocument, path: str) -> list[DocChunk]:
    """
    Fonction de séparation du document
    en chunks.
    """
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


def chunk_directory(path: Path = settings.source_dir) -> list[DocChunk]:
    """
    Fonction de séparation de tous les documents
    du directory en chunks.
    """
    converter = build_converter()
    chunker = build_chunker()
    files = list_files(path)
    chunks = []

    for file in files:
        document = convert_file(file, converter=converter)
        path = get_path_after(file, "Documentation_Electrodomus")
        doc_chunks = chunk_document(chunker, document, path)
        chunks.extend(doc_chunks)
        print(f"Document {file} traité en {len(doc_chunks)} chunk(s).")

    print(f"Chunking fini. {len(chunks)} chunks produits.")
    return chunks
