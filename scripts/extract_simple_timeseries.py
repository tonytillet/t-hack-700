#!/usr/bin/env python3
"""
Script simple pour extraire les séries temporelles des données urgences
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

class SimpleTimeSeriesExtractor:
    def __init__(self):
        self.base_dir = Path("data")
        self.emergency_dir = self.base_dir / "processed" / "emergency_data"
        self.timeseries_dir = self.base_dir / "processed" / "timeseries"
        self.timeseries_dir.mkdir(parents=True, exist_ok=True)
    
    def load_and_parse_data(self):
        """Charge et parse les données urgences"""
        logger.info("📊 CHARGEMENT ET PARSING DES DONNÉES")
        logger.info("=" * 50)
        
        try:
            emergency_file = self.emergency_dir / "emergency_data.parquet"
            df = pd.read_parquet(emergency_file)
            
            logger.info(f"📊 Shape: {df.shape}")
            
            # Chercher les colonnes avec des données structurées
            structured_data = []
            
            # Colonnes avec données séparées par point-virgule
            semicolon_cols = [col for col in df.columns if ';' in str(col)]
            logger.info(f"📅 Colonnes avec point-virgule: {len(semicolon_cols)}")
            
            for col in semicolon_cols:
                logger.info(f"🔍 Analyse de: {col[:50]}...")
                
                # Prendre un échantillon pour analyser la structure
                sample_values = df[col].dropna().head(10).tolist()
                logger.info(f"📊 Échantillon: {sample_values[:3]}")
                
                # Parser les données si elles contiennent des informations utiles
                for idx, value in enumerate(df[col].dropna()):
                    if idx % 100000 == 0:
                        logger.info(f"📊 Traitement ligne {idx}")
                    
                    try:
                        # Split par point-virgule
                        parts = str(value).split(';')
                        
                        if len(parts) >= 3:
                            # Essayer d'extraire date, département, et cas COVID
                            date_str = parts[1] if len(parts) > 1 else None
                            dep_code = parts[0] if len(parts) > 0 else None
                            covid_cases = parts[2] if len(parts) > 2 else None
                            
                            # Valider et convertir
                            if date_str and dep_code and covid_cases:
                                try:
                                    date_val = pd.to_datetime(date_str, errors='coerce')
                                    dep_val = str(dep_code).strip()
                                    covid_val = float(covid_cases)
                                    
                                    if (pd.notna(date_val) and 
                                        date_val.year >= 2020 and 
                                        len(dep_val) == 2 and 
                                        covid_val >= 0):
                                        
                                        structured_data.append({
                                            'date': date_val,
                                            'department': dep_val,
                                            'covid_cases': covid_val
                                        })
                                        
                                        if len(structured_data) % 10000 == 0:
                                            logger.info(f"✅ {len(structured_data)} enregistrements extraits")
                                            
                                except:
                                    continue
                    
                    except Exception as e:
                        continue
            
            if structured_data:
                clean_df = pd.DataFrame(structured_data)
                logger.info(f"✅ Données structurées extraites: {clean_df.shape}")
                logger.info(f"📅 Période: {clean_df['date'].min()} à {clean_df['date'].max()}")
                logger.info(f"🗺️ Départements: {clean_df['department'].nunique()}")
                return clean_df
            else:
                logger.warning("⚠️ Aucune donnée structurée trouvée")
                return None
                
        except Exception as e:
            logger.error(f"❌ Erreur parsing: {e}")
            return None
    
    def create_daily_series(self, df):
        """Crée les séries temporelles quotidiennes"""
        logger.info("📅 CRÉATION DES SÉRIES QUOTIDIENNES")
        logger.info("=" * 50)
        
        try:
            # Agréger par date et département
            daily_series = df.groupby(['date', 'department']).agg({
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
            
            logger.info(f"✅ Séries quotidiennes: {daily_series.shape}")
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
            # Target variable (urgences dans 7 jours)
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
            
            logger.info(f"✅ Target: {target_series.shape}")
            logger.info(f"✅ Features: {features_series.shape}")
            
            return target_series, features_series
            
        except Exception as e:
            logger.error(f"❌ Erreur création target/features: {e}")
            return None, None
    
    def save_series(self, daily_series, target_series, features_series):
        """Sauvegarde toutes les séries"""
        logger.info("💾 SAUVEGARDE DES SÉRIES")
        logger.info("=" * 50)
        
        try:
            # Sauvegarder
            daily_series.to_parquet(self.timeseries_dir / "daily_emergency_series_simple.parquet", index=False)
            target_series.to_parquet(self.timeseries_dir / "target_series_simple.parquet", index=False)
            features_series.to_parquet(self.timeseries_dir / "features_series_simple.parquet", index=False)
            
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
            
            with open(self.timeseries_dir / "timeseries_summary_simple.json", 'w') as f:
                json.dump(summary, f, indent=2, default=str)
            
            logger.info("✅ SÉRIES SAUVEGARDÉES")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur sauvegarde: {e}")
            return False
    
    def run_extraction(self):
        """Lance l'extraction des séries temporelles"""
        logger.info("🚀 DÉBUT DE L'EXTRACTION DES SÉRIES TEMPORELLES")
        logger.info("=" * 60)
        
        # Charger et parser les données
        df = self.load_and_parse_data()
        if df is None:
            return False
        
        # Créer les séries quotidiennes
        daily_series = self.create_daily_series(df)
        if daily_series is None:
            return False
        
        # Créer target et features
        target_series, features_series = self.create_target_and_features(daily_series)
        if target_series is None or features_series is None:
            return False
        
        # Sauvegarder
        success = self.save_series(daily_series, target_series, features_series)
        
        if success:
            logger.info("✅ EXTRACTION TERMINÉE")
            logger.info("=" * 60)
            return True
        else:
            logger.error("❌ ÉCHEC DE L'EXTRACTION")
            return False

if __name__ == "__main__":
    extractor = SimpleTimeSeriesExtractor()
    extractor.run_extraction()
