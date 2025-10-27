# LUMEN - Flu Alert Prediction System

## Project Overview

**LUMEN** is a Streamlit-based flu alert prediction system that combines multiple data sources (emergency services data, weather data, Wikipedia content) to predict future flu activity using machine learning.

The system architecture follows a classic ML pipeline:
- Data Collection & Cleaning → Feature Engineering → Model Training → Predictions → Streamlit UI

## High-Level Architecture

```
Raw Data Sources
    ├── data.gouv.fr (health emergency data)
    ├── Weather APIs (temperature, humidity)
    └── Wikipedia APIs (health-related content)
         ↓
DVC Pipeline (Data Version Control)
    └── Clean & Standardize Data
         ↓
Feature Engineering
    ├── Create time-series features (lags, rolling windows)
    ├── One-hot encode categorical variables
    ├── Target variable: emergency cases at J+7
         ↓
Model Training
    └── RandomForestRegressor (temporal split validation)
         ↓
Predictions & Analysis
         ↓
Streamlit Dashboard (app.py)
```

## Project Structure

### Core Application
- **`app.py`** - Main Streamlit entry point (minimal, ready for dashboard content)
- **`requirements.txt`** - Python dependencies (pandas, scikit-learn, streamlit, plotly, etc.)

### Configuration Files
- **`Dockerfile`** - Python 3.9 slim image with auto-reload for development
- **`compose.yml`** - Docker Compose configuration (service: lumen on port 8501)
- **`dvc.yaml`** - DVC pipeline definition (clean_data stage)
- **`dvc.lock`** - DVC dependency lock file (ensures reproducibility)

### Data Management Structure

```
data/
├── raw/                          # Raw data sources (DVC tracked)
│   ├── data_gouv_fr/            # JSON files from data.gouv.fr API
│   └── other/                    # Weather, Wikipedia data
├── processed/                    # Cleaned data
│   ├── lumen_merged_clean.parquet    # Main cleaned dataset
│   ├── timeseries/              # Time-series specific data
│   ├── *_clean.parquet          # Source-specific cleaned files
│   └── clean_data.log           # Cleaning log
├── features/                     # ML-ready features
│   ├── features.parquet         # Input features (X)
│   ├── y_target.parquet         # Target variable (y_target = emergency cases J+7)
│   └── feature_list.json        # Feature names for model
├── artifacts/                    # Trained model & metadata
│   ├── rf.joblib               # RandomForest model
│   ├── metrics.json            # Training metrics (MAE, RMSE, R²)
│   ├── feature_importance.json # Feature importance rankings
│   └── model_summary.json      # Training metadata
├── config/                       # Reference statistics
│   ├── medians.json            # Median values for numeric features
│   ├── cats.json               # Categorical variable mappings
│   └── stats_summary.json      # Statistics summary
├── predictions/                  # Model predictions
│   ├── predictions.parquet     # Predictions with errors
│   └── predictions_summary.json # Prediction analysis & metrics
└── raw.dvc                      # DVC metadata for raw data
```

### Scripts Pipeline (in `scripts/` directory)

The ML pipeline executes sequentially through 4 main stages:

#### Stage 1: Data Cleaning
- **`clean_data.py`** - Main cleaning orchestrator
  - Processes data.gouv.fr JSON files
  - Cleans weather data (temperature, humidity)
  - Processes Wikipedia content metadata
  - Standardizes all data to common schema (date, region, departement, valeur, type_donnee, source, unite)
  - Outputs: `lumen_merged_clean.parquet`

#### Stage 2: Baseline Statistics
- **`fit_stats.py`** - Calculates reference statistics
  - Computes medians for numeric features
  - Maps categorical variables
  - Outputs: `medians.json`, `cats.json`, `stats_summary.json`

#### Stage 3: Feature Engineering
- **`make_features.py`** - Creates ML-ready features
  - Loads time-series data from `daily_emergency_series_simple.parquet`
  - Creates target variable: emergency count at J+7 (temporal shift)
  - Generates lags (t-1, t-7, t-14, etc.) and rolling windows (7d, 14d, 30d)
  - One-hot encodes categorical variables (departments, regions)
  - Outputs: `features.parquet`, `y_target.parquet`, `feature_list.json`

