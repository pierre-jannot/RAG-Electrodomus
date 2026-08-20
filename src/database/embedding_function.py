"""
Script de la classe d'embedding pour Chroma.

Permet de donner à Chroma la fonction avec laquelle
la vectorisation est réalisée.
"""

from typing import Any, Dict, Optional

from chromadb import Documents, EmbeddingFunction, Embeddings
from chromadb.utils.embedding_functions import register_embedding_function
from sentence_transformers import SentenceTransformer

from src.core.config import load_settings

settings = load_settings()


@register_embedding_function
class ChromaEmbeddingFunction(EmbeddingFunction):
    """Wrapper sentence-transformers pour le modèle choisi en config,
    utilisable par Chroma."""

    def __init__(
        self,
        model_name: str = settings.embed_model,
        device: Optional[str] = None,
    ):
        self.model_name = model_name
        self.device = device
        self.model = SentenceTransformer(model_name, device=device)

    def __call__(self, input: Documents) -> Embeddings:
        embeddings = self.model.encode(
            input,
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
    def build_from_config(config: Dict[str, Any]) -> "ChromaEmbeddingFunction":
        return ChromaEmbeddingFunction(
            model_name=config["model_name"],
            device=config.get("device"),
        )
