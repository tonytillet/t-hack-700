#!/usr/bin/env python3
"""
Script d'entraînement du modèle Random Forest pour la prédiction grippe
Utilise le dataset fusionné pour prédire les urgences J+7, J+14, J+21, J+28
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import TimeSeriesSplit, RandomizedSearchCV
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import joblib
import os
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class GrippePredictor:
    def __init__(self):
        """Initialise le prédicteur de grippe"""
        self.model = None
        self.feature_columns = None
        self.target_column = 'urgences_grippe'
        self.prediction_horizons = [7, 14, 21, 28]  # J+7, J+14, J+21, J+28
        
    def load_data(self, filepath):
        """Charge le dataset fusionné"""
        print(f"📂 Chargement du dataset: {filepath}")
        
        df = pd.read_csv(filepath)
        df['date'] = pd.to_datetime(df['date'])
        
        print(f"  ✅ Dataset chargé: {len(df)} enregistrements, {len(df.columns)} colonnes")
        print(f"  📅 Période: {df['date'].min().strftime('%Y-%m-%d')} à {df['date'].max().strftime('%Y-%m-%d')}")
        print(f"  🌍 Régions: {df['region'].nunique()}")
        
        return df
    
    def prepare_features(self, df):
        """Prépare les features pour l'entraînement"""
        print("\n🔧 Préparation des features...")
        
        # Sélection des features (exclusion des colonnes non pertinentes)
        exclude_cols = ['date', 'region', 'region_code', 'year', 'week_of_year']
        
        # Features de base
        feature_cols = [col for col in df.columns if col not in exclude_cols]
        
        # Suppression des colonnes avec trop de valeurs manquantes
        missing_threshold = 0.5
        valid_cols = []
        for col in feature_cols:
            if col != self.target_column:
                missing_pct = df[col].isna().sum() / len(df)
                if missing_pct < missing_threshold:
                    valid_cols.append(col)
                else:
                    print(f"  ⚠️ Colonne exclue (trop de NaN): {col} ({missing_pct:.1%})")
        
        self.feature_columns = valid_cols
        print(f"  ✅ {len(self.feature_columns)} features sélectionnées")
        
        # Nettoyage des données
        df_clean = df.copy()
        df_clean = df_clean.fillna(0)
        
        # Suppression des lignes avec target manquant
        df_clean = df_clean.dropna(subset=[self.target_column])
        
        print(f"  📊 Dataset nettoyé: {len(df_clean)} enregistrements")
        return df_clean
    
    def create_targets(self, df):
        """Crée les targets pour différents horizons de prédiction"""
        print("\n🎯 Création des targets multi-horizons...")
        
        df_with_targets = df.copy()
        
        for horizon in self.prediction_horizons:
            target_col = f'{self.target_column}_j{horizon}'
            
            # Création du target décalé
            df_with_targets[target_col] = df_with_targets.groupby('region')[self.target_column].shift(-horizon)
            
            # Statistiques
            valid_targets = df_with_targets[target_col].dropna()
            print(f"  ✅ J+{horizon}: {len(valid_targets)} targets valides")
        
        return df_with_targets
    
    def train_single_horizon(self, df, horizon, test_size=0.2):
        """Entraîne le modèle pour un horizon spécifique"""
        print(f"\n🚀 Entraînement modèle J+{horizon}...")
        
        target_col = f'{self.target_column}_j{horizon}'
        
        # Préparation des données
        df_train = df.dropna(subset=[target_col]).copy()
        
        if len(df_train) < 100:
            print(f"  ⚠️ Pas assez de données pour J+{horizon} ({len(df_train)} échantillons)")
            return None
        
        X = df_train[self.feature_columns]
        y = df_train[target_col]
        
        print(f"  📊 Données d'entraînement: {len(X)} échantillons, {len(self.feature_columns)} features")
        
        # Division temporelle
        split_idx = int(len(X) * (1 - test_size))
        X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
        y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]
        
        print(f"  📈 Train: {len(X_train)} échantillons")
        print(f"  📉 Test: {len(X_test)} échantillons")
        
        # Configuration du modèle
        rf = RandomForestRegressor(
            n_estimators=200,
            max_depth=15,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1
        )
        
        # Entraînement
        print("  ⏳ Entraînement en cours...")
        rf.fit(X_train, y_train)
        
        # Prédictions
        y_pred_train = rf.predict(X_train)
        y_pred_test = rf.predict(X_test)
        
        # Métriques
        train_mae = mean_absolute_error(y_train, y_pred_train)
        test_mae = mean_absolute_error(y_test, y_pred_test)
        train_r2 = r2_score(y_train, y_pred_train)
        test_r2 = r2_score(y_test, y_pred_test)
        
        print(f"  📊 Métriques J+{horizon}:")
        print(f"     Train MAE: {train_mae:.2f}, R²: {train_r2:.3f}")
        print(f"     Test MAE: {test_mae:.2f}, R²: {test_r2:.3f}")
        
        # Importance des features
        feature_importance = pd.DataFrame({
            'feature': self.feature_columns,
            'importance': rf.feature_importances_
        }).sort_values('importance', ascending=False)
        
        print(f"  🔍 Top 5 features importantes:")
        for _, row in feature_importance.head(5).iterrows():
            print(f"     {row['feature']}: {row['importance']:.3f}")
        
        return {
            'model': rf,
            'train_mae': train_mae,
            'test_mae': test_mae,
            'train_r2': train_r2,
            'test_r2': test_r2,
            'feature_importance': feature_importance,
            'horizon': horizon
        }
    
    def train_all_models(self, df):
        """Entraîne les modèles pour tous les horizons"""
        print("\n🎯 ENTRAÎNEMENT DES MODÈLES MULTI-HORIZONS")
        print("=" * 50)
        
        models = {}
        
        for horizon in self.prediction_horizons:
            model_result = self.train_single_horizon(df, horizon)
            if model_result is not None:
                models[f'j{horizon}'] = model_result
        
        return models
    
    def save_models(self, models, output_dir='../models'):
        """Sauvegarde les modèles entraînés"""
        print(f"\n💾 Sauvegarde des modèles...")
        
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        saved_models = {}
        
        for model_name, model_data in models.items():
            # Sauvegarde du modèle
            model_file = f'{output_dir}/rf_grippe_{model_name}_{timestamp}.pkl'
            joblib.dump(model_data['model'], model_file)
            
            # Sauvegarde des métriques
            metrics_file = f'{output_dir}/metrics_{model_name}_{timestamp}.csv'
            metrics_df = pd.DataFrame({
                'metric': ['train_mae', 'test_mae', 'train_r2', 'test_r2'],
                'value': [model_data['train_mae'], model_data['test_mae'], 
                         model_data['train_r2'], model_data['test_r2']]
            })
            metrics_df.to_csv(metrics_file, index=False)
            
            # Sauvegarde de l'importance des features
            importance_file = f'{output_dir}/importance_{model_name}_{timestamp}.csv'
            model_data['feature_importance'].to_csv(importance_file, index=False)
            
            saved_models[model_name] = {
                'model_file': model_file,
                'metrics_file': metrics_file,
                'importance_file': importance_file,
                'horizon': model_data['horizon']
            }
            
            print(f"  ✅ {model_name}: {model_file}")
        
        # Sauvegarde de la configuration
        config_file = f'{output_dir}/config_{timestamp}.json'
        import json
        config = {
            'feature_columns': self.feature_columns,
            'target_column': self.target_column,
            'prediction_horizons': self.prediction_horizons,
            'models': saved_models,
            'timestamp': timestamp
        }
        
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"  ✅ Configuration: {config_file}")
        return config
    
    def generate_predictions(self, df, models):
        """Génère les prédictions pour le dataset"""
        print(f"\n🔮 Génération des prédictions...")
        
        df_pred = df.copy()
        
        for model_name, model_data in models.items():
            horizon = model_data['horizon']
            target_col = f'{self.target_column}_j{horizon}'
            pred_col = f'pred_{target_col}'
            
            # Prédictions
            X = df_pred[self.feature_columns].fillna(0)
            predictions = model_data['model'].predict(X)
            
            df_pred[pred_col] = predictions
            
            print(f"  ✅ {model_name}: {len(predictions)} prédictions générées")
        
        return df_pred

