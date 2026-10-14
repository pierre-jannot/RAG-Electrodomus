"""
Script de mise en place de benchmark
"""

import json
from time import time

from src.client.groq_client import GroqClient
from src.client.ollama_client import OllamaClient
from src.core.config import load_api_settings
from src.services.call.prompt_service import build_prompt
from src.services.embedding.hybrid_search import hybrid_search
from src.services.extraction.regex_extractor import resolve_query_where_clause
from src.utils.dict import get_leaf_strings

ollama_client = OllamaClient()
groq_client = GroqClient()

api_settings = load_api_settings()


def read_benchmark_json(path: str) -> dict:
    """Lit le fichier JSON du benchmark à réaliser."""
    with open(path, encoding="utf-8") as file:
        executions = json.load(file)

    return executions


def write_benchmark_json(path: str, queries: dict) -> None:
    """Écrit les résultats du benchmark."""
    with open(path, "w", encoding="utf-8") as file:
        json.dump(queries, file, indent=4, ensure_ascii=False)


def run_benchmark_chunks(parameters: dict, question: str) -> dict:
    """Exécute une occurrence paramètres/question et retourne les
    chunks trouvés."""
    n_candidates = parameters["n_candidates"]
    rrf_candidates = parameters["top_k"]

    where_clause = resolve_query_where_clause(question, api_key=api_settings.fastapi_key)
    chunks = hybrid_search(question, where_clause, n_candidates, rrf_candidates)

    result_dict = {}

    for chunk_id, chunk in enumerate(chunks, start=1):
        result_dict[chunk_id] = chunk["id"]

    parameters_results = {"parameters": parameters,
                        "results": result_dict}

    return parameters_results


def run_benchmark_llm(parameters: dict, question: str) -> dict:
    """Exécute une occurrence paramètres/question et retourne la réponse
    LLM donnée."""
    method = parameters["method"]
    model = parameters["model"]

    t0 = time()

    where_clause = resolve_query_where_clause(question, api_key=api_settings.fastapi_key)
    model_and_error = get_leaf_strings(where_clause)
    request = f"{' - '.join(model_and_error)} | {question}"
    chunks = hybrid_search(request, where_clause=where_clause)
    prompt = build_prompt(request, chunks)

    if method == "groq":
        response = groq_client.ask(prompt, model=model)
    else:
        response = ollama_client.ask(prompt, model=model)

    results = {"reponse": response, "duration": time()-t0}

    parameters_results = {"parameters": parameters,
                        "results": results}

    return parameters_results


def run_chunk_benchmark_query(query: dict) -> dict:
    """Réalise l'exécution RAG de chaque couple de paramètres
    sur la question de la query."""
    question = query["question"]
    chunks_queries = {"question": question,
                    "results": []}
    for parameters in query["list"]:
        parameters_results = run_benchmark_chunks(parameters, question)
        chunks_queries["results"].append(parameters_results)

    return chunks_queries


def run_llm_benchmark_query(query: dict) -> dict:
    """Réalise l'exécution RAG & LLM de chaque couple de paramètres
    sur la question de la query."""
    question = query["question"]
    chunks_queries = {"question": question,
                    "results": []}
    for parameters in query["list"]:
        parameters_results = run_benchmark_llm(parameters, question)
        chunks_queries["results"].append(parameters_results)

    return chunks_queries


def run_benchmark() -> None:
    """Fonction de lancement du benchmark"""
    benchmarks = read_benchmark_json("src/benchmark/benchmark.json")
    result = {"chunks": [], "LLM": []}

    for benchmark in benchmarks:
        benchmark_type = benchmark["type"]
        queries = {}
        if benchmark_type == "chunks":
            for index, query in enumerate(benchmark["queries"], start=1):
                chunks_queries = run_chunk_benchmark_query(query)
                queries[index] = {"results": chunks_queries}

        if benchmark_type == "LLM":
            for index, query in enumerate(benchmark["queries"], start=1):
                llm_queries = run_llm_benchmark_query(query)
                queries[index] = {"results": llm_queries}

        result[benchmark_type].append(queries)

    write_benchmark_json("src/benchmark/results.json", result)


if __name__ == "__main__":
    run_benchmark()
