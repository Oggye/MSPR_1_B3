# Phase 2 – Prétraitement des données

## Objectif

L'objectif de cette étape est de préparer le dataset construit lors de la Phase 0 et analysé lors de la Phase 1 afin de le rendre exploitable par les algorithmes de Machine Learning.

Cette phase garantit que les données sont correctement structurées, encodées et normalisées avant l'entraînement des modèles.

---

## Sélection des variables

À partir du dataset de substitution, seules les variables pertinentes pour la prédiction ont été conservées.

Variables numériques :

* distance_km
* duration_min
* duration_hours
* avg_speed_kmh
* long_night_route
* night_bonus

Variables catégorielles :

* country_name
* operator_name
* distance_category
* duration_category

Les identifiants techniques (`fact_id`, `route_id`, `country_id`, `operator_id`) ont été exclus car ils n'apportent aucune information métier utile à la prédiction.

La variable cible retenue est :

* candidate_substitution

---

## Séparation des données

Le dataset a été séparé en deux ensembles :

* 80 % pour l'entraînement
* 20 % pour les tests

Une séparation stratifiée a été utilisée afin de conserver la même répartition des classes dans les différents ensembles.

---

## Encodage des variables catégorielles

Les variables textuelles ont été transformées à l'aide de la méthode **One-Hot Encoding**.

Cette méthode permet de convertir les catégories (pays, opérateurs, types de trajets) en variables numériques exploitables par les algorithmes de Machine Learning.

---

## Standardisation des variables numériques

Les variables numériques ont été standardisées à l'aide de **StandardScaler**.

Cette transformation permet d'harmoniser les échelles de valeurs et d'améliorer les performances de certains modèles d'apprentissage automatique.

---

## Mise en place d'un pipeline de prétraitement

Un pipeline de prétraitement a été construit avec **ColumnTransformer** afin d'automatiser :

* la standardisation des variables numériques ;
* l'encodage des variables catégorielles.

Cette approche garantit la reproductibilité du projet et facilite son intégration future dans l'API de prédiction.

---

## Sauvegarde du préprocesseur

Le pipeline de prétraitement a été sauvegardé au format `joblib`.

Cette sauvegarde permettra de réutiliser exactement les mêmes transformations lors :

* de l'entraînement final ;
* des prédictions via l'API ;
* d'un futur réentraînement du modèle.

---

## Résultat

À l'issue de cette étape, les données sont entièrement préparées pour la phase suivante :

**Développement et comparaison de plusieurs modèles de Machine Learning (Régression Logistique, Random Forest, XGBoost et Réseau de Neurones).**
