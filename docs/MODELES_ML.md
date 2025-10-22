# 🤖 LUMEN - Modèles Machine Learning

## 📋 Table des Matières
- [Vue d'ensemble](#vue-densemble)
- [Modèle Principal](#modèle-principal)
- [Architecture du Modèle](#architecture-du-modèle)
- [Hyperparamètres](#hyperparamètres)
- [Performance](#performance)
- [Comparaison de Modèles](#comparaison-de-modèles)
- [Entraînement](#entraînement)

---

## 🎯 Vue d'ensemble

LUMEN utilise actuellement **UN SEUL modèle** de Machine Learning pour les prédictions :

### Modèle Utilisé
- **🌳 Random Forest Regressor** (Forêt Aléatoire)
- **Bibliothèque** : scikit-learn
- **Type** : Régression (prédiction de valeurs continues)
- **Fichier** : `ml/train_random_forest.py`

### Pourquoi Random Forest ?

✅ **Avantages** :
- **Robuste** : Résistant au sur-apprentissage
- **Performant** : Excellentes performances sans tuning intensif
- **Interprétable** : Importance des features facilement analysable
- **Versatile** : Gère bien les relations non-linéaires
- **Stable** : Peu sensible aux valeurs aberrantes

❌ **Inconvénients** :
- Temps d'entraînement plus long que les modèles linéaires
- Taille du modèle plus importante
- Moins performant sur données très volumineuses (>1M lignes)

---

## 🌳 Modèle Principal : Random Forest Regressor

### Description

Le **Random Forest** est un ensemble de **300 arbres de décision** qui votent pour faire une prédiction. Chaque arbre est entraîné sur un sous-ensemble aléatoire des données.

### Architecture

```
🌳 Random Forest Regressor
├── 300 arbres de décision
├── Profondeur maximale: 10 niveaux
├── Échantillonnage: Bootstrap (avec remplacement)
├── Features par split: sqrt(n_features)
└── Prédiction finale: Moyenne des 300 arbres
```

### Hyperparamètres Actuels

```python
RandomForestRegressor(
    n_estimators=300,      # Nombre d'arbres
    max_depth=10,          # Profondeur maximale
    random_state=42,       # Reproductibilité
    n_jobs=-1              # Utilise tous les CPU
)
```

| Paramètre | Valeur | Description |
|-----------|--------|-------------|
| **n_estimators** | 300 | Nombre d'arbres dans la forêt |
| **max_depth** | 10 | Profondeur maximale de chaque arbre |
| **random_state** | 42 | Graine aléatoire pour reproductibilité |
| **n_jobs** | -1 | Parallélisation (tous les CPU) |
| **min_samples_split** | 2 (défaut) | Minimum d'échantillons pour split |
| **min_samples_leaf** | 1 (défaut) | Minimum d'échantillons par feuille |
| **max_features** | auto (défaut) | Features considérées par split |

---

## 📊 Performance

### Métriques Actuelles

D'après les mémoires du projet :

| Métrique | Valeur | Description |
|----------|--------|-------------|
| **R² Score** | 0.971 | 97.1% de variance expliquée |
| **MAE** | 5.08 | Erreur absolue moyenne |
| **RMSE** | 8.23 | Erreur quadratique moyenne |

**Note** : Ces métriques peuvent varier selon la version du dataset.

### Interprétation

- **R² = 0.971** : Le modèle explique **97.1%** de la variance des données
  - Excellent (>0.9)
  - Risque de sur-apprentissage à surveiller
  
- **MAE = 5.08** : En moyenne, le modèle se trompe de **5.08 passages aux urgences**
  - Très bon pour des valeurs allant de 0 à plusieurs centaines
  
- **RMSE = 8.23** : Pénalise davantage les grandes erreurs
  - Légèrement supérieur au MAE (normal)

### Importance des Features

**Top 10 des features les plus importantes** (selon les mémoires) :

1. **passages_urgences_lag1** : Passages urgences semaine précédente
2. **temperature_moyenne** : Température moyenne
3. **humidite** : Humidité relative
4. **pop_65_plus** : Population +65 ans
5. **densite** : Densité de population
6. **passages_urgences_ma3** : Moyenne mobile 3 semaines
7. **sin_semaine** : Saisonnalité (sin)
8. **cos_semaine** : Saisonnalité (cos)
9. **temp_humidite** : Interaction température-humidité
10. **taux_urbanisation** : Taux d'urbanisation

---

## 🔬 Comparaison de Modèles

### Modèles Testés (Selon Architecture Mémoire)

D'après la mémoire système, plusieurs modèles ont été envisagés :

| Modèle | Type | Avantages | Inconvénients | Statut |
|--------|------|-----------|---------------|--------|
| **Random Forest** | Ensemble | Robuste, performant | Lent, volumineux | ✅ **UTILISÉ** |
| **Ridge** | Linéaire | Rapide, simple | Moins performant | 🔄 Envisagé |
| **LightGBM** | Gradient Boosting | Très rapide, performant | Complexe | 🔄 Envisagé |
| **XGBoost** | Gradient Boosting | Très performant | Complexe, lent | 🔄 Envisagé |
| **ElasticNet** | Linéaire | Régularisation L1+L2 | Linéaire | 🔄 Envisagé |
| **SARIMAX** | Série temporelle | Spécialisé temps | Complexe | 🔄 Envisagé |

### Pourquoi Random Forest a été Choisi ?

1. **Équilibre performance/complexité** : Excellent R² sans tuning intensif
2. **Robustesse** : Gère bien les outliers et valeurs manquantes
3. **Interprétabilité** : Feature importance claire
4. **Stabilité** : Résultats reproductibles
5. **Pas de scaling requis** : Contrairement aux modèles linéaires

---

## 🚀 Entraînement du Modèle

### Script d'Entraînement

**Fichier** : `ml/train_random_forest.py`

**Commande** :
```bash
python3 ml/train_random_forest.py
```

### Pipeline d'Entraînement

```
1. CHARGEMENT DU DATASET
   ↓ data/processed/clean_dataset.csv
   
2. PRÉPARATION DES FEATURES
   ↓ Sélection features numériques
   ↓ Exclusion colonnes non pertinentes
   
3. SPLIT TRAIN/TEST (80/20)
   ↓ Train: 80% des données
   ↓ Test: 20% des données
   
4. ENTRAÎNEMENT RANDOM FOREST
   ↓ 300 arbres, profondeur 10
   ↓ Parallélisation sur tous les CPU
   
5. ÉVALUATION
   ↓ Calcul MAE, R², RMSE
   ↓ Analyse importance features
   
6. GÉNÉRATION PRÉDICTIONS
   ↓ Prédictions sur tout le dataset
   ↓ Calcul écarts et erreurs
   
7. SAUVEGARDE
   ↓ ml/artefacts/random_forest.pkl
   ↓ ml/artefacts/metrics.json
   ↓ ml/artefacts/feature_importance.csv
   ↓ data/processed/predictions.csv
```

### Durée d'Entraînement

- **Chargement** : ~1-2 secondes
- **Préparation** : ~1-2 secondes
- **Entraînement** : ~30-60 secondes (selon CPU)
- **Évaluation** : ~5-10 secondes
- **Sauvegarde** : ~2-5 secondes

**Total** : ~1-2 minutes

---

## 📁 Artefacts Générés

Après l'entraînement, les fichiers suivants sont créés :

### 1. Modèle Entraîné
**Fichier** : `ml/artefacts/random_forest.pkl`
- Modèle Random Forest sérialisé (joblib)
- Utilisable pour prédictions futures
- Taille : ~5-50 MB (selon complexité)

### 2. Métriques de Performance
**Fichier** : `ml/artefacts/metrics.json`
```json
{
  "model_type": "RandomForestRegressor",
  "target": "nb_passages",
  "features_count": 25,
  "train_samples": 3360,
  "test_samples": 840,
  "MAE": 5.08,
  "R2": 0.971,
  "timestamp": "2025-10-22T14:30:00"
}
```

### 3. Importance des Features
**Fichier** : `ml/artefacts/feature_importance.csv`
```csv
feature,importance
passages_urgences_lag1,0.3542
temperature_moyenne,0.1823
humidite,0.1245
...
```

**Graphique** : `ml/artefacts/feature_importance.png`
- Graphique en barres horizontales
- Visualisation de l'importance de chaque feature

### 4. Prédictions
**Fichier** : `data/processed/predictions.csv`
- Dataset complet avec prédictions
- Colonnes ajoutées :
  - `pred_nb_passages` : Prédiction du modèle
  - `ecart` : Différence (réel - prédit)
  - `ecart_absolu` : Valeur absolue de l'écart
  - `ecart_pct` : Écart en pourcentage

### 5. Rapport de Performance
**Fichier** : `ml/artefacts/performance_report.json`
- Rapport détaillé complet
- Statistiques sur les prédictions
- Informations sur le modèle

**Fichier** : `ml/artefacts/TRAINING_SUMMARY.txt`
- Résumé lisible du training
- Top 5 features importantes
- Métriques principales

---

## 🔧 Optimisation et Tuning

### Hyperparamètres à Ajuster

Si les performances ne sont pas satisfaisantes, voici les paramètres à modifier :

#### 1. Nombre d'Arbres (`n_estimators`)
```python
# Actuel: 300
# Augmenter pour plus de précision (mais plus lent)
n_estimators=500  # Plus précis
n_estimators=100  # Plus rapide
```

#### 2. Profondeur Maximale (`max_depth`)
```python
# Actuel: 10
# Augmenter si sous-apprentissage
max_depth=15  # Plus complexe
max_depth=5   # Plus simple (évite sur-apprentissage)
```

#### 3. Échantillons Minimum par Split
```python
# Ajouter pour éviter sur-apprentissage
min_samples_split=10  # Minimum 10 échantillons pour split
min_samples_leaf=5    # Minimum 5 échantillons par feuille
```

#### 4. Features par Split
```python
# Contrôler la randomisation
max_features='sqrt'  # Racine carrée du nombre de features
max_features='log2'  # Log2 du nombre de features
max_features=0.5     # 50% des features
```

### Grid Search (Recherche Exhaustive)

Pour trouver les meilleurs hyperparamètres :

```python
from sklearn.model_selection import GridSearchCV

param_grid = {
    'n_estimators': [100, 200, 300],
    'max_depth': [5, 10, 15],
    'min_samples_split': [2, 5, 10],
    'min_samples_leaf': [1, 2, 5]
}

grid_search = GridSearchCV(
    RandomForestRegressor(random_state=42),
    param_grid,
    cv=5,
    scoring='r2',
    n_jobs=-1
)

grid_search.fit(X_train, y_train)
best_model = grid_search.best_estimator_
```

---

## 🎯 Variable Cible (Target)

### Variable Prédite

**Variable** : `nb_passages` (ou similaire selon le dataset)

**Description** : Nombre de passages aux urgences pour syndrome grippal

**Type** : Continue (régression)

**Plage** : 0 à plusieurs centaines

### Transformation de la Cible

Actuellement, **aucune transformation** n'est appliquée à la cible.

**Transformations possibles** (si nécessaire) :
- **Log** : `log(y + 1)` pour réduire l'impact des valeurs extrêmes
- **Standardisation** : `(y - mean) / std` pour normaliser
- **Binning** : Transformer en classes (classification)

---

## 📈 Évolution Future

### Modèles à Tester

1. **LightGBM** 🚀
   - Plus rapide que Random Forest
   - Très performant sur gros datasets
   - Moins de mémoire requise

2. **XGBoost** 💪
   - Souvent meilleur que Random Forest
   - Régularisation intégrée
   - Gestion native des valeurs manquantes

3. **Ridge/Lasso** ⚡
   - Très rapides
   - Bons pour baseline
   - Interprétables

4. **SARIMAX** 📅
   - Spécialisé séries temporelles
   - Capture saisonnalité
   - Prédictions à long terme

### Ensemble de Modèles

**Stacking** : Combiner plusieurs modèles

```python
from sklearn.ensemble import StackingRegressor

estimators = [
    ('rf', RandomForestRegressor()),
    ('gb', GradientBoostingRegressor()),
    ('ridge', Ridge())
]

stacking = StackingRegressor(
    estimators=estimators,
    final_estimator=Ridge()
)
```

---

## 🔍 Diagnostic et Monitoring

### Vérifier les Performances

```bash
# Voir les métriques
cat ml/artefacts/metrics.json

# Voir le résumé
cat ml/artefacts/TRAINING_SUMMARY.txt

# Voir l'importance des features
cat ml/artefacts/feature_importance.csv
```

### Signes de Sur-Apprentissage

⚠️ **Attention si** :
- R² train >> R² test (écart >0.1)
- R² = 1.000 (trop parfait)
- MAE train << MAE test

**Solutions** :
- Réduire `max_depth`
- Augmenter `min_samples_split`
- Augmenter `min_samples_leaf`
- Ajouter plus de données

### Signes de Sous-Apprentissage

⚠️ **Attention si** :
- R² < 0.7 (mauvais)
- MAE très élevé
- Prédictions plates (peu de variance)

**Solutions** :
- Augmenter `max_depth`
- Augmenter `n_estimators`
- Ajouter plus de features
- Essayer un modèle plus complexe (XGBoost)

---

## 📚 Ressources

### Documentation scikit-learn
- [Random Forest Regressor](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestRegressor.html)
- [Ensemble Methods](https://scikit-learn.org/stable/modules/ensemble.html)

### Tutoriels
- [Random Forest Explained](https://towardsdatascience.com/understanding-random-forest-58381e0602d2)
- [Hyperparameter Tuning](https://towardsdatascience.com/hyperparameter-tuning-the-random-forest-in-python-using-scikit-learn-28d2aa77dd74)

---

## 📞 Commandes Utiles

```bash
# Entraîner le modèle
python3 ml/train_random_forest.py

# Voir les métriques
cat ml/artefacts/metrics.json | python3 -m json.tool

# Voir l'importance des features
cat ml/artefacts/feature_importance.csv | column -t -s,

# Charger le modèle en Python
python3 -c "import joblib; model = joblib.load('ml/artefacts/random_forest.pkl'); print(model)"
```

---

**🤖 LUMEN Enhanced - Machine Learning**

*Random Forest • Performance • Robustesse*
