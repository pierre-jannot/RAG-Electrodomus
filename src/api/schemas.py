"""
Modèles Pydantic définissant les contrats d'entrée/sortie de l'API.
"""

from enum import Enum

from pydantic import BaseModel, Field


class ApplianceType(str, Enum):
    """Types d'électroménager reconnus pour le filtrage explicite."""

    LV = "LV"  # Lave-vaisselle
    WX = "WX"  # Lave-linge (à ajuster si le libellé réel diffère)
    FR = "FR"  # Réfrigérateur (à ajuster si le libellé réel diffère)


class QuestionRequest(BaseModel):
    """Requête entrante : la question posée par l'utilisateur."""

    question: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="Question de l'utilisateur en langage naturel.",
        examples=["Je n'arrive plus à fermer la porte de mon lave-linge 350, que dois-je faire ?"],
    )


class DetailedQuestionRequest(BaseModel):
    """Question posée avec paramètres."""

    question: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="Question de l'utilisateur en langage naturel.",
        examples=["Je n'arrive plus à fermer la porte de mon lave-linge 350, que dois-je faire ?"],
    )
    appliance_type: ApplianceType = Field(
        ..., description="Type d'électroménager concerné."
    )
    model_id: str | None = Field(
        default=None, description="Identifiant du modèle, si connu."
    )
    error_code: str | None = Field(
        default=None, description="Code erreur mentionné, si applicable."
    )


class MetadataRequest(BaseModel):
    """Schéma des paramètres d'appel d'un ajout de métadonnées à Chroma."""

    key: str = Field(
        ...,
        min_length=1,
        max_length=15,
        description="Clé de la métadonnée à ajouter/modifier."
    )

    value: str |int = Field(
            description="Valeur de la métadonnée."
        )


class MetadataFilteredRequest(BaseModel):
    """Schéma des paramètres d'appel d'un ajout de métadonnées à Chroma."""

    filter_key: str = Field(
            ...,
            min_length=1,
            max_length=15,
            description="Clé de la métadonnée de filtrage."
    )

    filter_value: str |int = Field(
            description="Valeur de la métadonnée de filtrage."
        )

    key: str = Field(
        ...,
        min_length=1,
        max_length=15,
        description="Clé de la métadonnée à ajouter/modifier."
    )

    value: str |int = Field(
            description="Valeur de la métadonnée."
        )


class AnswerResponse(BaseModel):
    """Réponse renvoyée par l'API."""

    answer: str
