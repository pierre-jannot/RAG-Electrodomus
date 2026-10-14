"""Fonctions utilitaires pour dictionnaires Python."""


EXCLUDED_KEYS = {"access"}


def get_leaf_strings(obj) -> list[str]:
    """Récupère uniquement les strings au fond d'une structure dict/list imbriquée,
    en ignorant les clés exclues (et tout ce qu'elles contiennent)."""
    values = []

    if isinstance(obj, dict):
        for key, v in obj.items():
            if key in EXCLUDED_KEYS:
                continue
            values.extend(get_leaf_strings(v))
    elif isinstance(obj, list):
        for item in obj:
            values.extend(get_leaf_strings(item))
    elif isinstance(obj, str):
        values.append(obj)

    return values
