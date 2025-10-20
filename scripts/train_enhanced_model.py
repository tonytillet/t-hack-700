#!/usr/bin/env python3
"""
Script d'entraînement du modèle amélioré avec features temporelles
Utilise la comparaison inter-années (N-2, N-1, N) pour prédire N+1
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import TimeSeriesSplit, RandomizedSearchCV
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.preprocessing import StandardScaler
import joblib
import os
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class EnhancedFluPredictor:
    def __init__(self):
        """Initialise le prédicteur de grippe amélioré"""
        self.model = None
        self.scaler = StandardScaler()
        self.feature_columns = []
        self.target_columns = []
        self.feature_importance = None
        
    def load_enhanced_data(self, filepath):
        """Charge le dataset amélioré avec features temporelles"""
        print(f"📂 Chargement du dataset amélioré: {filepath}")
        
        self.data = pd.read_csv(filepath)
        self.data['date'] = pd.to_datetime(self.data['date'])
        
        print(f"  ✅ Dataset chargé: {len(self.data)} enregistrements, {len(self.data.columns)} colonnes")
        print(f"  📅 Période: {self.data['date'].min().strftime('%Y-%m-%d')} à {self.data['date'].max().strftime('%Y-%m-%d')}")
        
        return self.data
    
    def prepare_enhanced_features(self):
        """Prépare les features améliorées avec comparaison inter-années"""
        print("\n🔧 Préparation des features améliorées...")
        
        df = self.data.copy()
        df = df.sort_values(['region', 'date']).reset_index(drop=True)
        
        # Features de base
        base_features = [
            'urgences_grippe', 'cas_sentinelles', 'ias_syndrome_grippal',
            'google_trends_grippe', 'google_trends_vaccin', 'google_trends_symptomes',
            'wiki_grippe_views', 'wiki_vaccination_views',
            'temperature', 'humidity', 'taux_vaccination', 'population_65_plus_pct'
        ]
        
        # Features temporelles de base
        temporal_features = []
        for feature in base_features:
            if feature in df.columns:
                # Lags 1-4 semaines
                for lag in range(1, 5):
                    df[f'{feature}_lag_{lag}'] = df.groupby('region')[feature].shift(lag)
                    temporal_features.append(f'{feature}_lag_{lag}')
                
                # Moyennes mobiles 2-4 semaines
                for window in [2, 4]:
                    df[f'{feature}_ma_{window}'] = df.groupby('region')[feature].rolling(window=window, min_periods=1).mean().reset_index(0, drop=True)
                    temporal_features.append(f'{feature}_ma_{window}')
        
        # Features de comparaison inter-années
        yearly_features = []
        for feature in ['urgences_grippe', 'cas_sentinelles', 'ias_syndrome_grippal']:
            if feature in df.columns:
                # Features N-2, N-1, N
                yearly_features.extend([
                    f'{feature}_year_minus_2', f'{feature}_year_minus_1', f'{feature}_year_current',
                    f'{feature}_diff_n1_n2', f'{feature}_diff_n_n1', f'{feature}_diff_n_n2',
                    f'{feature}_ratio_n_n1', f'{feature}_ratio_n_n2',
                    f'{feature}_mean_3years', f'{feature}_std_3years', f'{feature}_zscore_3years'
                ])
        
        # Features saisonnières
        seasonal_features = []
        for feature in ['urgences_grippe', 'cas_sentinelles']:
            if f'{feature}_seasonal_anomaly' in df.columns:
                seasonal_features.append(f'{feature}_seasonal_anomaly')
        
        # Features d'épidémie
        epidemic_features = []
        for feature in ['urgences_grippe', 'cas_sentinelles']:
            if f'{feature}_epidemic_level' in df.columns:
                epidemic_features.extend([
                    f'{feature}_epidemic_level', f'{feature}_distance_to_epidemic', f'{feature}_epidemic_probability'
                ])
        
        # Features de tendance
        trend_features = []
        for feature in ['urgences_grippe', 'cas_sentinelles']:
            if f'{feature}_trend' in df.columns:
                trend_features.extend([f'{feature}_trend', f'{feature}_trend_ratio'])
        
        # Features météo et démographiques
        context_features = ['temperature', 'humidity', 'taux_vaccination', 'population_65_plus_pct']
        
        # Features Google Trends et Wikipedia
        trends_features = ['google_trends_grippe', 'google_trends_vaccin', 'google_trends_symptomes']
        wiki_features = ['wiki_grippe_views', 'wiki_vaccination_views']
        
        # Combinaison de toutes les features
        all_features = (base_features + temporal_features + yearly_features + 
                       seasonal_features + epidemic_features + trend_features + 
                       context_features + trends_features + wiki_features)
        
        # Filtrage des features disponibles
        available_features = [f for f in all_features if f in df.columns]
        
        print(f"  📊 Features disponibles: {len(available_features)}")
        print(f"    - Features de base: {len([f for f in base_features if f in df.columns])}")
        print(f"    - Features temporelles: {len(temporal_features)}")
        print(f"    - Features inter-années: {len(yearly_features)}")
        print(f"    - Features saisonnières: {len(seasonal_features)}")
        print(f"    - Features d'épidémie: {len(epidemic_features)}")
        print(f"    - Features de tendance: {len(trend_features)}")
        
        self.feature_columns = available_features
        return df
    
    def create_multi_horizon_targets(self, df):
        """Crée les targets multi-horizons (J+1, J+7, J+14, J+21, J+28)"""
        print("\n🎯 Création des targets multi-horizons...")
        
        # Targets pour les urgences grippe
        if 'urgences_grippe' in df.columns:
            df['target_urgences_j1'] = df.groupby('region')['urgences_grippe'].shift(-1)
            df['target_urgences_j7'] = df.groupby('region')['urgences_grippe'].shift(-7)
            df['target_urgences_j14'] = df.groupby('region')['urgences_grippe'].shift(-14)
            df['target_urgences_j21'] = df.groupby('region')['urgences_grippe'].shift(-21)
            df['target_urgences_j28'] = df.groupby('region')['urgences_grippe'].shift(-28)
            
            self.target_columns = ['target_urgences_j1', 'target_urgences_j7', 'target_urgences_j14', 'target_urgences_j21', 'target_urgences_j28']
            print(f"  ✅ Targets créés: {len(self.target_columns)} horizons")
        
        return df
    
    def prepare_training_data(self, df):
        """Prépare les données d'entraînement"""
        print("\n📊 Préparation des données d'entraînement...")
        
        # Suppression des lignes avec valeurs manquantes
        df_clean = df.dropna(subset=self.feature_columns + self.target_columns)
        
        print(f"  📊 Données après nettoyage: {len(df_clean)} enregistrements")
        
        # Séparation des features et targets
        X = df_clean[self.feature_columns]
        y = df_clean[self.target_columns]
        
        # Normalisation des features
        X_scaled = self.scaler.fit_transform(X)
        
        print(f"  ✅ Features normalisées: {X_scaled.shape}")
        print(f"  ✅ Targets préparés: {y.shape}")
        
        return X_scaled, y, df_clean
    
    def train_enhanced_model(self, X, y):
        """Entraîne le modèle Random Forest amélioré"""
        print("\n🤖 Entraînement du modèle Random Forest amélioré...")
        
        # Configuration du modèle
        rf_params = {
            'n_estimators': [100, 200, 300],
            'max_depth': [10, 20, 30, None],
            'min_samples_split': [2, 5, 10],
            'min_samples_leaf': [1, 2, 4],
            'max_features': ['sqrt', 'log2', None],
            'bootstrap': [True, False]
        }
        
        # Validation croisée temporelle
        tscv = TimeSeriesSplit(n_splits=5)
        
        # Recherche d'hyperparamètres
        rf = RandomForestRegressor(random_state=42, n_jobs=-1)
        random_search = RandomizedSearchCV(
            rf, rf_params, n_iter=50, cv=tscv, 
            scoring='neg_mean_absolute_error', 
            random_state=42, n_jobs=-1
        )
        
        # Entraînement
        print("  🔄 Recherche des meilleurs hyperparamètres...")
        random_search.fit(X, y)
        
        self.model = random_search.best_estimator_
        self.feature_importance = self.model.feature_importances_
        
        print(f"  ✅ Meilleurs paramètres: {random_search.best_params_}")
        print(f"  ✅ Score CV: {-random_search.best_score_:.2f} MAE")
        
        return self.model
    
    def evaluate_model(self, X, y, df_clean):
        """Évalue le modèle sur les données de test"""
        print("\n📊 Évaluation du modèle...")
        
        # Prédictions
        y_pred = self.model.predict(X)
        
        # Métriques par horizon
        results = {}
        for i, target in enumerate(self.target_columns):
            mae = mean_absolute_error(y.iloc[:, i], y_pred[:, i])
            r2 = r2_score(y.iloc[:, i], y_pred[:, i])
            
            results[target] = {'MAE': mae, 'R²': r2}
            
            print(f"  📈 {target}: MAE={mae:.2f}, R²={r2:.3f}")
        
        # Importance des features
        feature_importance_df = pd.DataFrame({
            'feature': self.feature_columns,
            'importance': self.feature_importance
        }).sort_values('importance', ascending=False)
        
        print(f"\n🔝 Top 10 des features les plus importantes:")
        for i, row in feature_importance_df.head(10).iterrows():
            print(f"  {row['feature']}: {row['importance']:.3f}")
        
        return results, feature_importance_df
    
    def save_model(self, model_path=None):
        """Sauvegarde le modèle entraîné"""
        if model_path is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            model_path = f'models/flu_predictor_enhanced_{timestamp}.joblib'
        
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        
        # Sauvegarde du modèle et du scaler
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'feature_columns': self.feature_columns,
            'target_columns': self.target_columns,
            'feature_importance': self.feature_importance
        }
        
        joblib.dump(model_data, model_path)
        print(f"💾 Modèle sauvegardé: {model_path}")
        
        return model_path

