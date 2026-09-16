"""
Routes des options de paramètres pour l'appel SAV.
"""

from fastapi import APIRouter

from src.api.schemas import ApplianceType
from src.services.call.options_service import get_available_error_codes, get_available_models


router = APIRouter(prefix="/options", tags=["options"])

@router.get("/appliance-types", response_model=list[ApplianceType])
def list_appliance_types() -> list[ApplianceType]:
    """Liste fixe des types d'électroménager disponibles."""
    return list(ApplianceType)
 
 
@router.get("/{appliance_type}/models", response_model=list[str])
def list_models(appliance_type: ApplianceType) -> list[str]:
    """
    Liste des identifiants de modèle disponibles pour un type
    d'électroménager donné.
    """
    return get_available_models(appliance_type)
 
 
@router.get("/{appliance_type}/{model_id}/error-codes", response_model=list[str])
def list_error_codes(appliance_type: ApplianceType, model_id: str) -> list[str]:
    """
    Liste des codes erreur disponibles pour un modèle d'électroménager précis.
    """
    return get_available_error_codes(appliance_type, model_id)
