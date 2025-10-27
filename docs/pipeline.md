# Pipeline Technique de Traitement des Données

## Vue d'ensemble

Le système LUMEN utilise un pipeline de traitement de données en 5 étapes pour transformer les données brutes en prédictions exploitables. Chaque étape est orchestrée par un script Python dédié et peut être exécutée indépendamment ou via le script principal `run_pipeline.py`.

## Architecture du Pipeline

```
┌─────────────────────────────────────────────────────────────────┐
│                      SOURCES DE DONNÉES                         │
├─────────────────────────────────────────────────────────────────┤
│  • data.gouv.fr (urgences hospitalières)                        │
│  • APIs météo (température, humidité)                           │
│  • Wikipedia (métadonnées santé publique)                       │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│             ÉTAPE 1 : Nettoyage des Données                     │
│                   (clean_data.py)                               │
├─────────────────────────────────────────────────────────────────┤
│  • Standardisation du schéma (date, région, département, etc.)  │
│  • Validation et correction des types                           │
│  • Harmonisation des codes régions/départements                 │
│  • Fusion multi-sources                                         │
│  → Sortie : lumen_merged_clean.parquet                          │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│          ÉTAPE 2 : Calcul des Statistiques de Référence         │
│                   (fit_stats.py)                                │
├─────────────────────────────────────────────────────────────────┤
│  • Médianes pour imputation des valeurs manquantes              │
│  • Mapping des variables catégorielles                          │
│  • Statistiques descriptives globales                           │
│  → Sorties : medians.json, cats.json, stats_summary.json        │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│            ÉTAPE 3 : Ingénierie des Features                    │
│                  (make_features.py)                             │
├─────────────────────────────────────────────────────────────────┤
│  • Création de la variable cible : cas d'urgence à J+7          │
│  • Features temporelles : lags (t-1, t-7, t-14)                 │
│  • Features agrégées : moyennes mobiles (7j, 14j, 30j)          │
│  • One-hot encoding des variables catégorielles                 │
│  → Sorties : features.parquet, y_target.parquet                 │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│              ÉTAPE 4 : Entraînement du Modèle                   │
│                (train_random_forest.py)                         │
├─────────────────────────────────────────────────────────────────┤
│  • Split temporel 80/20 (pas de shuffle)                        │
│  • RandomForestRegressor (100 arbres, profondeur=20)            │
│  • Calcul des métriques (MAE, RMSE, R²)                         │
│  • Extraction de l'importance des features                      │
│  → Sorties : rf.joblib, metrics.json, feature_importance.json   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                ÉTAPE 5 : Génération des Prédictions             │
│                     (predict.py)                                │
├─────────────────────────────────────────────────────────────────┤
│  • Prédictions sur l'ensemble du dataset                        │
│  • Calcul des erreurs absolues et relatives                     │
│  • Métriques par département                                    │
│  → Sorties : predictions.parquet, predictions_summary.json      │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                   DASHBOARD STREAMLIT                           │
│                      (app.py)                                   │
└─────────────────────────────────────────────────────────────────┘
```

## Schéma de Données Standardisé

Toutes les données nettoyées respectent ce schéma unifié :

```python
{
    'date': datetime,           # Date de la mesure
    'region': str,              # Code région (IDF, ARA, PACA, etc.)
    'departement': str,         # Identifiant département
    'valeur': float,            # Valeur numérique mesurée
    'type_donnee': str,         # Type (temperature, case_count, etc.)
    'source': str,              # Origine (data_gouv_fr, open_meteo, wikipedia)
    'unite': str                # Unité de mesure (celsius, count, etc.)
}
```

## Description Détaillée des Étapes

### Étape 1 : Nettoyage des Données

**Script** : `scripts/clean_data.py`

**Responsabilités** :
- Lecture des fichiers JSON bruts depuis `data/raw/data_gouv_fr/`
- Normalisation des formats de date (ISO 8601)
- Standardisation des codes régions (mapping vers codes 2 lettres)
- Validation des types de données (conversions numériques)
- Suppression des doublons et valeurs aberrantes
- Logging détaillé dans `data/processed/clean_data.log`

