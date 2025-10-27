# LUMEN - Système d'alerte grippe prédictif

Application de prédiction et suivi des épidémies de grippe en France, avec dashboard interactif et prédictions à J+7.

## Démarrage rapide

```bash
docker compose up -d --build
```

Une fois démarré, ouvrez votre navigateur sur : **http://localhost:8501**

## Fonctionnalités du Dashboard

### Visualisations principales
- **Carte de France interactive** : Visualisation géographique des alertes par département avec niveaux de gravité
- **Dashboard KPI** : Métriques clés (alerte nationale, départements critiques, tendance, précision du modèle)
- **Graphique temporel** : Suivi des cas réels vs prédictions avec visualisation J+7

### Analyses complémentaires
- **Comparaison régionale** : Top 10 des départements les plus touchés
- **Timeline épidémique** : Évolution des vagues grippales 2023 vs 2024
- **Performance du modèle** : Analyse des erreurs de prédiction par département

## Pipeline ML

Le système utilise un pipeline en 5 étapes pour générer les prédictions :

```bash
# Exécuter le pipeline complet
python scripts/run_pipeline.py

# Ou via DVC
dvc repro
```

### Étapes du pipeline
1. **clean_data.py** : Nettoyage et standardisation des données brutes
2. **fit_stats.py** : Calcul des statistiques de référence
3. **make_features.py** : Création des features temporelles (lags, rolling windows)
4. **train_random_forest.py** : Entraînement du modèle RandomForest
5. **predict.py** : Génération des prédictions avec analyse d'erreurs

## Gestion des données avec DVC

Ce projet utilise **DVC** (Data Version Control) pour gérer les fichiers volumineux.

### Première utilisation

```bash
# Activer l'environnement virtuel
source .venv/bin/activate

# Récupérer les données
dvc pull
```

### Structure des données

```
data/
├── raw/           # Données brutes (versionées avec DVC)
├── processed/     # Données traitées par le pipeline
├── features/      # Features ML générées
├── artifacts/     # Modèles entraînés et statistiques
├── predictions/   # Prédictions finales (utilisées par le dashboard)
└── logs/          # Logs de traitement
```

### Commandes utiles

```bash
# Voir l'état des données
dvc status

# Reproduire le pipeline complet
dvc repro

# Synchroniser avec le remote
dvc pull
dvc push
```

## Développement local

### Sans Docker

```bash
# Créer un environnement virtuel
python3 -m venv .venv

# Activer l'environnement
source .venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt

# Récupérer les données
dvc pull

# Lancer l'application
streamlit run app.py
```

### Avec Docker

```bash
# Mode développement avec auto-reload
docker compose up --build

# Mode arrière-plan
docker compose up -d --build

# Arrêter l'application
docker compose down
```

## Architecture du projet

```
t-hack-700/
├── app.py                    # Application Streamlit (dashboard)
├── scripts/                  # Pipeline ML
│   ├── clean_data.py        # Nettoyage données
│   ├── fit_stats.py         # Statistiques
│   ├── make_features.py     # Création features
│   ├── train_random_forest.py # Entraînement
│   ├── predict.py           # Prédictions
│   └── run_pipeline.py      # Orchestrateur
├── data/                     # Données (géré par DVC)
├── dvc.yaml                  # Configuration pipeline DVC
├── requirements.txt          # Dépendances Python
└── docker-compose.yml        # Configuration Docker
```

## Technologies utilisées

- **Streamlit** : Interface web interactive
- **Plotly** : Visualisations interactives
- **Pandas & NumPy** : Manipulation des données
- **Scikit-learn** : Machine Learning (RandomForest)
- **DVC** : Versioning des données
- **Docker** : Containerisation

## Données sources

- **Data.gouv.fr** : Données de santé publique
- **APIs météo** : Données météorologiques
- **Wikipedia** : Données contextuelles sur les épidémies

## Prédictions

Le modèle prédit le nombre de cas d'urgences liées à la grippe à **J+7** pour chaque département français, permettant une anticipation et une gestion proactive des ressources sanitaires.

### Niveaux d'alerte

- 🔴 **Rouge** : > 150 cas (alerte maximale)
- 🟠 **Orange** : 100-150 cas (alerte élevée)
- 🟡 **Jaune** : 50-100 cas (vigilance)
- 🟢 **Vert** : < 50 cas (normal)
