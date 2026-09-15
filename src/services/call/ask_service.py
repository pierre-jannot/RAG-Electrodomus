"""
Script Python des fonctions service d'appel utilisateur.
"""

from src.client.groq_client import GroqClient
from src.services.embedding.hybrid_search import hybrid_search
from src.services.extraction.regex_extractor import resolve_query_where_clause
from src.services.call.prompt_service import build_prompt

client = GroqClient()
# question = "Je n'arrive plus à fermer la porte de mon lave-linge 350, que dois-je faire ?"

def ask(question: str) -> str:
    """Fonction pour question utilisateur sur le corpus Electrodomus."""

    where_clause = resolve_query_where_clause(question)

    results = hybrid_search(question, where_clause=where_clause, top_k=5)

    if not results:
        results = ("Aucun résultat — vérifiez que le filtre correspond à des chunks existants "
                "(collection.get(where=where_clause) pour diagnostiquer).")

    prompt = build_prompt(question, results)
    # response = client.ask(prompt=prompt)

    return prompt
