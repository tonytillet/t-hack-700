# 🧠 LUMEN Enhanced
## Système de Surveillance Épidémiologique Intelligente

[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen.svg)]()

### 🎯 **Vue d'ensemble**

LUMEN Enhanced est un système de surveillance épidémiologique intelligent qui utilise l'intelligence artificielle pour prédire et surveiller les épidémies de grippe en temps réel. Le système combine des données officielles françaises, des modèles de machine learning avancés et des visualisations interactives pour fournir des alertes précoces et des recommandations actionnables.

---

## 🚀 **Démarrage Rapide**

### **Option 1 : Script Automatique (Recommandé)**
```bash
git clone <votre-repo-url>
cd t-hack-700
./start.sh
```

### **Option 2 : Lancement Manuel**
```bash
git clone <votre-repo-url>
cd t-hack-700
pip install -r requirements.txt
python3 serveur_simple.py
```

### **Option 3 : Docker**
```bash
git clone <votre-repo-url>
cd t-hack-700
docker compose up --build
```

---

## 🌐 **Accès au Système**

Une fois lancé, accédez au projet sur : **http://localhost:8080/**

### 📊 **Dashboards Disponibles**

| Dashboard | URL | Description |
|-----------|-----|-------------|
| 🏠 **Menu Principal** | `/` | Interface unifiée avec navigation |
| 🔔 **Bulletin Public** | `/bulletin_lumen.html` | Résumé pour le grand public |
| 📚 **Vue Pédagogique** | `/dashboard_pedagogique.html` | Indicateurs simplifiés |
| 🗺️ **Carte des Risques** | `/dashboard_risk_heatmap.html` | Visualisation géographique |
| 📈 **Prédictions** | `/dashboard_real_vs_predicted.html` | Comparaison prédictions/réalité |
| 🚨 **Alertes Actives** | `/dashboard_active_alerts.html` | Surveillance temps réel |

---

## 🎯 **Fonctionnalités Principales**

### 🤖 **Intelligence Artificielle**
- **Prédictions précises** : 97.1% de fiabilité
- **Machine Learning** : Random Forest optimisé
- **Explicabilité** : 15 plots SHAP générés automatiquement
- **Auto-retrain** : Mise à jour hebdomadaire automatique

### 📊 **Données en Temps Réel**
- **Sources officielles** : Data.gouv.fr, Météo France, Santé Publique France
- **51 indicateurs** analysés simultanément
- **20 départements** français couverts
- **Mise à jour quotidienne** automatique

### 🎨 **Interface Utilisateur**
- **Design responsive** : Mobile et desktop
- **Indicateurs visuels** : Jauges colorées et emojis
- **Messages dynamiques** : Alertes automatiques
- **Navigation intuitive** : Menu unifié

---

## 📈 **Métriques de Performance**

| Métrique | Valeur | Description |
|----------|--------|-------------|
| **R² Score** | 97.1% | Fiabilité des prévisions |
| **MAE** | 5.08 | Erreur moyenne (cas) |
| **Accuracy** | 94.2% | Précision de classification |
| **F1-Score** | 91% | Équilibre précision/rappel |
| **Temps de réponse** | < 1s | Prédictions en temps réel |
| **Couverture** | 20 départements | Zones surveillées |

---

## 🛠️ **Architecture Technique**

### **Pipeline de Données**
```
Récupération → Gel → Nettoyage → Validation → Fusion → ML → Prédictions → Visualisations
```

### **Technologies Utilisées**
- **Backend** : Python 3.7+, Flask
- **ML** : Scikit-learn, Pandas, NumPy
- **Visualisation** : Plotly, HTML/CSS/JS
- **Validation** : Pandera, Dataprep
- **Explicabilité** : SHAP

### **Structure du Projet**
```
t-hack-700/
├── 📊 dashboards/          # Visualisations HTML
├── 🤖 ml/                  # Modèles et entraînement
├── 📁 data/               # Données (raw, processed, validated)
├── 🔍 explicabilite/      # Plots SHAP
├── 📊 monitoring/         # Surveillance automatique
├── 🚀 serveur_simple.py   # Serveur principal
└── 📚 docs/              # Documentation
```

---

## 🔧 **Configuration**

### **Variables d'Environnement**
```bash
# Port du serveur (défaut: 8080)
export LUMEN_PORT=8080

# Mode debug (défaut: False)
export LUMEN_DEBUG=False
```

### **Fichiers de Configuration**
- `requirements.txt` : Dépendances Python
- `monitoring/config.json` : Configuration monitoring
- `ml/train_random_forest.py` : Configuration ML

---

## 📚 **Documentation**

- **[Guide de Lancement](LANCEMENT_PROJET.md)** : Instructions détaillées
- **[Pipeline de Données](PIPELINE_DONNEES_COMPLET.md)** : Architecture complète
- **[Métriques Publiques](METRIQUES_PUBLIQUES.md)** : Explication des performances
- **[Nettoyage Git](NETTOYAGE_GIT.md)** : Gestion des fichiers volumineux

---

## 🤝 **Contribution**

### **Développement Local**
```bash
# Cloner le projet
git clone <votre-repo-url>
cd t-hack-700

# Créer une branche
git checkout -b feature/nouvelle-fonctionnalite

# Installer en mode développement
pip install -e .

# Lancer les tests
python -m pytest tests/

# Lancer le serveur
python3 serveur_simple.py
```

### **Workflow Git**
1. Fork du projet
2. Créer une branche feature
3. Développer et tester
4. Créer une Pull Request
5. Review et merge

---

## 📞 **Support**

### **Problèmes Courants**
- **Port occupé** : Le script `start.sh` trouve automatiquement un port libre
- **Dépendances manquantes** : `pip install -r requirements.txt`
- **Fichiers manquants** : `python3 dashboard_integration.py`

### **Logs et Debug**
```bash
# Vérifier les logs
tail -f data/logs/validation.log

# Mode debug
export LUMEN_DEBUG=True
python3 serveur_simple.py
```

---

## 📄 **Licence**

Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

---

## 🎉 **Remerciements**

- **Santé Publique France** pour les données épidémiologiques
- **Data.gouv.fr** pour l'ouverture des données
- **Météo France** pour les données météorologiques
- **Communauté Python** pour les librairies open-source

---

## 📊 **Statistiques du Projet**

- **Lignes de code** : 15,000+
- **Fichiers** : 50+
- **Dashboards** : 6
- **Modèles ML** : 3
- **Plots SHAP** : 15
- **Départements couverts** : 20

---

**🧠 LUMEN Enhanced - Surveillance Épidémiologique Intelligente**  
*Transformons les données en prédictions actionnables pour protéger la population française.*