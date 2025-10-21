#!/usr/bin/env python3
import streamlit as st

def render_filters():
    """Filtres du dashboard: retourne (level_choice, data_type, period_choice)."""
    # Espace au-dessus des filtres pour séparer des KPIs
    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
    f1, f2, f3, f4 = st.columns([1,1,1,2])
    with f1:
        level_choice = st.selectbox("Niveau d'alerte", ['Tous', '🔴 Critique', '🟠 Élevé', '🟡 Modéré', '🟢 Faible'], key="dash_level")
    with f2:
        data_type = st.selectbox("Type de données", ['Toutes', 'Alertes', 'Urgences', 'Vaccination'], key="dash_dtype")
    with f3:
        period_choice = st.selectbox("Période", ['7 derniers jours', '14 derniers jours', '30 derniers jours', '90 derniers jours', 'Toute la période'], key="dash_period")
    with f4:
        st.checkbox("Actualisation automatique", value=False, key="dash_autorefresh")
    return level_choice, data_type, period_choice
