#!/usr/bin/env python3
"""
Script pour entraîner un modèle RandomForest avec split temporel,
afficher la MAE, et sauvegarder les artefacts
"""

import pandas as pd
import numpy as np
from pathlib import Path
import logging
import json
import joblib
from datetime import datetime
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import TimeSeriesSplit
import warnings
warnings.filterwarnings('ignore')

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RandomForestTrainer:
    def __init__(self):
        self.base_dir = Path("data")
        self.features_dir = self.base_dir / "features"
        self.artifacts_dir = self.base_dir / "artifacts"
        self.artifacts_dir.mkdir(parents=True, exist_ok=True)
        
        # Fichiers d'entrée
        self.features_path = self.features_dir / "features.parquet"
        self.target_path = self.features_dir / "y_target.parquet"
        self.feature_list_path = self.features_dir / "feature_list.json"
        
        # Fichiers de sortie
        self.model_path = self.artifacts_dir / "rf.joblib"
        self.feature_importance_path = self.artifacts_dir / "feature_importance.json"
        self.metrics_path = self.artifacts_dir / "metrics.json"
    
    def load_data(self):
        """Charge les features et la target"""
        logger.info("📊 CHARGEMENT DES DONNÉES")
        logger.info("=" * 50)
        
        try:
            # Charger les features
            if not self.features_path.exists():
                logger.error(f"❌ Fichier features non trouvé: {self.features_path}")
                return None, None, None
            
            X = pd.read_parquet(self.features_path)
            logger.info(f"✅ Features chargées: {X.shape}")
            
            # Charger la target
            if not self.target_path.exists():
                logger.error(f"❌ Fichier target non trouvé: {self.target_path}")
                return None, None, None
            
            y_df = pd.read_parquet(self.target_path)
            y = y_df['y_target'].values
            logger.info(f"✅ Target chargée: {len(y)} échantillons")
            
            # Charger la liste des features
            feature_list = {}
            if self.feature_list_path.exists():
                with open(self.feature_list_path, 'r', encoding='utf-8') as f:
                    feature_list = json.load(f)
                logger.info(f"✅ Liste des features chargée: {len(feature_list.get('feature_names', []))} features")
            
            return X, y, feature_list
            
        except Exception as e:
            logger.error(f"❌ Erreur chargement: {e}")
            return None, None, None
    
    def create_temporal_split(self, X, y, test_size=0.2):
        """Crée un split temporel pour les séries temporelles"""
        logger.info("📅 CRÉATION DU SPLIT TEMPOREL")
        logger.info("=" * 50)
        
        try:
            # Calculer l'index de split
            split_idx = int(len(X) * (1 - test_size))
            
            # Split temporel
            X_train = X.iloc[:split_idx]
            X_test = X.iloc[split_idx:]
            y_train = y[:split_idx]
            y_test = y[split_idx:]
            
            logger.info(f"✅ Split temporel créé:")
            logger.info(f"  - Train: {X_train.shape[0]} échantillons")
            logger.info(f"  - Test: {X_test.shape[0]} échantillons")
            logger.info(f"  - Ratio test: {len(y_test)/len(y):.2%}")
            
            return X_train, X_test, y_train, y_test
            
        except Exception as e:
            logger.error(f"❌ Erreur split temporel: {e}")
            return None, None, None, None
    
    def train_model(self, X_train, y_train):
        """Entraîne le modèle RandomForest"""
        logger.info("🤖 ENTRAÎNEMENT DU MODÈLE RANDOM FOREST")
        logger.info("=" * 50)
        
        try:
            # Configuration du modèle
            rf_params = {
                'n_estimators': 100,
                'max_depth': 20,
                'min_samples_split': 5,
                'min_samples_leaf': 2,
                'max_features': 'sqrt',
                'random_state': 42,
                'n_jobs': -1
            }
            
            logger.info(f"📊 Paramètres du modèle: {rf_params}")
            
            # Entraînement
            model = RandomForestRegressor(**rf_params)
            model.fit(X_train, y_train)
            
            logger.info("✅ Modèle entraîné avec succès")
            return model
            
        except Exception as e:
            logger.error(f"❌ Erreur entraînement: {e}")
            return None
    
    def evaluate_model(self, model, X_test, y_test):
        """Évalue le modèle"""
        logger.info("📊 ÉVALUATION DU MODÈLE")
        logger.info("=" * 50)
        
        try:
            # Prédictions
            y_pred = model.predict(X_test)
            
            # Métriques
            mae = mean_absolute_error(y_test, y_pred)
            mse = mean_squared_error(y_test, y_pred)
            rmse = np.sqrt(mse)
            r2 = r2_score(y_test, y_pred)
            
            # Métriques relatives
            mae_relative = mae / np.mean(y_test) * 100
            rmse_relative = rmse / np.mean(y_test) * 100
            
            metrics = {
                "mae": float(mae),
                "mse": float(mse),
                "rmse": float(rmse),
                "r2": float(r2),
                "mae_relative": float(mae_relative),
                "rmse_relative": float(rmse_relative),
                "mean_target": float(np.mean(y_test)),
                "std_target": float(np.std(y_test))
            }
            
            logger.info(f"📊 MÉTRIQUES DU MODÈLE:")
            logger.info(f"  - MAE: {mae:.2f} ({mae_relative:.1f}%)")
            logger.info(f"  - RMSE: {rmse:.2f} ({rmse_relative:.1f}%)")
            logger.info(f"  - R²: {r2:.3f}")
            logger.info(f"  - Moyenne target: {np.mean(y_test):.2f}")
            logger.info(f"  - Écart-type target: {np.std(y_test):.2f}")
            
            return metrics, y_pred
            
        except Exception as e:
            logger.error(f"❌ Erreur évaluation: {e}")
            return None, None
    
    def analyze_feature_importance(self, model, feature_names):
        """Analyse l'importance des features"""
        logger.info("🔍 ANALYSE DE L'IMPORTANCE DES FEATURES")
        logger.info("=" * 50)
        
        try:
            # Importance des features
            importance = model.feature_importances_
            
            # Créer un DataFrame
            feature_importance = pd.DataFrame({
                'feature': feature_names,
                'importance': importance
            }).sort_values('importance', ascending=False)
            
            # Top 20 features
            top_features = feature_importance.head(20)
            
            logger.info("🏆 TOP 20 FEATURES LES PLUS IMPORTANTES:")
            for idx, row in top_features.iterrows():
                logger.info(f"  {row['feature']}: {row['importance']:.4f}")
            
            # Sauvegarder l'importance
            importance_dict = {
                "feature_importance": feature_importance.to_dict('records'),
                "top_10_features": top_features.head(10).to_dict('records'),
                "total_features": len(feature_names),
                "mean_importance": float(np.mean(importance)),
                "std_importance": float(np.std(importance))
            }
            
            return importance_dict
            
        except Exception as e:
            logger.error(f"❌ Erreur analyse importance: {e}")
            return None
    
    def save_artifacts(self, model, metrics, feature_importance, feature_list):
        """Sauvegarde les artefacts du modèle"""
        logger.info("💾 SAUVEGARDE DES ARTEFACTS")
        logger.info("=" * 50)
        
        try:
            # Sauvegarder le modèle
            joblib.dump(model, self.model_path)
            logger.info(f"✅ Modèle sauvegardé: {self.model_path}")
            
            # Sauvegarder les métriques
            with open(self.metrics_path, 'w', encoding='utf-8') as f:
                json.dump(metrics, f, indent=2, ensure_ascii=False)
            logger.info(f"✅ Métriques sauvegardées: {self.metrics_path}")
            
            # Sauvegarder l'importance des features
            with open(self.feature_importance_path, 'w', encoding='utf-8') as f:
                json.dump(feature_importance, f, indent=2, ensure_ascii=False)
            logger.info(f"✅ Importance des features sauvegardée: {self.feature_importance_path}")
            
            # Créer un résumé
            summary = {
                "model_info": {
                    "type": "RandomForestRegressor",
                    "n_estimators": model.n_estimators,
                    "max_depth": model.max_depth,
                    "features_count": len(feature_list.get('feature_names', [])),
                    "trained_at": datetime.now().isoformat()
                },
                "performance": metrics,
                "feature_importance": {
                    "top_5_features": feature_importance.get('top_10_features', [])[:5],
                    "total_features": feature_importance.get('total_features', 0)
                }
            }
            
            summary_path = self.artifacts_dir / "model_summary.json"
            with open(summary_path, 'w', encoding='utf-8') as f:
                json.dump(summary, f, indent=2, ensure_ascii=False)
            
            logger.info(f"📋 Résumé du modèle sauvegardé: {summary_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur sauvegarde: {e}")
            return False
    
    def run_training(self):
        """Lance l'entraînement complet"""
        logger.info("🚀 DÉBUT DE L'ENTRAÎNEMENT DU MODÈLE")
        logger.info("=" * 60)
        
        # Charger les données
        X, y, feature_list = self.load_data()
        if X is None:
            return False
        
        # Créer le split temporel
        X_train, X_test, y_train, y_test = self.create_temporal_split(X, y)
        if X_train is None:
            return False
        
        # Entraîner le modèle
        model = self.train_model(X_train, y_train)
        if model is None:
            return False
        
        # Évaluer le modèle
        metrics, y_pred = self.evaluate_model(model, X_test, y_test)
        if metrics is None:
            return False
        
        # Analyser l'importance des features
        feature_names = feature_list.get('feature_names', X.columns.tolist())
        feature_importance = self.analyze_feature_importance(model, feature_names)
        if feature_importance is None:
            return False
        
        # Sauvegarder les artefacts
        success = self.save_artifacts(model, metrics, feature_importance, feature_list)
        
        if success:
            logger.info("✅ ENTRAÎNEMENT TERMINÉ AVEC SUCCÈS")
            logger.info("=" * 60)
            logger.info(f"🎯 MAE Final: {metrics['mae']:.2f} ({metrics['mae_relative']:.1f}%)")
            logger.info(f"📊 R² Final: {metrics['r2']:.3f}")
            logger.info(f"💾 Modèle sauvegardé: {self.model_path}")
            return True
        else:
            logger.error("❌ ÉCHEC DE L'ENTRAÎNEMENT")
            return False

if __name__ == "__main__":
    trainer = RandomForestTrainer()
    trainer.run_training()