#### Stage 4: Model Training
- **`train_random_forest.py`** - Trains RandomForestRegressor
  - Uses temporal split (no shuffle) to respect time-series nature
  - Split: 80% train, 20% test
  - Model config: 100 estimators, max_depth=20, sqrt features
  - Outputs: `rf.joblib`, `metrics.json`, `feature_importance.json`

#### Stage 5: Predictions
- **`predict.py`** - Generates predictions on full dataset
  - Loads trained model and features
  - Predicts emergency cases for all data points
  - Calculates errors (absolute, relative)
  - Generates per-department metrics
  - Outputs: `predictions.parquet`, `predictions_summary.json`

### Pipeline Orchestration
- **`run_pipeline.py`** - Master script that runs all 4 stages sequentially
  - Executes: fit_stats → make_features → train_random_forest → predict
  - Logs each step and stops on first failure
  - Use: `python scripts/run_pipeline.py`

### Data Collection Scripts (for reference)
- `collect_emergency_data.py` - Fetches emergency service data via API
- `collect_weather_data_gouv.py` - Collects weather data
- Various data extraction & transformation scripts (for historical use)

## Development Workflow

### Quick Start

```bash
# Clone repo
git clone git@github.com:tonytillet/t-hack-700.git
cd t-hack-700

# Option 1: Docker (recommended)
docker compose up -d --build
# Access: http://localhost:8501

# Option 2: Local development
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Pull data
dvc pull

# Run ML pipeline
python scripts/run_pipeline.py

# Or run individual stages
python scripts/fit_stats.py
python scripts/make_features.py
python scripts/train_random_forest.py
python scripts/predict.py

# Run Streamlit app
streamlit run app.py
```

### Key Commands

#### DVC (Data Management)
```bash
# Sync with remote
dvc pull              # Download large data files
dvc push              # Upload changes
dvc status            # Check what changed
dvc repro             # Reproduce pipeline

# Add new raw data
dvc add data/raw/new_file.csv
git add data/raw/new_file.csv.dvc
git commit -m "add: new raw data"
dvc push
```

#### Development
```bash
# Full ML pipeline (all 4 stages)
python scripts/run_pipeline.py

# Individual stages (useful for debugging)
python scripts/clean_data.py        # Clean raw data
python scripts/fit_stats.py          # Calculate statistics
python scripts/make_features.py      # Create features
python scripts/train_random_forest.py # Train model
python scripts/predict.py            # Generate predictions

# Dashboard
streamlit run app.py                # Dev mode with auto-reload
docker compose up -d --build        # Production via Docker
```

#### Git Workflow
```bash
# Check recent work
git log --oneline -n 10

# Create feature branch
git checkout -b feature/description

# Commit (following repo conventions)
git add .
git commit -m "feat: description"  # or fix:, docs:, etc.

# Push and create PR
git push origin feature/description
```

## Data Flow & Key Concepts

### Data Schema (Standardized)
All cleaned data follows this schema:
```python
{
    'date': datetime,           # When the measurement occurred
    'region': str,              # Region code (IDF, ARA, PACA, etc.)
    'departement': str,         # Department identifier
    'valeur': float,            # Numeric measurement value
    'type_donnee': str,         # Data type (temperature, case_count, etc.)
    'source': str,              # Data origin (data_gouv_fr, open_meteo, wikipedia)
    'unite': str                # Unit of measurement (celsius, count, etc.)
}
```

### Target Variable
- **y_target**: Emergency department visits at date D+7
- Created by shifting emergency count forward 7 days
- Used to predict "what will happen in the next week"

### Feature Categories
1. **Lag features**: Past values (t-1, t-7, t-14 days)
2. **Rolling features**: Moving averages/sums (7-day, 14-day, 30-day windows)
3. **Categorical features**: One-hot encoded (region, department)
4. **Metadata**: Reference statistics from `medians.json` and `cats.json`

### Model Evaluation Metrics
- **MAE** (Mean Absolute Error): Average absolute prediction error
- **RMSE** (Root Mean Squared Error): Penalizes larger errors more
- **R²** (Coefficient of determination): % of variance explained
- **Relative metrics**: MAE/RMSE as % of mean target value
- All metrics reported on hold-out test set (last 20% of time period)

## Dependencies & Configuration

### Python Packages
- **pandas, pyarrow** - Data manipulation & Parquet I/O
- **scikit-learn** - Machine learning (RandomForest, metrics)
- **numpy** - Numerical computations
- **joblib** - Model serialization
- **streamlit, plotly** - Dashboard & visualization
- **matplotlib** - Plotting
- **wikipedia-api** - Wikipedia data collection

