# 🚀 Guide de démarrage rapide - Pipeline Grippe

## ⚡ Lancement rapide

```bash
cd scripts

# Pipeline complète en 3 étapes
python collect_all_data.py  # Collecte les données
python fuse_data.py          # Fusionne les données
python train_model.py        # Entraîne les modèles
```

**⚠️ Important** : Vous devez d'abord exécuter `collect_all_data.py` pour générer les données avant de lancer `fuse_data.py`.

## 📋 Ce qui se passe

### 1. **Collecte** (collect_all_data.py)
   - Collecte **13 sources de données** :
     - Google Trends (3 sources)
     - Wikipedia (2 sources)
     - SPF - Santé Publique France (4 sources)
     - Contexte : INSEE + Météo (4 sources)
   - Sauvegarde dans `data/google_trends/`, `data/wikipedia/`, `data/spf/`, `data/context/`

### 2. **Fusion** (fuse_data.py)
   - Fusionne les 13 sources de données
   - Crée des features avancées (lags, moyennes mobiles, z-scores)
   - Calcule l'indice **FLURISK** (indicateur de risque grippe)
   - Gère les 13 régions françaises
   - Sauvegarde dans `data/processed/`

### 3. **Entraînement** (train_model.py)
   - Entraîne 4 modèles Random Forest (J+7, J+14, J+21, J+28)
   - Génère les prédictions avec métriques détaillées
   - Sauvegarde modèles, métriques et importance des features
   - Sauvegarde dans `models/`

## 📁 Résultats

Après exécution, vous trouverez:

```
data/
├── google_trends/       ← Données Google Trends
├── wikipedia/           ← Données Wikipedia
├── spf/                 ← Données Santé Publique France
├── context/             ← Données INSEE + Météo
└── processed/           ← Dataset fusionné avec FLURISK

models/                  ← Modèles entraînés (.pkl)
├── rf_grippe_j7_*.pkl
├── rf_grippe_j14_*.pkl
├── rf_grippe_j21_*.pkl
├── rf_grippe_j28_*.pkl
├── config_*.json
└── metrics_*.csv
```

## 📊 Exécution étape par étape

Si vous préférez exécuter étape par étape:

```bash
cd scripts

# Étape 1: Collecte des données (13 sources)
python collect_all_data.py

# Étape 2: Fusion et création des features
python fuse_data.py

# Étape 3: Entraînement des modèles
python train_model.py
```

## 🔍 Collecteurs individuels

Vous pouvez aussi lancer les collecteurs individuellement:

```bash
# Google Trends uniquement
python collect_google_trends.py

# Wikipedia uniquement
python collect_wikipedia.py

# SPF (Santé Publique France) uniquement
python collect_spf_data.py

# Contexte (INSEE + Météo) uniquement
python collect_context_data.py
```

## 🎯 Fonctionnalités avancées

### Indice FLURISK
Le script `fuse_data.py` calcule automatiquement l'indice FLURISK pour chaque région :
- **0-50** : Risque faible 🟢
- **50-70** : Risque moyen 🟠
- **70-100** : Risque élevé 🔴

### Features créées
- Lags : 1, 2, 3, 4, 8, 12 semaines
- Moyennes mobiles : 3, 4, 8 semaines
- Z-scores pour normalisation
- Ratios et interactions

### Régions gérées
13 régions françaises :
- Île-de-France
- Auvergne-Rhône-Alpes
- Nouvelle-Aquitaine
- Occitanie
- Hauts-de-France
- Grand Est
- Pays de la Loire
- Bretagne
- Normandie
- Centre-Val de Loire
- Bourgogne-Franche-Comté
- Provence-Alpes-Côte d'Azur
- Corse

## 🐛 En cas de problème

- **Erreur de collecte**: Les scripts génèrent automatiquement des données simulées
- **Données manquantes**: Vérifiez que chaque étape s'est bien terminée
- **Erreur de modèle**: Vérifiez qu'il y a assez de données dans `data/processed/`

## 📖 Documentation complète

- **`docs/SCRIPTS.md`** - Détails sur chaque script
- **`docs/FLURISK.md`** - Explication complète de l'indice FLURISK
- **`docs/VISUALISATION.md`** - Guide complet de `app.py` et `demo.py`

## 👁️ Visualiser les résultats

### Option 1 : Application Web Streamlit (Recommandé)

```bash
streamlit run app.py
```

Ouvre une interface web interactive avec :
- 🗺️ Carte de France avec FLURISK par région
- 📋 Top 10 priorités des régions à risque
- 🔍 Zoom département avec prédictions J+7, J+14, J+21, J+28
- 🎛️ Simulation ROI des campagnes de vaccination
- 💾 Export CSV

**URL** : http://localhost:8501

### Option 2 : Vérification rapide en terminal

```bash
python demo.py
```

Affiche dans le terminal :
- ✅ État des données collectées
- 📊 Statistiques du dataset
- 🚨 FLURISK actuel par région (Top 5)
- 🤖 Performance des modèles (MAE, R²)
- 🌐 Statut de l'application Streamlit

### Option 3 : Voir les fichiers directement

**FLURISK et données :**
- `data/processed/dataset_grippe_*.csv` - Dataset complet avec FLURISK

**Métriques des modèles :**
- `models/metrics_j7_*.csv` - Performance J+7
- `models/metrics_j14_*.csv` - Performance J+14
- `models/metrics_j21_*.csv` - Performance J+21
- `models/metrics_j28_*.csv` - Performance J+28

**Importance des features :**
- `models/importance_*.csv` - Importance de FLURISK et autres variables

**Prédictions :**
- `data/processed/dataset_with_predictions_*.csv` - Dataset avec prédictions

## ✅ Vérification rapide

Pour vérifier que tout fonctionne:

```bash
cd scripts
python collect_all_data.py
```

Vous devriez voir:
```
✅ COLLECTE TERMINÉE
💡 Prochaine étape: Fusion et traitement des données
```

Durée estimée: 3-5 minutes pour la pipeline complète
