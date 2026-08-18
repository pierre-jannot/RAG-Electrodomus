"""
core/config.py

Script de lecture des variables d'environnement
"""

from __future__ import annotations

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

    settings = Settings(
        source_dir=Path(source_dir),
    )
    settings.validate_folder()
    return settings
