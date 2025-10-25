#!/usr/bin/env python3
"""
Script pour créer les séries temporelles quotidiennes à partir des données urgences
"""

import pandas as pd
import numpy as np
from pathlib import Path
import logging
from datetime import datetime, timedelta
import json

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TimeSeriesCreator:
    def __init__(self):
        self.base_dir = Path("data")
        self.emergency_dir = self.base_dir / "processed" / "emergency_data"
        self.timeseries_dir = self.base_dir / "processed" / "timeseries"
        self.timeseries_dir.mkdir(parents=True, exist_ok=True)
        
        # Fichiers de sortie
        self.daily_series_path = self.timeseries_dir / "daily_emergency_series.parquet"
        self.weekly_series_path = self.timeseries_dir / "weekly_emergency_series.parquet"
        self.target_series_path = self.timeseries_dir / "target_series.parquet"
        self.features_series_path = self.timeseries_dir / "features_series.parquet"
    
    def load_emergency_data(self):
        """Charge les données urgences téléchargées"""
        logger.info("📊 CHARGEMENT DES DONNÉES URGENCES")
        logger.info("=" * 50)
        
        try:
            emergency_file = self.emergency_dir / "emergency_data.parquet"
            df = pd.read_parquet(emergency_file)
            
            logger.info(f"✅ Données urgences chargées: {df.shape}")
            logger.info(f"📅 Colonnes disponibles: {list(df.columns)}")
            
            return df
            
        except Exception as e:
            logger.error(f"❌ Erreur chargement données urgences: {e}")
            return None
    
    def clean_emergency_data(self, df):
        """Nettoie et standardise les données urgences"""
        logger.info("🧹 NETTOYAGE DES DONNÉES URGENCES")
        logger.info("=" * 50)
        
        try:
            # Identifier les colonnes utiles
            useful_cols = []
            for col in df.columns:
                if any(keyword in col.lower() for keyword in ['date', 'dep', 'reg', 'covid', 'urg', 'pass', 'hosp']):
                    useful_cols.append(col)
            
            logger.info(f"📅 Colonnes utiles identifiées: {len(useful_cols)}")
            
            # Créer un DataFrame nettoyé
            clean_df = df[useful_cols].copy()
            
            # Standardiser les colonnes de date
            date_cols = [col for col in clean_df.columns if 'date' in col.lower()]
            logger.info(f"📅 Colonnes de date trouvées: {date_cols}")
            
            # Créer une colonne date standardisée
            if date_cols:
                # Prendre la première colonne de date disponible
                date_col = date_cols[0]
                clean_df['date'] = pd.to_datetime(clean_df[date_col], errors='coerce')
            else:
                logger.warning("⚠️ Aucune colonne de date trouvée")
                return None
            
            # Standardiser les colonnes géographiques
            dep_cols = [col for col in clean_df.columns if 'dep' in col.lower()]
            reg_cols = [col for col in clean_df.columns if 'reg' in col.lower()]
            
            if dep_cols:
                clean_df['department'] = clean_df[dep_cols[0]]
            if reg_cols:
                clean_df['region'] = clean_df[reg_cols[0]]
            
            # Standardiser les colonnes de santé
            covid_cols = [col for col in clean_df.columns if 'covid' in col.lower()]
            urg_cols = [col for col in clean_df.columns if 'urg' in col.lower()]
            
            if covid_cols:
                clean_df['covid_cases'] = pd.to_numeric(clean_df[covid_cols[0]], errors='coerce')
            if urg_cols:
                clean_df['total_emergency'] = pd.to_numeric(clean_df[urg_cols[0]], errors='coerce')
            
            # Supprimer les lignes avec des dates invalides
            clean_df = clean_df.dropna(subset=['date'])
            
            logger.info(f"✅ Données nettoyées: {clean_df.shape}")
            logger.info(f"📅 Période: {clean_df['date'].min()} à {clean_df['date'].max()}")
            
            return clean_df
            
        except Exception as e:
            logger.error(f"❌ Erreur nettoyage: {e}")
            return None
    
    def create_daily_series(self, df):
        """Crée les séries temporelles quotidiennes"""
        logger.info("📅 CRÉATION DES SÉRIES TEMPORELLES QUOTIDIENNES")
        logger.info("=" * 50)
        
        try:
            # Grouper par date et département
            daily_series = df.groupby(['date', 'department']).agg({
                'covid_cases': 'sum',
                'total_emergency': 'sum'
            }).reset_index()
            
            # Créer des colonnes dérivées
            daily_series['covid_rate'] = daily_series['covid_cases'] / (daily_series['total_emergency'] + 1e-6)
            daily_series['covid_rate'] = daily_series['covid_rate'].fillna(0)
            
            # Ajouter des features temporelles
            daily_series['year'] = daily_series['date'].dt.year
            daily_series['month'] = daily_series['date'].dt.month
            daily_series['day_of_week'] = daily_series['date'].dt.dayofweek
            daily_series['week_of_year'] = daily_series['date'].dt.isocalendar().week
            daily_series['quarter'] = daily_series['date'].dt.quarter
            
            # Ajouter des features saisonnières
            daily_series['is_weekend'] = daily_series['day_of_week'].isin([5, 6]).astype(int)
            daily_series['is_peak_season'] = daily_series['month'].isin([10, 11, 12, 1, 2, 3]).astype(int)
            
            # Créer des moyennes mobiles
            daily_series = daily_series.sort_values(['department', 'date'])
            daily_series['covid_cases_ma7'] = daily_series.groupby('department')['covid_cases'].rolling(window=7, min_periods=1).mean().reset_index(0, drop=True)
            daily_series['covid_cases_ma30'] = daily_series.groupby('department')['covid_cases'].rolling(window=30, min_periods=1).mean().reset_index(0, drop=True)
            
            logger.info(f"✅ Séries quotidiennes créées: {daily_series.shape}")
            logger.info(f"📅 Période: {daily_series['date'].min()} à {daily_series['date'].max()}")
            logger.info(f"🗺️ Départements: {daily_series['department'].nunique()}")
            
            return daily_series
            
        except Exception as e:
            logger.error(f"❌ Erreur création séries quotidiennes: {e}")
            return None
    
    def create_target_series(self, daily_series):
        """Crée la série cible pour la prédiction t+7"""
        logger.info("🎯 CRÉATION DE LA SÉRIE CIBLE T+7")
        logger.info("=" * 50)
        
        try:
            # Créer la target variable (urgences dans 7 jours)
            target_series = daily_series.copy()
            target_series['target_date'] = target_series['date'] + timedelta(days=7)
            
            # Renommer les colonnes pour la target
            target_series = target_series.rename(columns={
                'covid_cases': 'target_covid_cases',
                'total_emergency': 'target_total_emergency',
                'covid_rate': 'target_covid_rate'
            })
            
            # Garder seulement les colonnes nécessaires
            target_cols = ['date', 'department', 'target_covid_cases', 'target_total_emergency', 'target_covid_rate']
            target_series = target_series[target_cols]
            
            logger.info(f"✅ Série cible créée: {target_series.shape}")
            logger.info(f"📅 Période target: {target_series['date'].min()} à {target_series['date'].max()}")
            
            return target_series
            
        except Exception as e:
            logger.error(f"❌ Erreur création série cible: {e}")
            return None
    
    def create_features_series(self, daily_series):
        """Crée les features pour la prédiction"""
        logger.info("🔧 CRÉATION DES FEATURES")
        logger.info("=" * 50)
        
        try:
            # Features temporelles
            features_series = daily_series.copy()
            
            # Features de tendance
            features_series['covid_trend_7d'] = features_series.groupby('department')['covid_cases'].pct_change(7)
            features_series['covid_trend_30d'] = features_series.groupby('department')['covid_cases'].pct_change(30)
            
            # Features de volatilité
            features_series['covid_volatility_7d'] = features_series.groupby('department')['covid_cases'].rolling(window=7, min_periods=1).std().reset_index(0, drop=True)
            features_series['covid_volatility_30d'] = features_series.groupby('department')['covid_cases'].rolling(window=30, min_periods=1).std().reset_index(0, drop=True)
            
            # Features de saisonnalité
            features_series['sin_month'] = np.sin(2 * np.pi * features_series['month'] / 12)
            features_series['cos_month'] = np.cos(2 * np.pi * features_series['month'] / 12)
            features_series['sin_day'] = np.sin(2 * np.pi * features_series['day_of_week'] / 7)
            features_series['cos_day'] = np.cos(2 * np.pi * features_series['day_of_week'] / 7)
            
            # Features d'interaction
            features_series['covid_weekend_interaction'] = features_series['covid_cases'] * features_series['is_weekend']
            features_series['covid_peak_interaction'] = features_series['covid_cases'] * features_series['is_peak_season']
            
            logger.info(f"✅ Features créées: {features_series.shape}")
            logger.info(f"📅 Colonnes features: {list(features_series.columns)}")
            
            return features_series
            
        except Exception as e:
            logger.error(f"❌ Erreur création features: {e}")
            return None
    
    def save_series(self, daily_series, target_series, features_series):
        """Sauvegarde toutes les séries temporelles"""
        logger.info("💾 SAUVEGARDE DES SÉRIES TEMPORELLES")
        logger.info("=" * 50)
        
        try:
            # Sauvegarder les séries quotidiennes
            daily_series.to_parquet(self.daily_series_path, index=False)
            logger.info(f"✅ Séries quotidiennes: {self.daily_series_path}")
            
            # Sauvegarder la série cible
            target_series.to_parquet(self.target_series_path, index=False)
            logger.info(f"✅ Série cible: {self.target_series_path}")
            
            # Sauvegarder les features
            features_series.to_parquet(self.features_series_path, index=False)
            logger.info(f"✅ Features: {self.features_series_path}")
            
            # Créer un résumé
            summary = {
                "daily_series": {
                    "shape": daily_series.shape,
                    "period": f"{daily_series['date'].min()} to {daily_series['date'].max()}",
                    "departments": daily_series['department'].nunique(),
                    "columns": list(daily_series.columns)
                },
                "target_series": {
                    "shape": target_series.shape,
                    "period": f"{target_series['date'].min()} to {target_series['date'].max()}",
                    "columns": list(target_series.columns)
                },
                "features_series": {
                    "shape": features_series.shape,
                    "period": f"{features_series['date'].min()} to {features_series['date'].max()}",
                    "columns": list(features_series.columns)
                }
            }
            
            summary_path = self.timeseries_dir / "timeseries_summary.json"
            with open(summary_path, 'w', encoding='utf-8') as f:
                json.dump(summary, f, indent=2, ensure_ascii=False, default=str)
            
            logger.info(f"📋 Résumé sauvegardé: {summary_path}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur sauvegarde: {e}")
            return False
    
    def run_creation(self):
        """Lance la création des séries temporelles"""
        logger.info("🚀 DÉBUT DE LA CRÉATION DES SÉRIES TEMPORELLES")
        logger.info("=" * 60)
        
        # Charger les données urgences
        emergency_df = self.load_emergency_data()
        if emergency_df is None:
            return False
        
        # Nettoyer les données
        clean_df = self.clean_emergency_data(emergency_df)
        if clean_df is None:
            return False
        
        # Créer les séries quotidiennes
        daily_series = self.create_daily_series(clean_df)
        if daily_series is None:
            return False
        
        # Créer la série cible
        target_series = self.create_target_series(daily_series)
        if target_series is None:
            return False
        
        # Créer les features
        features_series = self.create_features_series(daily_series)
        if features_series is None:
            return False
        
        # Sauvegarder toutes les séries
        success = self.save_series(daily_series, target_series, features_series)
        
        if success:
            logger.info("✅ CRÉATION DES SÉRIES TEMPORELLES TERMINÉE")
            logger.info("=" * 60)
            return True
        else:
            logger.error("❌ ÉCHEC DE LA CRÉATION DES SÉRIES TEMPORELLES")
            return False

if __name__ == "__main__":
    creator = TimeSeriesCreator()
    creator.run_creation()
