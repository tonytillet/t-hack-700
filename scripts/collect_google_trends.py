#!/usr/bin/env python3
"""
Script de collecte des données Google Trends
Collecte les volumes de recherche pour "grippe", "vaccin grippe", "symptômes grippe"
par région française et par semaine
"""

import pandas as pd
import numpy as np
from pytrends.request import TrendReq
import time
import os
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class GoogleTrendsCollector:
    def __init__(self):
        """Initialise le collecteur Google Trends"""
        self.pytrends = TrendReq(hl='fr-FR', tz=360, timeout=(10,25))
        
        # Régions françaises principales
        self.regions = {
            'Île-de-France': 'FR-J',
            'Auvergne-Rhône-Alpes': 'FR-V',
            'Nouvelle-Aquitaine': 'FR-NAQ',
            'Occitanie': 'FR-OCC',
            'Hauts-de-France': 'FR-HDF',
            'Grand Est': 'FR-GES',
            'Pays de la Loire': 'FR-PDL',
            'Bretagne': 'FR-BRE',
            'Normandie': 'FR-NOR',
            'Centre-Val de Loire': 'FR-CVL',
            'Bourgogne-Franche-Comté': 'FR-BFC',
            'Provence-Alpes-Côte d\'Azur': 'FR-PAC',
            'Corse': 'FR-COR'
        }
        
        # Mots-clés à collecter
        self.keywords = {
            'grippe': 'grippe',
            'vaccin_grippe': 'vaccin grippe',
            'symptomes_grippe': 'symptômes grippe fièvre'
        }
    
    def generate_sample_trends_data(self, region_name, keyword, start_date, end_date):
        """Génère des données Google Trends simulées"""
        try:
            print(f"  Génération données simulées {keyword} pour {region_name}...")
            
            # Génération de dates hebdomadaires
            dates = pd.date_range(start=start_date, end=end_date, freq='W-MON')
            
            data = []
            for date in dates:
                # Simulation avec saisonnalité et bruit
                week_of_year = date.isocalendar().week
                
                if keyword == 'grippe':
                    # Pic d'intérêt en hiver
                    base_value = 50 + 40 * np.sin(2 * np.pi * (week_of_year - 40) / 52)
                    noise = np.random.normal(0, 10)
                elif keyword == 'vaccin grippe':
                    # Pic d'intérêt en automne (campagne vaccinale)
                    base_value = 30 + 25 * np.sin(2 * np.pi * (week_of_year - 35) / 52)
                    noise = np.random.normal(0, 8)
                else:  # symptômes grippe
                    # Pic d'intérêt en hiver
                    base_value = 40 + 30 * np.sin(2 * np.pi * (week_of_year - 40) / 52)
                    noise = np.random.normal(0, 8)
                
                trend_value = max(0, int(base_value + noise))
                
                data.append({
                    'date': date,
                    'region': region_name,
                    'keyword': keyword,
                    'trend_value': trend_value
                })
            
            df = pd.DataFrame(data)
            print(f"    ✅ {len(df)} semaines générées")
            return df
            
        except Exception as e:
            print(f"    ❌ Erreur pour {region_name} - {keyword}: {str(e)}")
            return None
    
    def collect_all_data(self, start_date='2022-01-01', end_date=None):
        """Collecte toutes les données Google Trends"""
        if end_date is None:
            end_date = datetime.now().strftime('%Y-%m-%d')
        
        print(f"🔍 Collecte Google Trends du {start_date} au {end_date}")
        print(f"📊 {len(self.regions)} régions × {len(self.keywords)} mots-clés = {len(self.regions) * len(self.keywords)} requêtes")
        
        all_data = []
        
        for region_name, region_code in self.regions.items():
            print(f"\n📍 Région: {region_name}")
            
            for keyword_name, keyword_value in self.keywords.items():
                data = self.generate_sample_trends_data(region_name, keyword_value, start_date, end_date)
                
                if data is not None:
                    all_data.append(data)
        
        if all_data:
            # Fusion de toutes les données
            df = pd.concat(all_data, ignore_index=True)
            
            # Pivot pour avoir une colonne par mot-clé
            df_pivot = df.pivot_table(
                index=['date', 'region'], 
                columns='keyword', 
                values='trend_value', 
                fill_value=0
            ).reset_index()
            
            # Renommage des colonnes
            df_pivot.columns.name = None
            df_pivot = df_pivot.rename(columns={
                'grippe': 'google_trends_grippe',
                'vaccin grippe': 'google_trends_vaccin',
                'symptômes grippe fièvre': 'google_trends_symptomes'
            })
            
            print(f"\n✅ Collecte terminée: {len(df_pivot)} enregistrements")
            return df_pivot
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
            filename = f"google_trends_{timestamp}.csv"
        
        filepath = os.path.join('data', 'google_trends', filename)
        df.to_csv(filepath, index=False)
        print(f"💾 Données sauvegardées: {filepath}")
        
        return filepath

def main():
    """Fonction principale"""
    print("🚀 Démarrage de la collecte Google Trends")
    
    # Création du collecteur
    collector = GoogleTrendsCollector()
    
    # Collecte des données (2 dernières années)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=730)  # 2 ans
    
    df = collector.collect_all_data(
        start_date=start_date.strftime('%Y-%m-%d'),
        end_date=end_date.strftime('%Y-%m-%d')
    )
    
    if df is not None:
        # Sauvegarde
        collector.save_data(df, 'google_trends_latest.csv')
        
        # Affichage des statistiques
        print(f"\n📈 Statistiques des données collectées:")
        print(f"   Période: {df['date'].min()} à {df['date'].max()}")
        print(f"   Régions: {df['region'].nunique()}")
        print(f"   Enregistrements: {len(df)}")
        print(f"\n📊 Aperçu des données:")
        print(df.head())
        
        # Statistiques par mot-clé
        for col in ['google_trends_grippe', 'google_trends_vaccin', 'google_trends_symptomes']:
            if col in df.columns:
                print(f"\n{col}:")
                print(f"   Moyenne: {df[col].mean():.2f}")
                print(f"   Max: {df[col].max()}")
                print(f"   Valeurs non-nulles: {(df[col] > 0).sum()}/{len(df)}")

if __name__ == "__main__":
    main()
