#!/usr/bin/env python3
"""
Script pour faire des prédictions avec le modèle entraîné
"""

import pandas as pd
import numpy as np
from pathlib import Path
import logging
import json
import joblib
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Predictor:
    def __init__(self):
        self.base_dir = Path("data")
        self.features_dir = self.base_dir / "features"
        self.artifacts_dir = self.base_dir / "artifacts"
        self.predictions_dir = self.base_dir / "predictions"
        self.predictions_dir.mkdir(parents=True, exist_ok=True)
        
        # Fichiers d'entrée
        self.model_path = self.artifacts_dir / "rf.joblib"
        self.features_path = self.features_dir / "features.parquet"
        self.target_path = self.features_dir / "y_target.parquet"
        self.feature_list_path = self.features_dir / "feature_list.json"
        
        # Fichiers de sortie
        self.predictions_path = self.predictions_dir / "predictions.parquet"
        self.predictions_summary_path = self.predictions_dir / "predictions_summary.json"
    
    def load_model_and_data(self):
        """Charge le modèle et les données"""
        logger.info("📊 CHARGEMENT DU MODÈLE ET DES DONNÉES")
        logger.info("=" * 50)
        
        try:
            # Charger le modèle
            if not self.model_path.exists():
                logger.error(f"❌ Modèle non trouvé: {self.model_path}")
                return None, None, None, None
            
            model = joblib.load(self.model_path)
            logger.info(f"✅ Modèle chargé: {type(model).__name__}")
            
            # Charger les features
            if not self.features_path.exists():
                logger.error(f"❌ Features non trouvées: {self.features_path}")
                return None, None, None, None
            
            X = pd.read_parquet(self.features_path)
            logger.info(f"✅ Features chargées: {X.shape}")
            
            # Charger la target (pour comparaison)
            y_df = pd.read_parquet(self.target_path)
            logger.info(f"✅ Target chargée: {y_df.shape}")
            
            # Charger la liste des features
            feature_list = {}
            if self.feature_list_path.exists():
                with open(self.feature_list_path, 'r', encoding='utf-8') as f:
                    feature_list = json.load(f)
                logger.info(f"✅ Liste des features chargée: {len(feature_list.get('feature_names', []))} features")
            
            return model, X, y_df, feature_list
            
        except Exception as e:
            logger.error(f"❌ Erreur chargement: {e}")
            return None, None, None, None
    
    def make_predictions(self, model, X, y_df):
        """Fait les prédictions"""
        logger.info("🔮 GÉNÉRATION DES PRÉDICTIONS")
        logger.info("=" * 50)
        
        try:
            # Prédictions
            predictions = model.predict(X)
            
            # Créer le DataFrame de prédictions
            pred_df = y_df.copy()
            pred_df['prediction'] = predictions
            pred_df['prediction_date'] = pred_df['date'] + timedelta(days=7)
            pred_df['error'] = pred_df['y_target'] - pred_df['prediction']
            pred_df['abs_error'] = np.abs(pred_df['error'])
            pred_df['relative_error'] = pred_df['abs_error'] / (pred_df['y_target'] + 1e-6) * 100
            
            logger.info(f"✅ Prédictions générées: {len(predictions)} échantillons")
            logger.info(f"📅 Période des prédictions: {pred_df['date'].min()} à {pred_df['date'].max()}")
            
            return pred_df
            
        except Exception as e:
            logger.error(f"❌ Erreur prédictions: {e}")
            return None
    
    def analyze_predictions(self, pred_df):
        """Analyse les prédictions"""
        logger.info("📊 ANALYSE DES PRÉDICTIONS")
        logger.info("=" * 50)
        
        try:
            # Métriques globales
            mae = pred_df['abs_error'].mean()
            rmse = np.sqrt((pred_df['error'] ** 2).mean())
            mape = pred_df['relative_error'].mean()
            r2 = 1 - (pred_df['error'] ** 2).sum() / ((pred_df['y_target'] - pred_df['y_target'].mean()) ** 2).sum()
            
            # Métriques par département
            dept_metrics = pred_df.groupby('department').agg({
                'abs_error': 'mean',
                'relative_error': 'mean',
                'y_target': ['mean', 'std'],
                'prediction': ['mean', 'std']
            }).round(2)
            
            # Top 10 meilleures prédictions
            best_predictions = pred_df.nsmallest(10, 'abs_error')[['date', 'department', 'y_target', 'prediction', 'abs_error']]
            
            # Top 10 pires prédictions
            worst_predictions = pred_df.nlargest(10, 'abs_error')[['date', 'department', 'y_target', 'prediction', 'abs_error']]
            
            analysis = {
                "global_metrics": {
                    "mae": float(mae),
                    "rmse": float(rmse),
                    "mape": float(mape),
                    "r2": float(r2),
                    "total_predictions": len(pred_df)
                },
                "department_metrics": dept_metrics.to_dict(),
                "best_predictions": best_predictions.to_dict('records'),
                "worst_predictions": worst_predictions.to_dict('records'),
                "prediction_stats": {
                    "mean_target": float(pred_df['y_target'].mean()),
                    "mean_prediction": float(pred_df['prediction'].mean()),
                    "std_target": float(pred_df['y_target'].std()),
                    "std_prediction": float(pred_df['prediction'].std())
                }
            }
            
            logger.info(f"📊 MÉTRIQUES GLOBALES:")
            logger.info(f"  - MAE: {mae:.2f}")
            logger.info(f"  - RMSE: {rmse:.2f}")
            logger.info(f"  - MAPE: {mape:.1f}%")
            logger.info(f"  - R²: {r2:.3f}")
            
            return analysis
            
        except Exception as e:
            logger.error(f"❌ Erreur analyse: {e}")
            return None
    
    def save_predictions(self, pred_df, analysis):
        """Sauvegarde les prédictions et l'analyse"""
        logger.info("💾 SAUVEGARDE DES PRÉDICTIONS")
        logger.info("=" * 50)
        
        try:
            # Sauvegarder les prédictions
            pred_df.to_parquet(self.predictions_path, index=False)
            logger.info(f"✅ Prédictions sauvegardées: {self.predictions_path}")
            
            # Sauvegarder l'analyse
            with open(self.predictions_summary_path, 'w', encoding='utf-8') as f:
                json.dump(analysis, f, indent=2, ensure_ascii=False)
            logger.info(f"✅ Analyse sauvegardée: {self.predictions_summary_path}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur sauvegarde: {e}")
            return False
    
    def run_prediction(self):
        """Lance la prédiction complète"""
        logger.info("🚀 DÉBUT DE LA PRÉDICTION")
        logger.info("=" * 60)
        
        # Charger le modèle et les données
        model, X, y_df, feature_list = self.load_model_and_data()
        if model is None:
            return False
        
        # Faire les prédictions
        pred_df = self.make_predictions(model, X, y_df)
        if pred_df is None:
            return False
        
        # Analyser les prédictions
        analysis = self.analyze_predictions(pred_df)
        if analysis is None:
            return False
        
        # Sauvegarder
        success = self.save_predictions(pred_df, analysis)
        
        if success:
            logger.info("✅ PRÉDICTION TERMINÉE AVEC SUCCÈS")
            logger.info("=" * 60)
            logger.info(f"🎯 MAE: {analysis['global_metrics']['mae']:.2f}")
            logger.info(f"📊 R²: {analysis['global_metrics']['r2']:.3f}")
            logger.info(f"💾 Prédictions sauvegardées: {self.predictions_path}")
            return True
        else:
            logger.error("❌ ÉCHEC DE LA PRÉDICTION")
            return False

if __name__ == "__main__":
    predictor = Predictor()
    predictor.run_prediction()
