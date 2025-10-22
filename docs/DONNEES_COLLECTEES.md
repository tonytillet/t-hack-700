# 📊 LUMEN - Données Collectées et Utilisées

## 🎯 Vue d'ensemble

Ce document décrit **toutes les données collectées et utilisées** dans le projet LUMEN pour prédire les risques de grippe en France.

---

## 📁 Structure des Données

```
data/
├── raw/                    # Données brutes (vide - nettoyées après collecte)
├── validated/              # Données validées (75 fichiers parquet)
└── processed/              # Dataset final pour ML
    └── dataset.parquet     # Dataset consolidé avec features (169 KB)
```

---

## 🔍 Analyse du Dataset Principal

**Fichier** : `data/processed/dataset.parquet`

Pour analyser le contenu, exécutez :

```python
import pandas as pd

# Charger le dataset
df = pd.read_parquet('data/processed/dataset.parquet')

# Informations générales
print(f"📊 Lignes: {len(df):,}")
print(f"📋 Colonnes: {len(df.columns)}")
print(f"\n🔑 Colonnes disponibles:")
for col in df.columns:
    print(f"   • {col}")

# Aperçu des données
print(f"\n👀 Aperçu:")
print(df.head())

# Statistiques
print(f"\n📈 Statistiques:")
print(df.describe())
```

---

## 🏥 Sources de Données

### 1. **Santé Publique France (SPF)** 🏥

