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

def ask(request: str) -> str:
    """Fonction pour question utilisateur sur le corpus Electrodomus."""

    where_clause = resolve_query_where_clause(request)
    model_and_error = get_leaf_strings(where_clause)

    request = f"{' - '.join(model_and_error)} | {request}"

    results = hybrid_search(request, where_clause=where_clause, top_k=5)

    prompt = build_prompt(request, results)
    response = client.ask(prompt=prompt)

    return response


def ask_filtered(
        request: str,
        appliance_type: str | None,
        appliance_id: str | None,
        error_code: str | None):
    """Fonction d'appel avec paramètres."""
    if appliance_type and appliance_id:
        filter_str = f"{appliance_type}-{appliance_id}"
    elif appliance_type:
        filter_str = appliance_type
    else:
        filter_str = ""
    if error_code:
        filter_str += f" - {error_code}"

    if filter_str:
        request = f"{filter_str} | {request}"

    where_clause = resolve_query_where_clause(filter_str)
    model_and_error = get_leaf_strings(where_clause)

    request = f"{' - '.join(model_and_error)} | {request}"

    results = hybrid_search(request, where_clause=where_clause, top_k=5)

    prompt = build_prompt(request, results)
    response = client.ask(prompt=prompt)

    return response
