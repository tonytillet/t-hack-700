#!/usr/bin/env python3
"""
Point d'entrée principal de l'application LUMEN
Application Streamlit refactorisée avec architecture modulaire
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
import base64
import warnings
warnings.filterwarnings('ignore')

# Import des modules personnalisés
from models.app import GrippeAlertApp
from models.chatbot import GrippeChatbot
from utils.helpers import (
    load_config, format_number, format_percentage, format_currency,
    get_latest_file, calculate_trend, validate_data_integrity
)
from config.settings import config
from views.pages import map_page, dashboard_page, protocols_page, analysis_page, assistant_page

# Configuration de la page
st.set_page_config(
    page_title=config.get('app.name'),
    page_icon="🚨",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    """Fonction principale de l'application"""
    st.markdown(
        """
        <style>
        :root {
            --primary:#1f77b4; /* bleu pro */
            --accent:#2ca02c;  /* vert validation */
            --warning:#ff7f0e; /* orange attention */
            --danger:#d62728;  /* rouge alerte */
            --muted:#6c757d;
        }
        .badge {padding:4px 8px;border-radius:12px;font-weight:600;}
        .badge-red {background:#fdecea;color:#b71c1c;border:1px solid #f5c6cb;}
        .badge-orange {background:#fff4e6;color:#7f3e00;border:1px solid #ffd8a8;}
        .badge-yellow {background:#fff9db;color:#7a6c00;border:1px solid #ffe066;}
        .badge-green {background:#e6f4ea;color:#1b5e20;border:1px solid #b7e1cd;}
        </style>
        """,
        unsafe_allow_html=True,
    )

    
    # Header avec logo institutionnel
    logo_b64 = ""
    try:
        with open("assets/logo_msp.png", "rb") as f:
            logo_b64 = base64.b64encode(f.read()).decode()
    except Exception:
        logo_b64 = ""

    st.markdown(f"""
    <div style="display: flex; align-items: center; gap: 16px; margin-bottom: 1.5rem; padding: 1rem; background: #ffffff; border-radius: 8px; border: 1px solid #e1e5e9; box-shadow: 0 2px 8px rgba(0,0,0,0.06);">
        <div style=\"margin-right: 8px;\">{'<img src="data:image/png;base64,'+logo_b64+'" alt="Logo" style="height: 56px; width: auto;">' if logo_b64 else ''}</div>
        <div>
            <h1 style="color: #2c3e50; margin: 0; font-size: 1.9rem; font-weight: 700; letter-spacing: -0.5px;">{config.get('app.name')}</h1>
            <p style="color: #6a6a6a; margin: 2px 0 0 0; font-size: 0.95rem;">{config.get('app.description')}</p>
            <p style="color: #9aa0a6; margin: 2px 0 0 0; font-size: 0.85rem;">Version {config.get('app.version')}</p>
        </div>
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

    # Création des onglets
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🗺️ Carte des alertes",
        "📊 Tableau de bord",
        "📋 Protocoles d'action",
        "🔍 Analyse détaillée",
        "🤖 Assistant IA"
    ])

    # Contenu des onglets
    with tab1:
        map_page.render_map(app)

    with tab2:
        dashboard_page.render_dashboard(app)

    with tab3:
        protocols_page.render_protocols(app)

    with tab4:
        analysis_page.render_analysis(app)

    

    with tab5:
        assistant_page.render_assistant(app)

if __name__ == "__main__":
    main()
