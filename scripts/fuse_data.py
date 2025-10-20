#!/usr/bin/env python3
"""
Script de fusion et validation des données collectées
Fusionne les 13 sources de données en un dataset unifié pour le modèle Random Forest
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import warnings
warnings.filterwarnings('ignore')

class DataFusion:
    def __init__(self):
        """Initialise le système de fusion de données"""
        self.data_dir = 'data'
        self.output_dir = 'data/processed'
        
        # Mapping des régions pour uniformiser
        self.region_mapping = {
            'Île-de-France': 'Île-de-France',
            'Auvergne-Rhône-Alpes': 'Auvergne-Rhône-Alpes',
            'Nouvelle-Aquitaine': 'Nouvelle-Aquitaine',
            'Occitanie': 'Occitanie',
            'Hauts-de-France': 'Hauts-de-France',
            'Grand Est': 'Grand Est',
            'Pays de la Loire': 'Pays de la Loire',
            'Bretagne': 'Bretagne',
            'Normandie': 'Normandie',
            'Centre-Val de Loire': 'Centre-Val de Loire',
            'Bourgogne-Franche-Comté': 'Bourgogne-Franche-Comté',
            'Provence-Alpes-Côte d\'Azur': 'Provence-Alpes-Côte d\'Azur',
            'Corse': 'Corse'
        }
    
    def load_latest_files(self):
        """Charge les derniers fichiers de données collectées"""
        print("📂 Chargement des données collectées...")
        
        data = {}
        
        # 1. Google Trends
        gt_files = [f for f in os.listdir(f'{self.data_dir}/google_trends') if f.endswith('.csv')]
        if gt_files:
            latest_gt = sorted(gt_files)[-1]
            data['google_trends'] = pd.read_csv(f'{self.data_dir}/google_trends/{latest_gt}')
            print(f"  ✅ Google Trends: {latest_gt}")
        
        # 2. Wikipedia
        wiki_files = [f for f in os.listdir(f'{self.data_dir}/wikipedia') if f.endswith('.csv')]
        if wiki_files:
            latest_wiki = sorted(wiki_files)[-1]
            data['wikipedia'] = pd.read_csv(f'{self.data_dir}/wikipedia/{latest_wiki}')
            print(f"  ✅ Wikipedia: {latest_wiki}")
        
        # 3. SPF - Urgences
        spf_files = [f for f in os.listdir(f'{self.data_dir}/spf') if 'urgences' in f and f.endswith('.csv')]
        if spf_files:
            latest_urgences = sorted(spf_files)[-1]
            data['urgences'] = pd.read_csv(f'{self.data_dir}/spf/{latest_urgences}')
            print(f"  ✅ Urgences: {latest_urgences}")
        
        # 3. SPF - Sentinelles
        spf_files = [f for f in os.listdir(f'{self.data_dir}/spf') if 'sentinelles' in f and f.endswith('.csv')]
        if spf_files:
            latest_sentinelles = sorted(spf_files)[-1]
            data['sentinelles'] = pd.read_csv(f'{self.data_dir}/spf/{latest_sentinelles}')
            print(f"  ✅ Sentinelles: {latest_sentinelles}")
        
        # 4. SPF - Vaccination
        spf_files = [f for f in os.listdir(f'{self.data_dir}/spf') if 'vaccination' in f and f.endswith('.csv')]
        if spf_files:
            latest_vaccination = sorted(spf_files)[-1]
            data['vaccination'] = pd.read_csv(f'{self.data_dir}/spf/{latest_vaccination}')
            print(f"  ✅ Vaccination: {latest_vaccination}")
        
        # 5. SPF - IAS
        spf_files = [f for f in os.listdir(f'{self.data_dir}/spf') if 'ias' in f and f.endswith('.csv')]
        if spf_files:
            latest_ias = sorted(spf_files)[-1]
            data['ias'] = pd.read_csv(f'{self.data_dir}/spf/{latest_ias}')
            print(f"  ✅ IAS: {latest_ias}")
        
        # 6. Population
        context_files = [f for f in os.listdir(f'{self.data_dir}/context') if 'population' in f and f.endswith('.csv')]
        if context_files:
            latest_population = sorted(context_files)[-1]
            data['population'] = pd.read_csv(f'{self.data_dir}/context/{latest_population}')
            print(f"  ✅ Population: {latest_population}")
        
        # 7. Météo
        context_files = [f for f in os.listdir(f'{self.data_dir}/context') if 'weather' in f and f.endswith('.csv')]
        if context_files:
            latest_weather = sorted(context_files)[-1]
            data['weather'] = pd.read_csv(f'{self.data_dir}/context/{latest_weather}')
            print(f"  ✅ Météo: {latest_weather}")
        
        print(f"\n📊 {len(data)} sources de données chargées")
        return data
    
    def prepare_google_trends_data(self, df):
        """Prépare les données Google Trends"""
        if df is None:
            return None
        
        df = df.copy()
        df['date'] = pd.to_datetime(df['date'])
        
        # Les données sont déjà pivotées, on les agrège par date
        df_agg = df.groupby('date').agg({
            'google_trends_grippe': 'mean',
            'google_trends_vaccin': 'mean', 
            'google_trends_symptomes': 'mean'
        }).reset_index()
        
        # Normalisation (z-score)
        for col in ['google_trends_grippe', 'google_trends_vaccin', 'google_trends_symptomes']:
            if col in df_agg.columns:
                df_agg[f'{col}_zscore'] = (df_agg[col] - df_agg[col].mean()) / df_agg[col].std()
        
        return df_agg
    
    def prepare_wikipedia_data(self, df):
        """Prépare les données Wikipedia"""
        if df is None:
            return None
        
        df = df.copy()
        df['date'] = pd.to_datetime(df['date'])
        
        # Normalisation des vues (z-score)
        for col in ['wiki_grippe_views', 'wiki_vaccination_views']:
            if col in df.columns:
                df[f'{col}_zscore'] = (df[col] - df[col].mean()) / df[col].std()
        
        return df[['date', 'wiki_grippe_views', 'wiki_vaccination_views', 
                  'wiki_grippe_views_zscore', 'wiki_vaccination_views_zscore']]
    
    def prepare_spf_data(self, data):
        """Prépare les données SPF"""
        prepared = {}
        
        # Urgences
        if 'urgences' in data:
            df = data['urgences'].copy()
            df['date'] = pd.to_datetime(df['date'])
            prepared['urgences'] = df[['date', 'region', 'urgences_grippe']]
        
        # Sentinelles
        if 'sentinelles' in data:
            df = data['sentinelles'].copy()
            df['date'] = pd.to_datetime(df['date'])
            prepared['sentinelles'] = df[['date', 'region', 'cas_sentinelles']]
        
        # IAS
        if 'ias' in data:
            df = data['ias'].copy()
            df['date'] = pd.to_datetime(df['date'])
            prepared['ias'] = df[['date', 'region', 'ias_syndrome_grippal']]
        
        # Vaccination (annuelle)
        if 'vaccination' in data:
            df = data['vaccination'].copy()
            prepared['vaccination'] = df[['region', 'year', 'taux_vaccination']]
        
        return prepared
    
    def prepare_context_data(self, data):
        """Prépare les données contextuelles"""
        prepared = {}
        
        # Population
        if 'population' in data:
            df = data['population'].copy()
            prepared['population'] = df[['region', 'population_totale', 'pct_65_plus']]
        
        # Météo
        if 'weather' in data:
            df = data['weather'].copy()
            df['date'] = pd.to_datetime(df['date'])
            prepared['weather'] = df[['date', 'region', 'temperature', 'humidity']]
        
        return prepared
    
    def create_weekly_dataset(self, data):
        """Crée le dataset hebdomadaire unifié"""
        print("\n🔄 Création du dataset hebdomadaire unifié...")
        
        # Préparation des données
        gt_data = self.prepare_google_trends_data(data.get('google_trends'))
        wiki_data = self.prepare_wikipedia_data(data.get('wikipedia'))
        spf_data = self.prepare_spf_data(data)
        context_data = self.prepare_context_data(data)
        
        # Création de la grille temporelle (semaines)
        start_date = datetime(2023, 1, 1)
        end_date = datetime(2025, 12, 31)
        weeks = pd.date_range(start=start_date, end=end_date, freq='W-MON')
        
        # Création de la grille régionale
        regions = list(self.region_mapping.keys())
        
        # Dataset de base
        base_data = []
        for week in weeks:
            for region in regions:
                base_data.append({
                    'date': week,
                    'region': region,
                    'week_of_year': week.isocalendar().week,
                    'year': week.year
                })
        
        df = pd.DataFrame(base_data)
        print(f"  📅 Grille de base: {len(df)} enregistrements ({len(weeks)} semaines × {len(regions)} régions)")
        
        # Fusion avec les données Google Trends (pas de dimension régionale)
        if gt_data is not None:
            df = df.merge(gt_data, on='date', how='left')
            print(f"  ✅ Google Trends fusionné")
        
        # Fusion avec les données Wikipedia (pas de dimension régionale)
        if wiki_data is not None:
            df = df.merge(wiki_data, on='date', how='left')
            print(f"  ✅ Wikipedia fusionné")
        
        # Fusion avec les données SPF
        for data_type, spf_df in spf_data.items():
            if data_type == 'vaccination':
                # Vaccination annuelle
                df = df.merge(spf_df, on=['region', 'year'], how='left')
            else:
                # Données hebdomadaires
                df = df.merge(spf_df, on=['date', 'region'], how='left')
            print(f"  ✅ {data_type} fusionné")
        
        # Fusion avec les données contextuelles
        if 'population' in context_data:
            df = df.merge(context_data['population'], on='region', how='left')
            print(f"  ✅ Population fusionné")
        
        if 'weather' in context_data:
            df = df.merge(context_data['weather'], on=['date', 'region'], how='left')
            print(f"  ✅ Météo fusionné")
        
        # Nettoyage des données
        df = df.fillna(0)
        
        print(f"  📊 Dataset final: {len(df)} enregistrements, {len(df.columns)} colonnes")
        return df
    
    def add_features(self, df):
        """Ajoute les features pour le modèle Random Forest"""
        print("\n🔧 Ajout des features pour le modèle...")
        
        # Tri par région et date
        df = df.sort_values(['region', 'date']).reset_index(drop=True)
        
        # Features temporelles
        df['month'] = df['date'].dt.month
        df['is_winter'] = df['month'].isin([12, 1, 2]).astype(int)
        df['is_autumn'] = df['month'].isin([9, 10, 11]).astype(int)
        
        # Lags pour les variables importantes
        lag_vars = ['urgences_grippe', 'cas_sentinelles', 'ias_syndrome_grippal', 
                   'wiki_grippe_views', 'wiki_vaccination_views']
        
        for var in lag_vars:
            if var in df.columns:
                for lag in [1, 2, 3, 4, 8, 12]:  # 1, 2, 3, 4, 8, 12 semaines
                    df[f'{var}_lag{lag}'] = df.groupby('region')[var].shift(lag)
        
        # Moyennes mobiles
        for var in lag_vars:
            if var in df.columns:
                for window in [3, 4, 8]:  # 3, 4, 8 semaines
                    df[f'{var}_ma{window}'] = df.groupby('region')[var].rolling(window=window, min_periods=1).mean().reset_index(0, drop=True)
        
        # Ratios et interactions
        if 'urgences_grippe' in df.columns and 'population_totale' in df.columns:
            df['urgences_per_100k'] = (df['urgences_grippe'] / df['population_totale'] * 100000).fillna(0)
        
        if 'cas_sentinelles' in df.columns and 'population_totale' in df.columns:
            df['sentinelles_per_100k'] = (df['cas_sentinelles'] / df['population_totale'] * 100000).fillna(0)
        
        # Features météo
        if 'temperature' in df.columns:
            df['temp_cold'] = (df['temperature'] < 5).astype(int)
            df['temp_mild'] = ((df['temperature'] >= 5) & (df['temperature'] < 15)).astype(int)
            df['temp_warm'] = (df['temperature'] >= 15).astype(int)
        
        if 'humidity' in df.columns:
            df['humidity_high'] = (df['humidity'] > 80).astype(int)
        
        print(f"  ✅ Features ajoutées: {len(df.columns)} colonnes totales")
        return df
    
    def calculate_flurisk(self, df):
        """Calcule l'indice FLURISK pour chaque département"""
        print("\n📊 Calcul de l'indice FLURISK...")
        
        # Normalisation des variables pour FLURISK
        def normalize_zscore(series):
            return (series - series.mean()) / series.std()
        
        # Composantes FLURISK
        flurisk_components = {}
        
        # 1. Vaccination (inversée: plus c'est bas, plus c'est risqué)
        if 'taux_vaccination' in df.columns:
            flurisk_components['vaccination'] = 100 - df['taux_vaccination']
        
        # 2. IAS
        if 'ias_syndrome_grippal' in df.columns:
            flurisk_components['ias'] = df['ias_syndrome_grippal'] * 50  # Échelle 0-100
        
        # 3. Google Trends (z-score)
        if 'wiki_grippe_views_zscore' in df.columns:
            flurisk_components['trends'] = (df['wiki_grippe_views_zscore'] + 2) * 25  # Échelle 0-100
        
        # 4. Wikipedia (z-score)
        if 'wiki_grippe_views_zscore' in df.columns:
            flurisk_components['wiki'] = (df['wiki_grippe_views_zscore'] + 2) * 25  # Échelle 0-100
        
        # 5. Population 65+
        if 'pct_65_plus' in df.columns:
            flurisk_components['age'] = df['pct_65_plus']
        
        # Calcul FLURISK (pondérations)
        df['flurisk'] = 0
        if 'vaccination' in flurisk_components:
            df['flurisk'] += 0.25 * flurisk_components['vaccination']
        if 'ias' in flurisk_components:
            df['flurisk'] += 0.25 * flurisk_components['ias']
        if 'trends' in flurisk_components:
            df['flurisk'] += 0.20 * flurisk_components['trends']
        if 'wiki' in flurisk_components:
            df['flurisk'] += 0.15 * flurisk_components['wiki']
        if 'age' in flurisk_components:
            df['flurisk'] += 0.15 * flurisk_components['age']
        
        # Normalisation finale (0-100)
        df['flurisk'] = np.clip(df['flurisk'], 0, 100)
        
        print(f"  ✅ FLURISK calculé: min={df['flurisk'].min():.1f}, max={df['flurisk'].max():.1f}, moy={df['flurisk'].mean():.1f}")
        return df
    
    def save_processed_data(self, df):
        """Sauvegarde le dataset traité"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'dataset_grippe_{timestamp}.csv'
        filepath = os.path.join(self.output_dir, filename)
        
        df.to_csv(filepath, index=False)
        print(f"\n💾 Dataset sauvegardé: {filepath}")
        print(f"   📊 {len(df)} enregistrements, {len(df.columns)} colonnes")
        
        return filepath
    
    def generate_summary(self, df):
        """Génère un résumé du dataset"""
        print("\n📋 RÉSUMÉ DU DATASET")
        print("=" * 50)
        
        print(f"📅 Période: {df['date'].min().strftime('%Y-%m-%d')} à {df['date'].max().strftime('%Y-%m-%d')}")
        print(f"🌍 Régions: {df['region'].nunique()}")
        print(f"📊 Enregistrements: {len(df):,}")
        print(f"🔧 Variables: {len(df.columns)}")
        
        print(f"\n📈 Variables principales:")
        main_vars = ['urgences_grippe', 'cas_sentinelles', 'ias_syndrome_grippal', 
                    'taux_vaccination', 'flurisk', 'wiki_grippe_views']
        
        for var in main_vars:
            if var in df.columns:
                print(f"   {var}: moy={df[var].mean():.2f}, max={df[var].max():.2f}")
        
        print(f"\n🎯 FLURISK par région (dernière semaine):")
        latest_week = df.groupby('region')['date'].max().max()
        latest_data = df[df['date'] == latest_week][['region', 'flurisk']].sort_values('flurisk', ascending=False)
        for _, row in latest_data.head(10).iterrows():
            print(f"   {row['region']}: {row['flurisk']:.1f}")

def main():
    """Fonction principale de fusion"""
    print("🚀 FUSION DES DONNÉES POUR LE MODÈLE GRIPPE")
    print("=" * 60)
    
    # Création du répertoire de sortie
    os.makedirs('data/processed', exist_ok=True)
    
    # Initialisation du système de fusion
    fusion = DataFusion()
    
    # Chargement des données
    data = fusion.load_latest_files()
    
    if not data:
        print("❌ Aucune donnée trouvée")
        return
    
    # Création du dataset unifié
    df = fusion.create_weekly_dataset(data)
    
    # Ajout des features
    df = fusion.add_features(df)
    
    # Calcul FLURISK
    df = fusion.calculate_flurisk(df)
    
    # Sauvegarde
    filepath = fusion.save_processed_data(df)
    
    # Résumé
    fusion.generate_summary(df)
    
    print(f"\n✅ FUSION TERMINÉE")
    print(f"📁 Dataset prêt pour le modèle: {filepath}")

if __name__ == "__main__":
    main()
