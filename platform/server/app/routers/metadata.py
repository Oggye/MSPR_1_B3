# server\app\routers\metadata.py
# ROUTER: Endpoints de métadonnées et qualité des données
# ========================================================
# Rôle: Garantir la transparence et la traçabilité du processus ETL
#       conformément aux exigences RGPD et aux bonnes pratiques.

# Sources utilisées:
# - quality_reports.json : Rapport de qualité généré par le pipeline ETL
# - Documentation du projet
# - Catalogue des sources de données

# Endpoints implémentés:
# 1. GET /api/metadata/quality - Rapport qualité complet
# 2. GET /api/metadata/sources - Catalogue des sources utilisées

# Résultats attendus:
# - Conformité réglementaire (RGPD)
# - Transparence pour les partenaires institutionnels
# - Documentation technique pour la reproductibilité