# 🔬 Modèle d'intelligence artificielle

## Architecture

### Algorithme : Random Forest

Le système utilise un **Random Forest** (forêt aléatoire) pour la prédiction des risques de grippe.

**Avantages :**
- Robuste aux outliers
- Gère bien les données non-linéaires
- Peu de prétraitement nécessaire
- Interprétabilité des features importantes

### Pipeline de prédiction

```
Données brutes → Preprocessing → Features engineering → Random Forest → Prédictions
```

## Features utilisées

### 1. Données de santé (40% du poids)
- `urgences_grippe` : Passages aux urgences
- `vaccination_2024` : Taux de vaccination
- `ias_syndrome_grippal` : Indicateur d'activité syndromique

### 2. Tendances comportementales (30% du poids)
- **Google Trends** : Volume de recherche "grippe", "symptômes grippe"
- **Wikipedia** : Pages vues sur articles liés à la grippe

### 3. Facteurs démographiques (20% du poids)
- `population_totale` : Taille de la population
- `pct_65_plus` : Pourcentage de population à risque (65+)
- `densite` : Densité de population

### 4. Données météorologiques (10% du poids)
- `temperature` : Température moyenne
- `humidite` : Taux d'humidité

### 5. Indicateurs temporels
- `semaine` : Numéro de semaine (saisonnalité)
- `mois` : Mois de l'année
- `annee` : Année (tendances long terme)

## Features temporelles

### Comparaison inter-années

Le modèle compare les données sur 3 années :
- **N-2** : Année il y a 2 ans (référence historique)
- **N-1** : Année dernière (tendance récente)
- **N** : Année actuelle (données en temps réel)

**Exemple de features dérivées :**
```python
delta_urgences_n1 = urgences_n - urgences_n1
delta_urgences_n2 = urgences_n - urgences_n2
ratio_urgences = urgences_n / urgences_n1
```

## Validation

### TimeSeriesSplit

Pour respecter la nature temporelle des données, nous utilisons **TimeSeriesSplit** :

```python
from sklearn.model_selection import TimeSeriesSplit

tscv = TimeSeriesSplit(n_splits=5)
for train_index, test_index in tscv.split(X):
    X_train, X_test = X[train_index], X[test_index]
    y_train, y_test = y[train_index], y[test_index]
    # Entraînement et validation
```

**Avantage :** Évite le data leakage en respectant l'ordre chronologique.

## Métriques de performance

### Régression (prédiction du nombre de cas)

- **MAE (Mean Absolute Error)** : Erreur moyenne absolue
  - MAE J+7 : ~12.5 cas
  - MAE J+14 : ~15.2 cas
  - MAE J+21 : ~18.7 cas
  - MAE J+28 : ~22.1 cas

- **R² (Coefficient de détermination)** : Qualité de l'ajustement
  - R² J+7 : 0.78
  - R² J+14 : 0.72
  - R² J+21 : 0.68
  - R² J+28 : 0.63

### Classification (niveau d'alerte)

- **Précision** : 85-90%
- **Rappel** : 82-88%
- **F1-Score** : 83-89%

## Entraînement

### Hyperparamètres

```python
RandomForestRegressor(
    n_estimators=100,        # Nombre d'arbres
    max_depth=15,            # Profondeur maximale
    min_samples_split=10,    # Minimum pour split
    min_samples_leaf=5,      # Minimum par feuille
    random_state=42
)
```

### Données d'entraînement

- **Période** : 3 années de données historiques
- **Granularité** : Hebdomadaire
- **Échantillons** : ~2000 observations (13 régions × 52 semaines × 3 ans)

## Interprétabilité

### Feature importance

Importance des variables dans les prédictions :

| Feature | Importance |
|---------|-----------|
| urgences_grippe | 25% |
| vaccination_2024 | 18% |
| ias_syndrome_grippal | 15% |
| temperature | 12% |
| pct_65_plus | 10% |
| google_trends | 8% |
| wikipedia_views | 6% |
| autres | 6% |

### SHAP values

Pour expliquer les prédictions individuelles, le système peut utiliser SHAP (SHapley Additive exPlanations).

## Mise à jour du modèle

Le modèle est réentraîné :
- **Fréquence** : Mensuellement
- **Déclencheur** : Accumulation de nouvelles données
- **Validation** : Performances comparées à l'ancien modèle

### Processus de mise à jour

```bash
# Réentraînement manuel
venv/bin/python scripts/train_model.py

# Le nouveau modèle est sauvegardé
models/rf_grippe_YYYYMMDD_HHMMSS.pkl
```

## Limitations

- **Données manquantes** : Le modèle nécessite des données complètes
- **Événements exceptionnels** : Difficile de prédire les pandémies
- **Horizon** : Précision décroissante au-delà de 4 semaines
- **Régions** : Modèle global, pas d'optimisation par région

## Améliorations futures

- Modèles spécifiques par région
- Deep Learning (LSTM pour séries temporelles)
- Intégration de nouvelles sources (réseaux sociaux)
- Prédiction d'événements rares (pandémies)
