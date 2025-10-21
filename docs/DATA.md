# 📊 Données - Collecte et traitement

Ce document explique où se trouvent les données, comment elles sont collectées, traitées et utilisées dans LUMEN.

## 📁 Structure des données

```
data/
├── spf/                    # Santé Publique France
│   ├── sentinelles_*.csv
│   ├── urgences_*.csv
│   └── vaccination_*.csv
├── insee/                  # Données démographiques
│   └── insee_*.csv
├── meteo/                  # Données météorologiques
│   └── meteo_*.csv
├── wikipedia/              # Pages vues Wikipedia
│   └── wikipedia_*.csv
├── google_trends/          # Tendances de recherche
│   └── trends_*.csv
├── processed/              # Données fusionnées
│   └── dataset_with_alerts_*.csv
├── alerts/                 # Alertes générées
│   ├── alertes_*.csv
│   └── protocoles_*.csv
└── collection_config.json  # Configuration de collecte
```

**Note :** Tous les fichiers CSV utilisent un timestamp `YYYYMMDD_HHMMSS` pour versionning.

## 🔄 Pipeline de données

### Vue d'ensemble

```
1. COLLECTE              2. FUSION              3. ALERTES              4. VISUALISATION
   ↓                         ↓                      ↓                       ↓
generate_demo_data.py → dataset_with_alerts → alertes + protocoles → app_complete.py
   ↓                         ↓                      ↓                       ↓
data/[sources]/          data/processed/       data/alerts/            Interface web
```

## 1️⃣ Collecte des données

### Script : `scripts/generate_demo_data.py`

**Ce qu'il fait :**
- Génère des données de démonstration basées sur des patterns réalistes
- Simule les variations saisonnières (pic hivernal)
- Crée des données cohérentes pour les 13 régions françaises

**Commande :**
```bash
venv/bin/python scripts/generate_demo_data.py
```

**Sortie :**
```
✅ Données de démonstration générées :
   📊 Dataset: data/processed/dataset_with_alerts_20251021_104801.csv
   🚨 Alertes: data/alerts/alertes_20251021_104801.csv
   📋 Protocoles: data/alerts/protocoles_20251021_104801.csv
   ⚙️  Configuration: models/config_20251021_104801.json
```

### Données générées

#### Structure du dataset principal

```csv
date,region,urgences_grippe,vaccination_2024,ias_syndrome_grippal,population_totale,pct_65_plus,alert_score,flurisk,pred_urgences_grippe_j7,pred_urgences_grippe_j14,pred_urgences_grippe_j21,pred_urgences_grippe_j28
2024-10-21,Île-de-France,125,67.5,2.3,12000000,18.5,42.3,42.3,138,150,163,175
```

**Colonnes principales :**
- `date` : Date de l'observation (YYYY-MM-DD)
- `region` : Nom de la région française
- `urgences_grippe` : Nombre de passages aux urgences pour grippe
- `vaccination_2024` : Taux de vaccination (0-100%)
- `ias_syndrome_grippal` : Indicateur d'activité syndromique
- `population_totale` : Population de la région
- `pct_65_plus` : Pourcentage de population 65+ ans
- `alert_score` : Score d'alerte calculé (0-100)
- `flurisk` : Alias de alert_score
- `pred_urgences_grippe_j7` : Prédiction à 7 jours
- `pred_urgences_grippe_j14` : Prédiction à 14 jours
- `pred_urgences_grippe_j21` : Prédiction à 21 jours
- `pred_urgences_grippe_j28` : Prédiction à 28 jours

#### Structure des alertes

```csv
region,level,alert_score,action,timeline,urgences_actuelles,vaccination_rate
Île-de-France,ÉLEVÉ,72.5,Préparer campagne,1-2 semaines,85,52.3
```

**Colonnes :**
- `region` : Région concernée
- `level` : Niveau d'alerte (CRITIQUE, ÉLEVÉ, MODÉRÉ, FAIBLE)
- `alert_score` : Score numérique (0-100)
- `action` : Action recommandée
- `timeline` : Délai de mise en œuvre
- `urgences_actuelles` : Nombre d'urgences actuelles
- `vaccination_rate` : Taux de vaccination actuel

#### Structure des protocoles

