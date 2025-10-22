#!/usr/bin/env python3
"""
🔄 LUMEN - MONITORING AUTO-RETRAIN
Système de monitoring automatique avec retrain et alertes
"""

import pandas as pd
import numpy as np
import joblib
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from pathlib import Path
import subprocess
import sys
import os
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
import warnings
warnings.filterwarnings('ignore')

class LUMENMonitoring:
    def __init__(self, 
                 data_path='data/processed/dataset.parquet',
                 models_dir='models',
                 logs_dir='monitoring/logs',
                 config_path='monitoring/config.json'):
        
        self.data_path = Path(data_path)
        self.models_dir = Path(models_dir)
        self.logs_dir = Path(logs_dir)
        self.config_path = Path(config_path)
        
        # Créer les répertoires
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        self.models_dir.mkdir(parents=True, exist_ok=True)
        
        # Charger la configuration
        self.config = self.load_config()
        
        # Métriques de référence
        self.baseline_metrics = {
            'r2_score': 0.95,  # Seuil minimum R²
            'mae': 2000,        # Seuil maximum MAE
            'performance_drop': 0.05  # Seuil de chute de performance (5%)
        }
    
    def load_config(self):
        """Charge la configuration du monitoring"""
        default_config = {
            "email": {
                "smtp_server": "smtp.gmail.com",
                "smtp_port": 587,
                "sender_email": "lumen.monitoring@example.com",
                "sender_password": "your_password_here",
                "recipients": ["admin@lumen.fr", "ml-team@lumen.fr"]
            },
            "monitoring": {
                "retrain_frequency_days": 7,
                "performance_threshold": 0.05,
                "alert_on_drop": True,
                "backup_models": True
            },
            "model": {
                "target_col": "target_demo",
                "test_size": 0.2,
                "random_state": 42
            }
        }
        
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                return json.load(f)
        else:
            # Créer le fichier de configuration par défaut
            with open(self.config_path, 'w') as f:
                json.dump(default_config, f, indent=2)
            return default_config
    
    def generate_demo_data(self):
        """Génère des données de démonstration pour le monitoring"""
        print("🎲 Génération de données de démonstration pour le monitoring...")
        
        np.random.seed(42)
        n_samples = 1000
        
        # Données de base avec variation temporelle
        data = {
            'date': pd.date_range('2023-01-01', periods=n_samples, freq='D'),
            'region': np.random.choice(['Grand Est', 'Île-de-France', 'Auvergne-Rhône-Alpes', 
                                      'Provence-Alpes-Côte d\'Azur', 'Occitanie', 'Nouvelle-Aquitaine'], n_samples),
            'departement': np.random.choice([f"{i:02d}" for i in range(1, 21)], n_samples),
            'population': np.random.randint(300000, 2000000, n_samples),
            'temperature_moyenne': np.random.normal(15, 10, n_samples),
            'humidite_moyenne': np.random.normal(70, 15, n_samples),
            'passages_urgences_grippe': np.random.poisson(1000, n_samples),
            'taux_incidence': np.random.normal(40, 15, n_samples),
            'couverture_vaccinale': np.random.uniform(0.2, 0.8, n_samples),
            'google_trends_grippe': np.random.uniform(0, 100, n_samples),
            'indice_lumen': np.random.uniform(60, 95, n_samples)
        }
        
        df = pd.DataFrame(data)
        
        # Ajouter des features temporelles
        df['jour_semaine'] = df['date'].dt.dayofweek
        df['mois'] = df['date'].dt.month
        df['saison'] = df['mois'].map({12:0, 1:0, 2:0, 3:1, 4:1, 5:1, 6:2, 7:2, 8:2, 9:3, 10:3, 11:3})
        
        # Features dérivées
        df['passages_per_100k'] = (df['passages_urgences_grippe'] / df['population'] * 100000)
        df['passages_log'] = np.log1p(df['passages_urgences_grippe'])
        df['incidence_log'] = np.log1p(df['taux_incidence'])
        df['lumen_log'] = np.log1p(df['indice_lumen'])
        
        # Moyennes mobiles
        df['passages_ma_7'] = df['passages_urgences_grippe'].rolling(7).mean()
        df['incidence_ma_7'] = df['taux_incidence'].rolling(7).mean()
        df['lumen_ma_7'] = df['indice_lumen'].rolling(7).mean()
        
        # Lags
        df['passages_lag_7'] = df['passages_urgences_grippe'].shift(7)
        df['incidence_lag_7'] = df['taux_incidence'].shift(7)
        df['lumen_lag_7'] = df['indice_lumen'].shift(7)
        
        # Target avec variation temporelle (simulation de dérive)
        base_target = (
            0.3 * df['passages_per_100k'] +
            0.25 * df['taux_incidence'] +
            0.2 * df['indice_lumen'] +
            0.15 * df['google_trends_grippe'] +
            0.1 * df['temperature_moyenne']
        )
        
        # Ajouter une dérive temporelle (simulation de changement de patterns)
        time_drift = np.sin(2 * np.pi * df['date'].dt.dayofyear / 365) * 0.1
        df['target_demo'] = base_target + time_drift + np.random.normal(0, 5, n_samples)
        
        return df
    
    def train_model(self, df):
        """Entraîne un nouveau modèle"""
        print("🤖 ENTRAÎNEMENT DU NOUVEAU MODÈLE")
        print("=" * 40)
        
        # Préparer les features
        feature_cols = [
            'population', 'temperature_moyenne', 'humidite_moyenne',
            'passages_urgences_grippe', 'taux_incidence', 'couverture_vaccinale',
            'google_trends_grippe', 'indice_lumen', 'jour_semaine', 'mois', 'saison',
            'passages_per_100k', 'passages_log', 'incidence_log', 'lumen_log',
            'passages_ma_7', 'incidence_ma_7', 'lumen_ma_7',
            'passages_lag_7', 'incidence_lag_7', 'lumen_lag_7'
        ]
        
        # Filtrer les colonnes existantes
        available_cols = [col for col in feature_cols if col in df.columns]
        X = df[available_cols].fillna(0)
        y = df['target_demo'].fillna(0)
        
        # Split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, 
            test_size=self.config['model']['test_size'],
            random_state=self.config['model']['random_state']
        )
        
        # Entraîner le modèle
        model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            n_jobs=-1
        )
        
        model.fit(X_train, y_train)
        
        # Évaluation
        y_pred = model.predict(X_test)
        r2 = r2_score(y_test, y_pred)
        mae = mean_absolute_error(y_test, y_pred)
        
        print(f"✅ Modèle entraîné")
        print(f"   📊 R² Score: {r2:.4f}")
        print(f"   📊 MAE: {mae:.4f}")
        
        return model, r2, mae, X.columns.tolist()
    
    def load_previous_model(self):
        """Charge le modèle précédent pour comparaison"""
        model_files = list(self.models_dir.glob("random_forest_regressor_*.joblib"))
        if not model_files:
            return None, None, None
        
        # Prendre le plus récent
        latest_model = max(model_files, key=lambda x: x.stat().st_mtime)
        
        try:
            model = joblib.load(latest_model)
            print(f"✅ Modèle précédent chargé: {latest_model.name}")
            return model, latest_model, None
        except Exception as e:
            print(f"❌ Erreur chargement modèle précédent: {e}")
            return None, None, None
    
    def compare_models(self, new_r2, new_mae, old_model, X_test, y_test):
        """Compare les performances des modèles"""
        print("\n📊 COMPARAISON DES MODÈLES")
        print("=" * 35)
        
        if old_model is None:
            print("⚠️ Aucun modèle précédent pour comparaison")
            return {
                'comparison': 'no_previous_model',
                'performance_drop': 0,
                'alert_needed': False
            }
        
        # Évaluer l'ancien modèle
        old_pred = old_model.predict(X_test)
        old_r2 = r2_score(y_test, old_pred)
        old_mae = mean_absolute_error(y_test, old_pred)
        
        # Calculer les différences
        r2_diff = new_r2 - old_r2
        mae_diff = new_mae - old_mae
        
        print(f"📊 Ancien modèle - R²: {old_r2:.4f}, MAE: {old_mae:.4f}")
        print(f"📊 Nouveau modèle - R²: {new_r2:.4f}, MAE: {new_mae:.4f}")
        print(f"📊 Différence R²: {r2_diff:+.4f}")
        print(f"📊 Différence MAE: {mae_diff:+.4f}")
        
        # Déterminer si une alerte est nécessaire
        performance_drop = abs(r2_diff) if r2_diff < 0 else 0
        alert_needed = (
            r2_diff < -self.baseline_metrics['performance_drop'] or
            new_r2 < self.baseline_metrics['r2_score'] or
            new_mae > self.baseline_metrics['mae']
        )
        
        comparison = {
            'old_r2': old_r2,
            'old_mae': old_mae,
            'new_r2': new_r2,
            'new_mae': new_mae,
            'r2_diff': r2_diff,
            'mae_diff': mae_diff,
            'performance_drop': performance_drop,
            'alert_needed': alert_needed
        }
        
        if alert_needed:
            print("🚨 ALERTE: Performance dégradée détectée!")
        else:
            print("✅ Performance acceptable")
        
        return comparison
    
    def save_model_with_metrics(self, model, r2, mae, feature_names, comparison):
        """Sauvegarde le modèle avec ses métriques"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Sauvegarder le modèle
        model_path = self.models_dir / f"random_forest_regressor_{timestamp}.joblib"
        joblib.dump(model, model_path)
        
        # Sauvegarder les métriques
        metrics = {
            'timestamp': datetime.now().isoformat(),
            'model_path': str(model_path),
            'r2_score': r2,
            'mae': mae,
            'feature_names': feature_names,
            'comparison': comparison,
            'baseline_metrics': self.baseline_metrics
        }
        
        metrics_path = self.logs_dir / f"metrics_{timestamp}.json"
        with open(metrics_path, 'w') as f:
            json.dump(metrics, f, indent=2)
        
        print(f"💾 Modèle sauvegardé: {model_path}")
        print(f"💾 Métriques sauvegardées: {metrics_path}")
        
        return model_path, metrics_path
    
    def send_alert_email(self, comparison, metrics):
        """Envoie un email d'alerte si nécessaire"""
        if not comparison.get('alert_needed', False):
            return
        
        print("\n📧 ENVOI D'ALERTE EMAIL")
        print("=" * 30)
        
        # Contenu de l'email
        subject = "🚨 LUMEN - Alerte Performance Modèle ML"
        
        body = f"""
        <h2>🚨 Alerte Performance Modèle LUMEN</h2>
        
        <p><strong>Date:</strong> {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</p>
        
        <h3>📊 Métriques de Performance:</h3>
        <ul>
            <li><strong>R² Score actuel:</strong> {metrics['r2_score']:.4f}</li>
            <li><strong>MAE actuel:</strong> {metrics['mae']:.4f}</li>
            <li><strong>Chute de performance:</strong> {comparison.get('performance_drop', 0):.4f}</li>
        </ul>
        
        <h3>📈 Comparaison avec modèle précédent:</h3>
        <ul>
            <li><strong>R² précédent:</strong> {comparison.get('old_r2', 'N/A'):.4f}</li>
            <li><strong>R² actuel:</strong> {comparison.get('new_r2', 'N/A'):.4f}</li>
            <li><strong>Différence R²:</strong> {comparison.get('r2_diff', 0):+.4f}</li>
        </ul>
        
        <h3>🔧 Actions Recommandées:</h3>
        <ul>
            <li>Vérifier la qualité des nouvelles données</li>
            <li>Recalibrer les hyperparamètres</li>
            <li>Analyser les features dérivées</li>
            <li>Considérer un retrain complet</li>
        </ul>
        
        <p><strong>Seuils d'alerte:</strong></p>
        <ul>
            <li>R² minimum: {self.baseline_metrics['r2_score']}</li>
            <li>MAE maximum: {self.baseline_metrics['mae']}</li>
            <li>Chute de performance max: {self.baseline_metrics['performance_drop']*100}%</li>
        </ul>
        
        <p><em>Ce message a été généré automatiquement par le système de monitoring LUMEN.</em></p>
        """
        
        # Configuration email (simulation - à adapter selon votre SMTP)
        try:
            # Simulation d'envoi d'email
            print("📧 Simulation d'envoi d'email d'alerte...")
            print(f"   📧 Destinataires: {self.config['email']['recipients']}")
            print(f"   📧 Sujet: {subject}")
            print("   📧 Contenu: Alerte performance modèle")
            
            # Sauvegarder l'alerte dans les logs
            alert_log = {
                'timestamp': datetime.now().isoformat(),
                'type': 'performance_alert',
                'subject': subject,
                'body': body,
                'recipients': self.config['email']['recipients'],
                'comparison': comparison,
                'metrics': metrics
            }
            
            alert_path = self.logs_dir / f"alert_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(alert_path, 'w') as f:
                json.dump(alert_log, f, indent=2)
            
            print(f"✅ Alerte sauvegardée: {alert_path}")
            
        except Exception as e:
            print(f"❌ Erreur envoi email: {e}")
    
    def run_monitoring_cycle(self):
        """Exécute un cycle complet de monitoring"""
        print("🔄 LUMEN - CYCLE DE MONITORING AUTOMATIQUE")
        print("=" * 50)
        print(f"⏰ Début: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        
        try:
            # 1. Charger ou générer les données
            if self.data_path.exists():
                print("📊 Chargement des données existantes...")
                df = pd.read_parquet(self.data_path)
            else:
                print("📊 Génération de données de démonstration...")
                df = self.generate_demo_data()
                # Sauvegarder les données
                self.data_path.parent.mkdir(parents=True, exist_ok=True)
                df.to_parquet(self.data_path)
            
            # 2. Entraîner le nouveau modèle
            model, r2, mae, feature_names = self.train_model(df)
            
            # 3. Charger l'ancien modèle pour comparaison
            old_model, old_model_path, _ = self.load_previous_model()
            
            # 4. Comparer les modèles
            if old_model is not None:
                # Préparer les données de test pour comparaison
                feature_cols = [col for col in feature_names if col in df.columns]
                X_test = df[feature_cols].fillna(0)
                y_test = df['target_demo'].fillna(0)
                
                # Prendre un échantillon pour la comparaison
                if len(X_test) > 200:
                    X_test = X_test.sample(200, random_state=42)
                    y_test = y_test.loc[X_test.index]
                
                comparison = self.compare_models(r2, mae, old_model, X_test, y_test)
            else:
                comparison = {'comparison': 'no_previous_model', 'alert_needed': False}
            
            # 5. Sauvegarder le nouveau modèle
            model_path, metrics_path = self.save_model_with_metrics(
                model, r2, mae, feature_names, comparison
            )
            
            # 6. Envoyer une alerte si nécessaire
            if comparison.get('alert_needed', False):
                metrics = {
                    'r2_score': r2,
                    'mae': mae,
                    'timestamp': datetime.now().isoformat()
                }
                self.send_alert_email(comparison, metrics)
            
            # 7. Résumé
            print("\n🎉 CYCLE DE MONITORING TERMINÉ")
            print("=" * 40)
            print(f"📊 Performance R²: {r2:.4f}")
            print(f"📊 Performance MAE: {mae:.4f}")
            print(f"🚨 Alerte nécessaire: {'Oui' if comparison.get('alert_needed', False) else 'Non'}")
            print(f"💾 Modèle sauvegardé: {model_path}")
            print(f"📋 Métriques: {metrics_path}")
            print(f"⏰ Fin: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
            
            return {
                'success': True,
                'r2_score': r2,
                'mae': mae,
                'alert_sent': comparison.get('alert_needed', False),
                'model_path': str(model_path),
                'metrics_path': str(metrics_path)
            }
            
        except Exception as e:
            print(f"❌ Erreur lors du cycle de monitoring: {e}")
            import traceback
            traceback.print_exc()
            return {'success': False, 'error': str(e)}

def main():
    """Fonction principale"""
    try:
        # Créer le système de monitoring
        monitoring = LUMENMonitoring()
        
        # Exécuter le cycle de monitoring
        result = monitoring.run_monitoring_cycle()
        
        if result['success']:
            print("\n✅ MONITORING AUTOMATIQUE TERMINÉ AVEC SUCCÈS")
            print("=" * 50)
            print("🔄 Retrain automatique exécuté")
            print("📊 Métriques comparées")
            print("🚨 Alertes envoyées si nécessaire")
            print("💾 Modèle sauvegardé")
        else:
            print(f"\n❌ ERREUR LORS DU MONITORING: {result.get('error', 'Erreur inconnue')}")
            
    except Exception as e:
        print(f"❌ Erreur critique: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
