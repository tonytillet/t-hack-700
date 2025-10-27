# LUMEN - Système d'alerte grippe prédictif

## Démarrage rapide

```bash
docker compose up -d --build
```

Une fois démarré, ouvrez votre navigateur sur : **http://localhost:8501**

## 📊 Gestion des données avec DVC

Ce projet utilise **DVC** (Data Version Control) pour gérer les fichiers volumineux.

### 🚀 Première utilisation

```bash
# Activer l'environnement virtuel
source .venv/bin/activate

# Récupérer les données
dvc pull
```

### 📁 Structure des données

```
data/
├── raw/           # Données brutes (versionées avec DVC)
├── processed/     # Données traitées
└── logs/         # Logs de traitement
```

### 🔄 Workflow DVC

**Ajouter de nouvelles données :**
```bash
# Ajouter des fichiers à DVC
dvc add data/raw/nouveau_fichier.csv

# Commiter les métadonnées
git add data/raw/nouveau_fichier.csv.dvc
git commit -m "add new data"

# Pousser vers le remote
dvc push
```

**Récupérer les données :**
```bash
# Cloner le repo
git clone <url>

# Télécharger les données
dvc pull
```

### 💾 Stockage

- **Local** : `dvcstore/` (dossier local)
- **Métadonnées** : Fichiers `.dvc` dans Git
- **Fichiers lourds** : Stockés séparément, versionnés par DVC

### 🛠️ Commandes utiles

```bash
# Voir l'état des données
dvc status

# Voir l'historique des versions
dvc list data/raw

# Synchroniser avec le remote
dvc pull
dvc push
```

### 🔄 Pipeline de données

Le projet utilise un pipeline DVC pour le traitement automatique des données :

```bash
# Reproduire le pipeline complet
dvc repro

# Vérifier les changements dans le pipeline
dvc status

# Synchroniser le pipeline avec le remote
dvc push
dvc pull
```

**Pipeline :** `data/raw/` → `clean_data.py` → `data/processed/lumen_merged_clean.parquet`
