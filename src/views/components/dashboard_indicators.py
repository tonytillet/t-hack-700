#!/usr/bin/env python3
import streamlit as st
import pandas as pd

# src/indicators/__init__.py
from indicators.rt import compute_rt_avg_from_data
from indicators.sc import compute_sc_avg_from_data
from indicators.severity import compute_severity_avg
from indicators.lumen_score import compute_lumen_score_avg


__all__ = [
    "compute_rt_avg_from_data",
    "compute_sc_avg_from_data",
    "compute_severity_avg",
    "compute_lumen_score_avg",
]


def _metric_card(title: str, value: str, subtitle: str, color: str, icon: str):
    st.markdown(
        f"""
        <div style="background:#ffffff;border:1px solid #e2e8f0;border-left:4px solid {color};
                    border-radius:10px;padding:16px;">
            <div style="display:flex;align-items:center;gap:10px;margin-bottom:8px;">
                <span style="font-size:20px;line-height:1">{icon}</span>
                <span style="font-weight:700;color:#0f172a;">{title}</span>
            </div>
            <div style="font-size:28px;font-weight:800;color:#111827;">{value}</div>
            <div style="font-size:12px;color:#475569;margin-top:4px;">{subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

def render_advanced_indicators(app):
    """Indicateurs avancés: SC, R0, Gravité, LUMEN-Score (cartes colorées)."""
    st.subheader("Indicateurs avancés")
    if app.data is None or len(app.data) == 0:
        return
    latest = app.data.groupby('region').last().reset_index()
    colA, colB, colC, colD = st.columns(4)

    # ── SC (violet)
    avg_sc = compute_rt_avg_from_data(app.data)
    with colA:
        _metric_card("Seuil critique (SC)", f"{avg_sc:.2f}", "SC = R0 × (1-V) × D_norm", "#7c3aed", "🧭")

    # ── R0 (bleu)
    avg_r0 = compute_sc_avg_from_data(app.data)
    with colB:
        _metric_card("Transmissibilité (R0)", f"{avg_r0:.2f}", "Force de propagation moyenne", "#2563eb", "🔗")

    # ── Gravité (orange)
    avg_grav = compute_severity_avg(latest)
    with colC:
        _metric_card("Taux de gravité", f"{avg_grav:.1f}%", "Hospitalisations / Cas × 100", "#f97316", "⚠️")

    # ── LUMEN-Score (vert)
    avg_ls = compute_lumen_score_avg(latest)
    with colD:
        _metric_card("LUMEN-Score", f"{avg_ls:.1f}/100", "Score composite de priorisation", "#16a34a", "📊")