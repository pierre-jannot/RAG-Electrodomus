"""Fonctions utilitaires pour dictionnaires Python."""


EXCLUDED_KEYS = {"access"}


def get_leaf_strings(obj, excluded_keys: set[str] = EXCLUDED_KEYS) -> list[str]:
    """Récupère uniquement les strings au fond d'une structure dict/list imbriquée,
    en ignorant les clés exclues (et tout ce qu'elles contiennent)."""
    values = []

    if isinstance(obj, dict):
        for key, v in obj.items():
            if key in excluded_keys:
                continue
            values.extend(get_leaf_strings(v, excluded_keys))
    elif isinstance(obj, list):
        for item in obj:
            values.extend(get_leaf_strings(item, excluded_keys))
    elif isinstance(obj, str):
        values.append(obj)

    return values
