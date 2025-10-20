# 🎯 FLURISK - Indice de Risque Grippe

## 📊 Qu'est-ce que FLURISK ?

**FLURISK** est un **indice composite** calculé automatiquement par le script `fuse_data.py` qui combine plusieurs sources de données pour estimer le **risque de grippe** dans chaque région française.

### Échelle FLURISK
- **0-50** : Risque faible 🟢
- **50-70** : Risque moyen 🟠
- **70-100** : Risque élevé 🔴

---

## 🔗 Lien avec la pipeline

### Pipeline complète

```
1. collect_all_data.py
   ↓ Collecte 13 sources
   ├── Google Trends (recherches "grippe", "vaccin", "symptômes")
   ├── Wikipedia (vues pages "Grippe", "Vaccination")
   ├── SPF Urgences (passages aux urgences pour grippe)
   ├── SPF Sentinelles (cas de grippe détectés)
   ├── SPF IAS (Indicateurs Avancés Sanitaires)
   ├── SPF Vaccination (taux de couverture vaccinale)
   ├── INSEE Population (population totale, % 65+)
   └── Météo (température, humidité)

2. fuse_data.py
   ↓ Fusionne les données
   ↓ Crée les features (lags, moyennes mobiles, z-scores)
   ↓ **CALCULE FLURISK** ← ICI
   └── Sauvegarde dans data/processed/

3. train_model.py
   ↓ Utilise FLURISK comme feature
   └── Entraîne les modèles Random Forest
```

---

## 🧮 Formule de calcul FLURISK

FLURISK est calculé comme une **moyenne pondérée** de 5 composantes :

```python
FLURISK = 0.25 × Vaccination (inversée)
        + 0.25 × IAS (syndrome grippal)
        + 0.20 × Google Trends (z-score normalisé)
        + 0.15 × Wikipedia (z-score normalisé)
        + 0.15 × Population 65+ (%)
```

### Détail des composantes

#### 1. **Vaccination** (25% du score) - Inversée
```python
vaccination_score = 100 - taux_vaccination
```
- **Source** : `SPF Vaccination` (collect_spf_data.py)
- **Logique** : Plus le taux de vaccination est **bas**, plus le risque est **élevé**
- **Exemple** : 
  - Taux vaccination = 60% → Score = 40
  - Taux vaccination = 30% → Score = 70

#### 2. **IAS - Indicateurs Avancés Sanitaires** (25% du score)
```python
ias_score = ias_syndrome_grippal × 50
```
- **Source** : `SPF IAS` (collect_spf_data.py)
- **Logique** : Indicateurs précoces de l'activité grippale
- **Échelle** : 0-100

#### 3. **Google Trends** (20% du score)
```python
trends_score = (google_trends_zscore + 2) × 25
```
- **Source** : `Google Trends` (collect_google_trends.py)
- **Logique** : Volume de recherches "grippe", "symptômes grippe"
- **Normalisation** : Z-score (écart à la moyenne)
- **Interprétation** : Pic de recherches = intérêt accru = épidémie probable

#### 4. **Wikipedia** (15% du score)
```python
wiki_score = (wiki_grippe_views_zscore + 2) × 25
```
- **Source** : `Wikipedia` (collect_wikipedia.py)
- **Logique** : Vues de la page "Grippe" sur Wikipedia FR
- **Normalisation** : Z-score
- **Interprétation** : Pic de consultations = recherche d'informations = épidémie

#### 5. **Population 65+** (15% du score)
```python
age_score = pct_65_plus
```
- **Source** : `INSEE Population` (collect_context_data.py)
- **Logique** : Population âgée = plus vulnérable à la grippe
- **Exemple** : 
  - Région avec 20% de 65+ → Score = 20
  - Région avec 25% de 65+ → Score = 25

---

## 📍 Où est calculé FLURISK ?

### Dans `fuse_data.py` - Fonction `calculate_flurisk()`

```python
def calculate_flurisk(self, df):
    """Calcule l'indice FLURISK pour chaque département"""
    
    # 1. Vaccination (inversée)
    flurisk_components['vaccination'] = 100 - df['taux_vaccination']
    
    # 2. IAS
    flurisk_components['ias'] = df['ias_syndrome_grippal'] * 50
    
    # 3. Google Trends (z-score)
    flurisk_components['trends'] = (df['wiki_grippe_views_zscore'] + 2) * 25
    
    # 4. Wikipedia (z-score)
    flurisk_components['wiki'] = (df['wiki_grippe_views_zscore'] + 2) * 25
    
    # 5. Population 65+
    flurisk_components['age'] = df['pct_65_plus']
    
    # Calcul FLURISK avec pondérations
    df['flurisk'] = (
        0.25 * flurisk_components['vaccination'] +
        0.25 * flurisk_components['ias'] +
        0.20 * flurisk_components['trends'] +
        0.15 * flurisk_components['wiki'] +
        0.15 * flurisk_components['age']
    )
    
    # Normalisation finale (0-100)
    df['flurisk'] = np.clip(df['flurisk'], 0, 100)
    
    return df
```

---

## 🔄 Flux de données pour FLURISK

