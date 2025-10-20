#!/usr/bin/env python3
"""
Script d'amélioration des features temporelles
Ajoute la comparaison sur plusieurs années (N-2, N-1, N) pour prédire N+1
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import warnings
warnings.filterwarnings('ignore')

class TemporalFeatureEnhancer:
    def __init__(self):
        """Initialise l'améliorateur de features temporelles"""
        self.data = None
    
    def load_data(self, filepath):
        """Charge le dataset existant"""
        print(f"📂 Chargement du dataset: {filepath}")
        
        self.data = pd.read_csv(filepath)
        self.data['date'] = pd.to_datetime(self.data['date'])
        
        print(f"  ✅ Dataset chargé: {len(self.data)} enregistrements, {len(self.data.columns)} colonnes")
        print(f"  📅 Période: {self.data['date'].min().strftime('%Y-%m-%d')} à {self.data['date'].max().strftime('%Y-%m-%d')}")
        
        return self.data
    
    def add_yearly_comparison_features(self):
        """Ajoute les features de comparaison inter-années"""
        print("\n🔄 Ajout des features de comparaison inter-années...")
        
        df = self.data.copy()
        df = df.sort_values(['region', 'date']).reset_index(drop=True)
        
        # Ajout des colonnes d'année et semaine
        df['year'] = df['date'].dt.year
        df['week_of_year'] = df['date'].dt.isocalendar().week
        
        # Features de comparaison inter-années
        yearly_features = [
            'urgences_grippe', 'cas_sentinelles', 'ias_syndrome_grippal',
            'google_trends_grippe', 'google_trends_vaccin', 'google_trends_symptomes',
            'wiki_grippe_views', 'wiki_vaccination_views',
            'temperature', 'humidity'
        ]
        
        for feature in yearly_features:
            if feature in df.columns:
                print(f"  📊 Traitement de {feature}...")
                
                # N-2 (2 ans avant)
                df[f'{feature}_year_minus_2'] = df.groupby(['region', 'week_of_year'])[feature].shift(2)
                
                # N-1 (1 an avant)
                df[f'{feature}_year_minus_1'] = df.groupby(['region', 'week_of_year'])[feature].shift(1)
                
                # N (année actuelle)
                df[f'{feature}_year_current'] = df[feature]
                
                # Différences inter-années
                df[f'{feature}_diff_n1_n2'] = df[f'{feature}_year_minus_1'] - df[f'{feature}_year_minus_2']
                df[f'{feature}_diff_n_n1'] = df[f'{feature}_year_current'] - df[f'{feature}_year_minus_1']
                df[f'{feature}_diff_n_n2'] = df[f'{feature}_year_current'] - df[f'{feature}_year_minus_2']
                
                # Ratios inter-années
                df[f'{feature}_ratio_n_n1'] = df[f'{feature}_year_current'] / (df[f'{feature}_year_minus_1'] + 1e-6)
                df[f'{feature}_ratio_n_n2'] = df[f'{feature}_year_current'] / (df[f'{feature}_year_minus_2'] + 1e-6)
                
                # Moyennes mobiles inter-années
                ma_3years = df.groupby(['region', 'week_of_year'])[feature].rolling(window=3, min_periods=1).mean()
                df[f'{feature}_ma_3years'] = ma_3years.reset_index(level=[0,1], drop=True)
                
                # Écart-type inter-années
                std_3years = df.groupby(['region', 'week_of_year'])[feature].rolling(window=3, min_periods=1).std()
                df[f'{feature}_std_3years'] = std_3years.reset_index(level=[0,1], drop=True)
                
                # Z-score inter-années
                df[f'{feature}_zscore_3years'] = (df[feature] - df[f'{feature}_ma_3years']) / (df[f'{feature}_std_3years'] + 1e-6)
        
        print(f"  ✅ Features inter-années ajoutées")
        return df
    
    def add_seasonal_patterns(self):
        """Ajoute les patterns saisonniers inter-années"""
        print("\n🌡️ Ajout des patterns saisonniers...")
        
        df = self.data.copy()
        
        # Patterns saisonniers par région
        for region in df['region'].unique():
            region_data = df[df['region'] == region].copy()
            region_data = region_data.sort_values('date')
            
            # Calcul des patterns saisonniers sur 3 ans
            for feature in ['urgences_grippe', 'cas_sentinelles', 'ias_syndrome_grippal']:
                if feature in df.columns:
                    # Moyenne saisonnière sur 3 ans
                    seasonal_mean = region_data.groupby(region_data['date'].dt.isocalendar().week)[feature].mean()
                    
                    # Écart-type saisonnier sur 3 ans
                    seasonal_std = region_data.groupby(region_data['date'].dt.isocalendar().week)[feature].std()
                    
                    # Application aux données
                    for idx in region_data.index:
                        week = region_data.loc[idx, 'date'].isocalendar().week
                        if week in seasonal_mean.index:
                            df.loc[idx, f'{feature}_seasonal_mean'] = seasonal_mean[week]
                            df.loc[idx, f'{feature}_seasonal_std'] = seasonal_std[week]
                            
                            # Anomalie saisonnière
                            current_value = region_data.loc[idx, feature]
                            seasonal_avg = seasonal_mean[week]
                            seasonal_sd = seasonal_std[week]
                            
                            if not pd.isna(seasonal_sd) and seasonal_sd > 0:
                                df.loc[idx, f'{feature}_seasonal_anomaly'] = (current_value - seasonal_avg) / seasonal_sd
                            else:
                                df.loc[idx, f'{feature}_seasonal_anomaly'] = 0
        
        print(f"  ✅ Patterns saisonniers ajoutés")
        return df
    
    def add_epidemic_indicators(self):
        """Ajoute des indicateurs d'épidémie basés sur l'historique"""
        print("\n🚨 Ajout des indicateurs d'épidémie...")
        
        df = self.data.copy()
        
        # Seuils d'épidémie basés sur l'historique
        for region in df['region'].unique():
            region_data = df[df['region'] == region].copy()
            
            for feature in ['urgences_grippe', 'cas_sentinelles']:
                if feature in df.columns:
                    # Calcul des seuils (percentiles 75, 90, 95)
                    p75 = region_data[feature].quantile(0.75)
                    p90 = region_data[feature].quantile(0.90)
                    p95 = region_data[feature].quantile(0.95)
                    
                    # Indicateurs d'épidémie
                    df.loc[df['region'] == region, f'{feature}_epidemic_level'] = 0
                    df.loc[(df['region'] == region) & (df[feature] > p75), f'{feature}_epidemic_level'] = 1
                    df.loc[(df['region'] == region) & (df[feature] > p90), f'{feature}_epidemic_level'] = 2
                    df.loc[(df['region'] == region) & (df[feature] > p95), f'{feature}_epidemic_level'] = 3
                    
                    # Distance au seuil épidémique
                    df.loc[df['region'] == region, f'{feature}_distance_to_epidemic'] = df[feature] - p75
                    
                    # Probabilité d'épidémie (basée sur l'historique)
                    epidemic_prob = (region_data[feature] > p75).mean()
                    df.loc[df['region'] == region, f'{feature}_epidemic_probability'] = epidemic_prob
        
        print(f"  ✅ Indicateurs d'épidémie ajoutés")
        return df
    
    def add_trend_analysis(self):
        """Ajoute l'analyse de tendances sur plusieurs années"""
        print("\n📈 Ajout de l'analyse de tendances...")
        
        df = self.data.copy()
        df = df.sort_values(['region', 'date']).reset_index(drop=True)
        
        # Analyse de tendances par région
        for region in df['region'].unique():
            region_data = df[df['region'] == region].copy()
            region_data = region_data.sort_values('date')
            
            for feature in ['urgences_grippe', 'cas_sentinelles', 'ias_syndrome_grippal']:
                if feature in df.columns:
                    # Tendance linéaire sur 3 ans
                    from scipy import stats
                    
                    # Calcul de la tendance pour chaque semaine de l'année
                    for week in range(1, 53):
                        week_data = region_data[region_data['date'].dt.isocalendar().week == week]
                        if len(week_data) >= 3:  # Au moins 3 points
                            years = week_data['date'].dt.year.values
                            values = week_data[feature].values
                            
                            if len(years) >= 3:
                                slope, intercept, r_value, p_value, std_err = stats.linregress(years, values)
                                
                                # Application de la tendance
                                for idx in week_data.index:
                                    df.loc[idx, f'{feature}_trend_slope'] = slope
                                    df.loc[idx, f'{feature}_trend_r2'] = r_value**2
                                    df.loc[idx, f'{feature}_trend_pvalue'] = p_value
                                    
                                    # Prédiction basée sur la tendance
                                    current_year = df.loc[idx, 'date'].year
                                    predicted_value = slope * current_year + intercept
                                    df.loc[idx, f'{feature}_trend_prediction'] = predicted_value
                                    df.loc[idx, f'{feature}_trend_residual'] = df.loc[idx, feature] - predicted_value
        
        print(f"  ✅ Analyse de tendances ajoutée")
        return df
    
    def create_enhanced_dataset(self):
        """Crée le dataset amélioré avec toutes les features temporelles"""
        print("\n🚀 Création du dataset amélioré...")
        
        # Application de toutes les améliorations
        df = self.add_yearly_comparison_features()
        df = self.add_seasonal_patterns()
        df = self.add_epidemic_indicators()
        df = self.add_trend_analysis()
        
        # Nettoyage des données
        df = df.fillna(0)
        
        print(f"  ✅ Dataset amélioré créé: {len(df)} enregistrements, {len(df.columns)} colonnes")
        return df
    
    def save_enhanced_dataset(self, df, output_file=None):
        """Sauvegarde le dataset amélioré"""
        if output_file is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = f'dataset_grippe_enhanced_{timestamp}.csv'
        
        filepath = os.path.join('data', 'processed', output_file)
        df.to_csv(filepath, index=False)
        print(f"💾 Dataset amélioré sauvegardé: {filepath}")
        
        return filepath

