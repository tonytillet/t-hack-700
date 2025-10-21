#!/usr/bin/env python3
import streamlit as st

def render_assistant(app):
    st.header("Assistant IA LUMEN")
    user_question = st.text_input("Posez votre question sur la grippe ou LUMEN :")
    if user_question:
        chatbot = app.chatbot
        response = chatbot.get_response(user_question)
        st.markdown(response)
    st.markdown("### Questions fréquentes :")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🤒 Symptômes de la grippe"):
            st.markdown(app.chatbot.get_response("symptômes grippe"))
        if st.button("💉 Vaccination"):
            st.markdown(app.chatbot.get_response("vaccination"))
    with col2:
        if st.button("📊 Surveillance LUMEN"):
            st.markdown(app.chatbot.get_response("surveillance lumen"))
        if st.button("🎯 Objectifs LUMEN"):
            st.markdown(app.chatbot.get_response("lumen"))