### Étape 1 : Collecte (collect_all_data.py)
```
collect_google_trends.py    → ../data/google_trends/google_trends_latest.csv
collect_wikipedia.py         → ../data/wikipedia/wikipedia_latest.csv
collect_spf_data.py          → ../data/spf/spf_urgences_*.csv
                             → ../data/spf/spf_ias_*.csv
                             → ../data/spf/spf_vaccination_*.csv
collect_context_data.py      → ../data/context/context_population_*.csv
```

### Étape 2 : Fusion (fuse_data.py)
```
1. load_latest_files()       → Charge tous les CSV
2. create_weekly_dataset()   → Fusionne par date + région
3. add_features()            → Ajoute lags, moyennes mobiles, z-scores
4. calculate_flurisk()       → CALCULE FLURISK ← ICI
5. save_processed_data()     → ../data/processed/dataset_grippe_*.csv
```

### Étape 3 : Modélisation (train_model.py)
```
1. load_data()               → Charge dataset_grippe_*.csv
2. prepare_features()        → Sélectionne features (dont FLURISK)
3. train_all_models()        → Entraîne RF avec FLURISK comme feature
4. save_models()             → ../models/rf_grippe_*.pkl
```

---

## 📊 Exemple de résultat FLURISK

Après exécution de `fuse_data.py`, vous verrez :

```
📊 Calcul de l'indice FLURISK...
  ✅ FLURISK calculé: min=15.3, max=78.9, moy=42.1

🎯 FLURISK par région (dernière semaine):
   Île-de-France: 68.5
   Hauts-de-France: 62.3
   Grand Est: 58.7
   Auvergne-Rhône-Alpes: 54.2
   Provence-Alpes-Côte d'Azur: 51.8
   ...
```

---

## 🎯 Utilisation de FLURISK

### Dans le dataset final
FLURISK est une **colonne** du dataset `data/processed/dataset_grippe_*.csv` :

```csv
date,region,urgences_grippe,taux_vaccination,flurisk,...
2024-01-08,Île-de-France,1250,58.3,68.5,...
2024-01-08,Hauts-de-France,890,52.1,62.3,...
```

### Dans le modèle Random Forest
FLURISK est utilisé comme **feature** (variable explicative) pour prédire les cas de grippe futurs :

```
Features utilisées par le modèle:
- urgences_grippe_lag1
- urgences_grippe_lag2
- flurisk ← ICI
- google_trends_grippe
- wiki_grippe_views
- temperature
- humidity
- ...
```

---

## 💡 Pourquoi FLURISK est utile ?

### 1. **Indicateur composite**
Combine plusieurs sources en un seul score facile à interpréter

### 2. **Détection précoce**
Utilise des signaux avancés (Google Trends, Wikipedia, IAS)

### 3. **Feature pour ML**
Améliore les prédictions du modèle Random Forest

### 4. **Visualisation**
Permet de comparer facilement les régions

### 5. **Aide à la décision**
Les autorités peuvent prioriser les régions à risque élevé

---

## 🔧 Personnalisation

Vous pouvez modifier les **pondérations** dans `fuse_data.py` :

```python
# Pondérations actuelles
df['flurisk'] = (
    0.25 * vaccination +  # 25% - Vaccination
    0.25 * ias +          # 25% - IAS
    0.20 * trends +       # 20% - Google Trends
    0.15 * wiki +         # 15% - Wikipedia
    0.15 * age            # 15% - Population 65+
)

# Exemple: Donner plus d'importance à la vaccination
df['flurisk'] = (
    0.40 * vaccination +  # 40% - Vaccination
    0.20 * ias +          # 20% - IAS
    0.15 * trends +       # 15% - Google Trends
    0.15 * wiki +         # 15% - Wikipedia
    0.10 * age            # 10% - Population 65+
)
```

---

## 📝 Résumé

✅ **FLURISK** = Indice composite (0-100) calculé par `fuse_data.py`  
✅ Combine **5 sources** : Vaccination, IAS, Google Trends, Wikipedia, Démographie  
✅ Calculé pour **chaque région** et **chaque semaine**  
✅ Utilisé comme **feature** dans le modèle Random Forest  
✅ Permet de **détecter précocement** les épidémies  
✅ Facilite la **comparaison** entre régions  

**FLURISK est le lien entre la collecte de données et la prédiction !** 🎯

┌─────────────────────────────────────────────────────────┐
│  1. COLLECTE (collect_all_data.py)                      │
├─────────────────────────────────────────────────────────┤
│  collect_google_trends.py    → Google Trends            │
│  collect_wikipedia.py         → Wikipedia               │
│  collect_spf_data.py          → Urgences, IAS, Vaccin   │
│  collect_context_data.py      → Population, Météo       │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│  2. FUSION + FLURISK (fuse_data.py)                     │
├─────────────────────────────────────────────────────────┤
│  1. Charge les 13 sources                               │
│  2. Fusionne par date + région                          │
│  3. Ajoute features (lags, MA, z-scores)                │
│  4. ✨ CALCULE FLURISK ✨                               │
│  5. Sauvegarde → data/processed/dataset_grippe_*.csv    │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│  3. MODÉLISATION (train_model.py)                       │
├─────────────────────────────────────────────────────────┤
│  1. Charge dataset avec FLURISK                         │
│  2. Utilise FLURISK comme feature                       │
│  3. Entraîne Random Forest                              │
│  4. Prédit cas de grippe J+7, J+14, J+21, J+28          │
└─────────────────────────────────────────────────────────┘