# server\app\routers\statistics.py
# ROUTER: Endpoints d'analyse statistique avancée
# ===============================================
# Rôle: Fournir des analyses temporelles et comparatives
#       sur les indicateurs clés du transport ferroviaire.

# Tables utilisées:
# - facts_country_stats : Données statistiques historiques
# - dim_years : Dimension temporelle
# - dim_countries : Contexte géographique

# Endpoints implémentés:
# 1. GET /api/statistics/timeline - Évolution temporelle des indicateurs
# 2. GET /api/statistics/co2-ranking - Classement des pays par performance CO2

# Résultats attendus:
# - Identification des tendances 2010-2024
# - Détection des meilleures pratiques nationales
# - Données pour les modèles prédictifs