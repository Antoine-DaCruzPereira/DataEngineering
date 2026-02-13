import streamlit as st
import os
import pymongo


st.set_page_config(
    page_title="Projet Scrapping",
    page_icon="🚗",
    layout="wide",
)

st.title("Projet Scrapping")
st.write("Dashboard de recherche et d'analyse des annonces automobiles")
st.markdown("---")

st.info("Utilisez le menu latéral pour naviguer vers les différentes pages de l'application.")

st.markdown("---")
st.markdown("<p style='text-align: center; color: gray;'>© 2025 Data Engineering - Projet Scrapping - DCP Antoine & Souprayen Soen</p>", 
            unsafe_allow_html=True)

