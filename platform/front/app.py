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
API_BASE_URL = "http://127.0.0.1:8000/api"

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
    /* Footer accessible */
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

def load_all_data():
    """Charge toutes les données nécessaires pour le dashboard"""
    with st.spinner("Chargement des données..."):
        kpis = fetch_data("dashboard/kpis")
        metrics = fetch_data("dashboard/metrics")
        countries = fetch_data("countries")
        night_trains = fetch_data("night-trains", {"limit": 500})
        co2_ranking = fetch_data("statistics/co2-ranking", {"limit": 20})
        timeline = fetch_data("statistics/timeline")
        comparison = fetch_data("analysis/train-types-comparison")
        geographic = fetch_data("geographic/coverage")
        recommendations = fetch_data("analysis/policy-recommendations")
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
    
    # Chargement des données pour les filtres
    countries_data = fetch_data("countries")
    operators_data = fetch_data("operators")
    
    if countries_data:
        country_list = ["Tous"] + [c["country_name"] for c in countries_data]
        st.session_state.filters["country"] = st.selectbox(
            "🌍 Pays",
            country_list,
            index=0
        )
    
    if operators_data:
        operator_list = ["Tous"] + [o["operator_name"] for o in operators_data]
        st.session_state.filters["operator"] = st.selectbox(
            "🏢 Opérateur",
            operator_list,
            index=0
        )
    
    st.session_state.filters["year"] = st.slider(
        "📅 Année",
        2010, 2024, 2024
    )
    
    st.markdown("---")
    
    
    
    st.markdown("---")
    st.markdown("**📊 Données mises à jour:**")
    st.markdown(f"{datetime.now().strftime('%d/%m/%Y %H:%M')}")

# Chargement initial des données
if "data" not in st.session_state:
    st.session_state.data = load_all_data()

data = st.session_state.data

