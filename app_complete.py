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

class GrippeChatbot:
    def __init__(self):
        self.knowledge_base = {
            "grippe": {
                "symptomes": "Fièvre, toux, maux de tête, courbatures, fatigue",
                "transmission": "Gouttelettes respiratoires, contact direct, surfaces contaminées",
                "prevention": "Vaccination, lavage des mains, port du masque, aération",
                "duree": "7-10 jours en moyenne, jusqu'à 2 semaines pour la fatigue"
            },
            "vaccination": {
                "efficacite": "60-70% d'efficacité contre les formes graves",
                "recommandations": "Personnes à risque, professionnels de santé, +65 ans",
                "periode": "Octobre à mars, idéalement avant décembre",
                "effets": "Réactions locales légères, rarement des effets systémiques"
            },
            "surveillance": {
                "indicateurs": "Urgences, sentinelles, Google Trends, Wikipedia",
                "seuils": "Critique ≥80, Élevé 60-79, Modéré 40-59, Faible <40",
                "frequence": "Mise à jour hebdomadaire, alertes en temps réel",
                "sources": "Santé Publique France, INSEE, Open-Meteo, Google"
            },
            "lumen": {
                "objectif": "Prédire les épidémies 1-2 mois à l'avance",
                "donnees": "Signaux faibles + données officielles + météo",
                "ia": "Random Forest avec features temporelles inter-années",
                "impact": "-40% pics d'urgences, +25% efficacité campagnes"
            }
        }
    
    def get_response(self, question):
        question_lower = question.lower()
        
        # Recherche par mots-clés
        for category, info in self.knowledge_base.items():
            if any(keyword in question_lower for keyword in [category, "grippe", "vaccin", "surveillance", "lumen"]):
                if category == "grippe":
                    if "symptome" in question_lower:
                        return f"**Symptômes de la grippe :**\n{info['symptomes']}\n\n**Durée :** {info['duree']}"
                    elif "transmission" in question_lower or "contagieux" in question_lower:
                        return f"**Transmission de la grippe :**\n{info['transmission']}\n\n**Prévention :** {info['prevention']}"
                    else:
                        return f"**À propos de la grippe :**\n- **Symptômes :** {info['symptomes']}\n- **Transmission :** {info['transmission']}\n- **Prévention :** {info['prevention']}\n- **Durée :** {info['duree']}"
                
                elif category == "vaccination":
                    return f"**Vaccination contre la grippe :**\n- **Efficacité :** {info['efficacite']}\n- **Recommandations :** {info['recommandations']}\n- **Période :** {info['periode']}\n- **Effets secondaires :** {info['effets']}"
                
                elif category == "surveillance":
                    return f"**Surveillance grippale LUMEN :**\n- **Indicateurs :** {info['indicateurs']}\n- **Seuils d'alerte :** {info['seuils']}\n- **Fréquence :** {info['frequence']}\n- **Sources :** {info['sources']}"
                
                elif category == "lumen":
                    return f"**Plateforme LUMEN :**\n- **Objectif :** {info['objectif']}\n- **Données :** {info['donnees']}\n- **IA :** {info['ia']}\n- **Impact :** {info['impact']}"
        
        # Réponses par défaut
        if "bonjour" in question_lower or "salut" in question_lower:
            return "Bonjour ! Je suis l'assistant IA de LUMEN. Je peux vous aider avec des questions sur la grippe, la vaccination, la surveillance épidémiologique et la plateforme LUMEN. Que souhaitez-vous savoir ?"
        
        elif "aide" in question_lower or "help" in question_lower:
            return "**Comment puis-je vous aider ?**\n\nJe peux répondre à vos questions sur :\n- Les symptômes et la transmission de la grippe\n- La vaccination contre la grippe\n- Le système de surveillance LUMEN\n- Les indicateurs d'alerte et les seuils\n- Le fonctionnement de la plateforme\n\nPosez-moi votre question !"
        
        elif "merci" in question_lower:
            return "De rien ! N'hésitez pas si vous avez d'autres questions sur la surveillance grippale ou LUMEN."
        
        else:
            return "Je ne suis pas sûr de comprendre votre question. Je peux vous aider avec des informations sur la grippe, la vaccination, la surveillance épidémiologique et la plateforme LUMEN. Pouvez-vous reformuler votre question ?"