def main():
    """Fonction principale"""
    print("🚀 AMÉLIORATION DES FEATURES TEMPORELLES")
    print("=" * 60)
    
    # Chargement du dataset existant
    dataset_file = 'data/processed/dataset_grippe_20251020_164111.csv'
    if not os.path.exists(dataset_file):
        print(f"❌ Dataset non trouvé: {dataset_file}")
        return
    
    # Initialisation
    enhancer = TemporalFeatureEnhancer()
    df = enhancer.load_data(dataset_file)
    
    # Création du dataset amélioré
    enhanced_df = enhancer.create_enhanced_dataset()
    
    # Sauvegarde
    output_file = enhancer.save_enhanced_dataset(enhanced_df)
    
    # Statistiques
    print(f"\n📊 STATISTIQUES DU DATASET AMÉLIORÉ:")
    print(f"  📅 Période: {enhanced_df['date'].min().strftime('%Y-%m-%d')} à {enhanced_df['date'].max().strftime('%Y-%m-%d')}")
    print(f"  🌍 Régions: {enhanced_df['region'].nunique()}")
    print(f"  📊 Enregistrements: {len(enhanced_df):,}")
    print(f"  🔧 Variables: {len(enhanced_df.columns)}")
    
    # Nouvelles features ajoutées
    new_features = [col for col in enhanced_df.columns if any(x in col for x in ['_year_', '_diff_', '_ratio_', '_ma_3years', '_seasonal_', '_epidemic_', '_trend_'])]
    print(f"  ✨ Nouvelles features: {len(new_features)}")
    
    print(f"\n✅ AMÉLIORATION TERMINÉE")
    print(f"📁 Dataset amélioré: {output_file}")

if __name__ == "__main__":
    main()
