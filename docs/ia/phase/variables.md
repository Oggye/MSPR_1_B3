# Tableau des Variables ML — Projet ObRail Europe

---

## 1. Source des données

Les deux datasets ML sont construits à partir de la jointure :

```
facts_country_stats  ←→  dim_countries  ←→  dim_years
```

Source warehouse : `data/warehouse/facts_country_stats.csv` (630 lignes — 42 pays × 15 ans, 2010–2024)

---

## 2. Tableau des variables

| Variable | Type | Source | Rôle | Présente dans |
|----------|------|--------|------|---------------|
| `country_id` | int | `dim_countries` | Identifiant numérique du pays | Régression + Classification |
| `country_name` | str | `dim_countries` | Nom du pays (encodé OHE) | Régression + Classification |
| `year` | int | `dim_years` | Année de l'observation (feature temporelle) | Régression + Classification |
| `year_id` | int | `dim_years` | Identifiant numérique de l'année | Régression + Classification |
| `co2_emissions` | float | `facts_country_stats` | Émissions CO₂ totales du secteur ferroviaire national (année N) | Régression + Classification |
| `co2_per_passenger` | float | `facts_country_stats` | Efficacité carbone : CO₂ par passager (année N) | Régression + Classification |
| `co2_lag1` | float | Calculé (shift −1) | Efficacité carbone de l'année N-1 | Régression + Classification |
| `passengers_lag1` | float | Calculé (shift −1) | Volume de passagers ferroviaires de l'année N-1 | Régression + Classification |
| `passengers_lag2` | float | Calculé (shift −2) | Volume de passagers ferroviaires de l'année N-2 | Régression + Classification |
| `passengers` | float | `facts_country_stats` | 🎯 **Cible régression** — Volume de passagers (année N) | Régression uniquement |
| `en_declin` | int (0/1) | Calculé | 🎯 **Cible classification** — 1 si `passengers` < `passengers_lag2` | Classification uniquement |

---

## 3. Statistiques descriptives des features numériques

*Issues de l'exécution de `run_pipeline.py`*

| Variable | Minimum | Maximum | Médiane (passagers) |
|----------|---------|---------|---------------------|
| `passengers` (cible régression) | 0 | 1 080 000 | 14 178 |

> Les statistiques complètes (moyenne, écart-type, quartiles) pour toutes les features numériques seront produites dans `notebooks/01_eda.ipynb` (à réaliser — Phase 2).

---

## 4. Distribution de la cible classification

| Classe | Valeur | Effectif | Proportion |
|--------|--------|----------|------------|
| En croissance | 0 | 338 | 61,9 % |
| En déclin | 1 | 208 | 38,1 % |
| **Total** | | **546** | **100 %** |

---

## 5. Preprocessing appliqué

| Variable | Transformation |
|----------|---------------|
| `year` | `StandardScaler()` |
| `co2_emissions` | `StandardScaler()` |
| `co2_per_passenger` | `StandardScaler()` |
| `co2_lag1` | `StandardScaler()` |
| `passengers_lag1` | `StandardScaler()` |
| `passengers_lag2` | `StandardScaler()` |
| `country_name` | `OneHotEncoder()` → 41 colonnes binaires |
| `country_id` | Supprimé (`remainder="drop"`) |
| `year_id` | Supprimé (`remainder="drop"`) |

**Dimension finale après preprocessing** : 47 features (6 numériques + 41 OHE)

---

## 6. Justification du feature engineering

### Variables lag

Les variables `passengers_lag1` et `passengers_lag2` constituent le cœur du feature engineering temporel. Elles permettent :
- d'introduire une **dépendance temporelle** dans le modèle sans utiliser la cible de l'année N
- d'apprendre la **dynamique d'évolution** de la fréquentation (tendance, inertie)
- de détecter les **retournements de tendance** (base de la cible `en_declin`)

### `co2_lag1`

La variable `co2_lag1` complète `co2_per_passenger` (année N) par sa valeur de l'année précédente, permettant au modèle de détecter une évolution de l'efficacité carbone comme signal prédictif.

### `country_name` (OHE)

L'encodage One-Hot du pays permet au modèle de capturer les **effets fixes pays** — chaque pays a une dynamique ferroviaire propre (taille du réseau, politique ferroviaire nationale, densité de population).

---

## 7. Variables exclues et justification

| Variable exclue | Raison |
|----------------|--------|
| `country_id` | Redondant avec `country_name` après OHE |
| `year_id` | Redondant avec `year` (même information, identifiant technique) |
| `passengers` (dans clf) | Serait un leakage direct dans l'axe classification |
| `en_declin` (dans reg) | Non pertinent pour la régression |
