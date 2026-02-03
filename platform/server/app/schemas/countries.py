# SCHÉMAS: Modèles Pydantic pour les données pays
# ===============================================
# Rôle: Définir la structure et la validation des données
#       pour les endpoints relatifs aux pays.

# Modèles définis:
# - CountryBase : Structure de base d'un pays
# - CountryResponse : Réponse API avec identifiant
# - CountryStatsBase : Statistiques fondamentales
# - CountryStatsResponse : Statistiques enrichies du contexte

# Validation:
# - Types de données stricts (float pour les métriques)
# - Contraintes de domaine (codes pays ISO)
# - Transformation depuis les modèles SQLAlchemy

# Utilisation: Serialisation/validation dans tous les endpoints pays