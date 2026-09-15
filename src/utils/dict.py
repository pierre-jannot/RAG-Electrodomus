"""Fonctions utilitaires pour dictionnaires Python."""


def get_leaf_strings(obj) -> list[str]:
    """Récupère uniquement les strings au fond d'une structure dict/list imbriquée."""
    values = []

    if isinstance(obj, dict):
        for v in obj.values():
            values.extend(get_leaf_strings(v))
    elif isinstance(obj, list):
        for item in obj:
            values.extend(get_leaf_strings(item))
    elif isinstance(obj, str):
        values.append(obj)

    return values