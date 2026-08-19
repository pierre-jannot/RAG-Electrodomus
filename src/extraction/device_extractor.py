"""
Script de fonctions REGEX pour récupérer le ou les
modèles présents dans le chunk/le document.
"""

import re


MODEL_PATTERN = re.compile(r"\b((?:FR|WX|LV)-\d{3,4})\b")

DEVICE_TYPE_PATTERN = re.compile(r"\b(FR|WX|LV)\b(?!-\d)")


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


def resolve_chunk_models(chunk_text: str, doc_level_models: list[str] | None) -> list[str] | None:
    """
    Applique la logique complète à l'échelle d'un chunk :
    - règles 1 & 2 : ce que le chunk contient lui-même (précis ou type seul)
    - règle 3 : repli sur les modèles du document si le chunk n'en contient aucun
    - règle 4 : None si ni le chunk ni le document n'en contiennent
    """
    chunk_result = resolve_models(chunk_text)
    if chunk_result is not None:
        return chunk_result

    return doc_level_models
