"""
Application Streamlit LUMEN - Version propre et moderne
Système d'alerte grippe France
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import folium
from streamlit_folium import st_folium
from datetime import datetime, timedelta
import os
import json
import warnings
warnings.filterwarnings('ignore')

# Configuration de la page
st.set_page_config(
    page_title="LUMEN - Surveillance Grippe France",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS simple et propre
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #1e40af, #3b82f6);
        color: white;
        padding: 2rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        text-align: center;
    }
    
    .metric-card {
        background: white;
        border-radius: 8px;
        padding: 1.5rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        border-left: 4px solid #3b82f6;
        margin: 0.5rem 0;
    }
    
    .section-title {
        background: #f8fafc;
        border-left: 4px solid #3b82f6;
        padding: 1rem;
        border-radius: 4px;
        margin: 1rem 0;
        font-weight: 600;
        color: #1e293b;
    }
</style>
""", unsafe_allow_html=True)

class GrippeAlertApp:
    def __init__(self):
        self.data = None
        self.alerts = None
        self.protocols = None
        self.load_data()
    
    def load_data(self):
        """Charger les données"""
        try:
            # Charger les données principales
            data_files = [f for f in os.listdir('data/processed') if f.startswith('dataset_with_alerts_') and f.endswith('.csv')]
            if data_files:
                latest_file = max(data_files)
                self.data = pd.read_csv(f'data/processed/{latest_file}')
                self.data['date'] = pd.to_datetime(self.data['date'])
            
            # Charger les alertes
            alert_files = [f for f in os.listdir('data/alerts') if f.startswith('alertes_') and f.endswith('.csv')]
            if alert_files:
                latest_alert_file = max(alert_files)
                self.alerts = pd.read_csv(f'data/alerts/{latest_alert_file}')
            
            # Charger les protocoles
            protocol_files = [f for f in os.listdir('data/alerts') if f.startswith('protocoles_') and f.endswith('.csv')]
            if protocol_files:
                latest_protocol_file = max(protocol_files)
                self.protocols = pd.read_csv(f'data/alerts/{latest_protocol_file}')
                
        except Exception as e:
            st.error(f"Erreur lors du chargement des données: {e}")
    
    def create_map(self):
        """Créer la carte de France"""
        if self.data is None:
            return None
        
        # Données les plus récentes
        latest_data = self.data.groupby('region').last().reset_index()
        
        # Créer la carte
        m = folium.Map(
            location=[46.2276, 2.2137],
            zoom_start=6,
            tiles='OpenStreetMap'
        )
        
        # Ajouter les marqueurs
        for _, row in latest_data.iterrows():
            # Coordonnées approximatives par région
            coords = {
                'Île-de-France': [48.8566, 2.3522],
                'Auvergne-Rhône-Alpes': [45.7640, 4.8357],
                'Provence-Alpes-Côte d\'Azur': [43.2965, 5.3698],
                'Occitanie': [43.6047, 1.4442],
                'Nouvelle-Aquitaine': [44.8378, -0.5792],
                'Hauts-de-France': [50.6292, 3.0573],
                'Grand Est': [48.5734, 7.7521],
                'Bretagne': [48.2020, -2.9326],
                'Normandie': [49.4432, 1.0993],
                'Pays de la Loire': [47.4739, -0.5517],
                'Bourgogne-Franche-Comté': [47.3220, 5.0415],
                'Centre-Val de Loire': [47.7516, 1.6751],
                'Corse': [42.0396, 9.0129]
            }
            
            if row['region'] in coords:
                lat, lon = coords[row['region']]
                
                # Couleur selon le score d'alerte
                if row['alert_score'] >= 80:
                    color = 'red'
                elif row['alert_score'] >= 60:
                    color = 'orange'
                elif row['alert_score'] >= 40:
                    color = 'yellow'
                else:
                    color = 'green'
                
                folium.Marker(
                    [lat, lon],
                    popup=f"""
                    <b>{row['region']}</b><br>
                    Score: {row['alert_score']:.0f}<br>
                    Urgences: {row['urgences_grippe']}<br>
                    Vaccination: {row['vaccination_2024']:.1f}%
                    """,
                    icon=folium.Icon(color=color, icon='info-sign')
                ).add_to(m)
        
        return m
    
    def create_alert_dashboard(self):
        """Créer le tableau de bord des alertes"""
        if self.alerts is None or len(self.alerts) == 0:
            return None
        
        return self.alerts
    
    def create_protocol_dashboard(self):
        """Créer le tableau des protocoles"""
        if self.protocols is None or len(self.protocols) == 0:
            return None
        
        return self.protocols

