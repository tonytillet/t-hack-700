# Structure du projet LUMEN

## Vue d'ensemble

**LUMEN** - Système d'alerte précoce pour prédire les risques de grippe en France 1-2 mois à l'avance.

Application Streamlit utilisant Random Forest pour l'analyse prédictive des épidémies de grippe.

## 📁 Arborescence complète

```
t-hack-700/
├── main.py                      # Point d'entrée principal
│
├── README.md                    # Documentation principale
├── INSTALL.md                   # Guide d'installation complet
├── CLAUDE.md                    # Documentation pour Claude Code
│
├── Dockerfile                   # Configuration Docker
├── Makefile                     # Commandes make (dev/start/stop)
├── compose.yml                  # Docker Compose production
├── compose.dev.yml              # Docker Compose développement
│
├── requirements.txt             # Dépendances production
├── requirements.txt.backup      # Dépendances complètes avec Jupyter
│
├── config/                      # Configuration
│   └── app_config.json          # Configuration de l'application
│
├── src/                         # Code source (architecture MVC)
│   ├── __init__.py
│   ├── config/
│   │   └── settings.py          # Paramètres de configuration
│   ├── models/
│   │   ├── app.py               # Logique métier (GrippeAlertApp)
│   │   └── chatbot.py           # Chatbot (GrippeChatbot)
│   ├── utils/
│   │   └── helpers.py           # Fonctions utilitaires
│   └── views/
│       ├── main_app.py          # Application Streamlit principale
│       ├── components/          # Composants UI réutilisables
│       │   ├── dashboard_alerts_table.py
│       │   ├── dashboard_filters.py
│       │   ├── dashboard_indicators.py
│       │   ├── dashboard_kpis.py
│       │   └── sections.py
│       ├── helpers/
│       │   └── data_filters.py  # Helpers pour filtres
│       └── pages/               # Modules de pages
│           ├── map_page.py      # Carte interactive
│           ├── dashboard_page.py # Tableau de bord
│           ├── protocols_page.py # Protocoles d'action
│           ├── analysis_page.py # Analyse régionale
│           └── assistant_page.py # Assistant chatbot
│
├── docs/                        # Documentation détaillée
│   ├── ARCHITECTURE.md          # Architecture technique
│   ├── CONFIGURATION.md         # Configuration et seuils
│   ├── DATA.md                  # Pipeline de données
│   ├── MODEL.md                 # Modèle d'IA
│   ├── PERFORMANCE.md           # Métriques et benchmarks
│   ├── SOURCES.md               # Sources de données
│   ├── STRUCTURE.md             # Ce fichier - Architecture du projet
│   └── USAGE.md                 # Guide d'utilisation
│
├── scripts/                     # Scripts de traitement
│   ├── generate_demo_data.py    # ⭐ Génération données démo (principal)
│   ├── collect_data.py          # Collecte données réelles
│   ├── fuse_data.py             # Fusion des sources de données
│   └── create_alert_system.py  # Génération des alertes
│
├── data/                        # Données (gitignored)
│   ├── processed/               # dataset_with_alerts_*.csv
│   ├── alerts/                  # alertes_*.csv, protocoles_*.csv
│   ├── spf/                     # Santé Publique France
│   ├── insee/                   # INSEE (démographie)
│   ├── meteo/                   # Météo France
│   ├── wikipedia/               # Wikipedia views
│   ├── google_trends/           # Google Trends
│   └── collection_config.json   # Config de collecte
│
├── models/                      # Modèles ML sauvegardés (gitignored)
│   ├── config_*.json            # Configurations
│   ├── rf_grippe_*.pkl          # Random Forest models
│   └── flu_predictor_*.joblib   # Prédicteurs complets
│
└── assets/
    └── logo_msp.png             # Logo ministère
```

## 📋 Fichiers principaux

### Application

| Fichier | Description |
|---------|-------------|
| `main.py` | Point d'entrée principal qui ajoute `src/` au path Python et lance `src/views/main_app.py` |
| `src/views/main_app.py` | Application Streamlit principale avec navigation entre 5 pages (Map, Dashboard, Protocols, Analysis, Assistant) |
| `src/models/app.py` | Logique métier principale (`GrippeAlertApp` class) |
| `src/models/chatbot.py` | Assistant conversationnel (`GrippeChatbot` class) |

### Docker

| Fichier | Description |
|---------|-------------|
| `Dockerfile` | Configuration Docker multi-stage (development/builder/runner) |
| `compose.yml` | Docker Compose pour production |
| `compose.dev.yml` | Docker Compose pour développement avec hot-reload |
| `Makefile` | Commandes make (dev/start/stop/logs) |
| `requirements.txt` | Dépendances Python |
| `requirements.txt.backup` | Dépendances complètes incluant Jupyter |

### Documentation

| Fichier | Description |
|---------|-------------|
| `README.md` | Documentation principale avec quick start et table des matières |
| `INSTALL.md` | Guide d'installation détaillé avec troubleshooting (macOS/Linux/Windows) |
| `CLAUDE.md` | Documentation technique pour Claude Code (architecture, patterns, contraintes) |
| `docs/*.md` | Documentation détaillée (voir section Dossiers ci-dessous) |

