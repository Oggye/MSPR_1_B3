# Phase 8 — Explicabilité des Modèles

---

## 1. Contexte

### Objectif de l'étape

Produire des visualisations d'explicabilité pour les modèles finaux retenus :

- **XGBoost optimisé** pour la classification `en_declin`
- **Ridge baseline** pour la régression `passengers`

L'objectif est de comprendre quelles variables influencent le plus les prédictions, afin de compléter l'évaluation purement métrique par une interprétation métier.

### Position dans le projet

Cette phase intervient après l'évaluation, l'optimisation et la sélection des modèles. Elle permet de justifier les décisions du modèle auprès du jury et de vérifier que les variables importantes sont cohérentes avec la problématique ObRail Europe.

### Lien avec le cahier des charges

Le cahier des charges demande de documenter les modèles, de justifier leur fonctionnement et de produire des éléments d'interprétation. L'explicabilité répond à cette exigence en montrant les variables qui pilotent les prédictions.

---

## 2. Travaux réalisés

Le notebook **`ia/src/ml/notebooks/03_explicabilite.ipynb`** a été créé pour produire les visualisations d'explicabilité.

Il contient deux blocs principaux :

- **Bloc 1 — Classification** : analyse du modèle `xgboost_optimized_clf.joblib`
- **Bloc 2 — Régression** : analyse du modèle `ridge_reg.joblib`

Les figures sont sauvegardées dans :

`docs/ia/img/`

Ce dossier est ignoré par Git afin d'éviter de versionner les images générées automatiquement.

---

## 3. Fonctionnement

### 3.1 Classification — XGBoost optimisé

Le notebook recharge :

- le dataset de classification
- le preprocessor de classification
- le modèle `xgboost_optimized`

Deux types d'explications sont produits.

| Méthode | Rôle | Sortie |
|---------|------|--------|
| `model.feature_importances_` | Importance native des variables dans XGBoost | Barplot horizontal |
| `shap.TreeExplainer(model)` | Contribution globale des variables aux prédictions | Summary plot SHAP |

La feature importance native permet d'identifier les variables les plus utilisées par le modèle lors des séparations d'arbres.

SHAP complète cette analyse en indiquant l'impact des variables sur la prédiction : contribution vers la classe "en déclin" ou vers la classe "en croissance".

### 3.2 Régression — Ridge baseline

Le notebook recharge :

- le dataset de régression
- le preprocessor de régression
- le modèle `ridge`

Deux types d'explications sont produits.

| Méthode | Rôle | Sortie |
|---------|------|--------|
| `model.coef_` | Coefficients du modèle linéaire Ridge | Barplot horizontal |
| `shap.LinearExplainer(model, X_train)` | Contribution globale des variables aux prédictions | Summary plot SHAP |

Pour Ridge, il n'existe pas de `feature_importances_` natif. Les coefficients sont donc utilisés comme indicateur d'influence des variables. Un coefficient positif augmente la prédiction de fréquentation, tandis qu'un coefficient négatif la diminue.

---

## 4. Résultats attendus

Les variables attendues comme importantes sont cohérentes avec la logique métier :

| Variable | Interprétation métier |
|----------|------------------------|
| `passengers_lag1` | Dynamique récente de fréquentation, signal principal pour prévoir l'année suivante |
| `passengers_lag2` | Tendance historique sur deux ans |
| `co2_per_passenger` | Indicateur d'efficacité environnementale |
| `year` | Tendance temporelle globale |

Cette cohérence est importante : elle montre que les modèles ne s'appuient pas sur des variables arbitraires, mais sur des signaux temporels et environnementaux pertinents pour ObRail Europe.

---

## 5. Difficultés rencontrées

- La librairie `shap` n'était pas installée initialement dans l'environnement Python du notebook.
- Le chargement des modèles `.joblib` nécessite que les librairies utilisées à l'entraînement soient présentes dans le même environnement, notamment `xgboost`.
- Les notebooks peuvent utiliser un kernel différent du terminal, ce qui peut provoquer des erreurs du type `ModuleNotFoundError` même après installation d'une dépendance.
- Les images générées peuvent disparaître si le dossier `docs/ia/img` est supprimé, car elles sont régénérables et non versionnées.

---

## 6. Correctifs appliqués

- Ajout de `shap` dans `ia/src/requirements.txt`.
- Alignement du dossier de sortie du notebook 03 sur les notebooks 01 et 02 : `docs/ia/img`.
- Ajout de commentaires courts dans les cellules code pour expliquer le rôle de chaque bloc.
- Vérification que les figures sont sauvegardées avec `plt.savefig(...)`.

---

## 7. Impact sur la suite du projet

Cette phase apporte une justification qualitative aux modèles retenus :

- XGBoost classification peut être expliqué par importance native et par SHAP.
- Ridge régression est interprétable via ses coefficients et via SHAP.
- Les variables temporelles de lag confirment leur rôle central dans la prévision de fréquentation.

L'explicabilité renforce donc la crédibilité des résultats présentés dans les phases précédentes.

---

## 8. Livrables produits

| Livrable | Chemin | Statut |
|----------|--------|--------|
| Notebook explicabilité | `ia/src/ml/notebooks/03_explicabilite.ipynb` | Produit |
| Feature importance classification | `docs/ia/img/fig_feature_importance_clf.png` | Généré par le notebook |
| SHAP classification | `docs/ia/img/fig_shap_clf.png` | Généré par le notebook |
| Coefficients Ridge régression | `docs/ia/img/fig_feature_importance_reg.png` | Généré par le notebook |
| SHAP régression | `docs/ia/img/fig_shap_reg.png` | Généré par le notebook |
| Dépendance SHAP | `ia/src/requirements.txt` | Ajoutée |

---

## 9. Lancement

### Préparer l'environnement

Depuis la racine du projet :

```bash
python -m pip install -r ia/src/requirements.txt
```

Si le notebook utilise Anaconda, installer les dépendances dans l'environnement Anaconda.

```

### Générer les figures

Ouvrir puis exécuter toutes les cellules de :

`ia/src/ml/notebooks/03_explicabilite.ipynb`

Les images sont alors générées dans :

`docs/ia/img/`

Comme ce dossier est dans `.gitignore`, les figures ne sont pas poussées sur Git et doivent être régénérées localement si nécessaire.

