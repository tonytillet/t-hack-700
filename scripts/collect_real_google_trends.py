#!/usr/bin/env python3
"""
Script de collecte des VRAIES données Google Trends
Utilise pytrends pour récupérer les données réelles
"""

import pandas as pd
import numpy as np
from pytrends.request import TrendReq
import time
import os
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class RealGoogleTrendsCollector:
    def __init__(self):
        """Initialise le collecteur Google Trends réel"""
        self.pytrends = TrendReq(hl='fr-FR', tz=360, timeout=(10,25))
        
        # Régions françaises avec codes Google Trends
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
        self.keywords = ['grippe', 'vaccin grippe', 'symptômes grippe']
    
    def collect_region_keyword(self, region_name, region_code, keyword, start_date, end_date):
        """Collecte les données pour une région et un mot-clé spécifiques"""
        try:
            print(f"  Collecte {keyword} pour {region_name}...")
            
            # Configuration de la requête
            self.pytrends.build_payload(
                [keyword], 
                cat=0, 
                timeframe=f'{start_date} {end_date}',
                geo=region_code,
                gprop=''
            )
            
            # Récupération des données
            data = self.pytrends.interest_over_time()
            
            if data.empty:
                print(f"    ⚠️ Aucune donnée pour {region_name} - {keyword}")
                return None
            
            # Nettoyage des données
            data = data.reset_index()
            data['region'] = region_name
            data['keyword'] = keyword
            data['date'] = pd.to_datetime(data['date'])
            
            # Renommage de la colonne de valeurs
            value_col = [col for col in data.columns if col not in ['date', 'region', 'keyword', 'isPartial']][0]
            data = data.rename(columns={value_col: 'trend_value'})
            
            # Suppression des colonnes inutiles
            data = data[['date', 'region', 'keyword', 'trend_value']].copy()
            
            print(f"    ✅ {len(data)} semaines collectées")
            return data
            
        except Exception as e:
            print(f"    ❌ Erreur pour {region_name} - {keyword}: {str(e)}")
            return None
    
    def collect_all_data(self, start_date='2022-01-01', end_date=None):
        """Collecte toutes les données Google Trends réelles"""
        if end_date is None:
            end_date = datetime.now().strftime('%Y-%m-%d')
        
        print(f"🔍 Collecte Google Trends RÉELLES du {start_date} au {end_date}")
        print(f"📊 {len(self.regions)} régions × {len(self.keywords)} mots-clés = {len(self.regions) * len(self.keywords)} requêtes")
        print("⚠️  Attention: Google Trends a des limites de taux, la collecte peut prendre du temps...")
        
        all_data = []
        total_requests = len(self.regions) * len(self.keywords)
        current_request = 0
        
        for region_name, region_code in self.regions.items():
            print(f"\n📍 Région: {region_name}")
            
            for keyword in self.keywords:
                current_request += 1
                print(f"  [{current_request}/{total_requests}]")
                
                data = self.collect_region_keyword(region_name, region_code, keyword, start_date, end_date)
                
                if data is not None:
                    all_data.append(data)
                
                # Pause pour éviter les limites de taux (plus long pour les vraies données)
                print(f"    ⏳ Pause 5 secondes...")
                time.sleep(5)
        
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
                'symptômes grippe': 'google_trends_symptomes'
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
            filename = f"google_trends_real_{timestamp}.csv"
        
        filepath = os.path.join('data', 'google_trends', filename)
        df.to_csv(filepath, index=False)
        print(f"💾 Données sauvegardées: {filepath}")
        
        return filepath

def main():
    """Fonction principale"""
    print("🚀 Démarrage de la collecte Google Trends RÉELLES")
    
    # Création du collecteur
    collector = RealGoogleTrendsCollector()
    
    # Collecte des données (2 dernières années)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=730)  # 2 ans
    
    df = collector.collect_all_data(
        start_date=start_date.strftime('%Y-%m-%d'),
        end_date=end_date.strftime('%Y-%m-%d')
    )
    
    if df is not None:
        # Sauvegarde
        collector.save_data(df, 'google_trends_real_latest.csv')
        
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
