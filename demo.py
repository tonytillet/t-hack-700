#!/usr/bin/env python3
"""
Script de démonstration du système de prédiction grippe
Affiche les principales fonctionnalités et données collectées
"""

import pandas as pd
import numpy as np
from datetime import datetime
import os

def show_data_summary():
    """Affiche un résumé des données collectées"""
    print("🔮 SYSTÈME DE PRÉDICTION GRIPPE FRANCE")
    print("=" * 60)
    
    # Vérification des données
    data_dirs = ['insee', 'meteo', 'google_trends', 'wikipedia', 'spf', 'processed']
    
    print("\n📊 ÉTAT DES DONNÉES COLLECTÉES:")
    print("-" * 40)
    
    total_files = 0
    for dir_name in data_dirs:
        dir_path = f'data/{dir_name}'
        if os.path.exists(dir_path):
            files = [f for f in os.listdir(dir_path) if f.endswith('.csv')]
            total_files += len(files)
            status = "✅" if files else "❌"
            print(f"  {status} {dir_name}: {len(files)} fichier(s)")
        else:
            print(f"  ❌ {dir_name}: Répertoire non trouvé")
    
    print(f"\n📈 Total: {total_files} fichiers de données")
    
    # Chargement du dataset principal
    processed_files = [f for f in os.listdir('data/processed') if f.startswith('dataset_grippe_') and f.endswith('.csv')]
    if processed_files:
        latest_file = sorted(processed_files)[-1]
        df = pd.read_csv(f'data/processed/{latest_file}')
        df['date'] = pd.to_datetime(df['date'])
        
        print(f"\n🎯 DATASET PRINCIPAL: {latest_file}")
        print("-" * 40)
        print(f"  📅 Période: {df['date'].min().strftime('%Y-%m-%d')} à {df['date'].max().strftime('%Y-%m-%d')}")
        print(f"  🌍 Régions: {df['region'].nunique()}")
        print(f"  📊 Enregistrements: {len(df):,}")
        print(f"  🔧 Variables: {len(df.columns)}")
        
        # FLURISK actuel
        latest_week = df['date'].max()
        latest_data = df[df['date'] == latest_week]
        
        print(f"\n🚨 FLURISK ACTUEL (semaine du {latest_week.strftime('%Y-%m-%d')}):")
        print("-" * 40)
        
        # Vérification des colonnes disponibles
        available_cols = latest_data.columns.tolist()
        print(f"  Colonnes disponibles: {available_cols[:10]}...")
        
        # Sélection des colonnes disponibles
        cols_to_show = ['region', 'flurisk']
        if 'pred_urgences_grippe_j28' in available_cols:
            cols_to_show.append('pred_urgences_grippe_j28')
        if 'taux_vaccination' in available_cols:
            cols_to_show.append('taux_vaccination')
        
        top_risks = latest_data.nlargest(5, 'flurisk')[cols_to_show]
        for _, row in top_risks.iterrows():
            risk_level = "🔴" if row['flurisk'] > 70 else "🟠" if row['flurisk'] > 50 else "🟢"
            urgences_info = f" | Urgences J+28: {row['pred_urgences_grippe_j28']:.0f}" if 'pred_urgences_grippe_j28' in cols_to_show else ""
            vacc_info = f" | Vaccination: {row['taux_vaccination']:.1f}%" if 'taux_vaccination' in cols_to_show else ""
            print(f"  {risk_level} {row['region']}: FLURISK {row['flurisk']:.1f}{urgences_info}{vacc_info}")

def show_model_performance():
    """Affiche les performances du modèle"""
    print(f"\n🤖 PERFORMANCE DU MODÈLE RANDOM FOREST:")
    print("-" * 40)
    
    # Vérification des modèles
    if os.path.exists('models'):
        model_files = [f for f in os.listdir('models') if f.startswith('rf_grippe_') and f.endswith('.pkl')]
        print(f"  ✅ {len(model_files)} modèles entraînés")
        
        # Chargement des métriques
        metrics_files = [f for f in os.listdir('models') if f.startswith('metrics_') and f.endswith('.csv')]
        if metrics_files:
            print(f"  📊 Métriques disponibles:")
            for file in sorted(metrics_files):
                horizon = file.replace('metrics_', '').replace('.csv', '')
                df_metrics = pd.read_csv(f'models/{file}')
                test_mae = df_metrics[df_metrics['metric'] == 'test_mae']['value'].iloc[0]
                test_r2 = df_metrics[df_metrics['metric'] == 'test_r2']['value'].iloc[0]
                print(f"    - {horizon}: MAE {test_mae:.1f}, R² {test_r2:.3f}")
    else:
        print("  ❌ Aucun modèle trouvé")

def show_application_status():
    """Affiche le statut de l'application"""
    print(f"\n🌐 APPLICATION STREAMLIT:")
    print("-" * 40)
    
    try:
        import requests
        response = requests.get('http://localhost:8501', timeout=5)
        if response.status_code == 200:
            print("  ✅ Application en cours d'exécution")
            print("  🌐 URL: http://localhost:8501")
            print("  📱 Fonctionnalités disponibles:")
            print("    - 🇫🇷 Carte France avec FLURISK")
            print("    - 📋 Top 10 priorités + export CSV")
            print("    - 🔍 Zoom département avec prédictions")
            print("    - 🎛️ Simulation ROI des campagnes")
        else:
            print("  ⚠️ Application accessible mais erreur HTTP")
    except:
        print("  ❌ Application non accessible")
        print("  💡 Pour lancer: python3 -m streamlit run app.py --server.port 8501")

def show_next_steps():
    """Affiche les prochaines étapes possibles"""
    print(f"\n🚀 PROCHAINES ÉTAPES POSSIBLES:")
    print("-" * 40)
    print("  1. 📊 Collecter de vraies données SPF (urgences, vaccination)")
    print("  2. 🔄 Améliorer la collecte Google Trends (proxies, délais)")
    print("  3. 🎯 Optimiser les hyperparamètres du modèle")
    print("  4. 📱 Ajouter des alertes automatiques")
    print("  5. 🌐 Déployer en production")
    print("  6. 📈 Ajouter plus de sources de données (Twitter, etc.)")

def main():
    """Fonction principale de démonstration"""
    show_data_summary()
    show_model_performance()
    show_application_status()
    show_next_steps()
    
    print(f"\n" + "=" * 60)
    print("🎉 SYSTÈME OPÉRATIONNEL - Prêt pour la démonstration !")
    print("=" * 60)

if __name__ == "__main__":
    main()
