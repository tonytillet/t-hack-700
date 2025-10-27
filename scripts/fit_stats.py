#!/usr/bin/env python3
"""
Script pour calculer les statistiques de référence (medians.json et cats.json)
à partir des fichiers Parquet
"""

import pandas as pd
import numpy as np
from pathlib import Path
import logging
import json
from datetime import datetime

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class StatsFitter:
    def __init__(self):
        self.base_dir = Path("data")
        self.processed_dir = self.base_dir / "processed"
        self.timeseries_dir = self.processed_dir / "timeseries"
        self.stats_dir = self.base_dir / "config"
        self.stats_dir.mkdir(parents=True, exist_ok=True)
        
        # Fichiers de sortie
        self.medians_path = self.stats_dir / "medians.json"
        self.cats_path = self.stats_dir / "cats.json"
    
    def load_timeseries_data(self):
        """Charge les données des séries temporelles"""
        logger.info("📊 CHARGEMENT DES DONNÉES SÉRIES TEMPORELLES")
        logger.info("=" * 50)
        
        try:
            # Charger les séries quotidiennes
            daily_file = self.timeseries_dir / "daily_emergency_series_simple.parquet"
            if not daily_file.exists():
                logger.error(f"❌ Fichier non trouvé: {daily_file}")
                return None
            
            df = pd.read_parquet(daily_file)
            logger.info(f"✅ Données chargées: {df.shape}")
            logger.info(f"📅 Période: {df['date'].min()} à {df['date'].max()}")
            logger.info(f"🗺️ Départements: {df['department'].nunique()}")
            
            return df
            
        except Exception as e:
            logger.error(f"❌ Erreur chargement: {e}")
            return None
    
    def calculate_medians(self, df):
        """Calcule les médianes pour les variables numériques"""
        logger.info("📊 CALCUL DES MÉDIANES")
        logger.info("=" * 50)
        
        try:
            # Identifier les colonnes numériques
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            logger.info(f"📊 Colonnes numériques: {numeric_cols}")
            
            # Calculer les médianes
            medians = {}
            for col in numeric_cols:
                if col not in ['year', 'month', 'day_of_week', 'week_of_year', 'quarter']:
                    median_val = df[col].median()
                    medians[col] = float(median_val) if not pd.isna(median_val) else 0.0
                    logger.info(f"  - {col}: {medians[col]:.2f}")
            
            # Ajouter des médianes par département pour les variables clés
            key_vars = ['covid_cases', 'covid_cases_ma7', 'covid_cases_ma30']
            for var in key_vars:
                if var in df.columns:
                    dept_medians = df.groupby('department')[var].median().to_dict()
                    medians[f"{var}_by_dept"] = {str(k): float(v) if not pd.isna(v) else 0.0 
                                                for k, v in dept_medians.items()}
                    logger.info(f"  - {var}_by_dept: {len(dept_medians)} départements")
            
            logger.info(f"✅ Médianes calculées: {len(medians)} variables")
            return medians
            
        except Exception as e:
            logger.error(f"❌ Erreur calcul médianes: {e}")
            return {}
    
    def calculate_categories(self, df):
        """Calcule les catégories pour les variables catégorielles"""
        logger.info("📊 CALCUL DES CATÉGORIES")
        logger.info("=" * 50)
        
        try:
            # Identifier les colonnes catégorielles
            categorical_cols = ['department', 'is_weekend', 'is_peak_season']
            
            # Ajouter les colonnes temporelles comme catégories
            if 'month' in df.columns:
                categorical_cols.append('month')
            if 'quarter' in df.columns:
                categorical_cols.append('quarter')
            if 'day_of_week' in df.columns:
                categorical_cols.append('day_of_week')
            
            cats = {}
            
            for col in categorical_cols:
                if col in df.columns:
                    unique_vals = sorted(df[col].unique().tolist())
                    # Convertir en string pour JSON
                    cats[col] = [str(v) for v in unique_vals]
                    logger.info(f"  - {col}: {len(unique_vals)} catégories")
            
            # Ajouter des catégories dérivées
            if 'month' in df.columns:
                # Saisons
                cats['season'] = ['winter', 'spring', 'summer', 'autumn']
                logger.info(f"  - season: 4 catégories")
            
            # Catégories de température (si disponible)
            cats['temp_category'] = ['cold', 'mild', 'hot']
            logger.info(f"  - temp_category: 3 catégories")
            
            logger.info(f"✅ Catégories calculées: {len(cats)} variables")
            return cats
            
        except Exception as e:
            logger.error(f"❌ Erreur calcul catégories: {e}")
            return {}
    
    def save_stats(self, medians, cats):
        """Sauvegarde les statistiques"""
        logger.info("💾 SAUVEGARDE DES STATISTIQUES")
        logger.info("=" * 50)
        
        try:
            # Sauvegarder les médianes
            with open(self.medians_path, 'w', encoding='utf-8') as f:
                json.dump(medians, f, indent=2, ensure_ascii=False)
            logger.info(f"✅ Médianes sauvegardées: {self.medians_path}")
            
            # Sauvegarder les catégories
            with open(self.cats_path, 'w', encoding='utf-8') as f:
                json.dump(cats, f, indent=2, ensure_ascii=False)
            logger.info(f"✅ Catégories sauvegardées: {self.cats_path}")
            
            # Créer un résumé
            summary = {
                "generated_at": datetime.now().isoformat(),
                "medians_count": len(medians),
                "categories_count": len(cats),
                "medians_variables": list(medians.keys()),
                "categories_variables": list(cats.keys())
            }
            
            summary_path = self.stats_dir / "stats_summary.json"
            with open(summary_path, 'w', encoding='utf-8') as f:
                json.dump(summary, f, indent=2, ensure_ascii=False)
            
            logger.info(f"📋 Résumé sauvegardé: {summary_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur sauvegarde: {e}")
            return False
    
    def run_fit_stats(self):
        """Lance le calcul des statistiques"""
        logger.info("🚀 DÉBUT DU CALCUL DES STATISTIQUES")
        logger.info("=" * 60)
        
        # Charger les données
        df = self.load_timeseries_data()
        if df is None:
            return False
        
        # Calculer les médianes
        medians = self.calculate_medians(df)
        if not medians:
            return False
        
        # Calculer les catégories
        cats = self.calculate_categories(df)
        if not cats:
            return False
        
        # Sauvegarder
        success = self.save_stats(medians, cats)
        
        if success:
            logger.info("✅ CALCUL DES STATISTIQUES TERMINÉ")
            logger.info("=" * 60)
            return True
        else:
            logger.error("❌ ÉCHEC DU CALCUL DES STATISTIQUES")
            return False

if __name__ == "__main__":
    fitter = StatsFitter()
    fitter.run_fit_stats()
