#!/usr/bin/env python3
import streamlit as st
import pandas as pd
from utils.helpers import format_number, format_percentage

def _metric_card(title: str, value: str, subtitle: str, color: str, icon: str):
    st.markdown(
        f"""
        <div style="background:#ffffff;border:1px solid #e2e8f0;border-left:4px solid {color};
                    border-radius:10px;padding:16px;">
            <div style="display:flex;align-items:center;gap:10px;margin-bottom:8px;">
                <span style="font-size:18px;line-height:1">{icon}</span>
                <span style="font-weight:700;color:#0f172a;">{title}</span>
            </div>
            <div style="font-size:24px;font-weight:800;color:#111827;">{value}</div>
            <div style="font-size:12px;color:#475569;margin-top:4px;">{subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_context_section(app):
    """Rendu de la section Données contextuelles"""
    st.subheader("Données contextuelles")
    if app.data is None or len(app.data) == 0:
        st.info("Aucune donnée disponible")
        return
    latest = app.data.groupby('region').last().reset_index()
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        total_pop = latest.get('population_totale', pd.Series([0])).sum() if 'population_totale' in latest.columns else 0
        _metric_card("Population totale", format_number(total_pop, 0), "Somme sur toutes les régions", "#0ea5e9", "👥")
    with c2:
        pct65 = latest.get('pct_65_plus', pd.Series([0])).mean() if 'pct_65_plus' in latest.columns else 0
        _metric_card("Population 65+ (moy.)", format_percentage(pct65), "Proportion moyenne", "#6366f1", "👵")
    with c3:
        dens = (total_pop / max(len(latest), 1)) if total_pop else 0
        _metric_card("Densité démographique", f"{format_number(dens,0)} hab/région", "Moyenne par région", "#10b981", "🏙️")
    with c4:
        vuln = latest.get('pct_65_plus', pd.Series([0])).mean() * 0.43 if 'pct_65_plus' in latest.columns else 0
        _metric_card("Indice vulnérabilité", format_percentage(vuln), "Indice composite", "#f59e0b", "🛡️")


def render_economic_section(app):
    """Rendu de la section Données économiques"""
    st.subheader("Données économiques")
    if app.data is None or len(app.data) == 0:
        st.info("Aucune donnée disponible")
        return
    latest = app.data.groupby('region').last().reset_index()
    e1, e2, e3, e4 = st.columns(4)
    total_pop = (latest.get('population_totale', pd.Series([0])).sum()) if 'population_totale' in latest.columns else 0
    taux_vacc = (latest.get('vaccination_2024', pd.Series([50])).mean() / 100) if 'vaccination_2024' in latest.columns else 0.5
    cas_evitables = total_pop * (1 - taux_vacc) * 0.10
    cout_cas = 150
    cout_nv = cas_evitables * cout_cas / 1_000_000
    with e1:
        _metric_card("Coût non-vaccination", f"{cout_nv:.1f} M€", "Estimation macro", "#ef4444", "💸")
    with e2:
        cout_ss = cout_nv * 0.75
        _metric_card("Coût Sécurité sociale", f"{cout_ss:.1f} M€", "Part remboursée", "#3b82f6", "🏥")
    with e3:
        cout_prev = cout_nv * 0.235
        _metric_card("Coût prévention", f"{cout_prev:.1f} M€", "Investissement estimé", "#f59e0b", "🧰")
    with e4:
        roi = (cout_nv / max(cout_prev, 1e-6)) * 100
        _metric_card("ROI prévention", f"{roi:.0f}%", "Retour sur investissement", "#22c55e", "📈")


def render_derived_section(app):
    """Rendu de la section Données dérivées"""
    st.subheader("Données dérivées")
    if app.data is None or len(app.data) == 0:
        st.info("Aucune donnée disponible")
        return
    latest = app.data.groupby('region').last().reset_index()
    d1, d2, d3, d4 = st.columns(4)
    sc_values = []
    for _, row in latest.iterrows():
        r0 = max(0.8, min(2.0, row.get('urgences_grippe', 1) / max(row.get('urgences_grippe', 1), 1)))
        v = (row.get('vaccination_2024', 50) or 50) / 100
        d_norm = min(1.0, (row.get('population_totale', 100000) or 100000) / 10000000)
        sc_values.append(r0 * (1 - v) * d_norm)
    avg_sc = sum(sc_values) / len(sc_values) if sc_values else 0
    with d1:
        _metric_card("Seuil critique (SC)", f"{avg_sc:.2f}", "SC = R0 × (1-V) × D_norm", "#7c3aed", "🧭")
    r0_values = []
    for _, row in latest.iterrows():
        r0_values.append(max(0.8, min(2.0, row.get('urgences_grippe', 1) / max(row.get('urgences_grippe', 1), 1))))
    avg_r0 = sum(r0_values) / len(r0_values) if r0_values else 1.0
    with d2:
        _metric_card("Transmissibilité (R0)", f"{avg_r0:.2f}", "Force de propagation moyenne", "#2563eb", "🔗")
    gravite_vals = []
    for _, row in latest.iterrows():
        urg = row.get('urgences_grippe', 0) or 0
        cas = row.get('cas_sentinelles', 0) or 0
        gravite_vals.append((urg / max(cas, 1)) * 100)
    avg_grav = sum(gravite_vals) / len(gravite_vals) if gravite_vals else 0
    with d3:
        _metric_card("Taux de gravité", f"{avg_grav:.1f}%", "Hospitalisations / Cas × 100", "#f97316", "⚠️")
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
    with d4:
        _metric_card("LUMEN-Score", f"{avg_ls:.1f}/100", "Score composite de priorisation", "#16a34a", "📊")
