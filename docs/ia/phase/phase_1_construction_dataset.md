# Phase 1 — Construction des Datasets ML

---

## 1. Contexte

### Objectif de l'étape

Construire deux datasets propres et exploitables à partir du warehouse ObRail Europe, en intégrant un **feature engineering temporel (variables lag)** et en créant les variables cibles des deux axes ML :
- **Axe régression** : prévision du volume de passagers ferroviaires (`passengers`)
- **Axe classification** : détection des pays dont la fréquentation est en déclin (`en_declin`)

### Position dans le projet

Cette phase est la première étape de la chaîne ML, après la résolution de l'incident data leakage (Phase 0). Elle conditionne l'ensemble des étapes suivantes (preprocessing, entraînement, évaluation).

### Lien avec le cahier des charges

Le cahier des charges ObRail demande :
- de **générer des données d'entrée** adaptées au modèle d'apprentissage ;
- d'effectuer les **transformations nécessaires** (feature engineering) ;
- de **construire les ensembles de données** selon les bonnes pratiques.

---

## 2. Travaux réalisés

### Script principal

**`ia/src/ml/build_dataset.py`** — script de construction des deux datasets ML.

### Sources de données utilisées

| Fichier source | Contenu | Lignes |
|---------------|---------|--------|
| `data/warehouse/facts_country_stats.csv` | Fréquentation + CO₂ par pays et par année | 630 |
| `data/warehouse/dim_countries.csv` | Référentiel des pays (id, code, nom) | 48 |
| `data/warehouse/dim_years.csv` | Référentiel des années (id, année) | 16 |

### Étapes de traitement

1. **Chargement des trois sources** via `pd.read_csv()`
2. **Jointure principale** : `facts_country_stats` ← `dim_countries` (sur `country_id`) ← `dim_years` (sur `year_id`)
3. **Tri chronologique** par `country_id` puis `year` pour garantir l'ordre temporel avant le calcul des lags
4. **Feature engineering** : création des variables lag par pays
5. **Construction de la cible classification** `en_declin`
6. **Suppression des lignes sans lag** (années 2010 et 2011 par pays)
7. **Export** des deux datasets finaux en CSV

---

## 3. Fonctionnement

### 3.1 Jointure et tri

```python
df = (stats
      .merge(countries, on='country_id', how='left')
      .merge(years,     on='year_id',    how='left'))
df = df.sort_values(['country_id', 'year']).reset_index(drop=True)
```

Le tri chronologique est indispensable avant le calcul des lags : sans lui, `shift(1)` produirait des valeurs décalées incorrectes.

### 3.2 Variables lag (feature engineering temporel)

```python
df['passengers_lag1'] = df.groupby('country_id')['passengers'].shift(1)
df['passengers_lag2'] = df.groupby('country_id')['passengers'].shift(2)
df['co2_lag1']        = df.groupby('country_id')['co2_emissions'].shift(1)
```

Les lags sont calculés **par groupe de pays** (`groupby('country_id')`), ce qui évite qu'un lag "déborde" d'un pays à l'autre. Ces variables permettent au modèle d'apprendre la **dynamique temporelle** sans accès à la valeur cible de l'année N.

| Variable | Signification |
|----------|--------------|
| `passengers_lag1` | Fréquentation de l'année N-1 |
| `passengers_lag2` | Fréquentation de l'année N-2 |
| `co2_lag1` | Émissions CO₂ de l'année N-1 |

### 3.3 Construction de la cible classification

```python
df['en_declin'] = (df['passengers'] < df['passengers_lag2']).astype(int)
```

La cible vaut **1** si la fréquentation de l'année N est inférieure à celle de l'année N-2, **0** sinon. Elle est construite à partir de données historiques réelles, sans règle arbitraire fondée sur des seuils externes — ce qui garantit l'absence de leakage.

### 3.4 Suppression des NaN

Les années 2010 et 2011 ne disposent pas de valeurs de lag suffisantes (`lag2` nécessite deux années antérieures). Ces lignes sont supprimées :

