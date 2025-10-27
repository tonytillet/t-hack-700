# Processus d'Entraînement du Modèle

## Vue d'ensemble

Le système LUMEN utilise un modèle de **Random Forest Regressor** pour prédire les cas d'urgences hospitalières à 7 jours. Ce document détaille le processus d'entraînement, les choix méthodologiques, l'évaluation et l'optimisation du modèle.

## Architecture du Modèle

### Choix de l'Algorithme : Random Forest

**Pourquoi Random Forest ?**

1. **Robustesse** : Résistant au surapprentissage grâce à l'agrégation de multiples arbres
2. **Non-linéarité** : Capture les relations complexes entre features sans transformation manuelle
3. **Importance des features** : Fournit des métriques d'explicabilité (feature importance)
4. **Pas de scaling requis** : Indépendant de l'échelle des variables
5. **Gestion des interactions** : Détecte automatiquement les interactions entre variables
6. **Performance éprouvée** : Excellent sur les données tabulaires (benchmark Kaggle)

**Alternatives considérées** :

| Modèle | Avantages | Inconvénients | Décision |
|--------|-----------|---------------|----------|
| **Linear Regression** | Simple, interprétable | Suppose linéarité, pas d'interactions | Rejeté (trop simpliste) |
| **XGBoost/LightGBM** | Très performant, rapide | Hyperparams complexes, moins stable | Futur candidat |
| **LSTM (Deep Learning)** | Capture temporalité | Nécessite beaucoup de données, black box | Trop complexe pour v1 |
| **Prophet (Facebook)** | Spécialisé time-series | Moins flexible, pas de features externes | Pas adapté |
| **Random Forest** | Bon compromis performance/interprétabilité | Plus lent que boosting | ✅ **Choisi** |

### Configuration du Modèle

```python
from sklearn.ensemble import RandomForestRegressor

model = RandomForestRegressor(
    n_estimators=100,           # Nombre d'arbres
    max_depth=20,               # Profondeur maximale de chaque arbre
    min_samples_split=5,        # Min échantillons pour split un nœud
    min_samples_leaf=2,         # Min échantillons dans une feuille
    max_features='sqrt',        # √n features considérées à chaque split
    random_state=42,            # Graine aléatoire (reproductibilité)
    n_jobs=-1,                  # Parallélisation sur tous les cœurs
    bootstrap=True,             # Échantillonnage avec remise (bagging)
    oob_score=False,            # Score Out-of-Bag (non utilisé)
    verbose=0                   # Pas de logs détaillés
)
```

**Justification des hyperparamètres** :

- **`n_estimators=100`** : Compromis entre performance et temps de calcul (plus = meilleur mais plus lent)
- **`max_depth=20`** : Limite la profondeur pour éviter le surapprentissage
- **`min_samples_split=5`** : Évite de splitter sur trop peu de données (régularisation)
- **`min_samples_leaf=2`** : Feuilles avec au moins 2 échantillons (stabilité)
- **`max_features='sqrt'`** : Sélection aléatoire de √n features → décorrélation des arbres
- **`random_state=42`** : Reproductibilité complète des résultats
- **`n_jobs=-1`** : Utilise tous les cœurs CPU disponibles (accélération x4-x8)

## Pipeline d'Entraînement

### Étape 1 : Chargement des Données

```python
# scripts/train_random_forest.py

import pandas as pd
from pathlib import Path

# Chargement des features et de la cible
X = pd.read_parquet('data/features/features.parquet')
y = pd.read_parquet('data/features/y_target.parquet')

# Vérification des dimensions
print(f"Features shape: {X.shape}")  # Ex: (10000, 150)
print(f"Target shape: {y.shape}")     # Ex: (10000,)
```

