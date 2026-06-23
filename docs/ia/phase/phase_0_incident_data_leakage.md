# Phase 0 — Incident Data Leakage : Diagnostic et Réorientation du Sujet ML

---

## 1. Contexte

### Objectif de l'étape

Cette phase documente un incident critique identifié en cours de projet : un **data leakage structurel** rendant tous les modèles initialement entraînés invalides. Elle retrace le diagnostic, les tentatives de correction successives, et la décision de réorientation vers un nouveau sujet ML cohérent avec les données disponibles.

### Position dans le projet

Cette phase précède toute la chaîne ML. Sans sa résolution, aucun modèle produit n'aurait de valeur scientifique ou opérationnelle.

### Lien avec le cahier des charges

Le cahier des charges ObRail impose que le modèle soit :
- **reproductible et justifié** ;
- conforme aux **bonnes pratiques de préparation et d'évaluation des données** ;
- accompagné d'une **documentation des choix méthodologiques**.

La détection et la correction d'un data leakage s'inscrivent directement dans ces exigences, et constituent une compétence clé évaluée : *"Résoudre les incidents techniques"* (bloc E6.4).

---

## 2. Travaux réalisés

### 2.1 Sujet initial et construction de la cible

Le premier sujet retenu était l'**identification automatique des lignes ferroviaires candidates à la substitution avion → train**. Une variable cible binaire `candidate_substitution` a été construite à partir de règles métier explicites :

```python
if distance_km <= 1200 and duration_min <= 480:
    candidate_substitution = 1
if is_night and distance_km <= 1500 and duration_min <= 720:
    candidate_substitution = 1
```

Ces règles ont été appliquées sur la table `facts_night_trains`, qui contient les variables `distance_km`, `duration_min` et `is_night`.

### 2.2 Symptôme détecté

Lors de l'évaluation des premiers modèles, tous ont atteint une **accuracy de 1.0**, quelle que soit l'architecture testée (régression logistique, Random Forest, XGBoost, MLP). Ce résultat parfait sur l'ensemble de test constitue le signal d'alerte classique d'un data leakage.

### 2.3 Tentatives de correction

**Tentative 1 — Cible basée sur `passengers` et `co2_per_passenger` par pays**

```python
ligne_fragile = (passengers < médiane) AND (co2_per_passenger > médiane)
```

Problème identifié : `passengers` et `co2_per_passenger` sont des valeurs **agrégées au niveau pays**. Avec 42 pays, tous les enregistrements d'un même pays reçoivent la même valeur de cible. Les modèles mémorisent 42 règles pays → scores quasi-parfaits persistants.

**Tentative 2 — Cible basée sur distance et vitesse au niveau train**

```python
signal_distance = distance_km > médiane
signal_speed    = avg_speed_kmh < médiane
ligne_fragile   = (signal_distance + signal_speed + is_night) >= 2
```

Problème identifié : `avg_speed_kmh` est calculé comme `distance_km / duration_hours`. Les features `distance_category` et `duration_category` encodaient les mêmes seuils sous forme catégorielle. Les modèles retrouvaient la règle de construction de la cible via les features dérivées — **leakage indirect**.

---

## 3. Fonctionnement — Mécanisme du Data Leakage

Le data leakage survient lorsque **la variable cible est construite à partir des mêmes variables que celles utilisées comme features d'entraînement**. Dans ce cas, le modèle n'apprend pas une relation statistique réelle : il mémorise une fonction déterministe.

```
[Règle métier]
    ↓
construction de la cible via distance_km et duration_min
    ↓
ces mêmes variables présentes dans les features
    ↓
le modèle apprend : if distance_km ≤ 1200 → predict 1
    ↓
accuracy = 1.0 → invalide
```

Ce type d'erreur est particulièrement difficile à détecter car les métriques semblent excellentes. C'est précisément leur perfection qui constitue le signal d'alerte.

---

## 4. Résultats obtenus (sujet initial — invalides)

| Modèle | Accuracy |
|--------|----------|
| Logistic Regression | 1.0 |
| Random Forest | 1.0 |
| XGBoost | 1.0 |
| MLP | 1.0 |

