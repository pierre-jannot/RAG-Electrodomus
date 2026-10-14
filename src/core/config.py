"""
core/config.py

Script de lecture des variables d'environnement
"""

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


def env_bool(name: str, default: bool = False) -> bool:
        value = os.getenv(name)
        if value is None:
            return default
        return value.strip().lower() in ("1", "true", "yes", "on")


@dataclass(frozen=True)
class Settings:
    """
    Classe Settings contenant les variables d'environnement
    et des fonctions utilitaires.
    """
    source_dir: Path
    db_dir: Path
    dir_name: str
    collection_name: str
    max_tokens: int
    min_tokens: int
    embed_model: str
    ollama_model: str
    groq_model: str
    groq_api_key: str
    fastapi_key: str
    n_candidates: int
    rrf_candidates: int
    rerank_candidates: int
    cross_encode: bool

    def validate_folder(self) -> None:
        """Validation des variables d'environnement au lancement du projet"""
        if not self.source_dir.exists():
            raise FileNotFoundError(
                f"RAG_SOURCE_DIR pointe vers un dossier inexistant : {self.source_dir}"
            )
        if not self.source_dir.is_dir():
            raise NotADirectoryError(
                f"RAG_SOURCE_DIR doit être un dossier, pas un fichier : {self.source_dir}"
            )


def load_settings() -> Settings:
    """
    Fonction d'initialisation des variables d'environnement.
    """
    source_dir = os.getenv("RAG_SOURCE_DIR", "data/corpus")
    db_dir = os.getenv("DATABASE_PATH", "./chroma_db")
    dir_name = os.getenv("DIR_NAME", "Documentation_Electrodomus")
    collection_name = os.getenv("COLLECTION_NAME", "rag_electrodomus")
    max_tokens = os.getenv("MAX_TOKENS", "512")
    min_tokens = os.getenv("MIN_TOKENS", "200")
    embed_model = os.getenv("EMBED_MODEL", "BAAI/bge-m3")
    ollama_model = os.getenv("OLLAMA_MODEL", "ministral-3:latest")
    groq_model = os.getenv("GROQ_MODEL", "gpt-oss-20b")
    groq_api_key = os.getenv("GROQ_API_KEY", None)
    fastapi_key = os.getenv("API_KEY", None)
    n_candidates = int(os.getenv("N_CANDIDATES", 100))
    rrf_candidates = int(os.getenv("RRF_CANDIDATES", 20))
    rerank_candidates = int(os.getenv("RERANK_CANDIDATES", 10))
    cross_encode = env_bool(os.getenv("CROSS_ENCODE", False))

    settings = Settings(
        source_dir=Path(source_dir),
        db_dir=Path(db_dir),
        dir_name=dir_name,
        collection_name=collection_name,
        max_tokens=max_tokens,
        min_tokens=min_tokens,
        embed_model=embed_model,
        ollama_model=ollama_model,
        groq_model=groq_model,
        groq_api_key=groq_api_key,
        fastapi_key=fastapi_key,
        n_candidates=n_candidates,
        rrf_candidates=rrf_candidates,
        rerank_candidates=rerank_candidates,
        cross_encode=cross_encode
    )
    settings.validate_folder()
    return settings
