"""
Script d'extraction des documents excel.
"""

import pandas as pd


def read_sheet_fixed_template(xlsx_path: str, sheet_name: str) -> dict:
    """
    Lit une feuille excel au format fixe :
    A1 = titre du document, A2 = version, ligne 4 = en-têtes, ligne 5+ = données.
    """
    # Métadonnées : les 2 premières cellules de la colonne A
    meta = pd.read_excel(
        xlsx_path, sheet_name=sheet_name, header=None,
        nrows=2, usecols="A", dtype=str,
    )
    # A1 : Titre
    doc_title = meta.iloc[0, 0]
    # A2 : Version
    doc_version = meta.iloc[1, 0]

    df = pd.read_excel(xlsx_path, sheet_name=sheet_name, header=3, dtype=str).fillna("")

    return {"doc_title": doc_title, "doc_version": doc_version, "data": df}
