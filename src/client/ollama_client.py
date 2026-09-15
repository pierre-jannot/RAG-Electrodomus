"""
Fichier python du client Ollama avec les fonctions d'exécution des modèles.
"""

from dataclasses import dataclass
import logging

import ollama
from ollama import ResponseError

from src.core.config import load_settings

logger = logging.getLogger(__name__)
settings = load_settings()


class OllamaConnectionError(Exception):
    """Classe de l'erreur de connexion au client Ollama."""


class OllamaModelError(Exception):
    """Classe de l'erreur d'exécution du modèle par Ollama."""


@dataclass
class OllamaClient:
    """Classe du client Ollama, avec ses fonctions utilitaires d'appel."""

    host: str = "http://localhost:11434"
    default_model: str = settings.ollama_model
    default_think: bool = False

    def __post_init__(self) -> None:
        self._client = ollama.Client(host=self.host)

    def ask(
            self,
            prompt: str,
            system: str | None = None,
            model: str | None = None,
            think: bool |None = None,
            stream: bool = False,
    ) -> str:
        """Appel au LLM initialisé sur le client Ollama."""
        messages: list[dict[str, str]] = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        try:
            response = self._client.chat(
                model=model or self.default_model,
                messages=messages,
                think=self.default_think if think is None else think,
                stream=False,
            )

        except ResponseError as e:
            logger.error("Erreur Ollama (modèle=%s) : %s", model or self.default_model, e)
            raise OllamaModelError(str(e)) from e
        
        except ConnectionError as e:
            logger.error("Impossible de joindre Ollama sur %s : %s", self.host, e)
            raise OllamaConnectionError(
                f"Serveur Ollama injoignable sur {self.host}. "
                f"Vérifie qu'il tourne bien (`ollama serve`)."
            ) from e
        
        return response["message"]["content"]

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    client = OllamaClient()
    try:
        reponse = client.ask("Explique en une phrase ce qu'est un RAG (informatique, sur un corpus).")
        print(reponse)
    except (OllamaConnectionError, OllamaModelError) as e:
        print(f"Erreur : {e}")