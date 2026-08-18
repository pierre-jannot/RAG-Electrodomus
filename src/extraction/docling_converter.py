""""
docling_converter.py

Wrapper autour de Docling DocumentConverter pour les formats du projet :
PDF (texte), DOCX, HTML, XLSX.
"""

from pathlib import Path

from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption

from docling_core.types.doc import DoclingDocument

def build_converter() -> DocumentConverter:
    """
    Builder du convertisseur de documents.
    Permet de paramétrer le convertisseur en fonction des
    documents attendus par le projet.
    """
    pdf_options = PdfPipelineOptions()
    pdf_options.do_ocr = False
    pdf_options.do_picture_description = False
    pdf_options.do_picture_classification = False

    return DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(pipeline_options=pdf_options),
        },
    )


def convert_file(path: Path, converter: DocumentConverter | None = None) -> DoclingDocument:
    """
    Convertit un fichier en DoclingDocument.
    """
    if converter is None:
        converter = build_converter()
    result = converter.convert(path)
    return result.document
