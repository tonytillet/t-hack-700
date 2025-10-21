#!/usr/bin/env python3
import streamlit as st
import json
from utils.helpers import format_currency

def render_protocols(app):
    st.header("Protocoles d'action automatiques")
    protocol_dashboard = app.create_protocol_dashboard()
    if protocol_dashboard is not None and len(protocol_dashboard) > 0:
        for _, protocol in protocol_dashboard.iterrows():
            with st.expander(f"{protocol['region']} - Priorité: {protocol.get('priority','N/A')}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Coût estimé", format_currency(protocol.get('estimated_cost')))
                    st.metric("Délai", protocol.get('timeline', 'N/A'))
                with col2:
                    impact = {}
                    try:
                        raw = protocol.get('expected_impact', '{}')
                        if isinstance(raw, str):
                            impact = json.loads(raw or '{}')
                        elif isinstance(raw, dict):
                            impact = raw
                    except Exception:
                        impact = {}
                    st.metric("Urgences évitées", f"{impact.get('urgences_evitees', 'N/A')}")
                    st.metric("Économies", format_currency(impact.get('economies_estimees')))
                    st.metric("ROI", f"{impact.get('roi_estime', 'N/A')}x")
                st.subheader("Actions à déclencher :")
                actions = []
                try:
                    raw_actions = protocol.get('actions', '[]')
                    if isinstance(raw_actions, str):
                        actions = json.loads(raw_actions or '[]')
                    elif isinstance(raw_actions, list):
                        actions = raw_actions
                except Exception:
                    actions = []
                for i, action in enumerate(actions, 1):
                    st.write(f"{i}. {action}")
                if st.button(f"Déclencher protocole - {protocol['region']}", key=f"protocol_{protocol['region']}"):
                    st.success(f"Protocole déclenché pour {protocol['region']} !")
                    st.info("Notifications envoyées et procédures lancées (simulation)")
    else:
        st.info("Aucun protocole actif actuellement")
