#!/usr/bin/env python3
"""
Script de collecte des données contextuelles
Collecte les données INSEE (population) et météo (température, humidité)
"""

import pandas as pd
import numpy as np
import requests
import json
from datetime import datetime, timedelta
import time
import os
import warnings
warnings.filterwarnings('ignore')

class ContextDataCollector:
    def __init__(self):
        """Initialise le collecteur de données contextuelles"""
        self.regions = {
            'Île-de-France': '11',
            'Auvergne-Rhône-Alpes': '84',
            'Nouvelle-Aquitaine': '75',
            'Occitanie': '76',
            'Hauts-de-France': '32',
            'Grand Est': '44',
            'Pays de la Loire': '52',
            'Bretagne': '53',
            'Normandie': '28',
            'Centre-Val de Loire': '24',
            'Bourgogne-Franche-Comté': '27',
            'Provence-Alpes-Côte d\'Azur': '93',
            'Corse': '94'
        }
        
        # Coordonnées approximatives des régions pour la météo
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
    
    def generate_sample_population_data(self):
        """Génère des données de population simulées (INSEE)"""
        print("  Génération de données population INSEE...")
        
        data = []
        for region_name, region_code in self.regions.items():
            # Simulation avec variation régionale réaliste
            base_pop = {
                'Île-de-France': 12000000,
                'Auvergne-Rhône-Alpes': 8000000,
                'Nouvelle-Aquitaine': 6000000,
                'Occitanie': 6000000,
                'Hauts-de-France': 6000000,
                'Grand Est': 5500000,
                'Pays de la Loire': 3800000,
                'Bretagne': 3300000,
                'Normandie': 3300000,
                'Centre-Val de Loire': 2600000,
                'Bourgogne-Franche-Comté': 2800000,
                'Provence-Alpes-Côte d\'Azur': 5000000,
                'Corse': 340000
            }
            
            population = base_pop.get(region_name, 2000000)
            
            # Pourcentage 65+ (variation régionale)
            pct_65_plus = {
                'Île-de-France': 16.5,
                'Auvergne-Rhône-Alpes': 19.2,
                'Nouvelle-Aquitaine': 22.1,
                'Occitanie': 21.8,
                'Hauts-de-France': 19.5,
                'Grand Est': 20.3,
                'Pays de la Loire': 21.4,
                'Bretagne': 22.7,
                'Normandie': 21.9,
                'Centre-Val de Loire': 22.2,
                'Bourgogne-Franche-Comté': 22.5,
                'Provence-Alpes-Côte d\'Azur': 23.1,
                'Corse': 20.8
            }
            
            data.append({
                'region': region_name,
                'region_code': region_code,
                'population_totale': population,
                'pct_65_plus': pct_65_plus.get(region_name, 20.0)
            })
        
        df = pd.DataFrame(data)
        print(f"    ✅ {len(df)} régions générées")
        return df
    
    def get_weather_data(self, lat, lon, start_date, end_date):
        """Récupère les données météo via Open-Meteo API"""
        try:
            # Formatage des dates
            start_str = start_date.strftime('%Y-%m-%d')
            end_str = end_date.strftime('%Y-%m-%d')
            
            url = f"https://archive-api.open-meteo.com/v1/archive"
            params = {
                'latitude': lat,
                'longitude': lon,
                'start_date': start_str,
                'end_date': end_str,
                'daily': 'temperature_2m_mean,relative_humidity_2m_mean',
                'timezone': 'Europe/Paris'
            }
            
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if 'daily' not in data:
                return None
            
            # Conversion en DataFrame
            df = pd.DataFrame({
                'date': pd.to_datetime(data['daily']['time']),
                'temperature': data['daily']['temperature_2m_mean'],
                'humidity': data['daily']['relative_humidity_2m_mean']
            })
            
            return df
            
        except Exception as e:
            print(f"    ❌ Erreur météo pour {lat}, {lon}: {str(e)}")
            return None
    
    def generate_sample_weather_data(self, start_date, end_date):
        """Génère des données météo simulées"""
        print("  Génération de données météo simulées...")
        
        dates = pd.date_range(start=start_date, end=end_date, freq='D')
        
        all_weather = []
        for region_name, (lat, lon) in self.region_coords.items():
            region_data = []
            
            for date in dates:
                # Simulation avec saisonnalité
                day_of_year = date.timetuple().tm_yday
                
                # Température avec saisonnalité
                base_temp = 15 + 10 * np.sin(2 * np.pi * (day_of_year - 80) / 365)
                temp_noise = np.random.normal(0, 3)
                temperature = base_temp + temp_noise
                
                # Humidité (inverse de la température)
                base_humidity = 70 - (temperature - 15) * 2
                humidity_noise = np.random.normal(0, 5)
                humidity = max(30, min(95, base_humidity + humidity_noise))
                
                region_data.append({
                    'date': date,
                    'region': region_name,
                    'temperature': round(temperature, 1),
                    'humidity': round(humidity, 1)
                })
            
            all_weather.extend(region_data)
        
        df = pd.DataFrame(all_weather)
        
        # Agrégation par semaine
        df['week'] = df['date'].dt.to_period('W-MON')
        df_weekly = df.groupby(['week', 'region']).agg({
            'temperature': 'mean',
            'humidity': 'mean'
        }).reset_index()
        
        df_weekly['date'] = df_weekly['week'].dt.start_time
        df_weekly = df_weekly.drop('week', axis=1)
        
        print(f"    ✅ {len(df_weekly)} enregistrements générés")
        return df_weekly
    
    def collect_all_data(self, start_date='2022-01-01', end_date=None):
        """Collecte toutes les données contextuelles"""
        if end_date is None:
            end_date = datetime.now()
        else:
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
        
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        
        print(f"🔍 Collecte données contextuelles du {start_date.strftime('%Y-%m-%d')} au {end_date.strftime('%Y-%m-%d')}")
        
        all_data = {}
        
        # Collecte population
        print("\n👥 Collecte données population...")
        population_df = self.generate_sample_population_data()
        all_data['population'] = population_df
        
        # Collecte météo
        print("\n🌤️ Collecte données météo...")
        weather_df = self.generate_sample_weather_data(start_date, end_date)
        all_data['weather'] = weather_df
        
        print(f"\n✅ Collecte terminée: {len(all_data)} types de données")
        return all_data
    
    def save_data(self, all_data, prefix='context'):
        """Sauvegarde toutes les données collectées"""
        if not all_data:
            print("❌ Aucune donnée à sauvegarder")
            return
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        for data_type, df in all_data.items():
            filename = f"{prefix}_{data_type}_{timestamp}.csv"
            filepath = os.path.join('data', 'context', filename)
            df.to_csv(filepath, index=False)
            print(f"💾 {data_type} sauvegardé: {filepath}")
        
        return True

def main():
    """Fonction principale"""
    print("🚀 Démarrage de la collecte données contextuelles")
    
    # Import numpy pour les simulations
    import numpy as np
    
    # Création du collecteur
    collector = ContextDataCollector()
    
    # Collecte des données (2 dernières années)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=730)  # 2 ans
    
    all_data = collector.collect_all_data(
        start_date=start_date.strftime('%Y-%m-%d'),
        end_date=end_date.strftime('%Y-%m-%d')
    )
    
    if all_data:
        # Sauvegarde
        collector.save_data(all_data)
        
        # Affichage des statistiques
        print(f"\n📈 Statistiques des données collectées:")
        for data_type, df in all_data.items():
            print(f"\n{data_type.upper()}:")
            print(f"   Enregistrements: {len(df)}")
            if 'date' in df.columns:
                print(f"   Période: {df['date'].min()} à {df['date'].max()}")
            print(f"   Régions: {df['region'].nunique()}")
            print(f"   Aperçu:")
            print(df.head(3))

if __name__ == "__main__":
    main()
