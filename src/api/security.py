"""
Script des fonctions de sécurisation par clé API des routes FastAPI.
"""

from src.core.config import load_settings
from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader


settings = load_settings()

API_KEY = settings.fastapi_key

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def verify_api_key(api_key: str | None = Security(api_key_header)) -> str:
    """Clé API obligatoire et valide."""
    if api_key is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Clé API manquante",
        )
    if api_key != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Clé API invalide",
        )
    return api_key


def verify_api_key_optional(api_key: str | None = Security(api_key_header)) -> str | None:
    """
    Clé API optionnelle :
    - absente -> None (comportement "public")
    - présente et valide -> la clé
    - présente et invalide -> erreur
    """
    if api_key is None:
        return None
    if api_key != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Clé API invalide",
        )
    return api_key