import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
from datetime import datetime
import folium
from streamlit_folium import folium_static
import altair as alt

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

# Fonctions de chargement par page (paresseux)
@st.cache_data(ttl=300)
def load_kpis():
    return fetch_data("dashboard/kpis")

@st.cache_data(ttl=300)
def load_metrics():
    return fetch_data("dashboard/metrics")

@st.cache_data(ttl=300)
def load_countries():
    return fetch_data("countries")

@st.cache_data(ttl=300)
def load_night_trains(limit=500):
    return fetch_data("night-trains", {"limit": limit})

@st.cache_data(ttl=300)
def load_co2_ranking(limit=20):
    return fetch_data("statistics/co2-ranking", {"limit": limit})

@st.cache_data(ttl=300)
def load_timeline():
    return fetch_data("statistics/timeline")

@st.cache_data(ttl=300)
def load_comparison():
    return fetch_data("analysis/train-types-comparison")

@st.cache_data(ttl=300)
def load_geographic():
    return fetch_data("geographic/coverage")

@st.cache_data(ttl=300)
def load_recommendations():
    return fetch_data("analysis/policy-recommendations")

@st.cache_data(ttl=300)
def load_operators():
    return fetch_data("operators")

@st.cache_data(ttl=300)
def load_quality():
    return fetch_data("metadata/quality")

@st.cache_data(ttl=300)
def load_sources():
    return fetch_data("metadata/sources")

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
         "🚂 Trains de Nuit", 
         "🌍 Carte Interactive",
         "📈 Analyses CO2",
         "🏢 Opérateurs",
         "📚 Sources & Qualité"]
    )
    
    st.markdown("---")
    
    # Filtres globaux 
    if "filters" not in st.session_state:
        st.session_state.filters = {
            "year": 2024,
            "country": "Tous",
            "operator": "Tous"
        }
    
    # Chargement des données pour les filtres (pays et opérateurs)
    countries_data = load_countries()
    operators_data = load_operators()
    
    if countries_data:
        country_list = ["Tous"] + [c["country_name"] for c in countries_data]
        st.session_state.filters["country"] = st.selectbox(
            "🌍 Pays",
            country_list,
            index=country_list.index(st.session_state.filters["country"]) 
                if st.session_state.filters["country"] in country_list else 0
        )
    
    if operators_data:
        operator_list = ["Tous"] + [o["operator_name"] for o in operators_data]
        st.session_state.filters["operator"] = st.selectbox(
            "🏢 Opérateur",
            operator_list,
            index=operator_list.index(st.session_state.filters["operator"])
                if st.session_state.filters["operator"] in operator_list else 0
        )
    
    st.session_state.filters["year"] = st.slider(
        "📅 Année",
        2010, 2024, st.session_state.filters["year"]
    )
    
    st.markdown("---")
    st.markdown("**📊 Données mises à jour:**")
    # On utilisera la date de dernière mise à jour si disponible, sinon l'heure actuelle
    quality = load_quality()
    if quality and quality.get("execution_date"):
        last_update = quality["execution_date"]
    else:
        last_update = datetime.now().strftime('%d/%m/%Y %H:%M')
    st.markdown(f"{last_update}")

