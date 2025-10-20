#!/usr/bin/env python3
"""
Collecte des données météorologiques réelles
Température, humidité, pression par région
"""

import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import json
import time

# Coordonnées des principales villes françaises par région
REGION_COORDINATES = {
    'Île-de-France': {'lat': 48.8566, 'lon': 2.3522},
    'Auvergne-Rhône-Alpes': {'lat': 45.7640, 'lon': 4.8357},
    'Provence-Alpes-Côte d\'Azur': {'lat': 43.2965, 'lon': 5.3698},
    'Nouvelle-Aquitaine': {'lat': 44.8378, 'lon': -0.5792},
    'Occitanie': {'lat': 43.6047, 'lon': 1.4442},
    'Grand Est': {'lat': 48.5734, 'lon': 7.7521},
    'Hauts-de-France': {'lat': 50.6292, 'lon': 3.0573},
    'Normandie': {'lat': 49.1829, 'lon': -0.3707},
    'Bretagne': {'lat': 48.2020, 'lon': -2.9326},
    'Pays de la Loire': {'lat': 47.4739, 'lon': -0.5517},
    'Centre-Val de Loire': {'lat': 47.7516, 'lon': 1.6751},
    'Bourgogne-Franche-Comté': {'lat': 47.3220, 'lon': 5.0415},
    'Corse': {'lat': 42.0396, 'lon': 9.0129}
}

def collect_meteo_data_region(region, lat, lon, start_date, end_date):
    """Collecte les données météo pour une région"""
    print(f"🌡️ Collecte météo pour {region}...")
    
    # URL de l'API Open-Meteo
    url = "https://archive-api.open-meteo.com/v1/archive"
    
    params = {
        'latitude': lat,
        'longitude': lon,
        'start_date': start_date,
        'end_date': end_date,
        'daily': 'temperature_2m_mean,relative_humidity_2m_mean,precipitation_sum,wind_speed_10m_mean,pressure_msl_mean',
        'timezone': 'Europe/Paris'
    }
    
    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        
        # Conversion en DataFrame
        df = pd.DataFrame(data['daily'])
        df['date'] = pd.to_datetime(df['date'])
        df['region'] = region
        df['latitude'] = lat
        df['longitude'] = lon
        
        # Renommage des colonnes
        df = df.rename(columns={
            'temperature_2m_mean': 'temperature',
            'relative_humidity_2m_mean': 'humidity',
            'precipitation_sum': 'precipitation',
            'wind_speed_10m_mean': 'wind_speed',
            'pressure_msl_mean': 'pressure'
        })
        
        return df
        
    except Exception as e:
        print(f"❌ Erreur météo {region}: {e}")
        return None

def collect_all_meteo_data():
    """Collecte les données météo pour toutes les régions"""
    print("🌤️ Collecte des données météorologiques...")
    
    # Période de collecte (2 dernières années)
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=730)).strftime('%Y-%m-%d')
    
    all_data = []
    
    for region, coords in REGION_COORDINATES.items():
        df = collect_meteo_data_region(
            region, 
            coords['lat'], 
            coords['lon'], 
            start_date, 
            end_date
        )
        
        if df is not None:
            all_data.append(df)
        
        # Pause entre les requêtes
        time.sleep(1)
    
    if all_data:
        # Fusion de toutes les données
        combined_df = pd.concat(all_data, ignore_index=True)
        
        # Sauvegarde
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'data/meteo/meteo_real_{timestamp}.csv'
        combined_df.to_csv(filename, index=False)
        
        print(f"✅ Données météo collectées: {len(combined_df)} enregistrements")
        return filename
    else:
        print("❌ Aucune donnée météo collectée")
        return None

def collect_air_quality_data():
    """Collecte les données de qualité de l'air"""
    print("🌬️ Collecte des données de qualité de l'air...")
    
    # URL de l'API Air Quality
    url = "https://air-quality-api.open-meteo.com/v1/air-quality"
    
    # Coordonnées de Paris (représentatif de l'Île-de-France)
    params = {
        'latitude': 48.8566,
        'longitude': 2.3522,
        'start_date': (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d'),
        'end_date': datetime.now().strftime('%Y-%m-%d'),
        'daily': 'pm10,pm2_5,ozone,nitrogen_dioxide,sulphur_dioxide',
        'timezone': 'Europe/Paris'
    }
    
    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        
        # Conversion en DataFrame
        df = pd.DataFrame(data['daily'])
        df['date'] = pd.to_datetime(df['date'])
        df['region'] = 'Île-de-France'
        
        # Sauvegarde
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'data/meteo/air_quality_real_{timestamp}.csv'
        df.to_csv(filename, index=False)
        
        print(f"✅ Données qualité air collectées: {len(df)} enregistrements")
        return filename
        
    except Exception as e:
        print(f"❌ Erreur qualité air: {e}")
        return None

def collect_weather_alerts():
    """Collecte les alertes météorologiques"""
    print("⚠️ Collecte des alertes météorologiques...")
    
    # URL de l'API Météo France
    url = "https://public-api.meteofrance.fr/public/DPVigilance/v1/cartevigilance"
    
    try:
        headers = {
            'Accept': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        
        # Conversion en DataFrame
        alerts = []
        for dept, info in data.items():
            if isinstance(info, dict) and 'vigilance' in info:
                alerts.append({
                    'departement': dept,
                    'vigilance': info['vigilance'],
                    'date': datetime.now().strftime('%Y-%m-%d'),
                    'region': info.get('region', 'Unknown')
                })
        
        df = pd.DataFrame(alerts)
        
        # Sauvegarde
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'data/meteo/weather_alerts_real_{timestamp}.csv'
        df.to_csv(filename, index=False)
        
        print(f"✅ Alertes météo collectées: {len(df)} enregistrements")
        return filename
        
    except Exception as e:
        print(f"❌ Erreur alertes météo: {e}")
        return None

def main():
    """Fonction principale de collecte"""
    print("🚀 COLLECTE DES DONNÉES MÉTÉOROLOGIQUES RÉELLES")
    print("=" * 60)
    
    # Création du dossier
    os.makedirs('data/meteo', exist_ok=True)
    
    # Collecte des données
    files = []
    
    # 1. Données météo principales
    meteo_file = collect_all_meteo_data()
    if meteo_file:
        files.append(meteo_file)
    
    time.sleep(2)
    
    # 2. Qualité de l'air
    air_quality_file = collect_air_quality_data()
    if air_quality_file:
        files.append(air_quality_file)
    
    time.sleep(2)
    
    # 3. Alertes météo
    alerts_file = collect_weather_alerts()
    if alerts_file:
        files.append(alerts_file)
    
    # Résumé
    print(f"\n✅ COLLECTE TERMINÉE")
    print(f"📁 Fichiers créés: {len(files)}")
    for file in files:
        print(f"  - {file}")
    
    # Sauvegarde de la configuration
    config = {
        'collection_date': datetime.now().isoformat(),
        'files': files,
        'source': 'Open-Meteo, Météo France',
        'data_type': 'real'
    }
    
    with open('data/meteo/collection_config.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"\n📋 Configuration sauvegardée: data/meteo/collection_config.json")

if __name__ == "__main__":
    main()
