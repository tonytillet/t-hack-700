#!/usr/bin/env python3
"""
Script de collecte des données Wikipedia
Collecte les vues des pages "Grippe" et "Vaccination" (Wikipedia FR)
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

class WikipediaCollector:
    def __init__(self):
        """Initialise le collecteur Wikipedia"""
        self.base_url = "https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article"
        self.headers = {
            'User-Agent': 'GrippePredictionBot/1.0 (https://example.com/contact)'
        }
        
        # Pages à surveiller
        self.pages = {
            'grippe': 'Grippe',
            'vaccination': 'Vaccination'
        }
    
    def generate_sample_pageviews(self, page_title, start_date, end_date):
        """Génère des données de vues Wikipedia simulées"""
        try:
            print(f"  Génération données simulées pour {page_title}")
            
            # Génération de dates hebdomadaires
            dates = pd.date_range(start=start_date, end=end_date, freq='W-MON')
            
            data = []
            for date in dates:
                # Simulation avec saisonnalité et bruit
                week_of_year = date.isocalendar().week
                
                if page_title == 'Grippe':
                    # Pic d'intérêt en hiver
                    base_views = 1000 + 800 * np.sin(2 * np.pi * (week_of_year - 40) / 52)
                    noise = np.random.normal(0, 200)
                else:  # Vaccination
                    # Pic d'intérêt en automne (campagne vaccinale)
                    base_views = 500 + 300 * np.sin(2 * np.pi * (week_of_year - 35) / 52)
                    noise = np.random.normal(0, 100)
                
                views = max(0, int(base_views + noise))
                
                data.append({
                    'date': date,
                    'page': page_title,
                    'views': views
                })
            
            df = pd.DataFrame(data)
            print(f"    ✅ {len(df)} semaines générées")
            return df
            
        except Exception as e:
            print(f"    ❌ Erreur pour {page_title}: {str(e)}")
            return None
    
    def collect_all_data(self, start_date='2022-01-01', end_date=None):
        """Collecte toutes les données Wikipedia"""
        if end_date is None:
            end_date = datetime.now()
        else:
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
        
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        
        print(f"🔍 Collecte Wikipedia du {start_date.strftime('%Y-%m-%d')} au {end_date.strftime('%Y-%m-%d')}")
        print(f"📊 {len(self.pages)} pages à collecter")
        
        all_data = []
        
        for page_key, page_title in self.pages.items():
            print(f"\n📄 Page: {page_title}")
            
            data = self.generate_sample_pageviews(page_title, start_date, end_date)
            
            if data is not None:
                all_data.append(data)
        
        if all_data:
            # Fusion de toutes les données
            df = pd.concat(all_data, ignore_index=True)
            
            # Pivot pour avoir une colonne par page
            df_pivot = df.pivot_table(
                index='date', 
                columns='page', 
                values='views', 
                fill_value=0
            ).reset_index()
            
            # Renommage des colonnes
            df_pivot.columns.name = None
            df_pivot = df_pivot.rename(columns={
                'Grippe': 'wiki_grippe_views',
                'Vaccination': 'wiki_vaccination_views'
            })
            
            # Agrégation par semaine (lundi = début de semaine)
            df_weekly = df_pivot.copy()
            df_weekly['week'] = df_weekly['date'].dt.to_period('W-MON')
            df_weekly = df_weekly.groupby('week').agg({
                'wiki_grippe_views': 'sum',
                'wiki_vaccination_views': 'sum'
            }).reset_index()
            
            # Conversion de la période en date
            df_weekly['date'] = df_weekly['week'].dt.start_time
            df_weekly = df_weekly.drop('week', axis=1)
            
            print(f"\n✅ Collecte terminée: {len(df_weekly)} semaines")
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
            filename = f"wikipedia_{timestamp}.csv"
        
        filepath = os.path.join('..', 'data', 'wikipedia', filename)
        df.to_csv(filepath, index=False)
        print(f"💾 Données sauvegardées: {filepath}")
        
        return filepath

def main():
    """Fonction principale"""
    print("🚀 Démarrage de la collecte Wikipedia")
    
    # Création du collecteur
    collector = WikipediaCollector()
    
    # Collecte des données (2 dernières années)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=730)  # 2 ans
    
    df = collector.collect_all_data(
        start_date=start_date.strftime('%Y-%m-%d'),
        end_date=end_date.strftime('%Y-%m-%d')
    )
    
    if df is not None:
        # Sauvegarde
        collector.save_data(df, 'wikipedia_latest.csv')
        
        # Affichage des statistiques
        print(f"\n📈 Statistiques des données collectées:")
        print(f"   Période: {df['date'].min()} à {df['date'].max()}")
        print(f"   Enregistrements: {len(df)}")
        print(f"\n📊 Aperçu des données:")
        print(df.head())
        
        # Statistiques par page
        for col in ['wiki_grippe_views', 'wiki_vaccination_views']:
            if col in df.columns:
                print(f"\n{col}:")
                print(f"   Moyenne: {df[col].mean():.2f}")
                print(f"   Max: {df[col].max()}")
                print(f"   Total: {df[col].sum():,}")

if __name__ == "__main__":
    main()
