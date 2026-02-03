# ROUTER: Endpoints pour le tableau de bord ObRail
# ================================================
# Rôle: Alimenter le dashboard interactif avec des indicateurs synthétiques
#       et des métriques agrégées pour la prise de décision.

# Tables/vues utilisées:
# - dashboard_metrics : Vue SQL des indicateurs agrégés
# - facts_country_stats : Données sources
# - dim_countries : Contexte géographique

# Endpoints implémentés:
# 1. GET /api/dashboard/metrics - Métriques pour visualisations
# 2. GET /api/dashboard/kpis - Indicateurs clés de performance

# Résultats attendus:
# - Dashboard temps réel pour décideurs politiques
# - Monitoring de la mobilité durable européenne
# - Support visuel pour les présentations institutionnelles