#!/usr/bin/env python3
"""
Script de collecte des données SPF (Santé Publique France)
Collecte les données d'urgences, vaccination, IAS et sentinelles
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

class SPFDataCollector:
    def __init__(self):
        """Initialise le collecteur SPF"""
        self.base_urls = {
            'urgences': 'https://odisse.santepubliquefrance.fr/explore/dataset/grippe-passages-aux-urgences-et-actes-sos-medecins-france/download/',
            'sentinelles': 'https://www.sentiweb.fr/france/fr/?page=table',
            'vaccination': 'https://www.data.gouv.fr/fr/datasets/couverture-vaccinale-contre-la-grippe-saisonniere/',
            'ias': 'https://www.data.gouv.fr/fr/datasets/indicateurs-avances-sanitaires-ias/'
        }
        
        # Régions françaises
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
    
    def generate_sample_urgences_data(self, start_date, end_date):
        """Génère des données d'urgences simulées (en attendant l'accès aux vraies données)"""
        print("  Génération de données d'urgences simulées...")
        
        # Génération de dates hebdomadaires
        dates = pd.date_range(start=start_date, end=end_date, freq='W-MON')
        
        data = []
        for region_name, region_code in self.regions.items():
            for date in dates:
                # Simulation avec saisonnalité et bruit
                week_of_year = date.isocalendar().week
                base_value = 50 + 30 * np.sin(2 * np.pi * (week_of_year - 40) / 52)  # Pic en hiver
                noise = np.random.normal(0, 10)
                urgences = max(0, int(base_value + noise))
                
                data.append({
                    'date': date,
                    'region': region_name,
                    'region_code': region_code,
                    'urgences_grippe': urgences
                })
        
        df = pd.DataFrame(data)
        print(f"    ✅ {len(df)} enregistrements générés")
        return df
    
    def generate_sample_sentinelles_data(self, start_date, end_date):
        """Génère des données sentinelles simulées"""
        print("  Génération de données sentinelles simulées...")
        
        dates = pd.date_range(start=start_date, end=end_date, freq='W-MON')
        
        data = []
        for region_name, region_code in self.regions.items():
            for date in dates:
                # Simulation avec saisonnalité
                week_of_year = date.isocalendar().week
                base_value = 20 + 15 * np.sin(2 * np.pi * (week_of_year - 40) / 52)
                noise = np.random.normal(0, 5)
                cas_sentinelles = max(0, int(base_value + noise))
                
                data.append({
                    'date': date,
                    'region': region_name,
                    'region_code': region_code,
                    'cas_sentinelles': cas_sentinelles
                })
        
        df = pd.DataFrame(data)
        print(f"    ✅ {len(df)} enregistrements générés")
        return df
    
    def generate_sample_vaccination_data(self, start_date, end_date):
        """Génère des données de vaccination simulées"""
        print("  Génération de données de vaccination simulées...")
        
        # Données annuelles (la vaccination se fait principalement en automne)
        years = list(range(start_date.year, end_date.year + 1))
        
        data = []
        for region_name, region_code in self.regions.items():
            for year in years:
                # Simulation avec variation régionale
                base_vaccination = 45 + np.random.normal(0, 10)  # Moyenne 45% avec variation
                base_vaccination = max(20, min(80, base_vaccination))  # Bornes réalistes
                
                data.append({
                    'year': year,
                    'region': region_name,
                    'region_code': region_code,
                    'taux_vaccination': round(base_vaccination, 1)
                })
        
        df = pd.DataFrame(data)
        print(f"    ✅ {len(df)} enregistrements générés")
        return df
    
    def generate_sample_ias_data(self, start_date, end_date):
        """Génère des données IAS simulées"""
        print("  Génération de données IAS simulées...")
        
        dates = pd.date_range(start=start_date, end=end_date, freq='W-MON')
        
        data = []
        for region_name, region_code in self.regions.items():
            for date in dates:
                # Simulation avec saisonnalité
                week_of_year = date.isocalendar().week
                base_value = 0.5 + 0.3 * np.sin(2 * np.pi * (week_of_year - 40) / 52)
                noise = np.random.normal(0, 0.1)
                ias = max(0, min(2, base_value + noise))  # IAS entre 0 et 2
                
                data.append({
                    'date': date,
                    'region': region_name,
                    'region_code': region_code,
                    'ias_syndrome_grippal': round(ias, 2)
                })
        
        df = pd.DataFrame(data)
        print(f"    ✅ {len(df)} enregistrements générés")
        return df
    
    def collect_all_data(self, start_date='2022-01-01', end_date=None):
        """Collecte toutes les données SPF"""
        if end_date is None:
            end_date = datetime.now()
        else:
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
        
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        
        print(f"🔍 Collecte données SPF du {start_date.strftime('%Y-%m-%d')} au {end_date.strftime('%Y-%m-%d')}")
        print("⚠️  Note: Utilisation de données simulées (accès API SPF à configurer)")
        
        all_data = {}
        
        # Collecte urgences
        print("\n🏥 Collecte données urgences...")
        urgences_df = self.generate_sample_urgences_data(start_date, end_date)
        all_data['urgences'] = urgences_df
        
        # Collecte sentinelles
        print("\n🔬 Collecte données sentinelles...")
        sentinelles_df = self.generate_sample_sentinelles_data(start_date, end_date)
        all_data['sentinelles'] = sentinelles_df
        
        # Collecte vaccination
        print("\n💉 Collecte données vaccination...")
        vaccination_df = self.generate_sample_vaccination_data(start_date, end_date)
        all_data['vaccination'] = vaccination_df
        
        # Collecte IAS
        print("\n📊 Collecte données IAS...")
        ias_df = self.generate_sample_ias_data(start_date, end_date)
        all_data['ias'] = ias_df
        
        print(f"\n✅ Collecte terminée: {len(all_data)} types de données")
        return all_data
    
    def save_data(self, all_data, prefix='spf'):
        """Sauvegarde toutes les données collectées"""
        if not all_data:
            print("❌ Aucune donnée à sauvegarder")
            return
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        for data_type, df in all_data.items():
            filename = f"{prefix}_{data_type}_{timestamp}.csv"
            filepath = os.path.join('data', 'spf', filename)
            df.to_csv(filepath, index=False)
            print(f"💾 {data_type} sauvegardé: {filepath}")
        
        return True

def main():
    """Fonction principale"""
    print("🚀 Démarrage de la collecte données SPF")
    
    # Import numpy pour les simulations
    import numpy as np
    
    # Création du collecteur
    collector = SPFDataCollector()
    
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
            elif 'year' in df.columns:
                print(f"   Années: {df['year'].min()} à {df['year'].max()}")
            print(f"   Régions: {df['region'].nunique()}")
            print(f"   Aperçu:")
            print(df.head(3))

if __name__ == "__main__":
    main()
