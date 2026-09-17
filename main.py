"""
Point d'entrée de l'API.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.endpoints import sav, options, metadata


app = FastAPI(
    title="RAG-Electrodomus API",
    description="API exposant le pipeline RAG (retrieval + LLM).",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(sav.router)
app.include_router(options.router)
app.include_router(metadata.router)
