# Phase 0 – Compréhension métier et préparation du dataset IA

## Objectif métier

Dans le cadre du projet ObRail Europe, l'équipe a choisi d'étudier l'enjeu suivant :

**Identification automatique des lignes candidates à la substitution avion → train.**

L'objectif est d'aider les décideurs européens à identifier les liaisons ferroviaires susceptibles de remplacer efficacement le transport aérien, dans une logique de mobilité durable et de réduction des émissions de CO₂.

---

## Construction du dataset d'apprentissage

Les données utilisées proviennent du Data Warehouse construit lors des étapes précédentes du projet.

La table principale exploitée est :

* `facts_night_trains`

Cette table contient notamment :

* la distance des trajets (`distance_km`)
* la durée des trajets (`duration_min`)
* le type de train (jour/nuit)
* le pays concerné
* l'opérateur ferroviaire

Les dimensions pays et opérateurs ont été jointes afin d'obtenir un dataset enrichi et exploitable par les algorithmes d'apprentissage automatique.

---

## Création des variables métier (Feature Engineering)

Plusieurs variables ont été créées afin d'améliorer la capacité des futurs modèles à détecter les lignes présentant un potentiel de substitution.

Variables générées :

* `duration_hours` : durée convertie en heures.
* `avg_speed_kmh` : vitesse moyenne du trajet.
* `distance_per_hour` : distance parcourue par heure.
* `long_night_route` : indicateur des trajets de nuit supérieurs à 800 km.
* `distance_category` : catégorisation des trajets (court, moyen, long).
* `duration_category` : catégorisation des durées (rapide, moyenne, lente).
* `night_bonus` : indicateur binaire train de nuit.

Ces variables permettent d'apporter une représentation métier plus riche que les données brutes initiales.

---

## Création de la variable cible

Aucune donnée historique indiquant directement quelles lignes sont substituables n'étant disponible, une règle métier a été définie afin de générer une cible supervisée.

Une ligne est considérée comme candidate à la substitution si :

* distance ≤ 1200 km et durée ≤ 8 heures

ou

* train de nuit
* distance ≤ 1500 km
* durée ≤ 12 heures

Cette règle permet de produire la variable :

`candidate_substitution`

* 1 = ligne candidate
* 0 = ligne non candidate

---

## Résultat obtenu

Le dataset final contient :

* 15 528 observations
* 20 variables

Répartition de la cible :

* Candidates : 12 594 (81,1 %)
* Non candidates : 2 934 (18,9 %)

Exemples :

| Ligne               | Distance | Durée | Candidat |
| ------------------- | -------- | ----- | -------- |
| ÖBB NJ 408 + NJ 409 | 668 km   | 7 h   | Oui      |
| ÖBB NJ 468 + NJ 469 | 1522 km  | 16 h  | Non      |

Le dataset obtenu est désormais prêt pour l'analyse exploratoire et l'entraînement des modèles de Machine Learning.