### Environment Configuration
- Python 3.9 (in Docker)
- DVC with local storage (`dvcstore/` directory)
- Streamlit server on port 8501
- Auto-reload enabled for development

### Important Notes for Developers

1. **Time-series handling**: Always use temporal split (no shuffle) when training
2. **Target shift**: y_target is created by shifting emergency data forward 7 days
3. **Missing data**: Handled via median imputation (from `medians.json`)
4. **Region mapping**: Custom standardization to 2-letter codes (IDF, ARA, etc.)
5. **Data paths**: All paths relative to project root, use `Path()` from pathlib
6. **Logging**: All scripts log to both console and `data/processed/clean_data.log`
7. **DVC reproducibility**: Never manually edit `dvc.lock`; let DVC manage it

## ML Model Details

### RandomForestRegressor Configuration
```python
{
    'n_estimators': 100,           # Number of trees
    'max_depth': 20,               # Tree depth limit
    'min_samples_split': 5,        # Min samples to split node
    'min_samples_leaf': 2,         # Min samples in leaf
    'max_features': 'sqrt',        # Feature selection at each split
    'random_state': 42,            # Reproducibility
    'n_jobs': -1                   # Use all CPU cores
}
```

### Training Setup
- **Validation**: Temporal split (80/20) - no data leakage
- **Loss metric**: Mean Squared Error (regression)
- **Feature scaling**: Not used (Random Forests are scale-invariant)
- **Hyperparameters**: Fixed (no grid search in current version)

## Common Development Tasks

### Adding New Data Source
1. Create collection script in `scripts/`
2. Save raw data to `data/raw/<source_name>/`
3. Add processing logic to `clean_data.py`
4. Test pipeline: `python scripts/run_pipeline.py`
5. Commit: `git add . && git commit -m "feat: add new data source"`

### Debugging Data Pipeline
```bash
# Check what files exist
ls data/raw/
ls data/processed/

# Load and inspect cleaned data
python -c "import pandas as pd; df = pd.read_parquet('data/processed/lumen_merged_clean.parquet'); print(df.head())"

# Check model performance
python -c "import json; print(json.load(open('data/artifacts/metrics.json')))"
```

### Improving Model Performance
1. Examine `feature_importance.json` (top features vs. their importance)
2. Check `predictions_summary.json` for per-department errors
3. Adjust feature engineering in `make_features.py` (new lags, windows, etc.)
4. Try different hyperparameters in `train_random_forest.py`
5. Retrain: `python scripts/run_pipeline.py`

### Extending Streamlit Dashboard
Edit `app.py`:
```python
import streamlit as st
import pandas as pd

# Load predictions
preds = pd.read_parquet('data/predictions/predictions.parquet')

# Display metrics
st.metric("MAE", preds['abs_error'].mean())

# Show plot
st.plotly_chart(...)
```

## Repository Status

- **Main branch**: Stable, deployable
- **Recent changes**: Dependency updates, code cleanup
- **PR convention**: Feature branches from `main`, described PRs
- **Git workflow**: Conventional commits (feat:, fix:, docs:, refactor:, etc.)

## Troubleshooting

### DVC Pull Fails
- Ensure `.dvc/config` points to correct remote
- Check local storage space: `df -h`
- Verify network access to remote

### Pipeline Fails at Stage X
1. Check the stage's log output for details
2. Verify input files exist and are readable
3. Run individual stage script to debug
4. Check `data/processed/clean_data.log` for cleaning issues

### Model Metrics Are NaN
- Check if features/target are being loaded correctly
- Look for missing data not handled by median imputation
- Verify temporal split logic in `train_random_forest.py`

### Docker Build Fails
- Clear Docker build cache: `docker system prune`
- Rebuild: `docker compose up -d --build`
- Check `requirements.txt` for incompatible versions

## Next Steps for Developers

1. **Understand the pipeline**: Run `python scripts/run_pipeline.py` end-to-end
2. **Inspect artifacts**: Look at `data/artifacts/` JSON files for model details
3. **Build dashboard**: Extend `app.py` with visualizations from predictions
4. **Test locally**: Use Docker Compose for full environment
5. **Review ML model**: Examine feature importance and prediction errors