```csv
region,protocol,estimated_cost,expected_roi,timeline
Île-de-France,Campagne de vaccination ciblée - Île-de-France,125000,3.5,1-2 semaines
```

**Colonnes :**
- `region` : Région concernée
- `protocol` : Description du protocole
- `estimated_cost` : Coût estimé (€)
- `expected_roi` : Retour sur investissement attendu
- `timeline` : Délai de mise en œuvre

## 2️⃣ Fusion des données (pipeline complet)

### Architecture complète (si utilisation de vraies données)

Pour utiliser de vraies données au lieu des données de démonstration :

#### Étape 1 : Collecte

**Script :** `scripts/collect_real_data_fixed.py`

```bash
venv/bin/python scripts/collect_real_data_fixed.py
```

**Actions :**
- Collecte ou simule les données SPF (sentinelles, urgences, vaccination)
- Collecte les données INSEE (population)
- Collecte les données météo (Open-Meteo API)
- Génère `collection_config.json` avec la liste des fichiers

**Fichiers créés :**
```
data/spf/sentinelles_real_YYYYMMDD_HHMMSS.csv
data/spf/urgences_real_YYYYMMDD_HHMMSS.csv
data/spf/vaccination_real_YYYYMMDD_HHMMSS.csv
data/insee/insee_real_YYYYMMDD_HHMMSS.csv
data/meteo/meteo_real_YYYYMMDD_HHMMSS.csv
```

#### Étape 2 : Fusion

**Script :** `scripts/fuse_data.py`

```bash
venv/bin/python scripts/fuse_data.py
```

**Actions :**
- Lit le dernier fichier de chaque source
- Fusionne sur les clés `region` + `date`
- Calcule des features dérivées
- Sauvegarde le dataset unifié

**Fichier créé :**
```
data/processed/dataset_fused_YYYYMMDD_HHMMSS.csv
```

#### Étape 3 : Génération d'alertes

**Script :** `scripts/create_alert_system.py`

```bash
venv/bin/python scripts/create_alert_system.py
```

**Actions :**
- Lit le dataset fusionné
- Calcule les scores d'alerte par région
- Génère les protocoles d'action recommandés
- Sauvegarde alertes et protocoles

**Fichiers créés :**
```
data/alerts/alertes_YYYYMMDD_HHMMSS.csv
data/alerts/protocoles_YYYYMMDD_HHMMSS.csv
data/processed/dataset_with_alerts_YYYYMMDD_HHMMSS.csv
```

## 3️⃣ Utilisation par l'application

### Chargement des données

**Fichier :** `app_complete.py`

```python
# L'application charge toujours le fichier le plus récent
alert_files = [f for f in os.listdir('data/processed')
               if f.startswith('dataset_with_alerts_')]
if alert_files:
    latest_file = sorted(alert_files)[-1]
    self.data = pd.read_csv(f'data/processed/{latest_file}')
```

**Pattern de nommage :**
- Le tri lexicographique des fichiers avec timestamp donne automatiquement le plus récent
- Format : `dataset_with_alerts_20251021_104801.csv`
- Tri : `20251021_104801` > `20251020_153000` ✅

### Mise en cache

L'application utilise le cache Streamlit pour optimiser les performances :

```python
@st.cache_data
def load_data():
    return pd.read_csv('data/processed/dataset_with_alerts_latest.csv')
```

## 🔧 Configuration de collecte

### Fichier : `data/collection_config.json`

```json
{
  "collection_date": "2025-10-21T10:31:50.763370",
  "files": [
    "data/spf/sentinelles_real_20251021_103150.csv",
    "data/spf/urgences_real_20251021_103150.csv",
    "data/spf/vaccination_real_20251021_103150.csv",
    "data/insee/insee_real_20251021_103150.csv",
    "data/meteo/meteo_real_20251021_103150.csv"
  ],
  "sources": [
    "Santé Publique France",
    "INSEE",
    "Météo France"
  ],
  "data_type": "real_based",
  "description": "Données générées basées sur les patterns réels des sources officielles"
}
```

**Utilité :**
- Traçabilité des données collectées
- Liste des fichiers sources utilisés
- Date de dernière collecte
- Type de données (demo, real, real_based)

## 📈 Calcul du score d'alerte

### Algorithme