**Source officielle** : [data.gouv.fr](https://data.gouv.fr)

**Données collectées** :
- 📊 **Passages aux urgences** pour syndrome grippal
- 🏥 **Consultations SOS Médecins** pour grippe
- 📈 **Nombre d'actes médicaux** liés à la grippe
- 📅 **Données hebdomadaires** par département/région
- 🔢 **Taux d'incidence** (pour 100,000 habitants)

**Indicateurs clés** :
- `passages_urgences` : Nombre de passages aux urgences
- `consultations_sos` : Consultations SOS Médecins
- `actes_grippe` : Actes médicaux pour grippe
- `taux_incidence` : Taux d'incidence pour 100k hab
- `syndrome_grippal` : Cas de syndrome grippal

**Volume** : ~4,317 enregistrements

---

### 2. **Météo France** 🌡️

**Source officielle** : [Météo France Open Data](https://donneespubliques.meteofrance.fr/)

**Données collectées** :
- 🌡️ **Température** (moyenne, min, max)
- 💧 **Humidité relative** (%)
- 🌧️ **Précipitations** (mm)
- 💨 **Vitesse du vent** (km/h)
- ☁️ **Nébulosité** (couverture nuageuse)
- 🌡️ **Température ressentie**

**Indicateurs clés** :
- `temperature_moyenne` : Température moyenne (°C)
- `temperature_min` : Température minimale (°C)
- `temperature_max` : Température maximale (°C)
- `humidite` : Humidité relative (%)
- `precipitation` : Précipitations (mm)
- `vent_vitesse` : Vitesse du vent (km/h)

**Granularité** : Données quotidiennes agrégées en hebdomadaire

**Volume** : ~3,939 enregistrements météorologiques

---

### 3. **INSEE** 👥

**Source officielle** : [INSEE - Institut National de la Statistique](https://www.insee.fr)

**Données collectées** :
- 👥 **Population totale** par département/région
- 📊 **Densité de population** (hab/km²)
- 👴 **Répartition par âge** (notamment +65 ans)
- 🏙️ **Taux d'urbanisation**
- 🌾 **Taux de ruralité**
- 📍 **Codes géographiques** (département, région)

**Indicateurs clés** :
- `population` : Population totale
- `densite` : Densité de population (hab/km²)
- `pop_65_plus` : Population de 65 ans et plus
- `taux_urbanisation` : Taux d'urbanisation (%)
- `code_departement` : Code département (01-95)
- `code_region` : Code région (01-13)

**Couverture** : 13 régions françaises

---

### 4. **Google Trends** 🔍 (Optionnel)

**Source** : Google Trends API

**Données collectées** :
- 🔍 **Volume de recherches** pour "grippe"
- 📈 **Tendances** de recherche par région
- 🗓️ **Évolution temporelle** des recherches

**Indicateurs clés** :
- `google_trends_grippe` : Volume de recherches "grippe"
- `google_trends_symptomes` : Recherches symptômes grippaux

**Note** : Données complémentaires, non essentielles au modèle

---

## 🔗 Features Créées (Feature Engineering)

À partir des données brutes, le système crée des **features supplémentaires** pour améliorer les prédictions :

### 1. **Features Temporelles** 📅
- `jour_semaine` : Jour de la semaine (0-6)
- `mois` : Mois de l'année (1-12)
- `trimestre` : Trimestre (1-4)
- `semaine_annee` : Numéro de semaine (1-52)

### 2. **Features de Lag (Retard)** ⏮️
- `passages_urgences_lag1` : Valeur de la semaine précédente
- `passages_urgences_lag2` : Valeur d'il y a 2 semaines
- `passages_urgences_lag3` : Valeur d'il y a 3 semaines
- `passages_urgences_lag4` : Valeur d'il y a 4 semaines

### 3. **Moyennes Mobiles** 📊
- `passages_urgences_ma3` : Moyenne mobile sur 3 semaines
- `passages_urgences_ma7` : Moyenne mobile sur 7 semaines
- `temperature_ma3` : Moyenne mobile température sur 3 semaines

### 4. **Features de Saisonnalité** 🌍
- `sin_semaine` : Composante sinusoïdale (Fourier)
- `cos_semaine` : Composante cosinusoïdale (Fourier)
- `saison` : Saison (hiver, printemps, été, automne)

### 5. **Features d'Interaction** 🔗
- `temp_humidite` : Température × Humidité
- `densite_pop_65` : Densité × Population +65 ans
- `urbanisation_incidence` : Urbanisation × Taux d'incidence

### 6. **Features Dérivées** 📈
- `diff_passages` : Différence avec semaine précédente
- `taux_croissance` : Taux de croissance hebdomadaire
- `variation_temperature` : Variation de température

---

## 📊 Dataset Final

### Caractéristiques

| Propriété | Valeur |
|-----------|--------|
| **Fichier** | `data/processed/dataset.parquet` |
| **Taille** | ~169 KB |
| **Format** | Parquet (optimisé) |
| **Lignes** | ~4,200 (à vérifier) |
| **Colonnes** | ~25-30 features |
| **Période** | 2017-2024 (7 ans) |
| **Granularité** | Hebdomadaire |
| **Couverture** | France entière (13 régions) |

### Structure Typique

```
date | code_dept | code_region | passages_urgences | temperature | humidite | population | ... | flurisk_score
-----|-----------|-------------|-------------------|-------------|----------|------------|-----|---------------
2024 |    75     |     11      |       1250        |    12.5     |   75     |  2,187,526 | ... |     45.2
```

---

## 🔄 Pipeline de Traitement

```
1. COLLECTE (data.gouv.fr, Météo France, INSEE)
   ↓
2. NETTOYAGE (suppression doublons, valeurs manquantes)
   ↓ data/validated/ (75 fichiers parquet)
3. VALIDATION (vérification types, plages de valeurs)
   ↓
4. FEATURE ENGINEERING (lags, moyennes mobiles, saisonnalité)
   ↓
5. CONSOLIDATION
   ↓ data/processed/dataset.parquet
6. ENTRAÎNEMENT ML (Random Forest)
   ↓ models/random_forest_regressor_*.joblib
7. PRÉDICTIONS & DASHBOARDS
```

---

## 📈 Statistiques des Données

### Volume Total
- **75 fichiers** dans `data/validated/`
- **Taille totale** : ~50 MB (données validées)
- **Dataset final** : 169 KB (optimisé)

### Couverture Géographique
- **13 régions** françaises
- **101 départements** (métropole + DOM-TOM)
- **Données nationales** agrégées

### Couverture Temporelle
- **Période** : 2017-2024 (7 ans)
- **Granularité** : Hebdomadaire
- **Fréquence de mise à jour** : Hebdomadaire (automatique)

---

## 🎯 Utilisation dans le Modèle ML

### Features Principales (Top 10)

Les 10 features les plus importantes pour le modèle Random Forest :

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

### Target (Variable à Prédire)

- **`flurisk_score`** : Score de risque de grippe (0-100)
  - Calculé à partir des passages aux urgences, consultations SOS Médecins, et taux d'incidence
  - Normalisé sur une échelle de 0 à 100
  - Utilisé pour générer les alertes (VERT, JAUNE, ORANGE, ROUGE)

---

## 🔍 Comment Explorer les Données

### Méthode 1 : Python

```python
import pandas as pd

# Charger le dataset
df = pd.read_parquet('data/processed/dataset.parquet')

# Explorer
print(df.info())
print(df.describe())
print(df.head(10))

# Colonnes disponibles
print(df.columns.tolist())
```

### Méthode 2 : Jupyter Notebook

```bash
jupyter notebook
# Ouvrir un nouveau notebook et charger le dataset
```

### Méthode 3 : Script d'Analyse

Créer un script `explore_data.py` :

```python
import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_parquet('data/processed/dataset.parquet')

# Statistiques
print(df.describe())

# Visualisations
df['flurisk_score'].hist(bins=50)
plt.title('Distribution du Score de Risque')
plt.show()
```

---

## ✅ Garanties de Qualité

### Traçabilité
- ✅ **100% données officielles** françaises
- ✅ **Sources vérifiables** (data.gouv.fr, Météo France, INSEE)
- ✅ **Checksums SHA256** pour intégrité
- ✅ **Versioning Git** complet

### Validation
- ✅ **Validation stricte** avec Pandera
- ✅ **Vérification des types** de données
- ✅ **Détection des anomalies**
- ✅ **Gestion des valeurs manquantes**

### Mise à Jour
- ✅ **Collecte automatique** hebdomadaire
- ✅ **Pipeline de nettoyage** automatisé
- ✅ **Ré-entraînement** du modèle automatique
- ✅ **Monitoring** de la qualité des données

---

## 📞 Pour Aller Plus Loin

### Consulter les Données

```bash
# Voir le dataset
python3 -c "import pandas as pd; print(pd.read_parquet('data/processed/dataset.parquet').info())"

# Statistiques
python3 -c "import pandas as pd; print(pd.read_parquet('data/processed/dataset.parquet').describe())"

# Colonnes
python3 -c "import pandas as pd; print(pd.read_parquet('data/processed/dataset.parquet').columns.tolist())"
```

### Documentation Complémentaire

- **[Pipeline ML](PIPELINE_ML.md)** : Pipeline complet de traitement
- **[Scripts](SCRIPTS.md)** : Documentation des scripts de collecte
- **[README Principal](../README.md)** : Vue d'ensemble du projet

---

**🧠 LUMEN Enhanced - Données Officielles Françaises**

*Transparence • Traçabilité • Qualité*
