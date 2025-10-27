#!/usr/bin/env python3
"""
Script pour créer un fichier features.parquet séparé avec toutes les features pour l'IA
"""

import pandas as pd
import numpy as np
from pathlib import Path
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_features_parquet():
    """Crée un fichier features.parquet avec toutes les features pour l'IA"""
    logger.info("🔧 CRÉATION DU FICHIER FEATURES.PARQUET")
    logger.info("=" * 50)
    
    try:
        # Lire le dataset final
        dataset_file = Path("data/processed/lumen_fixed_dataset.parquet")
        df = pd.read_parquet(dataset_file)
        
        logger.info(f"📊 Dataset chargé: {df.shape}")
        
        # Séparer les features de la target variable
        target_cols = ['valeur', 'valeur_normalized']
        feature_cols = [col for col in df.columns if col not in target_cols]
        
        # Créer le DataFrame des features
        features_df = df[feature_cols].copy()
        
        # Ajouter des features engineering supplémentaires
        logger.info("🔧 Ajout de features engineering...")
        
        # Features d'interaction
        if 'population' in features_df.columns and 'density' in features_df.columns:
            features_df['population_density_interaction'] = features_df['population'] * features_df['density']
        
        # Features de normalisation
        numeric_cols = features_df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            if col not in ['region_code', 'age_group', 'is_senior', 'is_winter', 'is_spring', 'is_summer', 'is_autumn']:
                features_df[f'{col}_normalized'] = (features_df[col] - features_df[col].mean()) / features_df[col].std()
        
        # Features de catégorisation avancées
        if 'age_group' in features_df.columns:
            age_dummies = pd.get_dummies(features_df['age_group'], prefix='age')
            features_df = pd.concat([features_df, age_dummies], axis=1)
        
        if 'season' in features_df.columns:
            season_dummies = pd.get_dummies(features_df['season'], prefix='season')
            features_df = pd.concat([features_df, season_dummies], axis=1)
        
        # Features temporelles avancées
        if 'month' in features_df.columns:
            features_df['is_peak_season'] = features_df['month'].isin([10, 11, 12, 1, 2, 3]).astype(int)
            features_df['is_off_season'] = features_df['month'].isin([4, 5, 6, 7, 8, 9]).astype(int)
        
        # Features météo avancées
        if 'avg_temperature' in features_df.columns:
            features_df['temperature_category'] = pd.cut(features_df['avg_temperature'], 
                                                      bins=[-np.inf, 5, 15, 25, np.inf], 
                                                      labels=['very_cold', 'cold', 'mild', 'warm'])
        
        # Sauvegarder le fichier features.parquet
        features_file = Path("data/processed/features.parquet")
        features_df.to_parquet(features_file, index=False)
        
        logger.info(f"✅ Features sauvegardées: {features_file}")
        logger.info(f"📊 Shape features: {features_df.shape}")
        logger.info(f"📅 Colonnes features: {list(features_df.columns)}")
        
        # Créer aussi un fichier target.parquet
        target_df = df[target_cols].copy()
        target_file = Path("data/processed/target.parquet")
        target_df.to_parquet(target_file, index=False)
        
        logger.info(f"✅ Target sauvegardée: {target_file}")
        logger.info(f"📊 Shape target: {target_df.shape}")
        
        # Afficher un résumé des features
        print_features_summary(features_df)
        
        return features_df, target_df
        
    except Exception as e:
        logger.error(f"❌ Erreur création features: {e}")
        return None, None

def print_features_summary(features_df):
    """Affiche un résumé des features"""
    logger.info("📋 RÉSUMÉ DES FEATURES")
    logger.info("=" * 40)
    
    # Catégoriser les features
    temporal_features = [col for col in features_df.columns if col in ['season', 'campagne', 'year', 'month', 'quarter', 'is_peak_season', 'is_off_season']]
    geographic_features = [col for col in features_df.columns if col in ['region', 'region_code', 'population', 'density', 'population_density_interaction']]
    demographic_features = [col for col in features_df.columns if col in ['age_group', 'groupe', 'is_senior']]
    weather_features = [col for col in features_df.columns if col in ['avg_temperature', 'humidity', 'precipitation', 'temperature_category']]
    behavioral_features = [col for col in features_df.columns if col in ['behavioral_score']]
    
    logger.info(f"📅 Features temporelles ({len(temporal_features)}): {temporal_features}")
    logger.info(f"🗺️ Features géographiques ({len(geographic_features)}): {geographic_features}")
    logger.info(f"👥 Features démographiques ({len(demographic_features)}): {demographic_features}")
    logger.info(f"🌦️ Features météo ({len(weather_features)}): {weather_features}")
    logger.info(f"🧠 Features comportementales ({len(behavioral_features)}): {behavioral_features}")
    
    logger.info(f"📊 Total features: {len(features_df.columns)}")
    logger.info("=" * 40)

if __name__ == "__main__":
    create_features_parquet()
