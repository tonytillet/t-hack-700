# LUMEN - Système de Prédiction d'Alertes Grippe

**LUMEN** est un système de prédiction des afflux d'urgences hospitalières liées à la grippe. Il combine données de santé publique, météo et machine learning pour anticiper les pics d'activité à 7 jours et optimiser la gestion des ressources sanitaires.

## Démarrage Rapide

```bash
docker compose up --build
```

Une fois démarré, ouvrez votre navigateur sur : **http://localhost:8501**

## Documentation

Toute la documentation technique est organisée dans le dossier `docs/` :

### Sommaire

- **[Pipeline Technique](docs/pipeline.md)** : Architecture complète du traitement des données (5 étapes : nettoyage → statistiques → features → entraînement → prédictions)

- **[Éthique et Confidentialité](docs/ethics-privacy.md)** : Principes éthiques, protection des données (RGPD), sources de données publiques, mesures de sécurité et conformité réglementaire

- **[Processus d'Entraînement](docs/training.md)** : Méthodologie ML détaillée (Random Forest, validation temporelle, feature engineering, hyperparameter tuning, monitoring)

## À Propos

LUMEN utilise un modèle Random Forest pour prédire les cas d'urgence à J+7, permettant aux établissements de santé d'anticiper les besoins en personnel et en ressources.

**Technologies** : Streamlit, Plotly, Scikit-learn, DVC, Docker

**Sources de données** : Data.gouv.fr (Open Data santé), APIs météo publiques

**Licence** : Open source - Données publiques sous Licence Ouverte 2.0
