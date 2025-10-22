#!/usr/bin/env python3
"""
🤖 ENTRAÎNEMENT RANDOM FOREST - LUMEN
Système ML complet : entraînement, évaluation et prédictions
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.metrics import mean_absolute_error, r2_score, accuracy_score, classification_report
import joblib
import os
import json
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class LumenMLTrainer:
    def __init__(self):
        self.dataset_path = "data/processed/clean_dataset.csv"
        self.artifacts_dir = "ml/artefacts"
        self.predictions_path = "data/processed/predictions.csv"
        
        # Créer les dossiers
        os.makedirs(self.artifacts_dir, exist_ok=True)
        os.makedirs("data/processed", exist_ok=True)
        
        self.df = None
        self.features = []
        self.target = None
        self.rf_model = None
        self.metrics = {}

    def load_dataset(self):
        """Charge le dataset fusionné"""
        print("📊 CHARGEMENT DU DATASET FUSIONNÉ")
        print("=" * 40)
        
        try:
            self.df = pd.read_csv(self.dataset_path)
            print(f"✅ Dataset chargé: {self.df.shape}")
            print(f"📊 Colonnes disponibles: {list(self.df.columns)}")
            return True
        except Exception as e:
            print(f"❌ Erreur chargement dataset: {e}")
            return False

    def prepare_features_and_target(self):
        """Prépare les features et la variable cible"""
        print("\n🎯 PRÉPARATION DES FEATURES ET CIBLE")
        print("=" * 45)
        
        # Analyser les colonnes disponibles
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns.tolist()
        print(f"📊 Colonnes numériques disponibles: {len(numeric_cols)}")
        
        # Identifier la variable cible (nb_passages semble être notre cible principale)
        if 'nb_passages' in self.df.columns:
            self.target = 'nb_passages'
            print(f"🎯 Variable cible identifiée: {self.target}")
        else:
            # Prendre la première colonne numérique comme cible
            self.target = numeric_cols[0]
            print(f"🎯 Variable cible par défaut: {self.target}")
        
        # Sélectionner les features (exclure la cible et les colonnes non pertinentes)
        exclude_cols = [
            self.target, '_source_file', 'date', 'date_de_passage', 
            'geo_point_2d', 'geo_point', 'geometry'
        ]
        
        self.features = [col for col in numeric_cols if col not in exclude_cols]
        
        print(f"🔧 Features sélectionnées ({len(self.features)}):")
        for i, feature in enumerate(self.features, 1):
            print(f"   {i:2d}. {feature}")
        
        return len(self.features) > 0

    def train_regression_model(self):
        """Entraîne le modèle de régression Random Forest"""
        print("\n🤖 ENTRAÎNEMENT MODÈLE DE RÉGRESSION")
        print("=" * 45)
        
        # Préparer les données
        X = self.df[self.features].fillna(0)  # Remplacer NaN par 0
        y = self.df[self.target].fillna(0)
        
        print(f"📊 Features shape: {X.shape}")
        print(f"📊 Target shape: {y.shape}")
        print(f"📊 Target stats: min={y.min():.2f}, max={y.max():.2f}, mean={y.mean():.2f}")
        
        # Split train/test
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        print(f"📊 Train: {X_train.shape[0]} échantillons")
        print(f"📊 Test: {X_test.shape[0]} échantillons")
        
        # Entraînement Random Forest
        print("🔄 Entraînement en cours...")
        self.rf_model = RandomForestRegressor(
            n_estimators=300,
            max_depth=10,
            random_state=42,
            n_jobs=-1
        )
        
        self.rf_model.fit(X_train, y_train)
        
        # Prédictions et évaluation
        y_pred = self.rf_model.predict(X_test)
        
        mae = mean_absolute_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        
        print(f"✅ MAE: {mae:.3f}")
        print(f"✅ R²: {r2:.3f}")
        
        # Sauvegarder les métriques
        self.metrics = {
            "model_type": "RandomForestRegressor",
            "target": self.target,
            "features_count": len(self.features),
            "train_samples": len(X_train),
            "test_samples": len(X_test),
            "MAE": float(mae),
            "R2": float(r2),
            "timestamp": datetime.now().isoformat()
        }
        
        return True

    def analyze_feature_importance(self):
        """Analyse l'importance des features"""
        print("\n📊 ANALYSE DE L'IMPORTANCE DES FEATURES")
        print("=" * 45)
        
        # Calculer l'importance des features
        importances = pd.Series(
            self.rf_model.feature_importances_, 
            index=self.features
        ).sort_values(ascending=True)
        
        print("🏆 TOP 10 FEATURES LES PLUS IMPORTANTES:")
        for i, (feature, importance) in enumerate(importances.tail(10).items(), 1):
            print(f"   {i:2d}. {feature:<25} {importance:.4f}")
        
        # Créer le graphique d'importance
        plt.figure(figsize=(10, 8))
        importances.plot(kind="barh", color="teal")
        plt.title("Importance des variables - Random Forest", fontsize=14, fontweight='bold')
        plt.xlabel("Importance", fontsize=12)
        plt.ylabel("Variables", fontsize=12)
        plt.tight_layout()
        
        # Sauvegarder le graphique
        importance_plot_path = os.path.join(self.artifacts_dir, "feature_importance.png")
        plt.savefig(importance_plot_path, dpi=300, bbox_inches='tight')
        print(f"📊 Graphique sauvegardé: {importance_plot_path}")
        
        # Sauvegarder les importances en CSV
        importance_df = pd.DataFrame({
            'feature': importances.index,
            'importance': importances.values
        })
        importance_csv_path = os.path.join(self.artifacts_dir, "feature_importance.csv")
        importance_df.to_csv(importance_csv_path, index=False)
        print(f"📊 CSV sauvegardé: {importance_csv_path}")
        
        plt.close()

    def generate_predictions(self):
        """Génère les prédictions pour tout le dataset"""
        print("\n🔮 GÉNÉRATION DES PRÉDICTIONS")
        print("=" * 35)
        
        # Préparer les features
        X = self.df[self.features].fillna(0)
        
        # Générer les prédictions
        print("🔄 Génération des prédictions...")
        predictions = self.rf_model.predict(X)
        
        # Ajouter les prédictions au dataset
        self.df["pred_" + self.target] = predictions
        self.df["ecart"] = self.df[self.target] - self.df["pred_" + self.target]
        
        # Calculer des métriques supplémentaires
        self.df["ecart_absolu"] = abs(self.df["ecart"])
        self.df["ecart_pct"] = (self.df["ecart"] / (self.df[self.target] + 1e-8)) * 100
        
        print(f"✅ Prédictions générées pour {len(predictions)} échantillons")
        print(f"📊 Écart moyen: {self.df['ecart'].mean():.3f}")
        print(f"📊 Écart absolu moyen: {self.df['ecart_absolu'].mean():.3f}")
        print(f"📊 Écart % moyen: {self.df['ecart_pct'].mean():.1f}%")
        
        return True

    def save_model_and_artifacts(self):
        """Sauvegarde le modèle et les artefacts"""
        print("\n💾 SAUVEGARDE DU MODÈLE ET ARTEFACTS")
        print("=" * 45)
        
        # Sauvegarder le modèle
        model_path = os.path.join(self.artifacts_dir, "random_forest.pkl")
        joblib.dump(self.rf_model, model_path)
        print(f"✅ Modèle sauvegardé: {model_path}")
        
        # Sauvegarder les métriques
        metrics_path = os.path.join(self.artifacts_dir, "metrics.json")
        with open(metrics_path, 'w', encoding='utf-8') as f:
            json.dump(self.metrics, f, indent=2, ensure_ascii=False)
        print(f"✅ Métriques sauvegardées: {metrics_path}")
        
        # Sauvegarder les prédictions
        self.df.to_csv(self.predictions_path, index=False)
        print(f"✅ Prédictions sauvegardées: {self.predictions_path}")
        
        # Créer un rapport de performance
        self.create_performance_report()

    def create_performance_report(self):
        """Crée un rapport de performance détaillé"""
        print("\n📋 CRÉATION DU RAPPORT DE PERFORMANCE")
        print("=" * 45)
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "model_info": {
                "type": "RandomForestRegressor",
                "target_variable": self.target,
                "features_used": self.features,
                "features_count": len(self.features)
            },
            "performance": self.metrics,
            "predictions_info": {
                "total_predictions": len(self.df),
                "mean_prediction": float(self.df["pred_" + self.target].mean()),
                "mean_actual": float(self.df[self.target].mean()),
                "mean_error": float(self.df["ecart"].mean()),
                "mean_absolute_error": float(self.df["ecart_absolu"].mean()),
                "mean_percentage_error": float(self.df["ecart_pct"].mean())
            }
        }
        
        # Sauvegarder le rapport
        report_path = os.path.join(self.artifacts_dir, "performance_report.json")
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"📄 Rapport de performance: {report_path}")
        
        # Créer un résumé lisible
        summary_path = os.path.join(self.artifacts_dir, "TRAINING_SUMMARY.txt")
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write("🤖 RAPPORT D'ENTRAÎNEMENT - LUMEN ML\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"📅 Date: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
            f.write(f"🎯 Variable cible: {self.target}\n")
            f.write(f"🔧 Features utilisées: {len(self.features)}\n")
            f.write(f"📊 Échantillons d'entraînement: {self.metrics['train_samples']:,}\n")
            f.write(f"📊 Échantillons de test: {self.metrics['test_samples']:,}\n\n")
            
            f.write("📈 PERFORMANCE:\n")
            f.write("-" * 15 + "\n")
            f.write(f"• MAE (Erreur Absolue Moyenne): {self.metrics['MAE']:.3f}\n")
            f.write(f"• R² (Coefficient de détermination): {self.metrics['R2']:.3f}\n\n")
            
            f.write("🔮 PRÉDICTIONS:\n")
            f.write("-" * 12 + "\n")
            f.write(f"• Total prédictions: {len(self.df):,}\n")
            f.write(f"• Valeur moyenne prédite: {self.df['pred_' + self.target].mean():.2f}\n")
            f.write(f"• Valeur moyenne réelle: {self.df[self.target].mean():.2f}\n")
            f.write(f"• Écart moyen: {self.df['ecart'].mean():.2f}\n")
            f.write(f"• Écart absolu moyen: {self.df['ecart_absolu'].mean():.2f}\n")
            f.write(f"• Erreur % moyenne: {self.df['ecart_pct'].mean():.1f}%\n\n")
            
            f.write("🏆 TOP 5 FEATURES IMPORTANTES:\n")
            f.write("-" * 30 + "\n")
            importances = pd.Series(self.rf_model.feature_importances_, index=self.features)
            top_features = importances.sort_values(ascending=False).head(5)
            for i, (feature, importance) in enumerate(top_features.items(), 1):
                f.write(f"{i}. {feature}: {importance:.4f}\n")
        
        print(f"📄 Résumé: {summary_path}")

    def run_training_pipeline(self):
        """Lance le pipeline d'entraînement complet"""
        print("🤖 ENTRAÎNEMENT RANDOM FOREST - LUMEN")
        print("=" * 50)
        print("🎯 Système ML complet : entraînement, évaluation, prédictions")
        print(f"⏰ Début: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        
        # 1. Charger le dataset
        if not self.load_dataset():
            return False
        
        # 2. Préparer features et cible
        if not self.prepare_features_and_target():
            print("❌ Impossible de préparer les features")
            return False
        
        # 3. Entraîner le modèle
        if not self.train_regression_model():
            print("❌ Échec de l'entraînement")
            return False
        
        # 4. Analyser l'importance des features
        self.analyze_feature_importance()
        
        # 5. Générer les prédictions
        if not self.generate_predictions():
            print("❌ Échec de génération des prédictions")
            return False
        
        # 6. Sauvegarder tout
        self.save_model_and_artifacts()
        
        # Résumé final
        print("\n🎉 ENTRAÎNEMENT TERMINÉ AVEC SUCCÈS")
        print("=" * 40)
        print(f"🎯 Variable cible: {self.target}")
        print(f"🔧 Features: {len(self.features)}")
        print(f"📊 Performance R²: {self.metrics['R2']:.3f}")
        print(f"📊 Performance MAE: {self.metrics['MAE']:.3f}")
        print(f"🔮 Prédictions: {len(self.df):,} échantillons")
        print(f"💾 Modèle: ml/artefacts/random_forest.pkl")
        print(f"📊 Prédictions: data/processed/predictions.csv")
        print(f"⏰ Fin: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

if __name__ == "__main__":
    trainer = LumenMLTrainer()
    trainer.run_training_pipeline()
