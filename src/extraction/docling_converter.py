""""
docling_converter.py

Wrapper autour de Docling DocumentConverter pour les formats du projet :
PDF (texte), DOCX, HTML, XLSX.
"""

from io import BytesIO
from pathlib import Path

from docling.datamodel.base_models import InputFormat, DocumentStream
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling_core.types.doc import DoclingDocument, DocItemLabel

import pandas as pd

from src.extraction.xlsx_extractor import read_sheet_fixed_template
from src.extraction.html_extractor import promote_summary_to_heading


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
    Convertit un fichier en DoclingDocument, avec un traitement dédié par
    extension quand le pipeline générique de Docling ne suffit pas.
    """
    if converter is None:
        converter = build_converter()

    suffix = path.suffix.lower()

    match suffix:

        case ".xlsx":
            return xlsx_to_docling_document(str(path))

        case ".html" | ".htm":
            raw_html = path.read_text(encoding="utf-8")
            transformed_html = promote_summary_to_heading(raw_html)
            stream = DocumentStream(
                name=path.name,
                stream=BytesIO(transformed_html.encode("utf-8")),
            )
            result = converter.convert(stream)
            return result.document

        case ".docx" | ".pdf":
            result = converter.convert(path)
            return result.document

        case _:
            raise ValueError(f"Extension non supportée : {suffix} ({path.name})")

def xlsx_to_docling_document(xlsx_path: str) -> DoclingDocument:
    """
    Fonction de transformation du excel en Docling.
    """
    path = Path(xlsx_path)
    document = DoclingDocument(name=path.stem)
    document.add_title(text=path.stem.replace("_"," "))

    for sheet_name in pd.ExcelFile(xlsx_path).sheet_names:
        parsed = read_sheet_fixed_template(xlsx_path, sheet_name)
        df = parsed["data"]
        if df.empty:
            continue

        document.add_heading(text=parsed["doc_title"] or sheet_name, level=1)
        document.add_text(label=DocItemLabel.TEXT, text=parsed["doc_version"])

        columns = df.columns.tolist()
        identifier_col, *content_cols = columns

        for _, row in df.iterrows():
            # Niveau 2 : "Code : E10" — nom de colonne + valeur
            document.add_heading(text=f"{identifier_col} {row[identifier_col]}", level=2)

            # Niveau 3 : idem pour chaque colonne restante
            for col in content_cols:
                document.add_heading(text=f"{col}", level=3)
                document.add_text(label=DocItemLabel.TEXT, text=str(row[col]))

    return document
