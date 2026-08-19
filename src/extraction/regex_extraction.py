"""
Script de fonctions REGEX pour récupérer :
- le ou les modèles présents dans le chunk/le document
- le ou les codes d'erreur présents dans le chunk/le document
- la date du document
"""

import re
from datetime import datetime


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

ERROR_CODE_PATTERN = re.compile(r"\bE\d{2}\b")


def extract_specific_models(text: str) -> list[str]:
    """Modèles précis mentionnés, ex: ['LV-451', 'LV-452']."""
    return sorted(set(MODEL_PATTERN.findall(text)))


def extract_bare_device_types(text: str) -> list[str]:
    """Types d'appareil mentionnés sans modèle précis, ex: ['FR']."""
    return sorted(set(DEVICE_TYPE_PATTERN.findall(text)))


def resolve_models(text: str) -> list[str] | None:
    """
    Résout les modèles/types associés à un texte selon la priorité :
    1. Modèle(s) précis (XX-999) s'ils existent
    2. Sinon type(s) d'appareil seul(s) (FR/WX/LV) s'ils existent
    3. Sinon None
    """
    specific = extract_specific_models(text)
    if specific:
        return specific

    bare = extract_bare_device_types(text)
    if bare:
        return bare

    return None


def resolve_chunk_models(chunk_text: str, document_level_models: list[str] | None) -> list[str] | None:
    """
    Applique la logique complète à l'échelle d'un chunk :
    - règles 1 & 2 : ce que le chunk contient lui-même (précis ou type seul)
    - règle 3 : repli sur les modèles du document si le chunk n'en contient aucun
    - règle 4 : None si ni le chunk ni le document n'en contiennent
    """
    chunk_result = resolve_models(chunk_text)
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

def resolve_chunk_errors(chunk_text: str, document_level_errors: list[str] | None) -> list[str] | None:
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


def extract_document_date(text: str) -> str | None:
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

            elif kind == "text":
                month_name, year = match.groups()
                month = MONTHS_FR[month_name.lower()]
                return f"{year}-{month:02d}"

        except ValueError:
            continue

    return None
