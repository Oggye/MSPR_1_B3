# Rapport de réorientation ML — Projet ObRail Europe

## Contexte

Ce rapport documente les problèmes identifiés lors du développement du modèle de Machine Learning initial, les tentatives de correction successives, et la décision de réorientation vers un sujet adapté aux données réellement disponibles.

---

## 1. Problèmes identifiés

### 1.1 Data leakage structurel — Sujet initial

Le premier sujet retenu était **l'identification automatique des lignes candidates à la substitution avion → train**. La variable cible `candidate_substitution` a été construite à partir de règles métier directement fondées sur les variables utilisées comme features d'entraînement :

```python
# Règle de construction de la cible
if distance_km <= 1200 and duration_min <= 480:
    candidate_substitution = 1
if is_night and distance_km <= 1500 and duration_min <= 720:
    candidate_substitution = 1
```

Les variables `distance_km`, `duration_min` et `is_night` étant simultanément dans les features et dans la règle de construction de la cible, les modèles ont appris une fonction if/else déterministe plutôt qu'une relation statistique réelle. Résultat : tous les modèles ont atteint une accuracy de 1.0, rendant les résultats invalides.

### 1.2 Tentatives de correction et leurs limites

**Tentative 1 — Cible basée sur `passengers` et `co2_per_passenger` par pays**

```python
ligne_fragile = (passengers < médiane) AND (co2_per_passenger > médiane)
```

Problème : `passengers` et `co2_per_passenger` sont des valeurs agrégées au niveau pays. Avec 42 pays, tous les trains d'un même pays héritent de la même cible. Les modèles mémorisent 42 règles pays → scores quasi-parfaits persistants.

**Tentative 2 — Cible basée sur distance et vitesse au niveau train**

```python
signal_distance = distance_km > médiane
signal_speed    = avg_speed_kmh < médiane
ligne_fragile   = (signal_distance + signal_speed + is_night) >= 2
```

Problème : `avg_speed_kmh` est calculé à partir de `distance_km / duration_hours`. Les features `distance_category` et `duration_category` encodaient les mêmes seuils sous forme catégorielle. Les modèles retrouvaient la règle de construction de la cible à travers les features dérivées — leakage indirect.

### 1.3 Limite fondamentale du dataset

Après audit complet, la conclusion est la suivante : la table `facts_night_trains` contient uniquement des variables descriptives du trajet (`distance_km`, `duration_min`, `is_night`). **Aucune variable de cette table ne constitue un signal de fragilité indépendant des caractéristiques du trajet lui-même.** Il est donc structurellement impossible de construire une cible de classification crédible à partir de cette table seule, sans reproduire un leakage.

---

## 2. Analyse des données disponibles

Le diagnostic ETL révèle que le warehouse contient en réalité bien plus que les tables initialement exploitées :

| Source | Données disponibles | Pertinence ML |
|--------|---------------------|---------------|
| `facts_country_stats` | Fréquentation + CO₂ par pays et par année, 2010–2024 | **Très élevée** — série temporelle réelle |
| `facts_night_trains` | 15 538 trajets, distance, durée, type jour/nuit | Moyenne — features contextuelles |
| `passengers_processed` (Eurostat) | 1 605 lignes, fréquentation détaillée | **Élevée** — données officielles |
| `traffic_processed` (Eurostat) | 7 812 lignes, trafic ferroviaire | **Élevée** — indicateurs complémentaires |
| `co2_emissions_processed` | 106 032 lignes, émissions par pays et année | **Élevée** — évolution temporelle CO₂ |

La donnée la plus exploitable pour un modèle ML propre est `facts_country_stats` : elle contient une vraie variation temporelle (15 années × 42 pays = 630 observations), avec des variables numériques continues réelles (`passengers`, `co2_emissions`, `co2_per_passenger`) qui ne sont pas des reformulations les unes des autres.

---

## 3. Nouveau sujet retenu

### Prévision de la fréquentation ferroviaire et identification des pays en déclin

Ce sujet exploite directement la série temporelle disponible dans `facts_country_stats` jointe à `dim_years` et `dim_countries`.

**Axe principal — Régression : prévision de la fréquentation**

Prédire le volume de passagers ferroviaires d'un pays pour une année N à partir des années précédentes et des indicateurs CO₂.

```
Features : year, co2_emissions, co2_per_passenger,
           passengers_lag1 (année N-1), passengers_lag2 (année N-2)
Cible    : passengers (année N)
Modèles  : Ridge, RandomForest Regressor, XGBoost Regressor
Métriques: MAE, RMSE, R²
```

**Axe secondaire — Classification : détection des pays en déclin**

Classer chaque pays-année comme "en croissance" ou "en déclin" selon l'évolution réelle de sa fréquentation.

```
Cible : en_déclin = 1 si passengers_annee_N < passengers_annee_N-2
                   0 sinon
```

Cette cible est construite à partir de données historiques réelles, sans aucune règle arbitraire fondée sur des seuils.

### Pourquoi ce sujet est adapté

- La cible ne dépend d'aucune feature utilisée dans l'entraînement
- Les variables lag introduisent une vraie dépendance temporelle que le modèle doit apprendre
- Les résultats sont interprétables : "le modèle prédit une baisse de fréquentation en Roumanie d'ici 2026"
- Le sujet répond directement aux enjeux d'ObRail formulés dans le cahier des charges : *"Anticiper la demande en mobilité ferroviaire"* et *"Évaluer l'impact environnemental futur"*
- Des scores imparfaits et différenciés entre modèles seront obtenus, permettant une vraie comparaison et une sélection justifiée

---

## 4. Architecture du dataset ML final

```
facts_country_stats
    JOIN dim_countries  ON country_id
    JOIN dim_years      ON year_id
    → Enrichissement temporel (variables lag)
    → Construction de la cible en_déclin

Dataset final :
  - 630 lignes (42 pays × 15 ans)
  - Features : year, country_name, co2_emissions, co2_per_passenger,
               passengers_lag1, passengers_lag2
  - Cible régression  : passengers
  - Cible classification : en_déclin (0/1)
```

---

## 5. Conclusion

Les problèmes rencontrés — data leakage structurel, granularité inadaptée, cibles artificielles — sont la conséquence directe d'un sujet ML initialement défini sans audit préalable de la richesse réelle des données disponibles. Le warehouse ObRail Europe contient des données de fréquentation temporelle exploitables et scientifiquement valides. Le nouveau sujet s'appuie sur ces données pour construire un modèle défendable, aux résultats interprétables et cohérents avec les objectifs métier d'ObRail.