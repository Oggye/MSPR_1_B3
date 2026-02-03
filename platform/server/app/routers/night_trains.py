# server\app\routers\night_trains.py
# ROUTER: Endpoints pour les trains de nuit européens
# ====================================================
# Rôle: Exposer le catalogue des trains de nuit avec leurs caractéristiques
#       et permettre l'analyse de leur couverture géographique.

# Tables utilisées:
# - facts_night_trains : Inventaire des trains de nuit
# - dim_countries : Pays desservis
# - dim_operators : Opérateurs ferroviaires
# - dim_years : Période de fonctionnement

# Endpoints implémentés:
# 1. GET /api/night-trains/ - Liste avec filtres pays/opérateur/année
# 2. GET /api/night-trains/by-operator/{id} - Trains par opérateur

# Résultats attendus:
# - Visualisation du réseau de trains de nuit
# - Support pour les études de mobilité durable
# - Données pour les comparaisons modales (train vs avion)