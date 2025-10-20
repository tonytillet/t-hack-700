#!/usr/bin/env python3
"""
Test de l'application Streamlit
"""

import sys
import os
sys.path.append('.')

def test_imports():
    """Test des imports"""
    try:
        import streamlit as st
        import pandas as pd
        import numpy as np
        import plotly.express as px
        import plotly.graph_objects as go
        print("✅ Tous les imports fonctionnent")
        return True
    except Exception as e:
        print(f"❌ Erreur d'import: {e}")
        return False

def test_data_loading():
    """Test du chargement des données"""
    try:
        import pandas as pd
        
        # Chargement des données
        enhanced_files = [f for f in os.listdir('data/processed') if f.startswith('dataset_grippe_enhanced_')]
        
        if not enhanced_files:
            print("❌ Aucun dataset amélioré trouvé")
            return False
        
        latest_dataset = sorted(enhanced_files)[-1]
        df = pd.read_csv(f'data/processed/{latest_dataset}')
        df['date'] = pd.to_datetime(df['date'])
        
        print(f"✅ Dataset chargé: {latest_dataset}")
        print(f"📊 {len(df)} enregistrements, {len(df.columns)} colonnes")
        
        # Test du FLURISK
        if 'urgences_grippe_seasonal_anomaly' in df.columns:
            df['flurisk'] = (
                0.25 * (100 - df.get('taux_vaccination', 50)) +
                0.25 * df.get('ias_syndrome_grippal', 0) +
                0.2 * df.get('urgences_grippe_seasonal_anomaly', 0) +
                0.15 * df.get('cas_sentinelles_seasonal_anomaly', 0) +
                0.15 * df.get('pct_65_plus', 20)
            )
            print("✅ FLURISK amélioré calculé")
        else:
            print("⚠️ Features temporelles non disponibles")
        
        return True
    except Exception as e:
        print(f"❌ Erreur de chargement: {e}")
        return False

def test_streamlit_basic():
    """Test basique de Streamlit"""
    try:
        import streamlit as st
        
        # Test de création d'un graphique simple
        import plotly.express as px
        import pandas as pd
        
        df = pd.DataFrame({
            'x': [1, 2, 3, 4, 5],
            'y': [2, 4, 6, 8, 10]
        })
        
        fig = px.line(df, x='x', y='y', title='Test')
        print("✅ Graphique Plotly créé")
        
        return True
    except Exception as e:
        print(f"❌ Erreur Streamlit: {e}")
        return False

def main():
    """Fonction principale de test"""
    print("🧪 TEST DE L'APPLICATION STREAMLIT")
    print("=" * 50)
    
    # Test 1: Imports
    print("\n1️⃣ Test des imports...")
    if not test_imports():
        return
    
    # Test 2: Chargement des données
    print("\n2️⃣ Test du chargement des données...")
    if not test_data_loading():
        return
    
    # Test 3: Streamlit basique
    print("\n3️⃣ Test Streamlit basique...")
    if not test_streamlit_basic():
        return
    
    print("\n✅ TOUS LES TESTS RÉUSSIS!")
    print("🎉 L'application devrait fonctionner")
    
    print("\n📋 Pour lancer l'application:")
    print("   python3 -m streamlit run app_ultra_simple.py --server.port 8501")
    print("   Puis ouvrir: http://localhost:8501")

if __name__ == "__main__":
    main()
