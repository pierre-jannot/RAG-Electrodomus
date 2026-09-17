"""
Routes des modifications des métadonnées des chunks.
"""

from fastapi import APIRouter

from src.api.schemas import MetadataRequest, MetadataFilteredRequest
from src.database.database_functions import add_metadata_to_all, add_metadata_by_title


router = APIRouter(prefix="/metadatas", tags=["metadatas"])

@router.post("/add-metadata")
def add_metadata(request: MetadataRequest):
    """Ajoute ou modifie une métadonnées à tous les chunks."""

    add_metadata_to_all(key=request.key, value=request.value)
    return {"result": "OK"}


@router.post("/add-metadata-filter")
def add_metadata_filtered(request: MetadataFilteredRequest):
    """Ajoute ou modifie une métadonnées sur les chunks selectionnés."""

    add_metadata_by_title(filter_key=request.filter_key,
                          filter_value=request.filter_value,
                          key=request.key,
                          value=request.value)
    return {"result": "OK"}
