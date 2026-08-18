"""
Fonctions utilitaires concernant les fichiers.
"""

from pathlib import Path

def list_files(folder: Path) -> list[Path]:
    """
    Fonction utilitaire pour lister les fichiers d'un dossier.
    """
    files = folder.rglob("*")
    result_files = []
    for file in files:
        if file.is_file():
            result_files.append(file)
    return result_files
