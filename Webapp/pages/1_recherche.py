import streamlit as st
import pandas as pd
from pymongo import MongoClient
import csv
import io
import os

# Connexion à MongoDB
@st.cache_resource
def get_mongo_client():
    try:
        mongo_uri = os.environ.get("MONGO_URI", "mongodb://localhost:27017/")
        
        print(f"🔌 Tentative de connexion à : {mongo_uri}")
        
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
        # Petit test de connexion ("ping") pour vérifier que ça marche tout de suite
        client.server_info()
        return client
    except Exception as e:
        st.error(f"❌ Impossible de se connecter à MongoDB ({mongo_uri}) : {e}")
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
        st.error(f"Erreur lors de la récupération des données: {e}")
        return pd.DataFrame()

st.set_page_config(page_title="Recherche", page_icon="🔍", layout="wide")

st.title("🔍 Recherche de Voitures")
st.markdown("---")

if "show_filters" not in st.session_state:
    st.session_state.show_filters = False
if "filters_applied" not in st.session_state:
    st.session_state.filters_applied = False
if "selected_brands" not in st.session_state:
    st.session_state.selected_brands = []
if "prix_range" not in st.session_state:
    st.session_state.prix_range = (0, 100000)
if "annee_range" not in st.session_state:
    st.session_state.annee_range = (1990, 2024)
if "selected_energy" not in st.session_state:
    st.session_state.selected_energy = []

df_original = get_voitures()

if df_original.empty:
    st.warning("Aucune voiture trouvée dans la base de données. Assurez-vous que MongoDB est en cours d'exécution et contient des données.")
