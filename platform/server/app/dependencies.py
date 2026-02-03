# Pas necessaire de faire ce code pour l'instant



# DÉPENDANCES: Gestion des ressources partagées
# =============================================
# Rôle: Centraliser la gestion des ressources communes
#       comme les sessions de base de données.

# Fonctions fournies:
# - get_db() : Gestion du cycle de vie des sessions DB
# - get_current_user() : Authentification (si nécessaire)
# - rate_limiter() : Limitation des requêtes

# Avantages:
# - Injection de dépendances propre
# - Gestion automatique des connexions
# - Configuration centralisée
# - Facilité de test

# Utilisation: Tous les endpoints via FastAPI Depends()