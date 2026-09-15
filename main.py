"""
Point d'entrée de l'API.
"""

from fastapi import FastAPI, HTTPException

from src.api.schemas import AnswerResponse, QuestionRequest
from src.client.groq_client import GroqConfigError, GroqRequestError
from src.services.call.ask_service import ask

app = FastAPI(
    title="RAG-Electrodomus API",
    description="API exposant le pipeline RAG (retrieval + LLM).",
)

@app.post("/ask")
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