def main():
    """Fonction principale d'entraînement"""
    print("🚀 ENTRAÎNEMENT DU MODÈLE RANDOM FOREST GRIPPE")
    print("=" * 60)
    
    # Initialisation
    predictor = GrippePredictor()
    
    # Recherche du dernier dataset
    processed_dir = '../data/processed'
    
    if not os.path.exists(processed_dir):
        print(f"❌ Dossier non trouvé: {processed_dir}")
        print("💡 Exécutez d'abord: python fuse_data.py")
        return
    
    # Liste des fichiers dataset_grippe_*.csv
    dataset_files = [f for f in os.listdir(processed_dir) if f.startswith('dataset_grippe_') and f.endswith('.csv')]
    
    if not dataset_files:
        print(f"❌ Aucun dataset trouvé dans {processed_dir}")
        print("💡 Exécutez d'abord: python fuse_data.py")
        return
    
    # Prendre le dernier fichier (tri par nom = tri par timestamp)
    latest_dataset = sorted(dataset_files)[-1]
    dataset_file = os.path.join(processed_dir, latest_dataset)
    
    print(f"📂 Chargement du dataset: {latest_dataset}")
    
    df = predictor.load_data(dataset_file)
    
    # Préparation des features
    df = predictor.prepare_features(df)
    
    # Création des targets
    df = predictor.create_targets(df)
    
    # Entraînement des modèles
    models = predictor.train_all_models(df)
    
    if not models:
        print("❌ Aucun modèle entraîné avec succès")
        return
    
    # Sauvegarde des modèles
    config = predictor.save_models(models)
    
    # Génération des prédictions
    df_pred = predictor.generate_predictions(df, models)
    
    # Sauvegarde du dataset avec prédictions
    output_file = f'../data/processed/dataset_with_predictions_{config["timestamp"]}.csv'
    df_pred.to_csv(output_file, index=False)
    print(f"\n💾 Dataset avec prédictions sauvegardé: {output_file}")
    
    # Résumé final
    print(f"\n✅ ENTRAÎNEMENT TERMINÉ")
    print(f"📊 {len(models)} modèles entraînés")
    print(f"🎯 Horizons: {list(models.keys())}")
    print(f"📁 Modèles sauvegardés dans: models/")

if __name__ == "__main__":
    main()
