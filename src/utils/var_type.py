"""
Fichier de modification des types de variables.
"""

import os


def str_to_bool(name: str, default: bool = False) -> bool:
    """
    Transforme une string en bool.
    """
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in ("1", "true", "yes", "on")
