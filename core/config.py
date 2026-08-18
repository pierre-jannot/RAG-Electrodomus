"""
core/config.py

Script de lecture des variables d'environnement
"""

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    """
    Classe Settings contenant les variables d'environnement
    et des fonctions utilitaires.
    """
    source_dir: Path
    max_tokens: int
    min_tokens: int
    embed_model: str

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
    max_tokens = os.getenv("MAX_TOKENS", "512")
    min_tokens = os.getenv("MIN_TOKENS", "200")
    embed_model = os.getenv("EMBED_MODEL", "BAAI/bge-m3")

    settings = Settings(
        source_dir=Path(source_dir),
        max_tokens=max_tokens,
        min_tokens=min_tokens,
        embed_model=embed_model,
    )
    settings.validate_folder()
    return settings
