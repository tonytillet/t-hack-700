@echo off
REM 🚨 INSTALLATION ULTRA-SIMPLE - Système d'alerte grippe France
REM Une seule commande pour tout installer !

echo 🚨 Installation du système d'alerte grippe France
echo ==================================================
echo.

REM Vérification de Python
echo 📋 Vérification de Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python n'est pas installé.
    echo 💡 Veuillez installer Python depuis https://python.org
    echo    Assurez-vous de cocher "Add Python to PATH" lors de l'installation
    pause
    exit /b 1
)
echo ✅ Python détecté

REM Vérification de pip
echo 📋 Vérification de pip...
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 💡 Installation de pip...
    python -m ensurepip --upgrade
)
echo ✅ pip détecté

REM Mise à jour de pip
echo 📦 Mise à jour de pip...
python -m pip install --upgrade pip

REM Installation des dépendances une par une
echo 📦 Installation des dépendances...
echo.

echo Installing streamlit...
python -m pip install streamlit

echo Installing pandas...
python -m pip install pandas

echo Installing numpy...
python -m pip install numpy

echo Installing scikit-learn...
python -m pip install scikit-learn

echo Installing plotly...
python -m pip install plotly

echo Installing folium...
python -m pip install folium

echo Installing streamlit-folium...
python -m pip install streamlit-folium

echo Installing requests...
python -m pip install requests

echo Installing scipy...
python -m pip install scipy

echo Installing joblib...
python -m pip install joblib

REM Création des dossiers
echo 📁 Création des dossiers...
if not exist "data" mkdir data
if not exist "data\spf" mkdir data\spf
if not exist "data\insee" mkdir data\insee
if not exist "data\meteo" mkdir data\meteo
if not exist "data\wikipedia" mkdir data\wikipedia
if not exist "data\google_trends" mkdir data\google_trends
if not exist "data\processed" mkdir data\processed
if not exist "data\alerts" mkdir data\alerts
if not exist "models" mkdir models

REM Génération de données de démonstration
echo 📊 Préparation des données...
python -c "
import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta

# Créer des données de démonstration
regions = ['Île-de-France', 'Auvergne-Rhône-Alpes', 'Provence-Alpes-Côte d\'Azur', 
           'Nouvelle-Aquitaine', 'Occitanie', 'Grand Est', 'Hauts-de-France', 
           'Normandie', 'Bretagne', 'Pays de la Loire', 'Centre-Val de Loire', 
           'Bourgogne-Franche-Comté', 'Corse']

data = []
for i, region in enumerate(regions):
    for week in range(52):
        date = datetime(2024, 1, 1) + timedelta(weeks=week)
        data.append({
            'region': region,
            'date': date.strftime('%Y-%m-%d'),
            'alert_score': np.random.uniform(20, 90),
            'urgences_grippe': np.random.randint(50, 500),
            'vaccination_2024': np.random.uniform(25, 75),
            'pct_65_plus': np.random.uniform(15, 25),
            'population_totale': np.random.randint(500000, 12000000)
        })

df = pd.DataFrame(data)
df.to_csv('data/processed/dataset_demo.csv', index=False)
print('✅ Données de démonstration créées')
"

REM Créer des alertes de démonstration
python -c "
import pandas as pd
import numpy as np

alerts = []
regions = ['Île-de-France', 'Auvergne-Rhône-Alpes', 'Provence-Alpes-Côte d\'Azur']
for region in regions:
    alerts.append({
        'region': region,
        'level': 'CRITIQUE' if np.random.random() > 0.5 else 'ÉLEVÉ',
        'score': np.random.uniform(70, 95),
        'message': f'Alerte {region} - Action immédiate requise',
        'timestamp': '2024-10-20 22:00:00'
    })

df_alerts = pd.DataFrame(alerts)
df_alerts.to_csv('data/alerts/alertes_demo.csv', index=False)
print('✅ Alertes de démonstration créées')
"

echo.
echo 🎉 Installation terminée avec succès !
echo.
echo 🚀 Pour lancer l'application :
echo    python launch_app.py
echo.
echo 🌐 L'application sera accessible sur :
echo    http://localhost:8501
echo.
echo 📚 En cas de problème, consultez le README.md
echo.
echo ✅ Prêt à prédire les risques de grippe !
pause