def main():
    """Fonction principale"""
    
    # Header principal
    st.markdown("""
    <div class="main-header">
        <h1 style="margin: 0; font-size: 2.5rem; font-weight: 700;">
            LUMEN
        </h1>
        <p style="margin: 0.5rem 0 0 0; font-size: 1.1rem; opacity: 0.9;">
            Plateforme nationale de surveillance grippale
        </p>
        <p style="margin: 0.5rem 0 0 0; font-size: 0.9rem; opacity: 0.8;">
            Dernière mise à jour: """ + datetime.now().strftime("%d/%m/%Y %H:%M") + """
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialisation de l'application
    app = GrippeAlertApp()
    
    # Navigation simple
    tab1, tab2, tab3 = st.tabs(["📊 Tableau de bord", "🚨 Alertes", "⚙️ Configuration"])
    
    with tab1:
        st.markdown('<div class="section-title">📊 Indicateurs nationaux</div>', unsafe_allow_html=True)
        
        if app.data is not None:
            latest_data = app.data.groupby('region').last().reset_index()
            
            # Métriques principales
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                total_urgences = latest_data['urgences_grippe'].sum()
                st.markdown(f"""
                <div class="metric-card">
                    <div style="font-size: 2rem; font-weight: 700; color: #dc2626;">
                        {total_urgences:.0f}
                    </div>
                    <div style="color: #6b7280;">Urgences grippe</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                avg_vaccination = latest_data['vaccination_2024'].mean()
                st.markdown(f"""
                <div class="metric-card">
                    <div style="font-size: 2rem; font-weight: 700; color: #059669;">
                        {avg_vaccination:.1f}%
                    </div>
                    <div style="color: #6b7280;">Vaccination moyenne</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                regions_alerte = len(latest_data[latest_data['alert_score'] >= 60])
                st.markdown(f"""
                <div class="metric-card">
                    <div style="font-size: 2rem; font-weight: 700; color: #d97706;">
                        {regions_alerte}/{len(latest_data)}
                    </div>
                    <div style="color: #6b7280;">Régions en alerte</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                avg_ias = latest_data['ias_syndrome_grippal'].mean()
                st.markdown(f"""
                <div class="metric-card">
                    <div style="font-size: 2rem; font-weight: 700; color: #7c3aed;">
                        {avg_ias:.2f}
                    </div>
                    <div style="color: #6b7280;">IAS Syndrome</div>
                </div>
                """, unsafe_allow_html=True)
            
            # Carte de France
            st.markdown('<div class="section-title">🗺️ Carte de surveillance</div>', unsafe_allow_html=True)
            map_obj = app.create_map()
            if map_obj:
                st_folium(map_obj, width=700, height=500)
            else:
                st.warning("Impossible de charger la carte")
            
            # Tableau des régions
            st.markdown('<div class="section-title">📋 Données par région</div>', unsafe_allow_html=True)
            display_data = latest_data[['region', 'urgences_grippe', 'vaccination_2024', 'alert_score']].copy()
            display_data.columns = ['Région', 'Urgences', 'Vaccination (%)', 'Score alerte']
            st.dataframe(display_data, use_container_width=True)
        
        else:
            st.error("Aucune donnée disponible")
    
    with tab2:
        st.markdown('<div class="section-title">🚨 Alertes actives</div>', unsafe_allow_html=True)
        
        alert_dashboard = app.create_alert_dashboard()
        if alert_dashboard is not None and len(alert_dashboard) > 0:
            st.dataframe(alert_dashboard, use_container_width=True)
        else:
            st.info("✅ Aucune alerte active")
    
    with tab3:
        st.markdown('<div class="section-title">⚙️ Configuration</div>', unsafe_allow_html=True)
        
        st.subheader("Seuils d'alerte")
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Seuil critique", "60", "Score minimum pour alerte")
            st.metric("Seuil élevé", "80", "Score pour alerte majeure")
        
        with col2:
            st.metric("Population totale", "67M", "Habitants en France")
            st.metric("Régions surveillées", "13", "Régions métropolitaines")
        
        st.subheader("Sources de données")
        st.info("""
        - **Santé Publique France** : Données épidémiologiques
        - **INSEE** : Données démographiques  
        - **Météo France** : Données climatiques
        - **Google Trends** : Signaux comportementaux
        """)

if __name__ == "__main__":
    main()
