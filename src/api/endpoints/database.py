"""
Routes d'appel à la mise à jour/création de la base de données.
"""

from fastapi import APIRouter, Depends

from src.api.security import verify_api_key
from src.services.database_service import populate_database, synchronize_database


router = APIRouter(prefix="/database", tags=["database"], dependencies=[Depends(verify_api_key)])

@router.get("/initialize")
def intialize():
    """Crée la base de données avec le corpus interne."""
    populate_database()
    return {"result": "OK"}


@router.get("/synchronize")
def update():
    """Met à jour la base de données avec le corpus interne."""
    result = synchronize_database()
    return result
