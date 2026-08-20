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


def get_path_after(filepath: Path, target_folder: str) -> str | None:
    """Retourne le chemin qui suit immédiatement target_folder, ou None si absent."""
    parts = list(filepath.parts)
    if target_folder in parts:
        idx = parts.index(target_folder)
        if idx + 1 < len(parts):
            return parts[idx + 1:-1]
    return None
