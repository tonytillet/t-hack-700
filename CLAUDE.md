# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**LUMEN** - Système d'alerte précoce pour prédire les risques de grippe en France 1-2 mois à l'avance.

- **Type:** Streamlit web application with ML prediction system
- **Stack:** Python 3.8+, Streamlit, scikit-learn (Random Forest), pandas, plotly, folium
- **Purpose:** Analyze health data, behavioral trends, and environmental factors to predict flu epidemics

## Quick Start Commands

### First-time Installation
```bash
# Create virtual environment
python3 -m venv venv

# Install using automated script (recommended)
venv/bin/python install.py

# Launch application
venv/bin/python launch_app.py
```

**Note:** On macOS with Homebrew, you may need to use explicit Python path:
```bash
/opt/homebrew/bin/python3.13 -m venv venv
```

### Daily Usage
```bash
# Activate venv and launch
source venv/bin/activate  # Linux/Mac
python launch_app.py
```

### Data Generation

**Primary method (demo data):**
```bash
venv/bin/python scripts/generate_demo_data.py
```

**Full pipeline (if using real data collection):**
```bash
# 1. Collect data from sources (SPF, INSEE, météo, Google Trends, Wikipedia)
venv/bin/python scripts/collect_real_data_fixed.py

# 2. Merge all data sources into unified dataset
venv/bin/python scripts/fuse_data.py

# 3. Generate alerts and action protocols
venv/bin/python scripts/create_alert_system.py
```

## Architecture

### Application Entry Point
- **Main app:** `app_complete.py` (launched via `launch_app.py`)
- **Port:** 8501 (Streamlit default)
- **Interface:** 5 tabs - Carte, Tableau de bord, Protocoles, Analyse, Configuration

### Data Pipeline Flow

**Standard workflow (demo data - recommended):**
```
generate_demo_data.py → app_complete.py
       ↓
  dataset_with_alerts_*.csv
  alertes_*.csv
  protocoles_*.csv
```

**Advanced workflow (real data collection):**
```
collect_real_data_fixed.py → fuse_data.py → create_alert_system.py → app_complete.py
      (raw data)           (merged data)      (alerts + protocols)    (visualization)
```

#### Demo Data Generation (`scripts/generate_demo_data.py`)
**Primary method for getting started quickly.**

- Generates 30 days of realistic data with seasonal patterns
- Creates all required files in one step:
  - `data/processed/dataset_with_alerts_{timestamp}.csv` - Main dataset
  - `data/alerts/alertes_{timestamp}.csv` - Alert levels by region
  - `data/alerts/protocoles_{timestamp}.csv` - Action protocols with costs/ROI
  - `models/config_{timestamp}.json` - Model configuration
- Simulates seasonal flu patterns (winter peaks)
- Includes predictions for J+7, J+14, J+21, J+28

#### Real Data Collection (`scripts/collect_real_data_fixed.py`)
**Alternative for production use with real data sources.**

- Collects/simulates data from multiple sources
- **Sources:** SPF (urgences, sentinelles, vaccination), INSEE (population), Open-Meteo (weather), Google Trends, Wikipedia
- **Output:** Timestamped CSV files in `data/{source}/` subdirectories
- Creates `data/collection_config.json` tracking metadata

#### Data Fusion (`scripts/fuse_data.py`)
- Merges all source files on `region` + `date` keys
- **Output:** `data/processed/dataset_fused_{timestamp}.csv`
- Handles 13 French regions with proper encoding (accents/apostrophes)

#### Alert System (`scripts/create_alert_system.py`)
- Calculates alert scores using weighted formula (vaccination 40%, urgences 30%, IAS 30%)
- Generates action protocols with estimated costs and ROI
- **Output:** alertes_*.csv, protocoles_*.csv, dataset_with_alerts_*.csv

### Main Application (`app_complete.py`)

**Key classes:**
- `GrippeAlertApp`: Main application controller
  - Loads latest data from `data/processed/` and `data/alerts/`
  - Creates interactive map with Folium
  - Calculates KPIs and displays dashboards
  - Manages alert configuration

- `GrippeChatbot`: Rule-based chatbot assistant
  - Knowledge base about flu, vaccination, surveillance, and LUMEN platform
  - Provides contextual responses to user questions

**Data loading pattern:**
```python
# Always loads the latest timestamped file
files = [f for f in os.listdir('data/processed') if f.startswith('dataset_with_alerts_')]
latest = sorted(files)[-1]
data = pd.read_csv(f'data/processed/{latest}')
```