**Transformations clés** :
- Régions : `Île-de-France` → `IDF`, `Auvergne-Rhône-Alpes` → `ARA`
- Dates : parsing flexible avec gestion des fuseaux horaires
- Valeurs manquantes : marquées pour imputation ultérieure

**Sortie principale** : `data/processed/lumen_merged_clean.parquet`

### Étape 2 : Statistiques de Référence

**Script** : `scripts/fit_stats.py`

**Responsabilités** :
- Calcul des médianes pour chaque feature numérique
- Création du mapping des modalités catégorielles
- Génération des statistiques descriptives (min, max, écart-type)

**Utilité** :
- Les médianes servent à l'imputation des valeurs manquantes
- Les mappings catégoriels sont utilisés pour le one-hot encoding
- Les statistiques permettent la validation des nouvelles données

**Sorties** :
- `data/config/medians.json` : valeurs médianes par feature
- `data/config/cats.json` : modalités des variables catégorielles
- `data/config/stats_summary.json` : statistiques globales

### Étape 3 : Ingénierie des Features

**Script** : `scripts/make_features.py`

**Responsabilités** :
- Chargement des séries temporelles d'urgences
- Création de la variable cible : `y_target = cas_urgences[date + 7 jours]`
- Génération des features temporelles :
  - **Lags** : valeurs passées (t-1, t-7, t-14, t-21, t-30 jours)
  - **Rolling windows** : moyennes mobiles (7j, 14j, 30j)
  - **Statistiques glissantes** : min, max, std sur fenêtres temporelles
- One-hot encoding des variables catégorielles (régions, départements)
- Gestion des valeurs manquantes (imputation par médianes)

**Principe de la variable cible** :
```python
# Pour chaque date t, on prédit le nombre de cas à t+7
y_target[t] = cas_urgences[t + 7 jours]
```

**Sorties** :
- `data/features/features.parquet` : matrice X (features)
- `data/features/y_target.parquet` : vecteur y (cible)
- `data/features/feature_list.json` : noms des colonnes

### Étape 4 : Entraînement du Modèle

**Script** : `scripts/train_random_forest.py`

**Configuration du modèle** :
```python
RandomForestRegressor(
    n_estimators=100,           # 100 arbres de décision
    max_depth=20,               # Profondeur maximale
    min_samples_split=5,        # Min d'échantillons pour split
    min_samples_leaf=2,         # Min d'échantillons par feuille
    max_features='sqrt',        # √n features par split
    random_state=42,            # Reproductibilité
    n_jobs=-1                   # Parallélisation sur tous les cœurs
)
```

**Validation** :
- **Split temporel** : 80% train / 20% test (pas de shuffle)
- Respect de l'ordre chronologique (pas de fuite de données futures)
- Évaluation sur période de test non vue

**Métriques calculées** :
- **MAE** (Mean Absolute Error) : erreur absolue moyenne
- **RMSE** (Root Mean Squared Error) : pénalise les grandes erreurs
- **R²** : coefficient de détermination (variance expliquée)
- **Métriques relatives** : MAE et RMSE en % de la moyenne de y

**Sorties** :
- `data/artifacts/rf.joblib` : modèle sérialisé
- `data/artifacts/metrics.json` : performances du modèle
- `data/artifacts/feature_importance.json` : importance des features
- `data/artifacts/model_summary.json` : métadonnées d'entraînement

### Étape 5 : Génération des Prédictions

**Script** : `scripts/predict.py`

**Responsabilités** :
- Chargement du modèle entraîné (`rf.joblib`)
- Prédiction sur l'ensemble du dataset (train + test)
- Calcul des erreurs par observation :
  - **Erreur absolue** : `|y_pred - y_true|`
  - **Erreur relative** : `|y_pred - y_true| / y_true * 100`
- Agrégation des métriques par département
- Identification des périodes/régions problématiques

**Sorties** :
- `data/predictions/predictions.parquet` : prédictions + erreurs
- `data/predictions/predictions_summary.json` : analyse des erreurs

