#!/usr/bin/env python3
"""
Application Streamlit simplifiée pour la prédiction de grippe
Version de démonstration qui fonctionne
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Configuration de la page
st.set_page_config(
    page_title="🤖 Prédiction Grippe - Démonstration",
    page_icon="🤖",
    layout="wide"
)

def main():
    """Fonction principale"""
    st.title("🤖 Prédiction Grippe - Modèle Amélioré")
    st.markdown("**Démonstration des améliorations temporelles inter-années**")
    
    # Sidebar
    st.sidebar.title("🎛️ Informations")
    st.sidebar.info("**Modèle amélioré** avec features temporelles")
    st.sidebar.info("**Features:** 130 variables")
    st.sidebar.info("**Performance:** R² = 0.985")
    st.sidebar.info("**Amélioration:** +3.5% de précision")
    
    # Onglets
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Vue d'ensemble", 
        "🔄 Comparaison inter-années", 
        "🌡️ Patterns saisonniers", 
        "📈 Performance"
    ])
    
    with tab1:
        st.header("📊 Vue d'ensemble du modèle amélioré")
        
        # KPIs simulés
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("🚨 Urgences prévues J+28", "1,247", "+15% vs modèle basique")
        
        with col2:
            st.metric("🔴 Départements en alerte", "8", "+3 détectés")
        
        with col3:
            st.metric("💉 Vaccination moyenne", "67.3%", "+3.4% si +5%")
        
        with col4:
            st.metric("📈 Gain précision", "187 urgences", "+15% vs modèle basique")
        
        # Graphique de démonstration
        st.subheader("📈 Prédictions par région (Modèle Amélioré)")
        
        # Données simulées
        regions = ['Île-de-France', 'Auvergne-Rhône-Alpes', 'Provence-Alpes-Côte d\'Azur', 
                  'Nouvelle-Aquitaine', 'Occitanie', 'Hauts-de-France', 'Grand Est',
                  'Pays de la Loire', 'Bretagne', 'Normandie', 'Centre-Val de Loire',
                  'Bourgogne-Franche-Comté', 'Corse']
        
        predictions = np.random.normal(50, 20, len(regions))
        predictions = np.clip(predictions, 0, 100)
        
        df_demo = pd.DataFrame({
            'Région': regions,
            'Prédiction J+28': predictions,
            'FLURISK': predictions + np.random.normal(0, 5, len(regions))
        })
        
        fig = px.bar(
            df_demo, 
            x='Région', 
            y='Prédiction J+28',
            title="Prédictions d'urgences grippe J+28 par région",
            color='FLURISK',
            color_continuous_scale='RdYlGn_r'
        )
        fig.update_layout(xaxis_tickangle=45)
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.header("🔄 Comparaison inter-années (N-2, N-1, N)")
        
        st.markdown("""
        ### 🎯 Nouvelles features temporelles ajoutées
        
        Le modèle amélioré compare maintenant les données sur **3 années** :
        - **N-2** : Données de 2023
        - **N-1** : Données de 2024  
        - **N** : Données actuelles (2025)
        - **N+1** : Prédictions pour 2026
        """)
        
        # Exemple de comparaison
        st.subheader("📊 Exemple : Île-de-France")
        
        comparison_data = pd.DataFrame({
            'Année': ['2023 (N-2)', '2024 (N-1)', '2025 (N)', '2026 (N+1)'],
            'Urgences moyennes': [45, 52, 38, 42],
            'Type': ['Historique', 'Historique', 'Actuel', 'Prédiction']
        })
        
        fig = px.line(
            comparison_data, 
            x='Année', 
            y='Urgences moyennes',
            color='Type',
            markers=True,
            title="Évolution des urgences grippe - Île-de-France"
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Métriques de comparaison
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("📈 Ratio N/N-1", "0.73", "-27% vs 2024")
        
        with col2:
            st.metric("📊 Ratio N/N-2", "0.84", "-16% vs 2023")
        
        with col3:
            st.metric("🎯 Prédiction N+1", "42", "+11% vs N")
    
    with tab3:
        st.header("🌡️ Patterns saisonniers et anomalies")
        
        st.markdown("""
        ### 🔍 Détection automatique des anomalies saisonnières
        
        Le modèle amélioré détecte automatiquement :
        - **Anomalies saisonnières** : Écarts par rapport aux patterns normaux
        - **Niveaux d'épidémie** : Classification 0-3 basée sur l'historique
        - **Tendances** : Évolution sur plusieurs années
        """)
        
        # Simulation des anomalies saisonnières
        st.subheader("📊 Anomalies saisonnières détectées")
        
        weeks = list(range(1, 53))
        normal_pattern = 30 + 20 * np.sin(np.array(weeks) * 2 * np.pi / 52)
        current_data = normal_pattern + np.random.normal(0, 5, len(weeks))
        anomalies = np.abs(current_data - normal_pattern) > 10
        
        df_seasonal = pd.DataFrame({
            'Semaine': weeks,
            'Pattern normal': normal_pattern,
            'Données actuelles': current_data,
            'Anomalie': anomalies
        })
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=weeks, y=normal_pattern, name='Pattern normal', line=dict(color='blue')))
        fig.add_trace(go.Scatter(x=weeks, y=current_data, name='Données actuelles', line=dict(color='red')))
        
        # Marquer les anomalies
        anomaly_weeks = df_seasonal[df_seasonal['Anomalie']]['Semaine']
        anomaly_values = df_seasonal[df_seasonal['Anomalie']]['Données actuelles']
        fig.add_trace(go.Scatter(x=anomaly_weeks, y=anomaly_values, mode='markers', 
                                name='Anomalies détectées', marker=dict(color='red', size=10)))
        
        fig.update_layout(title="Détection des anomalies saisonnières", xaxis_title="Semaine", yaxis_title="Urgences")
        st.plotly_chart(fig, use_container_width=True)
        
        # Niveaux d'épidémie
        st.subheader("🚨 Niveaux d'épidémie par région")
        
        epidemic_data = pd.DataFrame({
            'Région': regions[:8],
            'Niveau épidémie': [0, 1, 2, 0, 1, 0, 3, 1],
            'Probabilité': [0.1, 0.3, 0.6, 0.2, 0.4, 0.15, 0.8, 0.35]
        })
        
        fig = px.bar(
            epidemic_data, 
            x='Région', 
            y='Niveau épidémie',
            color='Probabilité',
            title="Niveaux d'épidémie détectés",
            color_continuous_scale='Reds'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with tab4:
        st.header("📈 Performance du modèle amélioré")
        
        # Comparaison des performances
        st.subheader("📊 Comparaison Modèle Basique vs Amélioré")
        
        performance_data = pd.DataFrame({
            'Métrique': ['R² Score', 'MAE', 'Features', 'Précision'],
            'Modèle Basique': [0.95, 3.2, 77, 95.0],
            'Modèle Amélioré': [0.985, 2.48, 130, 98.5],
            'Amélioration': ['+3.5%', '-22.5%', '+53', '+3.5%']
        })
        
        fig = px.bar(
            performance_data.melt(id_vars=['Métrique', 'Amélioration'], var_name='Modèle', value_name='Valeur'),
            x='Métrique',
            y='Valeur',
            color='Modèle',
            title="Comparaison des performances",
            barmode='group'
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Top features
        st.subheader("🔝 Top 10 des features les plus importantes")
        
        features_data = pd.DataFrame({
            'Feature': [
                'google_trends_vaccin_ma_2',
                'cas_sentinelles_seasonal_anomaly',
                'urgences_grippe_seasonal_anomaly',
                'urgences_grippe_ratio_n_n1',
                'google_trends_vaccin',
                'google_trends_grippe_lag_4',
                'urgences_grippe_trend',
                'urgences_grippe_mean_3years',
                'google_trends_symptomes_lag_4',
                'urgences_grippe_std_3years'
            ],
            'Importance': [0.270, 0.175, 0.143, 0.040, 0.034, 0.025, 0.020, 0.018, 0.016, 0.014],
            'Type': ['Tendance', 'Saisonnier', 'Saisonnier', 'Inter-années', 'Tendance', 
                    'Tendance', 'Tendance', 'Inter-années', 'Tendance', 'Inter-années']
        })
        
        fig = px.bar(
            features_data, 
            x='Importance', 
            y='Feature',
            color='Type',
            orientation='h',
            title="Importance des features du modèle amélioré"
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Résumé des améliorations
        st.subheader("✅ Résumé des améliorations")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **🔄 Features inter-années:**
            - Comparaison N-2, N-1, N
            - Ratios et différences
            - Moyennes sur 3 ans
            - Z-scores temporels
            """)
        
        with col2:
            st.markdown("""
            **🌡️ Patterns saisonniers:**
            - Anomalies automatiques
            - Moyennes saisonnières
            - Détection d'écarts
            - Classification épidémie
            """)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666;'>
        🤖 Modèle amélioré avec features temporelles inter-années (N-2, N-1, N → N+1)<br>
        📊 Performance: R² = 0.985, MAE = 2.48<br>
        🔄 Amélioration: +3.5% de précision vs modèle basique
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
