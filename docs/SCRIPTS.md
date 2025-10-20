# 📊 Scripts de la pipeline de collecte de données

## 📁 Scripts existants

### ✅ Scripts de collecte de données (EXISTANTS)

| Script | Fonction | Sources | Statut |
|--------|----------|---------|--------|
| **`collect_all_data.py`** | **Orchestrateur principal** | Appelle tous les collecteurs | ✅ **EXISTE** |
| `collect_google_trends.py` | Google Trends | Recherches "grippe", "vaccin", "symptômes" | ✅ Existe |
| `collect_wikipedia.py` | Wikipedia | Vues pages "Grippe" et "Vaccination" | ✅ Existe |
| `collect_spf_data.py` | Santé Publique France | Urgences, sentinelles, vaccination, IAS | ✅ Existe |
| `collect_context_data.py` | Données contextuelles | Population INSEE, météo | ✅ Existe |

### 🔄 Scripts de traitement (EXISTANTS)

| Script | Fonction | Statut |
|--------|----------|--------|
| **`fuse_data.py`** | Fusion de toutes les sources | ✅ Existe |
| **`train_model.py`** | Entraînement Random Forest | ✅ Existe |

### 👁️ Scripts de visualisation (EXISTANTS)

| Script | Fonction | Statut |
|--------|----------|--------|
| **`app.py`** | Application web Streamlit interactive | ✅ Existe |
| **`demo.py`** | Script de vérification rapide (terminal) | ✅ Existe |

### 🆕 Scripts créés récemment (PAR MOI)

| Script | Fonction | Statut |
|--------|----------|--------|
| `01_clean_data.py` | Nettoyage avec URLs | 🆕 Nouveau |
| `02_merge_data.py` | Fusion simplifiée | 🆕 Nouveau |
| `03_predict.py` | Prédiction simplifiée | 🆕 Nouveau |
| `run_pipeline.py` | Orchestrateur simple | 🆕 Nouveau |

---

## 🎯 Script orchestrateur principal : `collect_all_data.py`

### ✅ Ce qu'il fait déjà

```python
# Étape 1: Google Trends
from collect_google_trends import GoogleTrendsCollector
gt_collector = GoogleTrendsCollector()
gt_data = gt_collector.collect_all_data()

# Étape 2: Wikipedia
from collect_wikipedia import WikipediaCollector
wiki_collector = WikipediaCollector()
wiki_data = wiki_collector.collect_all_data()

# Étape 3: SPF (Santé Publique France)
from collect_spf_data import SPFDataCollector
spf_collector = SPFDataCollector()
spf_data = spf_collector.collect_all_data()

# Étape 4: Contexte (INSEE + Météo)
from collect_context_data import ContextDataCollector
context_collector = ContextDataCollector()
context_data = context_collector.collect_all_data()
```

### 📊 Sources collectées (13 au total)

1. **Google Trends** (3 sources)
   - Recherches "grippe"
   - Recherches "vaccin grippe"
   - Recherches "symptômes grippe"

2. **Wikipedia** (2 sources)
   - Vues page "Grippe"
   - Vues page "Vaccination"

3. **SPF - Santé Publique France** (4 sources)
   - Urgences grippe
   - Sentinelles
   - Vaccination
   - IAS (Indicateurs Avancés Sanitaires)

4. **Contexte** (2 sources)
   - Population INSEE (par région)
   - Météo (température, humidité)

5. **Autres** (2 sources potentielles)
   - Données réelles Google Trends
   - Données réelles INSEE/Météo

---

## 🔄 Pipeline complète existante

```
┌─────────────────────────────────────────────────────────────┐
│                   COLLECTE DES DONNÉES                      │
│                  (collect_all_data.py)                      │
└─────────────────────────────────────────────────────────────┘
                            ↓
        ┌───────────────────┼───────────────────┐
        ↓                   ↓                   ↓
┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│ Google       │   │ Wikipedia    │   │ SPF          │
│ Trends       │   │              │   │              │
└──────────────┘   └──────────────┘   └──────────────┘
        ↓                   ↓                   ↓
        └───────────────────┼───────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                   FUSION DES DONNÉES                        │
│                     (fuse_data.py)                          │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              ENTRAÎNEMENT DU MODÈLE                         │
│                  (train_model.py)                           │
└─────────────────────────────────────────────────────────────┘
```

---

## 📂 Structure des données

```
data/
├── google_trends/
│   └── google_trends_latest.csv
├── wikipedia/
│   └── wikipedia_latest.csv
├── spf/
│   ├── spf_urgences_*.csv
│   ├── spf_sentinelles_*.csv
│   ├── spf_vaccination_*.csv
│   └── spf_ias_*.csv
├── context/
│   ├── context_population_*.csv
│   └── context_weather_*.csv
└── processed/
    └── dataset_grippe_*.csv
```

---

## ⚖️ Comparaison : Pipeline existante vs nouvelle

| Aspect | Pipeline EXISTANTE | Pipeline NOUVELLE (créée) |
|--------|-------------------|---------------------------|
| **Collecte** | ✅ Complète (13 sources) | ⚠️ Simplifiée (5 sources) |
| **Sources** | Google Trends, Wikipedia, SPF, INSEE, Météo | URLs data.gouv.fr uniquement |
| **Orchestrateur** | ✅ `collect_all_data.py` | 🆕 `run_pipeline.py` |
| **Fusion** | ✅ `fuse_data.py` (complet) | 🆕 `02_merge_data.py` (simple) |
| **Modèle** | ✅ `train_model.py` (complet) | 🆕 `03_predict.py` (simple) |
| **Features** | ✅ Très complet (lags, MA, z-scores) | ⚠️ Basique (lags, MA) |
| **FLURISK** | ✅ Calculé | ❌ Non calculé |
| **Données réelles** | ✅ Scripts pour vraies APIs | ❌ Données simulées |

