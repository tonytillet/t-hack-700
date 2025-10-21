#!/usr/bin/env python3
import streamlit as st
import pandas as pd

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

    # SC (violet)
    sc_values = []
    for _, row in latest.iterrows():
        r0 = max(0.8, min(2.0, row.get('urgences_grippe', 1) / max(row.get('urgences_grippe', 1), 1)))
        v = (row.get('vaccination_2024', 50) or 50) / 100
        d_norm = min(1.0, (row.get('population_totale', 100000) or 100000) / 10000000)
        sc_values.append(r0 * (1 - v) * d_norm)
    avg_sc = sum(sc_values) / len(sc_values) if sc_values else 0
    with colA:
        _metric_card("Seuil critique (SC)", f"{avg_sc:.2f}", "SC = R0 × (1-V) × D_norm", "#7c3aed", "🧭")

    # R0 (bleu)
    r0_values = []
    for _, row in latest.iterrows():
        r0_values.append(max(0.8, min(2.0, row.get('urgences_grippe', 1) / max(row.get('urgences_grippe', 1), 1))))
    avg_r0 = sum(r0_values) / len(r0_values) if r0_values else 1.0
    with colB:
        _metric_card("Transmissibilité (R0)", f"{avg_r0:.2f}", "Force de propagation moyenne", "#2563eb", "🔗")

    # Gravité (orange)
    gravite_vals = []
    for _, row in latest.iterrows():
        urg = row.get('urgences_grippe', 0) or 0
        cas = row.get('cas_sentinelles', 0) or 0
        gravite_vals.append((urg / max(cas, 1)) * 100)
    avg_grav = sum(gravite_vals) / len(gravite_vals) if gravite_vals else 0
    with colC:
        _metric_card("Taux de gravité", f"{avg_grav:.1f}%", "Hospitalisations / Cas × 100", "#f97316", "⚠️")

    # LUMEN-Score (vert)
    lumen_vals = []
    for _, row in latest.iterrows():
        trends = row.get('google_trends_grippe', 0) or 0
        wiki = row.get('wiki_grippe_views', 0) or 0
        iae = (trends + wiki) / 100
        r0_norm = min(1.0, max(0.0, (avg_r0 - 0.8) / 1.2))
        v = (row.get('vaccination_2024', 50) or 50) / 100
        d_norm = min(1.0, (row.get('population_totale', 100000) or 100000) / 10000000)
        climat_norm = 0.5
        ls = (0.30 * iae + 0.25 * r0_norm + 0.20 * (1 - v) + 0.15 * d_norm + 0.10 * climat_norm) * 100
        lumen_vals.append(ls)
    avg_ls = sum(lumen_vals) / len(lumen_vals) if lumen_vals else 0
    with colD:
        _metric_card("LUMEN-Score", f"{avg_ls:.1f}/100", "Score composite de priorisation", "#16a34a", "📊")