# PAGE ACCUEIL
if page == "🏠 Accueil":
    st.markdown("<h1 class='main-header'>🚂 ObRail - Observatoire Européen du Rail</h1>", unsafe_allow_html=True)
    
    kpis = load_kpis()
    if kpis:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f"""
                <div class='kpi-card'>
                    <div class='kpi-number'>{kpis.get('total_countries', 'N/A')}</div>
                    <div class='kpi-label'>Pays couverts</div>
                </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
                <div class='kpi-card'>
                    <div class='kpi-number'>{kpis.get('total_night_trains', 'N/A')}</div>
                    <div class='kpi-label'>Trains de nuit</div>
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
            avg_co2 = kpis.get('avg_co2_per_passenger')
            if avg_co2 is not None:
                st.markdown(f"""
                    <div class='kpi-card'>
                        <div class='kpi-number'>{avg_co2:.3f}</div>
                        <div class='kpi-label'>kg CO₂/passager (moy)</div>
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                    <div class='kpi-card'>
                        <div class='kpi-number'>N/A</div>
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
        if kpis:
            st.markdown(f"""
            - **{kpis.get('years_covered', 'N/A')}** : Période couverte  
            - **{kpis.get('total_passengers', 0):,.0f}** : Millions de passagers  
            - **{kpis.get('total_co2_emissions', 0):,.0f}** : Tonnes CO₂
            """)
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Graphique d'évolution temporelle (avec filtres éventuels)
    timeline = load_timeline()
    if timeline:
        st.markdown("<h2 class='sub-header'>📈 Évolution temporelle</h2>", unsafe_allow_html=True)
        
        timeline_df = pd.DataFrame(timeline)
        # Filtrer par année si souhaité (mais ici on veut toute la série)
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
    
    filters = st.session_state.filters
    
    # Classement CO2
    co2_ranking = load_co2_ranking()
    if co2_ranking:
        st.markdown("<h2 class='sub-header'>🏆 Classement CO₂ par passager</h2>", unsafe_allow_html=True)
        
        ranking_df = pd.DataFrame(co2_ranking)
        ranking_df = ranking_df[['ranking', 'country_name', 'avg_co2_per_passenger', 'performance']]
        ranking_df.columns = ['Rang', 'Pays', 'kg CO₂/passager', 'Performance']
        
        def color_performance(val):
            if val == 'good':
                return 'background-color: #10B981; color: white'
            elif val == 'average':
                return 'background-color: #F59E0B; color: white'
            else:
                return 'background-color: #EF4444; color: white'
        
        styled_df = ranking_df.style.map(color_performance, subset=['Performance'])
        
        col1, col2 = st.columns([2, 1])
        with col1:
            st.dataframe(styled_df, use_container_width=True, height=400)
        with col2:
            top5 = ranking_df.head(5)
            fig = px.bar(
                top5,
                x='Pays',
                y='kg CO₂/passager',
                color='Performance',
                color_discrete_map={'good': '#10B981', 'average': '#F59E0B', 'poor': '#EF4444'},
                title="Top 5 des pays avec le meilleur ratio CO₂"
            )
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
    
    # Métriques par pays (avec filtres)
    metrics = load_metrics()
    if metrics:
        st.markdown("<h2 class='sub-header'>📊 Métriques par pays</h2>", unsafe_allow_html=True)
        metrics_df = pd.DataFrame(metrics)
        
        # Application des filtres
        if filters["country"] != "Tous":
            metrics_df = metrics_df[metrics_df['country_name'] == filters["country"]]
        if filters["year"]:
            metrics_df = metrics_df[metrics_df['year'] == filters["year"]]
        
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

