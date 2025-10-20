# 👁️ Visualisation des Résultats

## 📊 Deux outils de visualisation

Le projet propose **deux outils** pour visualiser les résultats de la prédiction grippe :

1. **`app.py`** - Application web interactive (Streamlit)
2. **`demo.py`** - Script de vérification rapide (Terminal)

---

## 🌐 Application Web - `app.py`

### Description

**Interface web interactive** construite avec Streamlit pour visualiser et explorer les prédictions de grippe en France.

### Fonctionnalités

#### 1. 🗺️ Carte de France Interactive
- Visualisation géographique du FLURISK par région
- Code couleur selon le niveau de risque :
  - 🟢 Vert : Risque faible (0-50)
  - 🟠 Orange : Risque moyen (50-70)
  - 🔴 Rouge : Risque élevé (70-100)
- Survol pour voir les détails de chaque région

#### 2. 📋 Top 10 Priorités
- Liste des 10 régions à risque le plus élevé
- Tri par FLURISK décroissant
- Affichage des métriques clés :
  - FLURISK actuel
  - Prédictions J+7, J+14, J+21, J+28
  - Taux de vaccination
  - Passages aux urgences
- **Export CSV** pour analyse externe

#### 3. 🔍 Zoom Département
- Sélection d'une région spécifique
- Graphiques d'évolution temporelle :
  - FLURISK historique
  - Passages aux urgences
  - Prédictions futures
- Comparaison avec la moyenne nationale
- Statistiques détaillées

#### 4. 🎛️ Simulation ROI
- Simulation de l'impact d'une campagne de vaccination
- Paramètres ajustables :
  - Augmentation du taux de vaccination
  - Coût par dose
  - Coût d'une hospitalisation évitée
- Calcul du ROI (Return On Investment)
- Estimation des hospitalisations évitées

### Lancement

```bash
# Depuis la racine du projet
streamlit run app.py

# Ou avec un port spécifique
streamlit run app.py --server.port 8501
```

### Accès

Une fois lancé, ouvrir dans le navigateur :
```
http://localhost:8501
```

### Prérequis

L'application nécessite :
- ✅ Dataset avec prédictions : `data/processed/dataset_with_predictions_*.csv`
- ✅ Modèles entraînés : `models/rf_grippe_*.pkl`
- ✅ Configuration : `models/config_*.json`

Si ces fichiers n'existent pas, lancer d'abord :
```bash
cd scripts
python collect_all_data.py
python fuse_data.py
python train_model.py
```

### Dépendances

```bash
pip install streamlit plotly folium streamlit-folium
```

### Captures d'écran

#### Vue Carte
```
┌─────────────────────────────────────────────────────────┐
│  🔮 Prédiction Grippe France                            │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  [Carte de France interactive]                           │
│                                                           │
│  Île-de-France: 🔴 68.5                                  │
│  Hauts-de-France: 🟠 62.3                                │
│  Grand Est: 🟠 58.7                                      │
│                                                           │
└─────────────────────────────────────────────────────────┘
```

#### Vue Top 10
```
┌─────────────────────────────────────────────────────────┐
│  📋 Top 10 Régions Prioritaires                         │
├─────────────────────────────────────────────────────────┤
│  Région              FLURISK  J+7   J+14  J+21  J+28    │
│  1. Île-de-France      68.5  1200  1350  1450  1500    │
│  2. Hauts-de-France    62.3   890   950  1020  1080    │
│  3. Grand Est          58.7   780   820   880   920    │
│  ...                                                     │
│                                                           │
│  [Bouton Export CSV]                                     │
└─────────────────────────────────────────────────────────┘
```

---

## 🖥️ Script de Démonstration - `demo.py`

### Description

**Script terminal** qui affiche un résumé complet du système de prédiction grippe.

### Fonctionnalités

#### 1. ✅ État des Données Collectées
- Vérification de tous les dossiers de données
- Comptage des fichiers CSV par source
- Statut de chaque collecteur

#### 2. 📊 Statistiques du Dataset
- Période couverte (dates min/max)
- Nombre de régions
- Nombre d'enregistrements
- Nombre de variables

#### 3. 🚨 FLURISK Actuel
- Top 5 des régions à risque élevé
- FLURISK de la dernière semaine
- Prédictions J+28
- Taux de vaccination

#### 4. 🤖 Performance des Modèles
- Liste des modèles entraînés
- Métriques pour chaque horizon :
  - MAE (Mean Absolute Error)
  - R² (Coefficient de détermination)

#### 5. 🌐 Statut Application Streamlit
- Vérification si l'application tourne
- URL d'accès
- Instructions de lancement

#### 6. 🚀 Prochaines Étapes
- Suggestions d'améliorations
- Pistes de développement

### Lancement

```bash
# Depuis la racine du projet
python demo.py
```

### Exemple de Sortie

