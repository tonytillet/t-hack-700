#!/usr/bin/env python3
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
from views.helpers.data_filters import apply_filters

def render_alerts_table(app, level_choice: str, period_choice: str):
    st.subheader("Alertes actives")
    alert_dashboard = app.create_alert_dashboard()
    if alert_dashboard is None or len(alert_dashboard) == 0:
        st.info("Aucune alerte active actuellement")
        return

    expected_cols = ['region', 'level', 'alert_score', 'action', 'timeline', 'urgences_actuelles', 'vaccination_rate']
    for col in expected_cols:
        if col not in alert_dashboard.columns:
            alert_dashboard[col] = np.nan

    level_map = {
        'critical': '🔴 Critique',
        'elevated': '🟠 Élevé',
        'moderate': '🟡 Modéré',
        'low': '🟢 Faible'
    }
    if 'level' in alert_dashboard.columns:
        alert_dashboard['level'] = alert_dashboard['level'].map(level_map).fillna(alert_dashboard['level'])

    filtered_data = apply_filters(app.data, level_choice, period_choice) if app.data is not None else None
    if filtered_data is not None and len(filtered_data) > 0:
        latest = filtered_data.groupby('region').last().reset_index()[['region','alert_score']]
        alert_dashboard = alert_dashboard.merge(latest, on='region', how='left', suffixes=('', '_flt'))
        alert_dashboard['alert_score'] = alert_dashboard['alert_score_flt'].fillna(alert_dashboard['alert_score'])
        alert_dashboard.drop(columns=[c for c in alert_dashboard.columns if c.endswith('_flt')], inplace=True)

    alert_dashboard = alert_dashboard.sort_values('alert_score', ascending=False)

    st.dataframe(
        alert_dashboard[expected_cols],
        use_container_width=True,
        hide_index=True
    )

    csv = alert_dashboard[expected_cols].to_csv(index=False)
    st.download_button(
        label="Exporter les alertes (CSV)",
        data=csv,
        file_name=f"alertes_grippe_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )
