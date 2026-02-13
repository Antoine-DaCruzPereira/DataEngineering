import streamlit as st
import pandas as pd
from pymongo import MongoClient
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

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

def flatten_caracteristiques(df):
    if 'caracteristiques' in df.columns:
        carac_df = pd.json_normalize(df['caracteristiques'])
        for col in carac_df.columns:
            if col not in df.columns:
                df[col] = carac_df[col]
    return df

st.title("Statistiques - Marché de l'occasion")
st.markdown("---")

df = get_voitures()
df = flatten_caracteristiques(df)

if df.empty:
    st.warning("Aucune donnée disponible")
else:
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["Vue d'ensemble", "Analyse des prix", "Analyse du marché", "Carburants & Boite", "Corrélations avancées", "Insights Avancés"])
    
    # ========== TAB 1: VUE D'ENSEMBLE ==========
    with tab1:
        st.subheader("Métriques clés")
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("Total annonces", len(df))
        
        with col2:
            if "prix" in df.columns:
                st.metric("Prix moyen", f"{df['prix'].mean():.0f} €")
        
        with col3:
            if "prix" in df.columns:
                st.metric("Prix médian", f"{df['prix'].median():.0f} €")
        
        with col4:
            if "kilometrage" in df.columns:
                st.metric("Km moyen", f"{df['kilometrage'].mean():.0f} km")
        
        with col5:
            if "annee" in df.columns:
                st.metric("Année moyenne", f"{df['annee'].mean():.0f}")
        
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if "marque" in df.columns:
                st.subheader("Top 10 des marques")
                marques_count = df["marque"].value_counts().head(10)
                fig, ax = plt.subplots(figsize=(10, 6))
                marques_count.plot(kind='barh', ax=ax, color='salmon')
                ax.set_xlabel("Nombre d'annonces")
                ax.set_title("Top 10 Marques")
                ax.grid(axis='x', alpha=0.3)
                st.pyplot(fig)
        
        with col2:
            if "energie" in df.columns:
                st.subheader("Distribution par carburant")
                energie_count = df["energie"].value_counts()
                fig, ax = plt.subplots(figsize=(10, 6))
                ax.pie(energie_count.values, labels=energie_count.index, autopct='%1.1f%%', startangle=90)
                ax.set_title("Répartition par Type d'Énergie")
                st.pyplot(fig)
        
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if "boite" in df.columns:
                st.subheader("Distribution par transmission")
                boite_count = df["boite"].value_counts()
                fig, ax = plt.subplots(figsize=(10, 6))
                boite_count.plot(kind='bar', ax=ax, color='lightblue')
                ax.set_xlabel("Type de transmission")
                ax.set_ylabel("Nombre d'annonces")
                ax.set_title("Répartition par Boîte de Vitesses")
                ax.grid(axis='y', alpha=0.3)
                plt.xticks(rotation=45)
                st.pyplot(fig)
        
        with col2:
            if "prix" in df.columns:
                st.subheader("Statistiques des prix")
                stats_prix = df["prix"].describe()
                st.dataframe(stats_prix.to_frame().round(0))
    
    # ========== TAB 2: ANALYSE DES PRIX ==========
    with tab2:
        st.subheader("Analyse détaillée des prix")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if "prix" in df.columns:
                st.write("**Distribution des prix (Histogramme)**")
                fig, ax = plt.subplots(figsize=(10, 6))
                ax.hist(df["prix"].dropna(), bins=50, edgecolor='black', color='skyblue', alpha=0.7)
                ax.set_xlabel("Prix (€)")
                ax.set_ylabel("Nombre de voitures")
                ax.set_title("Distribution des prix")
                ax.grid(axis='y', alpha=0.3)
                st.pyplot(fig)
        
        with col2:
            if "prix" in df.columns:
                st.write("**Box Plot des prix**")
                fig, ax = plt.subplots(figsize=(10, 6))
                ax.boxplot(df["prix"].dropna(), vert=True)
                ax.set_ylabel("Prix (€)")
                ax.set_title("Box Plot des Prix")
                ax.grid(axis='y', alpha=0.3)
                st.pyplot(fig)
        
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if "prix" in df.columns and "marque" in df.columns:
                st.write("**Prix moyen par marque (Top 10)**")
                prix_by_marque = df.groupby("marque")["prix"].mean().sort_values(ascending=False).head(10)
                fig, ax = plt.subplots(figsize=(10, 6))
                prix_by_marque.plot(kind='barh', ax=ax, color='lightcoral')
                ax.set_xlabel("Prix moyen (€)")
                ax.set_title("Prix Moyen par Marque")
                ax.grid(axis='x', alpha=0.3)
                st.pyplot(fig)
        
        with col2:
            if "prix" in df.columns and "energie" in df.columns:
                st.write("**Prix moyen par carburant**")
                prix_by_energie = df.groupby("energie")["prix"].mean().sort_values(ascending=False)
                fig, ax = plt.subplots(figsize=(10, 6))
                prix_by_energie.plot(kind='bar', ax=ax, color='lightgreen')
                ax.set_xlabel("Type d'énergie")
                ax.set_ylabel("Prix moyen (€)")
                ax.set_title("Prix Moyen par Carburant")
                ax.grid(axis='y', alpha=0.3)
                plt.xticks(rotation=45)
                st.pyplot(fig)
        
        st.markdown("---")
        
        if "prix" in df.columns and "boite" in df.columns:
            st.write("**Prix moyen par type de boîte**")
            prix_by_boite = df.groupby("boite")["prix"].mean().sort_values(ascending=False)
            fig, ax = plt.subplots(figsize=(10, 6))
            prix_by_boite.plot(kind='bar', ax=ax, color='lightyellow')
            ax.set_xlabel("Type de boîte")
            ax.set_ylabel("Prix moyen (€)")
            ax.set_title("Prix Moyen par Type de Boîte")
            ax.grid(axis='y', alpha=0.3)
            plt.xticks(rotation=45)
            st.pyplot(fig)
    
    # ========== TAB 3: ANALYSE DU MARCHÉ ==========
    with tab3:
        st.subheader("Analyse du marché")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if "annee" in df.columns:
                st.write("**Distribution par année**")
                fig, ax = plt.subplots(figsize=(10, 6))
                annee_count = df["annee"].value_counts().sort_index()
                ax.plot(annee_count.index, annee_count.values, marker='o', linewidth=2, markersize=6, color='purple')
                ax.set_xlabel("Année")
                ax.set_ylabel("Nombre d'annonces")
                ax.set_title("Nombre d'annonces par année")
                ax.grid(alpha=0.3)
                st.pyplot(fig)
        
        with col2:
            if "kilometrage" in df.columns:
                st.write("**Distribution du kilométrage**")
                fig, ax = plt.subplots(figsize=(10, 6))
                ax.hist(df["kilometrage"].dropna(), bins=50, edgecolor='black', color='orange', alpha=0.7)
                ax.set_xlabel("Kilométrage (km)")
                ax.set_ylabel("Nombre de voitures")
                ax.set_title("Distribution du kilométrage")
                ax.grid(axis='y', alpha=0.3)
                st.pyplot(fig)
        
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if "prix" in df.columns and "annee" in df.columns:
                st.write("**Tendance des prix par année**")
                prix_by_year = df.groupby("annee")["prix"].mean().sort_index()
                fig, ax = plt.subplots(figsize=(10, 6))
                ax.plot(prix_by_year.index, prix_by_year.values, marker='s', linewidth=2, markersize=6, color='red')
                ax.set_xlabel("Année")
                ax.set_ylabel("Prix moyen (€)")
                ax.set_title("Évolution du prix moyen par année")
                ax.grid(alpha=0.3)
                st.pyplot(fig)
        
        with col2:
            if "kilometrage" in df.columns and "annee" in df.columns:
                st.write("**Kilométrage moyen par année**")
                km_by_year = df.groupby("annee")["kilometrage"].mean().sort_index()
                fig, ax = plt.subplots(figsize=(10, 6))
                ax.plot(km_by_year.index, km_by_year.values, marker='^', linewidth=2, markersize=6, color='green')
                ax.set_xlabel("Année")
                ax.set_ylabel("Kilométrage moyen (km)")
                ax.set_title("Kilométrage moyen par année")
                ax.grid(alpha=0.3)
                st.pyplot(fig)
    
    # ========== TAB 4: CARBURANTS & BOÎTE ==========
    with tab4:
        st.subheader("Analyse Carburants & Boîte de vitesses")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if "energie" in df.columns and "boite" in df.columns:
                st.write("**Distribution croisée Carburant × Boîte**")
                cross_tab = pd.crosstab(df["energie"], df["boite"])
                fig, ax = plt.subplots(figsize=(10, 6))
                cross_tab.plot(kind='bar', ax=ax)
                ax.set_xlabel("Type d'énergie")
                ax.set_ylabel("Nombre d'annonces")
                ax.set_title("Carburant × Boîte de vitesses")
                ax.legend(title="Boîte")
                plt.xticks(rotation=45)
                ax.grid(axis='y', alpha=0.3)
                st.pyplot(fig)
        
        with col2:
            if "energie" in df.columns and "marque" in df.columns:
                st.write("**Heatmap Top 8 Marques × Carburant**")
                top_marques = df["marque"].value_counts().head(8).index
                df_top = df[df["marque"].isin(top_marques)]
                cross_tab = pd.crosstab(df_top["marque"], df_top["energie"])
                fig, ax = plt.subplots(figsize=(10, 6))
                sns.heatmap(cross_tab, annot=True, fmt='d', cmap='YlOrRd', ax=ax, cbar_kws={'label': 'Nombre'})
                ax.set_title("Heatmap: Marques × Carburants")
                st.pyplot(fig)
        
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if "kilometrage" in df.columns and "energie" in df.columns:
                st.write("**Kilométrage moyen par carburant**")
                km_by_energie = df.groupby("energie")["kilometrage"].mean().sort_values(ascending=False)
                fig, ax = plt.subplots(figsize=(10, 6))
                km_by_energie.plot(kind='bar', ax=ax, color='lightblue')
                ax.set_xlabel("Type d'énergie")
                ax.set_ylabel("Kilométrage moyen (km)")
                ax.set_title("Kilométrage Moyen par Carburant")
                ax.grid(axis='y', alpha=0.3)
                plt.xticks(rotation=45)
                st.pyplot(fig)
        
        with col2:
            if "kilometrage" in df.columns and "boite" in df.columns:
                st.write("**Kilométrage moyen par transmission**")
                km_by_boite = df.groupby("boite")["kilometrage"].mean().sort_values(ascending=False)
                fig, ax = plt.subplots(figsize=(10, 6))
                km_by_boite.plot(kind='bar', ax=ax, color='lightgray')
                ax.set_xlabel("Type de transmission")
                ax.set_ylabel("Kilométrage moyen (km)")
                ax.set_title("Kilométrage Moyen par Transmission")
                ax.grid(axis='y', alpha=0.3)
                plt.xticks(rotation=45)
                st.pyplot(fig)
    
    # ========== TAB 5: CORRÉLATIONS AVANCÉES ==========
    with tab5:
        st.subheader("Analyse des corrélations")
        
        # Préparer les données numériques
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
        if len(numeric_cols) > 1:
            st.write("**Matrice de corrélation**")
            corr_matrix = df[numeric_cols].corr()
            fig, ax = plt.subplots(figsize=(10, 8))
            sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0, ax=ax, fmt='.2f')
            ax.set_title("Matrice de Corrélation")
            st.pyplot(fig)
        
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if "prix" in df.columns and "kilometrage" in df.columns:
                st.write("**Relation Prix vs Kilométrage**")
                fig, ax = plt.subplots(figsize=(10, 6))
                ax.scatter(df["kilometrage"].dropna(), df["prix"].dropna(), alpha=0.5, color='blue')
                ax.set_xlabel("Kilométrage (km)")
                ax.set_ylabel("Prix (€)")
                ax.set_title("Prix vs Kilométrage")
                ax.grid(alpha=0.3)
                st.pyplot(fig)
        
        with col2:
            if "prix" in df.columns and "annee" in df.columns:
                st.write("**Relation Prix vs Année**")
                fig, ax = plt.subplots(figsize=(10, 6))
                ax.scatter(df["annee"].dropna(), df["prix"].dropna(), alpha=0.5, color='green')
                ax.set_xlabel("Année")
                ax.set_ylabel("Prix (€)")
                ax.set_title("Prix vs Année")
                ax.grid(alpha=0.3)
                st.pyplot(fig)
        
        st.markdown("---")
        
        if "prix" in df.columns and "energie" in df.columns and "kilometrage" in df.columns:
            st.write("**Scatter Plot Prix vs Km coloré par carburant**")
            fig, ax = plt.subplots(figsize=(12, 6))
            
            colors_map = {
                'Diesel': '#FF6B6B',
                'Essence': '#4ECDC4',
                'Hybride': '#45B7D1',
                'Électrique': '#96CEB4',
                'GPL': '#FFEAA7'
            }
            
            for energie in df["energie"].unique():
                if pd.notna(energie):
                    df_energie = df[df["energie"] == energie]
                    ax.scatter(df_energie["kilometrage"].dropna(), df_energie["prix"].dropna(), 
                              alpha=0.5, label=energie, color=colors_map.get(energie, '#999999'))
            
            ax.set_xlabel("Kilométrage (km)")
            ax.set_ylabel("Prix (€)")
            ax.set_title("Prix vs Kilométrage par Carburant")
            ax.legend()
            ax.grid(alpha=0.3)
            st.pyplot(fig)
        
        st.markdown("---")
        
        if "prix" in df.columns and "energie" in df.columns and "annee" in df.columns:
            st.write("**Scatter Plot Prix vs Année coloré par carburant**")
            fig, ax = plt.subplots(figsize=(12, 6))
            
            colors_map = {
                'Diesel': '#FF6B6B',
                'Essence': '#4ECDC4',
                'Hybride': '#45B7D1',
                'Électrique': '#96CEB4',
                'GPL': '#FFEAA7'
            }
            
            for energie in df["energie"].unique():
                if pd.notna(energie):
                    df_energie = df[df["energie"] == energie]
                    ax.scatter(df_energie["annee"].dropna(), df_energie["prix"].dropna(), 
                              alpha=0.5, label=energie, color=colors_map.get(energie, '#999999'))
            
            ax.set_xlabel("Année")
            ax.set_ylabel("Prix (€)")
            ax.set_title("Prix vs Année par Carburant")
            ax.legend()
            ax.grid(alpha=0.3)
            st.pyplot(fig)
    
    # ========== TAB 6: INSIGHTS AVANCÉS ==========
    with tab6:
        st.subheader("📈 Insights Avancés du Marché")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if "energie" in df.columns and "prix" in df.columns:
                st.write("**Distribution des prix par carburant (Box Plot)**")
                fig, ax = plt.subplots(figsize=(10, 6))
                
                energy_types = sorted([e for e in df["energie"].unique() if pd.notna(e)])
                data_to_plot = [df[df["energie"] == energy]["prix"].dropna().values for energy in energy_types]
                
                bp = ax.boxplot(data_to_plot, labels=energy_types, patch_artist=True)
                for patch in bp['boxes']:
                    patch.set_facecolor('#87CEEB')
                
                ax.set_ylabel("Prix (€)")
                ax.set_xlabel("Type d'énergie")
                ax.set_title("Comparaison des prix par carburant")
                ax.tick_params(axis='x', rotation=45)
                ax.grid(axis='y', alpha=0.3)
                st.pyplot(fig)
        
        with col2:
            if "boite" in df.columns and "prix" in df.columns:
                st.write("**Distribution des prix par transmission (Box Plot)**")
                fig, ax = plt.subplots(figsize=(10, 6))
                
                transmission_types = sorted([t for t in df["boite"].unique() if pd.notna(t)])
                data_to_plot = [df[df["boite"] == trans]["prix"].dropna().values for trans in transmission_types]
                
                bp = ax.boxplot(data_to_plot, labels=transmission_types, patch_artist=True)
                for patch in bp['boxes']:
                    patch.set_facecolor('#FFB6C1')
                
                ax.set_ylabel("Prix (€)")
                ax.set_xlabel("Type de transmission")
                ax.set_title("Comparaison des prix par transmission")
                ax.grid(axis='y', alpha=0.3)
                st.pyplot(fig)
        
        st.markdown("---")
        
        if "energie" in df.columns:
            st.subheader("📊 Statistiques détaillées par carburant")
            stats_energie = df.groupby("energie", observed=True).agg({
                "prix": ["count", "mean", "median", "min", "max"],
                "kilometrage": "mean",
                "annee": "mean"
            }).round(0)
            
            stats_energie.columns = ["Nombre annonces", "Prix moyen", "Prix médian", "Prix min", "Prix max", "Km moyen", "Année moyenne"]
            st.dataframe(stats_energie.astype(int))
        
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if "marque" in df.columns and "energie" in df.columns:
                st.subheader("🏆 Top 5 marques par carburant")
                energy_types = sorted([e for e in df["energie"].unique() if pd.notna(e)])
                
                for energy in energy_types[:2]:
                    st.write(f"**{energy}**")
                    top_marques = df[df["energie"] == energy]["marque"].value_counts().head(5)
                    st.write(", ".join([f"{marque} ({count})" for marque, count in top_marques.items()]))
        
        with col2:
            if "marque" in df.columns and "energie" in df.columns:
                st.write("")
                energy_types = sorted([e for e in df["energie"].unique() if pd.notna(e)])
                
                for energy in energy_types[2:]:
                    st.write(f"**{energy}**")
                    top_marques = df[df["energie"] == energy]["marque"].value_counts().head(5)
                    if len(top_marques) > 0:
                        st.write(", ".join([f"{marque} ({count})" for marque, count in top_marques.items()]))
        
        st.markdown("---")
        
        if "prix" in df.columns and "annee" in df.columns:
            st.subheader("💰 Statistiques par tranche de prix")
            
            df_copy = df.copy()
            df_copy['tranche_prix'] = pd.cut(df_copy['prix'], 
                                            bins=[0, 10000, 20000, 50000, 100000, float('inf')],
                                            labels=['<10k€', '10-20k€', '20-50k€', '50-100k€', '>100k€'])
            
            stats_prix = df_copy.groupby('tranche_prix', observed=True).agg({
                'prix': 'count',
                'annee': 'mean',
                'kilometrage': 'mean'
            }).round(0)
            
            stats_prix.columns = ['Nombre', 'Année moyenne', 'Km moyen']
            st.dataframe(stats_prix.astype(int))
        
        st.markdown("---")
        
        if "marque" in df.columns and "energie" in df.columns:
            st.subheader("🔥 Top 8 marques par carburant (Graphique)")
            
            fig, axes = plt.subplots(2, 2, figsize=(14, 10))
            axes = axes.flatten()
            
            energy_types = sorted([e for e in df["energie"].unique() if pd.notna(e)])[:4]
            
            for idx, energy in enumerate(energy_types):
                energy_df = df[df["energie"] == energy]
                top_marques = energy_df["marque"].value_counts().head(8)
                
                top_marques.plot(kind='barh', ax=axes[idx], color='#B8D0E8')
                axes[idx].set_xlabel("Nombre d'annonces")
                axes[idx].set_title(f"Top 8 marques - {energy}")
                axes[idx].grid(axis='x', alpha=0.3)
            
            plt.tight_layout()
            st.pyplot(fig)
        
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if "energie" in df.columns and "annee" in df.columns:
                st.subheader("📅 Prix moyen par carburant et année (Top 5 ans)")
                top_years = df["annee"].value_counts().head(5).index
                
                fig, ax = plt.subplots(figsize=(10, 6))
                for energy in df["energie"].unique():
                    if pd.notna(energy):
                        df_energy = df[(df["energie"] == energy) & (df["annee"].isin(top_years))]
                        prix_by_year = df_energy.groupby("annee")["prix"].mean().sort_index()
                        ax.plot(prix_by_year.index, prix_by_year.values, marker='o', label=energy, linewidth=2)
                
                ax.set_xlabel("Année")
                ax.set_ylabel("Prix moyen (€)")
                ax.set_title("Évolution du prix par carburant")
                ax.legend()
                ax.grid(alpha=0.3)
                st.pyplot(fig)
        
        with col2:
            if "boite" in df.columns and "prix" in df.columns and "annee" in df.columns:
                st.subheader("📅 Prix moyen par transmission et année (Top 5 ans)")
                top_years = df["annee"].value_counts().head(5).index
                
                fig, ax = plt.subplots(figsize=(10, 6))
                for boite in df["boite"].unique():
                    if pd.notna(boite):
                        df_boite = df[(df["boite"] == boite) & (df["annee"].isin(top_years))]
                        prix_by_year = df_boite.groupby("annee")["prix"].mean().sort_index()
                        ax.plot(prix_by_year.index, prix_by_year.values, marker='s', label=boite, linewidth=2)
                
                ax.set_xlabel("Année")
                ax.set_ylabel("Prix moyen (€)")
                ax.set_title("Évolution du prix par transmission")
                ax.legend()
                ax.grid(alpha=0.3)
                st.pyplot(fig)
