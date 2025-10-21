# Installation manuelle (sans Docker)

Ce guide explique comment installer et lancer LUMEN sans Docker, en utilisant un environnement virtuel Python.

## 📝 Prérequis

Vérifier la présence de Python 3.8 ou supérieur sur votre machine :

```bash
python3 --version
```

Parfois sur macOS, il peut être nécessaire d'utiliser `python3.13` ou une autre version spécifique :

```bash
python3.13 --version
```

## 📦 Première installation

### Option 1 : Commande inline (recommandée pour les débutants)

Créer le `venv`, installer et lancer l'app:

```bash
python3 -m venv venv # Créer l'environnement virtuel
venv/bin/python install.py # Installer les dépendances
venv/bin/python launch_app.py # Lancer l'application
```

**L'application sera accessible sur :** http://localhost:8501

Stopper l'app avec `CTRL+C` une fois terminée.

### Option 2 : Via l'environnement virtuel (développeurs Python expérimentés)

Créer et entrer dans le `venv`, puis installer et lancer l'app:

```bash
python3 -m venv venv # Créer et activer l'environnement virtuel
source venv/bin/activate # Activer l'environnement virtuel
python install.py # Installer les dépendances
python launch_app.py # Lancer l'application
```

**L'application sera accessible sur :** http://localhost:8501

Stopper l'app avec `CTRL+C` et quitter le `venv` avec `deactivate`.

## 🔄 Utilisation quotidienne

### Option 1 : Commande inline

```bash
venv/bin/python launch_app.py
```

### Option 2 : Via l'environnement virtuel

```bash
source venv/bin/activate
python launch_app.py
```

## 🐛 Troubleshooting

Pour plus d'aide sur le dépannage, consultez le [guide d'installation complet](../INSTALL.md).