```
🔮 SYSTÈME DE PRÉDICTION GRIPPE FRANCE
============================================================

📊 ÉTAT DES DONNÉES COLLECTÉES:
----------------------------------------
  ✅ google_trends: 1 fichier(s)
  ✅ wikipedia: 2 fichier(s)
  ✅ spf: 4 fichier(s)
  ✅ context: 2 fichier(s)
  ✅ processed: 2 fichier(s)

📈 Total: 11 fichiers de données

🎯 DATASET PRINCIPAL: dataset_grippe_20251020_163607.csv
----------------------------------------
  📅 Période: 2023-01-02 à 2025-12-30
  🌍 Régions: 13
  📊 Enregistrements: 2,028
  🔧 Variables: 45

🚨 FLURISK ACTUEL (semaine du 2025-12-30):
----------------------------------------
  🔴 Île-de-France: FLURISK 68.5 | Urgences J+28: 1250 | Vaccination: 58.3%
  🟠 Hauts-de-France: FLURISK 62.3 | Urgences J+28: 890 | Vaccination: 52.1%
  🟠 Grand Est: FLURISK 58.7 | Urgences J+28: 780 | Vaccination: 55.4%
  🟠 Auvergne-Rhône-Alpes: FLURISK 54.2 | Urgences J+28: 720 | Vaccination: 60.2%
  🟠 Provence-Alpes-Côte d'Azur: FLURISK 51.8 | Urgences J+28: 680 | Vaccination: 57.8%

🤖 PERFORMANCE DU MODÈLE RANDOM FOREST:
----------------------------------------
  ✅ 4 modèles entraînés
  📊 Métriques disponibles:
    - j7: MAE 85.3, R² 0.892
    - j14: MAE 102.1, R² 0.856
    - j21: MAE 118.5, R² 0.823
    - j28: MAE 135.2, R² 0.791

🌐 APPLICATION STREAMLIT:
----------------------------------------
  ❌ Application non accessible
  💡 Pour lancer: python3 -m streamlit run app.py --server.port 8501

🚀 PROCHAINES ÉTAPES POSSIBLES:
----------------------------------------
  1. 📊 Collecter de vraies données SPF (urgences, vaccination)
  2. 🔄 Améliorer la collecte Google Trends (proxies, délais)
  3. 🎯 Optimiser les hyperparamètres du modèle
  4. 📱 Ajouter des alertes automatiques
  5. 🌐 Déployer en production
  6. 📈 Ajouter plus de sources de données (Twitter, etc.)

============================================================
🎉 SYSTÈME OPÉRATIONNEL - Prêt pour la démonstration !
============================================================
```

### Prérequis

Le script nécessite :
- ✅ Données collectées dans `data/`
- ✅ Dataset traité dans `data/processed/`
- ✅ Modèles dans `models/` (optionnel)

### Utilisation

Idéal pour :
- ✅ Vérifier rapidement que tout fonctionne
- ✅ Voir un résumé du système avant une démo
- ✅ Débugger si quelque chose ne va pas
- ✅ Vérifier les performances des modèles

---

## 📊 Comparaison

| Aspect | **`demo.py`** | **`app.py`** |
|--------|---------------|--------------|
| **Type** | Script terminal | Application web |
| **Interface** | Texte | Graphique interactive |
| **Interactivité** | ❌ Non | ✅ Oui |
| **Graphiques** | ❌ Non | ✅ Oui (Plotly, Folium) |
| **Export** | ❌ Non | ✅ Oui (CSV) |
| **Carte France** | ❌ Non | ✅ Oui |
| **Simulation ROI** | ❌ Non | ✅ Oui |
| **Rapidité** | ⚡ Instantané | 🐢 Quelques secondes |
| **Usage** | Vérification rapide | Exploration complète |
| **Lancement** | `python demo.py` | `streamlit run app.py` |
| **Sortie** | Terminal | Navigateur (localhost:8501) |

---

## 🎯 Quand utiliser quoi ?

### Utiliser `demo.py` quand :
- ✅ Vous voulez vérifier rapidement que tout fonctionne
- ✅ Vous voulez voir un résumé avant une présentation
- ✅ Vous débuggez un problème
- ✅ Vous n'avez pas besoin de graphiques

### Utiliser `app.py` quand :
- ✅ Vous voulez explorer les données en détail
- ✅ Vous faites une démonstration/présentation
- ✅ Vous voulez voir des graphiques et cartes
- ✅ Vous voulez exporter des données
- ✅ Vous voulez simuler des scénarios

---

## 🚀 Workflow Recommandé

### 1. Après avoir lancé la pipeline

```bash
# Lancer la pipeline complète
cd scripts
python collect_all_data.py
python fuse_data.py
python train_model.py

# Vérification rapide
cd ..
python demo.py
```

### 2. Pour explorer les résultats

```bash
# Lancer l'application web
streamlit run app.py
```

### 3. Pour une présentation

```bash
# 1. Vérifier avec demo.py
python demo.py

# 2. Si tout est OK, lancer l'app
streamlit run app.py

# 3. Ouvrir http://localhost:8501 dans le navigateur
```

---

## 📝 Résumé

✅ **`app.py`** = Interface web complète avec visualisations interactives  
✅ **`demo.py`** = Script de vérification rapide en terminal  
✅ Les deux utilisent les **mêmes données** (dataset avec FLURISK et prédictions)  
✅ **`app.py`** est l'outil principal pour présenter le projet  
✅ **`demo.py`** est pratique pour vérifier rapidement le système  

**Utilisez `demo.py` pour vérifier, `app.py` pour explorer !** 🎉
