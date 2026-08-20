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
from docling_core.types.doc import DoclingDocument, DocItemLabel, SectionHeaderItem, ContentLayer

import pandas as pd

from src.extraction.xlsx_extractor import read_sheet_fixed_template
from src.extraction.html_extractor import promote_summary_to_heading


FIRST_LINE_NOISE_VALUES = {
    "ELECTRODOMUS",
    "ELECTRODOMUS — Documentation interne",
}

NOISE_TEXTS = ["Ce bulletin prévaut sur la documentation produit antérieure (manuels et référentiel des codes erreur) pour les points qu'il traite."]


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
            document = xlsx_to_docling_document(str(path))

        case ".html" | ".htm":
            raw_html = path.read_text(encoding="utf-8")
            transformed_html = promote_summary_to_heading(raw_html)
            stream = DocumentStream(
                name=path.name,
                stream=BytesIO(transformed_html.encode("utf-8")),
            )
            document = converter.convert(stream).document

        case ".docx" | ".pdf":
            result = converter.convert(path)
            document = normalize_first_lines(result.document)

        case _:
            raise ValueError(f"Extension non supportée : {suffix} ({path.name})")

    document = strip_formatting(document=document)
    document = strip_noise_lines(document=document, noise_texts=NOISE_TEXTS)
    return document


def promote_to_heading(item, target_level: int = 1) -> SectionHeaderItem:
    """Construit un SectionHeaderItem qui réutilise le self_ref exact de
    l'item remplacé — aucun nouveau ref créé, donc pas de risque de collision
    avec add_heading() lors d'un delete_items() ultérieur."""
    return SectionHeaderItem(
        self_ref=item.self_ref,
        parent=item.parent,
        children=item.children,
        content_layer=item.content_layer,
        label=DocItemLabel.SECTION_HEADER,
        prov=item.prov,
        orig=item.orig,
        text=item.text,
        formatting=getattr(item, "formatting", None),
        hyperlink=getattr(item, "hyperlink", None),
        level=target_level,
    )


def normalize_first_lines(document: DoclingDocument, target_level: int = 0) -> DoclingDocument:
    """
    - la 1re ligne de contenu (body) est supprimée
    - la 2e ligne devient le titre principal du document
    """
    body_items = [item for item in document.texts if item.content_layer == ContentLayer.BODY]

    if not body_items:
        return document

    first_item = body_items[0]

    if first_item.text.strip() in FIRST_LINE_NOISE_VALUES:
        if len(body_items) < 2:
            document.delete_items(node_items=[first_item])
            return document
        title_item = body_items[1]
        document.delete_items(node_items=[first_item])
    else:
        title_item = first_item

    if isinstance(title_item, SectionHeaderItem):
        title_item.level = target_level
    else:
        new_heading = promote_to_heading(title_item, target_level=1)
        new_heading.level = target_level
        document.replace_item(new_item=new_heading, old_item=title_item)

    return document


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

        document.add_heading(text=sheet_name, level=1)
        document.add_text(label=DocItemLabel.TEXT, text=parsed["doc_version"])

        columns = df.columns.tolist()
        identifier_col, *content_cols = columns

        for _, row in df.iterrows():
            # Niveau 2 : "Code : E10" — nom de colonne + valeur
            document.add_heading(text=f"{identifier_col} {row[identifier_col]}", level=2)

            # Niveau 3 : idem pour chaque colonne restante
            for col in content_cols:
                document.add_text(label=DocItemLabel.TEXT, text=f"{col} : " + str(row[col]))

    return document


def strip_formatting(document: DoclingDocument) -> DoclingDocument:
    """
    Retire toute mise en forme (gras, italique...) portée par les items
    texte du document, pour un export markdown sans ** ou autres marqueurs.
    """
    for item in document.texts:
        if getattr(item, "formatting", None) is not None:
            item.formatting = None
    return document


def strip_noise_lines(document: DoclingDocument, noise_texts: list[str]) -> DoclingDocument:
    """
    Supprime tous les items dont le texte correspond exactement à l'une
    des chaînes fournies dans noise_texts — utile pour des mentions
    récurrentes sans valeur informative (bandeaux, mentions légales
    répétées, numéros de version en pied de page, etc.).
    """
    noise_set = set(noise_texts)
    items_to_delete = [
        item for item in document.texts
        if item.text.strip() in noise_set
    ]

    if items_to_delete:
        document.delete_items(node_items=items_to_delete)

    return document
