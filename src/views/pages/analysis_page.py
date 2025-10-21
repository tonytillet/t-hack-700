#!/usr/bin/env python3
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from utils.helpers import format_number, format_percentage

def render_analysis(app):
    st.header("Analyse détaillée par région")
    if app.data is None or len(app.data) == 0:
        st.info("Aucune donnée disponible")
        return
    regions = app.data['region'].unique()
    selected_region = st.selectbox("Sélectionnez une région :", regions)
    if not selected_region:
        return
    region_data = app.data[app.data['region'] == selected_region].copy()
    region_data = region_data.sort_values('date')

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        latest_score = region_data.get('alert_score', pd.Series([np.nan])).iloc[-1]
        st.metric("Niveau de risque", format_number(latest_score))
    with col2:
        urgences = region_data.get('urgences_grippe', pd.Series([0])).iloc[-1]
        st.metric("Urgences actuelles", format_number(urgences, 0))
    with col3:
        vaccination = region_data.get('vaccination_2024', pd.Series([np.nan])).iloc[-1]
        st.metric("Vaccination", format_percentage(vaccination))
    with col4:
        if 'pct_65_plus' in region_data.columns:
            population_65 = region_data['pct_65_plus'].iloc[-1]
            st.metric("Population 65+", format_percentage(population_65))
        else:
            st.metric("Population 65+ (est.)", "20.0%")

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=region_data['date'],
        y=region_data.get('urgences_grippe', pd.Series([0]*len(region_data))),
        name='Urgences grippe',
        line=dict(color='blue', width=2)
    ))
    if 'alert_score' in region_data.columns:
        fig.add_trace(go.Scatter(
            x=region_data['date'],
            y=region_data['alert_score'],
            name="Niveau de risque",
            line=dict(color='red', width=2),
            yaxis='y2'
        ))
    fig.update_layout(
        title=f"Évolution - {selected_region}",
        xaxis_title="Date",
        yaxis_title="Urgences grippe",
        yaxis2=dict(title="Niveau de risque", overlaying="y", side="right"),
        height=420,
        template='plotly_white',
        legend_title_text='' 
    )
    st.plotly_chart(fig, use_container_width=True)
