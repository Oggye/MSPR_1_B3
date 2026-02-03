# ROUTER: Endpoints pour les opérateurs ferroviaires
# ==================================================
# Rôle: Analyser la performance et la contribution des différents
#       opérateurs ferroviaires européens.

# Tables utilisées:
# - dim_operators : Catalogue des opérateurs
# - facts_night_trains : Trains opérés
# - facts_country_stats : Contexte statistique

# Endpoints implémentés:
# 1. GET /api/operators/ - Liste des opérateurs
# 2. GET /api/operators/{id}/stats - Statistiques par opérateur

# Résultats attendus:
# - Évaluation comparative des opérateurs
# - Identification des leaders du secteur
# - Données pour les partenariats public-privé