# PAGE TRAINS DE NUIT
elif page == "🚂 Trains de Nuit":
    st.markdown("<h1 class='main-header'>🚂 Catalogue des Trains de Nuit</h1>", unsafe_allow_html=True)
    
    night_trains = load_night_trains()
    if night_trains:
        trains_df = pd.DataFrame(night_trains)
        filters = st.session_state.filters
        
        # Filtre pays
        if filters["country"] != "Tous":
            trains_df = trains_df[trains_df['country_name'] == filters["country"]]
        
        # Filtre opérateur (robuste : gestion des listes séparées par des virgules)
        if filters["operator"] != "Tous":
            mask = trains_df['operator_name'].apply(
                lambda ops: filters["operator"] in [op.strip() for op in str(ops).split(',')]
            )
            trains_df = trains_df[mask]
        
        # Filtre année
        if filters["year"]:
            trains_df = trains_df[trains_df['year'] == filters["year"]]
        
        st.markdown(f"**{len(trains_df)}** trains trouvés")
        
        if not trains_df.empty:
            display_df = trains_df[['night_train', 'country_name', 'operator_name', 'year']]
            display_df.columns = ['Train', 'Pays', 'Opérateur(s)', 'Année']
            st.dataframe(display_df, use_container_width=True, height=500)
            
            # Distribution par pays
            st.markdown("<h2 class='sub-header'>📊 Distribution par pays</h2>", unsafe_allow_html=True)
            country_counts = trains_df['country_name'].value_counts().reset_index()
            country_counts.columns = ['Pays', 'Nombre de trains']
            fig = px.pie(
                country_counts,
                values='Nombre de trains',
                names='Pays',
                title="Répartition des trains de nuit par pays"
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Aucun train ne correspond aux filtres sélectionnés.")

# PAGE CARTE INTERACTIVE
elif page == "🌍 Carte Interactive":
    st.markdown("<h1 class='main-header'>🌍 Carte des Trains de Nuit</h1>", unsafe_allow_html=True)
    
    geographic = load_geographic()
    night_trains = load_night_trains(limit=500)  # On garde une limite pour la carte
    
    if geographic and night_trains:
        geo_data = geographic
        trains_data = pd.DataFrame(night_trains)
        filters = st.session_state.filters
        
        # Optionnel : filtrer les trains affichés sur la carte selon les filtres
        if filters["country"] != "Tous":
            trains_data = trains_data[trains_data['country_name'] == filters["country"]]
        if filters["operator"] != "Tous":
            mask = trains_data['operator_name'].apply(
                lambda ops: filters["operator"] in [op.strip() for op in str(ops).split(',')]
            )
            trains_data = trains_data[mask]
        if filters["year"]:
            trains_data = trains_data[trains_data['year'] == filters["year"]]
        
        # Création de la carte
        m = folium.Map(location=[50, 10], zoom_start=4)
        
        # Dictionnaire des coordonnées approximatives des pays
        country_coords = {
            'FR': [46.603354, 1.888334],
            'DE': [51.165691, 10.451526],
            'IT': [41.87194, 12.56738],
            'ES': [40.463667, -3.74922],
            'BE': [50.85045, 4.34878],
            'NL': [52.132633, 5.291266],
            'UK': [55.378051, -3.435973],
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
        }
        
        # Ajout des pays avec trains
        for country in geo_data.get("coverage_by_country", []):
            country_code = country.get("country_code")
            if country_code not in country_coords:
                continue
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
            
            popup_text = f"""
            <b>{country.get('country_name')}</b><br>
            Trains de nuit: {train_count}<br>
            """
            
            folium.CircleMarker(
                location=country_coords[country_code],
                radius=train_count / 2,
                popup=popup_text,
                color=color,
                fill=True,
                fillColor=color,
                fillOpacity=0.6
            ).add_to(m)
        
        # Ajout des trains individuels (limité à 100 pour la clarté)
        for idx, train in trains_data.head(100).iterrows():
            country_code = train.get('country_code')
            if country_code not in country_coords:
                continue
            base_coord = country_coords[country_code]
            # Léger décalage pour éviter la superposition parfaite, basé sur l'index pour être reproductible
            offset_lat = (idx % 10 - 5) * 0.05
            offset_lon = ((idx // 10) % 10 - 5) * 0.05
            coord = [base_coord[0] + offset_lat, base_coord[1] + offset_lon]
            
            folium.Marker(
                location=coord,
                popup=f"{train['night_train']}<br>Opérateur: {train['operator_name']}",
                icon=folium.Icon(color='blue', icon='train', prefix='fa')
            ).add_to(m)
        
        # Affichage de la carte
        folium_static(m, width=1200, height=600)
        
        # Statistiques
        st.markdown(f"""
        <div class='info-card'>
            <b>🌍 Couverture géographique:</b> {geo_data.get('total_countries_covered', 'N/A')} pays avec des trains de nuit
        </div>
        """, unsafe_allow_html=True)

# PAGE ANALYSES CO2
elif page == "📈 Analyses CO2":
    st.markdown("<h1 class='main-header'>📈 Analyses des Émissions CO₂</h1>", unsafe_allow_html=True)
    
    comparison = load_comparison()
    if comparison:
        st.markdown("<h2 class='sub-header'>⚖️ Comparaison Trains de Jour vs Nuit</h2>", unsafe_allow_html=True)
        
        comparison_df = pd.DataFrame(comparison)
        if not comparison_df.empty and 'train_type' in comparison_df.columns:
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
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                if 'efficiency_score' in comparison_df.columns:
                    fig = px.bar(
                        comparison_df,
                        x='train_type',
                        y='efficiency_score',
                        color='train_type',
                        title="Score d'efficacité environnementale",
                        labels={'train_type': 'Type de train', 'efficiency_score': 'Score (100 = meilleur)'},
                        color_discrete_map={'night': '#2563EB', 'day': '#10B981'}
                    )
                    st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Données de comparaison non disponibles.")
    
    recommendations = load_recommendations()
    if recommendations:
        st.markdown("<h2 class='sub-header'>💡 Recommandations Politiques</h2>", unsafe_allow_html=True)
        
        for rec in recommendations.get("recommendations", []):
            with st.expander(f"**{rec.get('title', 'Sans titre')}**"):
                st.markdown(f"**Description:** {rec.get('description', 'N/A')}")
                st.markdown(f"**Suggestion:** {rec.get('suggestion', 'N/A')}")
                if 'avg_co2_per_passenger' in rec and rec['avg_co2_per_passenger']:
                    vals = rec['avg_co2_per_passenger'][:5]
                    st.markdown(f"**Valeurs CO₂:** {', '.join([f'{x:.3f}' for x in vals])}")

# PAGE OPÉRATEURS
elif page == "🏢 Opérateurs":
    st.markdown("<h1 class='main-header'>🏢 Opérateurs Ferroviaires</h1>", unsafe_allow_html=True)
    
    operators = load_operators()
    if operators:
        operators_df = pd.DataFrame(operators)
        filters = st.session_state.filters
        
        # Recherche textuelle
        search = st.text_input("🔍 Rechercher un opérateur", "")
        if search:
            operators_df = operators_df[operators_df['operator_name'].str.contains(search, case=False)]
        
        st.dataframe(operators_df, use_container_width=True)
        
        # Statistiques si un opérateur est sélectionné
        if filters["operator"] != "Tous":
            selected_operator = filters["operator"]
            operator_row = operators_df[operators_df['operator_name'] == selected_operator]
            if not operator_row.empty:
                operator_id = operator_row.iloc[0]['operator_id']
                operator_stats = fetch_data(f"operators/{operator_id}/stats")
                if operator_stats:
                    st.markdown(f"<h2 class='sub-header'>Statistiques {operator_stats.get('operator_name')}</h2>", unsafe_allow_html=True)
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Trains opérés", operator_stats.get('total_trains', 'N/A'))
                    with col2:
                        st.metric("Pays desservis", operator_stats.get('countries_count', 'N/A'))
                    with col3:
                        countries = operator_stats.get('countries_served', [])
                        st.metric("Pays", ", ".join(countries[:3]) + ("..." if len(countries) > 3 else ""))
                else:
                    st.warning("Impossible de charger les statistiques pour cet opérateur.")
            else:
                st.warning("Opérateur non trouvé dans la liste.")

# PAGE SOURCES & QUALITÉ
elif page == "📚 Sources & Qualité":
    st.markdown("<h1 class='main-header'>📚 Sources de Données & Qualité</h1>", unsafe_allow_html=True)
    
    sources = load_sources()
    quality = load_quality()
    
    if sources:
        st.markdown("<h2 class='sub-header'>📋 Sources de données</h2>", unsafe_allow_html=True)
        for source in sources.get("sources", []):
            with st.expander(f"**{source.get('name', 'Inconnu')}**"):
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.markdown(f"**Description:** {source.get('description', 'N/A')}")
                    url = source.get('url', '#')
                    st.markdown(f"**URL:** [{url}]({url})")
                    st.markdown(f"**Licence:** {source.get('license', 'N/A')}")
                with col2:
                    st.markdown(f"**Fréquence:** {source.get('update_frequency', 'N/A')}")
                    st.markdown(f"**Couverture:** {source.get('coverage', 'N/A')}")
                    st.markdown(f"**Périmètre:** {source.get('geographic_scope', 'N/A')}")
                datasets = source.get('datasets', [])
                st.markdown(f"**Datasets:** {', '.join(datasets)}")
    
    if quality:
        st.markdown("<h2 class='sub-header'>📊 Rapport de Qualité</h2>", unsafe_allow_html=True)
        
        st.markdown(f"**Date d'exécution:** {quality.get('execution_date', 'N/A')}")
        st.markdown(f"**Projet:** {quality.get('project', 'N/A')}")
        
        summary = quality.get("summary", {})
        if summary:
            st.markdown(f"**Résumé:** {'✅ Succès' if summary.get('success') else '❌ Échec'}")
            st.markdown(f"**Sources traitées:** {summary.get('total_sources_processed', 'N/A')}")
        
        traceability = quality.get("traceability", {})
        data_quality = traceability.get("data_quality", {})
        if data_quality:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Pays totaux", data_quality.get("total_countries", "N/A"))
                st.metric("Pays inconnus", data_quality.get("unknown_countries", "N/A"))
            with col2:
                st.metric("Enregistrements trains nuit", data_quality.get("night_train_records", "N/A"))
                st.metric("Enregistrements stats pays", data_quality.get("country_stats_records", "N/A"))
            with col3:
                st.metric("Années couvertes", data_quality.get("total_years", "N/A"))
                st.metric("Opérateurs", data_quality.get("total_operators", "N/A"))
        
        transformations = traceability.get("transformations_applied", [])
        if transformations:
            st.markdown("**Transformations appliquées:**")
            for t in transformations:
                st.markdown(f"- {t}")

# Footer avec date de mise à jour
quality = load_quality()
if quality and quality.get("execution_date"):
    last_update = quality["execution_date"]
else:
    last_update = datetime.now().strftime('%d/%m/%Y %H:%M')

st.markdown(f"""
    <footer class="footer" role="contentinfo">
        <div>🚂 ObRail - Observatoire Européen du Rail | Données ferroviaires 2010-2024</div>
        <div style="font-size: 0.9rem; margin-top: 0.5rem;">
            <span>♿ Site accessible - Conformité partielle RGAA</span> | 
            <span>📊 Données Eurostat & Back-on-Track</span> | 
            <span>🔄 Mise à jour: {last_update}</span>
        </div>
    </footer>
""", unsafe_allow_html=True)