```python
df_clean = df.dropna(subset=['passengers_lag1', 'passengers_lag2']).copy()
```

**Impact** : 630 − 546 = 84 lignes supprimées (2 années × 42 pays).

---

## 4. Résultats obtenus

### Construction de la base

| Indicateur | Valeur |
|-----------|--------|
| Lignes base complète | 630 |
| Colonnes base complète | 10 |
| Pays couverts | 41 |
| Années couvertes | 2010 → 2024 |
| Lignes après suppression NaN lag | **546** |

### Dataset régression (`regression_dataset.csv`)

| Indicateur | Valeur |
|-----------|--------|
| Shape | (546, 10) |
| Cible | `passengers` |
| Minimum | 0 |
| Maximum | 1 080 000 |
| Médiane | 14 178 |

### Dataset classification (`classification_dataset.csv`)

| Indicateur | Valeur |
|-----------|--------|
| Shape | (546, 10) |
| Cible | `en_declin` (0/1) |
| Classe 0 — En croissance | 338 (61,9 %) |
| Classe 1 — En déclin | 208 (38,1 %) |

### Variables présentes dans les deux datasets

| Variable | Type | Rôle |
|----------|------|------|
| `country_id` | int | Identifiant pays |
| `country_name` | str | Nom du pays (utilisé en OHE) |
| `year` | int | Année (feature temporelle) |
| `year_id` | int | Identifiant année |
| `co2_emissions` | float | Émissions CO₂ totales (année N) |
| `co2_per_passenger` | float | Efficacité carbone (année N) |
| `co2_lag1` | float | Efficacité carbone (année N-1) |
| `passengers_lag1` | float | Fréquentation N-1 |
| `passengers_lag2` | float | Fréquentation N-2 |
| `passengers` | float | **Cible régression** |
| `en_declin` | int | **Cible classification** (0/1) |

---

## 5. Difficultés rencontrées

- **Asymétrie forte de la cible régression** : la valeur `passengers` varie de 0 à 1 080 000 avec une médiane à 14 178, ce qui reflète une distribution très hétérogène entre petits et grands pays ferroviaires. Les modèles de régression devront gérer cette variance importante.
- **Déséquilibre modéré des classes** : 61,9 % / 38,1 % — non négligeable, justifiant l'usage de `class_weight="balanced"` et du F1-score comme métrique principale plutôt que l'accuracy.
- **Perte de données lag** : 84 lignes supprimées (13,3 % du dataset initial) pour les années 2010–2011. Cette perte est inévitable et documentée.

---

## 6. Correctifs appliqués

La résolution de l'incident Phase 0 est le principal correctif de cette étape :
- **Abandon de `facts_night_trains`** comme source ML principale
- **Adoption de `facts_country_stats`** avec variables lag temporelles
- La cible `en_declin` ne dépend d'aucune feature d'entraînement → zéro leakage confirmé

---

## 7. Impact sur la suite du projet

- Les deux datasets sont directement consommables par les scripts d'entraînement (`run_training.py`)
- Les variables lag constituent des features temporelles riches qui permettent aux modèles d'apprendre la dynamique d'évolution de la fréquentation
- Le déséquilibre de classes documenté guide les choix de paramétrage des modèles de classification (notamment `class_weight` et `scale_pos_weight`)
- La distribution asymétrique de `passengers` oriente vers des métriques de régression robustes (MAE, R²)

---

## 8. Livrables produits

| Livrable | Chemin | Description |
|----------|--------|-------------|
| Script de construction | `ia/src/ml/build_dataset.py` | Génère les deux datasets |
| Script de configuration | `ia/src/ml/config.py` | Chemins et constantes |
| Script de pipeline | `ia/src/ml/run_pipeline.py` | Orchestration (STEP 0) |
| Dataset régression | `data/ml/regression_dataset.csv` | 546 lignes, cible `passengers` |
| Dataset classification | `data/ml/classification_dataset.csv` | 546 lignes, cible `en_declin` |

### Commande de lancement

```bash
python run_pipeline.py
```
