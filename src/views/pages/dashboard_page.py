#!/usr/bin/env python3
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
from utils.helpers import format_number, format_percentage, format_currency
from views.helpers.data_filters import apply_filters, regions_in_alert_count
from views.components.sections import (
    render_context_section,
    render_economic_section,
    render_derived_section,
)
from views.components.dashboard_kpis import render_kpis
from views.components.dashboard_filters import render_filters
from views.components.dashboard_alerts_table import render_alerts_table
from views.components.dashboard_indicators import render_advanced_indicators

def render_dashboard(app):
    st.header("Tableau de bord des indicateurs")
    # KPIs
    render_kpis(app)

    # Filtres et tableau d'alertes
    level_choice, data_type, period_choice = render_filters()
    render_alerts_table(app, level_choice, period_choice)

    # Indicateurs avancés
    render_advanced_indicators(app)

    render_context_section(app)

    render_economic_section(app)

    render_derived_section(app)

    st.subheader("Données comportementales")
    if app.data is not None and len(app.data) > 0:
        latest = app.data.groupby('region').last().reset_index()
        b1, b2, b3, b4 = st.columns(4)
        gt_avg = latest.get('google_trends_grippe', pd.Series([0])).mean() if 'google_trends_grippe' in latest.columns else 0
        wiki_avg = latest.get('wiki_grippe_views', pd.Series([0])).mean() if 'wiki_grippe_views' in latest.columns else 0
        worry_idx = latest.get('wiki_grippe_views_zscore', pd.Series([0])).mean() * 10 if 'wiki_grippe_views_zscore' in latest.columns else 0
        trend_dir = "🟢 Baisse" if (latest.get('wiki_grippe_views_zscore', pd.Series([0])).mean() or 0) < 0 else "🔴 Hausse"
        with b1:
            st.metric("Google Trends (moy.)", f"{gt_avg:.1f}")
        with b2:
            st.metric("Wikipedia views (moy.)", f"{wiki_avg:.0f}")
        with b3:
            st.metric("Indice d'inquiétude", f"{worry_idx:.1f}")
        with b4:
            st.metric("Tendance comportementale", trend_dir)

    st.subheader("Seuils d'action automatiques")
    cA, cB, cC = st.columns(3)
    with cA:
        st.success("SURVEILLANCE")
        st.caption("SC ≤ 0.4")
    with cB:
        st.error("ALERTE ROUGE")
        st.caption("LUMEN-Score ≥ 70")
    with cC:
        st.info("CAMPAGNE RENTABLE")
        st.caption("ROI ≥ 100%")