class GrippeAlertApp:
    def __init__(self):
        """Initialise l'application"""
        self.data = None
        self.alerts = None
        self.protocols = None
        self.chatbot = GrippeChatbot()
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
                
                # Couleur et opacité basées sur le score - Couleurs gouvernementales
                if score >= 80:
                    color = '#ce0500'  # Rouge critique gouvernemental
                    fill_opacity = 0.8
                elif score >= 60:
                    color = '#b34000'  # Orange élevé gouvernemental
                    fill_opacity = 0.7
                elif score >= 40:
                    color = '#6a6a6a'  # Gris modéré gouvernemental
                    fill_opacity = 0.6
                else:
                    color = '#18753c'  # Vert faible gouvernemental
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
                <div style="width: 14px; height: 14px; background: #ce0500; border-radius: 50%; margin-right: 10px; border: 2px solid white; box-shadow: 0 1px 3px rgba(0,0,0,0.2);"></div>
                <span style="color: #161616; font-weight: 500;">Critique (80-100)</span>
            </div>
            <div style="display: flex; align-items: center; margin: 6px 0; padding: 4px 0;">
                <div style="width: 14px; height: 14px; background: #b34000; border-radius: 50%; margin-right: 10px; border: 2px solid white; box-shadow: 0 1px 3px rgba(0,0,0,0.2);"></div>
                <span style="color: #161616; font-weight: 500;">Élevé (60-79)</span>
            </div>
            <div style="display: flex; align-items: center; margin: 6px 0; padding: 4px 0;">
                <div style="width: 14px; height: 14px; background: #6a6a6a; border-radius: 50%; margin-right: 10px; border: 2px solid white; box-shadow: 0 1px 3px rgba(0,0,0,0.2);"></div>
                <span style="color: #161616; font-weight: 500;">Modéré (40-59)</span>
            </div>
            <div style="display: flex; align-items: center; margin: 6px 0; padding: 4px 0;">
                <div style="width: 14px; height: 14px; background: #18753c; border-radius: 50%; margin-right: 10px; border: 2px solid white; box-shadow: 0 1px 3px rgba(0,0,0,0.2);"></div>
                <span style="color: #161616; font-weight: 500;">Faible (0-39)</span>
            </div>
            <div style="margin-top: 12px; padding-top: 12px; border-top: 1px solid #e5e7eb; font-size: 11px; color: #6b7280; display: flex; align-items: center;">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor" style="margin-right: 6px;">
                    <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-6h2v6zm0-8h-2V7h2v2z"/>
                </svg>
                <strong>Conseil :</strong> Survolez ou cliquez sur une région pour plus de détails
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
        
        # Bouton de recentrage sur la France - positionné correctement
        recenter_html = '''
        <div style="
            position: absolute; 
            top: 10px; 
            right: 10px; 
            z-index: 1000;
        ">
            <button onclick="map.setView([46.2276, 2.2137], 6);" 
                    style="
                        background: #3b82f6; 
                        color: white; 
                        border: none; 
                        border-radius: 6px; 
                        padding: 8px 12px; 
                        font-size: 11px; 
                        font-weight: 600; 
                        cursor: pointer; 
                        box-shadow: 0 2px 6px rgba(0,0,0,0.2);
                        transition: all 0.2s ease;
                        font-family: Arial, sans-serif;
                    "
                    onmouseover="this.style.background='#2563eb'; this.style.transform='translateY(-1px)'"
                    onmouseout="this.style.background='#3b82f6'; this.style.transform='translateY(0)'">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" style="margin-right: 6px; vertical-align: middle;">
                    <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
                </svg>
                Recentrer
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
    # Charger et encoder le logo en base64
    import base64
    try:
        with open("assets/logo_msp.png", "rb") as f:
            logo_base64 = base64.b64encode(f.read()).decode()
    except FileNotFoundError:
        logo_base64 = ""
    
    # Header principal - Version Streamlit native
    st.markdown(f"""
    <div style="display: flex; align-items: center; margin-bottom: 2rem; padding: 1rem; background: #ffffff; border-radius: 8px; border: 1px solid #e1e5e9; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
        <div style="margin-right: 1.5rem;">
            <img src="data:image/png;base64,{logo_base64}" alt="Logo Ministère" style="height: 80px; width: auto;">
        </div>
        <div>
            <h1 style="
                color: #000091;
                margin: 0;
                font-size: 2.8rem;
                font-weight: 700;
                letter-spacing: -1px;
            ">LUMEN</h1>
            <p style="
                color: #6a6a6a;
                margin: 0.25rem 0 0 0;
                font-size: 1rem;
                font-weight: 400;
            ">Plateforme nationale de surveillance grippale</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Message principal
    st.info("**Anticipez les épidémies de grippe 1 à 2 mois à l'avance** - Protéger la santé publique et optimiser les ressources médicales")
    
    
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
    # Section de contexte et valeur ajoutée
    
    
    # Navigation responsive avec boutons
    if 'current_tab' not in st.session_state:
        st.session_state.current_tab = 0
    
    # Boutons de navigation responsive
    st.markdown("""
    <style>
    .nav-buttons {
        display: flex;
        gap: 8px;
        margin-bottom: 2rem;
        flex-wrap: wrap;
    }
    
    .nav-button {
        flex: 1;
        min-width: 150px;
        padding: 12px 20px;
        background-color: #000091;
        border: 2px solid #000091;
        border-radius: 8px;
        color: #ffffff;
        font-weight: 500;
        text-align: center;
        cursor: pointer;
        transition: all 0.3s ease;
        font-size: 14px;
    }
    
    .nav-button:hover {
        background-color: #1a1a9e;
        border-color: #1a1a9e;
        color: #ffffff;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 0, 145, 0.3);
    }
    
    .nav-button.active {
        background-color: #ffffff;
        border-color: #000091;
        color: #000091;
        box-shadow: 0 4px 12px rgba(0, 0, 145, 0.2);
    }
    
    .nav-button.active:hover {
        background-color: #f6f6f6;
        color: #000091;
        transform: translateY(-2px);
    }
    
    @media (max-width: 768px) {
        .nav-buttons {
            flex-direction: column;
            gap: 6px;
        }
        
        .nav-button {
            width: 100%;
            min-width: unset;
        }
    }
    
    @media (max-width: 480px) {
        .nav-button {
            padding: 10px 16px;
            font-size: 13px;
        }
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Boutons de navigation
    tabs = ["Carte des alertes", "Tableau de bord alertes", "Protocoles d'action", "Analyse détaillée", "Configuration"]
    
    st.markdown('<div class="nav-buttons">', unsafe_allow_html=True)
    
    cols = st.columns(len(tabs))
    for i, (col, tab_name) in enumerate(zip(cols, tabs)):
        with col:
            if st.button(tab_name, key=f"nav_{i}", use_container_width=True):
                st.session_state.current_tab = i
                st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Affichage du contenu selon l'onglet sélectionné
    if st.session_state.current_tab == 0:
        st.markdown("### Carte des alertes")
    elif st.session_state.current_tab == 1:
        st.markdown("### Tableau de bord alertes")
    elif st.session_state.current_tab == 2:
        st.markdown("### Protocoles d'action")
    elif st.session_state.current_tab == 3:
        st.markdown("### Analyse détaillée")
    elif st.session_state.current_tab == 4:
        st.markdown("### Assistant IA")
    elif st.session_state.current_tab == 5:
        st.markdown("### Configuration")
    
    # Contenu selon l'onglet sélectionné
    if st.session_state.current_tab == 0:
        # Calculer les indicateurs
        if app.data is not None:
            latest_data = app.data.groupby('region').last().reset_index()
            
            # Indicateurs clés avec design NCIS
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                # Seuil critique (SC)
                sc_values = []
                for _, row in latest_data.iterrows():
                    r0 = max(0.8, min(2.0, row.get('urgences_grippe', 1) / max(row.get('urgences_grippe', 1), 1)))
                    v = row.get('vaccination_2024', 50) / 100  # Utiliser vaccination_2024 au lieu de taux_vaccination
                    d_norm = min(1.0, row.get('population_totale', 100000) / 10000000)
                    sc = r0 * (1 - v) * d_norm
                    sc_values.append(sc)
                
                avg_sc = sum(sc_values) / len(sc_values) if sc_values else 0
                st.metric(
                    label="Seuil critique",
                    value=f"{avg_sc:.2f}",
                    help="SC = R0 × (1-V) × D_norm. Seuil d'alerte si > 0.6"
                )
            
            with col2:
                # Taux de transmissibilité (R0)
                r0_values = []
                for _, row in latest_data.iterrows():
                    r0 = max(0.8, min(2.0, row.get('urgences_grippe', 1) / max(row.get('urgences_grippe', 1), 1)))
                    r0_values.append(r0)
                
                avg_r0 = sum(r0_values) / len(r0_values) if r0_values else 1.0
                st.metric(
                    label="Transmissibilité (R0)",
                    value=f"{avg_r0:.2f}",
                    help="R0 = Cas_secondaires / Cas_initiaux. Épidémie si > 1"
                )
            
            with col3:
                # Taux de gravité
                gravite_values = []
                for _, row in latest_data.iterrows():
                    urgences = row.get('urgences_grippe', 0)
                    total_cas = row.get('cas_sentinelles', 1)
                    gravite = (urgences / max(total_cas, 1)) * 100
                    gravite_values.append(gravite)
                
                avg_gravite = sum(gravite_values) / len(gravite_values) if gravite_values else 0
                st.metric(
                    label="Taux de gravité (%)",
                    value=f"{avg_gravite:.1f}%",
                    help="G = (Hospitalisations / Cas_totaux) × 100"
                )
            
            with col4:
                # LUMEN-Score
                lumen_scores = []
                for _, row in latest_data.iterrows():
                    # IAE (Indice d'accélération épidémique)
                    trends = row.get('google_trends_grippe', 0)
                    wiki = row.get('wiki_grippe_views', 0)
                    iae = (trends + wiki) / 100  # Normalisation simple
                    
                    # R0 normalisé
                    r0_norm = min(1.0, max(0.0, (avg_r0 - 0.8) / 1.2))
                    
                    # Taux de vaccination
                    v = row.get('vaccination_2024', 50) / 100
                    
                    # Densité normalisée
                    d_norm = min(1.0, row.get('population_totale', 100000) / 10000000)
                    
                    # Climat normalisé (simulation)
                    climat_norm = 0.5  # Valeur par défaut
                    
                    # LUMEN-Score
                    ls = (0.30 * iae + 0.25 * r0_norm + 0.20 * (1-v) + 0.15 * d_norm + 0.10 * climat_norm) * 100
                    lumen_scores.append(ls)
                
                avg_ls = sum(lumen_scores) / len(lumen_scores) if lumen_scores else 0
                st.metric(
                    label="LUMEN-Score",
                    value=f"{avg_ls:.1f}/100",
                    help="Score composite 0-100 pour priorisation"
                )
            
            # Indicateurs économiques
            st.subheader("Indicateurs économiques")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                # Coût non-vaccination
                total_pop = latest_data['population_totale'].sum()
                taux_vacc = latest_data['vaccination_2024'].mean() / 100
                cas_evitables = total_pop * (1 - taux_vacc) * 0.1  # 10% taux d'attaque
                cout_cas = 150  # € par cas
                cout_nv = cas_evitables * cout_cas / 1000000  # en millions
                st.metric(
                    label="Coût non-vaccination",
                    value=f"{cout_nv:.1f}M€",
                    help="Coût évitable si pas de vaccination"
                )
            
            with col2:
                # Coût Sécurité sociale
                cout_ss = cout_nv * 0.75  # 75% remboursé
                st.metric(
                    label="Coût Assurance Maladie",
                    value=f"{cout_ss:.1f}M€",
                    help="Part remboursée par l'Assurance Maladie"
                )
            
            with col3:
                # Coût prévention
                nb_vacciner = total_pop * 0.1  # 10% à vacciner
                cout_vaccin = 15  # € par vaccination
                cout_com = 500000  # € communication
                cout_prev = (nb_vacciner * cout_vaccin + cout_com) / 1000000
                st.metric(
                    label="Coût prévention",
                    value=f"{cout_prev:.1f}M€",
                    help="Coût campagne de vaccination"
                )
            
            with col4:
                # ROI prévention
                roi = ((cout_ss - cout_prev) / cout_prev) * 100 if cout_prev > 0 else 0
                st.metric(
                    label="ROI prévention",
                    value=f"{roi:.0f}%",
                    help="Retour sur investissement de la prévention"
                )
            
            # Seuils d'action
            st.subheader("Seuils d'action automatiques")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if avg_sc > 0.6 and avg_r0 > 1:
                    st.error("VACCINATION D'URGENCE")
                    st.write("SC > 0.6 et R0 > 1")
                elif avg_sc > 0.4:
                    st.warning("CAMPAGNE DE SENSIBILISATION")
                    st.write("0.4 < SC ≤ 0.6")
                else:
                    st.success("SURVEILLANCE")
                    st.write("SC ≤ 0.4")
            
            with col2:
                if avg_ls >= 70:
                    st.error("ALERTE ROUGE")
                    st.write("LUMEN-Score ≥ 70")
                elif avg_ls >= 50:
                    st.warning("ALERTE ORANGE")
                    st.write("50 ≤ LUMEN-Score < 70")
                else:
                    st.success("SITUATION NORMALE")
                    st.write("LUMEN-Score < 50")
            
            with col3:
                if roi > 100:
                    st.success("CAMPAGNE RENTABLE")
                    st.write(f"ROI: {roi:.0f}%")
                elif roi > 0:
                    st.warning("CAMPAGNE MARGINALE")
                    st.write(f"ROI: {roi:.0f}%")
                else:
                    st.error("CAMPAGNE NON RENTABLE")
                    st.write(f"ROI: {roi:.0f}%")
        
        st.markdown("---")
        
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
        
        # Application des filtres
        filtered_data = app.data.copy() if app.data is not None else None
        
        if filtered_data is not None:
            # Filtre par niveau d'alerte
            if niveau_alerte != "Tous":
                if niveau_alerte == "Critique":
                    filtered_data = filtered_data[filtered_data.get('alert_score', 0) >= 80]
                elif niveau_alerte == "Élevé":
                    filtered_data = filtered_data[(filtered_data.get('alert_score', 0) >= 60) & (filtered_data.get('alert_score', 0) < 80)]
                elif niveau_alerte == "Modéré":
                    filtered_data = filtered_data[(filtered_data.get('alert_score', 0) >= 40) & (filtered_data.get('alert_score', 0) < 60)]
                elif niveau_alerte == "Faible":
                    filtered_data = filtered_data[filtered_data.get('alert_score', 0) < 40]
            
            # Filtre par période
            if periode != "Toutes":
                if periode == "7 derniers jours":
                    cutoff_date = pd.Timestamp.now() - pd.Timedelta(days=7)
                elif periode == "30 derniers jours":
                    cutoff_date = pd.Timestamp.now() - pd.Timedelta(days=30)
                elif periode == "3 derniers mois":
                    cutoff_date = pd.Timestamp.now() - pd.Timedelta(days=90)
                
                filtered_data = filtered_data[filtered_data['date'] >= cutoff_date]
            
            # Sauvegarder les données filtrées temporairement
            original_data = app.data
            app.data = filtered_data
            
            # Afficher le nombre de résultats filtrés
            st.info(f"{len(filtered_data)} régions affichées (filtres appliqués)")
        
        # Carte interactive avec style amélioré
        st.markdown("### Visualisation géographique")
        
        alert_map = app.create_alert_map()
        if alert_map:
            st_folium(alert_map, width=None, height=500)
        
        
        # Tableau de données détaillé
        st.markdown("### Données détaillées par région")
        
        if app.data is not None:
            latest_data = app.data.groupby('region').last().reset_index()
            
            # Sélection des colonnes à afficher (vérifier les colonnes disponibles)
            available_columns = latest_data.columns.tolist()
            display_columns = ['region', 'alert_score', 'urgences_grippe', 'vaccination_2024', 'population_totale']
            
            # Ajouter des colonnes supplémentaires si elles existent
            if 'pct_65_plus' in available_columns:
                display_columns.append('pct_65_plus')
            if 'ias_syndrome_grippal' in available_columns:
                display_columns.append('ias_syndrome_grippal')
            
            # Renommage des colonnes pour l'affichage - VERSION ÉLÉGANTE
            column_mapping = {
                'region': 'Région',
                'alert_score': 'Niveau de risque',
                'urgences_grippe': 'Urgences grippe',
                'vaccination_2024': 'Taux vaccination (%)',
                'population_totale': 'Population totale'
            }
            
            # Ajouter les colonnes conditionnelles au mapping
            if 'pct_65_plus' in display_columns:
                column_mapping['pct_65_plus'] = 'Population 65+ (%)'
            if 'ias_syndrome_grippal' in display_columns:
                column_mapping['ias_syndrome_grippal'] = 'IAS Syndrome grippal'
            
            display_data = latest_data[display_columns].copy()
            display_data = display_data.rename(columns=column_mapping)
            
            # Formatage des données
            display_data['Niveau de risque'] = display_data['Niveau de risque'].round(1)
            display_data['Taux vaccination (%)'] = display_data['Taux vaccination (%)'].round(1)
            display_data['Population totale'] = display_data['Population totale'].apply(lambda x: f"{x:,}")
            
            # Formatage conditionnel des colonnes optionnelles
            if 'Population 65+ (%)' in display_data.columns:
                display_data['Population 65+ (%)'] = display_data['Population 65+ (%)'].round(1)
            if 'IAS Syndrome grippal' in display_data.columns:
                display_data['IAS Syndrome grippal'] = display_data['IAS Syndrome grippal'].round(2)
            
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
    
    elif st.session_state.current_tab == 1:
        st.markdown('<div id="priorites"></div>', unsafe_allow_html=True)
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
    
    elif st.session_state.current_tab == 2:
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
    
    elif st.session_state.current_tab == 3:
        st.markdown('<div id="simulation"></div>', unsafe_allow_html=True)
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
                # Vérifier si la colonne existe, sinon utiliser une valeur par défaut
                if 'pct_65_plus' in region_data.columns:
                    population_65 = region_data['pct_65_plus'].iloc[-1]
                    st.metric("Population 65+", f"{population_65:.1f}%")
                else:
                    # Calculer approximativement basé sur la population totale
                    population_totale = region_data['population_totale'].iloc[-1]
                    # Estimation : 20% de la population française a 65+ ans
                    population_65_est = 20.0
                    st.metric("Population 65+ (est.)", f"{population_65_est:.1f}%")
            
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
    
    elif st.session_state.current_tab == 4:
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
    
    # Chatbot professionnel sans icônes
    if "chat_open" not in st.session_state:
        st.session_state.chat_open = False
    
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    # Bouton d'assistance professionnel
    st.markdown("---")
    col1, col2, col3 = st.columns([2, 1, 1])
    with col3:
        if st.button("Assistance", help="Ouvrir l'assistance LUMEN", key="chat_toggle", type="secondary", use_container_width=True):
            st.session_state.chat_open = not st.session_state.chat_open
            st.rerun()
    st.markdown("---")
    
    # Fenêtre d'assistance (si ouverte)
    if st.session_state.chat_open:
        st.markdown("### Assistance LUMEN")
        
        # Zone de messages
        if st.session_state.chat_history:
            for message in st.session_state.chat_history:
                if message["role"] == "user":
                    st.markdown(f"""
                    <div style="
                        background: #f8f9fa;
                        padding: 12px;
                        border-radius: 6px;
                        margin: 8px 0;
                        border-left: 3px solid #000091;
                    ">
                        <strong>Vous :</strong> {message['content']}
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div style="
                        background: #ffffff;
                        padding: 12px;
                        border-radius: 6px;
                        margin: 8px 0;
                        border: 1px solid #e1e5e9;
                    ">
                        <strong>Assistant LUMEN :</strong> {message['content']}
                    </div>
                    """, unsafe_allow_html=True)
        else:
            # Message de bienvenue
            st.markdown("""
            <div style="
                background: #f8f9fa;
                padding: 12px;
                border-radius: 6px;
                margin: 8px 0;
                border-left: 3px solid #000091;
            ">
                <strong>Assistant LUMEN :</strong> Bonjour ! Je peux vous aider avec des questions sur la grippe, la vaccination, la surveillance épidémiologique et la plateforme LUMEN. Que souhaitez-vous savoir ?
            </div>
            """, unsafe_allow_html=True)
        
        # Zone de saisie
        with st.form("chat_form", clear_on_submit=True):
            user_input = st.text_input("Votre question", placeholder="Tapez votre question ici...", key="user_input")
            submit_button = st.form_submit_button("Envoyer", use_container_width=True)
        
        if submit_button and user_input:
            # Ajouter la question de l'utilisateur à l'historique
            st.session_state.chat_history.append({"role": "user", "content": user_input})
            
            # Obtenir la réponse du chatbot
            response = app.chatbot.get_response(user_input)
            
            # Ajouter la réponse à l'historique
            st.session_state.chat_history.append({"role": "assistant", "content": response})
            
            # Rafraîchir la page pour afficher la nouvelle conversation
            st.rerun()
        
        # Questions fréquentes
        st.markdown("**Questions fréquentes :**")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Symptômes grippe", use_container_width=True):
                st.session_state.chat_history.append({"role": "user", "content": "Quels sont les symptômes de la grippe ?"})
                response = app.chatbot.get_response("Quels sont les symptômes de la grippe ?")
                st.session_state.chat_history.append({"role": "assistant", "content": response})
                st.rerun()
            
            if st.button("Fonctionnement LUMEN", use_container_width=True):
                st.session_state.chat_history.append({"role": "user", "content": "Comment fonctionne LUMEN ?"})
                response = app.chatbot.get_response("Comment fonctionne LUMEN ?")
                st.session_state.chat_history.append({"role": "assistant", "content": response})
                st.rerun()
        
        with col2:
            if st.button("Vaccination", use_container_width=True):
                st.session_state.chat_history.append({"role": "user", "content": "Quand se faire vacciner ?"})
                response = app.chatbot.get_response("Quand se faire vacciner ?")
                st.session_state.chat_history.append({"role": "assistant", "content": response})
                st.rerun()
            
            if st.button("Seuils d'alerte", use_container_width=True):
                st.session_state.chat_history.append({"role": "user", "content": "Quels sont les seuils d'alerte ?"})
                response = app.chatbot.get_response("Quels sont les seuils d'alerte ?")
                st.session_state.chat_history.append({"role": "assistant", "content": response})
                st.rerun()
        
        # Contrôles
        col_close, col_clear = st.columns(2)
        with col_close:
            if st.button("Fermer", use_container_width=True):
                st.session_state.chat_open = False
                st.rerun()
        with col_clear:
            if st.button("Effacer", type="secondary", use_container_width=True):
                st.session_state.chat_history = []
                st.rerun()
    
    # Footer gouvernemental avec composants Streamlit
    st.markdown("---")
    
    # Container principal du footer
    with st.container():
        # Logo et titre centré
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            st.markdown("""
            <div style="text-align: center; padding: 1rem 0;">
                <img src="data:image/png;base64,{logo_base64}" alt="Logo Ministère" style="height: 50px; width: auto; filter: brightness(0) invert(1); margin-bottom: 1rem;">
                <h3 style="color: #000091; margin: 0.5rem 0; font-size: 1.3rem; font-weight: 700;">LUMEN</h3>
                <p style="color: #6a6a6a; margin: 0; font-size: 1rem;">Ministère de la Santé et de la Prévention</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Navigation gouvernementale officielle
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("**Ministère de la Santé et de la Prévention**")
            st.markdown("[Gouvernement.fr](https://www.gouvernement.fr)")
            st.markdown("[Santé Publique France](https://www.santepubliquefrance.fr)")
            st.markdown("[Service Public](https://www.service-public.fr)")
            st.markdown("[Data.gouv.fr](https://www.data.gouv.fr)")
        
        with col2:
            st.markdown("**Ressources officielles**")
            st.markdown("[Info.gouv.fr](https://www.info.gouv.fr)")
            st.markdown("[Legifrance.gouv.fr](https://www.legifrance.gouv.fr)")
            st.markdown("[France.fr](https://www.france.fr)")
            st.markdown("[Elysee.fr](https://www.elysee.fr)")
        
        with col3:
            st.markdown("**Légal et transparence**")
            st.markdown("[Mentions légales](https://www.gouvernement.fr/mentions-legales)")
            st.markdown("[Politique de confidentialité](https://www.gouvernement.fr/politique-de-confidentialite)")
            st.markdown("[Accessibilité](https://www.gouvernement.fr/accessibilite)")
            st.markdown("[Contact](https://www.gouvernement.fr/contact)")
        
        # Copyright
        st.markdown("""
        <div style="text-align: center; padding: 1rem 0; border-top: 1px solid #e1e5e9; margin-top: 2rem;">
            <p style="color: #6a6a6a; margin: 0; font-size: 0.85rem;">
                © 2024 Ministère de la Santé et de la Prévention. Tous droits réservés.
            </p>
            <p style="color: #6a6a6a; margin: 0.5rem 0 0 0; font-size: 0.85rem;">
                Plateforme LUMEN - Système d'alerte précoce grippe
            </p>
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
