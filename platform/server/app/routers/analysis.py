# server\app\routers\analysis.py
# ROUTER: Endpoints d'analyse avancée et recommandations
# =======================================================
# Rôle: Produire des analyses comparatives et des recommandations
#       basées sur les données pour soutenir les politiques publiques.

# Tables utilisées:
# - facts_night_trains + facts_country_stats : Données combinées
# - dim_countries : Contexte national
# - dim_operators : Acteurs ferroviaires

# Endpoints implémentés:
# 1. GET /api/analysis/train-types-comparison - Comparaison jour/nuit
# 2. GET /api/analysis/policy-recommendations - Recommandations politiques

# Résultats attendus:
# - Preuves data-driven pour le Green Deal européen
# - Arguments pour le développement du ferroviaire nocturne
# - Base pour les décisions d'investissement