**Structure des prédictions** :
```python
{
    'date': datetime,
    'departement': str,
    'y_true': float,           # Valeur réelle
    'y_pred': float,           # Valeur prédite
    'abs_error': float,        # Erreur absolue
    'rel_error': float         # Erreur relative (%)
}
```

## Gestion des Versions avec DVC

### Configuration actuelle

Le pipeline utilise **Data Version Control (DVC)** pour gérer les données volumineuses :

```yaml
# dvc.yaml
stages:
  clean_data:
    cmd: python scripts/clean_data.py
    deps:
      - data/raw/
      - scripts/clean_data.py
    outs:
      - data/processed/lumen_merged_clean.parquet
```

### Commandes DVC essentielles

```bash
# Synchroniser les données
dvc pull                    # Télécharger les données versionnées
dvc push                    # Uploader les nouvelles versions

# Vérifier l'état
dvc status                  # Changements non commités
dvc diff                    # Différences entre versions

# Reproduire le pipeline
dvc repro                   # Exécuter les stages modifiés

# Ajouter de nouvelles données
dvc add data/raw/new_file.csv
git add data/raw/new_file.csv.dvc
git commit -m "feat: add new raw data"
```

## Exécution du Pipeline

### Pipeline complet

```bash
# Toutes les étapes en séquence
python scripts/run_pipeline.py
```

### Étapes individuelles (débogage)

```bash
# Étape 1 : Nettoyage
python scripts/clean_data.py

# Étape 2 : Statistiques
python scripts/fit_stats.py

# Étape 3 : Features
python scripts/make_features.py

# Étape 4 : Entraînement
python scripts/train_random_forest.py

# Étape 5 : Prédictions
python scripts/predict.py
```

### Avec Docker

```bash
# Construire et lancer
docker compose up --build

# Exécuter le pipeline dans le conteneur
docker compose exec lumen python scripts/run_pipeline.py
```

## Optimisation et Bonnes Pratiques

### Performance

1. **Parquet vs CSV** : Tous les fichiers de données utilisent Parquet (10x plus rapide)
2. **Parallélisation** : RandomForest utilise tous les cœurs CPU (`n_jobs=-1`)
3. **Lazy loading** : Chargement des données uniquement quand nécessaire
4. **Caching DVC** : Évite le recalcul des étapes non modifiées

### Reproductibilité

1. **Random seeds** : `random_state=42` dans tous les modèles
2. **DVC locks** : `dvc.lock` fige les dépendances de chaque stage
3. **Versioning Git** : Scripts et configurations sous version control
4. **Logs détaillés** : Traçabilité complète dans `clean_data.log`

### Maintenabilité

1. **Modularité** : Chaque étape est un script indépendant
2. **Paths relatifs** : Utilisation de `pathlib.Path` partout
3. **Configuration centralisée** : Statistiques de référence en JSON
4. **Tests unitaires** : (à implémenter) pour chaque transformation

## Troubleshooting

### Le pipeline échoue à l'étape X

1. Vérifier les logs : `tail -f data/processed/clean_data.log`
2. Exécuter l'étape individuellement pour isoler l'erreur
3. Vérifier que les fichiers d'entrée existent et sont lisibles
4. Contrôler les permissions sur le dossier `data/`

### Métriques dégradées après modification

1. Examiner `feature_importance.json` : les features importantes ont-elles changé ?
2. Comparer les distributions avant/après via `stats_summary.json`
3. Vérifier le split temporel : train/test cohérents ?
4. Inspecter les prédictions avec erreurs élevées dans `predictions.parquet`

### DVC ne trouve pas les données

```bash
# Reconfigurer le remote
dvc remote list
dvc remote modify origin url /path/to/dvcstore

# Forcer la synchronisation
dvc pull --force
```

## Évolutions Futures

### Court terme
- Ajout de tests unitaires pour chaque étape
- Monitoring des distributions de features (data drift)
- Dashboard de qualité des données

### Moyen terme
- Pipeline d'hyperparameter tuning (GridSearchCV)
- Modèles alternatifs (XGBoost, LightGBM)
- Features d'interaction (région × météo)

### Long terme
- Pipeline temps réel (streaming)
- AutoML pour sélection de features
- Explicabilité avancée (SHAP values)
