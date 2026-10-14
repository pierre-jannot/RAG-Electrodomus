"""
Script des routes d'authentification.
"""

from fastapi import APIRouter, Depends

from src.api.security import verify_api_key

router = APIRouter(prefix="/auth", tags=["auth"], dependencies=[Depends(verify_api_key)])


@router.get("/check")
def check_api_key():
    """Renvoie 200 si la clé est valide, 401/403 sinon (géré par la dépendance)."""
    return {"valid": True}
