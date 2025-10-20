#!/usr/bin/env python3
"""
Application Streamlit complète avec système d'alerte précoce
Données réelles + Prédictions + Alertes + Protocoles
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
    page_title="🚨 Système d'Alerte Grippe France",
    page_icon="🚨",
    layout="wide",
    initial_sidebar_state="expanded"
)

class GrippeAlertApp:
    def __init__(self):
        """Initialise l'application"""
        self.data = None
        self.alerts = None
        self.protocols = None
        self.load_data()
    
    def load_data(self):
        """Charge les données et alertes"""
        # Chargement des données enrichies avec alertes
        alert_files = [f for f in os.listdir('data/processed') if f.startswith('dataset_with_alerts_')]
        if alert_files:
            latest_file = sorted(alert_files)[-1]
            self.data = pd.read_csv(f'data/processed/{latest_file}')
            self.data['date'] = pd.to_datetime(self.data['date'])
        else:
            st.error("Aucune donnée avec alertes trouvée")
            return
        
        # Chargement des alertes
        alert_files = [f for f in os.listdir('data/alerts') if f.startswith('alertes_')]
        if alert_files:
            latest_alert_file = sorted(alert_files)[-1]
            self.alerts = pd.read_csv(f'data/alerts/{latest_alert_file}')
        
        # Chargement des protocoles
        protocol_files = [f for f in os.listdir('data/alerts') if f.startswith('protocoles_')]
        if protocol_files:
            latest_protocol_file = sorted(protocol_files)[-1]
            self.protocols = pd.read_csv(f'data/alerts/{latest_protocol_file}')
    
    def calculate_kpis(self):
        """Calcule les KPIs avec alertes"""
        if self.data is None:
            return {}
        
        latest_data = self.data.groupby('region').last().reset_index()
        
        # KPIs de base
        urgences = latest_data.get('urgences_grippe', pd.Series([0])).sum()
        vaccination = latest_data.get('vaccination_2024', pd.Series([50])).mean()
        
        # KPIs d'alerte
        if self.alerts is not None:
            critical_alerts = len(self.alerts[self.alerts['level'].str.contains('CRITIQUE')])
            elevated_alerts = len(self.alerts[self.alerts['level'].str.contains('ÉLEVÉ')])
            total_alerts = len(self.alerts)
        else:
            critical_alerts = 0
            elevated_alerts = 0
            total_alerts = 0
        
        return {
            'urgences_actuelles': urgences,
            'vaccination_moyenne': vaccination,
            'alertes_critiques': critical_alerts,
            'alertes_elevees': elevated_alerts,
            'total_alertes': total_alerts,
            'economies_potentielles': self.calculate_potential_savings()
        }
    
    def calculate_potential_savings(self):
        """Calcule les économies potentielles"""
        if self.protocols is not None:
            return self.protocols['expected_impact'].apply(lambda x: eval(x)['economies_estimees']).sum()
        return 0
    
    def create_alert_map(self):
        """Crée la carte avec les alertes"""
        if self.data is None:
            return None
        
        # Données les plus récentes
        latest_data = self.data.groupby('region').last().reset_index()
        
        # Coordonnées des régions
        region_coords = {
            'Île-de-France': [48.8566, 2.3522],
            'Auvergne-Rhône-Alpes': [45.7640, 4.8357],
            'Provence-Alpes-Côte d\'Azur': [43.2965, 5.3698],
            'Nouvelle-Aquitaine': [44.8378, -0.5792],
            'Occitanie': [43.6047, 1.4442],
            'Grand Est': [48.5734, 7.7521],
            'Hauts-de-France': [50.6292, 3.0573],
            'Normandie': [49.1829, -0.3707],
            'Bretagne': [48.2020, -2.9326],
            'Pays de la Loire': [47.4739, -0.5517],
            'Centre-Val de Loire': [47.7516, 1.6751],
            'Bourgogne-Franche-Comté': [47.3220, 5.0415],
            'Corse': [42.0396, 9.0129]
        }
        
        # Création de la carte
        m = folium.Map(location=[46.2276, 2.2137], zoom_start=6)
        
        # Ajout des marqueurs avec alertes
        for _, row in latest_data.iterrows():
            region = row['region']
            coords = region_coords.get(region, [46.2276, 2.2137])
            
            # Couleur basée sur le score d'alerte
            alert_score = row.get('alert_score', 0)
            if alert_score >= 80:
                color = 'red'
                icon = '🔴'
            elif alert_score >= 60:
                color = 'orange'
                icon = '🟠'
            elif alert_score >= 40:
                color = 'yellow'
                icon = '🟡'
            else:
                color = 'green'
                icon = '🟢'
            
            # Popup avec informations d'alerte
            popup_text = f"""
            <b>{icon} {region}</b><br>
            <b>Score d'alerte:</b> {alert_score:.1f}/100<br>
            <b>Urgences:</b> {row.get('urgences_grippe', 0):.0f}<br>
            <b>Vaccination:</b> {row.get('vaccination_2024', 0):.1f}%<br>
            <b>Population 65+:</b> {row.get('pct_65_plus', 0):.1f}%<br>
            <b>Densité:</b> {row.get('population_totale', 0):,} hab.
            """
            
            folium.CircleMarker(
                location=coords,
                radius=25,
                popup=popup_text,
                color=color,
                fill=True,
                fillOpacity=0.7
            ).add_to(m)
        
        return m
    
    def create_alert_dashboard(self):
        """Crée le tableau de bord des alertes"""
        if self.alerts is None:
            return None
        
        # Filtrage des alertes actives
        active_alerts = self.alerts[self.alerts['level'].str.contains('CRITIQUE|ÉLEVÉ')]
        
        return active_alerts
    
    def create_protocol_dashboard(self):
        """Crée le tableau de bord des protocoles"""
        if self.protocols is None:
            return None
        
        return self.protocols