```python
alert_score = min(100, max(0,
    (100 - vaccination) * 0.4 +      # 40% : Faible vaccination
    (urgences / 100) * 0.3 +          # 30% : Urgences élevées
    (ias * 10) * 0.3                  # 30% : IAS élevé
))
```

**Pondération :**
- Vaccination : 40% (inversement proportionnel)
- Urgences : 30% (directement proportionnel)
- IAS : 30% (directement proportionnel)

### Niveaux d'alerte

| Score | Niveau | Couleur | Action |
|-------|--------|---------|--------|
| 0-40 | FAIBLE | 🟢 Vert | Surveillance normale |
| 40-60 | MODÉRÉ | 🟡 Jaune | Préparation |
| 60-80 | ÉLEVÉ | 🟠 Orange | Campagne ciblée |
| 80-100 | CRITIQUE | 🔴 Rouge | Action immédiate |

## 🔄 Mise à jour des données

### Manuelle

```bash
# Régénérer les données de démonstration
venv/bin/python scripts/generate_demo_data.py

# Relancer l'application (elle chargera automatiquement les nouvelles données)
venv/bin/python launch_app.py
```

### Automatique (avec cron)

**Linux/Mac :**
```bash
# Éditer la crontab
crontab -e

# Ajouter (tous les lundis à 8h)
0 8 * * 1 cd /path/to/t-hack-700 && venv/bin/python scripts/generate_demo_data.py
```

**Windows (Planificateur de tâches) :**
1. Ouvrir le Planificateur de tâches
2. Créer une tâche basique
3. Déclencheur : Hebdomadaire, lundi 8h
4. Action : Lancer `C:\path\to\venv\Scripts\python.exe scripts\generate_demo_data.py`

## 🗄️ Nettoyage des anciennes données

### Script de nettoyage

Créer `scripts/cleanup_old_data.py` :

```python
import os
from datetime import datetime, timedelta

def cleanup_old_files(directory, days=30):
    """Supprime les fichiers plus vieux que X jours"""
    cutoff = datetime.now() - timedelta(days=days)

    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)
        if os.path.isfile(filepath):
            file_time = datetime.fromtimestamp(os.path.getmtime(filepath))
            if file_time < cutoff:
                os.remove(filepath)
                print(f"Supprimé: {filename}")

# Nettoyer les données de plus de 30 jours
cleanup_old_files('data/processed', days=30)
cleanup_old_files('data/alerts', days=30)
```

### Lancer le nettoyage

```bash
venv/bin/python scripts/cleanup_old_data.py
```

## 📊 Format et encodage

### Spécifications

- **Format** : CSV (Comma-Separated Values)
- **Encodage** : UTF-8
- **Séparateur** : `,` (virgule)
- **Décimales** : `.` (point)
- **Dates** : ISO 8601 (YYYY-MM-DD)
- **Header** : Première ligne (noms de colonnes)

### Exemple de lecture

```python
import pandas as pd

# Lecture standard
df = pd.read_csv('data/processed/dataset_with_alerts_latest.csv')

# Lecture avec options
df = pd.read_csv(
    'data/processed/dataset_with_alerts_latest.csv',
    encoding='utf-8',
    parse_dates=['date'],
    index_col='date'
)
```

## 🔍 Validation des données

### Checks effectués

1. **Complétude** : Toutes les régions présentes
2. **Cohérence** : Valeurs dans les plages attendues
3. **Continuité** : Pas de trous dans les dates
4. **Format** : Types de données corrects

### Script de validation

```python
def validate_data(df):
    # Vérifier les régions
    expected_regions = 13
    assert df['region'].nunique() == expected_regions

    # Vérifier les plages de valeurs
    assert (df['vaccination_2024'] >= 0).all()
    assert (df['vaccination_2024'] <= 100).all()
    assert (df['alert_score'] >= 0).all()
    assert (df['alert_score'] <= 100).all()

    print("✅ Données valides")
```

## 📚 Références

- **Données de démonstration** : `scripts/generate_demo_data.py`
- **Pipeline complet** : Voir [INSTALL.md](INSTALL.md)
- **Sources de données** : Voir [SOURCES.md](SOURCES.md)
- **Structure projet** : Voir [STRUCTURE.md](STRUCTURE.md)
