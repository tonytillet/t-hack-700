# 🧠 LUMEN - Structure Finale Nettoyée

## 📁 Fichiers Essentiels Conservés

### 🚀 Application Principale
- `main.py` - Application Streamlit principale
- `dashboard_final_integration.html` - Dashboard final intégré
- `dashboard_integration.py` - Script d'intégration dashboard

### 🤖 Machine Learning
- `ml/train_random_forest.py` - Entraînement modèle
- `models/` - Modèles entraînés (3 modèles)
- `ml/artefacts/` - Métriques et rapports ML

### 📊 Monitoring & Auto-Retrain
- `monitoring/` - Configuration monitoring
- `monitoring_auto_retrain.py` - Auto-retrain hebdomadaire

### 📈 Explicabilité SHAP
- `explicabilite/` - Plots SHAP (15 plots)
- `explicabilite_shap.py` - Génération plots

### 🗂️ Données
- `data/` - Données (raw, cleaned, processed, validated)
- `evidence/` - Bundle de preuve (9 fichiers)

### 🔧 Configuration
- `requirements.txt` - Dépendances
- `Makefile` - Commandes automatisées
- `Dockerfile` - Container
- `compose.yml` / `compose.dev.yml` - Docker Compose

### 🧹 Nettoyage & Validation
- `clean_data_controlled.py` - Nettoyage contrôlé
- `validate_data_strict.py` - Validation stricte
- `generate_meaningful_data.py` - Génération données

### 📊 Visualisations HTML
- `dashboard_risk_heatmap.html` - Carte zones à risque
- `dashboard_real_vs_predicted.html` - Graphiques réel vs prédit
- `dashboard_active_alerts.html` - Panneau alertes actives

## 🗑️ Fichiers Supprimés (34 fichiers)
- ✅ Tous les dashboards en double
- ✅ Scripts de test obsolètes
- ✅ Lanceurs multiples
- ✅ HTML en double
- ✅ Documentation redondante
- ✅ Scripts temporaires

## 🎯 Utilisation

### 🚀 Lancer l'Application
```bash
make dev
# ou
docker compose up --build
```

### 📊 Générer Visualisations
```bash
python3 dashboard_integration.py
```

### 🧠 Générer Explicabilité
```bash
python3 explicabilite_shap.py
```

### 🔄 Auto-Retrain
```bash
python3 monitoring_auto_retrain.py
```

## 🌐 Accès Dashboard
- **Dashboard Final:** http://localhost:8087/dashboard_final_integration.html
- **Carte Zones:** http://localhost:8087/dashboard_risk_heatmap.html
- **Prédictions:** http://localhost:8087/dashboard_real_vs_predicted.html
- **Alertes:** http://localhost:8087/dashboard_active_alerts.html

## 📊 Performance
- **R² Score:** 97.1%
- **MAE:** 5.08
- **Modèles:** 3 entraînés
- **Plots SHAP:** 15 générés
- **Alertes:** 6 actives

## 🎉 Résultat
Structure propre et organisée avec seulement les fichiers essentiels !