### Alert Thresholds (configurable in app)
```python
SEUILS = {
    'urgences_critiques': 150,      # Weekly ER visits
    'incidence_critique': 200,      # Per 100k population
    'vaccination_faible': 30,       # Vaccination rate %
    'pct_65_plus_risque': 20,      # At-risk population %
    'temperature_risque': 5,        # Temperature °C
    'tendance_hausse': 50          # Upward trend %
}
```

### French Regions (13 regions used throughout)
```python
regions = [
    'Île-de-France', 'Auvergne-Rhône-Alpes', 'Provence-Alpes-Côte d\'Azur',
    'Nouvelle-Aquitaine', 'Occitanie', 'Grand Est', 'Hauts-de-France',
    'Normandie', 'Bretagne', 'Pays de la Loire', 'Centre-Val de Loire',
    'Bourgogne-Franche-Comté', 'Corse'
]
```

## Important Patterns

### Timestamped File Pattern
All data scripts generate timestamped files to track versions:
```python
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
filename = f'data/spf/urgences_{timestamp}.csv'
```

Application always loads the latest:
```python
files = sorted([f for f in os.listdir(dir) if pattern in f])
latest = files[-1]  # Most recent by lexicographic sort
```

### Data Structure
- **Key columns:** `region`, `date`, `urgences_grippe`, `vaccination_2024`, `alert_score`
- **Date format:** ISO format (YYYY-MM-DD)
- **Region names:** Must match exactly (with proper accents/apostrophes)

### Alert Score Calculation
Demo data calculates alert scores using weighted formula:
```python
alert_score = min(100, max(0,
    (100 - vaccination) * 0.4 +      # 40% weight: low vaccination
    (urgences / 100) * 0.3 +          # 30% weight: high ER visits
    (ias * 10) * 0.3                  # 30% weight: high IAS
))
```

Alert levels:
- **CRITIQUE** (🔴): score ≥ 80
- **ÉLEVÉ** (🟠): 60 ≤ score < 80
- **MODÉRÉ** (🟡): 40 ≤ score < 60
- **FAIBLE** (🟢): score < 40

## Important Development Notes

### Python Environment Management
- **Always use venv** - Direct pip install will fail on Homebrew Python (PEP 668: externally-managed-environment)
- **macOS specific:** May need explicit Python path (`/opt/homebrew/bin/python3.13`) to create venv
- **Dependencies:** Use `requirements.txt` for production (essential packages only), `requirements.txt.backup` includes Jupyter for development

### Data Management
- **Current mode:** Demo data with realistic patterns (recommended for development)
- **Data directory:** Gitignored but structure preserved
- **File versioning:** All data files use `{name}_{YYYYMMDD_HHMMSS}.csv` timestamp pattern
- **App loading:** Always loads latest file by lexicographic sort

### Key Constraints
- **No environment variables needed** - uses public/simulated data sources
- **Port 8501 hardcoded** - Streamlit default
- **13 French regions hardcoded** - Region names must match exactly with proper accents
- **Python 3.8+ required** - Uses modern pandas/numpy features

### Code Origin
- Initially AI-generated (GPT5/Sonnet 4.5) by beginner students
- Has been significantly cleaned up (see git history on `feature/cleancode` branch)
- Documentation structure recently reorganized into `docs/` folder

## Documentation Structure

Comprehensive documentation is available in the repository:

- **[INSTALL.md](INSTALL.md)** - Complete installation guide with troubleshooting (macOS/Linux/Windows)
- **[docs/STRUCTURE.md](docs/STRUCTURE.md)** - Detailed project architecture
- **[docs/DATA.md](docs/DATA.md)** - Data pipeline, collection, and processing (11KB comprehensive guide)
- **[docs/USAGE.md](docs/USAGE.md)** - Interface usage, exports, automation
- **[docs/CONFIGURATION.md](docs/CONFIGURATION.md)** - System configuration and thresholds
- **[docs/MODEL.md](docs/MODEL.md)** - Random Forest architecture, features, metrics
- **[docs/PERFORMANCE.md](docs/PERFORMANCE.md)** - Benchmarks, scalability, optimization
- **[docs/SOURCES.md](docs/SOURCES.md)** - Data sources and APIs details

When working on specific aspects of the project, consult these documents for detailed information beyond this overview.
