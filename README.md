# 🚨 LUMEN - Système d'alerte grippe France

## ✅ SYSTÈME OPÉRATIONNEL

Un système d'alerte précoce opérationnel pour prédire les risques de grippe en France avec des **données réelles** et des protocoles automatiques.

### 🎯 État actuel
- 🏥 **Données réelles collectées** : 4,317 enregistrements SPF
- 👥 **INSEE** : 13 régions avec données démographiques  
- 🌡️ **Météo France** : 3,939 enregistrements météorologiques
- 🚨 **7 alertes actives** détectées
- 📋 **Protocoles automatiques** générés avec ROI

## 📋 Description

Ce projet utilise l'intelligence artificielle (Random Forest) pour analyser les données de santé publique, les tendances comportementales et les facteurs environnementaux afin de prédire les risques de grippe 1-2 mois à l'avance.

### 🎯 Fonctionnalités principales

-   **Carte interactive** : Visualisation des alertes par région
-   **Tableau de bord** : Suivi des alertes en temps réel
-   **Protocoles automatiques** : Actions recommandées avec coûts et ROI
-   **Analyse détaillée** : Zoom sur chaque région
-   **Assistant intelligent** : Chatbot pour répondre à vos questions

## 🚀 Installation

### 📦 Avec Docker

```bash
make dev    # Mode développement (hot-reload)
make start  # Mode production
make stop   # Arrêter les conteneurs
```

**L'application sera accessible sur :** http://localhost:8501

**Arrêter :** `CTRL+C` puis `make stop`

## 📚 Documentation

| Guide                                         | Description                                                    |
| --------------------------------------------- | -------------------------------------------------------------- |
| **[🚀 Processus de Démarrage](docs/PROCESSUS_DEMARRAGE.md)** | Guide complet pour lancer le projet (3 méthodes) |
| **[📜 Documentation des Scripts](docs/SCRIPTS.md)** | Documentation détaillée de tous les scripts Shell et Python |
| **[📖 Index Documentation](docs/README.md)** | Index de toute la documentation disponible |

## 📄 Licence

MIT License - Voir le fichier `LICENSE` pour plus de détails.
