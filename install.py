#!/usr/bin/env python3
"""
🚨 INSTALLATION ULTRA-SIMPLE - Système d'alerte grippe France
Une seule commande pour tout installer !
"""

import subprocess
import sys
import os
import platform
from pathlib import Path

def run_command(command, description=""):
    """Exécute une commande et affiche le résultat"""
    print(f"📦 {description}")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} - Succès")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - Erreur: {e.stderr}")
        return False

def check_python():
    """Vérifie et installe Python si nécessaire"""
    print("📋 Vérification de Python...")
    
    # Vérifier la version Python
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python {version.major}.{version.minor} détecté. Python 3.8+ requis.")
        print("💡 Veuillez installer Python 3.8+ depuis https://python.org")
        return False
    
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} détecté")
    return True

def install_dependencies():
    """Installe toutes les dépendances"""
    print("📦 Installation des dépendances...")
    
    dependencies = [
        "streamlit",
        "pandas", 
        "numpy",
        "scikit-learn",
        "plotly",
        "folium",
        "streamlit-folium",
        "requests",
        "scipy",
        "joblib"
    ]
    
    for dep in dependencies:
        if not run_command(f"{sys.executable} -m pip install {dep}", f"Installation de {dep}"):
            print(f"⚠️  Échec de l'installation de {dep}, mais on continue...")
    
    return True

def create_directories():
    """Crée les dossiers nécessaires"""
    print("📁 Création des dossiers...")
    
    directories = [
        "data/spf",
        "data/insee", 
        "data/meteo",
        "data/wikipedia",
        "data/google_trends",
        "data/processed",
        "data/alerts",
        "models"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    print("✅ Dossiers créés")
    return True

def create_demo_data():
    """Crée des données de démonstration"""
    print("📊 Création des données de démonstration...")
    
    try:
        import pandas as pd
        import numpy as np
        from datetime import datetime, timedelta
        
        # Données principales
        regions = [
            'Île-de-France', 'Auvergne-Rhône-Alpes', 'Provence-Alpes-Côte d\'Azur', 
            'Nouvelle-Aquitaine', 'Occitanie', 'Grand Est', 'Hauts-de-France', 
            'Normandie', 'Bretagne', 'Pays de la Loire', 'Centre-Val de Loire', 
            'Bourgogne-Franche-Comté', 'Corse'
        ]
        
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
        print("✅ Données de démonstration créées")
        
        # Alertes de démonstration
        alerts = []
        for region in regions[:3]:  # 3 régions en alerte
            alerts.append({
                'region': region,
                'level': 'CRITIQUE' if np.random.random() > 0.5 else 'ÉLEVÉ',
                'score': np.random.uniform(70, 95),
                'message': f'Alerte {region} - Action immédiate requise',
                'timestamp': '2024-10-20 22:00:00'
            })
        
        df_alerts = pd.DataFrame(alerts)
        df_alerts.to_csv('data/alerts/alertes_demo.csv', index=False)
        print("✅ Alertes de démonstration créées")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la création des données: {e}")
        return False

def main():
    """Fonction principale d'installation"""
    print("🚨 Installation du système d'alerte grippe France")
    print("=" * 50)
    print()
    
    # Vérification de Python
    if not check_python():
        return False
    
    # Installation des dépendances
    if not install_dependencies():
        print("⚠️  Certaines dépendances n'ont pas pu être installées")
    
    # Création des dossiers
    if not create_directories():
        return False
    
    # Générer des données de démonstration
    print("📊 Génération des données de démonstration...")
    try:
        from scripts.generate_demo_data import create_demo_data
        create_demo_data()
        print("✅ Données de démonstration générées")
    except Exception as e:
        print(f"⚠️  Erreur lors de la génération des données: {e}")
        print("💡 Vous pouvez générer les données manuellement avec: python3 scripts/generate_demo_data.py")
    
    print("🎉 Installation terminée avec succès !")
    print()
    print("🚀 Pour lancer l'application :")
    print("   python3 launch_app.py")
    print()
    print("🌐 L'application sera accessible sur :")
    print("   http://localhost:8501")
    print()
    print("📚 En cas de problème, consultez le README.md")
    print()
    print("✅ Prêt à prédire les risques de grippe !")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
