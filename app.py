#!/usr/bin/env python3
"""
Interface Streamlit pour le système de prédiction grippe
4 vues : Carte France, Top 10 priorités, Zoom département, Simulation ROI
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import folium
from streamlit_folium import st_folium
import joblib
import json
import os
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Configuration de la page
st.set_page_config(
    page_title="🔮 Prédiction Grippe France",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="expanded"
)

class GrippeDashboard:
    def __init__(self):
        """Initialise le dashboard"""
        self.data = None
        self.models = {}
        self.config = None
        self.load_data()
    
    def load_data(self):
        """Charge les données et modèles"""
        # Chargement du dataset avec prédictions
        dataset_files = [f for f in os.listdir('data/processed') if 'dataset_with_predictions' in f and f.endswith('.csv')]
        if dataset_files:
            latest_dataset = sorted(dataset_files)[-1]
            self.data = pd.read_csv(f'data/processed/{latest_dataset}')
            self.data['date'] = pd.to_datetime(self.data['date'])
            st.success(f"✅ Données chargées: {latest_dataset}")
        else:
            st.error("❌ Aucun dataset trouvé")
            return
        
        # Chargement de la configuration des modèles
        config_files = [f for f in os.listdir('models') if f.startswith('config_') and f.endswith('.json')]
        if config_files:
            latest_config = sorted(config_files)[-1]
            with open(f'models/{latest_config}', 'r') as f:
                self.config = json.load(f)
            st.success(f"✅ Configuration chargée: {latest_config}")
        else:
            st.error("❌ Aucune configuration de modèle trouvée")
            return
    
    def calculate_kpis(self):
        """Calcule les KPIs principaux"""
        latest_week = self.data['date'].max()
        latest_data = self.data[self.data['date'] == latest_week]
        
        kpis = {
            'urgences_j28': latest_data['pred_urgences_grippe_j28'].sum(),
            'depts_alerte': len(latest_data[latest_data['flurisk'] > 70]),
            'vaccination_moy': latest_data['taux_vaccination'].mean(),
            'gain_potentiel': latest_data['pred_urgences_grippe_j28'].sum() * 0.05
        }
        
        return kpis
    
    def create_france_map(self):
        """Crée la carte de France avec FLURISK"""
        latest_week = self.data['date'].max()
        latest_data = self.data[self.data['date'] == latest_week].copy()
        
        # Coordonnées des régions (approximatives)
        region_coords = {
            'Île-de-France': [48.8566, 2.3522],
            'Auvergne-Rhône-Alpes': [45.7640, 4.8357],
            'Nouvelle-Aquitaine': [44.8378, -0.5792],
            'Occitanie': [43.6047, 1.4442],
            'Hauts-de-France': [50.6292, 3.0573],
            'Grand Est': [48.5734, 7.7521],
            'Pays de la Loire': [47.2184, -1.5536],
            'Bretagne': [48.2020, -2.9326],
            'Normandie': [49.4432, 1.0993],
            'Centre-Val de Loire': [47.7516, 1.6753],
            'Bourgogne-Franche-Comté': [47.3220, 5.0415],
            'Provence-Alpes-Côte d\'Azur': [43.2965, 5.3698],
            'Corse': [42.0396, 9.0129]
        }
        
        # Création de la carte
        m = folium.Map(location=[46.0, 2.0], zoom_start=6)
        
        # Ajout des marqueurs par région
        for _, row in latest_data.iterrows():
            region = row['region']
            if region in region_coords:
                lat, lon = region_coords[region]
                flurisk = row['flurisk']
                urgences = row['pred_urgences_grippe_j28']
                vaccination = row['taux_vaccination']
                
                # Couleur selon FLURISK
                if flurisk > 70:
                    color = 'red'
                elif flurisk > 50:
                    color = 'orange'
                else:
                    color = 'green'
                
                # Popup avec informations
                popup_text = f"""
                <b>{region}</b><br>
                FLURISK: {flurisk:.1f}<br>
                Urgences J+28: {urgences:.0f}<br>
                Vaccination: {vaccination:.1f}%
                """
                
                folium.CircleMarker(
                    location=[lat, lon],
                    radius=20,
                    popup=popup_text,
                    color=color,
                    fill=True,
                    fillOpacity=0.7
                ).add_to(m)
        
        return m
    
    def create_top10_table(self):
        """Crée le tableau Top 10 des priorités"""
        latest_week = self.data['date'].max()
        latest_data = self.data[self.data['date'] == latest_week].copy()
        
        # Calcul des recommandations
        def get_recommendation(flurisk, urgences, vaccination):
            if flurisk > 70:
                doses_needed = max(0, int((100 - vaccination) * 1000))
                return f"🔴 Réaffecter +{doses_needed} doses"
            elif flurisk > 50:
                return "🟠 Campagne locale"
            else:
                return "🟢 OK"
        
        latest_data['recommendation'] = latest_data.apply(
            lambda row: get_recommendation(row['flurisk'], row['pred_urgences_grippe_j28'], row['taux_vaccination']),
            axis=1
        )
        
        # Tri par FLURISK décroissant
        top10 = latest_data.nlargest(10, 'flurisk')[
            ['region', 'flurisk', 'pred_urgences_grippe_j28', 'taux_vaccination', 'recommendation']
        ].round(1)
        
        return top10
    
    def create_department_analysis(self, selected_region):
        """Crée l'analyse détaillée d'un département"""
        region_data = self.data[self.data['region'] == selected_region].copy()
        region_data = region_data.sort_values('date')
        
        # Graphique des tendances
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Urgences vs Prédictions', 'FLURISK', 'Vaccination', 'IAS'),
            specs=[[{"secondary_y": True}, {"type": "indicator"}],
                   [{"type": "indicator"}, {"type": "indicator"}]]
        )
        
        # Courbe urgences réelles vs prédictions
        fig.add_trace(
            go.Scatter(x=region_data['date'], y=region_data['urgences_grippe'], 
                      name='Urgences réelles', line=dict(color='blue')),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Scatter(x=region_data['date'], y=region_data['pred_urgences_grippe_j7'], 
                      name='Prédiction J+7', line=dict(color='red', dash='dash')),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Scatter(x=region_data['date'], y=region_data['pred_urgences_grippe_j28'], 
                      name='Prédiction J+28', line=dict(color='orange', dash='dash')),
            row=1, col=1
        )
        
        # Jauge FLURISK
        latest_flurisk = region_data['flurisk'].iloc[-1]
        fig.add_trace(
            go.Indicator(
                mode="gauge+number",
                value=latest_flurisk,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "FLURISK"},
                gauge={'axis': {'range': [None, 100]},
                       'bar': {'color': "darkblue"},
                       'steps': [{'range': [0, 50], 'color': "lightgray"},
                                {'range': [50, 70], 'color': "yellow"},
                                {'range': [70, 100], 'color': "red"}]}
            ),
            row=1, col=2
        )
        
        # Jauge Vaccination
        latest_vaccination = region_data['taux_vaccination'].iloc[-1]
        fig.add_trace(
            go.Indicator(
                mode="gauge+number",
                value=latest_vaccination,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "Vaccination %"},
                gauge={'axis': {'range': [None, 100]},
                       'bar': {'color': "green"},
                       'steps': [{'range': [0, 50], 'color': "lightgray"},
                                {'range': [50, 70], 'color': "yellow"},
                                {'range': [70, 100], 'color': "green"}]}
            ),
            row=2, col=1
        )
        
        # Jauge IAS
        latest_ias = region_data['ias_syndrome_grippal'].iloc[-1]
        fig.add_trace(
            go.Indicator(
                mode="gauge+number",
                value=latest_ias,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "IAS"},
                gauge={'axis': {'range': [None, 2]},
                       'bar': {'color': "purple"}}
            ),
            row=2, col=2
        )
        
        fig.update_layout(height=600, showlegend=True)
        return fig
    
    def create_simulation(self, boost_vaccination):
        """Crée la simulation ROI"""
        latest_week = self.data['date'].max()
        latest_data = self.data[self.data['date'] == latest_week].copy()
        
        # Simulation avec boost de vaccination
        latest_data['vaccination_boosted'] = np.clip(
            latest_data['taux_vaccination'] + boost_vaccination, 0, 100
        )
        
        # Calcul des urgences évitées (formule simplifiée)
        latest_data['urgences_evitees'] = latest_data['pred_urgences_grippe_j28'] * (boost_vaccination / 100) * 0.02
        
        # Calculs ROI
        cost_per_vaccine = 10  # €
        cost_per_emergency = 300  # €
        
        latest_data['cout_campagne'] = (latest_data['vaccination_boosted'] - latest_data['taux_vaccination']) * latest_data['population_totale'] / 100 * cost_per_vaccine
        latest_data['economies'] = latest_data['urgences_evitees'] * cost_per_emergency
        latest_data['roi'] = (latest_data['economies'] - latest_data['cout_campagne']) / latest_data['cout_campagne'] * 100
        
        # Top 10 des départements avec le meilleur ROI
        top_roi = latest_data.nlargest(10, 'roi')[
            ['region', 'urgences_evitees', 'cout_campagne', 'economies', 'roi']
        ].round(1)
        
        return latest_data, top_roi

def main():
    """Fonction principale de l'application"""
    st.title("🔮 Système de Prédiction Grippe France")
    st.markdown("---")
    
    # Initialisation du dashboard
    dashboard = GrippeDashboard()
    
    if dashboard.data is None:
        st.error("❌ Impossible de charger les données")
        return
    
    # Sidebar
    st.sidebar.title("🎛️ Contrôles")
    
    # Sélection de la vue
    view = st.sidebar.selectbox(
        "Choisir la vue",
        ["🇫🇷 Carte France", "📋 Top 10 Priorités", "🔍 Zoom Département", "🎛️ Simulation ROI"]
    )
    
    # Vue 1: Carte France
    if view == "🇫🇷 Carte France":
        st.header("🇫🇷 Carte France - Vue d'ensemble")
        
        # KPIs
        kpis = dashboard.calculate_kpis()
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Urgences prévues J+28", f"{kpis['urgences_j28']:.0f}")
        with col2:
            st.metric("Départements en alerte", f"{kpis['depts_alerte']}")
        with col3:
            st.metric("Vaccination moyenne", f"{kpis['vaccination_moy']:.1f}%")
        with col4:
            st.metric("Gain si +5% vaccination", f"{kpis['gain_potentiel']:.0f} urgences")
        
        # Carte
        st.subheader("Carte FLURISK par région")
        france_map = dashboard.create_france_map()
        st_folium(france_map, width=700, height=500)
        
        # Légende
        st.info("""
        **Légende FLURISK:**
        - 🔴 Rouge: Risque élevé (>70) - Action immédiate requise
        - 🟠 Orange: Risque moyen (50-70) - Surveillance renforcée
        - 🟢 Vert: Risque faible (<50) - Situation normale
        """)
    
    # Vue 2: Top 10 Priorités
    elif view == "📋 Top 10 Priorités":
        st.header("📋 Top 10 Priorités - Actions recommandées")
        
        top10 = dashboard.create_top10_table()
        
        # Tableau
        st.dataframe(top10, use_container_width=True)
        
        # Bouton d'export
        csv = top10.to_csv(index=False)
        st.download_button(
            label="📥 Exporter CSV pour ARS",
            data=csv,
            file_name=f"priorites_grippe_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
        
        # Explication des recommandations
        st.info("""
        **Recommandations automatiques:**
        - 🔴 **Réaffecter +X doses**: Départements à risque élevé nécessitant une action immédiate
        - 🟠 **Campagne locale**: Départements à surveiller avec communication ciblée
        - 🟢 **OK**: Départements avec situation normale
        """)
    
    # Vue 3: Zoom Département
    elif view == "🔍 Zoom Département":
        st.header("🔍 Zoom Département - Analyse détaillée")
        
        # Sélection du département
        regions = sorted(dashboard.data['region'].unique())
        selected_region = st.selectbox("Sélectionner un département", regions)
        
        if selected_region:
            # Graphiques d'analyse
            fig = dashboard.create_department_analysis(selected_region)
            st.plotly_chart(fig, use_container_width=True)
            
            # Informations détaillées
            region_data = dashboard.data[dashboard.data['region'] == selected_region]
            latest = region_data.iloc[-1]
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("FLURISK actuel", f"{latest['flurisk']:.1f}")
            with col2:
                st.metric("Vaccination", f"{latest['taux_vaccination']:.1f}%")
            with col3:
                st.metric("Population 65+", f"{latest['pct_65_plus']:.1f}%")
    
    # Vue 4: Simulation ROI
    elif view == "🎛️ Simulation ROI":
        st.header("🎛️ Simulation ROI - Impact des campagnes")
        
        # Slider de boost vaccination
        boost_vaccination = st.slider(
            "Boost de vaccination (%)",
            min_value=0,
            max_value=20,
            value=5,
            step=1
        )
        
        # Simulation
        sim_data, top_roi = dashboard.create_simulation(boost_vaccination)
        
        # KPIs de simulation
        total_urgences_evitees = sim_data['urgences_evitees'].sum()
        total_cout = sim_data['cout_campagne'].sum()
        total_economies = sim_data['economies'].sum()
        roi_global = (total_economies - total_cout) / total_cout * 100 if total_cout > 0 else 0
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Urgences évitées", f"{total_urgences_evitees:.0f}")
        with col2:
            st.metric("Coût campagne", f"{total_cout:,.0f} €")
        with col3:
            st.metric("Économies", f"{total_economies:,.0f} €")
        with col4:
            st.metric("ROI global", f"{roi_global:.1f}%")
        
        # Top 10 ROI
        st.subheader("Top 10 départements - Meilleur ROI")
        st.dataframe(top_roi, use_container_width=True)
        
        # Graphique de comparaison
        fig = px.bar(
            top_roi.head(10),
            x='region',
            y='roi',
            title=f"ROI par département (+{boost_vaccination}% vaccination)",
            labels={'roi': 'ROI (%)', 'region': 'Département'}
        )
        fig.update_xaxis(tickangle=45)
        st.plotly_chart(fig, use_container_width=True)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: gray;'>
    🔮 Système de Prédiction Grippe France | Données mises à jour automatiquement
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
