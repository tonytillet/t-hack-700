#!/usr/bin/env python3
"""
🧠 LUMEN - EXPLICABILITÉ AVANCÉE AVEC SHAP
Analyse explicative des prédictions du modèle ML
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import shap
import joblib
from pathlib import Path
import json
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class LUMENExplicabilite:
    def __init__(self, data_path='data/processed/dataset.parquet', model_path='models/random_forest_regressor.joblib'):
        self.data_path = Path(data_path)
        self.model_path = Path(model_path)
        self.df = None
        self.model = None
        self.X = None
        self.y = None
        self.X_train = None
        self.X_test = None
        self.y_train = None
        self.y_test = None
        self.explainer = None
        self.shap_values = None
        
        # Créer les répertoires
        Path('explicabilite').mkdir(exist_ok=True)
        Path('explicabilite/plots').mkdir(exist_ok=True)
        Path('explicabilite/reports').mkdir(exist_ok=True)
    
    def load_data_and_model(self):
        """Charge les données et le modèle"""
        print("📊 CHARGEMENT DES DONNÉES ET DU MODÈLE")
        print("=" * 50)
        
        # Charger les données
        if self.data_path.exists():
            self.df = pd.read_parquet(self.data_path)
            print(f"✅ Données chargées: {len(self.df)} lignes, {len(self.df.columns)} colonnes")
        else:
            print("❌ Fichier de données non trouvé, génération de données de démonstration...")
            self.generate_demo_data()
        
        # Charger le modèle
        if self.model_path.exists():
            self.model = joblib.load(self.model_path)
            print(f"✅ Modèle chargé: {type(self.model).__name__}")
        else:
            print("❌ Modèle non trouvé, entraînement d'un nouveau modèle...")
            self.train_model()
        
        return True
    
    def generate_demo_data(self):
        """Génère des données de démonstration réalistes"""
        print("🎲 Génération de données de démonstration...")
        
        np.random.seed(42)
        n_samples = 1000
        
        # Données de base
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
        
        self.df = pd.DataFrame(data)
        
        # Ajouter des features temporelles
        self.df['jour_semaine'] = self.df['date'].dt.dayofweek
        self.df['mois'] = self.df['date'].dt.month
        self.df['saison'] = self.df['mois'].map({12:0, 1:0, 2:0, 3:1, 4:1, 5:1, 6:2, 7:2, 8:2, 9:3, 10:3, 11:3})
        
        # Features dérivées
        self.df['passages_per_100k'] = (self.df['passages_urgences_grippe'] / self.df['population'] * 100000)
        self.df['passages_log'] = np.log1p(self.df['passages_urgences_grippe'])
        self.df['incidence_log'] = np.log1p(self.df['taux_incidence'])
        self.df['lumen_log'] = np.log1p(self.df['indice_lumen'])
        
        # Moyennes mobiles
        self.df['passages_ma_7'] = self.df['passages_urgences_grippe'].rolling(7).mean()
        self.df['incidence_ma_7'] = self.df['taux_incidence'].rolling(7).mean()
        self.df['lumen_ma_7'] = self.df['indice_lumen'].rolling(7).mean()
        
        # Lags
        self.df['passages_lag_7'] = self.df['passages_urgences_grippe'].shift(7)
        self.df['incidence_lag_7'] = self.df['taux_incidence'].shift(7)
        self.df['lumen_lag_7'] = self.df['indice_lumen'].shift(7)
        
        # Target simulé
        self.df['target_demo'] = (
            0.3 * self.df['passages_per_100k'] +
            0.25 * self.df['taux_incidence'] +
            0.2 * self.df['indice_lumen'] +
            0.15 * self.df['google_trends_grippe'] +
            0.1 * self.df['temperature_moyenne'] +
            np.random.normal(0, 5, n_samples)
        )
        
        print(f"✅ Données de démonstration générées: {len(self.df)} lignes")
    
    def train_model(self):
        """Entraîne un nouveau modèle"""
        print("🤖 ENTRAÎNEMENT DU MODÈLE")
        print("=" * 30)
        
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
        available_cols = [col for col in feature_cols if col in self.df.columns]
        X = self.df[available_cols].fillna(0)
        y = self.df['target_demo'].fillna(0)
        
        # Split
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Entraîner le modèle
        self.model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            n_jobs=-1
        )
        
        self.model.fit(self.X_train, self.y_train)
        
        # Évaluation
        train_score = self.model.score(self.X_train, self.y_train)
        test_score = self.model.score(self.X_test, self.y_test)
        
        print(f"✅ Modèle entraîné")
        print(f"   📊 R² Train: {train_score:.4f}")
        print(f"   📊 R² Test: {test_score:.4f}")
        
        # Sauvegarder
        self.model_path.parent.mkdir(exist_ok=True)
        joblib.dump(self.model, self.model_path)
        print(f"💾 Modèle sauvegardé: {self.model_path}")
    
    def prepare_features(self):
        """Prépare les features pour SHAP"""
        print("\n🔧 PRÉPARATION DES FEATURES POUR SHAP")
        print("=" * 45)
        
        # Features numériques
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns.tolist()
        
        # Exclure les colonnes non pertinentes
        exclude_cols = ['target_demo', 'date', 'region', 'departement']
        feature_cols = [col for col in numeric_cols if col not in exclude_cols]
        
        self.X = self.df[feature_cols].fillna(0)
        
        # Utiliser un échantillon pour SHAP (plus rapide)
        if len(self.X) > 1000:
            self.X = self.X.sample(1000, random_state=42)
            print(f"📊 Échantillon SHAP: {len(self.X)} lignes")
        
        print(f"✅ Features préparées: {len(self.X.columns)} colonnes")
        print(f"📊 Colonnes: {list(self.X.columns)}")
        
        return True
    
    def compute_shap_values(self):
        """Calcule les valeurs SHAP"""
        print("\n🧠 CALCUL DES VALEURS SHAP")
        print("=" * 35)
        
        # Créer l'explainer
        print("🔄 Création de l'explainer SHAP...")
        self.explainer = shap.Explainer(self.model, self.X)
        
        # Calculer les valeurs SHAP
        print("🔄 Calcul des valeurs SHAP...")
        self.shap_values = self.explainer(self.X)
        
        print(f"✅ Valeurs SHAP calculées: {self.shap_values.shape}")
        return True
    
    def create_summary_plot(self):
        """Crée le graphique de résumé SHAP"""
        print("\n📊 CRÉATION DU GRAPHIQUE DE RÉSUMÉ SHAP")
        print("=" * 50)
        
        plt.figure(figsize=(12, 8))
        shap.summary_plot(self.shap_values, self.X, show=False)
        plt.title("🧠 LUMEN - Résumé des Contributions SHAP", fontsize=16, fontweight='bold')
        plt.tight_layout()
        
        plot_path = Path('explicabilite/plots/summary_plot.png')
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"✅ Graphique de résumé sauvegardé: {plot_path}")
        return plot_path
    
    def create_force_plots(self, n_samples=5):
        """Crée des graphiques de force pour quelques échantillons"""
        print(f"\n⚡ CRÉATION DES GRAPHIQUES DE FORCE ({n_samples} échantillons)")
        print("=" * 60)
        
        force_plots = []
        
        for i in range(min(n_samples, len(self.X))):
            print(f"🔄 Création du graphique de force {i+1}/{n_samples}...")
            
            try:
                # Graphique de force avec Explanation object
                force_plot = shap.force_plot(
                    self.explainer.expected_value,
                    self.shap_values[i],
                    self.X.iloc[i],
                    matplotlib=True,
                    show=False
                )
                
                plot_path = Path(f'explicabilite/plots/force_plot_{i+1}.png')
                plt.savefig(plot_path, dpi=300, bbox_inches='tight')
                plt.close()
                
                force_plots.append(plot_path)
                print(f"   ✅ Sauvegardé: {plot_path}")
                
            except Exception as e:
                print(f"   ⚠️ Erreur graphique de force {i+1}: {e}")
                # Créer un graphique alternatif
                self.create_alternative_force_plot(i, n_samples)
                continue
        
        return force_plots
    
    def create_alternative_force_plot(self, sample_idx, n_samples):
        """Crée un graphique alternatif pour la force"""
        try:
            # Graphique simple des contributions SHAP
            plt.figure(figsize=(12, 6))
            
            # Top 10 features par importance absolue
            shap_vals = self.shap_values[sample_idx]
            feature_importance = pd.DataFrame({
                'feature': self.X.columns,
                'shap_value': shap_vals
            }).sort_values('shap_value', key=abs, ascending=False).head(10)
            
            colors = ['red' if x < 0 else 'blue' for x in feature_importance['shap_value']]
            
            plt.barh(feature_importance['feature'], feature_importance['shap_value'], color=colors)
            plt.title(f"🧠 LUMEN - Contributions SHAP (Échantillon {sample_idx+1})")
            plt.xlabel("Contribution SHAP")
            plt.axvline(x=0, color='black', linestyle='--', alpha=0.5)
            plt.tight_layout()
            
            plot_path = Path(f'explicabilite/plots/force_plot_{sample_idx+1}.png')
            plt.savefig(plot_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            print(f"   ✅ Graphique alternatif sauvegardé: {plot_path}")
            
        except Exception as e:
            print(f"   ❌ Erreur graphique alternatif: {e}")
    
    def create_waterfall_plots(self, n_samples=3):
        """Crée des graphiques waterfall pour quelques échantillons"""
        print(f"\n🌊 CRÉATION DES GRAPHIQUES WATERFALL ({n_samples} échantillons)")
        print("=" * 60)
        
        waterfall_plots = []
        
        for i in range(min(n_samples, len(self.X))):
            print(f"🔄 Création du graphique waterfall {i+1}/{n_samples}...")
            
            try:
                # Graphique waterfall
                plt.figure(figsize=(10, 6))
                shap.waterfall_plot(
                    self.explainer.expected_value,
                    self.shap_values[i],
                    self.X.iloc[i],
                    show=False
                )
                
                plot_path = Path(f'explicabilite/plots/waterfall_plot_{i+1}.png')
                plt.savefig(plot_path, dpi=300, bbox_inches='tight')
                plt.close()
                
                waterfall_plots.append(plot_path)
                print(f"   ✅ Sauvegardé: {plot_path}")
                
            except Exception as e:
                print(f"   ⚠️ Erreur graphique waterfall {i+1}: {e}")
                # Créer un graphique alternatif
                self.create_alternative_waterfall_plot(i, n_samples)
                continue
        
        return waterfall_plots
    
    def create_alternative_waterfall_plot(self, sample_idx, n_samples):
        """Crée un graphique alternatif pour waterfall"""
        try:
            # Graphique de progression des contributions
            plt.figure(figsize=(12, 8))
            
            # Calculer la progression cumulative
            shap_vals = self.shap_values[sample_idx]
            feature_importance = pd.DataFrame({
                'feature': self.X.columns,
                'shap_value': shap_vals
            }).sort_values('shap_value', key=abs, ascending=False).head(15)
            
            # Progression cumulative
            cumulative = [self.explainer.expected_value]
            for val in feature_importance['shap_value']:
                cumulative.append(cumulative[-1] + val)
            
            # Graphique
            plt.plot(range(len(cumulative)), cumulative, 'o-', linewidth=2, markersize=6)
            plt.axhline(y=self.explainer.expected_value, color='red', linestyle='--', alpha=0.7, label='Valeur attendue')
            plt.axhline(y=cumulative[-1], color='green', linestyle='--', alpha=0.7, label='Prédiction finale')
            
            plt.title(f"🧠 LUMEN - Progression des Contributions SHAP (Échantillon {sample_idx+1})")
            plt.xlabel("Features (par importance)")
            plt.ylabel("Valeur cumulative")
            plt.legend()
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            
            plot_path = Path(f'explicabilite/plots/waterfall_plot_{sample_idx+1}.png')
            plt.savefig(plot_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            print(f"   ✅ Graphique waterfall alternatif sauvegardé: {plot_path}")
            
        except Exception as e:
            print(f"   ❌ Erreur graphique waterfall alternatif: {e}")
    
    def create_feature_importance_plot(self):
        """Crée le graphique d'importance des features"""
        print("\n📈 CRÉATION DU GRAPHIQUE D'IMPORTANCE DES FEATURES")
        print("=" * 55)
        
        # Importance des features du modèle
        feature_importance = pd.DataFrame({
            'feature': self.X.columns,
            'importance': self.model.feature_importances_
        }).sort_values('importance', ascending=True)
        
        # Graphique
        plt.figure(figsize=(12, 8))
        plt.barh(feature_importance['feature'], feature_importance['importance'])
        plt.title("🧠 LUMEN - Importance des Features (Random Forest)", fontsize=16, fontweight='bold')
        plt.xlabel("Importance")
        plt.tight_layout()
        
        plot_path = Path('explicabilite/plots/feature_importance.png')
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"✅ Graphique d'importance sauvegardé: {plot_path}")
        return plot_path
    
    def create_dependence_plots(self, top_features=5):
        """Crée des graphiques de dépendance pour les top features"""
        print(f"\n🔗 CRÉATION DES GRAPHIQUES DE DÉPENDANCE ({top_features} features)")
        print("=" * 65)
        
        # Top features par importance
        feature_importance = pd.DataFrame({
            'feature': self.X.columns,
            'importance': self.model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        top_features = feature_importance.head(top_features)['feature'].tolist()
        dependence_plots = []
        
        for i, feature in enumerate(top_features):
            print(f"🔄 Création du graphique de dépendance {i+1}/{len(top_features)}: {feature}")
            
            plt.figure(figsize=(10, 6))
            shap.dependence_plot(
                feature,
                self.shap_values,
                self.X,
                show=False
            )
            
            plot_path = Path(f'explicabilite/plots/dependence_plot_{feature}.png')
            plt.savefig(plot_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            dependence_plots.append(plot_path)
            print(f"   ✅ Sauvegardé: {plot_path}")
        
        return dependence_plots
    
    def generate_explicability_report(self):
        """Génère un rapport d'explicabilité complet"""
        print("\n📋 GÉNÉRATION DU RAPPORT D'EXPLICABILITÉ")
        print("=" * 45)
        
        # Métriques de base
        report = {
            "timestamp": datetime.now().isoformat(),
            "model_type": type(self.model).__name__,
            "n_features": len(self.X.columns),
            "n_samples": len(self.X),
            "feature_names": list(self.X.columns),
            "shap_values_shape": self.shap_values.shape if self.shap_values is not None else None,
            "expected_value": float(self.explainer.expected_value) if self.explainer else None
        }
        
        # Top features par importance
        if hasattr(self.model, 'feature_importances_'):
            feature_importance = pd.DataFrame({
                'feature': self.X.columns,
                'importance': self.model.feature_importances_
            }).sort_values('importance', ascending=False)
            
            report["top_features"] = feature_importance.head(10).to_dict('records')
        
        # Statistiques SHAP
        if self.shap_values is not None:
            report["shap_stats"] = {
                "mean_abs_shap": float(np.mean(np.abs(self.shap_values.values))),
                "max_abs_shap": float(np.max(np.abs(self.shap_values.values))),
                "min_abs_shap": float(np.min(np.abs(self.shap_values.values)))
            }
        
        # Sauvegarder le rapport
        report_path = Path('explicabilite/reports/explicability_report.json')
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Rapport d'explicabilité sauvegardé: {report_path}")
        return report_path
    
    def run_full_analysis(self):
        """Exécute l'analyse d'explicabilité complète"""
        print("🧠 LUMEN - ANALYSE D'EXPLICABILITÉ AVANCÉE AVEC SHAP")
        print("=" * 65)
        print(f"⏰ Début: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        
        # 1. Charger les données et le modèle
        self.load_data_and_model()
        
        # 2. Préparer les features
        self.prepare_features()
        
        # 3. Calculer les valeurs SHAP
        self.compute_shap_values()
        
        # 4. Créer les graphiques
        print("\n🎨 CRÉATION DES VISUALISATIONS")
        print("=" * 35)
        
        summary_plot = self.create_summary_plot()
        force_plots = self.create_force_plots(n_samples=5)
        waterfall_plots = self.create_waterfall_plots(n_samples=3)
        importance_plot = self.create_feature_importance_plot()
        dependence_plots = self.create_dependence_plots(top_features=5)
        
        # 5. Générer le rapport
        report_path = self.generate_explicability_report()
        
        # 6. Résumé
        print("\n🎉 ANALYSE D'EXPLICABILITÉ TERMINÉE")
        print("=" * 40)
        print(f"📊 Graphiques créés:")
        print(f"   📈 Résumé SHAP: {summary_plot}")
        print(f"   ⚡ Graphiques de force: {len(force_plots)}")
        print(f"   🌊 Graphiques waterfall: {len(waterfall_plots)}")
        print(f"   📊 Importance features: {importance_plot}")
        print(f"   🔗 Graphiques de dépendance: {len(dependence_plots)}")
        print(f"   📋 Rapport: {report_path}")
        print(f"⏰ Fin: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        
        return {
            "summary_plot": summary_plot,
            "force_plots": force_plots,
            "waterfall_plots": waterfall_plots,
            "importance_plot": importance_plot,
            "dependence_plots": dependence_plots,
            "report": report_path
        }

def main():
    """Fonction principale"""
    try:
        # Créer l'analyseur
        analyzer = LUMENExplicabilite()
        
        # Exécuter l'analyse complète
        results = analyzer.run_full_analysis()
        
        print("\n✅ ANALYSE SHAP TERMINÉE AVEC SUCCÈS")
        print("=" * 40)
        print("🧠 Explicabilité avancée générée")
        print("📊 Graphiques 'forces' créés")
        print("⚡ Effets positifs/négatifs visualisés")
        print("🔗 Dépendances entre variables analysées")
        
    except Exception as e:
        print(f"❌ Erreur lors de l'analyse SHAP: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
