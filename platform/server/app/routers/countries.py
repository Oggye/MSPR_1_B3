# ROUTER: Endpoints pour les données pays et statistiques nationales
# ==================================================================
# Rôle: Fournir l'accès aux données statistiques par pays (passagers, CO2)
#       avec filtrage avancé pour les analyses comparatives.

# Tables utilisées:
# - facts_country_stats : Statistiques annuelles par pays
# - dim_countries : Référentiel des pays européens  
# - dim_years : Dimension temporelle (2010-2024)

# Endpoints implémentés:
# 1. GET /api/countries/stats - Statistiques complètes avec filtres
# 2. GET /api/countries/ - Liste des pays référencés

# Résultats attendus:
# - Interface pour le tableau de bord ObRail
# - Données pour les rapports institutionnels
# - Base pour les analyses environnementales comparatives
