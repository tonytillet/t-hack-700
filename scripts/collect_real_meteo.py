#!/usr/bin/env python3
"""
Script de collecte des VRAIES données météo
Utilise Open-Meteo API pour récupérer les données météo réelles
"""

import pandas as pd
import requests
import json
from datetime import datetime, timedelta
import time
import os
import warnings
warnings.filterwarnings('ignore')

class RealMeteoCollector:
    def __init__(self):
        """Initialise le collecteur météo"""
        self.base_url = "https://archive-api.open-meteo.com/v1/archive"
        
        # Coordonnées des régions françaises
        self.region_coords = {
            'Île-de-France': (48.8566, 2.3522),  # Paris
            'Auvergne-Rhône-Alpes': (45.7640, 4.8357),  # Lyon
            'Nouvelle-Aquitaine': (44.8378, -0.5792),  # Bordeaux
            'Occitanie': (43.6047, 1.4442),  # Toulouse
            'Hauts-de-France': (50.6292, 3.0573),  # Lille
            'Grand Est': (48.5734, 7.7521),  # Strasbourg
            'Pays de la Loire': (47.2184, -1.5536),  # Nantes
            'Bretagne': (48.2020, -2.9326),  # Rennes
            'Normandie': (49.4432, 1.0993),  # Rouen
            'Centre-Val de Loire': (47.7516, 1.6753),  # Orléans
            'Bourgogne-Franche-Comté': (47.3220, 5.0415),  # Dijon
            'Provence-Alpes-Côte d\'Azur': (43.2965, 5.3698),  # Marseille
            'Corse': (42.0396, 9.0129)  # Ajaccio
        }
    
    def get_weather_data(self, region_name, lat, lon, start_date, end_date):
        """Récupère les données météo pour une région"""
        try:
            print(f"  Collecte météo pour {region_name}...")
            
            # Formatage des dates
            start_str = start_date.strftime('%Y-%m-%d')
            end_str = end_date.strftime('%Y-%m-%d')
            
            # Paramètres de la requête
            params = {
                'latitude': lat,
                'longitude': lon,
                'start_date': start_str,
                'end_date': end_str,
                'daily': 'temperature_2m_mean,relative_humidity_2m_mean',
                'timezone': 'Europe/Paris'
            }
            
            # Requête API
            response = requests.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if 'daily' not in data:
                print(f"    ⚠️ Aucune donnée météo pour {region_name}")
                return None
            
            # Conversion en DataFrame
            df = pd.DataFrame({
                'date': pd.to_datetime(data['daily']['time']),
                'region': region_name,
                'temperature': data['daily']['temperature_2m_mean'],
                'humidity': data['daily']['relative_humidity_2m_mean']
            })
            
            print(f"    ✅ {len(df)} jours collectés")
            return df
            
        except Exception as e:
            print(f"    ❌ Erreur météo pour {region_name}: {str(e)}")
            return None
    
    def collect_all_data(self, start_date='2022-01-01', end_date=None):
        """Collecte toutes les données météo"""
        if end_date is None:
            end_date = datetime.now()
        else:
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
        
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        
        print(f"🌤️ Collecte météo RÉELLE du {start_date.strftime('%Y-%m-%d')} au {end_date.strftime('%Y-%m-%d')}")
        print(f"📊 {len(self.region_coords)} régions à collecter")
        
        all_data = []
        
        for region_name, (lat, lon) in self.region_coords.items():
            print(f"\n📍 Région: {region_name}")
            
            data = self.get_weather_data(region_name, lat, lon, start_date, end_date)
            
            if data is not None:
                all_data.append(data)
            
            # Pause pour éviter les limites de taux
            time.sleep(1)
        
        if all_data:
            # Fusion de toutes les données
            df = pd.concat(all_data, ignore_index=True)
            
            # Agrégation par semaine (lundi = début de semaine)
            df['week'] = df['date'].dt.to_period('W-MON')
            df_weekly = df.groupby(['week', 'region']).agg({
                'temperature': 'mean',
                'humidity': 'mean'
            }).reset_index()
            
            # Conversion de la période en date
            df_weekly['date'] = df_weekly['week'].dt.start_time
            df_weekly = df_weekly.drop('week', axis=1)
            
            print(f"\n✅ Collecte terminée: {len(df_weekly)} enregistrements")
            return df_weekly
        else:
            print("❌ Aucune donnée collectée")
            return None
    
    def save_data(self, df, filename=None):
        """Sauvegarde les données collectées"""
        if df is None:
            print("❌ Aucune donnée à sauvegarder")
            return
        
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"meteo_real_{timestamp}.csv"
        
        filepath = os.path.join('data', 'meteo', filename)
        df.to_csv(filepath, index=False)
        print(f"💾 Données sauvegardées: {filepath}")
        
        return filepath

def main():
    """Fonction principale"""
    print("🚀 Démarrage de la collecte météo RÉELLES")
    
    # Création du collecteur
    collector = RealMeteoCollector()
    
    # Collecte des données (2 dernières années)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=730)  # 2 ans
    
    df = collector.collect_all_data(
        start_date=start_date.strftime('%Y-%m-%d'),
        end_date=end_date.strftime('%Y-%m-%d')
    )
    
    if df is not None:
        # Sauvegarde
        collector.save_data(df, 'meteo_real_latest.csv')
        
        # Affichage des statistiques
        print(f"\n📈 Statistiques des données collectées:")
        print(f"   Période: {df['date'].min()} à {df['date'].max()}")
        print(f"   Régions: {df['region'].nunique()}")
        print(f"   Enregistrements: {len(df)}")
        print(f"\n📊 Aperçu des données:")
        print(df.head())
        
        # Statistiques météo
        print(f"\n🌡️ Température moyenne: {df['temperature'].mean():.1f}°C")
        print(f"💧 Humidité moyenne: {df['humidity'].mean():.1f}%")

if __name__ == "__main__":
    main()