def main():
    """Fonction principale"""
    print("🚀 ENTRAÎNEMENT DU MODÈLE AMÉLIORÉ")
    print("=" * 60)
    
    # Chargement du dataset amélioré
    dataset_file = 'data/processed/dataset_grippe_enhanced_20251020_195427.csv'
    if not os.path.exists(dataset_file):
        print(f"❌ Dataset amélioré non trouvé: {dataset_file}")
        return
    
    # Initialisation
    predictor = EnhancedFluPredictor()
    df = predictor.load_enhanced_data(dataset_file)
    
    # Préparation des features
    df = predictor.prepare_enhanced_features()
    
    # Création des targets
    df = predictor.create_multi_horizon_targets(df)
    
    # Préparation des données d'entraînement
    X, y, df_clean = predictor.prepare_training_data(df)
    
    # Entraînement du modèle
    model = predictor.train_enhanced_model(X, y)
    
    # Évaluation
    results, feature_importance = predictor.evaluate_model(X, y, df_clean)
    
    # Sauvegarde
    model_path = predictor.save_model()
    
    print(f"\n✅ ENTRAÎNEMENT TERMINÉ")
    print(f"📁 Modèle sauvegardé: {model_path}")
    print(f"📊 Performance moyenne MAE: {np.mean([r['MAE'] for r in results.values()]):.2f}")
    print(f"📊 Performance moyenne R²: {np.mean([r['R²'] for r in results.values()]):.3f}")

if __name__ == "__main__":
    main()