Ces résultats sont **scientifiquement invalides** et ont conduit à l'abandon du sujet initial.

---

## 5. Difficultés rencontrées

### Limite fondamentale du dataset initial

Après audit complet, la conclusion est la suivante : la table `facts_night_trains` contient **uniquement des variables descriptives du trajet** (`distance_km`, `duration_min`, `is_night`). Aucune variable de cette table ne constitue un signal de fragilité **indépendant** des caractéristiques du trajet lui-même. Il est donc structurellement impossible de construire une cible de classification crédible à partir de cette table seule, sans reproduire un leakage.

### Tableau de synthèse des tentatives

| Tentative | Cible construite | Problème identifié |
|-----------|-----------------|-------------------|
| 1 | `candidate_substitution` (règles distance + durée) | Leakage direct : features = règles |
| 2 | `ligne_fragile` (agrégats pays) | 42 pays → mémorisation |
| 3 | `ligne_fragile` (distance + vitesse) | Leakage indirect via `avg_speed_kmh` |

---

## 6. Correctifs appliqués — Réorientation du sujet

### Audit des données disponibles

Un audit complet du warehouse a révélé que d'autres tables contiennent des données exploitables :

| Source | Données | Pertinence ML |
|--------|---------|---------------|
| `facts_country_stats` | Fréquentation + CO₂ par pays, 2010–2024 | **Très élevée** |
| `facts_night_trains` | 15 538 trajets, distance, durée | Moyenne |
| `passengers_processed` | 1 605 lignes Eurostat | Élevée |

### Nouveau sujet retenu

**Prévision de la fréquentation ferroviaire (régression) + Détection des pays en déclin (classification)**

La table `facts_country_stats` contient une vraie **variation temporelle** : 15 années × 42 pays = 630 observations, avec des variables numériques continues réelles (`passengers`, `co2_emissions`, `co2_per_passenger`) qui ne sont pas des reformulations les unes des autres.

**Axe 1 — Régression**
- Cible : `passengers` (année N)
- Features : `year`, `co2_emissions`, `co2_per_passenger`, `co2_lag1`, `passengers_lag1`, `passengers_lag2`

**Axe 2 — Classification**
- Cible : `en_declin = 1` si `passengers_annee_N < passengers_annee_N-2`
- Features : identiques à la régression, sans `passengers`

### Pourquoi ce sujet est exempt de leakage

La cible `en_declin` est construite en comparant `passengers` de l'année N avec `passengers_lag2` (année N-2). Or, `passengers` de l'année N **n'est pas une feature d'entraînement** dans l'axe classification. Les features `passengers_lag1` et `passengers_lag2` sont des valeurs historiques réelles — le modèle doit apprendre la dynamique temporelle sans accès à la valeur cible.

---

## 7. Impact sur la suite du projet

- **Validité scientifique restaurée** : les modèles entraînés sur le nouveau sujet produisent des métriques différenciées et réalistes.
- **Cohérence avec le cahier des charges** : le nouveau sujet répond directement aux enjeux d'ObRail (*"Anticiper la demande en mobilité ferroviaire"* et *"Évaluer l'impact environnemental futur"*).
- **Comparaison des modèles possible** : des scores imparfaits et différenciés entre modèles permettent une sélection justifiée.
- **Interprétabilité** : les résultats sont directement opérationnels ("le modèle prédit une baisse de fréquentation en Roumanie d'ici 2026").

---

## 8. Livrables produits

| Livrable | Description |
|----------|-------------|
| `docs/incident_data_leakage.md` | Ce rapport |
| `rapport_reorientation_ml.md` | Analyse complète de la réorientation |
| Abandon de `facts_night_trains` comme source ML principale | Décision documentée |
| Adoption de `facts_country_stats` comme source ML | Décision documentée |

---

> **Note pour la soutenance** : cet incident est un argument différenciant fort. Il démontre la capacité de l'équipe à détecter une erreur méthodologique grave, à en comprendre le mécanisme, et à apporter une correction fondée sur une analyse rigoureuse des données disponibles. Préparer 2 à 3 slides dédiés à cet incident est recommandé.
