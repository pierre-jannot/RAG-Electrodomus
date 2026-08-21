"""
Script de fonctions REGEX pour récupérer :
- le ou les modèles présents dans le chunk/le document
- le ou les codes d'erreur présents dans le chunk/le document
- la date du document
"""

import re
from datetime import datetime

from docling_core.transforms.chunker import DocChunk


MONTHS_FR = {
    "janvier": 1, "février": 2, "mars": 3, "avril": 4, "mai": 5, "juin": 6,
    "juillet": 7, "août": 8, "septembre": 9, "octobre": 10, "novembre": 11, "décembre": 12,
}
MONTHS_PATTERN = "|".join(MONTHS_FR.keys())

SPACE = r"[\s\xa0]+"

DATE_PATTERNS = [
    (re.compile(r"\b(\d{1,2})[/\-](\d{4})\b"), "numeric"),
    (re.compile(rf"\b({MONTHS_PATTERN}){SPACE}(\d{{4}})\b", re.IGNORECASE), "text"),
]

MODEL_PATTERN = re.compile(r"\b((?:FR|WX|LV)-\d{3,4})\b")

DEVICE_TYPE_PATTERN = re.compile(r"\b(FR|WX|LV)\b(?!-\d)")

SECTION_PATTERN = re.compile(
    r"Mod[eè]les?\s+concern[ée]s?\s*:?\s*\n?(.*?)(?:\n\s*\n|\n#{1,6}\s|\Z)",
    re.IGNORECASE | re.DOTALL,
)

PARENTHESES_PATTERN = re.compile(r"\([^)]*\)")

ERROR_CODE_PATTERN = re.compile(r"\bE\d{2}\b")


def extract_specific_models(text: str) -> list[str]:
    """Modèles précis mentionnés, ex: ['LV-451', 'LV-452']."""
    return sorted(set(MODEL_PATTERN.findall(text)))


def extract_bare_device_types(text: str) -> list[str]:
    """Types d'appareil mentionnés sans modèle précis, ex: ['FR']."""
    return sorted(set(DEVICE_TYPE_PATTERN.findall(text)))


def resolve_models(text: str, path: list[str] = []) -> list[str] | None:
    """
    Résout les modèles/types associés à un texte selon la priorité :
    1. Modèle(s) précis (XX-999) s'ils existent
    2. Sinon type(s) d'appareil seul(s) (FR/WX/LV) s'ils existent
    3. Sinon None
    """
    if "Procedures_SAV" in path:
        match = SECTION_PATTERN.search(text)
        if not match:
            return None

        section_text = match.group(1)

        first_sentence = section_text.split(".", 1)[0]

        text = PARENTHESES_PATTERN.sub("", first_sentence)

    specific = extract_specific_models(text)
    if specific:
        return specific

    bare = extract_bare_device_types(text)
    if bare:
        return bare

    return None


def resolve_chunk_models(
        chunk: DocChunk,
        text: str,
        document_level_models: list[str] | None, path: list[str]
        ) -> list[str] | None:
    """
    Applique la logique complète à l'échelle d'un chunk :
    - règles 1 & 2 : ce que le chunk contient lui-même (précis ou type seul)
    - règle 3 : repli sur les modèles du document si le chunk n'en contient aucun
    - règle 4 : None si ni le chunk ni le document n'en contiennent
    """
    if "Procedures_SAV" in path:
        headings = chunk.meta.headings or []
        if headings:
            last_heading = headings[-1]
            heading_result = resolve_models(last_heading)
            if heading_result is not None:
                return heading_result

        return document_level_models

    chunk_result = resolve_models(text)
    if chunk_result is not None:
        return chunk_result

    return document_level_models


def resolve_errors(text: str) -> list[str]:
    """
    Extrait tous les codes d'erreur au format EXX (E + 2 chiffres),
    sans doublons, dans l'ordre d'apparition dans le texte.
    """
    seen = []
    for match in ERROR_CODE_PATTERN.findall(text):
        if match not in seen:
            seen.append(match)

    if seen:
        return seen

    return None


def resolve_chunk_errors(
        chunk_text: str,
        document_level_errors: list[str] | None
        ) -> list[str] | None:
    """
    Applique la logique complète à l'échelle d'un chunk :
    - règles 1 & 2 : ce que le chunk contient lui-même (précis ou type seul)
    - règle 3 : repli sur les erreurs du document si le chunk n'en contient aucun
    - règle 4 : None si ni le chunk ni le document n'en contiennent
    """
    chunk_result = resolve_errors(chunk_text)
    if chunk_result is not None:
        return chunk_result

    return document_level_errors


def resolve_date(text: str) -> str | None:
    """
    Cherche une date mois/année dans le texte (format MM/YYYY ou "mois YYYY").
    Retourne YYYY-MM, ou None si rien trouvé.
    """
    for pattern, kind in DATE_PATTERNS:
        match = pattern.search(text)
        if not match:
            continue

        try:
            if kind == "numeric":
                month, year = match.groups()
                datetime(int(year), int(month), 1)  # validation du mois (1-12)
                return f"{year}-{int(month):02d}"

            if kind == "text":
                month_name, year = match.groups()
                month = MONTHS_FR[month_name.lower()]
                return f"{year}-{month:02d}"

        except ValueError:
            continue

    return None


def resolve_chunk_page(chunk: DocChunk) -> int | None:
    """Retourne le numéro de la première page couverte par le chunk, ou None si absent."""
    for item in chunk.meta.doc_items:
        for prov in item.prov:
            if prov.page_no is not None:
                return prov.page_no
    return None


def build_element_clause(element_list: list[str], element_name: str) -> dict | None:
    """
    Fonction de formattage des modèles et erreurs en where clause Chroma.
    """
    if len(element_list)>1:
        element_clause = []
        for element in element_list:
            element_clause.append({f"{element_name}": {"$contains": element}})
        return {"$or": element_clause}
    if len(element_list)==1:
        return {f"{element_name}": {"$contains": element_list[0]}}
    return None


def resolve_query_where_clause(question: str) -> dict:
    """Fonction de construction de la clause de filtrage de la query Chroma."""
    models = extract_specific_models(question)
    errors = resolve_errors(question)
    models_clause = build_element_clause(models, "models")
    errors_clause = build_element_clause(errors, "errors")
    if models_clause and errors_clause:
        return {"$and": [models_clause, errors_clause]}
    if models_clause:
        return models_clause
    if errors_clause:
        return errors_clause
    return None
