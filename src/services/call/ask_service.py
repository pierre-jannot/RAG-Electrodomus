"""
Script Python des fonctions service d'appel utilisateur.
"""

from src.client.groq_client import GroqClient
from src.services.embedding.hybrid_search import hybrid_search
from src.services.extraction.regex_extractor import resolve_query_where_clause
from src.services.call.prompt_service import build_prompt
from src.utils.dict import get_leaf_strings

client = GroqClient()
# question = "Je n'arrive plus à fermer la porte de mon lave-linge 350, que dois-je faire ?"

def ask(request: str, request_parameters: str = None) -> str:
    """Fonction pour question utilisateur sur le corpus Electrodomus."""

    where_clause = resolve_query_where_clause(request_parameters if request_parameters else request)
    model_and_error = get_leaf_strings(where_clause)

    request = f"{' - '.join(model_and_error)} | {request}"

    results = hybrid_search(request, where_clause=where_clause, top_k=5)

    prompt = build_prompt(request, results)
    response = client.ask(prompt=prompt)

    return response
