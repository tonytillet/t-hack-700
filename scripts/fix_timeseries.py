#!/usr/bin/env python3
"""
Script pour corriger les séries temporelles avec un meilleur parsing des dates
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

class TimeSeriesFixer:
    def __init__(self):
        self.base_dir = Path("data")
        self.emergency_dir = self.base_dir / "processed" / "emergency_data"
        self.timeseries_dir = self.base_dir / "processed" / "timeseries"
        self.timeseries_dir.mkdir(parents=True, exist_ok=True)
    
    def load_and_analyze_data(self):
        """Charge et analyse les données urgences pour identifier les bonnes colonnes"""
        logger.info("🔍 ANALYSE DES DONNÉES URGENCES")
        logger.info("=" * 50)
        
        try:
            emergency_file = self.emergency_dir / "emergency_data.parquet"
            df = pd.read_parquet(emergency_file)
            
            logger.info(f"📊 Shape: {df.shape}")
            logger.info(f"📅 Colonnes: {list(df.columns)}")
            
            # Analyser les colonnes de date
            date_cols = []
            for col in df.columns:
                if 'date' in col.lower():
                    sample_values = df[col].dropna().head(5).tolist()
                    logger.info(f"📅 Colonne '{col}': {sample_values}")
                    date_cols.append(col)
            
            # Analyser les colonnes de département
            dep_cols = []
            for col in df.columns:
                if 'dep' in col.lower() and 'code' in col.lower():
                    sample_values = df[col].dropna().head(5).tolist()
                    logger.info(f"🗺️ Colonne '{col}': {sample_values}")
                    dep_cols.append(col)
            
            # Analyser les colonnes de COVID
            covid_cols = []
            for col in df.columns:
                if 'covid' in col.lower() and 'nbre' in col.lower():
                    sample_values = df[col].dropna().head(5).tolist()
                    logger.info(f"🏥 Colonne '{col}': {sample_values}")
                    covid_cols.append(col)
            
            return df, date_cols, dep_cols, covid_cols
            
        except Exception as e:
            logger.error(f"❌ Erreur analyse: {e}")
            return None, [], [], []
    
    def extract_clean_data(self, df, date_cols, dep_cols, covid_cols):
        """Extrait les données propres avec les bonnes colonnes"""
        logger.info("🧹 EXTRACTION DES DONNÉES PROPRES")
        logger.info("=" * 50)
        
        try:
            # Créer un DataFrame avec les colonnes utiles
            clean_data = []
            
            # Parcourir les lignes pour extraire les données valides
            for idx, row in df.iterrows():
                if idx % 10000 == 0:
                    logger.info(f"📊 Traitement ligne {idx}/{len(df)}")
                
                # Chercher une date valide
                valid_date = None
                for col in date_cols:
                    if pd.notna(row[col]):
                        try:
                            # Essayer différents formats de date
                            date_str = str(row[col])
                            if len(date_str) > 10:  # Date complète
                                valid_date = pd.to_datetime(date_str, errors='coerce')
                                if pd.notna(valid_date) and valid_date.year > 2020:  # Date récente
                                    break
                        except:
                            continue
                
                if valid_date is None:
                    continue
                
                # Chercher un département valide
                valid_dep = None
                for col in dep_cols:
                    if pd.notna(row[col]):
                        dep_val = str(row[col]).strip()
                        if len(dep_val) == 2 and dep_val.isdigit():
                            valid_dep = dep_val
                            break
                
                if valid_dep is None:
                    continue
                
                # Chercher des données COVID valides
                covid_cases = 0
                for col in covid_cols:
                    if pd.notna(row[col]):
                        try:
                            val = float(row[col])
                            if val > 0:
                                covid_cases = val
                                break
                        except:
                            continue
                
                if covid_cases > 0:
                    clean_data.append({
                        'date': valid_date,
                        'department': valid_dep,
                        'covid_cases': covid_cases
                    })
            
            if clean_data:
                clean_df = pd.DataFrame(clean_data)
                logger.info(f"✅ Données propres extraites: {clean_df.shape}")
                logger.info(f"📅 Période: {clean_df['date'].min()} à {clean_df['date'].max()}")
                logger.info(f"🗺️ Départements: {clean_df['department'].nunique()}")
                return clean_df
            else:
                logger.warning("⚠️ Aucune donnée propre trouvée")
                return None
                
        except Exception as e:
            logger.error(f"❌ Erreur extraction: {e}")
            return None
    
    def create_daily_aggregated_series(self, clean_df):
        """Crée les séries temporelles agrégées par jour et département"""
        logger.info("📅 CRÉATION DES SÉRIES AGRÉGÉES")
        logger.info("=" * 50)
        
        try:
            # Agréger par date et département
            daily_series = clean_df.groupby(['date', 'department']).agg({
                'covid_cases': 'sum'
            }).reset_index()
            
            # Ajouter des features temporelles
            daily_series['year'] = daily_series['date'].dt.year
            daily_series['month'] = daily_series['date'].dt.month
            daily_series['day_of_week'] = daily_series['date'].dt.dayofweek
            daily_series['week_of_year'] = daily_series['date'].dt.isocalendar().week
            daily_series['quarter'] = daily_series['date'].dt.quarter
            
            # Features saisonnières
            daily_series['is_weekend'] = daily_series['day_of_week'].isin([5, 6]).astype(int)
            daily_series['is_peak_season'] = daily_series['month'].isin([10, 11, 12, 1, 2, 3]).astype(int)
            
            # Moyennes mobiles
            daily_series = daily_series.sort_values(['department', 'date'])
            daily_series['covid_cases_ma7'] = daily_series.groupby('department')['covid_cases'].rolling(window=7, min_periods=1).mean().reset_index(0, drop=True)
            daily_series['covid_cases_ma30'] = daily_series.groupby('department')['covid_cases'].rolling(window=30, min_periods=1).mean().reset_index(0, drop=True)
            
            logger.info(f"✅ Séries agrégées créées: {daily_series.shape}")
            logger.info(f"📅 Période: {daily_series['date'].min()} à {daily_series['date'].max()}")
            logger.info(f"🗺️ Départements: {daily_series['department'].nunique()}")
            
            return daily_series
            
        except Exception as e:
            logger.error(f"❌ Erreur création séries: {e}")
            return None
    
    def create_target_and_features(self, daily_series):
        """Crée la target variable et les features"""
        logger.info("🎯 CRÉATION TARGET ET FEATURES")
        logger.info("=" * 50)
        
        try:
            # Créer la target variable (urgences dans 7 jours)
            target_series = daily_series.copy()
            target_series['target_date'] = target_series['date'] + timedelta(days=7)
            target_series = target_series.rename(columns={'covid_cases': 'target_covid_cases'})
            
            # Features avancées
            features_series = daily_series.copy()
            
            # Tendance
            features_series['covid_trend_7d'] = features_series.groupby('department')['covid_cases'].pct_change(7)
            features_series['covid_trend_30d'] = features_series.groupby('department')['covid_cases'].pct_change(30)
            
            # Volatilité
            features_series['covid_volatility_7d'] = features_series.groupby('department')['covid_cases'].rolling(window=7, min_periods=1).std().reset_index(0, drop=True)
            features_series['covid_volatility_30d'] = features_series.groupby('department')['covid_cases'].rolling(window=30, min_periods=1).std().reset_index(0, drop=True)
            
            # Saisonnalité
            features_series['sin_month'] = np.sin(2 * np.pi * features_series['month'] / 12)
            features_series['cos_month'] = np.cos(2 * np.pi * features_series['month'] / 12)
            features_series['sin_day'] = np.sin(2 * np.pi * features_series['day_of_week'] / 7)
            features_series['cos_day'] = np.cos(2 * np.pi * features_series['day_of_week'] / 7)
            
            # Interactions
            features_series['covid_weekend_interaction'] = features_series['covid_cases'] * features_series['is_weekend']
            features_series['covid_peak_interaction'] = features_series['covid_cases'] * features_series['is_peak_season']
            
            logger.info(f"✅ Target créée: {target_series.shape}")
            logger.info(f"✅ Features créées: {features_series.shape}")
            
            return target_series, features_series
            
        except Exception as e:
            logger.error(f"❌ Erreur création target/features: {e}")
            return None, None
    
    def save_corrected_series(self, daily_series, target_series, features_series):
        """Sauvegarde les séries corrigées"""
        logger.info("💾 SAUVEGARDE DES SÉRIES CORRIGÉES")
        logger.info("=" * 50)
        
        try:
            # Sauvegarder
            daily_series.to_parquet(self.timeseries_dir / "daily_emergency_series_fixed.parquet", index=False)
            target_series.to_parquet(self.timeseries_dir / "target_series_fixed.parquet", index=False)
            features_series.to_parquet(self.timeseries_dir / "features_series_fixed.parquet", index=False)
            
            # Résumé
            summary = {
                "daily_series": {
                    "shape": daily_series.shape,
                    "period": f"{daily_series['date'].min()} to {daily_series['date'].max()}",
                    "departments": daily_series['department'].nunique()
                },
                "target_series": {
                    "shape": target_series.shape,
                    "period": f"{target_series['date'].min()} to {target_series['date'].max()}"
                },
                "features_series": {
                    "shape": features_series.shape,
                    "period": f"{features_series['date'].min()} to {features_series['date'].max()}"
                }
            }
            
            with open(self.timeseries_dir / "timeseries_summary_fixed.json", 'w') as f:
                json.dump(summary, f, indent=2, default=str)
            
            logger.info("✅ SÉRIES CORRIGÉES SAUVEGARDÉES")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur sauvegarde: {e}")
            return False
    
    def run_fix(self):
        """Lance la correction des séries temporelles"""
        logger.info("🚀 DÉBUT DE LA CORRECTION DES SÉRIES TEMPORELLES")
        logger.info("=" * 60)
        
        # Analyser les données
        df, date_cols, dep_cols, covid_cols = self.load_and_analyze_data()
        if df is None:
            return False
        
        # Extraire les données propres
        clean_df = self.extract_clean_data(df, date_cols, dep_cols, covid_cols)
        if clean_df is None:
            return False
        
        # Créer les séries agrégées
        daily_series = self.create_daily_aggregated_series(clean_df)
        if daily_series is None:
            return False
        
        # Créer target et features
        target_series, features_series = self.create_target_and_features(daily_series)
        if target_series is None or features_series is None:
            return False
        
        # Sauvegarder
        success = self.save_corrected_series(daily_series, target_series, features_series)
        
        if success:
            logger.info("✅ CORRECTION TERMINÉE")
            logger.info("=" * 60)
            return True
        else:
            logger.error("❌ ÉCHEC DE LA CORRECTION")
            return False

if __name__ == "__main__":
    fixer = TimeSeriesFixer()
    fixer.run_fix()
