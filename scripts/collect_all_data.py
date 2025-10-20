#!/usr/bin/env python3
"""
Script principal de collecte de toutes les données
Orchestre la collecte des 13 sources de données pour le projet de prédiction grippe
"""

import os
import sys
import pandas as pd
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Ajout du répertoire scripts au path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def main():
    """Fonction principale de collecte"""
    print("🚀 DÉMARRAGE DE LA COLLECTE COMPLÈTE DES DONNÉES")
    print("=" * 60)
    
    start_time = datetime.now()
    
    # Configuration des dates
    end_date = datetime.now()
    start_date = end_date - timedelta(days=730)  # 2 ans
    
    print(f"📅 Période de collecte: {start_date.strftime('%Y-%m-%d')} à {end_date.strftime('%Y-%m-%d')}")
    print(f"📊 13 sources de données à collecter")
    print()
    
    # 1. Collecte Google Trends
    print("🔍 ÉTAPE 1/4: COLLECTE GOOGLE TRENDS")
    print("-" * 40)
    try:
        from collect_google_trends import GoogleTrendsCollector
        gt_collector = GoogleTrendsCollector()
        gt_data = gt_collector.collect_all_data(
            start_date=start_date.strftime('%Y-%m-%d'),
            end_date=end_date.strftime('%Y-%m-%d')
        )
        if gt_data is not None:
            gt_collector.save_data(gt_data, 'google_trends_latest.csv')
            print("✅ Google Trends: Collecte réussie")
        else:
            print("❌ Google Trends: Échec de la collecte")
    except Exception as e:
        print(f"❌ Google Trends: Erreur - {str(e)}")
    
    print()
    
    # 2. Collecte Wikipedia
    print("📖 ÉTAPE 2/4: COLLECTE WIKIPEDIA")
    print("-" * 40)
    try:
        from collect_wikipedia import WikipediaCollector
        wiki_collector = WikipediaCollector()
        wiki_data = wiki_collector.collect_all_data(
            start_date=start_date.strftime('%Y-%m-%d'),
            end_date=end_date.strftime('%Y-%m-%d')
        )
        if wiki_data is not None:
            wiki_collector.save_data(wiki_data, 'wikipedia_latest.csv')
            print("✅ Wikipedia: Collecte réussie")
        else:
            print("❌ Wikipedia: Échec de la collecte")
    except Exception as e:
        print(f"❌ Wikipedia: Erreur - {str(e)}")
    
    print()
    
    # 3. Collecte données SPF
    print("🏥 ÉTAPE 3/4: COLLECTE DONNÉES SPF")
    print("-" * 40)
    try:
        from collect_spf_data import SPFDataCollector
        spf_collector = SPFDataCollector()
        spf_data = spf_collector.collect_all_data(
            start_date=start_date.strftime('%Y-%m-%d'),
            end_date=end_date.strftime('%Y-%m-%d')
        )
        if spf_data:
            spf_collector.save_data(spf_data)
            print("✅ SPF: Collecte réussie")
        else:
            print("❌ SPF: Échec de la collecte")
    except Exception as e:
        print(f"❌ SPF: Erreur - {str(e)}")
    
    print()
    
    # 4. Collecte données contextuelles
    print("🌍 ÉTAPE 4/4: COLLECTE DONNÉES CONTEXTUELLES")
    print("-" * 40)
    try:
        from collect_context_data import ContextDataCollector
        context_collector = ContextDataCollector()
        context_data = context_collector.collect_all_data(
            start_date=start_date.strftime('%Y-%m-%d'),
            end_date=end_date.strftime('%Y-%m-%d')
        )
        if context_data:
            context_collector.save_data(context_data)
            print("✅ Context: Collecte réussie")
        else:
            print("❌ Context: Échec de la collecte")
    except Exception as e:
        print(f"❌ Context: Erreur - {str(e)}")
    
    print()
    
    # Résumé final
    end_time = datetime.now()
    duration = end_time - start_time
    
    print("🎯 RÉSUMÉ DE LA COLLECTE")
    print("=" * 60)
    print(f"⏱️  Durée totale: {duration.total_seconds():.1f} secondes")
    print(f"📁 Données sauvegardées dans: data/")
    print()
    
    # Vérification des fichiers créés
    print("📋 FICHIERS CRÉÉS:")
    data_dirs = ['google_trends', 'wikipedia', 'spf', 'context']
    for dir_name in data_dirs:
        dir_path = os.path.join('data', dir_name)
        if os.path.exists(dir_path):
            files = os.listdir(dir_path)
            print(f"   {dir_name}/: {len(files)} fichier(s)")
            for file in files:
                if file.endswith('.csv'):
                    file_path = os.path.join(dir_path, file)
                    size = os.path.getsize(file_path)
                    print(f"     - {file} ({size:,} bytes)")
        else:
            print(f"   {dir_name}/: ❌ Répertoire non créé")
    
    print()
    print("✅ COLLECTE TERMINÉE")
    print("💡 Prochaine étape: Fusion et traitement des données")

if __name__ == "__main__":
    main()
