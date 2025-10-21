# 🚨 LUMEN - Système d'alerte grippe France

Un système d'alerte précoce pour prédire les risques de grippe en France avec des données temps réel et des protocoles automatiques.

## 📋 Description

Ce projet utilise l'intelligence artificielle (Random Forest) pour analyser les données de santé publique, les tendances comportementales et les facteurs environnementaux afin de prédire les risques de grippe 1-2 mois à l'avance.

### 🎯 Fonctionnalités principales

-   **Carte interactive** : Visualisation des alertes par région
-   **Tableau de bord** : Suivi des alertes en temps réel
-   **Protocoles automatiques** : Actions recommandées avec coûts et ROI
-   **Analyse détaillée** : Zoom sur chaque région
-   **Configuration** : Paramétrage des seuils d'alerte

## 🚀 Installation

### 📦 Avec Docker (recommandé)

Mode développement :

```bash
make dev    # Lancer en développement (hot-reload)
make start  # Lancer en production
```

**L'application sera accessible sur :** http://localhost:8501

Pour stopper le server -> `CTRL+C`

### 📝 Installation manuelle (sans Docker)

Pour installer sans Docker, consultez le [guide d'installation manuel](docs/INSTALL-MANUAL.md).

## 📚 Documentation

| Guide                                         | Description                                                    |
| --------------------------------------------- | -------------------------------------------------------------- |
| **[📦 Installation](INSTALL.md)**             | Guide d'installation détaillé avec troubleshooting             |
| **[📊 Données](docs/DATA.md)**                | Où sont les données, comment elles sont collectées et traitées |
| **[🚀 Utilisation](docs/USAGE.md)**           | Guide d'utilisation de l'interface et fonctionnalités          |
| **[⚙️ Configuration](docs/CONFIGURATION.md)** | Configuration des seuils et paramètres système                 |
| **[🔬 Modèle IA](docs/MODEL.md)**             | Architecture du modèle et features utilisées                   |
| **[📈 Performance](docs/PERFORMANCE.md)**     | Métriques, benchmarks et scalabilité                           |
| **[📖 Sources](docs/SOURCES.md)**             | Détail des sources de données et APIs                          |
| **[🔧 Claude Code](CLAUDE.md)**               | Documentation technique pour Claude Code                       |
| **[📁 Structure](docs/STRUCTURE.md)**         | Architecture complète du projet                                |

## 📄 Licence

MIT License - Voir le fichier `LICENSE` pour plus de détails.
