"""
Fichier Python de fonctions utilitaires de construction de prompt pour appel LLM.
"""


def build_rag_answer(rag_results: list[dict]) -> str:
    """
    Fonction de formattage des données RAG en chaîne de caractères.
    """
    rag_prompt = ""

    for rank, item in enumerate(rag_results, start=1):
        rag_prompt += f"--- Rang : {rank} (score reranker={item['score']:.4f}) ---\n"
        rag_prompt += f"Titre : {item['metadata'].get('title')}\n"
        rag_prompt += f"Date de modification : {item['metadata'].get('date')}\n"
        rag_prompt += f"Headings : {item['metadata'].get('headings')}\n"
        rag_prompt += f"Modèles concernés : {item['metadata'].get('models')}\n"
        rag_prompt += f"Codes d'erreur : {item['metadata'].get('errors')}\n"
        rag_prompt += f"{item['text']}\n\n"

    return rag_prompt


def build_prompt(context: str, rag_results: list[dict]) -> str:
    """
    Fonction de production d'un prompt à partir
    d'un contexte et de résultats RAG.
    """
    if not rag_results:
        rag_answer = ("Aucun résultat — vérifiez que le filtre correspond à des chunks existants "
            "(collection.get(where=where_clause) pour diagnostiquer).")

    rag_answer = build_rag_answer(rag_results)

    rag_prompt = f"**Question utilisateur :**\n{context}\n\n"
    rag_prompt += f"**Éléments retournés par le RAG :**\n\n{rag_answer}"

    return rag_prompt
