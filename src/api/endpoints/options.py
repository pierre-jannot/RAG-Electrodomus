"""
Routes des options de paramètres pour l'appel SAV.
"""

from fastapi import APIRouter, Depends

from src.api.schemas import ApplianceType
from src.api.security import verify_api_key_optional
from src.services.call.options_service import get_available_error_codes, get_available_models


router = APIRouter(prefix="/options", tags=["options"])

@router.get("/appliance-types", response_model=list[ApplianceType])
def list_appliance_types() -> list[ApplianceType]:
    """Liste fixe des types d'électroménager disponibles."""
    return list(ApplianceType)


@router.get("/{appliance_type}/models", response_model=list[str])
def list_models(
    appliance_type: ApplianceType,
    api_key: str | None = Depends(verify_api_key_optional)) -> list[str]:
    """
    Liste des identifiants de modèle disponibles pour un type
    d'électroménager donné.
    """
    return get_available_models(appliance_type, api_key)


@router.get("/{appliance_type}/{model_id}/error-codes", response_model=list[str])
def list_error_codes(
    appliance_type: ApplianceType,
    model_id: str,
    api_key: str | None = Depends(verify_api_key_optional)) -> list[str]:
    """
    Liste des codes erreur disponibles pour un modèle d'électroménager précis.
    """
    return get_available_error_codes(appliance_type, model_id, api_key)
