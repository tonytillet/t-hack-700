#!/usr/bin/env python3
import streamlit as st
from utils.helpers import format_number, format_percentage
from views.helpers.data_filters import regions_in_alert_count

def _metric_card(title: str, value: str, subtitle: str, color: str, icon: str):
    st.markdown(
        f"""
        <div style=\"background:#ffffff;border:1px solid #e2e8f0;border-left:4px solid {color};
                    border-radius:10px;padding:16px;\"> 
            <div style=\"display:flex;align-items:center;gap:10px;margin-bottom:8px;\">
                <span style=\"font-size:18px;line-height:1\">{icon}</span>
                <span style=\"font-weight:700;color:#0f172a;\">{title}</span>
            </div>
            <div style=\"font-size:26px;font-weight:800;color:#111827;\">{value}</div>
            <div style=\"font-size:12px;color:#475569;margin-top:4px;\">{subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

def render_kpis(app):
    kpis = app.calculate_kpis()
    regions_alert = regions_in_alert_count(app.data, threshold=60.0)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        _metric_card("Urgences actuelles", format_number(kpis.get('urgences_actuelles', 0), 0), "Passages aux urgences", "#ef4444", "🏥")
    with col2:
        _metric_card("Vaccination moyenne", format_percentage(kpis.get('vaccination_moyenne', 0)), "Couverture vaccinale", "#2563eb", "💉")
    with col3:
        _metric_card("Alertes critiques", str(kpis.get('alertes_critiques', 0)), "Niveau ≥ critique", "#b91c1c", "🚨")
    with col4:
        _metric_card("Régions en alerte", f"{regions_alert}/13", "Score ≥ 60", "#7c3aed", "📍")
