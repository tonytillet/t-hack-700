#!/usr/bin/env python3
"""
Script simplifié d'amélioration des features temporelles
Ajoute la comparaison sur plusieurs années (N-2, N-1, N) pour prédire N+1
"""

import pandas as pd
import numpy as np
from datetime import datetime
import os
import warnings
warnings.filterwarnings('ignore')

def enhance_temporal_features(input_file, output_file=None):
    """Améliore les features temporelles du dataset"""
    print("🚀 AMÉLIORATION DES FEATURES TEMPORELLES (SIMPLIFIÉE)")
    print("=" * 60)
    
    # Chargement du dataset
    print(f"📂 Chargement du dataset: {input_file}")
    df = pd.read_csv(input_file)
    df['date'] = pd.to_datetime(df['date'])
    
    print(f"  ✅ Dataset chargé: {len(df)} enregistrements, {len(df.columns)} colonnes")
    
    # Tri par région et date
    df = df.sort_values(['region', 'date']).reset_index(drop=True)
    
    # Ajout des colonnes d'année et semaine
    df['year'] = df['date'].dt.year
    df['week_of_year'] = df['date'].dt.isocalendar().week
    
    print(f"\n🔄 Ajout des features de comparaison inter-années...")
    
    # Features principales à traiter
    features = ['urgences_grippe', 'cas_sentinelles', 'ias_syndrome_grippal']
    
    for feature in features:
        if feature in df.columns:
            print(f"  📊 Traitement de {feature}...")
            
            # N-2 (2 ans avant) - décalage de 104 semaines (2 ans)
            df[f'{feature}_year_minus_2'] = df.groupby('region')[feature].shift(104)
            
            # N-1 (1 an avant) - décalage de 52 semaines (1 an)
            df[f'{feature}_year_minus_1'] = df.groupby('region')[feature].shift(52)
            
            # N (année actuelle)
            df[f'{feature}_year_current'] = df[feature]
            
            # Différences inter-années
            df[f'{feature}_diff_n1_n2'] = df[f'{feature}_year_minus_1'] - df[f'{feature}_year_minus_2']
            df[f'{feature}_diff_n_n1'] = df[f'{feature}_year_current'] - df[f'{feature}_year_minus_1']
            df[f'{feature}_diff_n_n2'] = df[f'{feature}_year_current'] - df[f'{feature}_year_minus_2']
            
            # Ratios inter-années
            df[f'{feature}_ratio_n_n1'] = df[f'{feature}_year_current'] / (df[f'{feature}_year_minus_1'] + 1e-6)
            df[f'{feature}_ratio_n_n2'] = df[f'{feature}_year_current'] / (df[f'{feature}_year_minus_2'] + 1e-6)
            
            # Moyennes sur 3 ans (simplifiée)
            df[f'{feature}_mean_3years'] = df[[f'{feature}_year_minus_2', f'{feature}_year_minus_1', f'{feature}_year_current']].mean(axis=1)
            
            # Écart-type sur 3 ans (simplifiée)
            df[f'{feature}_std_3years'] = df[[f'{feature}_year_minus_2', f'{feature}_year_minus_1', f'{feature}_year_current']].std(axis=1)
            
            # Z-score sur 3 ans
            df[f'{feature}_zscore_3years'] = (df[feature] - df[f'{feature}_mean_3years']) / (df[f'{feature}_std_3years'] + 1e-6)
    
    print(f"\n🌡️ Ajout des patterns saisonniers...")
    
    # Patterns saisonniers par région
    for region in df['region'].unique():
        region_mask = df['region'] == region
        region_data = df[region_mask]
        
        for feature in ['urgences_grippe', 'cas_sentinelles']:
            if feature in df.columns:
                # Moyenne saisonnière par semaine de l'année
                seasonal_stats = region_data.groupby('week_of_year')[feature].agg(['mean', 'std']).reset_index()
                seasonal_stats.columns = ['week_of_year', f'{feature}_seasonal_mean', f'{feature}_seasonal_std']
                
                # Merge avec le dataset principal
                df = df.merge(seasonal_stats, on='week_of_year', how='left', suffixes=('', '_temp'))
                
                # Anomalie saisonnière
                df[f'{feature}_seasonal_anomaly'] = (df[feature] - df[f'{feature}_seasonal_mean']) / (df[f'{feature}_seasonal_std'] + 1e-6)
                
                # Suppression des colonnes temporaires
                df = df.drop(columns=[f'{feature}_seasonal_mean', f'{feature}_seasonal_std'])
    
    print(f"\n🚨 Ajout des indicateurs d'épidémie...")
    
    # Indicateurs d'épidémie par région
    for region in df['region'].unique():
        region_mask = df['region'] == region
        region_data = df[region_mask]
        
        for feature in ['urgences_grippe', 'cas_sentinelles']:
            if feature in df.columns:
                # Seuils d'épidémie (percentiles)
                p75 = region_data[feature].quantile(0.75)
                p90 = region_data[feature].quantile(0.90)
                p95 = region_data[feature].quantile(0.95)
                
                # Indicateurs d'épidémie
                df.loc[region_mask, f'{feature}_epidemic_level'] = 0
                df.loc[(region_mask) & (df[feature] > p75), f'{feature}_epidemic_level'] = 1
                df.loc[(region_mask) & (df[feature] > p90), f'{feature}_epidemic_level'] = 2
                df.loc[(region_mask) & (df[feature] > p95), f'{feature}_epidemic_level'] = 3
                
                # Distance au seuil épidémique
                df.loc[region_mask, f'{feature}_distance_to_epidemic'] = df[feature] - p75
                
                # Probabilité d'épidémie
                epidemic_prob = (region_data[feature] > p75).mean()
                df.loc[region_mask, f'{feature}_epidemic_probability'] = epidemic_prob
    
    print(f"\n📈 Ajout de l'analyse de tendances...")
    
    # Analyse de tendances simplifiée
    for region in df['region'].unique():
        region_mask = df['region'] == region
        region_data = df[region_mask].copy()
        
        for feature in ['urgences_grippe', 'cas_sentinelles']:
            if feature in df.columns:
                # Tendance linéaire simple (dernière année vs précédente)
                current_year_data = region_data[region_data['year'] == region_data['year'].max()]
                prev_year_data = region_data[region_data['year'] == region_data['year'].max() - 1]
                
                if len(current_year_data) > 0 and len(prev_year_data) > 0:
                    # Moyenne de l'année actuelle vs précédente
                    current_avg = current_year_data[feature].mean()
                    prev_avg = prev_year_data[feature].mean()
                    
                    # Tendance (positive = augmentation)
                    trend = current_avg - prev_avg
                    trend_ratio = current_avg / (prev_avg + 1e-6)
                    
                    df.loc[region_mask, f'{feature}_trend'] = trend
                    df.loc[region_mask, f'{feature}_trend_ratio'] = trend_ratio
    
    # Nettoyage des données
    df = df.fillna(0)
    
    # Sauvegarde
    if output_file is None:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = f'dataset_grippe_enhanced_{timestamp}.csv'
    
    filepath = os.path.join('data', 'processed', output_file)
    df.to_csv(filepath, index=False)
    
    # Statistiques
    print(f"\n📊 STATISTIQUES DU DATASET AMÉLIORÉ:")
    print(f"  📅 Période: {df['date'].min().strftime('%Y-%m-%d')} à {df['date'].max().strftime('%Y-%m-%d')}")
    print(f"  🌍 Régions: {df['region'].nunique()}")
    print(f"  📊 Enregistrements: {len(df):,}")
    print(f"  🔧 Variables: {len(df.columns)}")
    
    # Nouvelles features ajoutées
    new_features = [col for col in df.columns if any(x in col for x in ['_year_', '_diff_', '_ratio_', '_mean_3years', '_seasonal_', '_epidemic_', '_trend'])]
    print(f"  ✨ Nouvelles features: {len(new_features)}")
    
    print(f"\n✅ AMÉLIORATION TERMINÉE")
    print(f"📁 Dataset amélioré: {filepath}")
    
    return filepath

def main():
    """Fonction principale"""
    input_file = 'data/processed/dataset_grippe_20251020_164111.csv'
    
    if not os.path.exists(input_file):
        print(f"❌ Dataset non trouvé: {input_file}")
        return
    
    enhance_temporal_features(input_file)

if __name__ == "__main__":
    main()
