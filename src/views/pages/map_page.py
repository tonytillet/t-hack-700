#!/usr/bin/env python3
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
from streamlit_folium import st_folium
from views.helpers.data_filters import apply_filters

def render_map(app):
    st.header("Carte des alertes")

    # Filtres
    f1, f2, f3, f4 = st.columns([1,1,1,2])
    with f1:
        level_choice = st.selectbox("Niveau d'alerte", ['Tous', '🔴 Critique', '🟠 Élevé', '🟡 Modéré', '🟢 Faible'], key="map_level")
    with f2:
        data_type = st.selectbox("Type de données", ['Toutes', 'Alertes', 'Urgences', 'Vaccination'], key="map_dtype")
    with f3:
        period_choice = st.selectbox("Période", ['7 derniers jours', '14 derniers jours', '30 derniers jours', '90 derniers jours', 'Toute la période'], key="map_period")
    with f4:
        st.checkbox("Actualisation automatique", value=False, key="map_autorefresh")

    # Récap filtres (compte régions)
    if app.data is not None and len(app.data) > 0:
        filtered = apply_filters(app.data, level_choice, period_choice)
        latest_regions = filtered.groupby('region').last().reset_index() if filtered is not None and len(filtered)>0 else pd.DataFrame()
        st.caption(f"{len(latest_regions)} régions affichées (filtres appliqués)")

    st.subheader("Visualisation géographique")

    alert_map = app.create_alert_map()
    if alert_map is not None:
        st_folium(alert_map, width=None, height=600)
    else:
        st.info("Aucune donnée cartographique disponible")
