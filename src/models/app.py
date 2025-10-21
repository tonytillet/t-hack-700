#!/usr/bin/env python3
"""
Modèle principal de l'application Grippe Alert
Gère les données, les calculs et la logique métier
"""

import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta
import warnings
import folium
import json
warnings.filterwarnings('ignore')

from .chatbot import GrippeChatbot

class GrippeAlertApp:
    """Classe principale de l'application de surveillance grippale"""

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
            print("Aucune donnée avec alertes trouvée")
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
            def _safe_economies(val):
                try:
                    if isinstance(val, str):
                        d = json.loads(val)
                        return d.get('economies_estimees', 0)
                    if isinstance(val, dict):
                        return val.get('economies_estimees', 0)
                except Exception:
                    return 0
                return 0
            return self.protocols['expected_impact'].apply(_safe_economies).sum()
        return 0

    def create_alert_map(self):
        """Crée une carte interactive moderne des alertes (UX alignée legacy)"""
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
            tiles='CartoDB positron',
            attr='CartoDB',
            zoom_control=True,
            scroll_wheel_zoom=True,
            double_click_zoom=True,
            box_zoom=True,
            dragging=True,
            keyboard=True,
            zoom_control_position='topleft',
            min_zoom=5,
            max_zoom=10,
            prefer_canvas=True,
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
                radius = max(8, min(25, 8 + (population / 1_000_000) * 2))

                # Couleur gouvernementale
                if score >= 80:
                    color = '#ce0500'  # Rouge critique
                    fill_opacity = 0.8
                    niveau_risque = 'CRITIQUE'
                    action_requise = 'Action immédiate'
                elif score >= 60:
                    color = '#b34000'  # Orange élevé
                    fill_opacity = 0.7
                    niveau_risque = 'ÉLEVÉ'
                    action_requise = 'Se préparer'
                elif score >= 40:
                    color = '#6a6a6a'  # Gris modéré
                    fill_opacity = 0.6
                    niveau_risque = 'MODÉRÉ'
                    action_requise = 'Surveiller'
                else:
                    color = '#18753c'  # Vert faible
                    fill_opacity = 0.5
                    niveau_risque = 'FAIBLE'
                    action_requise = 'Tout va bien'

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

                folium.CircleMarker(
                    location=[lat, lon],
                    radius=radius,
                    popup=folium.Popup(popup_text, max_width=300, min_width=280, max_height=400, show=False, sticky=False),
                    color='white',
                    weight=3,
                    fillColor=color,
                    fillOpacity=fill_opacity,
                    tooltip=f"""
                    <div style=\"font-family: Arial, sans-serif; font-size: 14px;\">
                        <strong style=\"color: {color};\">{region}</strong><br>
                        <span style=\"color: #6b7280;\">Niveau: {niveau_risque}</span><br>
                        <span style=\"color: #6b7280;\">Score: {score:.0f}/100</span><br>
                        <span style=\"color: #6b7280; font-size: 12px;\">Cliquez pour plus de détails</span>
                    </div>
                    """,
                    interactive=True,
                    bubbling_mouse_events=False
                ).add_to(m)

        # Ajouter la légende moderne
        legend_html = f'''
        <div style="
            position: fixed; bottom: 20px; left: 20px; width: 220px;
            background: white; border: 1px solid #e5e7eb; border-radius: 12px; padding: 15px;
            font-size: 12px; z-index: 9999; box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            font-family: Arial, sans-serif;">
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
                <strong style="margin-right:6px;">Conseil :</strong> Survolez ou cliquez sur une région pour plus de détails
            </div>
        </div>
        '''
        m.get_root().html.add_child(folium.Element(legend_html))

        # Contrôles supplémentaires
        try:
            from folium.plugins import Fullscreen, MeasureControl
            Fullscreen(position='topright', title='Plein écran', title_cancel='Quitter').add_to(m)
            MeasureControl(position='topright', primary_length_unit='kilometers', primary_area_unit='sqkilometers').add_to(m)
        except Exception:
            pass

        # Bouton de recentrage
        recenter_html = '''
        <div style="position: absolute; top: 10px; right: 10px; z-index: 1000;">
            <button onclick="map.setView([46.2276, 2.2137], 6);" style="background: #3b82f6; color: white; border: none; border-radius: 6px; padding: 8px 12px; font-size: 11px; font-weight: 600; cursor: pointer; box-shadow: 0 2px 6px rgba(0,0,0,0.2);">Recentrer</button>
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

        # Colonnes attendues par l'affichage
        expected_cols = ['region', 'level', 'alert_score', 'action', 'timeline', 'urgences_actuelles', 'vaccination_rate']
        missing = [c for c in expected_cols if c not in active_alerts.columns]

        if missing:
            # Enrichissement depuis les dernières données disponibles
            if self.data is not None and len(self.data) > 0:
                latest = self.data.groupby('region').last().reset_index()
                # Urgences actuelles
                if 'urgences_actuelles' in missing and 'urgences_grippe' in latest.columns:
                    active_alerts = active_alerts.merge(
                        latest[['region', 'urgences_grippe']].rename(columns={'urgences_grippe': 'urgences_actuelles'}),
                        on='region', how='left'
                    )
                # Taux de vaccination
                if 'vaccination_rate' in missing and 'vaccination_2024' in latest.columns:
                    active_alerts = active_alerts.merge(
                        latest[['region', 'vaccination_2024']].rename(columns={'vaccination_2024': 'vaccination_rate'}),
                        on='region', how='left'
                    )

            # Valeurs par défaut basées sur le niveau
            if 'action' in missing:
                level_to_action = {
                    '🔴 CRITIQUE': "Déclencher protocole d'urgence immédiatement",
                    '🟠 ÉLEVÉ': "Préparer campagne de vaccination renforcée",
                }
                active_alerts['action'] = active_alerts.get('action', active_alerts['level'].map(level_to_action)).fillna("Surveillance renforcée")
            if 'timeline' in missing:
                level_to_timeline = {
                    '🔴 CRITIQUE': "1-2 semaines",
                    '🟠 ÉLEVÉ': "2-4 semaines",
                }
                active_alerts['timeline'] = active_alerts.get('timeline', active_alerts['level'].map(level_to_timeline)).fillna("1-2 mois")
            if 'alert_score' in missing and 'alert_score' not in active_alerts.columns:
                active_alerts['alert_score'] = np.nan
            if 'urgences_actuelles' in missing and 'urgences_actuelles' not in active_alerts.columns:
                active_alerts['urgences_actuelles'] = np.nan
            if 'vaccination_rate' in missing and 'vaccination_rate' not in active_alerts.columns:
                active_alerts['vaccination_rate'] = np.nan

        return active_alerts

    def create_protocol_dashboard(self):
        """Crée le tableau de bord des protocoles"""
        if self.protocols is None:
            return None

        return self.protocols