**Caractéristiques des données** :
- **X** : Matrice de features (lags, rolling, one-hot encoding)
- **y** : Vecteur cible (nombre de cas d'urgence à J+7)
- **Alignement** : Les index de X et y sont synchronisés (même dates)

### Étape 2 : Split Temporel Train/Test

**IMPORTANT** : Pas de shuffle aléatoire (données time-series)

```python
from sklearn.model_selection import train_test_split

# Split temporel : 80% train / 20% test
# shuffle=False : respecte l'ordre chronologique
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    shuffle=False,  # CRUCIAL : pas de mélange temporel
    random_state=42
)

# Résultat :
# Train = dates anciennes (ex: 2020-2023)
# Test = dates récentes (ex: 2023-2024)
```

**Pourquoi pas de shuffle ?**
- Évite la **fuite de données** : le modèle ne doit pas connaître le futur
- Simule la **vraie prédiction** : entraîner sur le passé, prédire le futur
- Respecte la **dépendance temporelle** : les observations successives sont corrélées

**Illustration du split** :

```
Timeline: ─────────────────────────────────────────────►
          2020      2021      2022      2023      2024
          ├─────────────────────────────┤───────────┤
                   TRAIN (80%)          TEST (20%)
```

### Étape 3 : Entraînement

```python
# Entraînement du modèle
model.fit(X_train, y_train)

# Logs (automatiques si verbose=1)
# [Parallel(n_jobs=-1)]: Using backend ThreadingBackend with 8 concurrent workers.
# [Parallel(n_jobs=-1)]: Done  100 out of 100 | elapsed:   5.2s finished
```

**Processus interne du Random Forest** :

1. **Bootstrap** : Pour chaque arbre, échantillonner aléatoirement n_train données (avec remise)
2. **Feature sampling** : À chaque split, sélectionner √n features aléatoires
3. **Split optimal** : Choisir le seuil qui minimise la MSE (Mean Squared Error)
4. **Récursion** : Répéter jusqu'à `max_depth` ou `min_samples_leaf`
5. **Agrégation** : Prédiction finale = moyenne des prédictions de tous les arbres

**Temps d'entraînement** (sur machine standard) :
- 10 000 échantillons × 150 features : ~5 secondes
- 100 000 échantillons × 150 features : ~1 minute
- Scalabilité : linéaire avec `n_estimators`, log avec `n_samples`

### Étape 4 : Prédiction et Évaluation

```python
# Prédictions sur le set de test
y_pred = model.predict(X_test)

# Calcul des métriques
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import numpy as np

mae = mean_absolute_error(y_test, y_pred)
rmse = np.sqrt(mean_squared_error(y_test, y_pred))
r2 = r2_score(y_test, y_pred)

# Métriques relatives (% de la moyenne de y)
mae_rel = mae / y_test.mean() * 100
rmse_rel = rmse / y_test.mean() * 100

print(f"MAE:  {mae:.2f} (± {mae_rel:.1f}%)")
print(f"RMSE: {rmse:.2f} (± {rmse_rel:.1f}%)")
print(f"R²:   {r2:.3f}")
```

**Interprétation des métriques** :

| Métrique | Formule | Interprétation | Objectif |
|----------|---------|----------------|----------|
| **MAE** | `mean(\|y_true - y_pred\|)` | Erreur absolue moyenne | Minimiser |
| **RMSE** | `√mean((y_true - y_pred)²)` | Pénalise les grandes erreurs | Minimiser |
| **R²** | `1 - SS_res / SS_tot` | % de variance expliquée | Maximiser (proche de 1) |
| **MAE %** | `MAE / mean(y_true) * 100` | Erreur relative à la moyenne | < 10% = excellent |
| **RMSE %** | `RMSE / mean(y_true) * 100` | Idem mais pénalise outliers | < 15% = bon |

**Exemple de résultats** :
```
MAE:  12.5 cas (± 8.3%)    → En moyenne, on se trompe de 12.5 cas
RMSE: 18.2 cas (± 12.1%)   → Écart-type des erreurs = 18.2 cas
R²:   0.873                → Le modèle explique 87.3% de la variance
```

### Étape 5 : Feature Importance

```python
# Extraction de l'importance des features
importances = model.feature_importances_
feature_names = X.columns

# Tri par importance décroissante
importance_df = pd.DataFrame({
    'feature': feature_names,
    'importance': importances
}).sort_values('importance', ascending=False)

# Top 10 features
print(importance_df.head(10))
```

**Exemple de sortie** :

| Feature | Importance | Interprétation |
|---------|-----------|----------------|
| `lag_7` | 0.235 | Valeur d'il y a 7 jours (très prédictive) |
| `rolling_mean_7d` | 0.182 | Moyenne mobile 7 jours |
| `lag_14` | 0.121 | Valeur d'il y a 14 jours |
| `temperature_mean` | 0.089 | Température moyenne |
| `departement_75` | 0.067 | Département Paris (one-hot) |
| `rolling_std_7d` | 0.054 | Écart-type 7 jours |
| ... | ... | ... |

**Utilité** :
- Identifier les features clés (focus pour amélioration)
- Détecter les features inutiles (simplification du modèle)
- Valider la cohérence métier (les features importantes sont-elles logiques ?)

### Étape 6 : Sauvegarde des Artefacts

```python
import joblib
import json

# Sauvegarde du modèle
joblib.dump(model, 'data/artifacts/rf.joblib')

# Sauvegarde des métriques
metrics = {
    'mae': float(mae),
    'rmse': float(rmse),
    'r2': float(r2),
    'mae_relative': float(mae_rel),
    'rmse_relative': float(rmse_rel),
    'train_size': len(X_train),
    'test_size': len(X_test),
    'n_features': X.shape[1],
    'timestamp': datetime.now().isoformat()
}

with open('data/artifacts/metrics.json', 'w') as f:
    json.dump(metrics, f, indent=2)

# Sauvegarde de l'importance des features
importance_dict = importance_df.to_dict(orient='records')
with open('data/artifacts/feature_importance.json', 'w') as f:
    json.dump(importance_dict, f, indent=2)
```

## Validation et Diagnostics

### Cross-Validation Temporelle

**Problème** : Un seul split peut être chanceux/malchanceux

**Solution** : Time Series Split (validation glissante)

```python
from sklearn.model_selection import TimeSeriesSplit

tscv = TimeSeriesSplit(n_splits=5)

scores = []
for train_idx, test_idx in tscv.split(X):
    X_train_cv, X_test_cv = X.iloc[train_idx], X.iloc[test_idx]
    y_train_cv, y_test_cv = y.iloc[train_idx], y.iloc[test_idx]

    model.fit(X_train_cv, y_train_cv)
    y_pred_cv = model.predict(X_test_cv)
    mae_cv = mean_absolute_error(y_test_cv, y_pred_cv)
    scores.append(mae_cv)

print(f"CV MAE: {np.mean(scores):.2f} ± {np.std(scores):.2f}")
```

**Illustration** :

```
Fold 1: ████████████─────┤ Train │ Test
Fold 2: ████████████████─────┤ Train │ Test
Fold 3: ████████████████████─────┤ Train │ Test
Fold 4: ████████████████████████─────┤ Train │ Test
Fold 5: ████████████████████████████─────┤ Train │ Test
```

**Avantages** :
- Évalue la stabilité du modèle sur plusieurs périodes
- Détecte le surapprentissage (si variance des scores élevée)
- Plus robuste qu'un seul split

### Analyse des Résidus

```python
# Calcul des résidus
residuals = y_test - y_pred

# Distribution des résidus
import matplotlib.pyplot as plt

plt.figure(figsize=(12, 4))

# Histogramme
plt.subplot(1, 3, 1)
plt.hist(residuals, bins=50, edgecolor='black')
plt.title('Distribution des Résidus')
plt.xlabel('Résidu (cas réels - cas prédits)')

# Résidus vs prédictions
plt.subplot(1, 3, 2)
plt.scatter(y_pred, residuals, alpha=0.3)
plt.axhline(0, color='red', linestyle='--')
plt.title('Résidus vs Prédictions')
plt.xlabel('Prédictions')
plt.ylabel('Résidus')

# Q-Q plot (normalité)
from scipy import stats
plt.subplot(1, 3, 3)
stats.probplot(residuals, dist="norm", plot=plt)
plt.title('Q-Q Plot')

plt.tight_layout()
plt.savefig('data/artifacts/residuals_analysis.png')
```

**Interprétation** :
- **Distribution** : Doit être centrée sur 0 (pas de biais)
- **Résidus vs prédictions** : Pas de structure (hétéroscédasticité)
- **Q-Q plot** : Alignement sur la diagonale (normalité)

### Analyse par Département

```python
# Ajout du département aux prédictions
test_df = X_test.copy()
test_df['y_true'] = y_test.values
test_df['y_pred'] = y_pred

# Extraction du département (depuis one-hot encoding)
dept_cols = [col for col in X.columns if col.startswith('departement_')]
test_df['departement'] = test_df[dept_cols].idxmax(axis=1).str.replace('departement_', '')

# Métriques par département
dept_metrics = test_df.groupby('departement').apply(lambda df: pd.Series({
    'mae': mean_absolute_error(df['y_true'], df['y_pred']),
    'rmse': np.sqrt(mean_squared_error(df['y_true'], df['y_pred'])),
    'r2': r2_score(df['y_true'], df['y_pred']),
    'n_samples': len(df)
})).sort_values('mae', ascending=False)

print("Départements avec les plus grandes erreurs:")
print(dept_metrics.head(10))
```

**Utilité** :
- Identifier les départements mal prédits (focus amélioration)
- Détecter les biais géographiques
- Valider l'équité du modèle

## Optimisation du Modèle

### Hyperparameter Tuning

**Méthode 1 : Grid Search**

```python
from sklearn.model_selection import GridSearchCV, TimeSeriesSplit

param_grid = {
    'n_estimators': [50, 100, 200],
    'max_depth': [10, 20, 30],
    'min_samples_split': [2, 5, 10],
    'min_samples_leaf': [1, 2, 4]
}

tscv = TimeSeriesSplit(n_splits=3)

grid_search = GridSearchCV(
    RandomForestRegressor(random_state=42, n_jobs=-1),
    param_grid,
    cv=tscv,
    scoring='neg_mean_absolute_error',
    verbose=2,
    n_jobs=1  # 1 car RF déjà parallélisé
)

grid_search.fit(X_train, y_train)

print("Meilleurs paramètres:", grid_search.best_params_)
print("Meilleur score CV:", -grid_search.best_score_)
```

**Attention** : Grid search est coûteux (3×3×3×3 = 81 modèles × 3 folds = 243 entraînements)

**Méthode 2 : Random Search** (plus rapide)

```python
from sklearn.model_selection import RandomizedSearchCV
from scipy.stats import randint, uniform

param_distributions = {
    'n_estimators': randint(50, 200),
    'max_depth': randint(10, 50),
    'min_samples_split': randint(2, 20),
    'min_samples_leaf': randint(1, 10),
    'max_features': ['sqrt', 'log2', None]
}

random_search = RandomizedSearchCV(
    RandomForestRegressor(random_state=42, n_jobs=-1),
    param_distributions,
    n_iter=50,  # Teste 50 combinaisons aléatoires
    cv=tscv,
    scoring='neg_mean_absolute_error',
    verbose=2,
    random_state=42
)

random_search.fit(X_train, y_train)
```

### Feature Engineering Avancé

**Nouvelles features potentielles** :

1. **Interactions** :
```python
# Ex: température × département
X['temp_x_dept'] = X['temperature'] * X['departement_75']
```

2. **Features cycliques** :
```python
# Jour de la semaine (cyclique)
X['day_of_week_sin'] = np.sin(2 * np.pi * date.dayofweek / 7)
X['day_of_week_cos'] = np.cos(2 * np.pi * date.dayofweek / 7)
```

3. **Agrégations multi-échelles** :
```python
# Moyennes 3j, 7j, 14j, 30j, 90j
for window in [3, 7, 14, 30, 90]:
    X[f'rolling_mean_{window}d'] = series.rolling(window).mean()
```

4. **Features externes** :
```python
# Jours fériés, vacances scolaires
X['is_holiday'] = date.isin(holidays)
X['is_vacation'] = date.isin(school_vacations)
```

### Sélection de Features

**Méthode 1 : Importance seuil**

```python
# Garder seulement les features avec importance > 0.01
selector = SelectFromModel(model, threshold=0.01, prefit=True)
X_selected = selector.transform(X)
```

**Méthode 2 : Recursive Feature Elimination**

```python
from sklearn.feature_selection import RFECV

rfecv = RFECV(
    estimator=RandomForestRegressor(n_estimators=50, random_state=42),
    step=5,
    cv=tscv,
    scoring='neg_mean_absolute_error'
)

rfecv.fit(X_train, y_train)
print(f"Nombre optimal de features: {rfecv.n_features_}")
```

## Modèles Alternatifs (Futures Versions)

### XGBoost

**Avantages** :
- Plus rapide que Random Forest
- Souvent plus performant (boosting vs bagging)
- Régularisation L1/L2 intégrée

**Configuration** :
```python
import xgboost as xgb

model = xgb.XGBRegressor(
    n_estimators=100,
    max_depth=6,
    learning_rate=0.1,
    subsample=0.8,
    colsample_bytree=0.8,
    objective='reg:squarederror',
    random_state=42
)
```

### LightGBM

**Avantages** :
- Très rapide (histogrammes)
- Gère mieux les grandes datasets
- Moins de mémoire

**Configuration** :
```python
import lightgbm as lgb

model = lgb.LGBMRegressor(
    n_estimators=100,
    max_depth=20,
    learning_rate=0.05,
    num_leaves=31,
    random_state=42
)
```

### Ensemble de Modèles

**Stacking** : Combiner plusieurs modèles

```python
from sklearn.ensemble import StackingRegressor

estimators = [
    ('rf', RandomForestRegressor(n_estimators=100)),
    ('xgb', xgb.XGBRegressor(n_estimators=100)),
    ('lgb', lgb.LGBMRegressor(n_estimators=100))
]

stacking = StackingRegressor(
    estimators=estimators,
    final_estimator=Ridge(),  # Meta-learner
    cv=tscv
)
```

## Monitoring en Production

### Détection de Data Drift

**Problème** : Distribution des features change avec le temps

**Solution** : Tests statistiques

```python
from scipy.stats import ks_2samp

# Comparer train vs nouvelles données
for col in X.columns:
    stat, p_value = ks_2samp(X_train[col], X_new[col])
    if p_value < 0.05:
        print(f"DRIFT détecté sur {col}: p={p_value:.4f}")
```

### Réentraînement Automatique

**Stratégie** :
1. Entraîner un nouveau modèle chaque semaine sur les N derniers mois
2. Comparer les performances sur une période de validation
3. Déployer le nouveau modèle si amélioration > 5%

```python
# Pseudo-code
def retrain_pipeline():
    X_new, y_new = load_recent_data(months=12)
    model_new = train_model(X_new, y_new)

    mae_old = evaluate(model_old, X_val, y_val)
    mae_new = evaluate(model_new, X_val, y_val)

    if mae_new < mae_old * 0.95:  # Amélioration > 5%
        deploy(model_new)
        archive(model_old)
```

## Checklist d'Entraînement

Avant chaque entraînement, vérifier :

- [ ] Données nettoyées et validées (`lumen_merged_clean.parquet` existe)
- [ ] Features générées (`features.parquet`, `y_target.parquet`)
- [ ] Pas de valeurs manquantes dans X et y
- [ ] Split temporel respecté (pas de shuffle)
- [ ] Hyperparamètres cohérents (reproductibilité)
- [ ] Métriques calculées sur test set uniquement
- [ ] Feature importance extraite et analysée
- [ ] Artefacts sauvegardés (`rf.joblib`, `metrics.json`)
- [ ] Logs d'entraînement archivés
- [ ] Documentation mise à jour

## Commandes Utiles

```bash
# Entraîner le modèle
python scripts/train_random_forest.py

# Pipeline complet (inclut entraînement)
python scripts/run_pipeline.py

# Examiner les métriques
cat data/artifacts/metrics.json | python -m json.tool

# Charger le modèle en Python
python -c "import joblib; m = joblib.load('data/artifacts/rf.joblib'); print(m)"

# Visualiser l'importance des features
python -c "
import json
import pandas as pd
imp = json.load(open('data/artifacts/feature_importance.json'))
df = pd.DataFrame(imp).head(10)
print(df.to_string(index=False))
"
```

## Ressources

**Documentation** :
- [Scikit-learn Random Forest](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestRegressor.html)
- [Time Series Cross-Validation](https://scikit-learn.org/stable/modules/cross_validation.html#time-series-split)
- [Feature Importance](https://scikit-learn.org/stable/auto_examples/ensemble/plot_forest_importances.html)

**Papers** :
- Breiman, L. (2001). "Random Forests". Machine Learning, 45(1), 5-32.
- Hastie, T. et al. (2009). "The Elements of Statistical Learning" (Ch. 15: Random Forests)

**Benchmarks** :
- [Kaggle: Random Forest vs XGBoost](https://www.kaggle.com/competitions)
- [Papers With Code: Time Series Forecasting](https://paperswithcode.com/task/time-series-forecasting)
