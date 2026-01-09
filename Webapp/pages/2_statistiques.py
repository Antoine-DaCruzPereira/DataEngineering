import streamlit as st
import pandas as pd
from pymongo import MongoClient
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="Statistiques", page_icon="📊", layout="wide")

@st.cache_resource
def get_mongo_client():
    try:
        client = MongoClient("mongodb://localhost:27017/")
        return client
    except Exception as e:
        st.error(f"❌ Impossible de se connecter à MongoDB: {e}")
        return None

def get_voitures():
    """Récupère toutes les voitures de la base de données"""
    try:
        client = get_mongo_client()
        if client is None:
            return pd.DataFrame()
        
        db = client["auto_data"]
        collection = db["paruvendu"]
        
        documents = list(collection.find())
        
        if not documents:
            return pd.DataFrame()
        
        df = pd.DataFrame(documents)
        
        if "_id" in df.columns:
            df = df.drop("_id", axis=1)
        
        return df
    
    except Exception as e:
        st.error(f"❌ Erreur lors de la récupération des données: {e}")
        return pd.DataFrame()

st.title("Statistiques")
st.markdown("---")

df = get_voitures()

if df.empty:
    st.warning("Aucune donnée disponible")
else:
    tab1, = st.tabs(["Vue d'ensemble"])
    
    with tab1:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total annonces", len(df))
        
        with col2:
            if "prix" in df.columns:
                st.metric("Prix moyen", f"{df['prix'].mean():.0f} €")
        
        with col3:
            if "annee" in df.columns:
                st.metric("Année moyenne", f"{df['annee'].mean():.0f}")
        
        with col4:
            if "km" in df.columns:
                st.metric("Kilométrage moyen", f"{df['km'].mean():.0f} km")
        
        st.markdown("---")
        
        graph_col1, graph_col2 = st.columns(2)
        
        with graph_col1:
            if "prix" in df.columns:
                st.subheader("Distribution des prix")
                fig, ax = plt.subplots(figsize=(10, 6))
                ax.hist(df["prix"].dropna(), bins=30, edgecolor='black', color='skyblue')
                ax.set_xlabel("Prix (€)")
                ax.set_ylabel("Nombre de voitures")
                ax.grid(axis='y', alpha=0.3)
                st.pyplot(fig)
        
        with graph_col2:
            if "marque" in df.columns:
                st.subheader("Top 10 des marques")
                marques_count = df["marque"].value_counts().head(10)
                fig, ax = plt.subplots(figsize=(10, 6))
                marques_count.plot(kind='barh', ax=ax, color='lightcoral')
                ax.set_xlabel("Nombre d'annonces")
                ax.grid(axis='x', alpha=0.3)
                st.pyplot(fig)