## 📁 Dossiers

### docs/

Documentation détaillée du projet :

| Fichier | Description |
|---------|-------------|
| `CONFIGURATION.md` | Configuration des seuils d'alerte et paramètres système |
| `DATA.md` | Pipeline de données, collecte, traitement (11KB, très détaillé) |
| `MODEL.md` | Architecture du modèle Random Forest, features utilisées |
| `PERFORMANCE.md` | Métriques, benchmarks, scalabilité |
| `SOURCES.md` | Détail des sources de données et APIs |
| `STRUCTURE.md` | Ce fichier - Architecture complète du projet |
| `USAGE.md` | Guide d'utilisation de l'interface |

### scripts/

Scripts de traitement des données :

| Script | Usage | Description |
|--------|-------|-------------|
| `generate_demo_data.py` | **⭐ Principal** | Génère 30 jours de données démo avec patterns réalistes (alertes, protocoles, config) |
| `collect_data.py` | Avancé | Collecte données réelles depuis SPF, INSEE, Météo France, Google Trends, Wikipedia |
| `fuse_data.py` | Avancé | Fusionne toutes les sources sur `region` + `date` |
| `create_alert_system.py` | Avancé | Calcule scores d'alerte et génère protocoles d'action |

**Workflow recommandé :** Utiliser uniquement `generate_demo_data.py` pour démarrer rapidement.

**Workflow avancé :** `collect_data.py` → `fuse_data.py` → `create_alert_system.py`

### data/

**Note :** Tout le contenu du dossier `data/` est gitignored, seule la structure est préservée.

| Sous-dossier | Contenu | Format |
|--------------|---------|--------|
| `processed/` | Datasets fusionnés avec alertes | `dataset_with_alerts_{YYYYMMDD_HHMMSS}.csv` |
| `alerts/` | Alertes et protocoles générés | `alertes_*.csv`, `protocoles_*.csv` |
| `spf/` | Données Santé Publique France | `sentinelles_*.csv`, `urgences_*.csv`, `vaccination_*.csv` |
| `insee/` | Données démographiques INSEE | `insee_*.csv` |
| `meteo/` | Données météorologiques | `meteo_*.csv` |
| `wikipedia/` | Pages vues Wikipedia | `wikipedia_*.csv` |
| `google_trends/` | Tendances de recherche | `trends_*.csv` |

**Fichier spécial :** `collection_config.json` - Métadonnées de collecte (timestamp, sources, type)

### models/

**Note :** Tout le contenu du dossier `models/` est gitignored (modèles générés).

| Fichier | Description |
|---------|-------------|
| `config_*.json` | Configurations de modèle avec timestamp |
| `rf_grippe_*.pkl` | Modèles Random Forest entraînés |
| `flu_predictor_*.joblib` | Prédicteurs complets avec pipeline |

### assets/

| Fichier | Description |
|---------|-------------|
| `logo_msp.png` | Logo du Ministère de la Santé Publique |

## 🚀 Commandes principales

### Avec Docker

```bash
make dev    # Mode développement (hot-reload)
make start  # Mode production
make stop   # Arrêter les conteneurs
make logs   # Voir les logs
```

**Accès :** http://localhost:8501

### Génération de données

Les données sont générées automatiquement au démarrage des conteneurs Docker.

**Génération manuelle** (si nécessaire):
```bash
# Données démo
docker compose run python python scripts/generate_demo_data.py

# Pipeline complet
docker compose run python python scripts/collect_data.py
docker compose run python python scripts/fuse_data.py
docker compose run python python scripts/create_alert_system.py
```

## 🎯 Fonctionnalités de l'application

L'application propose 5 pages :

1. **Carte** : Visualisation géographique interactive des 13 régions françaises avec niveaux d'alerte
2. **Tableau de bord** : Indicateurs clés (urgences, vaccination, IAS) et graphiques temporels
3. **Protocoles** : Actions recommandées par région avec coûts estimés et ROI
4. **Analyse** : Analyse détaillée par région avec prédictions J+7, J+14, J+21, J+28
5. **Assistant** : Chatbot conversationnel pour répondre aux questions

**Fonctionnalités supplémentaires :**

## 🔧 Architecture technique

### Stack technologique


### Pattern de nommage des fichiers

Tous les fichiers de données utilisent un timestamp :
```
{nom}_{YYYYMMDD_HHMMSS}.csv
```

Exemple : `dataset_with_alerts_20251021_143022.csv`

L'application charge toujours le fichier le plus récent par tri lexicographique.

### Régions françaises

13 régions hardcodées avec accents/apostrophes exacts :

## 📊 Flux de données

### Mode démo (recommandé)

```
generate_demo_data.py
       ↓
data/processed/dataset_with_alerts_*.csv
data/alerts/alertes_*.csv
data/alerts/protocoles_*.csv
models/config_*.json
       ↓
main.py (chargement automatique)
```

### Mode production (avancé)

```
collect_data.py → fuse_data.py → create_alert_system.py → main.py
   (collecte sources)      (fusion données)   (calcul alertes)      (visualisation)
```

## 📖 Ressources