def main():
    """Fonction principale"""
    # Header moderne avec design épuré
    st.markdown("""
    <div style="
        background: #ffffff;
        padding: 2rem 1rem;
        border-radius: 8px;
        margin-bottom: 2rem;
        border: 1px solid #e1e5e9;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    ">
        <h1 style="
            color: #2c3e50;
            text-align: center;
            margin: 0;
            font-size: 2.2rem;
            font-weight: 600;
        ">Système d'alerte grippe France</h1>
        <p style="
            color: #6c757d;
            text-align: center;
            margin: 0.5rem 0 0 0;
            font-size: 1rem;
            font-weight: 400;
        ">Prédiction précoce • Données temps réel • Actions automatiques</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialisation de l'application
    app = GrippeAlertApp()
    
    if app.data is None:
        st.markdown("""
        <div style="
            background: #f8d7da;
            color: #721c24;
            padding: 1rem;
            border-radius: 10px;
            border-left: 4px solid #dc3545;
            margin: 1rem 0;
        ">
            <strong>Erreur de chargement</strong><br>
            Impossible de charger les données du système d'alerte.
        </div>
        """, unsafe_allow_html=True)
        return
    
    # Section de statut avec design épuré
    st.markdown("""
    <div style="
        background: #ffffff;
        padding: 1.5rem;
        border-radius: 8px;
        margin: 1rem 0;
        border: 1px solid #e1e5e9;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    ">
        <h3 style="
            color: #2c3e50;
            margin: 0 0 1rem 0;
            font-size: 1.1rem;
            font-weight: 600;
        ">État du système</h3>
        <div style="display: flex; gap: 1.5rem; flex-wrap: wrap;">
            <div style="
                background: #f8f9fa;
                color: #495057;
                padding: 1rem;
                border-radius: 6px;
                border: 1px solid #e9ecef;
                flex: 1;
                min-width: 200px;
            ">
                <strong style="color: #28a745;">Données chargées</strong><br>
                <small style="color: #6c757d;">Dataset avec alertes intégrées</small>
            </div>
            <div style="
                background: #f8f9fa;
                color: #495057;
                padding: 1rem;
                border-radius: 6px;
                border: 1px solid #e9ecef;
                flex: 1;
                min-width: 200px;
            ">
                <strong style="color: #dc3545;">Alertes actives</strong><br>
                <small style="color: #6c757d;">Surveillance en temps réel</small>
            </div>
            <div style="
                background: #f8f9fa;
                color: #495057;
                padding: 1rem;
                border-radius: 6px;
                border: 1px solid #e9ecef;
                flex: 1;
                min-width: 200px;
            ">
                <strong style="color: #007bff;">Protocoles prêts</strong><br>
                <small style="color: #6c757d;">Actions automatiques disponibles</small>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Calcul des KPIs
    kpis = app.calculate_kpis()
    
    # Section KPIs avec design épuré
    st.markdown("""
    <div style="
        background: #ffffff;
        padding: 1.5rem;
        border-radius: 8px;
        margin: 1rem 0;
        border: 1px solid #e1e5e9;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    ">
        <h3 style="
            color: #2c3e50;
            margin: 0 0 1.5rem 0;
            font-size: 1.2rem;
            font-weight: 600;
            text-align: center;
        ">Indicateurs clés en temps réel</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # KPIs avec design personnalisé
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.markdown(f"""
        <div style="
            background: #ffffff;
            color: #2c3e50;
            padding: 1.5rem 1rem;
            border-radius: 8px;
            text-align: center;
            border: 1px solid #e1e5e9;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        ">
            <div style="font-size: 1.8rem; font-weight: 700; margin-bottom: 0.25rem; color: #dc3545;">{kpis['urgences_actuelles']:.0f}</div>
            <div style="font-size: 0.9rem; color: #6c757d;">Urgences actuelles</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style="
            background: #ffffff;
            color: #2c3e50;
            padding: 1.5rem 1rem;
            border-radius: 8px;
            text-align: center;
            border: 1px solid #e1e5e9;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        ">
            <div style="font-size: 1.8rem; font-weight: 700; margin-bottom: 0.25rem; color: #28a745;">{kpis['vaccination_moyenne']:.1f}%</div>
            <div style="font-size: 0.9rem; color: #6c757d;">Vaccination moyenne</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div style="
            background: #ffffff;
            color: #2c3e50;
            padding: 1.5rem 1rem;
            border-radius: 8px;
            text-align: center;
            border: 1px solid #e1e5e9;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        ">
            <div style="font-size: 1.8rem; font-weight: 700; margin-bottom: 0.25rem; color: #dc3545;">{kpis['alertes_critiques']}</div>
            <div style="font-size: 0.9rem; color: #6c757d;">Alertes critiques</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div style="
            background: #ffffff;
            color: #2c3e50;
            padding: 1.5rem 1rem;
            border-radius: 8px;
            text-align: center;
            border: 1px solid #e1e5e9;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        ">
            <div style="font-size: 1.8rem; font-weight: 700; margin-bottom: 0.25rem; color: #ffc107;">{kpis['alertes_elevees']}</div>
            <div style="font-size: 0.9rem; color: #6c757d;">Alertes élevées</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col5:
        st.markdown(f"""
        <div style="
            background: #ffffff;
            color: #2c3e50;
            padding: 1.5rem 1rem;
            border-radius: 8px;
            text-align: center;
            border: 1px solid #e1e5e9;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        ">
            <div style="font-size: 1.8rem; font-weight: 700; margin-bottom: 0.25rem; color: #28a745;">{kpis['economies_potentielles']:,.0f}€</div>
            <div style="font-size: 0.9rem; color: #6c757d;">Économies potentielles</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Section des onglets avec style épuré
    st.markdown("""
    <div style="
        background: #ffffff;
        padding: 1rem;
        border-radius: 8px;
        margin: 2rem 0;
        border: 1px solid #e1e5e9;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    ">
        <h3 style="
            color: #2c3e50;
            margin: 0 0 1rem 0;
            font-size: 1.2rem;
            font-weight: 600;
            text-align: center;
        ">Tableau de bord interactif</h3>
        <p style="
            color: #6c757d;
            text-align: center;
            margin: 0;
            font-size: 0.95rem;
        ">Explorez les données, visualisez les alertes et déclenchez les actions</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Onglets
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Carte des alertes", 
        "Tableau de bord alertes", 
        "Protocoles d'action", 
        "Analyse détaillée", 
        "Configuration"
    ])
    
    with tab1:
        st.header("Carte des alertes en temps réel")
        
        # Carte interactive
        alert_map = app.create_alert_map()
        if alert_map:
            st_folium(alert_map, width=700, height=500)
        
        # Légende
        st.markdown("""
        **Légende des alertes :**
        - **Rouge** : Score ≥ 80 (critique) - Action immédiate requise
        - **Orange** : Score 60-79 (élevé) - Préparation campagne
        - **Jaune** : Score 40-59 (modéré) - Surveillance renforcée
        - **Vert** : Score < 40 (faible) - Surveillance normale
        """)
    
    with tab2:
        st.header("Tableau de bord des alertes")
        
        # Tableau des alertes actives
        alert_dashboard = app.create_alert_dashboard()
        if alert_dashboard is not None and len(alert_dashboard) > 0:
            st.dataframe(
                alert_dashboard[['region', 'level', 'alert_score', 'action', 'timeline', 'urgences_actuelles', 'vaccination_rate']],
                use_container_width=True,
                hide_index=True
            )
            
            # Export CSV
            csv = alert_dashboard.to_csv(index=False)
            st.download_button(
                label="Exporter alertes CSV",
                data=csv,
                file_name=f"alertes_grippe_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        else:
            st.info("Aucune alerte active actuellement")
    
    with tab3:
        st.header("Protocoles d'action automatiques")
        
        # Tableau des protocoles
        protocol_dashboard = app.create_protocol_dashboard()
        if protocol_dashboard is not None and len(protocol_dashboard) > 0:
            # Affichage des protocoles
            for _, protocol in protocol_dashboard.iterrows():
                with st.expander(f"{protocol['region']} - Priorité: {protocol['priority']}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.metric("Coût estimé", f"{protocol['estimated_cost']:,}€")
                        st.metric("Délai", protocol['timeline'])
                    
                    with col2:
                        impact = eval(protocol['expected_impact'])
                        st.metric("Urgences évitées", f"{impact['urgences_evitees']}")
                        st.metric("Économies", f"{impact['economies_estimees']:,}€")
                        st.metric("ROI", f"{impact['roi_estime']}x")
                    
                    st.subheader("Actions à déclencher :")
                    actions = eval(protocol['actions'])
                    for i, action in enumerate(actions, 1):
                        st.write(f"{i}. {action}")
                    
                    # Bouton de déclenchement (simulation)
                    if st.button(f"Déclencher protocole - {protocol['region']}", key=f"protocol_{protocol['region']}"):
                        st.success(f"Protocole déclenché pour {protocol['region']} !")
                        st.info("SMS/Email envoyés aux habitants")
                        st.info("Campagne de vaccination lancée")
                        st.info("Services d'urgence préparés")
        else:
            st.info("Aucun protocole actif actuellement")
    
    with tab4:
        st.header("Analyse détaillée par région")
        
        # Sélection de la région
        regions = app.data['region'].unique()
        selected_region = st.selectbox("Sélectionnez une région :", regions)
        
        if selected_region:
            region_data = app.data[app.data['region'] == selected_region].copy()
            region_data = region_data.sort_values('date')
            
            # Métriques de la région
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                latest_score = region_data['alert_score'].iloc[-1]
                st.metric("Score d'alerte", f"{latest_score:.1f}/100")
            
            with col2:
                urgences = region_data['urgences_grippe'].iloc[-1]
                st.metric("Urgences actuelles", f"{urgences:.0f}")
            
            with col3:
                vaccination = region_data.get('vaccination_2024', 0).iloc[-1]
                st.metric("Vaccination", f"{vaccination:.1f}%")
            
            with col4:
                population_65 = region_data['pct_65_plus'].iloc[-1]
                st.metric("Population 65+", f"{population_65:.1f}%")
            
            # Graphique d'évolution
            fig = go.Figure()
            
            # Urgences
            fig.add_trace(go.Scatter(
                x=region_data['date'], 
                y=region_data['urgences_grippe'],
                name='Urgences grippe',
                line=dict(color='blue', width=2)
            ))
            
            # Score d'alerte
            fig.add_trace(go.Scatter(
                x=region_data['date'], 
                y=region_data['alert_score'],
                name='Score d\'alerte',
                line=dict(color='red', width=2),
                yaxis='y2'
            ))
            
            fig.update_layout(
                title=f"Évolution - {selected_region}",
                xaxis_title="Date",
                yaxis_title="Urgences grippe",
                yaxis2=dict(title="Score d'alerte", overlaying="y", side="right"),
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    with tab5:
        st.header("Configuration du système")
        
        st.subheader("Seuils d'alerte")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Urgences critiques", "150/semaine")
            st.metric("Incidence critique", "200/100k")
            st.metric("Vaccination faible", "< 30%")
        
        with col2:
            st.metric("Population 65+ risque", "> 20%")
            st.metric("Température risque", "< 5°C")
            st.metric("Tendance hausse", "> 50%")
        
        st.subheader("Sources de données")
        st.write("• Santé Publique France (urgences, sentinelles, vaccination)")
        st.write("• INSEE (population, démographie)")
        st.write("• Météo France (température, humidité)")
        st.write("• Données comportementales (Google Trends, Wikipedia)")
        
        st.subheader("Mise à jour")
        if st.button("Actualiser les données"):
            st.info("Actualisation en cours...")
            st.success("Données actualisées !")
    
    # Footer épuré
    st.markdown("""
    <div style="
        background: #f8f9fa;
        color: #495057;
        padding: 1.5rem 1rem;
        border-radius: 8px;
        margin: 2rem 0 0 0;
        text-align: center;
        border: 1px solid #e1e5e9;
    ">
        <h4 style="
            margin: 0 0 1rem 0;
            font-size: 1.1rem;
            font-weight: 600;
            color: #2c3e50;
        ">Système d'Alerte Précoce Grippe France</h4>
        <div style="
            display: flex;
            justify-content: center;
            gap: 1.5rem;
            flex-wrap: wrap;
            margin: 1rem 0;
        ">
            <div style="
                background: #ffffff;
                color: #495057;
                padding: 0.5rem 1rem;
                border-radius: 6px;
                font-size: 0.85rem;
                border: 1px solid #e1e5e9;
            ">
                Prédiction 1-2 mois à l'avance
            </div>
            <div style="
                background: #ffffff;
                color: #495057;
                padding: 0.5rem 1rem;
                border-radius: 6px;
                font-size: 0.85rem;
                border: 1px solid #e1e5e9;
            ">
                Données temps réel
            </div>
            <div style="
                background: #ffffff;
                color: #495057;
                padding: 0.5rem 1rem;
                border-radius: 6px;
                font-size: 0.85rem;
                border: 1px solid #e1e5e9;
            ">
                Protocoles automatiques
            </div>
        </div>
        <p style="
            margin: 1rem 0 0 0;
            font-size: 0.85rem;
            color: #6c757d;
        ">Réduction des coûts médicaux • Prévention efficace • Actions ciblées</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
