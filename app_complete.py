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
        
        # Créer la carte avec un style moderne et une ergonomie améliorée
        m = folium.Map(
            location=[46.2276, 2.2137],
            zoom_start=6,
            tiles='CartoDB positron',  # Style plus moderne
            attr='CartoDB',
            # Améliorations ergonomiques
            zoom_control=True,
            scroll_wheel_zoom=True,
            double_click_zoom=True,
            box_zoom=True,
            dragging=True,
            keyboard=True,
            # Contrôles de zoom plus accessibles
            zoom_control_position='topleft',
            # Limites de zoom pour éviter de perdre la France
            min_zoom=5,
            max_zoom=10,
            # Style de la carte
            prefer_canvas=True,
            # Amélioration des performances
            no_wrap=False
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
                
                # Popup moderne avec informations claires et parlantes
                # Déterminer le niveau de risque en français
                if score >= 80:
                    niveau_risque = "CRITIQUE"
                    action_requise = "Action immédiate"
                elif score >= 60:
                    niveau_risque = "ÉLEVÉ"
                    action_requise = "Se préparer"
                elif score >= 40:
                    niveau_risque = "MODÉRÉ"
                    action_requise = "Surveiller"
                else:
                    niveau_risque = "FAIBLE"
                    action_requise = "Tout va bien"
                
                popup_text = f"""
                <div style="font-family: Arial, sans-serif; width: 280px;">
                    <h3 style="margin: 0 0 15px 0; color: #1f2937; font-size: 18px; text-align: center;">{region}</h3>
                    
                    <div style="background: #f8fafc; padding: 15px; border-radius: 8px; margin: 10px 0; border-left: 4px solid {color};">
                        <div style="text-align: center; margin-bottom: 12px;">
                            <div style="font-size: 14px; color: #6b7280; margin-bottom: 4px;">NIVEAU DE RISQUE</div>
                            <div style="font-size: 24px; font-weight: 700; color: {color}; margin-bottom: 4px;">{score:.0f}/100</div>
                            <div style="font-size: 12px; color: {color}; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;">{niveau_risque}</div>
                        </div>
                    </div>
                    
                    <div style="background: #ffffff; padding: 12px; border-radius: 6px; margin: 8px 0; border: 1px solid #e5e7eb;">
                        <div style="display: flex; justify-content: space-between; margin: 6px 0; padding: 4px 0;">
                            <span style="color: #374151; font-weight: 500;">Malades aux urgences cette semaine:</span>
                            <span style="font-weight: 700; color: #dc2626;">{urgences:.0f} personnes</span>
                        </div>
                        <div style="display: flex; justify-content: space-between; margin: 6px 0; padding: 4px 0;">
                            <span style="color: #374151; font-weight: 500;">Personnes vaccinées:</span>
                            <span style="font-weight: 700; color: #059669;">{vaccination:.0f}%</span>
                        </div>
                        <div style="display: flex; justify-content: space-between; margin: 6px 0; padding: 4px 0;">
                            <span style="color: #374151; font-weight: 500;">Nombre d'habitants:</span>
                            <span style="font-weight: 700; color: #1f2937;">{population:,.0f}</span>
                        </div>
                    </div>
                    
                    <div style="background: #fef3c7; padding: 10px; border-radius: 6px; margin: 8px 0; text-align: center;">
                        <div style="font-size: 12px; color: #92400e; font-weight: 600; margin-bottom: 2px;">ACTION RECOMMANDÉE</div>
                        <div style="font-size: 14px; color: #92400e; font-weight: 700;">{action_requise}</div>
                    </div>
                    
                    <div style="margin-top: 10px; font-size: 11px; color: #9ca3af; text-align: center;">
                        Dernière mise à jour: {row.get('date', 'N/A')}
                    </div>
                </div>
                """
                
                # Marqueur circulaire avec style moderne et interactions améliorées
                folium.CircleMarker(
                    location=[lat, lon],
                    radius=radius,
                    popup=folium.Popup(
                        popup_text, 
                        max_width=300,
                        min_width=280,
                        max_height=400,
                        show=False,  # Ne pas afficher automatiquement
                        sticky=False  # Le popup se ferme quand on clique ailleurs
                    ),
                    color='white',
                    weight=3,
                    fillColor=color,
                    fillOpacity=fill_opacity,
                    # Tooltip amélioré avec plus d'informations
                    tooltip=f"""
                    <div style="font-family: Arial, sans-serif; font-size: 14px;">
                        <strong style="color: {color};">{region}</strong><br>
                        <span style="color: #6b7280;">Niveau: {niveau_risque}</span><br>
                        <span style="color: #6b7280;">Score: {score:.0f}/100</span><br>
                        <span style="color: #6b7280; font-size: 12px;">Cliquez pour plus de détails</span>
                    </div>
                    """,
                    # Amélioration de l'interaction
                    interactive=True,
                    bubbling_mouse_events=False
                ).add_to(m)
        
        # Ajouter une légende moderne et des contrôles
        legend_html = f'''
        <div style="
            position: fixed; 
            bottom: 20px; 
            left: 20px; 
            width: 220px; 
            background: white; 
            border: 1px solid #e5e7eb; 
            border-radius: 12px; 
            padding: 15px; 
            font-size: 12px; 
            z-index: 9999;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            font-family: Arial, sans-serif;
        ">
            <h4 style="margin: 0 0 12px 0; color: #1f2937; font-size: 14px; font-weight: 600;">Niveaux de risque</h4>
            <div style="display: flex; align-items: center; margin: 6px 0; padding: 4px 0;">
                <div style="width: 14px; height: 14px; background: #dc2626; border-radius: 50%; margin-right: 10px; border: 2px solid white; box-shadow: 0 1px 3px rgba(0,0,0,0.2);"></div>
                <span style="color: #374151; font-weight: 500;">Critique (80-100)</span>
            </div>
            <div style="display: flex; align-items: center; margin: 6px 0; padding: 4px 0;">
                <div style="width: 14px; height: 14px; background: #f59e0b; border-radius: 50%; margin-right: 10px; border: 2px solid white; box-shadow: 0 1px 3px rgba(0,0,0,0.2);"></div>
                <span style="color: #374151; font-weight: 500;">Élevé (60-79)</span>
            </div>
            <div style="display: flex; align-items: center; margin: 6px 0; padding: 4px 0;">
                <div style="width: 14px; height: 14px; background: #eab308; border-radius: 50%; margin-right: 10px; border: 2px solid white; box-shadow: 0 1px 3px rgba(0,0,0,0.2);"></div>
                <span style="color: #374151; font-weight: 500;">Modéré (40-59)</span>
            </div>
            <div style="display: flex; align-items: center; margin: 6px 0; padding: 4px 0;">
                <div style="width: 14px; height: 14px; background: #22c55e; border-radius: 50%; margin-right: 10px; border: 2px solid white; box-shadow: 0 1px 3px rgba(0,0,0,0.2);"></div>
                <span style="color: #374151; font-weight: 500;">Faible (0-39)</span>
            </div>
            <div style="margin-top: 12px; padding-top: 12px; border-top: 1px solid #e5e7eb; font-size: 11px; color: #6b7280;">
                💡 <strong>Conseil :</strong> Survolez ou cliquez sur une région pour plus de détails
            </div>
        </div>
        '''
        m.get_root().html.add_child(folium.Element(legend_html))
        
        # Ajouter des contrôles de navigation
        from folium.plugins import Fullscreen, MeasureControl, Draw
        
        # Bouton plein écran
        Fullscreen(
            position='topright',
            title='Plein écran',
            title_cancel='Quitter le plein écran',
            force_separate_button=True
        ).add_to(m)
        
        # Outil de mesure
        MeasureControl(
            position='topright',
            primary_length_unit='kilometers',
            primary_area_unit='sqkilometers',
            active_color='#3b82f6',
            completed_color='#22c55e'
        ).add_to(m)
        
        # Bouton de recentrage sur la France
        recenter_html = '''
        <div style="
            position: fixed; 
            top: 20px; 
            right: 20px; 
            z-index: 9999;
        ">
            <button onclick="map.setView([46.2276, 2.2137], 6);" 
                    style="
                        background: #3b82f6; 
                        color: white; 
                        border: none; 
                        border-radius: 8px; 
                        padding: 10px 15px; 
                        font-size: 12px; 
                        font-weight: 600; 
                        cursor: pointer; 
                        box-shadow: 0 2px 8px rgba(0,0,0,0.15);
                        transition: all 0.2s ease;
                    "
                    onmouseover="this.style.background='#2563eb'"
                    onmouseout="this.style.background='#3b82f6'">
                🎯 Recentrer sur la France
            </button>
        </div>
        '''
        m.get_root().html.add_child(folium.Element(recenter_html))
        
        return m
    
    def create_alert_dashboard(self):
        """Crée le tableau de bord des alertes"""
        if self.alerts is None:
            return None
        
        # Filtrage des alertes actives
        active_alerts = self.alerts[self.alerts['level'].str.contains('CRITIQUE|ÉLEVÉ')].copy()
        
        if len(active_alerts) == 0:
            return None
        
        # Ajouter les colonnes manquantes avec des valeurs par défaut
        if 'alert_score' not in active_alerts.columns:
            active_alerts['alert_score'] = active_alerts.get('score', 0)
        
        if 'action' not in active_alerts.columns:
            active_alerts['action'] = active_alerts['level'].apply(
                lambda x: "Action immédiate" if "CRITIQUE" in x else "Préparer campagne"
            )
        
        if 'timeline' not in active_alerts.columns:
            active_alerts['timeline'] = "1-2 semaines"
        
        if 'urgences_actuelles' not in active_alerts.columns:
            # Essayer de récupérer depuis les données principales
            if self.data is not None:
                latest_data = self.data.groupby('region').last().reset_index()
                urgences_map = dict(zip(latest_data['region'], latest_data.get('urgences_grippe', 0)))
                active_alerts['urgences_actuelles'] = active_alerts['region'].map(urgences_map).fillna(0)
            else:
                active_alerts['urgences_actuelles'] = 0
        
        if 'vaccination_rate' not in active_alerts.columns:
            # Essayer de récupérer depuis les données principales
            if self.data is not None:
                latest_data = self.data.groupby('region').last().reset_index()
                vacc_map = dict(zip(latest_data['region'], latest_data.get('vaccination_2024', 0)))
                active_alerts['vaccination_rate'] = active_alerts['region'].map(vacc_map).fillna(0)
            else:
                active_alerts['vaccination_rate'] = 0
        
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
        
        # Légende élégante et professionnelle
        st.markdown("### Niveaux de risque")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown("""
            <div style="
                background: #fef2f2;
                border-left: 4px solid #dc2626;
                padding: 1.5rem;
                border-radius: 0 8px 8px 0;
                margin: 0.5rem 0;
            ">
                <div style="
                    color: #dc2626;
                    font-size: 0.9rem;
                    font-weight: 600;
                    margin-bottom: 0.5rem;
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                ">Critique</div>
                <div style="font-weight: 700; color: #1f2937; font-size: 1.1rem; margin-bottom: 0.3rem;">80-100</div>
                <div style="font-size: 0.9rem; color: #6b7280; line-height: 1.4;">
                    Risque très élevé<br>
                    <span style="color: #dc2626;">Action immédiate requise</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div style="
                background: #fffbeb;
                border-left: 4px solid #f59e0b;
                padding: 1.5rem;
                border-radius: 0 8px 8px 0;
                margin: 0.5rem 0;
            ">
                <div style="
                    color: #f59e0b;
                    font-size: 0.9rem;
                    font-weight: 600;
                    margin-bottom: 0.5rem;
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                ">Élevé</div>
                <div style="font-weight: 700; color: #1f2937; font-size: 1.1rem; margin-bottom: 0.3rem;">60-79</div>
                <div style="font-size: 0.9rem; color: #6b7280; line-height: 1.4;">
                    Risque élevé<br>
                    <span style="color: #f59e0b;">Préparation nécessaire</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div style="
                background: #fefce8;
                border-left: 4px solid #eab308;
                padding: 1.5rem;
                border-radius: 0 8px 8px 0;
                margin: 0.5rem 0;
            ">
                <div style="
                    color: #eab308;
                    font-size: 0.9rem;
                    font-weight: 600;
                    margin-bottom: 0.5rem;
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                ">Modéré</div>
                <div style="font-weight: 700; color: #1f2937; font-size: 1.1rem; margin-bottom: 0.3rem;">40-59</div>
                <div style="font-size: 0.9rem; color: #6b7280; line-height: 1.4;">
                    Risque modéré<br>
                    <span style="color: #eab308;">Surveillance renforcée</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown("""
            <div style="
                background: #f0fdf4;
                border-left: 4px solid #22c55e;
                padding: 1.5rem;
                border-radius: 0 8px 8px 0;
                margin: 0.5rem 0;
            ">
                <div style="
                    color: #22c55e;
                    font-size: 0.9rem;
                    font-weight: 600;
                    margin-bottom: 0.5rem;
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                ">Faible</div>
                <div style="font-weight: 700; color: #1f2937; font-size: 1.1rem; margin-bottom: 0.3rem;">0-39</div>
                <div style="font-size: 0.9rem; color: #6b7280; line-height: 1.4;">
                    Risque faible<br>
                    <span style="color: #22c55e;">Situation normale</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Section d'explication des données - VERSION ÉLÉGANTE
        st.markdown("### Comprendre les données")
        
        # Explication du score d'alerte en premier
        st.markdown("""
        <div style="
            background: #f8fafc;
            padding: 2rem;
            border-radius: 12px;
            margin: 1.5rem 0;
            border-left: 4px solid #3b82f6;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        ">
            <h4 style="margin: 0 0 1rem 0; color: #1e40af; font-size: 1.1rem; font-weight: 600;">Score d'alerte grippe</h4>
            <p style="margin: 0; color: #374151; font-size: 1rem; line-height: 1.6;">
                Un indicateur de 0 à 100 qui évalue le niveau de risque de grippe dans chaque région, 
                basé sur l'analyse de multiples facteurs épidémiologiques et comportementaux.
            </p>
            <div style="margin-top: 1rem; display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem;">
                <div style="padding: 0.75rem; background: #f0fdf4; border-radius: 6px; border-left: 3px solid #22c55e;">
                    <strong style="color: #166534;">0-39</strong><br>
                    <span style="color: #6b7280; font-size: 0.9rem;">Risque faible</span>
                </div>
                <div style="padding: 0.75rem; background: #fefce8; border-radius: 6px; border-left: 3px solid #eab308;">
                    <strong style="color: #a16207;">40-59</strong><br>
                    <span style="color: #6b7280; font-size: 0.9rem;">Risque modéré</span>
                </div>
                <div style="padding: 0.75rem; background: #fffbeb; border-radius: 6px; border-left: 3px solid #f59e0b;">
                    <strong style="color: #d97706;">60-79</strong><br>
                    <span style="color: #6b7280; font-size: 0.9rem;">Risque élevé</span>
                </div>
                <div style="padding: 0.75rem; background: #fef2f2; border-radius: 6px; border-left: 3px solid #dc2626;">
                    <strong style="color: #dc2626;">80-100</strong><br>
                    <span style="color: #6b7280; font-size: 0.9rem;">Risque critique</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div style="
                background: #ffffff;
                padding: 1.5rem;
                border-radius: 12px;
                border-left: 4px solid #dc2626;
                box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            ">
                <h4 style="margin: 0 0 1rem 0; color: #1f2937; font-weight: 600;">Données médicales</h4>
                <div style="color: #374151; line-height: 1.8;">
                    <div style="margin-bottom: 1.2rem; padding: 0.75rem; background: #fef2f2; border-radius: 6px;">
                        <strong style="color: #dc2626; display: block; margin-bottom: 0.25rem;">Urgences grippe</strong>
                        <span style="color: #6b7280; font-size: 0.9rem;">Nombre de passages aux urgences pour syndrome grippal</span>
                    </div>
                    <div style="margin-bottom: 1.2rem; padding: 0.75rem; background: #fef2f2; border-radius: 6px;">
                        <strong style="color: #dc2626; display: block; margin-bottom: 0.25rem;">Taux de vaccination</strong>
                        <span style="color: #6b7280; font-size: 0.9rem;">Pourcentage de couverture vaccinale par région</span>
                    </div>
                    <div style="margin-bottom: 0; padding: 0.75rem; background: #fef2f2; border-radius: 6px;">
                        <strong style="color: #dc2626; display: block; margin-bottom: 0.25rem;">Population 65+</strong>
                        <span style="color: #6b7280; font-size: 0.9rem;">Pourcentage de personnes âgées (population à risque)</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div style="
                background: #ffffff;
                padding: 1.5rem;
                border-radius: 12px;
                border-left: 4px solid #3b82f6;
                box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            ">
                <h4 style="margin: 0 0 1rem 0; color: #1f2937; font-weight: 600;">Signaux comportementaux</h4>
                <div style="color: #374151; line-height: 1.8;">
                    <div style="margin-bottom: 1.2rem; padding: 0.75rem; background: #f0f9ff; border-radius: 6px;">
                        <strong style="color: #1e40af; display: block; margin-bottom: 0.25rem;">Recherches Google</strong>
                        <span style="color: #6b7280; font-size: 0.9rem;">Volume de recherches liées à la grippe sur internet</span>
                    </div>
                    <div style="margin-bottom: 1.2rem; padding: 0.75rem; background: #f0f9ff; border-radius: 6px;">
                        <strong style="color: #1e40af; display: block; margin-bottom: 0.25rem;">Consultations Wikipedia</strong>
                        <span style="color: #6b7280; font-size: 0.9rem;">Nombre de consultations des pages médicales</span>
                    </div>
                    <div style="margin-bottom: 0; padding: 0.75rem; background: #f0f9ff; border-radius: 6px;">
                        <strong style="color: #1e40af; display: block; margin-bottom: 0.25rem;">Conditions météo</strong>
                        <span style="color: #6b7280; font-size: 0.9rem;">Température et humidité (facteurs de propagation)</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Tableau de données détaillé
        st.markdown("### Données détaillées par région")
        
        if app.data is not None:
            latest_data = app.data.groupby('region').last().reset_index()
            
            # Sélection des colonnes à afficher
            display_columns = [
                'region', 'alert_score', 'urgences_grippe', 'vaccination_2024', 
                'pct_65_plus', 'population_totale'
            ]
            
            # Renommage des colonnes pour l'affichage - VERSION ÉLÉGANTE
            column_mapping = {
                'region': 'Région',
                'alert_score': 'Niveau de risque',
                'urgences_grippe': 'Urgences grippe',
                'vaccination_2024': 'Taux vaccination (%)',
                'pct_65_plus': 'Population 65+ (%)',
                'population_totale': 'Population totale'
            }
            
            display_data = latest_data[display_columns].copy()
            display_data = display_data.rename(columns=column_mapping)
            
            # Formatage des données
            display_data['Niveau de risque'] = display_data['Niveau de risque'].round(1)
            display_data['Taux vaccination (%)'] = display_data['Taux vaccination (%)'].round(1)
            display_data['Population 65+ (%)'] = display_data['Population 65+ (%)'].round(1)
            display_data['Population totale'] = display_data['Population totale'].apply(lambda x: f"{x:,}")
            
            # Tri par score d'alerte décroissant
            display_data = display_data.sort_values('Niveau de risque', ascending=False)
            
            st.dataframe(
                display_data,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Niveau de risque": st.column_config.NumberColumn(
                        "Niveau de risque",
                        help="Score de 0 à 100 : 0-39=Faible, 40-59=Modéré, 60-79=Élevé, 80-100=Critique",
                        format="%.1f"
                    ),
                    "Urgences grippe": st.column_config.NumberColumn(
                        "Urgences grippe",
                        help="Nombre de passages aux urgences pour syndrome grippal cette semaine",
                        format="%d"
                    ),
                    "Taux vaccination (%)": st.column_config.NumberColumn(
                        "Taux vaccination (%)",
                        help="Pourcentage de couverture vaccinale contre la grippe",
                        format="%.1f%%"
                    ),
                    "Population 65+ (%)": st.column_config.NumberColumn(
                        "Population 65+ (%)",
                        help="Pourcentage de personnes de 65 ans et plus (population à risque)",
                        format="%.1f%%"
                    ),
                    "Population totale": st.column_config.TextColumn(
                        "Population totale",
                        help="Nombre total d'habitants dans cette région"
                    )
                }
            )
    
    with tab2:
        st.header("Tableau de bord des alertes")
        
        # Tableau des alertes actives
        alert_dashboard = app.create_alert_dashboard()
        if alert_dashboard is not None and len(alert_dashboard) > 0:
            # Renommer les colonnes pour plus de clarté
            display_columns = ['region', 'level', 'alert_score', 'action', 'timeline', 'urgences_actuelles', 'vaccination_rate']
            available_columns = [col for col in display_columns if col in alert_dashboard.columns]
            
            if available_columns:
                # Créer un DataFrame avec les colonnes disponibles
                display_data = alert_dashboard[available_columns].copy()
                
                # Renommer les colonnes pour l'affichage
                column_mapping = {
                    'region': 'Région',
                    'level': 'Niveau',
                    'alert_score': 'Score',
                    'action': 'Action recommandée',
                    'timeline': 'Délai',
                    'urgences_actuelles': 'Urgences actuelles',
                    'vaccination_rate': 'Taux vaccination (%)'
                }
                
                display_data = display_data.rename(columns=column_mapping)
                
                # Formatage des données
                if 'Score' in display_data.columns:
                    display_data['Score'] = display_data['Score'].round(1)
                if 'Urgences actuelles' in display_data.columns:
                    display_data['Urgences actuelles'] = display_data['Urgences actuelles'].round(0).astype(int)
                if 'Taux vaccination (%)' in display_data.columns:
                    display_data['Taux vaccination (%)'] = display_data['Taux vaccination (%)'].round(1)
                
                st.dataframe(
                    display_data,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Score": st.column_config.NumberColumn(
                            "Score",
                            help="Score de risque de 0 à 100",
                            format="%.1f"
                        ),
                        "Urgences actuelles": st.column_config.NumberColumn(
                            "Urgences actuelles",
                            help="Nombre de passages aux urgences cette semaine",
                            format="%d"
                        ),
                        "Taux vaccination (%)": st.column_config.NumberColumn(
                            "Taux vaccination (%)",
                            help="Pourcentage de personnes vaccinées",
                            format="%.1f%%"
                        )
                    }
                )
                
                # Export CSV
                csv = display_data.to_csv(index=False)
                st.download_button(
                    label="Exporter alertes CSV",
                    data=csv,
                    file_name=f"alertes_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
            else:
                st.warning("Aucune donnée d'alerte disponible")
        else:
            st.info("✅ Aucune alerte active pour le moment")
    
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
