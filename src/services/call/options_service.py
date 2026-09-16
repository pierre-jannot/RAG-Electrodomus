"""
Script Python permettant la récupération des métadonnées pour
déterminer un dictionnaire avec le format "type":["numéro":["erreur"]]
afin de changer dynamiquement les valeurs sélectionnables par
l'utilisateur de l'interface SAV.
"""

from functools import lru_cache

from src.api.schemas import ApplianceType
from src.services.embedding.hybrid_search import get_dense_collection
from src.utils.list import as_list


@lru_cache(maxsize=1)
def _all_metadatas() -> list[dict]:
    """
    Charge une seule fois toutes les métadonnées de la collection.
    """
    collection = get_dense_collection()
    result = collection.get(include=["metadatas"])
    return [meta for meta in result.get("metadatas", []) if meta]


@lru_cache(maxsize=1)
def build_metadata_index() -> dict[str, dict[str, list[str]]]:
    """
    Construit l'index {type: {modèle: [codes erreur]}} en un seul passage
    sur toutes les métadonnées.
    """
    index: dict[str, dict[str, set[str]]] = {t.value: {} for t in ApplianceType}

    for meta in _all_metadatas():
        models = as_list(meta.get("models"))
        errors = as_list(meta.get("errors"))

        for value in models:
            if "-" not in value:
                continue

            appliance_type, model_id = value.split("-", 1)
            if appliance_type not in index:
                continue

            index[appliance_type].setdefault(model_id, set()).update(errors)


    return {
        appliance_type: {model_id: sorted(codes) for model_id, codes in models_dict.items()}
        for appliance_type, models_dict in index.items()
    }


def get_available_models(appliance_type: ApplianceType) -> list[str]:
    """
    Liste des numéros de modèle disponibles pour un type d'électroménager.
    """
    return sorted(build_metadata_index()[appliance_type.value].keys())


def get_available_error_codes(appliance_type: ApplianceType, model_id: str) -> list[str]:
    """
    Liste des codes erreur disponibles pour un modèle précis d'un type
    d'électroménager donné.
    """
    return build_metadata_index()[appliance_type.value].get(model_id, [])
