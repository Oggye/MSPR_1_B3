# ia/Dockerfile
#
# Conteneur dédié à l'entraînement ML ObRail Europe.
# Exécuté une seule fois après l'ETL (db → etl → ia → api).
# Produit les artefacts dans les volumes partagés :
#   - /app/ia/models/   → modèles .joblib (utilisés par l'API via le cache LRU)
#   - /app/data/ml/     → datasets + preprocesseurs .joblib
#   - /app/ia/reports/  → rapports comparatifs CSV
#
# Compatibilité avec les modifications du router predict.py et ia/src/ml/predict.py :
#   - Le cache @lru_cache de predict.py est chargé au 1er appel API, pas ici.
#   - Ce conteneur produit uniquement les .joblib ; leur chargement est fait par l'API.
#   - La vérification finale des artefacts garantit un exit code non-zéro si l'entraînement
#     échoue, ce qui empêche l'API de démarrer avec des modèles manquants.

FROM python:3.11-slim

# Évite les fichiers .pyc et les buffers stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# PYTHONPATH positionné à /app pour que "from ia.src.ml..." fonctionne
# avec les imports relatifs du package, sans manipulation de sys.path.
ENV PYTHONPATH=/app

WORKDIR /app

# --- Dépendances système minimales ---
# gcc       : nécessaire pour compiler certaines extensions C (XGBoost, pandas)
# libgomp1  : OpenMP pour le parallélisme XGBoost (n_jobs=-1)
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# --- Dépendances Python ---
# requirements.ia.txt doit être à la racine du projet (context: . dans docker-compose).
# Ce fichier doit contenir : numpy, pandas, scikit-learn, xgboost, joblib,
# matplotlib, seaborn, shap — cf. requirements.ia.txt versionné.
COPY requirements.ia.txt .
RUN pip install --no-cache-dir -r requirements.ia.txt

# --- Code source IA ---
# Le dossier ia/ est copié dans l'image pour garantir que le code
# est disponible même si le volume n'est pas encore monté.
# En pratique le volume ./ia:/app/ia le remplace au runtime,
# mais la copie assure un fallback et un build autonome.
COPY ia/ ./ia/

# --- Dossiers de sortie ---
# Créés ici pour que les volumes puissent y écrire sans problème
# de permissions au premier démarrage.
RUN mkdir -p /app/ia/models /app/ia/reports /app/data/ml

# --- Séquence d'entraînement complète ---
#
# CORRECTIF — Vérification des artefacts après chaque étape critique :
#   Sans cette vérification, un échec partiel de run_training retourne exit code 0,
#   docker-compose considère le service "completed_successfully", et l'API démarre
#   sans trouver les .joblib → FileNotFoundError au premier appel /api/predict/*.
#
# Étape 1 : construction des datasets ML depuis le warehouse ETL
# Étape 2 : entraînement de tous les modèles candidats (clf + reg)
# Étape 3 : optimisation XGBoost + Ridge (RandomizedSearchCV + GridSearchCV)
# Étape 4 : vérification que les artefacts minimaux requis par l'API sont présents
#
# Artefacts minimaux requis par platform/server/app/routers/predict.py :
#   - ia/models/xgboost_clf.joblib             (ou xgboost_optimized_clf.joblib)
#   - ia/models/ridge_reg.joblib               (ou ridge_optimized_reg.joblib)
#   - data/ml/preprocessor_classification.joblib
#   - data/ml/preprocessor_regression.joblib

CMD ["sh", "-c", "\
  echo '=== STEP 1 — Construction des datasets ML ===' && \
  python -m ia.src.ml.run_pipeline && \
  \
  echo '=== STEP 2 — Entraînement des modèles candidats ===' && \
  python -m ia.src.ml.run_training && \
  \
  echo '=== STEP 3 — Optimisation XGBoost + Ridge ===' && \
  python -m ia.src.ml.models.optimize_xgboost_ridge && \
  \
  echo '=== STEP 4 — Vérification des artefacts ===' && \
  python -c \"\
import sys; from pathlib import Path; \
required = [ \
  'ia/models/xgboost_clf.joblib', \
  'ia/models/ridge_reg.joblib', \
  'data/ml/preprocessor_classification.joblib', \
  'data/ml/preprocessor_regression.joblib', \
]; \
missing = [f for f in required if not Path(f).exists()]; \
[print(f'❌ Artefact manquant : {f}') for f in missing]; \
sys.exit(1) if missing else print('✅ Tous les artefacts sont présents.') \
\" && \
  echo '=== ✅ Pipeline IA terminé ==='\
"]