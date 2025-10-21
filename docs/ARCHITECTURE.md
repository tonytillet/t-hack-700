# 📁 Structure du projet LUMEN (Refactorisé)

## 🏗️ Architecture modulaire

Le projet a été refactorisé selon les bonnes pratiques de développement Python avec séparation des responsabilités.

```
lumen/
├── main.py                    # Point d'entrée principal
├── src/                       # Code source organisé
│   ├── __init__.py           # Package principal
│   ├── models/               # Classes métier
│   │   ├── __init__.py
│   │   ├── app.py           # Classe principale GrippeAlertApp
│   │   └── chatbot.py       # Chatbot IA
│   ├── views/               # Interface utilisateur
│   │   ├── __init__.py
│   │   └── main_app.py      # Application Streamlit
│   ├── utils/               # Fonctions utilitaires
│   │   ├── __init__.py
│   │   └── helpers.py       # Helpers et fonctions communes
│   └── config/              # Configuration
│       ├── __init__.py
│       └── settings.py      # Gestion de la configuration
├── data/                    # Données (ignorées par Git sauf .gitkeep)
├── scripts/                 # Scripts de traitement
├── docs/                    # Documentation
├── requirements.txt         # Dépendances
└── README.md               # Documentation principale
```

## 🎯 Avantages de cette structure

### ✅ **Séparation des responsabilités**
- **Models** : Logique métier (GrippeAlertApp, Chatbot)
- **Views** : Interface utilisateur Streamlit
- **Utils** : Fonctions utilitaires réutilisables
- **Config** : Gestion centralisée de la configuration

### ✅ **Maintenabilité**
- Code organisé et facile à naviguer
- Chaque module a une responsabilité claire
- Tests unitaires plus faciles à écrire

### ✅ **Réutilisabilité**
- Modules peuvent être importés indépendamment
- Fonctions utilitaires réutilisables
- Configuration centralisée

### ✅ **Évolutivité**
- Ajout de nouvelles fonctionnalités plus simple
- Structure extensible
- Respect des conventions Python

## 🚀 Utilisation

### Lancement de l'application
```bash
python main.py
# ou
python -m src.views.main_app
```

### Développement
```bash
# Importer des composants spécifiques
from src.models.app import GrippeAlertApp
from src.models.chatbot import GrippeChatbot
from src.utils.helpers import format_number
```

## 📋 Conventions respectées

- ✅ **PEP 8** : Style de code Python
- ✅ **Imports relatifs** : Utilisation de `from .module import`
- ✅ **Packages** : `__init__.py` dans chaque dossier
- ✅ **Nommage** : Modules en minuscules, classes en PascalCase
- ✅ **Documentation** : Docstrings pour les classes et fonctions

## 🔄 Migration depuis l'ancien code

L'ancien `app_complete.py` a été décomposé en plusieurs modules :
- **Modèle** → `src/models/app.py`
- **Chatbot** → `src/models/chatbot.py`
- **Helpers** → `src/utils/helpers.py`
- **Configuration** → `src/config/settings.py`
- **Vue principale** → `src/views/main_app.py`

Le point d'entrée est maintenant `main.py` au lieu de `app_complete.py`.
