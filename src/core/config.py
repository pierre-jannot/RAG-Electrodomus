"""
core/config.py

Script de lecture des variables d'environnement
"""

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from dotenv import load_dotenv

from src.utils.var_type import str_to_bool

load_dotenv()


# --------------------------------------------------------------------------
# Groupes de paramètres
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class PathSettings:
    """Classe des paramètres de chemin."""
    source_dir: Path
    dir_name: str

    def validate(self) -> None:
        """Vérifie que le dossier source existe et est bien un dossier."""
        if not self.source_dir.exists():
            raise FileNotFoundError(
                f"RAG_SOURCE_DIR pointe vers un dossier inexistant : {self.source_dir}"
            )
        if not self.source_dir.is_dir():
            raise NotADirectoryError(
                f"RAG_SOURCE_DIR doit être un dossier, pas un fichier : {self.source_dir}"
            )


@dataclass(frozen=True)
class DatabaseSettings:
    """Classe des paramètres de ChromaDB."""
    db_dir: Path
    collection_name: str


@dataclass(frozen=True)
class ChunkingSettings:
    """Classe des paramètres de chunking/embedding."""
    max_tokens: int
    embed_model: str


@dataclass(frozen=True)
class SearchSettings:
    """Classe des paramètres de recherche hybride."""
    n_candidates: int
    rrf_candidates: int
    final_candidates: int
    cross_encoding: bool

    def validate(self) -> None:
        """Vérifie que n_candidates >= rrf_candidates >= rerank_candidates >= 1."""
        if not self.n_candidates >= self.rrf_candidates >= self.final_candidates >= 1:
            raise ValueError(
                "Il faut N_CANDIDATES >= RRF_CANDIDATES >= RERANK_CANDIDATES >= 1 "
                f"(reçu : {self.n_candidates}, {self.rrf_candidates}, "
                f"{self.final_candidates})"
            )


@dataclass(frozen=True)
class LLMSettings:
    """Classe des paramètres de LLM."""
    ollama_model: str
    groq_model: str
    groq_api_key: str | None


@dataclass(frozen=True)
class ApiSettings:
    """Sécurisation de l'API FastAPI."""
    fastapi_key: str | None


# --------------------------------------------------------------------------
# Fonctions de chargement (une par groupe, mises en cache)
# --------------------------------------------------------------------------

@lru_cache(maxsize=1)
def load_path_settings() -> PathSettings:
    """Charge et valide les chemins du corpus."""
    paths = PathSettings(
        source_dir=Path(os.getenv("RAG_SOURCE_DIR", "data/corpus")),
        dir_name=os.getenv("DIR_NAME", "Documentation_Electrodomus"),
    )
    paths.validate()
    return paths


@lru_cache(maxsize=1)
def load_database_settings() -> DatabaseSettings:
    """Charge les paramètres de la base Chroma."""
    return DatabaseSettings(
        db_dir=Path(os.getenv("DATABASE_PATH", "./chroma_db")),
        collection_name=os.getenv("COLLECTION_NAME", "rag_electrodomus"),
    )


@lru_cache(maxsize=1)
def load_embedding_settings() -> ChunkingSettings:
    """Charge les paramètres de chunking et d'embedding."""
    chunking = ChunkingSettings(
        max_tokens=int(os.getenv("MAX_TOKENS", "512")),
        embed_model=os.getenv("EMBED_MODEL", "BAAI/bge-m3"),
    )
    return chunking


@lru_cache(maxsize=1)
def load_search_settings() -> SearchSettings:
    """Charge les paramètres de recherche."""
    search = SearchSettings(
        n_candidates=int(os.getenv("N_CANDIDATES", "100")),
        rrf_candidates=int(os.getenv("RRF_CANDIDATES", "20")),
        final_candidates=int(os.getenv("FINAL_CANDIDATES", "10")),
        cross_encoding=str_to_bool(os.getenv("CROSS_ENCODING", "False"))
    )
    search.validate()
    return search


@lru_cache(maxsize=1)
def load_llm_settings() -> LLMSettings:
    """Charge les paramètres des modèles de langage."""
    return LLMSettings(
        ollama_model=os.getenv("OLLAMA_MODEL", "ministral-3:latest"),
        groq_model=os.getenv("GROQ_MODEL", "gpt-oss-20b"),
        groq_api_key=os.getenv("GROQ_API_KEY"),
    )


@lru_cache(maxsize=1)
def load_api_settings() -> ApiSettings:
    """Charge les paramètres de l'API."""
    return ApiSettings(fastapi_key=os.getenv("API_KEY"))
