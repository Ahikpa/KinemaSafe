import streamlit as st
import pandas as pd
import json
import altair as alt

# Configuration de la page
st.set_page_config(
    page_title="SystemX - Validation Dashboard",
    page_icon="🚗",
    layout="wide"
)

# --- HEADER ---
st.title("🚗 SystemX - Analyseur de Scénarios CCAM")
st.markdown("""
**Contexte :** Validation de systèmes de conduite automatisée.
Ce tableau de bord permet de visualiser les données de télémétrie issues des simulateurs et d'identifier les zones de criticité (Near Miss).
""")

# --- CHARGEMENT DES DONNÉES ---
@st.cache_data
def load_data():
    try:
        # Chargement CSV
        df = pd.read_csv("data/raw_simulation_log.csv")
        
        # Recalcul du TTC pour l'interactivité (Distance / Vitesse m/s)
        # On évite la division par zéro
        df['speed_ms'] = df['vehicle_speed_kph'] / 3.6
        df['ttc'] = df.apply(
            lambda x: x['obstacle_distance_m'] / x['speed_ms'] if x['speed_ms'] > 1 else 100, 
            axis=1
        )
        return df
    except FileNotFoundError:
        st.error("Fichier de données introuvable. Avez-vous lancé 'python pipeline.py' ?")
        return pd.DataFrame()

df = load_data()

if not df.empty:
    # --- SIDEBAR (CONTRÔLES) ---
    st.sidebar.header("Paramètres d'Analyse")
    st.sidebar.info("Ajustez les seuils pour recalibrer la détection d'événements.")
    
    ttc_threshold = st.sidebar.slider(
        "Seuil TTC Critique (secondes)", 
        min_value=0.5, 
        max_value=5.0, 
        value=2.5,
        step=0.1
    )

    # Catégorisation des données en fonction du seuil utilisateur
    df['Status'] = df['ttc'].apply(lambda x: 'CRITIQUE' if x < ttc_threshold else 'NORMAL')
    
    # --- KPI (INDICATEURS CLÉS) ---
    col1, col2, col3, col4 = st.columns(4)
    
    min_ttc = df['ttc'].min()
    critical_frames = df[df['Status'] == 'CRITIQUE'].shape[0]
    duration = df['timestamp'].max()
    
    col1.metric("Durée Scénario", f"{duration} s")
    col2.metric("Vitesse Max", f"{df['vehicle_speed_kph'].max()} km/h")
    col3.metric("TTC Minimum", f"{min_ttc:.2f} s", delta_color="inverse")
    col4.metric("Frames Critiques", f"{critical_frames}", delta="-High Risk" if critical_frames > 0 else "Safe")

    # --- VISUALISATIONS ---
    
    st.divider()
    
    # Graphique 1 : Évolution Temporelle (Distance & Vitesse)
    st.subheader("1. Télémétrie Véhicule")
    
    base = alt.Chart(df).encode(x='timestamp')

    line_speed = base.mark_line(color='blue').encode(
        y=alt.Y('vehicle_speed_kph', title='Vitesse (km/h)'),
        tooltip=['timestamp', 'vehicle_speed_kph']
    )
    
    line_dist = base.mark_line(color='orange').encode(
        y=alt.Y('obstacle_distance_m', title='Distance Obstacle (m)'),
        tooltip=['timestamp', 'obstacle_distance_m']
    )

    st.altair_chart(
        (line_speed).interactive() | (line_dist).interactive(), 
        use_container_width=True
    )

    # Graphique 2 : Zone de Danger (TTC)
    st.subheader("2. Analyse de Sécurité (TTC)")
    st.caption(f"Les zones en ROUGE indiquent un TTC < {ttc_threshold}s (Risque de collision imminent)")

    # On crée un graphique par points colorés selon le statut
    chart_ttc = alt.Chart(df).mark_circle(size=60).encode(
        x='timestamp',
        y=alt.Y('ttc', scale=alt.Scale(domain=[0, 10], clamp=True), title='Time To Collision (s)'),
        color=alt.Color('Status', scale=alt.Scale(domain=['NORMAL', 'CRITIQUE'], range=['green', 'red'])),
        tooltip=['timestamp', 'ttc', 'Status']
    ).interactive()

    # Ligne de seuil
    rule = alt.Chart(pd.DataFrame({'y': [ttc_threshold]})).mark_rule(color='red', strokeDash=[5, 5]).encode(y='y')

    st.altair_chart(chart_ttc + rule, use_container_width=True)

    # --- EXPORT SECTION ---
    st.divider()
    col_l, col_r = st.columns(2)
    
    with col_l:
        st.subheader("Extrait des Données Brutes")
        st.dataframe(df[['timestamp', 'vehicle_speed_kph', 'obstacle_distance_m', 'ttc', 'Status']].head(10))

    with col_r:
        st.subheader("Format Export SYNERGIES (JSON)")
        try:
            with open("data/synergies_standard_output.json", "r") as f:
                json_data = json.load(f)
            st.json(json_data, expanded=False)
        except:
            st.warning("Fichier JSON non généré.")

else:
    st.warning("Aucune donnée à afficher. Veuillez lancer le pipeline.")
