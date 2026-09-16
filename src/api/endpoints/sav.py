"""
Fichier Python des routes du "SAV".
"""

from fastapi import APIRouter, HTTPException

from src.api.schemas import AnswerResponse, QuestionRequest, DetailedQuestionRequest
from src.client.groq_client import GroqConfigError, GroqRequestError
from src.services.call.ask_service import ask, ask_filtered

router = APIRouter(prefix="/sav", tags=["sav"])


@router.post("/ask")
def ask_question(request: QuestionRequest) -> AnswerResponse:
    """
    Reçoit une question utilisateur, exécute le pipeline RAG complet
    et renvoie la réponse.
    """
    try:
        answer = ask(request.question)
    except GroqConfigError as e:
        raise HTTPException(
            status_code=500, detail="Erreur de configuration du service LLM."
        ) from e
    except GroqRequestError as e:
        raise HTTPException(
            status_code=503, detail="Service LLM momentanément indisponible."
        ) from e

    return AnswerResponse(answer=answer)


@router.post("/ask-filtered")
def ask_question_filtered(request: DetailedQuestionRequest) -> AnswerResponse:
    """
    Reçoit une question utilisateur avec des where_clause, exécute le pipeline RAG complet
    et renvoie la réponse.
    """
    try:
        answer = ask_filtered(
            request.question,
            request.appliance_type,
            request.model_id,
            request.error_code)
    except GroqConfigError as e:
        raise HTTPException(
            status_code=500, detail="Erreur de configuration du service LLM."
        ) from e
    except GroqRequestError as e:
        raise HTTPException(
            status_code=503, detail="Service LLM momentanément indisponible."
        ) from e

    return AnswerResponse(answer=answer)