---

## 🎯 Recommandations

### ✅ CE QUI EXISTE DÉJÀ ET FONCTIONNE

1. **`collect_all_data.py`** - Orchestrateur complet ✅
   - Appelle tous les collecteurs
   - Gère les erreurs
   - Affiche les statistiques

2. **`fuse_data.py`** - Fusion complète ✅
   - Fusionne les 13 sources
   - Crée des features avancées
   - Calcule FLURISK
   - Gestion des régions

3. **`train_model.py`** - Modèle complet ✅
   - Multi-horizons (J+7, J+14, J+21, J+28)
   - Métriques détaillées
   - Sauvegarde des modèles

### 🔧 CE QU'IL FAUT FAIRE

#### Option 1 : Utiliser la pipeline existante (RECOMMANDÉ) ✅

```bash
# Étape 1: Collecter toutes les données
python scripts/collect_all_data.py

# Étape 2: Fusionner les données
python scripts/fuse_data.py

# Étape 3: Entraîner le modèle
python scripts/train_model.py
```

#### Option 2 : Créer un orchestrateur global

Créer un nouveau script `run_full_pipeline.py` qui appelle :
1. `collect_all_data.py`
2. `fuse_data.py`
3. `train_model.py`

#### Option 3 : Améliorer les collecteurs existants

- Ajouter les vraies URLs dans les collecteurs
- Utiliser `data_urls_config.json` comme configuration
- Améliorer la gestion des erreurs

---

## 🚨 Points d'attention

### ⚠️ Doublons détectés

Vous avez maintenant **DEUX pipelines** :

1. **Pipeline EXISTANTE** (complète, professionnelle)
   - `collect_all_data.py` → `fuse_data.py` → `train_model.py`
   - 13 sources de données
   - Features avancées
   - FLURISK calculé

2. **Pipeline NOUVELLE** (simple, basique)
   - `run_pipeline.py` → `01_clean_data.py` → `02_merge_data.py` → `03_predict.py`
   - 5 sources de données
   - Features basiques
   - Pas de FLURISK

### 💡 Recommandation finale

**UTILISER LA PIPELINE EXISTANTE** et créer simplement un orchestrateur global :

```python
# run_full_pipeline.py
import subprocess

# Étape 1: Collecte
subprocess.run(['python', 'scripts/collect_all_data.py'])

# Étape 2: Fusion
subprocess.run(['python', 'scripts/fuse_data.py'])

# Étape 3: Modèle
subprocess.run(['python', 'scripts/train_model.py'])
```

---

## 📝 Conclusion

✅ **Vous avez déjà une pipeline complète et fonctionnelle !**

- `collect_all_data.py` collecte tout
- `fuse_data.py` fusionne tout
- `train_model.py` entraîne tout

**Il suffit de créer un script orchestrateur qui les appelle dans l'ordre.**

### ✅ Script orchestrateur créé : `run_full_pipeline.py`

**Script qui exécute automatiquement les 3 étapes de la pipeline.**

#### Utilisation
```bash
python run_full_pipeline.py
```

#### Ce qu'il fait
1. ✅ Exécute `collect_all_data.py` (Collecte)
2. ✅ Exécute `fuse_data.py` (Fusion + FLURISK)
3. ✅ Exécute `train_model.py` (Entraînement)
4. ✅ Affiche un résumé détaillé avec durées
5. ✅ Gère les erreurs et arrête si une étape échoue

#### Avantages
- 🎯 Une seule commande pour tout
- ⏱️ Suivi du temps d'exécution
- 📊 Résumé détaillé à la fin
- ❌ Gestion des erreurs
- 🛑 Arrêt automatique en cas d'échec

---

## 👁️ Scripts de Visualisation

### `app.py` - Application Web Streamlit

**Interface web interactive** pour visualiser les prédictions de grippe.

#### Fonctionnalités
- 🗺️ **Carte de France** avec FLURISK par région
- 📋 **Top 10 priorités** des régions à risque + export CSV
- 🔍 **Zoom département** avec prédictions J+7, J+14, J+21, J+28
- 🎛️ **Simulation ROI** des campagnes de vaccination

#### Lancement
```bash
streamlit run app.py
```
**URL** : http://localhost:8501

#### Prérequis
- Dataset avec prédictions : `data/processed/dataset_with_predictions_*.csv`
- Modèles entraînés : `models/rf_grippe_*.pkl`

---

### `demo.py` - Script de Vérification

**Script terminal** qui affiche un résumé du système.

#### Affiche
- ✅ État des données collectées
- 📊 Statistiques du dataset
- 🚨 FLURISK actuel par région (Top 5)
- 🤖 Performance des modèles (MAE, R²)
- 🌐 Statut de l'application Streamlit
- 🚀 Prochaines étapes suggérées

#### Lancement
```bash
python demo.py
```

#### Utilisation
Idéal pour vérifier rapidement que tout fonctionne avant une démonstration.

---

## 📖 Documentation Complète

Pour plus de détails sur la visualisation, consultez **`docs/VISUALISATION.md`**.
