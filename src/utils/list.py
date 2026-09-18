"""Fichier Python des fonctions utilitaires pour listes"""


def as_list(value) -> list:
    """Normalise une valeur de métadonnée (liste, scalaire, ou absente) en liste."""
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]
