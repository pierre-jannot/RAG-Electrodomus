"""
docling_converter.py

Wrapper autour de Docling DocumentConverter pour les formats du projet :
PDF (texte), DOCX, HTML, XLSX.

Responsabilité unique de ce module : configurer Docling et produire des
DoclingDocument bruts. La transformation vers le schéma pivot se fait
dans adapter.py, pas ici.
"""

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterator

from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import (
    DocumentConverter,
    ExcelFormatOption,
    PdfFormatOption,
)
from docling_core.types.doc import DoclingDocument

logger = logging.getLogger(__name__)

# Formats gérés par le projet
SUPPORTED_FORMATS = [
    InputFormat.PDF,
    InputFormat.DOCX,
    InputFormat.HTML,
    InputFormat.XLSX,
]

# Extensions traitées par le projet
SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".html", ".xlsx"}


@dataclass
class ConvertedDocument:
    """
    Classe de document importé avec Docling.

    relative_path conserve la structure de sous-dossiers depuis la racine
    scannée
    """

    document: DoclingDocument
    source_path: Path
    relative_path: Path

    @property
    def folder_tags(self) -> list[str]:
        """
        Les composants de sous-dossiers, dans l'ordre, en excluant le nom
        de fichier.
        """
        return list(self.relative_path.parent.parts)


@dataclass
class ConversionFailure:
    """Trace un échec de conversion sans interrompre le traitement du lot."""

    relative_path: Path
    error: str


@dataclass
class ConversionBatchResult:
    """Résultat d'une conversion de dossier : succès + échecs séparés."""

    documents: list[ConvertedDocument] = field(default_factory=list)
    failures: list[ConversionFailure] = field(default_factory=list)


def build_converter() -> DocumentConverter:
    """
    Construit le DocumentConverter Docling configuré pour le projet.

    Points clés :
    - do_picture_description / do_picture_classification désactivés :
      pas d'images dans le corpus, inutile de charger ces modèles
      (évite aussi un bug connu sur xlsx quand ces options sont actives).
    - OCR désactivé sur le pipeline PDF : les PDF du corpus sont
      exclusivement du texte natif.
    """
    pdf_options = PdfPipelineOptions()
    pdf_options.do_ocr = False
    pdf_options.do_picture_description = False
    pdf_options.do_picture_classification = False

    return DocumentConverter(
        allowed_formats=SUPPORTED_FORMATS,
        format_options={
            InputFormat.PDF: PdfFormatOption(pipeline_options=pdf_options),
            InputFormat.XLSX: ExcelFormatOption(),
        },
    )


def convert_file(path: Path, converter: DocumentConverter | None = None) -> DoclingDocument:
    """
    Convertit un fichier unique en DoclingDocument.

    Lève une exception si la conversion échoue — à charge de l'appelant
    de décider s'il logge et continue (cf. convert_directory) ou s'il
    interrompt le traitement.
    """
    converter = converter or build_converter()
    result = converter.convert(path)
    return result.document


def convert_directory(
    directory: Path,
    converter: DocumentConverter | None = None,
    recursive: bool = True,
) -> ConversionBatchResult:
    """
    Convertit tous les fichiers supportés d'un dossier, y compris ses
    sous-dossiers par défaut (recursive=True).

    Le chemin relatif à `directory` (sous-dossiers inclus) est conservé
    dans chaque ConvertedDocument — c'est la métadonnée d'organisation
    du corpus, distincte des métadonnées internes au fichier (auteur,
    date de création...) que l'adaptateur ira chercher dans le contenu.

    Ne s'arrête pas au premier échec : un fichier corrompu ou dans un
    format inattendu ne doit pas bloquer le traitement du reste du lot.
    Les échecs sont collectés dans batch.failures pour inspection/retry.
    """
    converter = converter or build_converter()
    batch = ConversionBatchResult()

    for path in _iter_supported_files(directory, recursive=recursive):
        relative_path = path.relative_to(directory)
        try:
            logger.info("Conversion de %s", relative_path)
            document = convert_file(path, converter=converter)
            batch.documents.append(
                ConvertedDocument(
                    document=document,
                    source_path=path,
                    relative_path=relative_path,
                )
            )
        except Exception as exc:  # noqa: BLE001 — on veut catcher large ici
            logger.warning("Échec de conversion pour %s : %s", relative_path, exc)
            batch.failures.append(ConversionFailure(relative_path=relative_path, error=str(exc)))

    return batch


def _iter_supported_files(directory: Path, recursive: bool = True) -> Iterator[Path]:
    walker = directory.rglob("*") if recursive else directory.glob("*")
    for path in sorted(walker):
        if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS:
            yield path


if __name__ == "__main__":
    from core.config import load_settings

    logging.basicConfig(level=logging.INFO)

    settings = load_settings()
    result_batch = convert_directory(settings.source_dir)

    print(f"{len(result_batch.documents)} fichiers convertis avec succès")
    for converted in result_batch.documents:
        print(f"  - {converted.relative_path}  (tags: {converted.folder_tags})")

    print(f"{len(result_batch.failures)} échecs")
    for failure in result_batch.failures:
        print(f"  - {failure.relative_path} : {failure.error}")