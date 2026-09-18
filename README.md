# RAG-Electrodomus

## Initialisation du projet

### 1 - Environnement d'exécution

Dans le terminal :

```PowerShell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2 - Fichier des variables d'environnement

Copier le .env.example en .env et remplir avec vos données.

### 3 - Ajout du corpus

Mettre le corpus sur lequel vous souhaitez utiliser le RAG dans data/corpus/

### 4 - Récupération d'une clé API Groq

Créer un compte et générer une clé API Groq : [console.groq.com/keys](https://console.groq.com/keys)

Ajouter la clé dans le .env

## Lancement du projet

### 1 - Lancer l'API FastAPI

Dans le terminal à la racine du projet :

```PowerShell
python -m uvicorn main:app --reload --port 8000
```

### 2a - Tester les routes depuis le Swagger

Se rendre sur **http://localhost:8000/docs**.

### 2b - Utiliser l'interface utilisateur

Ouvrir la page **index.html** sur un navigateur.

## Exécuter Pylint

Pour tester la qualité du code, exécuter la commande suivante depuis la racine du projet :

```PowerShell
python -m pylint src/*
```
