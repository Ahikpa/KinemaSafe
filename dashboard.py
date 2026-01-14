import streamlit as st
import pandas as pd
import json
import altair as alt

# Configuration de la page
st.set_page_config(
    page_title="KinemaSafe - Validation Dashboard",
    page_icon="🚗",
    layout="wide"
)

# --- HEADER ---
st.title("🚗 KinemaSafe - Safety Analysis Dashboard")
st.markdown("""
**Contexte :** Validation de sécurité pour véhicules autonomes.
Ce tableau de bord permet de visualiser les données de télémétrie issues des simulations et d'identifier les zones de criticité (Near Miss).
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
    # --- SIDEBAR (CONTRÔLES GLOBAUX) ---
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
    
    # --- TABS (ONGLETS) ---
    tab_data, tab_dashboard = st.tabs(["🔍 Données Brutes (Source)", "📊 Analyse & Sécurité"])

    # === ONGLET 1 : EXPLORATEUR DE DONNÉES ===
    with tab_data:
        st.header("Explorateur de Données Brutes (Source)")
        st.markdown("""
        Cette section permet d'auditer les données entrantes avant traitement.
        C'est l'équivalent de la **'Vérité Terrain' (Ground Truth)** issue du simulateur.
        """)
        
        col_desc, col_dict = st.columns([2, 1])
        
        with col_desc:
            st.subheader("Aperçu du Fichier CSV")
            st.dataframe(df.head(200), use_container_width=True)
            
            st.subheader("Statistiques Descriptives")
            st.write(df[['vehicle_speed_kph', 'obstacle_distance_m', 'ttc']].describe())

        with col_dict:
            st.subheader("Dictionnaire des Données")
            st.info("""
            **timestamp** (float)
            Temps écoulé en secondes depuis le début de l'enregistrement.
            
            **vehicle_speed_kph** (float)
            Vitesse instantanée du véhicule ego en km/h.
            
            **obstacle_distance_m** (float)
            Distance mesurée par le capteur frontal (Radar/Lidar) jusqu'à l'obstacle le plus proche.
            
            **brake_pedal_status** (0/1)
            État de l'actionneur de frein.
            * 0 : Pédale relâchée
            * 1 : Freinage actif
            """)

    # === ONGLET 2 : DASHBOARD DÉCISIONNEL ===
    with tab_dashboard:
        # --- KPI (INDICATEURS CLÉS) ---
        col1, col2, col3, col4 = st.columns(4)
        
        min_ttc = df['ttc'].min()
        critical_frames = df[df['Status'] == 'CRITIQUE'].shape[0]
        duration = df['timestamp'].max()
        
        col1.metric("Durée Scénario", f"{duration} s")
        col2.metric("Vitesse Max", f"{df['vehicle_speed_kph'].max()} km/h")
        col3.metric("TTC Minimum", f"{min_ttc:.2f} s", delta_color="inverse")
        col4.metric("Frames Capturées", f"{critical_frames}", delta="-High Risk" if critical_frames > 0 else "Safe")

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

        # --- EXPORT SECTION & INTERPRETATION ---
        st.divider()
        st.header("📋 Rapport d'Incident (Format Standardisé)")
        
        try:
            with open("data/kinemasafe_output.json", "r") as f:
                json_data = json.load(f)
            
            col_json1, col_json2 = st.columns([1, 2])
            
            with col_json1:
                st.subheader("Métadonnées d'Export")
                st.write(f"**Projet :** {json_data['metadata']['project']}")
                st.write(f"**Partenaire :** {json_data['metadata']['partner']}")
                st.write(f"**Date d'export :** {json_data['metadata']['export_date'][:10]}")
                
                scenario = json_data['scenarios_identified'][0]
                st.info(f"**Type :** {scenario['type']}\n\n**Description :** {scenario['description']}")
                st.metric("Frames Capturées", scenario['events_count'])

            with col_json2:
                st.subheader("Visualisation du Scénario Exporté")
                # Création d'un DF à partir des données du JSON
                df_exported = pd.DataFrame(scenario['time_series_data'])
                
                if not df_exported.empty:
                    # Graphique montrant la sévérité au cours du temps dans le JSON
                    export_chart = alt.Chart(df_exported).mark_bar().encode(
                        x=alt.X('timestamp:O', title="Timestamp (s)"),
                        y=alt.Y('ttc_value:Q', title="TTC calculé"),
                        color=alt.Color('severity', scale=alt.Scale(domain=['HIGH', 'MEDIUM'], range=['#930000', '#FF4B4B'])),
                        tooltip=['timestamp', 'ttc_value', 'severity']
                    ).properties(height=200)
                    
                    st.altair_chart(export_chart, use_container_width=True)
                    st.caption("Ce graphique montre uniquement les données extraites dans le JSON. C'est la 'preuve' de l'incident.")

            with st.expander("Voir le fichier JSON brut (Format Interopérable)"):
                st.json(json_data)

        except FileNotFoundError:
            st.warning("Fichier JSON non généré. Veuillez lancer 'python pipeline.py'.")


else:
    st.warning("Aucune donnée à afficher. Veuillez lancer le pipeline.")
