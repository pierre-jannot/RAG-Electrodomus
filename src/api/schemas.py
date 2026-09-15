"""
Modèles Pydantic définissant les contrats d'entrée/sortie de l'API.
"""

from pydantic import BaseModel, Field


class QuestionRequest(BaseModel):
    """Requête entrante : la question posée par l'utilisateur."""
 
    question: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="Question de l'utilisateur en langage naturel.",
        examples=["Je n'arrive plus à fermer la porte de mon lave-linge 350, que dois-je faire ?"],
    )

 
class AnswerResponse(BaseModel):
    """Réponse renvoyée par l'API."""
 
    answer: str
