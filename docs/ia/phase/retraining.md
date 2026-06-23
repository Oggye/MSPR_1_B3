# Procédure de Réentraînement — Projet ObRail Europe

---

## 1. Contexte

Ce document décrit la procédure complète de réentraînement des modèles ML ObRail, depuis la mise à jour des données source jusqu'au redéploiement en production.

### Lien avec le cahier des charges

> *"Sauvegarder le modèle final. Documenter la procédure de ré-entraînement."*

---

## 2. Déclencheurs de réentraînement

| Déclencheur | Fréquence | Responsable |
|-------------|-----------|-------------|
| Nouvelles données Eurostat disponibles | Annuel (Q1) | Équipe Data |
| Confiance moyenne < 60 % sur `/metrics` | Alerte dès détection | Monitoring automatique |
| Dégradation du R² ou du F1 > 5 % | À chaque évaluation | Équipe ML |
| Ajout de nouveaux pays couverts | Ponctuel | Équipe ETL |

---

## 3. Prérequis

Avant de lancer un réentraînement :

- [ ] Vérifier la disponibilité des nouvelles données Eurostat (`facts_country_stats` mis à jour)
- [ ] Vérifier l'intégrité du warehouse (absence de doublons, cohérence des clés)
- [ ] S'assurer que l'environnement Python est conforme au `requirements.txt`
- [ ] Sauvegarder les modèles actuels (renommer les `.joblib` avec la date : `xgboost_clf_20250101.joblib`)

---

## 4. Étapes de réentraînement

### Étape 1 — Mise à jour des données source

```bash
# Mettre à jour facts_country_stats.csv dans le warehouse
# (via le pipeline ETL)
data/warehouse/facts_country_stats.csv
```

Vérifications post-mise à jour :
```python
df = pd.read_csv("data/warehouse/facts_country_stats.csv")
assert df['year'].max() >= 2025, "Nouvelles données non intégrées"
assert df.duplicated().sum() == 0, "Doublons détectés"
```

### Étape 2 — Reconstruction des datasets ML

```bash
python run_pipeline.py
```

Vérifications attendues :
- Lignes > 546 (nouvelles années intégrées)
- Distribution `en_declin` toujours raisonnable (40–60 % chaque classe)
- Min/max/médiane de `passengers` cohérents avec les données précédentes

### Étape 3 — Réentraînement de tous les modèles

```bash
python -m ia.src.ml.run_training
```

Ce script entraîne les 7 modèles (4 clf + 3 reg) et génère automatiquement les métriques comparatives.

### Étape 4 — Validation des performances

```bash
pytest tests/ -v
```

Critères de validation :
- F1-Score classification ≥ 0.55 (seuil de régression du modèle actuel − 10 %)
- R² régression ≥ 0.95
- Aucun test unitaire échoué

Si les métriques baissent au-delà du seuil, **ne pas déployer** et investiguer :
- Qualité des nouvelles données (valeurs aberrantes ?)
- Dérive de distribution (`data drift`)
- Hyperparamètres à réoptimiser (relancer Phase 6)

### Étape 5 — Remplacement des modèles en production

```bash
# Remplacer les .joblib en production
cp ia/models/xgboost_clf.joblib /path/to/production/models/
cp ia/models/ridge_reg.joblib   /path/to/production/models/
cp data/ml/preprocessor_*.joblib /path/to/production/models/
```

### Étape 6 — Redémarrage de l'API

```bash
# Redémarrer l'API FastAPI
uvicorn api.main:app --reload
```

Vérification post-déploiement :
```bash
curl http://localhost:8000/health
# Attendu : {"status": "ok", "model_version": "..."}
```

---

## 5. Gestion des versions de modèles

| Artefact | Convention de nommage | Exemple |
|----------|----------------------|---------|
| Modèle classification | `xgboost_clf_YYYYMMDD.joblib` | `xgboost_clf_20250101.joblib` |
| Modèle régression | `ridge_reg_YYYYMMDD.joblib` | `ridge_reg_20250101.joblib` |
| Preprocesseur | `preprocessor_clf_YYYYMMDD.joblib` | `preprocessor_clf_20250101.joblib` |
| Métriques | `*_metrics_YYYYMMDD.json` | `xgboost_clf_metrics_20250101.json` |

**Politique de rétention** : conserver les 3 dernières versions pour permettre un rollback.

---

## 6. Matrice de décision post-évaluation

```
Nouvelles métriques ≥ métriques actuelles
    → Déploiement standard (étapes 5–6)

Nouvelles métriques légèrement inférieures (< 5 % de dégradation)
    → Analyse des causes + décision équipe
    → Si cause identifiée et corrigée : déploiement
    → Sinon : maintenir le modèle précédent

Nouvelles métriques fortement inférieures (> 5 % de dégradation)
    → Ne pas déployer
    → Relancer optimisation (Phase 6)
    → Vérifier qualité données (audit ETL)
```

---

## 7. Livrables produits

| Livrable | Chemin |
|----------|--------|
| Procédure réentraînement | `docs/retraining.md` (ce document) |
| Script pipeline | `ia/src/ml/run_pipeline.py` |
| Script entraînement | `ia/src/ml/run_training.py` |
| Tests unitaires | `tests/test_predict.py` |
