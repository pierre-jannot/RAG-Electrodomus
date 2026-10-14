"""
Script de la classe d'embedding pour Chroma.

Permet de donner à Chroma la fonction avec laquelle
la vectorisation est réalisée.
"""

from functools import lru_cache
from typing import Any, Dict, Optional

from chromadb import Documents, EmbeddingFunction, Embeddings
from chromadb.utils.embedding_functions import register_embedding_function
from sentence_transformers import SentenceTransformer

from src.core.config import load_embedding_settings

embedding_settings = load_embedding_settings()


@lru_cache(maxsize=4)
def _load_model(model_name: str, device: Optional[str]) -> SentenceTransformer:
    """Chargement du modèle, avec cache"""
    return SentenceTransformer(model_name, device=device)


@register_embedding_function
class ChromaDenseEmbeddingFunction(EmbeddingFunction):
    """Wrapper sentence-transformers pour le modèle choisi en config,
    utilisable par Chroma."""

    def __init__(
        self,
        model_name: str = embedding_settings.embed_model,
        device: Optional[str] = None,
    ):
        self.model_name = model_name
        self.device = device
        self.model = _load_model(model_name, device)

    def __call__(self, file_input: Documents) -> Embeddings:
        embeddings = self.model.encode(
            file_input,
            normalize_embeddings=True,
            batch_size=8,
            show_progress_bar=False,
        )
        return embeddings.tolist()

    @staticmethod
    def name() -> str:
        return "chroma-sentence-transformers-ef"

    def get_config(self) -> Dict[str, Any]:
        return {"model_name": self.model_name, "device": self.device}

    @staticmethod
    def build_from_config(config: Dict[str, Any]) -> "ChromaDenseEmbeddingFunction":
        return ChromaDenseEmbeddingFunction(
            model_name=config["model_name"],
            device=config.get("device"),
        )
