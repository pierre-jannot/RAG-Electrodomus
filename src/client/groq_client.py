"""
Fichier python du client ChatGPT avec les fonctions d'exécution par API.
"""

from dataclasses import dataclass
import logging
from pathlib import Path

from groq import (
    APIConnectionError,
    AuthenticationError,
    Groq,
    GroqError,
    RateLimitError,
)

from src.core.config import load_settings

logger = logging.getLogger(__name__)
settings = load_settings()
SYSTEM_PROMPT = Path("src/core/system_prompt.md").read_text(encoding="utf-8")


class GroqConfigError(Exception):
    """Erreur de clé API : invalide ou expirée"""


class GroqRequestError(Exception):
    """Erreur levée lors d'une erreur d'appel à l'API."""


@dataclass
class GroqClient:
    """Classe du client Groq, avec ses fonctions utilitaires d'appel."""

    host: str = "http://localhost:11434"
    default_model: str = settings.groq_model

    def __post_init__(self) -> None:
        self._client = Groq(api_key=settings.groq_api_key)

    def ask(
            self,
            prompt: str | None = None,
            system: str = SYSTEM_PROMPT,
            model: str | None = None,
    ) -> str:
        """Appel au LLM renseigné sur le client Groq."""
        messages: list[dict[str, str]] = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        try:
            response = self._client.chat.completions.create(
                model=model or self.default_model,
                messages=messages,
            )
        except AuthenticationError as e:
            logger.error("Clé API Groq invalide : %s", e)
            raise GroqConfigError("Clé API Groq invalide ou expirée.") from e
        except RateLimitError as e:
            logger.error("Quota / rate limit Groq atteint : %s", e)
            raise GroqRequestError(
                "Quota dépassé ou trop de requêtes envoyées (rate limit)."
            ) from e
        except APIConnectionError as e:
            logger.error("Impossible de joindre l'API Groq : %s", e)
            raise GroqRequestError(
                "Impossible de joindre l'API Groq (vérifie ta connexion réseau)."
            ) from e
        except GroqError as e:
            logger.error("Erreur API Groq (modèle=%s) : %s", model or self.default_model, e)
            raise GroqRequestError(str(e)) from e
 
        return response.choices[0].message.content


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        client = GroqClient()
        reponse = client.ask("Explique en une phrase ce qu'est un RAG (informatique, sur un corpus).")
        print(reponse)
    except (GroqConfigError, GroqRequestError) as e:
        print(f"Erreur : {e}")