# PAGE ACCUEIL
if page == "🏠 Accueil":
    st.markdown("<h1 class='main-header'>🚂 ObRail - Observatoire Européen du Rail</h1>", unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    if data["kpis"]:
        kpis = data["kpis"]
        
        with col1:
            st.markdown(f"""
                <div class='kpi-card'>
                    <div class='kpi-number'>{kpis['total_countries']}</div>
                    <div class='kpi-label'>Pays couverts</div>
                </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
                <div class='kpi-card'>
                    <div class='kpi-number'>{kpis['total_night_trains']}</div>
                    <div class='kpi-label'>Trains de nuit</div>
                </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
                <div class='kpi-card'>
                    <div class='kpi-number'>{kpis['total_operators']}</div>
                    <div class='kpi-label'>Opérateurs</div>
                </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
                <div class='kpi-card'>
                    <div class='kpi-number'>{kpis['avg_co2_per_passenger']:.3f}</div>
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
        if data["kpis"]:
            st.markdown(f"""
            - **{kpis['years_covered']}** : Période couverte  
            - **{kpis['total_passengers']:,.0f}** : Millions de passagers  
            - **{kpis['total_co2_emissions']:,.0f}** : Tonnes CO₂
            """)
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Graphique d'évolution temporelle
    if data["timeline"]:
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
    if data["co2_ranking"]:
        st.markdown("<h2 class='sub-header'>🏆 Classement CO₂ par passager</h2>", unsafe_allow_html=True)
        
        ranking_df = pd.DataFrame(data["co2_ranking"])
        ranking_df = ranking_df[['ranking', 'country_name', 'avg_co2_per_passenger', 'performance']]
        ranking_df.columns = ['Rang', 'Pays', 'kg CO₂/passager', 'Performance']
        
        # Colorer selon la performance
        def color_performance(val):
            if val == 'good':
                return 'background-color: #10B981; color: white'
            elif val == 'average':
                return 'background-color: #F59E0B; color: white'
            else:
                return 'background-color: #EF4444; color: white'
        
        styled_df = ranking_df.style.applymap(color_performance, subset=['Performance'])
        
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
                color_discrete_map={'good': '#10B981', 'average': '#F59E0B', 'poor': '#EF4444'},
                title="Top 5 des pays avec le meilleur ratio CO₂"
            )
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
    
    # Métriques par pays
    if data["metrics"]:
        st.markdown("<h2 class='sub-header'>📊 Métriques par pays</h2>", unsafe_allow_html=True)
        
        metrics_df = pd.DataFrame(data["metrics"])
        
        # APPLICATION DU FILTRE PAYS
        if st.session_state.filters["country"] != "Tous":
            metrics_df = metrics_df[metrics_df['country_name'] == st.session_state.filters["country"]]
            st.info(f"Affichage des données pour : {st.session_state.filters['country']}")
        
        fig = px.scatter(
            metrics_df,
            x='avg_passengers',
            y='avg_co2_per_passenger',
            size='avg_co2_emissions',
            color='country_name',
            hover_name='country_name',
            title="Relation passagers vs CO₂ par pays",
            labels={
                'avg_passengers': 'Passagers',
                'avg_co2_per_passenger': 'kg CO₂/passager',
                'avg_co2_emissions': 'Émissions totales'
            }
        )
        st.plotly_chart(fig, use_container_width=True)

# PAGE TRAINS DE NUIT
elif page == "🚂 Trains de Nuit":
    st.markdown("<h1 class='main-header'>🚂 Catalogue des Trains de Nuit</h1>", unsafe_allow_html=True)
    
    if data["night_trains"]:
        trains_df = pd.DataFrame(data["night_trains"])

        # APPLICATION DES FILTRES
        # Filtre par pays
        if st.session_state.filters["country"] != "Tous":
            trains_df = trains_df[trains_df['country_name'] == st.session_state.filters["country"]]
        
        # Filtre par opérateur
        if st.session_state.filters["operator"] != "Tous":
            trains_df = trains_df[trains_df['operator_name'].str.contains(st.session_state.filters["operator"], na=False)]
        
        # Filtre par année
        trains_df = trains_df[trains_df['year'] == st.session_state.filters["year"]]
        
        
        
        # Tableau des trains
        if not trains_df.empty:
            display_df = trains_df[['night_train', 'country_name', 'operator_name', 'year']]
            display_df.columns = ['Train', 'Pays', 'Opérateur(s)', 'Année']
            st.dataframe(display_df, use_container_width=True, height=500)
        else:
            st.warning("Aucun train ne correspond aux filtres sélectionnés")

# PAGE CARTE INTERACTIVE
elif page == "🌍 Carte Interactive":
    st.markdown("<h1 class='main-header'>🌍 Carte des Trains de Nuit</h1>", unsafe_allow_html=True)
    
    if data["geographic"] and data["night_trains"]:
        geo_data = data["geographic"]
        trains_data = data["night_trains"]
        trains_data = pd.DataFrame(trains_data)

        # APPLICATION DES FILTRES pour la carte
        if st.session_state.filters["country"] != "Tous":
            trains_data = trains_data[trains_data['country_name'] == st.session_state.filters["country"]]
        
        if st.session_state.filters["operator"] != "Tous":
            trains_data = trains_data[trains_data['operator_name'].str.contains(st.session_state.filters["operator"], na=False)]
        
        trains_data = trains_data[trains_data['year'] == st.session_state.filters["year"]]
        
        st.info(f"Affichage de {len(trains_data)} trains sur la carte")
        
        # Création de la carte
        m = folium.Map(location=[50, 10], zoom_start=4)
        
        # Ajout des pays avec trains
        for country in geo_data["coverage_by_country"]:
            # Couleurs selon le nombre de trains
            if country["train_count"] > 20:
                color = 'darkred'
            elif country["train_count"] > 10:
                color = 'red'
            elif country["train_count"] > 5:
                color = 'orange'
            elif country["train_count"] > 0:
                color = 'green'
            else:
                color = 'gray'
            
            # Coordonnées approximatives des pays
            coords = {
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
            }.get(country["country_code"], [50, 10])
            
            # Popup avec infos
            popup_text = f"""
            <b>{country['country_name']}</b><br>
            Trains de nuit: {country['train_count']}<br>
            """
            
            folium.CircleMarker(
                location=coords,
                radius=country['train_count']/2,
                popup=popup_text,
                color=color,
                fill=True,
                fillColor=color,
                fillOpacity=0.6
            ).add_to(m)
        
        # Ajout des trains individuels 
        for _, train in trains_data[:100].iterrows():
            # Coordonnées aléatoires autour du pays 
            coords = {
                'FR': [46.6 + (hash(train['night_train']) % 10 - 5) / 10, 1.9 + (hash(train['night_train']) % 10 - 5) / 10],
                'DE': [51.2 + (hash(train['night_train']) % 10 - 5) / 10, 10.5 + (hash(train['night_train']) % 10 - 5) / 10],
                'IT': [41.9 + (hash(train['night_train']) % 10 - 5) / 10, 12.6 + (hash(train['night_train']) % 10 - 5) / 10],
            }.get(train['country_code'], [50, 10])
            
            folium.Marker(
                location=coords,
                popup=f"{train['night_train']}<br>Opérateur: {train['operator_name']}",
                icon=folium.Icon(color='blue', icon='train', prefix='fa')
            ).add_to(m)
        
        # Affichage de la carte
        folium_static(m, width=1200, height=600)
        
        # Statistiques
        st.markdown(f"""
        <div class='info-card'>
            <b>🌍 Couverture géographique:</b> {geo_data['total_countries_covered']} pays avec des trains de nuit
        </div>
        """, unsafe_allow_html=True)

# PAGE ANALYSES CO2
elif page == "📈 Analyses CO2":
    st.markdown("<h1 class='main-header'>📈 Analyses des Émissions CO₂</h1>", unsafe_allow_html=True)

    st.info(f"Analyse basée sur les filtres: Pays={st.session_state.filters['country']}, "
            f"Opérateur={st.session_state.filters['operator']}, Année={st.session_state.filters['year']}")
    
    if data["comparison"]:
        st.markdown("<h2 class='sub-header'>⚖️ Comparaison Trains de Jour vs Nuit</h2>", unsafe_allow_html=True)
        
        comparison_df = pd.DataFrame(data["comparison"])
        
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
    
    if data["recommendations"]:
        st.markdown("<h2 class='sub-header'>💡 Recommandations Politiques</h2>", unsafe_allow_html=True)
        
        for rec in data["recommendations"]["recommendations"]:
            with st.expander(f"**{rec['title']}**"):
                st.markdown(f"**Description:** {rec['description']}")
                st.markdown(f"**Suggestion:** {rec['suggestion']}")
                if 'avg_co2_per_passenger' in rec and rec['avg_co2_per_passenger']:
                    st.markdown(f"**Valeurs CO₂:** {', '.join([f'{x:.3f}' for x in rec['avg_co2_per_passenger'][:5]])}")

# PAGE OPÉRATEURS
elif page == "🏢 Opérateurs":
    st.markdown("<h1 class='main-header'>🏢 Opérateurs Ferroviaires</h1>", unsafe_allow_html=True)
    
    if data["operators"]:
        operators_df = pd.DataFrame(data["operators"])
        
        # Recherche
        search = st.text_input("🔍 Rechercher un opérateur", "")
        if search:
            operators_df = operators_df[operators_df['operator_name'].str.contains(search, case=False)]
        
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
                    st.markdown(f"<h2 class='sub-header'>Statistiques {operator_stats['operator_name']}</h2>", unsafe_allow_html=True)
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Trains opérés", operator_stats['total_trains'])
                    
                    with col2:
                        st.metric("Pays desservis", operator_stats['countries_count'])
                    
                    with col3:
                        st.metric("Pays", ", ".join(operator_stats['countries_served'][:3]) + 
                                 ("..." if len(operator_stats['countries_served']) > 3 else ""))

# PAGE SOURCES & QUALITÉ
elif page == "📚 Sources & Qualité":
    st.markdown("<h1 class='main-header'>📚 Sources de Données & Qualité</h1>", unsafe_allow_html=True)
    
    if data["sources"] and data["quality"]:
        sources_data = data["sources"]
        quality_data = data["quality"]
        
        # Métriques de qualité
        if "traceability" in quality_data:
            q = quality_data["traceability"]["data_quality"]
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Pays totaux", q.get("total_countries", "N/A"))
                st.metric("Pays inconnus", q.get("unknown_countries", "N/A"))
            
            with col2:
                st.metric("Enregistrements trains nuit", q.get("night_train_records", "N/A"))
                st.metric("Enregistrements stats pays", q.get("country_stats_records", "N/A"))
            
            with col3:
                st.metric("Années couvertes", q.get("total_years", "N/A"))
                st.metric("Opérateurs", q.get("total_operators", "N/A"))
        
        st.markdown("<h2 class='sub-header'>📋 Sources de données</h2>", unsafe_allow_html=True)
        
        for source in sources_data["sources"]:
            with st.expander(f"**{source['name']}**"):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.markdown(f"**Description:** {source['description']}")
                    st.markdown(f"**URL:** [{source['url']}]({source['url']})")
                    st.markdown(f"**Licence:** {source['license']}")
                
                with col2:
                    st.markdown(f"**Fréquence:** {source['update_frequency']}")
                    st.markdown(f"**Couverture:** {source['coverage']}")
                    st.markdown(f"**Périmètre:** {source['geographic_scope']}")
                
                st.markdown(f"**Datasets:** {', '.join(source['datasets'])}")
        
        # Rapport de qualité
        st.markdown("<h2 class='sub-header'>📊 Rapport de Qualité</h2>", unsafe_allow_html=True)
        
        st.markdown(f"**Date d'exécution:** {quality_data.get('execution_date', 'N/A')}")
        st.markdown(f"**Projet:** {quality_data.get('project', 'N/A')}")
        
        if "summary" in quality_data:
            st.markdown(f"**Résumé:** {'✅ Succès' if quality_data['summary'].get('success') else '❌ Échec'}")
            st.markdown(f"**Sources traitées:** {quality_data['summary'].get('total_sources_processed', 'N/A')}")
        
        if "traceability" in quality_data and "transformations_applied" in quality_data["traceability"]:
            st.markdown("**Transformations appliquées:**")
            for t in quality_data["traceability"]["transformations_applied"]:
                st.markdown(f"- {t}")

# Footer
st.markdown("---")
st.markdown(f"""
    <footer class="footer" role="contentinfo">
        <div>🚂 ObRail - Observatoire Européen du Rail | Données ferroviaires 2010-2024</div>
        <div style="font-size: 0.9rem; margin-top: 0.5rem;">
            <span>♿ Site accessible - Conformité partielle RGAA</span> | 
            <span>📊 Données Eurostat & Back-on-Track</span> | 
            <span>🔄 Mise à jour: {datetime.now().strftime('%d/%m/%Y %H:%M')}</span>
        </div>
    </footer>
""", unsafe_allow_html=True)