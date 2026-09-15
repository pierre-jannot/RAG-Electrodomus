"""
Point d'entrée de l'API.
"""

from fastapi import FastAPI

from src.api.endpoints import sav


app = FastAPI(
    title="RAG-Electrodomus API",
    description="API exposant le pipeline RAG (retrieval + LLM).",
)

app.include_router(sav.router)
