# Structure du projet LUMEN

## 📁 Fichiers principaux

### Application
- `app_complete.py` - Application Streamlit principale
- `launch_app.py` - Script de lancement

### Installation
- `install.py` - Installation automatique (Python)
- `install.sh` - Installation Linux/Mac
- `install.bat` - Installation Windows
- `install_simple.sh` - Installation simple Linux/Mac
- `install_simple.bat` - Installation simple Windows

### Documentation
- `README.md` - Documentation principale
- `requirements.txt` - Dépendances Python

## 📁 Dossiers

### Assets
- `assets/logo_msp.png` - Logo du ministère

### Données
- `data/spf/` - Données Santé Publique France
- `data/insee/` - Données INSEE
- `data/meteo/` - Données météo
- `data/google_trends/` - Données Google Trends
- `data/wikipedia/` - Données Wikipedia
- `data/context/` - Données contextuelles
- `data/processed/` - Données traitées
- `data/alerts/` - Alertes générées

### Modèles
- `models/` - Modèles Random Forest entraînés
- `models/config_*.json` - Configurations des modèles
- `models/rf_grippe_*.pkl` - Modèles Random Forest
- `models/flu_predictor_*.joblib` - Prédicteurs avancés

### Scripts
- `scripts/collect_real_data_fixed.py` - Collecte données réelles
- `scripts/create_alert_system.py` - Système d'alertes
- `scripts/fuse_data.py` - Fusion des données

## 🚀 Utilisation

### Installation
```bash
python3 install.py
```

### Lancement
```bash
python3 launch_app.py
```

### Accès
Ouvrir http://localhost:8501 dans le navigateur

## 🎯 Fonctionnalités

- **Tableau de bord** : Indicateurs de surveillance grippale
- **Carte interactive** : Visualisation géographique des alertes
- **Système d'alertes** : Détection automatique des risques
- **Assistance IA** : Chatbot professionnel
- **Export de données** : CSV des alertes et protocoles
