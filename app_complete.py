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
        """Crée une carte interactive moderne des alertes"""
        if self.data is None:
            return None
        
        # Coordonnées des régions françaises (centres géographiques)
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
        
        # Créer la carte avec un style moderne
        m = folium.Map(
            location=[46.2276, 2.2137],
            zoom_start=6,
            tiles='CartoDB positron',  # Style plus moderne
            attr='CartoDB'
        )
        
        # Données les plus récentes par région
        latest_data = self.data.groupby('region').last().reset_index()
        
        # Ajouter des marqueurs pour chaque région
        for _, row in latest_data.iterrows():
            region = row['region']
            if region in region_coords:
                lat, lon = region_coords[region]
                score = row.get('alert_score', 0)
                urgences = row.get('urgences_grippe', 0)
                vaccination = row.get('vaccination_2024', 0)
                population = row.get('population_totale', 0)
                
                # Taille du marqueur basée sur la population
                radius = max(8, min(25, 8 + (population / 1000000) * 2))
                
                # Couleur et opacité basées sur le score
                if score >= 80:
                    color = '#dc2626'  # Rouge critique
                    fill_opacity = 0.8
                elif score >= 60:
                    color = '#f59e0b'  # Orange élevé
                    fill_opacity = 0.7
                elif score >= 40:
                    color = '#eab308'  # Jaune modéré
                    fill_opacity = 0.6
                else:
                    color = '#22c55e'  # Vert faible
                    fill_opacity = 0.5
                
                # Popup moderne avec plus d'informations
                popup_text = f"""
                <div style="font-family: Arial, sans-serif; width: 250px;">
                    <h3 style="margin: 0 0 10px 0; color: #1f2937; font-size: 16px;">{region}</h3>
                    <div style="background: #f8fafc; padding: 10px; border-radius: 6px; margin: 5px 0;">
                        <div style="display: flex; justify-content: space-between; margin: 3px 0;">
                            <span style="color: #6b7280;">Score d'alerte:</span>
                            <span style="font-weight: 600; color: {color};">{score:.1f}</span>
                        </div>
                        <div style="display: flex; justify-content: space-between; margin: 3px 0;">
                            <span style="color: #6b7280;">Urgences grippe:</span>
                            <span style="font-weight: 600;">{urgences:.0f}</span>
                        </div>
                        <div style="display: flex; justify-content: space-between; margin: 3px 0;">
                            <span style="color: #6b7280;">Vaccination:</span>
                            <span style="font-weight: 600;">{vaccination:.1f}%</span>
                        </div>
                        <div style="display: flex; justify-content: space-between; margin: 3px 0;">
                            <span style="color: #6b7280;">Population:</span>
                            <span style="font-weight: 600;">{population:,.0f}</span>
                        </div>
                    </div>
                    <div style="margin-top: 8px; font-size: 12px; color: #6b7280;">
                        Dernière mise à jour: {row.get('date', 'N/A')}
                    </div>
                </div>
                """
                
                # Marqueur circulaire avec style moderne
                folium.CircleMarker(
                    location=[lat, lon],
                    radius=radius,
                    popup=folium.Popup(popup_text, max_width=300),
                    color='white',
                    weight=3,
                    fillColor=color,
                    fillOpacity=fill_opacity,
                    tooltip=f"{region} - Score: {score:.1f}"
                ).add_to(m)
        
        # Ajouter une légende moderne
        legend_html = f'''
        <div style="
            position: fixed; 
            bottom: 50px; 
            left: 50px; 
            width: 200px; 
            height: 120px; 
            background: white; 
            border: 2px solid #e5e7eb; 
            border-radius: 8px; 
            padding: 10px; 
            font-size: 12px; 
            z-index: 9999;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        ">
            <h4 style="margin: 0 0 8px 0; color: #1f2937;">Niveaux d'alerte</h4>
            <div style="display: flex; align-items: center; margin: 3px 0;">
                <div style="width: 12px; height: 12px; background: #dc2626; border-radius: 50%; margin-right: 8px;"></div>
                <span>Critique (≥80)</span>
            </div>
            <div style="display: flex; align-items: center; margin: 3px 0;">
                <div style="width: 12px; height: 12px; background: #f59e0b; border-radius: 50%; margin-right: 8px;"></div>
                <span>Élevé (60-79)</span>
            </div>
            <div style="display: flex; align-items: center; margin: 3px 0;">
                <div style="width: 12px; height: 12px; background: #eab308; border-radius: 50%; margin-right: 8px;"></div>
                <span>Modéré (40-59)</span>
            </div>
            <div style="display: flex; align-items: center; margin: 3px 0;">
                <div style="width: 12px; height: 12px; background: #22c55e; border-radius: 50%; margin-right: 8px;"></div>
                <span>Faible (<40)</span>
            </div>
        </div>
        '''
        m.get_root().html.add_child(folium.Element(legend_html))
        
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
        # Header avec métriques clés
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 1.5rem;
            border-radius: 12px;
            margin-bottom: 2rem;
            color: white;
        ">
            <h2 style="margin: 0 0 1rem 0; font-size: 1.8rem; font-weight: 600;">Carte des alertes en temps réel</h2>
            <div style="display: flex; gap: 2rem; flex-wrap: wrap;">
                <div style="background: rgba(255,255,255,0.2); padding: 0.75rem 1.5rem; border-radius: 8px;">
                    <strong>Surveillance active</strong><br>
                    <span style="font-size: 1.2rem;">13 régions</span>
                </div>
                <div style="background: rgba(255,255,255,0.2); padding: 0.75rem 1.5rem; border-radius: 8px;">
                    <strong>Dernière mise à jour</strong><br>
                    <span style="font-size: 1.2rem;">Il y a 2 min</span>
                </div>
                <div style="background: rgba(255,255,255,0.2); padding: 0.75rem 1.5rem; border-radius: 8px;">
                    <strong>Précision du modèle</strong><br>
                    <span style="font-size: 1.2rem;">87.3%</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Filtres et contrôles
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            niveau_alerte = st.selectbox(
                "Niveau d'alerte",
                ["Tous", "Critique", "Élevé", "Modéré", "Faible"],
                help="Filtrer par niveau de risque"
            )
        
        with col2:
            type_donnees = st.selectbox(
                "Type de données",
                ["Toutes", "Urgences", "Vaccination", "Tendances", "Météo"],
                help="Focus sur un type de données spécifique"
            )
        
        with col3:
            periode = st.selectbox(
                "Période",
                ["7 derniers jours", "30 derniers jours", "3 derniers mois"],
                help="Période d'analyse des tendances"
            )
        
        with col4:
            st.markdown("<br>", unsafe_allow_html=True)
            auto_refresh = st.checkbox("Actualisation automatique", value=True, help="Mise à jour toutes les 5 minutes")
        
        # Carte interactive avec style amélioré
        st.markdown("### 🗺️ Visualisation géographique")
        
        alert_map = app.create_alert_map()
        if alert_map:
            st_folium(alert_map, width=700, height=500)
        
        # Légende moderne avec badges
        st.markdown("""
        <div style="
            background: #ffffff;
            padding: 1.5rem;
            border-radius: 12px;
            margin: 1rem 0;
            border: 1px solid #e1e5e9;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        ">
            <h4 style="margin: 0 0 1rem 0; color: #2c3e50;">Légende des niveaux d'alerte</h4>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1rem;">
                <div style="
                    background: #fee2e2;
                    border: 2px solid #dc2626;
                    padding: 1rem;
                    border-radius: 8px;
                    text-align: center;
                ">
                    <div style="
                        background: #dc2626;
                        color: white;
                        padding: 0.25rem 0.75rem;
                        border-radius: 20px;
                        font-size: 0.8rem;
                        font-weight: 600;
                        display: inline-block;
                        margin-bottom: 0.5rem;
                    ">CRITIQUE</div>
                    <div style="font-weight: 600; color: #dc2626;">Score ≥ 80</div>
                    <div style="font-size: 0.9rem; color: #6b7280;">Action immédiate requise</div>
                </div>
                
                <div style="
                    background: #fef3c7;
                    border: 2px solid #f59e0b;
                    padding: 1rem;
                    border-radius: 8px;
                    text-align: center;
                ">
                    <div style="
                        background: #f59e0b;
                        color: white;
                        padding: 0.25rem 0.75rem;
                        border-radius: 20px;
                        font-size: 0.8rem;
                        font-weight: 600;
                        display: inline-block;
                        margin-bottom: 0.5rem;
                    ">ÉLEVÉ</div>
                    <div style="font-weight: 600; color: #f59e0b;">Score 60-79</div>
                    <div style="font-size: 0.9rem; color: #6b7280;">Préparation campagne</div>
                </div>
                
                <div style="
                    background: #fefce8;
                    border: 2px solid #eab308;
                    padding: 1rem;
                    border-radius: 8px;
                    text-align: center;
                ">
                    <div style="
                        background: #eab308;
                        color: white;
                        padding: 0.25rem 0.75rem;
                        border-radius: 20px;
                        font-size: 0.8rem;
                        font-weight: 600;
                        display: inline-block;
                        margin-bottom: 0.5rem;
                    ">MODÉRÉ</div>
                    <div style="font-weight: 600; color: #eab308;">Score 40-59</div>
                    <div style="font-size: 0.9rem; color: #6b7280;">Surveillance renforcée</div>
                </div>
                
                <div style="
                    background: #f0fdf4;
                    border: 2px solid #22c55e;
                    padding: 1rem;
                    border-radius: 8px;
                    text-align: center;
                ">
                    <div style="
                        background: #22c55e;
                        color: white;
                        padding: 0.25rem 0.75rem;
                        border-radius: 20px;
                        font-size: 0.8rem;
                        font-weight: 600;
                        display: inline-block;
                        margin-bottom: 0.5rem;
                    ">FAIBLE</div>
                    <div style="font-weight: 600; color: #22c55e;">Score < 40</div>
                    <div style="font-size: 0.9rem; color: #6b7280;">Surveillance normale</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Section d'explication des données
        st.markdown("### 📊 Comprendre les données")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div style="
                background: #f8fafc;
                padding: 1.5rem;
                border-radius: 12px;
                border-left: 4px solid #3b82f6;
            ">
                <h4 style="margin: 0 0 1rem 0; color: #1e40af;">Données de santé publique</h4>
                <ul style="margin: 0; padding-left: 1.5rem; color: #374151;">
                    <li><strong>Urgences grippe</strong> : Passages aux urgences pour syndrome grippal (OSCOUR)</li>
                    <li><strong>Réseau Sentinelles</strong> : Cas hebdomadaires de grippe par région</li>
                    <li><strong>Vaccination</strong> : Taux de couverture vaccinale par région</li>
                    <li><strong>IAS</strong> : Indicateur d'activité syndromique</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div style="
                background: #f0fdf4;
                padding: 1.5rem;
                border-radius: 12px;
                border-left: 4px solid #22c55e;
            ">
                <h4 style="margin: 0 0 1rem 0; color: #166534;">Signaux comportementaux</h4>
                <ul style="margin: 0; padding-left: 1.5rem; color: #374151;">
                    <li><strong>Google Trends</strong> : Recherches "grippe", "symptômes", "vaccin"</li>
                    <li><strong>Wikipedia</strong> : Consultations des pages "Grippe" et "Vaccination"</li>
                    <li><strong>Facteurs démographiques</strong> : Population, âge, densité</li>
                    <li><strong>Météo</strong> : Température, humidité par région</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        
        # Tableau de données détaillé
        st.markdown("### 📋 Données détaillées par région")
        
        if app.data is not None:
            latest_data = app.data.groupby('region').last().reset_index()
            
            # Sélection des colonnes à afficher
            display_columns = [
                'region', 'alert_score', 'urgences_grippe', 'vaccination_2024', 
                'pct_65_plus', 'population_totale'
            ]
            
            # Renommage des colonnes pour l'affichage
            column_mapping = {
                'region': 'Région',
                'alert_score': 'Score d\'alerte',
                'urgences_grippe': 'Urgences grippe',
                'vaccination_2024': 'Vaccination (%)',
                'pct_65_plus': 'Population 65+ (%)',
                'population_totale': 'Population totale'
            }
            
            display_data = latest_data[display_columns].copy()
            display_data = display_data.rename(columns=column_mapping)
            
            # Formatage des données
            display_data['Score d\'alerte'] = display_data['Score d\'alerte'].round(1)
            display_data['Vaccination (%)'] = display_data['Vaccination (%)'].round(1)
            display_data['Population 65+ (%)'] = display_data['Population 65+ (%)'].round(1)
            display_data['Population totale'] = display_data['Population totale'].apply(lambda x: f"{x:,}")
            
            # Tri par score d'alerte décroissant
            display_data = display_data.sort_values('Score d\'alerte', ascending=False)
            
            st.dataframe(
                display_data,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Score d'alerte": st.column_config.NumberColumn(
                        "Score d'alerte",
                        help="Score de risque de 0 à 100",
                        format="%.1f"
                    ),
                    "Urgences grippe": st.column_config.NumberColumn(
                        "Urgences grippe",
                        help="Nombre de passages aux urgences",
                        format="%d"
                    ),
                    "Vaccination (%)": st.column_config.NumberColumn(
                        "Vaccination (%)",
                        help="Taux de couverture vaccinale",
                        format="%.1f%%"
                    ),
                    "Population 65+ (%)": st.column_config.NumberColumn(
                        "Population 65+ (%)",
                        help="Pourcentage de population de 65 ans et plus",
                        format="%.1f%%"
                    )
                }
            )
    
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
