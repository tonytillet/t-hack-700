#!/bin/bash

# 🚨 INSTALLATION ULTRA-SIMPLE - Système d'alerte grippe France
# Une seule commande pour tout installer !

echo "🚨 Installation du système d'alerte grippe France"
echo "=================================================="
echo ""

# Vérification et installation de Python si nécessaire
echo "📋 Vérification de Python..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 n'est pas installé."
    echo "💡 Installation de Python 3..."
    
    # Détection du système d'exploitation
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if command -v brew &> /dev/null; then
            brew install python3
        else
            echo "❌ Homebrew n'est pas installé. Veuillez installer Python 3 manuellement depuis https://python.org"
            exit 1
        fi
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        if command -v apt-get &> /dev/null; then
            sudo apt-get update && sudo apt-get install -y python3 python3-pip
        elif command -v yum &> /dev/null; then
            sudo yum install -y python3 python3-pip
        else
            echo "❌ Gestionnaire de paquets non reconnu. Veuillez installer Python 3 manuellement."
            exit 1
        fi
    else
        echo "❌ Système d'exploitation non supporté. Veuillez installer Python 3 manuellement."
        exit 1
    fi
fi

# Vérification de la version Python
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "✅ Python $PYTHON_VERSION détecté"

# Vérification et installation de pip
echo "📋 Vérification de pip..."
if ! command -v pip3 &> /dev/null; then
    echo "💡 Installation de pip..."
    curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
    python3 get-pip.py
    rm get-pip.py
fi
echo "✅ pip3 détecté"

# Mise à jour de pip
echo "📦 Mise à jour de pip..."
python3 -m pip install --upgrade pip

# Installation des dépendances une par une pour éviter les erreurs
echo "📦 Installation des dépendances..."
echo ""

# Dépendances principales
echo "Installing streamlit..."
python3 -m pip install streamlit

echo "Installing pandas..."
python3 -m pip install pandas

echo "Installing numpy..."
python3 -m pip install numpy

echo "Installing scikit-learn..."
python3 -m pip install scikit-learn

echo "Installing plotly..."
python3 -m pip install plotly

echo "Installing folium..."
python3 -m pip install folium

echo "Installing streamlit-folium..."
python3 -m pip install streamlit-folium

echo "Installing requests..."
python3 -m pip install requests

echo "Installing scipy..."
python3 -m pip install scipy

echo "Installing joblib..."
python3 -m pip install joblib

# Création des dossiers nécessaires
echo "📁 Création des dossiers..."
mkdir -p data/spf data/insee data/meteo data/wikipedia data/google_trends data/processed data/alerts models

# Génération de données de démonstration si les données réelles ne sont pas disponibles
echo "📊 Préparation des données..."
if [ ! -f "data/processed/dataset_with_alerts_*.csv" ]; then
    echo "💡 Génération de données de démonstration..."
    python3 -c "
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

    # Créer des alertes de démonstration
    python3 -c "
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
fi

echo ""
echo "🎉 Installation terminée avec succès !"
echo ""
echo "🚀 Pour lancer l'application :"
echo "   python3 launch_app.py"
echo ""
echo "🌐 L'application sera accessible sur :"
echo "   http://localhost:8501"
echo ""
echo "📚 En cas de problème, consultez le README.md"
echo ""
echo "✅ Prêt à prédire les risques de grippe !"
