#!/usr/bin/env python3
"""
Script pour fabriquer les features par groupe, créer y_target à J+7,
lags/rollings, One-Hot, et écrire dans data/features/
"""

import pandas as pd
import numpy as np
from pathlib import Path
import logging
import json
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FeatureMaker:
    def __init__(self):
        self.base_dir = Path("data")
        self.processed_dir = self.base_dir / "processed"
        self.timeseries_dir = self.processed_dir / "timeseries"
        self.features_dir = self.base_dir / "features"
        self.config_dir = self.base_dir / "config"
        
        # Créer les dossiers
        self.features_dir.mkdir(parents=True, exist_ok=True)
        
        # Fichiers de sortie
        self.features_path = self.features_dir / "features.parquet"
        self.target_path = self.features_dir / "y_target.parquet"
        self.feature_list_path = self.features_dir / "feature_list.json"
    
    def load_data_and_config(self):
        """Charge les données et la configuration"""
        logger.info("📊 CHARGEMENT DES DONNÉES ET CONFIGURATION")
        logger.info("=" * 50)
        
        try:
            # Charger les séries temporelles
            daily_file = self.timeseries_dir / "daily_emergency_series_simple.parquet"
            if not daily_file.exists():
                logger.error(f"❌ Fichier non trouvé: {daily_file}")
                return None, None, None
            
            df = pd.read_parquet(daily_file)
            logger.info(f"✅ Données chargées: {df.shape}")
            
            # Charger la configuration
            medians_file = self.config_dir / "medians.json"
            cats_file = self.config_dir / "cats.json"
            
            medians = {}
            cats = {}
            
            if medians_file.exists():
                with open(medians_file, 'r', encoding='utf-8') as f:
                    medians = json.load(f)
                logger.info(f"✅ Médianes chargées: {len(medians)} variables")
            
            if cats_file.exists():
                with open(cats_file, 'r', encoding='utf-8') as f:
                    cats = json.load(f)
                logger.info(f"✅ Catégories chargées: {len(cats)} variables")
            
            return df, medians, cats
            
        except Exception as e:
            logger.error(f"❌ Erreur chargement: {e}")
            return None, None, None
    
    def create_target_variable(self, df):
        """Crée la variable cible y_target à J+7"""
        logger.info("🎯 CRÉATION DE LA VARIABLE CIBLE J+7")
        logger.info("=" * 50)
        
        try:
            # Créer la target variable (urgences dans 7 jours)
            target_df = df.copy()
            target_df['target_date'] = target_df['date'] + timedelta(days=7)
            target_df['y_target'] = target_df['covid_cases']
            
            # Garder seulement les colonnes nécessaires pour la target
            target_cols = ['date', 'department', 'y_target', 'target_date']
            target_df = target_df[target_cols]
            
            logger.info(f"✅ Target créée: {target_df.shape}")
            logger.info(f"📅 Période target: {target_df['date'].min()} à {target_df['date'].max()}")
            
            return target_df
            
        except Exception as e:
            logger.error(f"❌ Erreur création target: {e}")
            return None
    
    def create_lag_features(self, df, lags=[1, 3, 7, 14, 30]):
        """Crée les features de lag"""
        logger.info("⏰ CRÉATION DES FEATURES DE LAG")
        logger.info("=" * 50)
        
        try:
            df_lagged = df.copy()
            
            # Trier par département et date
            df_lagged = df_lagged.sort_values(['department', 'date'])
            
            # Créer les lags pour covid_cases
            for lag in lags:
                df_lagged[f'covid_cases_lag_{lag}'] = df_lagged.groupby('department')['covid_cases'].shift(lag)
                logger.info(f"  - Lag {lag}j créé")
            
            # Créer les lags pour les moyennes mobiles
            if 'covid_cases_ma7' in df_lagged.columns:
                for lag in [1, 3, 7]:
                    df_lagged[f'covid_cases_ma7_lag_{lag}'] = df_lagged.groupby('department')['covid_cases_ma7'].shift(lag)
            
            if 'covid_cases_ma30' in df_lagged.columns:
                for lag in [1, 7, 14]:
                    df_lagged[f'covid_cases_ma30_lag_{lag}'] = df_lagged.groupby('department')['covid_cases_ma30'].shift(lag)
            
            logger.info(f"✅ Features de lag créées: {len([col for col in df_lagged.columns if 'lag' in col])} variables")
            return df_lagged
            
        except Exception as e:
            logger.error(f"❌ Erreur création lags: {e}")
            return df
    
    def create_rolling_features(self, df, windows=[3, 7, 14, 30]):
        """Crée les features de rolling"""
        logger.info("📈 CRÉATION DES FEATURES DE ROLLING")
        logger.info("=" * 50)
        
        try:
            df_rolling = df.copy()
            
            # Trier par département et date
            df_rolling = df_rolling.sort_values(['department', 'date'])
            
            # Rolling statistics pour covid_cases
            for window in windows:
                df_rolling[f'covid_cases_rolling_mean_{window}'] = df_rolling.groupby('department')['covid_cases'].rolling(window=window, min_periods=1).mean().reset_index(0, drop=True)
                df_rolling[f'covid_cases_rolling_std_{window}'] = df_rolling.groupby('department')['covid_cases'].rolling(window=window, min_periods=1).std().reset_index(0, drop=True)
                df_rolling[f'covid_cases_rolling_max_{window}'] = df_rolling.groupby('department')['covid_cases'].rolling(window=window, min_periods=1).max().reset_index(0, drop=True)
                df_rolling[f'covid_cases_rolling_min_{window}'] = df_rolling.groupby('department')['covid_cases'].rolling(window=window, min_periods=1).min().reset_index(0, drop=True)
                logger.info(f"  - Rolling {window}j créé")
            
            logger.info(f"✅ Features de rolling créées: {len([col for col in df_rolling.columns if 'rolling' in col])} variables")
            return df_rolling
            
        except Exception as e:
            logger.error(f"❌ Erreur création rolling: {e}")
            return df
    
    def create_temporal_features(self, df):
        """Crée les features temporelles avancées"""
        logger.info("📅 CRÉATION DES FEATURES TEMPORELLES")
        logger.info("=" * 50)
        
        try:
            df_temp = df.copy()
            
            # Features cycliques
            df_temp['sin_month'] = np.sin(2 * np.pi * df_temp['month'] / 12)
            df_temp['cos_month'] = np.cos(2 * np.pi * df_temp['month'] / 12)
            df_temp['sin_day'] = np.sin(2 * np.pi * df_temp['day_of_week'] / 7)
            df_temp['cos_day'] = np.cos(2 * np.pi * df_temp['day_of_week'] / 7)
            df_temp['sin_quarter'] = np.sin(2 * np.pi * df_temp['quarter'] / 4)
            df_temp['cos_quarter'] = np.cos(2 * np.pi * df_temp['quarter'] / 4)
            
            # Features de saisonnalité
            df_temp['is_winter'] = df_temp['month'].isin([12, 1, 2]).astype(int)
            df_temp['is_spring'] = df_temp['month'].isin([3, 4, 5]).astype(int)
            df_temp['is_summer'] = df_temp['month'].isin([6, 7, 8]).astype(int)
            df_temp['is_autumn'] = df_temp['month'].isin([9, 10, 11]).astype(int)
            
            # Features de période
            df_temp['is_peak_flu_season'] = df_temp['month'].isin([10, 11, 12, 1, 2, 3]).astype(int)
            df_temp['is_holiday_season'] = df_temp['month'].isin([12, 1]).astype(int)
            
            logger.info(f"✅ Features temporelles créées: {len([col for col in df_temp.columns if any(x in col for x in ['sin_', 'cos_', 'is_'])])} variables")
            return df_temp
            
        except Exception as e:
            logger.error(f"❌ Erreur création features temporelles: {e}")
            return df
    
    def create_one_hot_features(self, df, cats):
        """Crée les features One-Hot"""
        logger.info("🔢 CRÉATION DES FEATURES ONE-HOT")
        logger.info("=" * 50)
        
        try:
            df_encoded = df.copy()
            
            # One-hot encoding pour les variables catégorielles
            categorical_vars = ['department', 'is_weekend', 'is_peak_season']
            
            for var in categorical_vars:
                if var in df_encoded.columns:
                    dummies = pd.get_dummies(df_encoded[var], prefix=var, dtype=int)
                    df_encoded = pd.concat([df_encoded, dummies], axis=1)
                    logger.info(f"  - One-hot {var}: {dummies.shape[1]} colonnes")
            
            # One-hot pour les mois (si pas déjà fait)
            if 'month' in df_encoded.columns:
                month_dummies = pd.get_dummies(df_encoded['month'], prefix='month', dtype=int)
                df_encoded = pd.concat([df_encoded, month_dummies], axis=1)
                logger.info(f"  - One-hot month: {month_dummies.shape[1]} colonnes")
            
            # One-hot pour les trimestres
            if 'quarter' in df_encoded.columns:
                quarter_dummies = pd.get_dummies(df_encoded['quarter'], prefix='quarter', dtype=int)
                df_encoded = pd.concat([df_encoded, quarter_dummies], axis=1)
                logger.info(f"  - One-hot quarter: {quarter_dummies.shape[1]} colonnes")
            
            logger.info(f"✅ Features One-Hot créées: {len([col for col in df_encoded.columns if any(x in col for x in ['_0', '_1', '_2', '_3', '_4', '_5', '_6', '_7', '_8', '_9'])])} variables")
            return df_encoded
            
        except Exception as e:
            logger.error(f"❌ Erreur création One-Hot: {e}")
            return df
    
    def create_interaction_features(self, df):
        """Crée les features d'interaction"""
        logger.info("🔗 CRÉATION DES FEATURES D'INTERACTION")
        logger.info("=" * 50)
        
        try:
            df_inter = df.copy()
            
            # Interactions temporelles
            if 'covid_cases' in df_inter.columns:
                df_inter['covid_weekend_interaction'] = df_inter['covid_cases'] * df_inter['is_weekend']
                df_inter['covid_peak_interaction'] = df_inter['covid_cases'] * df_inter['is_peak_season']
                
                if 'covid_cases_ma7' in df_inter.columns:
                    df_inter['covid_ma7_weekend_interaction'] = df_inter['covid_cases_ma7'] * df_inter['is_weekend']
            
            # Interactions saisonnières
            if 'month' in df_inter.columns and 'covid_cases' in df_inter.columns:
                df_inter['covid_month_interaction'] = df_inter['covid_cases'] * df_inter['month']
                df_inter['covid_quarter_interaction'] = df_inter['covid_cases'] * df_inter['quarter']
            
            logger.info(f"✅ Features d'interaction créées: {len([col for col in df_inter.columns if 'interaction' in col])} variables")
            return df_inter
            
        except Exception as e:
            logger.error(f"❌ Erreur création interactions: {e}")
            return df
    
    def prepare_final_features(self, df):
        """Prépare les features finales pour l'entraînement"""
        logger.info("🔧 PRÉPARATION DES FEATURES FINALES")
        logger.info("=" * 50)
        
        try:
            # Sélectionner les colonnes de features (exclure target et métadonnées)
            exclude_cols = ['date', 'department', 'y_target', 'target_date']
            feature_cols = [col for col in df.columns if col not in exclude_cols]
            
            # Créer le DataFrame de features
            features_df = df[feature_cols].copy()
            
            # Remplacer les valeurs infinies et NaN
            features_df = features_df.replace([np.inf, -np.inf], np.nan)
            features_df = features_df.fillna(0)
            
            # Créer la liste des features
            feature_list = {
                "feature_names": feature_cols,
                "total_features": len(feature_cols),
                "feature_categories": {
                    "lag_features": [col for col in feature_cols if 'lag' in col],
                    "rolling_features": [col for col in feature_cols if 'rolling' in col],
                    "temporal_features": [col for col in feature_cols if any(x in col for x in ['sin_', 'cos_', 'is_', 'month', 'quarter', 'day_of_week'])],
                    "interaction_features": [col for col in feature_cols if 'interaction' in col],
                    "one_hot_features": [col for col in feature_cols if any(x in col for x in ['_0', '_1', '_2', '_3', '_4', '_5', '_6', '_7', '_8', '_9'])]
                }
            }
            
            logger.info(f"✅ Features finales préparées: {features_df.shape}")
            logger.info(f"📊 Total features: {len(feature_cols)}")
            
            return features_df, feature_list
            
        except Exception as e:
            logger.error(f"❌ Erreur préparation features: {e}")
            return None, None
    
    def save_features(self, features_df, target_df, feature_list):
        """Sauvegarde les features et la target"""
        logger.info("💾 SAUVEGARDE DES FEATURES")
        logger.info("=" * 50)
        
        try:
            # Sauvegarder les features
            features_df.to_parquet(self.features_path, index=False)
            logger.info(f"✅ Features sauvegardées: {self.features_path}")
            
            # Sauvegarder la target
            target_df.to_parquet(self.target_path, index=False)
            logger.info(f"✅ Target sauvegardée: {self.target_path}")
            
            # Sauvegarder la liste des features
            with open(self.feature_list_path, 'w', encoding='utf-8') as f:
                json.dump(feature_list, f, indent=2, ensure_ascii=False)
            logger.info(f"✅ Liste des features sauvegardée: {self.feature_list_path}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur sauvegarde: {e}")
            return False
    
    def run_make_features(self):
        """Lance la création des features"""
        logger.info("🚀 DÉBUT DE LA CRÉATION DES FEATURES")
        logger.info("=" * 60)
        
        # Charger les données et config
        df, medians, cats = self.load_data_and_config()
        if df is None:
            return False
        
        # Créer la target variable
        target_df = self.create_target_variable(df)
        if target_df is None:
            return False
        
        # Créer les features de lag
        df = self.create_lag_features(df)
        
        # Créer les features de rolling
        df = self.create_rolling_features(df)
        
        # Créer les features temporelles
        df = self.create_temporal_features(df)
        
        # Créer les features One-Hot
        df = self.create_one_hot_features(df, cats)
        
        # Créer les features d'interaction
        df = self.create_interaction_features(df)
        
        # Préparer les features finales
        features_df, feature_list = self.prepare_final_features(df)
        if features_df is None:
            return False
        
        # Sauvegarder
        success = self.save_features(features_df, target_df, feature_list)
        
        if success:
            logger.info("✅ CRÉATION DES FEATURES TERMINÉE")
            logger.info("=" * 60)
            return True
        else:
            logger.error("❌ ÉCHEC DE LA CRÉATION DES FEATURES")
            return False

if __name__ == "__main__":
    maker = FeatureMaker()
    maker.run_make_features()