else:
    st.metric("Nombre d'annonces", len(df_original))
    
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Export CSV", use_container_width=True):
            csv_data = df_original.to_csv(index=False)
            st.download_button(
                label="Télécharger CSV",
                data=csv_data,
                file_name="voitures.csv",
                mime="text/csv",
                use_container_width=True
            )
    
    with col2:
        if st.button("Filtrer", use_container_width=True):
            st.session_state.show_filters = True
    
    with col3:
        if st.button("Actualiser", use_container_width=True):
            st.rerun()
    
    st.markdown("---")
    
    if st.session_state.show_filters:
        # Utiliser des colonnes pour centrer le contenu
        col_left, col_center, col_right = st.columns([1, 2, 1])
        
        with col_center:
            # Container blanc avec les filtres
            with st.container(border=True):
                st.subheader("Filtres de Recherche")
                st.markdown("---")
                
                filter_col1, filter_col2 = st.columns(2)
                
                with filter_col1:
                    if "marque" in df_original.columns:
                        # Filtrer les marques qui ont au moins 2 annonces
                        marques_counts = df_original["marque"].value_counts()
                        marques_valides = marques_counts[marques_counts >= 2].index.tolist()
                        
                        st.session_state.selected_brands = st.multiselect(
                            "Sélectionnez une marque:",
                            marques_valides,
                            default=st.session_state.selected_brands,
                            key="filter_brands"
                        )
                    
                    if "prix" in df_original.columns:
                        prix_min_db = int(df_original["prix"].min()) if df_original["prix"].min() > 0 else 0
                        prix_max_db = int(df_original["prix"].max()) if df_original["prix"].max() > 0 else 100000
                        
                        st.write("Plage de prix:")
                        prix_col1, prix_col2 = st.columns(2)
                        
                        with prix_col1:
                            prix_min_manual = st.number_input(
                                "Prix minimum (€):",
                                min_value=prix_min_db,
                                max_value=prix_max_db,
                                value=st.session_state.prix_range[0],
                                key="prix_min_input"
                            )
                        
                        with prix_col2:
                            prix_max_manual = st.number_input(
                                "Prix maximum (€):",
                                min_value=prix_min_db,
                                max_value=prix_max_db,
                                value=st.session_state.prix_range[1],
                                key="prix_max_input"
                            )
                        
                        st.session_state.prix_range = st.slider(
                            "Ou utilisez le curseur:",
                            min_value=prix_min_db,
                            max_value=prix_max_db,
                            value=(prix_min_manual, prix_max_manual),
                            key="filter_prix"
                        )
                
                with filter_col2:
                    if "annee" in df_original.columns:
                        st.session_state.annee_range = st.slider(
                            "Sélectionnez une plage d'années:",
                            min_value=int(df_original["annee"].min()) if df_original["annee"].min() > 0 else 1990,
                            max_value=int(df_original["annee"].max()) if df_original["annee"].max() > 0 else 2024,
                            value=st.session_state.annee_range,
                            key="filter_annee"
                        )
                    
                    if "energie" in df_original.columns:
                        st.session_state.selected_energy = st.multiselect(
                            "Sélectionnez une énergie:",
                            df_original["energie"].unique(),
                            default=st.session_state.selected_energy,
                            key="filter_energie"
                        )
                
                st.markdown("---")
                
                button_col1, button_col2 = st.columns(2)
                
                with button_col1:
                    if st.button("Valider", use_container_width=True, key="validate_filters"):
                        st.session_state.show_filters = False
                        st.session_state.filters_applied = True
                        st.rerun()
                
                with button_col2:
                    if st.button("Annuler", use_container_width=True, key="cancel_filters"):
                        st.session_state.show_filters = False
                        st.session_state.selected_brands = []
                        st.session_state.prix_range = (0, 100000)
                        st.session_state.annee_range = (1990, 2024)
                        st.session_state.selected_energy = []
                        st.rerun()
    
    df = df_original.copy()
    
    if st.session_state.filters_applied:
        if st.session_state.selected_brands and "marque" in df.columns:
            df = df[df["marque"].isin(st.session_state.selected_brands)]
        
        if "prix" in df.columns:
            prix_min, prix_max = st.session_state.prix_range
            df = df[(df["prix"] >= prix_min) & (df["prix"] <= prix_max)]
        
        if "annee" in df.columns:
            annee_min, annee_max = st.session_state.annee_range
            df = df[(df["annee"] >= annee_min) & (df["annee"] <= annee_max)]
        
        if st.session_state.selected_energy and "energie" in df.columns:
            df = df[df["energie"].isin(st.session_state.selected_energy)]
    
    st.subheader(f"Résultats ({len(df)} voitures)")
    
    colonnes_a_afficher = []
    if "marque" in df.columns:
        colonnes_a_afficher.append("marque")
    if "titre" in df.columns:
        colonnes_a_afficher.append("titre")
    if "prix" in df.columns:
        colonnes_a_afficher.append("prix")
    if "annee" in df.columns:
        colonnes_a_afficher.append("annee")
    if "km" in df.columns:
        colonnes_a_afficher.append("km")
    if "energie" in df.columns:
        colonnes_a_afficher.append("energie")
    if "boite" in df.columns:
        colonnes_a_afficher.append("boite")
    if "lien" in df.columns:
        colonnes_a_afficher.append("lien")
    
    if colonnes_a_afficher:
        df_display = df[colonnes_a_afficher].copy()
        
        if "prix" in df_display.columns:
            df_display["prix"] = df_display["prix"].apply(
                lambda x: f'{x} €' if pd.notna(x) else "-"
            )
        
        if "lien" in df_display.columns:
            df_display["lien"] = df_display["lien"].apply(
                lambda x: f'<a href="{x}" target="_blank">Voir l\'annonce</a>' if pd.notna(x) and x else "-"
            )
        
        rename_dict = {
            "marque": "MARQUE",
            "titre": "VÉHICULE",
            "prix": "PRIX",
            "annee": "ANNÉE",
            "km": "KILOMÉTRAGE",
            "energie": "ÉNERGIE",
            "boite": "BOÎTE",
            "lien": "LIEN"
        }
        df_display = df_display.rename(columns=rename_dict)
        
        # Afficher avec HTML activé pour les liens
        st.markdown(df_display.to_html(escape=False), unsafe_allow_html=True)
    else:
        st.dataframe(df, use_container_width=True)
