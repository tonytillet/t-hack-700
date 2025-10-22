# 🤖 LUMEN - Pipeline Machine Learning Complet

## 📋 Table des Matières
- [Vue d'ensemble du Pipeline](#vue-densemble-du-pipeline)
- [Pipeline Complet Étape par Étape](#pipeline-complet-étape-par-étape)
- [Ordre d'Exécution des Scripts](#ordre-dexécution-des-scripts)
- [Commandes Makefile](#commandes-makefile)
- [Flux de Données](#flux-de-données)
- [Exemples Pratiques](#exemples-pratiques)

---

## 🎯 Vue d'ensemble du Pipeline

Le pipeline LUMEN suit un processus en **7 étapes** pour transformer les données brutes en prédictions ML :

```
📥 DONNÉES BRUTES
    ↓
🧹 NETTOYAGE (clean_data_controlled.py)
    ↓
✅ VALIDATION (validate_data_strict.py)
    ↓
🔄 FUSION & FEATURES (generate_meaningful_data.py)
    ↓
🤖 ENTRAÎNEMENT ML (ml/train_random_forest.py)
    ↓
📊 GÉNÉRATION DASHBOARDS (dashboard_integration.py)
    ↓
🔍 EXPLICABILITÉ (explicabilite_shap.py)
    ↓
🌐 SERVEUR (serveur_simple.py)
```

---

## 📊 Pipeline Complet Étape par Étape

### 🔹 Étape 0 : Préparation (Optionnel)

**Script** : Aucun (données déjà présentes)

**Objectif** : Avoir des données brutes dans `data/raw/`

**Données sources** :
- Santé Publique France (SPF) : Données épidémiologiques
- Météo France : Données météorologiques
- INSEE : Données démographiques
- Data.gouv.fr : Données ouvertes

**Commande** :
```bash
# Vérifier les données brutes
ls -la data/raw/
```

**Résultat attendu** :
```
data/raw/
├── spf_data.csv              (données SPF)
├── meteo_data.csv            (données météo)
├── insee_data.csv            (données INSEE)
└── data.gouv.fr_*.json       (données data.gouv.fr)
```

---

### 🔹 Étape 1 : Nettoyage des Données

**Script** : `clean_data_controlled.py`

**Objectif** : Nettoyer et standardiser les données brutes

**Processus** :
1. 📂 Lecture des données brutes depuis `data/raw/`
2. 🧹 Nettoyage avec **Dataprep** :
   - Suppression des doublons
   - Gestion des valeurs manquantes
   - Normalisation des formats
   - Harmonisation des libellés
3. 🔐 Calcul des checksums SHA256
4. 📋 Génération d'un rapport de nettoyage
5. 💾 Sauvegarde dans `data/cleaned/`

**Commande** :
```bash
# Méthode 1 : Direct
python3 clean_data_controlled.py

# Méthode 2 : Makefile
make clean-validate
```

**Durée** : ~30-60 secondes

**Fichiers générés** :
```
data/cleaned/
├── spf_data_cleaned.csv
├── meteo_data_cleaned.csv
├── insee_data_cleaned.csv
└── cleaning_report_YYYYMMDD_HHMMSS.json
```

**Sortie attendue** :
```
🧹 NETTOYAGE CONTRÔLÉ DES DONNÉES
==================================
📂 Lecture des données brutes...
✅ 4 fichiers trouvés

🧹 Nettoyage en cours...
  • spf_data.csv: 4,317 lignes → 4,200 lignes (117 doublons supprimés)
  • meteo_data.csv: 3,939 lignes → 3,900 lignes (39 doublons supprimés)
  • insee_data.csv: 13 lignes → 13 lignes (0 doublons)

🔐 Calcul des checksums SHA256...
✅ Checksums calculés

📋 Rapport de nettoyage généré
💾 Données sauvegardées dans data/cleaned/

✅ NETTOYAGE TERMINÉ
```

---

### 🔹 Étape 2 : Validation des Données

**Script** : `validate_data_strict.py`

**Objectif** : Valider strictement les données nettoyées avec **Pandera**

**Processus** :
1. 📂 Lecture des données nettoyées depuis `data/cleaned/`
2. ✅ Validation avec **Pandera** :
   - Vérification des types de données
   - Vérification des plages de valeurs
   - Vérification de la cohérence temporelle
   - Détection des anomalies
3. 📊 Génération de statistiques
4. 📋 Génération d'un rapport de validation
5. 💾 Sauvegarde dans `data/validated/`

**Commande** :
```bash
# Méthode 1 : Direct
python3 validate_data_strict.py

# Méthode 2 : Makefile
make validate-strict
```

**Durée** : ~20-40 secondes

**Fichiers générés** :
```
data/validated/
├── spf_data_validated.parquet
├── meteo_data_validated.parquet
├── insee_data_validated.parquet
└── validation_report_YYYYMMDD_HHMMSS.json
```

**Sortie attendue** :
```
✅ VALIDATION STRICTE DES DONNÉES
==================================
📂 Lecture des données nettoyées...
✅ 3 fichiers trouvés

🔍 Validation en cours...
  • spf_data_cleaned.csv: ✅ VALIDE (4,200 lignes)
  • meteo_data_cleaned.csv: ✅ VALIDE (3,900 lignes)
  • insee_data_cleaned.csv: ✅ VALIDE (13 lignes)

📊 Statistiques:
  • Total lignes validées: 8,113
  • Anomalies détectées: 0
  • Taux de validation: 100%

📋 Rapport de validation généré
💾 Données sauvegardées dans data/validated/

✅ VALIDATION TERMINÉE
```

---

### 🔹 Étape 3 : Fusion et Feature Engineering

**Script** : `generate_meaningful_data.py` (ou fusion automatique)

**Objectif** : Fusionner les données et créer les features pour le ML

**Processus** :
1. 📂 Lecture des données validées depuis `data/validated/`
2. 🔗 Fusion des datasets :
   - SPF + Météo (par date et région)
   - SPF + INSEE (par région)
3. 🛠️ Feature Engineering :
   - **Lags** : 1-4 semaines
   - **Moyennes mobiles** : 3 et 7 semaines
   - **Saisonnalité** : Fourier series (sin/cos)
   - **Features temporelles** : jour, mois, trimestre
   - **Features d'interaction** : température × humidité
4. 💾 Sauvegarde dans `data/processed/`

**Commande** :
```bash
python3 generate_meaningful_data.py
```

**Durée** : ~10-20 secondes

**Fichiers générés** :
```
data/processed/
├── dataset.parquet              (dataset complet)
└── features_description.json    (description des features)
```

**Features créées** (exemple) :
```
- passages_urgences_grippe       (cible)
- passages_urgences_lag1         (lag 1 semaine)
- passages_urgences_lag2         (lag 2 semaines)
- passages_urgences_ma7          (moyenne mobile 7 jours)
- temperature_moyenne
- humidite_moyenne
- taux_incidence
- couverture_vaccinale
- saison_sin                     (saisonnalité)
- saison_cos                     (saisonnalité)
- temp_x_humidite                (interaction)
```

**Sortie attendue** :
```
🔗 FUSION ET FEATURE ENGINEERING
=================================
📂 Lecture des données validées...
✅ 3 datasets trouvés

🔗 Fusion des datasets...
✅ SPF + Météo fusionnés (4,200 lignes)
✅ SPF + INSEE fusionnés (4,200 lignes)

🛠️ Feature Engineering...
✅ Lags créés (1-4 semaines)
✅ Moyennes mobiles créées (3, 7 semaines)
✅ Saisonnalité créée (sin/cos)
✅ Features temporelles créées
✅ Features d'interaction créées

📊 Dataset final:
  • Lignes: 4,200
  • Colonnes: 25 features
  • Taille: 2.5 MB

💾 Dataset sauvegardé dans data/processed/

✅ FUSION TERMINÉE
```

---

### 🔹 Étape 4 : Entraînement du Modèle ML

**Script** : `ml/train_random_forest.py`

**Objectif** : Entraîner le modèle Random Forest pour prédire la grippe

**Processus** :
1. 📂 Lecture du dataset depuis `data/processed/dataset.parquet`
2. 🔀 Split train/test (70/30 chronologique)
3. 🤖 Entraînement du Random Forest :
   - n_estimators=100
   - max_depth=8
   - min_samples_split=10
   - min_samples_leaf=5
4. 📊 Évaluation des performances (R², MAE, RMSE)
5. 📈 Calcul de l'importance des features
6. 💾 Sauvegarde du modèle dans `models/`

**Commande** :
```bash
python3 ml/train_random_forest.py
```

**Durée** : ~1-3 minutes

**Fichiers générés** :
```
models/
├── random_forest_regressor_YYYYMMDD_HHMMSS.joblib  (modèle)
└── ml/artefacts/
    ├── metrics.json                                 (métriques)
    ├── feature_importance.csv                       (importance)
    └── training_report.txt                          (rapport)
```

**Sortie attendue** :
```
🤖 ENTRAÎNEMENT DU MODÈLE RANDOM FOREST
========================================
📂 Chargement des données...
✅ Dataset chargé: 4,200 lignes, 25 features

🔀 Split train/test...
✅ Train: 2,940 lignes (70%)
✅ Test: 1,260 lignes (30%)

🤖 Entraînement en cours...
✅ Modèle entraîné (100 arbres)

📊 PERFORMANCES:
  • R² Score: 0.971 (97.1%)
  • MAE: 5.08
  • RMSE: 8.23

📈 TOP 5 FEATURES:
  1. passages_urgences_lag1 (0.35)
  2. passages_urgences_ma7 (0.22)
  3. temperature_moyenne (0.15)
  4. saison_sin (0.12)
  5. taux_incidence (0.08)

💾 Modèle sauvegardé: models/random_forest_regressor_20251022_115500.joblib

✅ ENTRAÎNEMENT TERMINÉ
```

---

### 🔹 Étape 5 : Génération des Dashboards

**Script** : `dashboard_integration.py`

**Objectif** : Générer les dashboards HTML interactifs avec Plotly

**Processus** :
1. 📂 Chargement du dataset depuis `data/processed/dataset.parquet`
2. 🤖 Chargement du modèle depuis `models/`
3. 🔮 Génération des prédictions
4. 📊 Calcul des niveaux d'alerte (VERT, JAUNE, ORANGE, ROUGE)
5. 🎨 Création des visualisations :
   - Carte des zones à risque
   - Graphiques réel vs prédit
   - Panneau des alertes actives
6. 💾 Sauvegarde des dashboards HTML

**Commande** :
```bash
python3 dashboard_integration.py
```

**Durée** : ~10-30 secondes

**Fichiers générés** :
```
./ (racine)
├── dashboard_risk_heatmap.html           (carte)
├── dashboard_real_vs_predicted.html      (graphiques)
└── dashboard_active_alerts.html          (alertes)
```

**Sortie attendue** :
```
🎯 LUMEN - INTÉGRATION DASHBOARD AVANCÉE
=========================================
📊 CHARGEMENT DES DONNÉES ET DU MODÈLE
✅ Données chargées: 4,200 lignes
✅ Modèle chargé: random_forest_regressor_20251022_115500.joblib

🔮 GÉNÉRATION DES PRÉDICTIONS
✅ Prédictions générées pour 4,200 échantillons
📊 Niveaux d'alerte: {'ROUGE': 150, 'ORANGE': 300, 'JAUNE': 500, 'VERT': 3250}

🎨 CRÉATION DES VISUALISATIONS
✅ Carte des zones à risque sauvegardée
✅ Graphique réel vs prédit sauvegardé
✅ Panneau des alertes actives sauvegardé
📊 7 alertes actives détectées

✅ INTÉGRATION DASHBOARD TERMINÉE
```

---

### 🔹 Étape 6 : Explicabilité SHAP (Optionnel)

**Script** : `explicabilite_shap.py`

**Objectif** : Générer les plots SHAP pour expliquer les prédictions

**Processus** :
1. 📂 Chargement du modèle depuis `models/`
2. 📂 Chargement du dataset de test
3. 🔍 Calcul des valeurs SHAP
4. 📊 Génération de 15 plots :
   - Summary plot
   - Waterfall plot
   - Force plot
   - Dependence plots
   - Feature importance
5. 💾 Sauvegarde dans `explicabilite/`

**Commande** :
```bash
python3 explicabilite_shap.py
```

**Durée** : ~1-2 minutes

**Fichiers générés** :
```
explicabilite/
├── shap_summary_plot.png
├── shap_waterfall_plot.png
├── shap_force_plot.html
├── shap_dependence_*.png (x10)
└── shap_feature_importance.png
```

**Sortie attendue** :
```
🔍 EXPLICABILITÉ SHAP
=====================
📂 Chargement du modèle...
✅ Modèle chargé

📂 Chargement des données de test...
✅ 1,260 échantillons de test

🔍 Calcul des valeurs SHAP...
✅ Valeurs SHAP calculées

📊 Génération des plots...
✅ Summary plot généré
✅ Waterfall plot généré
✅ Force plot généré
✅ Dependence plots générés (10)
✅ Feature importance généré

💾 15 plots sauvegardés dans explicabilite/

✅ EXPLICABILITÉ TERMINÉE
```

---

### 🔹 Étape 7 : Lancement du Serveur

**Script** : `serveur_simple.py`

**Objectif** : Lancer le serveur HTTP pour afficher les dashboards

**Processus** :
1. ✅ Vérification des fichiers HTML
2. 🌐 Démarrage du serveur HTTP sur port 8080
3. 🔄 Redirection automatique vers le dashboard principal
4. 📊 Service des dashboards HTML

**Commande** :
```bash
# Méthode 1 : Direct
python3 serveur_simple.py

# Méthode 2 : Script automatique
./start.sh
```

**Durée** : Instantané

**Sortie attendue** :
```
🌐 LUMEN - SERVEUR UNIFIÉ
========================================
🚀 Port unique: 8080
📊 Dashboard principal: http://localhost:8080/
🗺️ Carte des risques: http://localhost:8080/dashboard_risk_heatmap.html
📈 Prédictions: http://localhost:8080/dashboard_real_vs_predicted.html
🚨 Alertes actives: http://localhost:8080/dashboard_active_alerts.html
========================================
✅ Tous les dashboards sont prêts
🌐 Serveur démarré: http://localhost:8080
🛑 Ctrl+C pour arrêter
```

---

## 🚀 Ordre d'Exécution des Scripts

### 📝 Pipeline Complet Manuel

```bash
# 1. Nettoyage des données
python3 clean_data_controlled.py

# 2. Validation des données
python3 validate_data_strict.py

# 3. Fusion et feature engineering
python3 generate_meaningful_data.py

# 4. Entraînement du modèle ML
python3 ml/train_random_forest.py

# 5. Génération des dashboards
python3 dashboard_integration.py

# 6. Explicabilité SHAP (optionnel)
python3 explicabilite_shap.py

# 7. Lancement du serveur
python3 serveur_simple.py
```

**Durée totale** : ~5-10 minutes

---

### ⚡ Pipeline Complet Automatique (Makefile)

```bash
# Pipeline complet de validation des données
make full-pipeline

# Puis entraînement ML et dashboards
python3 ml/train_random_forest.py
python3 dashboard_integration.py
python3 serveur_simple.py
```

**Durée totale** : ~5-10 minutes

---

### 🎯 Pipeline Rapide (Script start.sh)

```bash
# Lance directement le serveur (suppose que les dashboards existent)
./start.sh
```

**Durée totale** : ~10 secondes

---

## 📊 Commandes Makefile

Le `Makefile` fournit des commandes pratiques pour le pipeline :

### Commandes Principales

```bash
# Afficher l'aide
make help

# Pipeline complet de validation
make full-pipeline
  ↓
  ├── make clean-validate    (nettoyage)
  ├── make validate-strict   (validation)
  ├── make audit-ge          (audit)
  ├── make version-dvc       (versioning)
  └── make evidence-pack     (bundle de preuve)

# Vérifier l'état du pipeline
make status

# Générer un rapport de qualité
make quality-report

# Nettoyer les fichiers temporaires
make clean

# Installer les dépendances
make install-deps

# Tester l'intégrité
make test-integrity
```

### Détail des Commandes

#### `make clean-validate`
```bash
make clean-validate
```
- Exécute `clean_data_controlled.py`
- Nettoie les données brutes
- Génère `data/cleaned/*.csv`

#### `make validate-strict`
```bash
make validate-strict
```
- Exécute `validate_data_strict.py`
- Valide les données nettoyées
- Génère `data/validated/*.parquet`

#### `make full-pipeline`
```bash
make full-pipeline
```
- Exécute toutes les étapes de validation
- Équivalent à :
  ```bash
  make clean-validate
  make validate-strict
  make audit-ge
  make version-dvc
  make evidence-pack
  ```

#### `make status`
```bash
make status
```
- Affiche l'état du pipeline
- Compte les fichiers dans chaque répertoire
- **Sortie** :
  ```
  📊 ÉTAT DU PIPELINE
  ===================
  📁 Données brutes: 4 fichiers
  🧹 Données nettoyées: 3 fichiers
  ✅ Données validées: 3 fichiers
  🧊 Données gelées: 4 fichiers
  📋 Logs: 12 fichiers
  📦 Bundle de preuve: 9 fichiers
  ```

---

## 🔄 Flux de Données

### Structure des Répertoires

```
t-hack-700/
│
├── data/
│   ├── raw/                    # 📥 Données brutes (sources)
│   │   ├── spf_data.csv
│   │   ├── meteo_data.csv
│   │   └── insee_data.csv
│   │
│   ├── frozen/                 # 🧊 Données gelées (snapshots)
│   │   └── 2025-10-21_*.csv
│   │
│   ├── cleaned/                # 🧹 Données nettoyées
│   │   ├── spf_data_cleaned.csv
│   │   └── cleaning_report.json
│   │
│   ├── validated/              # ✅ Données validées
│   │   ├── spf_data_validated.parquet
│   │   └── validation_report.json
│   │
│   └── processed/              # 🔗 Données fusionnées + features
│       └── dataset.parquet
│
├── models/                     # 🤖 Modèles ML entraînés
│   └── random_forest_regressor_*.joblib
│
├── ml/artefacts/               # 📊 Métriques et rapports ML
│   ├── metrics.json
│   └── feature_importance.csv
│
├── explicabilite/              # 🔍 Plots SHAP
│   └── shap_*.png
│
├── evidence/                   # 📦 Bundle de preuve
│   └── *.json
│
└── monitoring/logs/            # 📋 Logs de monitoring
    └── *.log
```

### Flux de Transformation

```
📥 DONNÉES BRUTES (data/raw/)
    ↓ clean_data_controlled.py
🧹 DONNÉES NETTOYÉES (data/cleaned/)
    ↓ validate_data_strict.py
✅ DONNÉES VALIDÉES (data/validated/)
    ↓ generate_meaningful_data.py
🔗 DATASET COMPLET (data/processed/)
    ↓ ml/train_random_forest.py
🤖 MODÈLE ML (models/)
    ↓ dashboard_integration.py
📊 DASHBOARDS HTML (racine)
    ↓ serveur_simple.py
🌐 SERVEUR WEB (http://localhost:8080)
```

---

## 💡 Exemples Pratiques

### Exemple 1 : Premier Lancement Complet

```bash
# 1. Installer les dépendances
pip install -r requirements.txt

# 2. Exécuter le pipeline de validation
make full-pipeline

# 3. Fusionner et créer les features
python3 generate_meaningful_data.py

# 4. Entraîner le modèle
python3 ml/train_random_forest.py

# 5. Générer les dashboards
python3 dashboard_integration.py

# 6. Lancer le serveur
./start.sh
```

---

### Exemple 2 : Ré-entraînement Rapide

```bash
# Si les données sont déjà validées, juste ré-entraîner
python3 ml/train_random_forest.py
python3 dashboard_integration.py
python3 serveur_simple.py
```

---

### Exemple 3 : Ajout de Nouvelles Données

```bash
# 1. Ajouter les nouvelles données dans data/raw/

# 2. Nettoyer les nouvelles données
python3 clean_data_controlled.py

# 3. Valider
python3 validate_data_strict.py

# 4. Fusionner
python3 generate_meaningful_data.py

# 5. Ré-entraîner
python3 ml/train_random_forest.py

# 6. Régénérer les dashboards
python3 dashboard_integration.py
```

---

### Exemple 4 : Monitoring Automatique

```bash
# Configuration du crontab pour monitoring automatique

# Éditer le crontab
crontab -e

# Ajouter ces lignes :
# Monitoring quotidien à 6h00
0 6 * * * cd /path/to/t-hack-700 && bash monitoring/daily_monitoring.sh

# Retrain hebdomadaire tous les dimanches à 2h00
0 2 * * 0 cd /path/to/t-hack-700 && bash monitoring/weekly_retrain.sh
```

---

## 🎯 Résumé

### Pipeline Minimal (Lancement Rapide)
```bash
./start.sh
```

### Pipeline Complet (Première Fois)
```bash
make full-pipeline
python3 generate_meaningful_data.py
python3 ml/train_random_forest.py
python3 dashboard_integration.py
./start.sh
```

### Pipeline de Ré-entraînement
```bash
python3 ml/train_random_forest.py
python3 dashboard_integration.py
python3 serveur_simple.py
```

---

## 📊 Tableau Récapitulatif

| Étape | Script | Durée | Fichiers Générés |
|-------|--------|-------|------------------|
| 1. Nettoyage | `clean_data_controlled.py` | 30-60s | `data/cleaned/*.csv` |
| 2. Validation | `validate_data_strict.py` | 20-40s | `data/validated/*.parquet` |
| 3. Fusion | `generate_meaningful_data.py` | 10-20s | `data/processed/dataset.parquet` |
| 4. ML | `ml/train_random_forest.py` | 1-3min | `models/*.joblib` |
| 5. Dashboards | `dashboard_integration.py` | 10-30s | `dashboard_*.html` |
| 6. SHAP | `explicabilite_shap.py` | 1-2min | `explicabilite/*.png` |
| 7. Serveur | `serveur_simple.py` | Instant | - |

**Durée totale** : ~5-10 minutes

---

## 🎉 Conclusion

Le pipeline LUMEN est conçu pour être :
- ✅ **Automatisé** : Makefile et scripts shell
- ✅ **Modulaire** : Chaque étape indépendante
- ✅ **Traçable** : Logs et rapports à chaque étape
- ✅ **Reproductible** : Checksums et versioning
- ✅ **Explicable** : SHAP pour l'explicabilité

Tu peux maintenant lancer le pipeline complet ou juste les étapes dont tu as besoin ! 🚀
