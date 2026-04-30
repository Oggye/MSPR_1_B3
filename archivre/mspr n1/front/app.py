import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
from datetime import datetime
import folium
from streamlit_folium import folium_static
import random

# Configuration de la page
st.set_page_config(
    page_title="ObRail - Observatoire Européen du Rail",
    page_icon="🚂",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API Configuration
API_BASE_URL = "http://api:8000/api"

# Style CSS personnalisé
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        color: #1E3A8A;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #2563EB;
        margin-top: 1rem;
    }
    .footer {
        text-align: center;
        color: #CCCCCC;
        padding: 1.5rem;
        background: rgba(0, 0, 0, 0.8);
        border-radius: 10px;
        margin-top: 2rem;
        backdrop-filter: blur(5px);
    }
    .kpi-card {
        background: linear-gradient(135deg, #1E3A8A 0%, #2563EB 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .kpi-number {
        font-size: 2.2rem;
        font-weight: bold;
    }
    .kpi-label {
        font-size: 1rem;
        opacity: 0.9;
    }
    .info-card {
        background-color: #F3F4F6;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #2563EB;
    }
    .metric-badge {
        background-color: #10B981;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.8rem;
    }
    </style>
""", unsafe_allow_html=True)

# Fonctions pour appeler l'API
@st.cache_data(ttl=300)
def fetch_data(endpoint, params=None):
    """Récupère les données depuis l'API"""
    try:
        url = f"{API_BASE_URL}/{endpoint}"
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Erreur de connexion à l'API: {e}")
        return None
    except Exception as e:
        st.error(f"Erreur: {e}")
        return None

def load_all_data(filters):
    """Charge toutes les données nécessaires en fonction des filtres"""
    params = {}
    if filters["year"] != 2024:
        params["year"] = filters["year"]
    if filters["operator"] != "Tous":
        params["operator_name"] = filters["operator"]  # L'API attend operator_name pour le filtre
    if filters["country"] != "Tous":
        params["country_code"] = get_country_code(filters["country"])  # Conversion nom -> code

    with st.spinner("Chargement des données..."):
        kpis = fetch_data("dashboard/kpis", params)
        metrics = fetch_data("dashboard/metrics", params)
        countries = fetch_data("countries")
        # Ajout du filtre type de train
        if filters["train_type"] == "Nuit":
            night_trains = fetch_data("night-trains/night", params)
        elif filters["train_type"] == "Jour":
            night_trains = fetch_data("night-trains/day", params)
        else:  # "Tous"
            night_trains = fetch_data("night-trains", {"limit": 500, **params})
        co2_ranking = fetch_data("statistics/co2-ranking", {"limit": 20, **params})
        timeline = fetch_data("statistics/timeline", params)
        comparison = fetch_data("analysis/train-types-comparison", params)
        geographic = fetch_data("geographic/coverage", params)
        recommendations = fetch_data("analysis/policy-recommendations", params)
        operators = fetch_data("operators")
        quality = fetch_data("metadata/quality")
        sources = fetch_data("metadata/sources")

    return {
        "kpis": kpis,
        "metrics": metrics,
        "countries": countries,
        "night_trains": night_trains,
        "co2_ranking": co2_ranking,
        "timeline": timeline,
        "comparison": comparison,
        "geographic": geographic,
        "recommendations": recommendations,
        "operators": operators,
        "quality": quality,
        "sources": sources
    }

def get_country_code(country_name):
    """Convertit un nom de pays en code pays (simplifié)"""
    if country_name == "Tous":
        return None
    # Récupérer depuis la liste des pays si disponible
    if "countries" in st.session_state.data:
        for c in st.session_state.data["countries"]:
            if c["country_name"] == country_name:
                return c["country_code"]
    return None

# Sidebar
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/train.png", width=80)
    st.title("ObRail - Observatoire")
    st.markdown("---")
    
    # Sélection de la page
    page = st.radio(
        "Navigation",
        ["🏠 Accueil", 
         "📊 Tableau de Bord", 
         "🚂 Trains (Jour & Nuit)",   
         "🌍 Carte Interactive",
         "📈 Analyses CO2",
         "🏢 Opérateurs",
         "📚 Sources & Qualité"]
    )
    
    st.markdown("---")
    
    # Initialisation des filtres dans session_state
    if "filters" not in st.session_state:
        st.session_state.filters = {
            "year": 2024,
            "country": "Tous",
            "operator": "Tous",
            "train_type": "Tous"
        }
    
    # Chargement des données pour les listes déroulantes
    countries_data = fetch_data("countries")
    operators_data = fetch_data("operators")
    
    if countries_data:
        country_list = ["Tous"] + [c["country_name"] for c in countries_data]
        selected_country = st.selectbox(
            "🌍 Pays",
            country_list,
            index=country_list.index(st.session_state.filters["country"]) if st.session_state.filters["country"] in country_list else 0
        )
        st.session_state.filters["country"] = selected_country
    
    if operators_data:
        operator_list = ["Tous"] + [o["operator_name"] for o in operators_data]
        selected_operator = st.selectbox(
            "🏢 Opérateur",
            operator_list,
            index=operator_list.index(st.session_state.filters["operator"]) if st.session_state.filters["operator"] in operator_list else 0
        )
        st.session_state.filters["operator"] = selected_operator
    
    # Ajout du sélecteur de type de train
    train_type = st.selectbox(
        "🚂 Type de train",
        ["Tous", "Nuit", "Jour"],
        index=["Tous", "Nuit", "Jour"].index(st.session_state.filters["train_type"])
    )
    st.session_state.filters["train_type"] = train_type
    
    st.session_state.filters["year"] = st.slider(
        "📅 Année",
        2010, 2024, st.session_state.filters["year"]
    )
    
    st.markdown("---")
    st.markdown("**📊 Données mises à jour:**")
    st.markdown(f"{datetime.now().strftime('%d/%m/%Y %H:%M')}")

# Vérifier si les filtres ont changé pour recharger les données
if "prev_filters" not in st.session_state:
    st.session_state.prev_filters = st.session_state.filters.copy()

if st.session_state.prev_filters != st.session_state.filters:
    st.session_state.data = load_all_data(st.session_state.filters)
    st.session_state.prev_filters = st.session_state.filters.copy()
elif "data" not in st.session_state:
    st.session_state.data = load_all_data(st.session_state.filters)

data = st.session_state.data

# PAGE ACCUEIL
if page == "🏠 Accueil":
    st.markdown("<h1 class='main-header'>🚂 ObRail - Observatoire Européen du Rail</h1>", unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    if data.get("kpis"):
        kpis = data["kpis"]
        
        with col1:
            st.markdown(f"""
                <div class='kpi-card'>
                    <div class='kpi-number'>{kpis.get('total_countries', 'N/A')}</div>
                    <div class='kpi-label'>Pays couverts</div>
                </div>
            """, unsafe_allow_html=True)
        
        with col2:
            # Afficher le total deu type des trains
            total_trains = len(data.get("night_trains", [])) if data.get("night_trains") else 0
            st.markdown(f"""
                <div class='kpi-card'>
                    <div class='kpi-number'>{total_trains}</div>
                    <div class='kpi-label'>Trains référencés</div>
                </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
                <div class='kpi-card'>
                    <div class='kpi-number'>{kpis.get('total_operators', 'N/A')}</div>
                    <div class='kpi-label'>Opérateurs</div>
                </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
                <div class='kpi-card'>
                    <div class='kpi-number'>{kpis.get('avg_co2_per_passenger', 0):.3f}</div>
                    <div class='kpi-label'>kg CO₂/passager (moy)</div>
                </div>
            """, unsafe_allow_html=True)
    
    st.markdown("<h2 class='sub-header'>📋 Dernières actualités</h2>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("<div class='info-card'>", unsafe_allow_html=True)
        st.markdown("**🎯 Mission**")
        st.markdown("""
        L'Observatoire Européen du Rail (ObRail) collecte, analyse et visualise 
        les données ferroviaires européennes pour promouvoir la mobilité durable.
        """)
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        st.markdown("<div class='info-card'>", unsafe_allow_html=True)
        st.markdown("**📊 Couverture**")
        if data.get("kpis"):
            kpis = data["kpis"]
            st.markdown(f"""
            - **{kpis.get('years_covered', 'N/A')}** : Période couverte  
            - **{kpis.get('total_passengers', 0):,.0f}** : Millions de passagers  
            - **{kpis.get('total_co2_emissions', 0):,.0f}** : Tonnes CO₂
            """)
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Graphique d'évolution temporelle
    if data.get("timeline"):
        st.markdown("<h2 class='sub-header'>📈 Évolution temporelle</h2>", unsafe_allow_html=True)
        
        timeline_df = pd.DataFrame(data["timeline"])
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=timeline_df['year'],
            y=timeline_df['passengers'],
            name='Passagers',
            mode='lines+markers',
            line=dict(color='#2563EB', width=3),
            marker=dict(size=8)
        ))
        
        fig.add_trace(go.Scatter(
            x=timeline_df['year'],
            y=timeline_df['co2_emissions'],
            name='Émissions CO₂',
            mode='lines+markers',
            line=dict(color='#10B981', width=3),
            marker=dict(size=8),
            yaxis='y2'
        ))
        
        fig.update_layout(
            title="Évolution des passagers et émissions CO₂",
            xaxis_title="Année",
            yaxis_title="Passagers (millions)",
            yaxis2=dict(
                title="Émissions CO₂ (tonnes)",
                overlaying='y',
                side='right'
            ),
            hovermode='x unified',
            height=500
        )
        
        st.plotly_chart(fig, use_container_width=True)

# PAGE TABLEAU DE BORD
elif page == "📊 Tableau de Bord":
    st.markdown("<h1 class='main-header'>📊 Tableau de Bord Principal</h1>", unsafe_allow_html=True)
    
    # Classement CO2
    if data.get("co2_ranking"):
        st.markdown("<h2 class='sub-header'>🏆 Classement CO₂ par passager</h2>", unsafe_allow_html=True)
        
        ranking_df = pd.DataFrame(data["co2_ranking"])
        if not ranking_df.empty:
            ranking_df = ranking_df[['ranking', 'country_name', 'avg_co2_per_passenger', 'performance']]
            ranking_df.columns = ['Rang', 'Pays', 'kg CO₂/passager', 'Performance']
            
            # Colorer selon la performance
            def color_performance(val):
                if val == 'good':
                    return 'background-color: #10B981; color: white'
                elif val == 'medium':
                    return 'background-color: #F59E0B; color: white'
                else:
                    return 'background-color: #EF4444; color: white'
            
            styled_df = ranking_df.style.map(color_performance, subset=['Performance'])
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.dataframe(styled_df, use_container_width=True, height=400)
            
            with col2:
                # Top 5 graphique
                top5 = ranking_df.head(5)
                fig = px.bar(
                    top5,
                    x='Pays',
                    y='kg CO₂/passager',
                    color='Performance',
                    color_discrete_map={'good': '#10B981', 'medium': '#F59E0B', 'bad': '#EF4444'},
                    title="Top 5 des pays avec le meilleur ratio CO₂"
                )
                fig.update_layout(showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
    
    # Métriques par pays
    if data.get("metrics"):
        st.markdown("<h2 class='sub-header'>📊 Métriques par pays</h2>", unsafe_allow_html=True)
        
        metrics_df = pd.DataFrame(data["metrics"])
        
        # Filtre par pays
        if st.session_state.filters["country"] != "Tous" and 'country_name' in metrics_df.columns:
            metrics_df = metrics_df[metrics_df['country_name'] == st.session_state.filters["country"]]
        
        if not metrics_df.empty:
            fig = px.scatter(
                metrics_df,
                x='avg_passengers',
                y='avg_co2_per_passenger',
                size='avg_co2_emissions',
                color='country_name',
                hover_name='country_name',
                title="Relation passagers vs CO₂ par pays",
                labels={
                    'avg_passengers': 'Passagers (millions)',
                    'avg_co2_per_passenger': 'kg CO₂/passager',
                    'avg_co2_emissions': 'Émissions totales'
                }
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Aucune donnée pour les filtres sélectionnés.")

# PAGE TRAINS (JOUR & NUIT)
elif page == "🚂 Trains (Jour & Nuit)":
    st.markdown("<h1 class='main-header'>🚂 Catalogue des Trains (Jour & Nuit)</h1>", unsafe_allow_html=True)
    
    if data.get("night_trains"):
        trains_df = pd.DataFrame(data["night_trains"])
        
        # Ajout d'une colonne type pour l'affichage
        trains_df['type'] = trains_df['is_night'].apply(
            lambda x: 'Tous' if x is None else ('Jour' if x is False else 'Nuit')
        )

        # Statistiques
        st.markdown(f"**{len(trains_df)}** trains trouvés")
        
        if not trains_df.empty:
            # Tableau des trains
            display_df = trains_df[['night_train', 'country_name', 'operator_name', 'year', 'type']]
            display_df.columns = ['Train', 'Pays', 'Opérateur(s)', 'Année', 'Type']
            
            st.dataframe(display_df, use_container_width=True, height=500, hide_index=True)
            
            # Distribution par pays
            st.markdown("<h2 class='sub-header'>📊 Distribution par pays</h2>", unsafe_allow_html=True)
            
            country_counts = trains_df.groupby(['country_name', 'type']).size().reset_index(name='count')
            
            fig = px.bar(
                country_counts,
                x='country_name',
                y='count',
                color='type',
                title="Répartition des trains par pays et type",
                labels={'country_name': 'Pays', 'count': 'Nombre de trains', 'type': 'Type'},
                barmode='group',
                color_discrete_map={'Jour': '#10B981', 'Nuit': '#2563EB'}
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Aucun train ne correspond aux filtres sélectionnés.")
    else:
        st.warning("Données de trains non disponibles.")

# PAGE CARTE INTERACTIVE
elif page == "🌍 Carte Interactive":
    st.markdown("<h1 class='main-header'>🌍 Carte des Trains (Jour & Nuit)</h1>", unsafe_allow_html=True)
    
    if data.get("geographic") and data.get("night_trains"):
        geo_data = data["geographic"]
        trains_data = pd.DataFrame(data["night_trains"])
        
        # Ajout colonne type
        if not trains_data.empty and 'is_night' in trains_data.columns:
            trains_data['type'] = trains_data['is_night'].apply(lambda x: 'Nuit' if x else 'Jour')
        
        # Dictionnaire complet des coordonnées des pays européens
        country_coords = {
            'FR': [46.603354, 1.888334],
            'DE': [51.165691, 10.451526],
            'IT': [41.87194, 12.56738],
            'ES': [40.463667, -3.74922],
            'BE': [50.85045, 4.34878],
            'NL': [52.132633, 5.291266],
            'GB': [55.378051, -3.435973],
            'CH': [46.818188, 8.227512],
            'AT': [47.516231, 14.550072],
            'PL': [51.919438, 19.145136],
            'RO': [45.943161, 24.96676],
            'BG': [42.733883, 25.48583],
            'HU': [47.162494, 19.503304],
            'SK': [48.669026, 19.699024],
            'CZ': [49.817492, 15.472962],
            'HR': [45.1, 15.2],
            'RS': [44.016521, 21.005859],
            'SE': [60.128161, 18.643501],
            'NO': [60.472024, 8.468946],
            'FI': [61.92411, 25.748151],
            'DK': [56.26392, 9.501785],
            'IE': [53.1424, -7.6921],
            'PT': [39.3999, -8.2245],
            'LU': [49.8153, 6.1296],
            'SI': [46.1512, 14.9955],
            'EE': [58.5953, 25.0136],
            'LV': [56.8796, 24.6032],
            'LT': [55.1694, 23.8813],
            'GR': [39.0742, 21.8243],
        }
        
        # Création de la carte
        m = folium.Map(location=[50, 10], zoom_start=4)
        
        # Ajout des pays avec trains (tous types confondus pour les cercles)
        for country in geo_data.get("coverage_by_country", []):
            # Couleurs selon le nombre de trains
            train_count = country.get("train_count", 0)
            if train_count > 20:
                color = 'darkred'
            elif train_count > 10:
                color = 'red'
            elif train_count > 5:
                color = 'orange'
            elif train_count > 0:
                color = 'green'
            else:
                color = 'gray'
            
            # Coordonnées du pays
            coords = country_coords.get(country.get("country_code"), [50, 10])
            
            # Popup avec infos
            popup_text = f"""
            <b>{country.get('country_name', 'Inconnu')}</b><br>
            Trains: {train_count}<br>
            """
            
            folium.CircleMarker(
                location=coords,
                radius=max(3, train_count / 2),
                popup=popup_text,
                color=color,
                fill=True,
                fillColor=color,
                fillOpacity=0.6
            ).add_to(m)
        
        # Ajout des trains individuels (limité à 100 pour la performance)
        if not trains_data.empty:
            for _, train in trains_data.head(100).iterrows():
                # Coordonnées approximatives autour du pays
                base_coords = country_coords.get(train.get('country_code'), [50, 10])
                # Ajout d'un petit décalage pour éviter la superposition
                offset_lat = random.uniform(-0.5, 0.5)
                offset_lon = random.uniform(-0.5, 0.5)
                coords = [base_coords[0] + offset_lat, base_coords[1] + offset_lon]
                
                # Icône différente pour jour/nuit
                if train.get('type') == 'Nuit':
                    icon = folium.Icon(color='darkblue', icon='moon', prefix='fa')
                else:
                    icon = folium.Icon(color='orange', icon='sun', prefix='fa')
                
                folium.Marker(
                    location=coords,
                    popup=f"{train.get('night_train', 'Train inconnu')}<br>Opérateur: {train.get('operator_name', 'Inconnu')}<br>Type: {train.get('type', 'Inconnu')}",
                    icon=icon
                ).add_to(m)
        
        # Ajout de la légende
        legend_html = """
        <div style="position: fixed; bottom: 50px; left: 50px; width: 240px; height: 200px; 
                    background-color: white; border:2px solid grey; z-index:9999; font-size:14px;
                    padding: 10px; border-radius: 5px; opacity:0.9;">
            <b>Légende</b><br>
            <span style="color:darkred;">●</span> > 20 trains<br>
            <span style="color:red;">●</span> 11–20 trains<br>
            <span style="color:orange;">●</span> 6–10 trains<br>
            <span style="color:green;">●</span> 1–5 trains<br>
            <span style="color:gray;">●</span> Aucun train<br>
            <span style="color:darkblue;">🌙</span> Train de nuit<br>
            <span style="color:orange;">☀️</span> Train de jour
        </div>
        """
        m.get_root().html.add_child(folium.Element(legend_html))
        
        # Affichage de la carte
        folium_static(m, width=1200, height=600)
        
        # Statistiques
        st.markdown(f"""
        <div class='info-card'>
            <b>🌍 Couverture géographique:</b> {geo_data.get('total_countries_covered', 0)} pays avec des trains
        </div>
        """, unsafe_allow_html=True)
    else:
        st.warning("Données géographiques non disponibles.")

# PAGE ANALYSES CO2
elif page == "📈 Analyses CO2":
    st.markdown("<h1 class='main-header'>📈 Analyses des Émissions CO₂</h1>", unsafe_allow_html=True)
    
    if data.get("comparison"):
        st.markdown("<h2 class='sub-header'>⚖️ Comparaison Trains de Jour vs Nuit</h2>", unsafe_allow_html=True)
        
        comparison_df = pd.DataFrame(data["comparison"])
        
        if not comparison_df.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                fig = px.bar(
                    comparison_df,
                    x='train_type',
                    y='avg_co2_per_passenger',
                    color='train_type',
                    title="Émissions CO₂ par passager",
                    labels={'train_type': 'Type de train', 'avg_co2_per_passenger': 'kg CO₂/passager'},
                    color_discrete_map={'night': '#2563EB', 'day': '#10B981'}
                )

                fig.update_xaxes(ticktext=['Nuit', 'Jour'], tickvals=['night', 'day'])
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                fig = px.bar(
                    comparison_df,
                    x='train_type',
                    y='efficiency_score',
                    color='train_type',
                    title="Score d'efficacité environnementale",
                    labels={'train_type': 'Type de train', 'efficiency_score': 'Score (100 = meilleur)'},
                    color_discrete_map={'night': '#2563EB', 'day': '#10B981'}
                )
                fig.update_xaxes(ticktext=['Nuit', 'Jour'], tickvals=['night', 'day'])
                st.plotly_chart(fig, use_container_width=True)
    
    if data.get("recommendations"):
        st.markdown("<h2 class='sub-header'>💡 Recommandations Politiques</h2>", unsafe_allow_html=True)
        
        for rec in data["recommendations"].get("recommendations", []):
            with st.expander(f"**{rec.get('title', 'Titre inconnu')}**"):
                st.markdown(f"**Description:** {rec.get('description', '')}")
                st.markdown(f"**Suggestion:** {rec.get('suggestion', '')}")
                if rec.get('avg_co2_per_passenger'):
                    st.markdown(f"**Valeurs CO₂:** {', '.join([f'{x:.3f}' for x in rec['avg_co2_per_passenger'][:5]])}")

# PAGE OPÉRATEURS
elif page == "🏢 Opérateurs":
    st.markdown("<h1 class='main-header'>🏢 Opérateurs Ferroviaires</h1>", unsafe_allow_html=True)
    
    if data.get("operators"):
        operators_df = pd.DataFrame(data["operators"])
        
        # Recherche
        search = st.text_input("🔍 Rechercher un opérateur", "")
        if search:
            operators_df = operators_df[operators_df['operator_name'].str.contains(search, case=False, na=False)]
        
        st.dataframe(operators_df, use_container_width=True, hide_index=True)
        
        # Statistiques par opérateur si un opérateur est sélectionné
        if st.session_state.filters["operator"] != "Tous":
            selected_operator = st.session_state.filters["operator"]
            # Trouver l'ID de l'opérateur
            operator_id = None
            for op in data["operators"]:
                if op["operator_name"] == selected_operator:
                    operator_id = op["operator_id"]
                    break
            
            if operator_id:
                operator_stats = fetch_data(f"operators/{operator_id}/stats")
                if operator_stats:
                    st.markdown(f"<h2 class='sub-header'>Statistiques {operator_stats.get('operator_name', '')}</h2>", unsafe_allow_html=True)
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Trains opérés", operator_stats.get('total_trains', 'N/A'))
                    
                    with col2:
                        st.metric("Pays desservis", operator_stats.get('countries_count', 'N/A'))
                    
                    with col3:
                        countries_served = operator_stats.get('countries_served', [])
                        st.metric("Pays", ", ".join(countries_served[:3]) + ("..." if len(countries_served) > 3 else ""))
    else:
        st.info("Aucune donnée opérateur disponible.")

# PAGE SOURCES & QUALITÉ
elif page == "📚 Sources & Qualité":
    st.markdown("<h1 class='main-header'>📚 Sources de Données & Qualité</h1>", unsafe_allow_html=True)
    
    if data.get("sources") and data.get("quality"):
        sources_data = data["sources"]
        quality_data = data["quality"]
        
        # Métriques de qualité
        traceability = quality_data.get("traceability", {})
        data_quality = traceability.get("data_quality", {})
        
        if data_quality:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Pays totaux", data_quality.get("total_countries", "N/A"))
                st.metric("Pays inconnus", data_quality.get("unknown_countries", "N/A"))
            
            with col2:
                # Afficher le nombre total de trains (tous types)
                total_trains = data_quality.get("night_train_records", "N/A")  # Le champ s'appelle encore night_train_records mais inclut tous les trains
                st.metric("Enregistrements trains", total_trains)
                st.metric("Enregistrements stats pays", data_quality.get("country_stats_records", "N/A"))
            
            with col3:
                st.metric("Années couvertes", data_quality.get("total_years", "N/A"))
                st.metric("Opérateurs", data_quality.get("total_operators", "N/A"))
        
        st.markdown("<h2 class='sub-header'>📋 Sources de données</h2>", unsafe_allow_html=True)
        
        for source in sources_data.get("sources", []):
            with st.expander(f"**{source.get('name', 'Source inconnue')}**"):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.markdown(f"**Description:** {source.get('description', '')}")
                    st.markdown(f"**URL:** [{source.get('url', '#')}]({source.get('url', '#')})")
                    st.markdown(f"**Licence:** {source.get('license', '')}")
                
                with col2:
                    st.markdown(f"**Fréquence:** {source.get('update_frequency', '')}")
                    st.markdown(f"**Couverture:** {source.get('coverage', '')}")
                    st.markdown(f"**Périmètre:** {source.get('geographic_scope', '')}")
                
                st.markdown(f"**Datasets:** {', '.join(source.get('datasets', []))}")
        
        # Rapport de qualité
        st.markdown("<h2 class='sub-header'>📊 Rapport de Qualité</h2>", unsafe_allow_html=True)
        
        st.markdown(f"**Date d'exécution:** {quality_data.get('execution_date', 'N/A')}")
        st.markdown(f"**Projet:** {quality_data.get('project', 'N/A')}")
        
        summary = quality_data.get("summary", {})
        if summary:
            st.markdown(f"**Résumé:** {'✅ Succès' if summary.get('success') else '❌ Échec'}")
            st.markdown(f"**Sources traitées:** {summary.get('total_sources_processed', 'N/A')}")
        
        transformations = traceability.get("transformations_applied", [])
        if transformations:
            st.markdown("**Transformations appliquées:**")
            for t in transformations:
                st.markdown(f"- {t}")
    else:
        st.warning("Données de qualité ou sources non disponibles.")

# Footer
st.markdown(f"""
    <footer class="footer" role="contentinfo">
        <div>🚂 ObRail - Observatoire Européen du Rail | Données ferroviaires 2010-2024</div>
        <div style="font-size: 0.9rem; margin-top: 0.5rem;">
            <span>♿ Site accessible - Conformité partielle RGAA</span> | 
            <span>📊 Données Eurostat & Back-on-Track & GTFS</span> | 
            <span>🔄 Mise à jour: {datetime.now().strftime('%d/%m/%Y %H:%M')}</span>
        </div>
    </footer>
""", unsafe_allow_html=True)