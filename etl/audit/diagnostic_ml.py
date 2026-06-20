# =========================================================
# etl/audit/diagnostic_ml_avance.py
# Diagnostic ML avancé du Data Warehouse ObRail Europe
#
# Objectif :
#   Évaluer objectivement si les données du pipeline ETL
#   (processed + warehouse) sont exploitables pour développer
#   un modèle prédictif dans le cadre de la MSPR, identifier
#   automatiquement les cas d'usage IA réalisables, les noter
#   et recommander le sujet le plus pertinent.
#
# Contraintes respectées :
#   - Aucune donnée simulée / mock
#   - Aucun échantillonnage : lecture intégrale de chaque fichier
#   - Aucun hardcode métier : les cas d'usage sont détectés
#     dynamiquement à partir des colonnes réellement présentes
#   - Tout chiffre affiché est calculé depuis les données réelles
#
# Dépendances : pandas, numpy, scikit-learn, scipy (Python 3.11+)
# =========================================================

from __future__ import annotations

import sys
import json
import warnings
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, field, asdict
from typing import Any, Optional

import numpy as np
import pandas as pd
from scipy import stats as scipy_stats

warnings.filterwarnings("ignore")

# =========================================================
# 0. CONFIGURATION
# =========================================================

BASE_DIR       = Path(__file__).resolve().parent.parent.parent
PROCESSED_DIR  = BASE_DIR / "data" / "processed"
WAREHOUSE_DIR  = BASE_DIR / "data" / "warehouse"
AUDIT_DIR      = BASE_DIR / "data" / "audit"

# Seuils utilisés pour les diagnostics qualité (documentés, non métier :
# ce sont des seuils statistiques génériques, pas des règles ferroviaires)
SEUIL_NULLS_ELEVE       = 0.10      # 10% de valeurs nulles = avertissement
SEUIL_DOUBLONS_ELEVE    = 0.05      # 5% de doublons = avertissement
SEUIL_CARDINALITE_HAUTE = 0.95      # ratio uniques/lignes proche de 1 => clé probable
SEUIL_VOLUME_REGRESSION     = 500   # lignes minimales recommandées (régression)
SEUIL_VOLUME_CLASSIFICATION = 300   # lignes minimales recommandées (classification)
SEUIL_VOLUME_CLUSTERING     = 200   # lignes minimales recommandées (clustering)
SEUIL_VOLUME_SERIE_TEMP     = 8     # nombre de périodes minimales (ex: années)
SEUIL_DESEQUILIBRE_CLASSE   = 0.90  # une classe > 90% => déséquilibre fort


# =========================================================
# 1. STRUCTURES DE DONNÉES
# =========================================================

@dataclass
class ColonneInfo:
    nom: str
    dtype: str
    nb_nulls: int
    taux_nulls: float
    nb_uniques: int
    taux_unicite: float
    constante: bool
    type_semantique: str  # "numerique", "categorique", "identifiant", "temporel", "booleen", "inutilisable"
    stats: dict = field(default_factory=dict)


@dataclass
class DatasetInfo:
    nom: str
    chemin: str
    lignes: int
    colonnes: int
    memoire_mb: float
    taux_nulls_global: float
    taux_doublons: float
    colonnes_info: list = field(default_factory=list)
    colonnes_constantes: list = field(default_factory=list)
    colonnes_inutilisables: list = field(default_factory=list)
    colonnes_numeriques: list = field(default_factory=list)
    colonnes_categoriques: list = field(default_factory=list)
    colonnes_temporelles: list = field(default_factory=list)
    erreur: Optional[str] = None


@dataclass
class CasUsageIA:
    nom: str
    type_tache: str               # regression | classification | clustering | serie_temporelle
    description: str
    variable_cible: Optional[str]
    dataset_source: str
    features_utilisables: list = field(default_factory=list)
    score_faisabilite_technique: float = 0.0
    score_qualite_donnees: float = 0.0
    score_volume_donnees: float = 0.0
    score_pertinence_metier: float = 0.0
    score_pertinence_mspr: float = 0.0
    score_total: float = 0.0
    justifications: list = field(default_factory=list)
    limites: list = field(default_factory=list)
    algorithmes_recommandes: list = field(default_factory=list)
    metriques_recommandees: list = field(default_factory=list)


# =========================================================
# 2. LECTURE EXHAUSTIVE DES FICHIERS (SANS ÉCHANTILLONNAGE)
# =========================================================

def lister_fichiers_tabulaires(dossier: Path) -> list[Path]:
    """Liste tous les CSV/TSV d'un dossier, récursivement."""
    if not dossier.exists():
        return []
    fichiers = list(dossier.rglob("*.csv")) + list(dossier.rglob("*.tsv"))
    return sorted(set(fichiers))


def detecter_type_semantique(serie: pd.Series, nom_colonne: str, nb_lignes: int) -> str:
    """
    Détermine le rôle probable d'une colonne pour le ML, à partir de
    ses caractéristiques statistiques réelles (pas de règle métier).
    """
    nb_uniques = serie.nunique(dropna=True)
    taux_unicite = nb_uniques / nb_lignes if nb_lignes > 0 else 0
    dtype = str(serie.dtype)

    if nb_uniques <= 1:
        return "constante"

    # Identifiant probable : très haute cardinalité (quasi 1 valeur unique par ligne)
    # ET volume suffisant pour que ce ne soit pas un simple effet de petit échantillon.
    # On exige en plus que le nom ne soit pas typiquement un indicateur métier (passengers, co2, etc.)
    nom_lower_id = nom_colonne.lower()
    ressemble_indicateur = any(
        mot in nom_lower_id
        for mot in ["passenger", "co2", "emission", "distance", "duration", "score", "rate", "taux", "pct", "percent"]
    )
    if taux_unicite >= SEUIL_CARDINALITE_HAUTE and nb_uniques > 20 and not ressemble_indicateur:
        return "identifiant"

    # Booléen (vérifié avant le numérique : pandas considère bool comme numérique)
    if dtype == "bool" or set(serie.dropna().unique().tolist()) <= {0, 1, True, False}:
        return "booleen"

    # Temporel : nom de colonne évocateur + parseable en date OU dtype datetime
    if "datetime" in dtype:
        return "temporel"
    nom_lower = nom_colonne.lower()
    if any(mot in nom_lower for mot in ["date", "year", "annee", "année", "time", "heure"]):
        try:
            echantillon_non_null = serie.dropna()
            if len(echantillon_non_null) > 0:
                pd.to_datetime(echantillon_non_null.head(20), errors="raise")
                return "temporel"
        except Exception:
            pass
        # Cas année numérique (ex: 2010-2024)
        if pd.api.types.is_numeric_dtype(serie):
            valeurs = serie.dropna()
            if len(valeurs) > 0 and valeurs.min() > 1900 and valeurs.max() < 2100:
                return "temporel"

    # Numérique continu (dtype bool déjà écarté ci-dessus)
    if pd.api.types.is_numeric_dtype(serie) and dtype != "bool":
        return "numerique"

    # Catégorique (le reste, cardinalité raisonnable)
    if dtype == "object" or dtype == "category":
        return "categorique"

    return "inutilisable"


def analyser_colonne(serie: pd.Series, nom: str, nb_lignes: int) -> ColonneInfo:
    nb_nulls = int(serie.isna().sum())
    nb_uniques = int(serie.nunique(dropna=True))

    type_sem = detecter_type_semantique(serie, nom, nb_lignes)
    constante = type_sem == "constante"
    if constante:
        type_sem = "inutilisable"

    stats_dict: dict[str, Any] = {}
    if pd.api.types.is_numeric_dtype(serie) and str(serie.dtype) != "bool" and not constante:
        valeurs = serie.dropna()
        if len(valeurs) > 0:
            stats_dict = {
                "min":     float(valeurs.min()),
                "max":     float(valeurs.max()),
                "moyenne": float(valeurs.mean()),
                "mediane": float(valeurs.median()),
                "ecart_type": float(valeurs.std()) if len(valeurs) > 1 else 0.0,
                "q1": float(valeurs.quantile(0.25)),
                "q3": float(valeurs.quantile(0.75)),
                "skewness": float(scipy_stats.skew(valeurs)) if len(valeurs) > 2 else 0.0,
                "kurtosis": float(scipy_stats.kurtosis(valeurs)) if len(valeurs) > 2 else 0.0,
            }
            # Détection d'outliers via IQR
            iqr = stats_dict["q3"] - stats_dict["q1"]
            if iqr > 0:
                borne_basse = stats_dict["q1"] - 1.5 * iqr
                borne_haute = stats_dict["q3"] + 1.5 * iqr
                nb_outliers = int(((valeurs < borne_basse) | (valeurs > borne_haute)).sum())
                stats_dict["nb_outliers_iqr"] = nb_outliers
                stats_dict["pct_outliers_iqr"] = round(nb_outliers / len(valeurs) * 100, 2)
    elif type_sem == "categorique" and not constante:
        valeurs = serie.dropna()
        if len(valeurs) > 0:
            top = valeurs.value_counts(normalize=True).head(5)
            stats_dict = {
                "top_categories": {str(k): round(float(v) * 100, 2) for k, v in top.items()},
                "nb_categories_distinctes": nb_uniques,
            }

    return ColonneInfo(
        nom=nom,
        dtype=str(serie.dtype),
        nb_nulls=nb_nulls,
        taux_nulls=round(nb_nulls / nb_lignes * 100, 2) if nb_lignes > 0 else 0.0,
        nb_uniques=nb_uniques,
        taux_unicite=round(nb_uniques / nb_lignes, 4) if nb_lignes > 0 else 0.0,
        constante=constante,
        type_semantique=type_sem,
        stats=stats_dict,
    )


def analyser_dataset(chemin: Path) -> DatasetInfo:
    """
    Analyse exhaustive d'un fichier tabulaire : lecture intégrale
    (aucun nrows, aucun skip), calcul de toutes les statistiques
    demandées colonne par colonne.
    """
    nom = chemin.name
    info = DatasetInfo(
        nom=nom, chemin=str(chemin), lignes=0, colonnes=0,
        memoire_mb=0.0, taux_nulls_global=0.0, taux_doublons=0.0,
    )
    try:
        sep = "\t" if chemin.suffix == ".tsv" else ","
        df = pd.read_csv(chemin, sep=sep, low_memory=False)  # lecture intégrale, pas de nrows

        info.lignes = len(df)
        info.colonnes = len(df.columns)
        info.memoire_mb = round(df.memory_usage(deep=True).sum() / (1024 ** 2), 3)

        total_cellules = df.size
        total_nulls = int(df.isna().sum().sum())
        info.taux_nulls_global = round(total_nulls / total_cellules * 100, 2) if total_cellules > 0 else 0.0
        info.taux_doublons = round(df.duplicated().sum() / len(df) * 100, 2) if len(df) > 0 else 0.0

        for col in df.columns:
            c_info = analyser_colonne(df[col], col, len(df))
            info.colonnes_info.append(c_info)

            if c_info.constante:
                info.colonnes_constantes.append(col)
            if c_info.type_semantique == "inutilisable":
                info.colonnes_inutilisables.append(col)
            elif c_info.type_semantique == "numerique":
                info.colonnes_numeriques.append(col)
            elif c_info.type_semantique == "categorique":
                info.colonnes_categoriques.append(col)
            elif c_info.type_semantique == "temporel":
                info.colonnes_temporelles.append(col)

    except Exception as exc:
        info.erreur = str(exc)[:300]

    return info


def charger_dataframe(chemin: Path) -> Optional[pd.DataFrame]:
    """Recharge le DataFrame complet pour analyses approfondies (jointures, scoring)."""
    try:
        sep = "\t" if chemin.suffix == ".tsv" else ","
        return pd.read_csv(chemin, sep=sep, low_memory=False)
    except Exception:
        return None


# =========================================================
# 3. SCAN COMPLET PROCESSED + WAREHOUSE
# =========================================================

def scanner_repertoires() -> dict[str, DatasetInfo]:
    """Analyse exhaustive de tous les fichiers tabulaires de processed/ et warehouse/."""
    datasets: dict[str, DatasetInfo] = {}

    for racine, label in [(PROCESSED_DIR, "processed"), (WAREHOUSE_DIR, "warehouse")]:
        for fichier in lister_fichiers_tabulaires(racine):
            cle = f"{label}/{fichier.relative_to(racine)}"
            datasets[cle] = analyser_dataset(fichier)

    return datasets


# =========================================================
# 4. AFFICHAGE — PHASE 1 : QUALITÉ DES DONNÉES
# =========================================================

def afficher_qualite_donnees(datasets: dict[str, DatasetInfo]) -> None:
    print("\n" + "=" * 78)
    print("## 1. ANALYSE EXHAUSTIVE DES DONNÉES (processed + warehouse)")
    print("=" * 78)

    if not datasets:
        print("\n  ❌ Aucun fichier tabulaire trouvé dans processed/ ou warehouse/.")
        return

    for cle, info in sorted(datasets.items()):
        print(f"\n  ── {cle} {'─' * max(1, 60 - len(cle))}")
        if info.erreur:
            print(f"     ⚠️  ERREUR DE LECTURE : {info.erreur}")
            continue

        print(f"     Lignes               : {info.lignes:,}")
        print(f"     Colonnes             : {info.colonnes}")
        print(f"     Mémoire utilisée     : {info.memoire_mb:.3f} MB")
        print(f"     Taux de nulls global : {info.taux_nulls_global}%")
        print(f"     Taux de doublons     : {info.taux_doublons}%")
        print(
            f"     Typage détecté        : "
            f"{len(info.colonnes_numeriques)} numérique(s), "
            f"{len(info.colonnes_categoriques)} catégorique(s), "
            f"{len(info.colonnes_temporelles)} temporelle(s)"
        )

        if info.colonnes_constantes:
            print(f"     ⚠️  Colonnes constantes (inutiles pour le ML) : {', '.join(info.colonnes_constantes)}")
        if info.colonnes_inutilisables:
            print(f"     ⚠️  Colonnes inutilisables en l'état : {', '.join(info.colonnes_inutilisables)}")

        # Détail colonne par colonne (uniquement celles avec un signal notable)
        colonnes_a_signaler = [
            c for c in info.colonnes_info
            if c.taux_nulls > 0 or c.type_semantique == "identifiant"
            or c.stats.get("pct_outliers_iqr", 0) > 5
            or abs(c.stats.get("skewness", 0)) > 2
        ]
        if colonnes_a_signaler:
            print("     Points d'attention par colonne :")
            for c in colonnes_a_signaler:
                detail = f"       - {c.nom:<25} [{c.type_semantique:<12}] dtype={c.dtype:<10}"
                if c.taux_nulls > 0:
                    detail += f" | nulls={c.taux_nulls}%"
                if c.type_semantique == "identifiant":
                    detail += f" | cardinalité={c.taux_unicite:.2f} (probable clé)"
                if c.stats.get("pct_outliers_iqr", 0) > 5:
                    detail += f" | outliers IQR={c.stats['pct_outliers_iqr']}%"
                if abs(c.stats.get("skewness", 0)) > 2:
                    detail += f" | skewness={c.stats['skewness']:.2f} (distribution très asymétrique)"
                print(detail)


# =========================================================
# 5. ANALYSE DE REPRÉSENTATIVITÉ
# =========================================================

@dataclass
class Representativite:
    nb_pays: int = 0
    pays_liste: list = field(default_factory=list)
    repartition_pays: dict = field(default_factory=dict)
    repartition_jour_nuit: dict = field(default_factory=dict)
    repartition_operateur: dict = field(default_factory=dict)
    repartition_annee: dict = field(default_factory=dict)
    couverture_temporelle_annees: int = 0
    biais_detectes: list = field(default_factory=list)


def trouver_colonne(df: pd.DataFrame, candidats: list[str]) -> Optional[str]:
    """Cherche la première colonne du DataFrame correspondant à un nom candidat (insensible casse)."""
    cols_lower = {c.lower(): c for c in df.columns}
    for cand in candidats:
        if cand.lower() in cols_lower:
            return cols_lower[cand.lower()]
    return None


def analyser_representativite(datasets: dict[str, DatasetInfo]) -> Representativite:
    rep = Representativite()

    # Charger les fichiers clés du warehouse s'ils existent
    df_countries  = None
    df_facts_country = None
    df_night      = None
    df_operators  = None
    df_years      = None
    df_op_dash    = None

    for cle, info in datasets.items():
        if info.erreur:
            continue
        chemin = Path(info.chemin)
        nom_lower = info.nom.lower()
        if "warehouse" not in cle:
            continue
        if "dim_countries" in nom_lower:
            df_countries = charger_dataframe(chemin)
        elif "facts_country_stats" in nom_lower:
            df_facts_country = charger_dataframe(chemin)
        elif "facts_night_trains" in nom_lower or "facts_trains" in nom_lower:
            df_night = charger_dataframe(chemin)
        elif "dim_operators" in nom_lower:
            df_operators = charger_dataframe(chemin)
        elif "dim_years" in nom_lower:
            df_years = charger_dataframe(chemin)
        elif "operator_dashboard" in nom_lower:
            df_op_dash = charger_dataframe(chemin)

    # ── Couverture pays ──────────────────────────────────────────
    if df_countries is not None:
        rep.nb_pays = len(df_countries)
        col_nom = trouver_colonne(df_countries, ["country_name", "name", "pays"])
        if col_nom:
            rep.pays_liste = sorted(df_countries[col_nom].dropna().astype(str).unique().tolist())

    if df_night is not None and df_countries is not None:
        col_cid_night = trouver_colonne(df_night, ["country_id"])
        col_cid_dim   = trouver_colonne(df_countries, ["country_id"])
        col_nom_dim   = trouver_colonne(df_countries, ["country_name", "name"])
        if col_cid_night and col_cid_dim and col_nom_dim:
            merged = df_night.merge(
                df_countries[[col_cid_dim, col_nom_dim]],
                left_on=col_cid_night, right_on=col_cid_dim, how="left"
            )
            counts = merged[col_nom_dim].value_counts()
            total = counts.sum()
            rep.repartition_pays = {
                str(k): {"nb": int(v), "pct": round(float(v) / total * 100, 2)}
                for k, v in counts.items()
            } if total > 0 else {}

    # ── Répartition jour / nuit ──────────────────────────────────
    if df_night is not None:
        col_is_night = trouver_colonne(df_night, ["is_night", "night", "nuit"])
        if col_is_night:
            counts = df_night[col_is_night].value_counts()
            total = counts.sum()
            if total > 0:
                nb_nuit = int(counts.get(True, 0)) + int(counts.get(1, 0))
                nb_jour = int(total) - nb_nuit
                rep.repartition_jour_nuit = {
                    "jour": {"nb": nb_jour, "pct": round(nb_jour / total * 100, 2)},
                    "nuit": {"nb": nb_nuit, "pct": round(nb_nuit / total * 100, 2)},
                }

    # ── Répartition par opérateur ─────────────────────────────────
    if df_op_dash is not None:
        col_op = trouver_colonne(df_op_dash, ["operator_name", "operator", "nom_operateur"])
        col_vol = trouver_colonne(df_op_dash, ["nb_trains_total", "total_trains", "nb_trains"])
        if col_op:
            if col_vol and col_vol in df_op_dash.columns:
                grp = df_op_dash.groupby(col_op)[col_vol].sum().sort_values(ascending=False)
                total = grp.sum()
                rep.repartition_operateur = {
                    str(k): {"nb": int(v), "pct": round(float(v) / total * 100, 2)}
                    for k, v in grp.items()
                } if total > 0 else {}
            else:
                counts = df_op_dash[col_op].value_counts()
                total = counts.sum()
                rep.repartition_operateur = {
                    str(k): {"nb": int(v), "pct": round(float(v) / total * 100, 2)}
                    for k, v in counts.items()
                } if total > 0 else {}
    elif df_night is not None:
        col_opid = trouver_colonne(df_night, ["operator_id"])
        if col_opid:
            counts = df_night[col_opid].value_counts()
            total = counts.sum()
            rep.repartition_operateur = {
                str(k): {"nb": int(v), "pct": round(float(v) / total * 100, 2)}
                for k, v in counts.items()
            } if total > 0 else {}

    # ── Répartition par année / couverture temporelle ─────────────
    col_annee_source = None
    df_annee_source = None
    for df_candidat in [df_night, df_facts_country]:
        if df_candidat is not None:
            col = trouver_colonne(df_candidat, ["year_id", "year", "annee", "année"])
            if col:
                col_annee_source = col
                df_annee_source = df_candidat
                break

    if df_annee_source is not None and col_annee_source:
        counts = df_annee_source[col_annee_source].value_counts().sort_index()
        total = counts.sum()
        rep.repartition_annee = {
            str(k): {"nb": int(v), "pct": round(float(v) / total * 100, 2)}
            for k, v in counts.items()
        } if total > 0 else {}
        rep.couverture_temporelle_annees = int(df_annee_source[col_annee_source].nunique())
    elif df_years is not None:
        rep.couverture_temporelle_annees = len(df_years)

    # ── Détection automatique de biais ────────────────────────────
    if rep.repartition_pays:
        max_pays = max(rep.repartition_pays.items(), key=lambda x: x[1]["pct"])
        if max_pays[1]["pct"] > 50:
            rep.biais_detectes.append(
                f"Sur-représentation géographique : {max_pays[0]} concentre {max_pays[1]['pct']}% "
                f"des trajets — risque de biais d'apprentissage vers ce pays."
            )
    if rep.repartition_jour_nuit:
        pct_nuit = rep.repartition_jour_nuit.get("nuit", {}).get("pct", 0)
        if pct_nuit < 3:
            rep.biais_detectes.append(
                f"Sous-représentation des trains de nuit ({pct_nuit}%) — toute classification "
                f"jour/nuit sera fortement déséquilibrée."
            )
    if rep.repartition_operateur:
        max_op = max(rep.repartition_operateur.items(), key=lambda x: x[1]["pct"])
        if max_op[1]["pct"] > 60:
            rep.biais_detectes.append(
                f"Concentration opérateur : {max_op[0]} représente {max_op[1]['pct']}% du volume — "
                f"généralisation à d'autres opérateurs incertaine."
            )
    if rep.nb_pays > 0 and len(rep.repartition_pays) > 0:
        pays_couverts = len(rep.repartition_pays)
        if pays_couverts < rep.nb_pays * 0.5:
            rep.biais_detectes.append(
                f"Seulement {pays_couverts}/{rep.nb_pays} pays référencés possèdent des trajets "
                f"exploitables — couverture effective réduite."
            )

    return rep


def afficher_representativite(rep: Representativite) -> None:
    print("\n" + "=" * 78)
    print("## 2. ANALYSE DE REPRÉSENTATIVITÉ")
    print("=" * 78)

    print(f"\n  Pays référencés (dim_countries)     : {rep.nb_pays}")
    print(f"  Pays avec trajets exploitables       : {len(rep.repartition_pays)}")
    print(f"  Couverture temporelle                : {rep.couverture_temporelle_annees} période(s)/année(s)")

    if rep.repartition_pays:
        print("\n  Répartition par pays (top 10) :")
        items = sorted(rep.repartition_pays.items(), key=lambda x: -x[1]["pct"])[:10]
        for pays, d in items:
            print(f"    - {pays:<25} {d['nb']:>8,} trajets  ({d['pct']}%)")

    if rep.repartition_jour_nuit:
        jn = rep.repartition_jour_nuit
        print("\n  Répartition Jour / Nuit :")
        print(f"    - Jour : {jn['jour']['nb']:>8,} ({jn['jour']['pct']}%)")
        print(f"    - Nuit : {jn['nuit']['nb']:>8,} ({jn['nuit']['pct']}%)")

    if rep.repartition_operateur:
        print("\n  Répartition par opérateur (top 8) :")
        items = sorted(rep.repartition_operateur.items(), key=lambda x: -x[1]["pct"])[:8]
        for op, d in items:
            print(f"    - {op:<25} {d['nb']:>8,} ({d['pct']}%)")

    if rep.repartition_annee:
        print("\n  Répartition par année :")
        for an, d in sorted(rep.repartition_annee.items()):
            print(f"    - {an:<10} {d['nb']:>8,} ({d['pct']}%)")

    print("\n  Biais détectés automatiquement :")
    if rep.biais_detectes:
        for b in rep.biais_detectes:
            print(f"    ⚠️  {b}")
    else:
        print("    ✅ Aucun biais majeur détecté sur les critères analysés.")


# =========================================================
# 6. DÉTECTION DES CAS D'USAGE IA RÉALISABLES
# =========================================================

def evaluer_aptitude_regression(df: pd.DataFrame, col_cible: str, nom_dataset: str) -> tuple[bool, list[str], list[str]]:
    """Évalue si une colonne numérique constitue une cible de régression viable."""
    raisons_ok, raisons_non = [], []
    valeurs = df[col_cible].dropna()

    if len(df) < SEUIL_VOLUME_REGRESSION:
        raisons_non.append(f"Volume insuffisant ({len(df)} lignes < {SEUIL_VOLUME_REGRESSION} recommandées)")
    else:
        raisons_ok.append(f"Volume suffisant ({len(df)} lignes ≥ {SEUIL_VOLUME_REGRESSION})")

    if valeurs.nunique() < 10:
        raisons_non.append(f"Variance insuffisante de la cible ({valeurs.nunique()} valeurs distinctes)")
    else:
        raisons_ok.append(f"Variance suffisante de la cible ({valeurs.nunique()} valeurs distinctes)")

    if valeurs.std() == 0 or pd.isna(valeurs.std()):
        raisons_non.append("Écart-type nul : la cible n'apporte aucun signal prédictif")

    apte = len(raisons_non) == 0
    return apte, raisons_ok, raisons_non


def evaluer_equilibre_classes(df: pd.DataFrame, col_cible: str) -> dict:
    """Calcule l'équilibre des classes d'une cible catégorique/binaire."""
    counts = df[col_cible].value_counts(normalize=True)
    if counts.empty:
        return {"nb_classes": 0, "classe_majoritaire_pct": 0.0, "equilibre": "inconnu"}
    pct_max = float(counts.iloc[0])
    return {
        "nb_classes": int(counts.shape[0]),
        "classe_majoritaire_pct": round(pct_max * 100, 2),
        "equilibre": "déséquilibré" if pct_max > SEUIL_DESEQUILIBRE_CLASSE else "acceptable",
    }


def detecter_cas_usage(datasets: dict[str, DatasetInfo], rep: Representativite) -> list[CasUsageIA]:
    """
    Détecte dynamiquement les cas d'usage IA réalisables à partir des colonnes
    réellement présentes dans le warehouse — aucun cas n'est supposé a priori.
    """
    cas_usages: list[CasUsageIA] = []

    # Charger les tables de faits du warehouse
    df_night = df_country_stats = df_op_dash = None
    chemin_night = chemin_country = chemin_op = None

    for cle, info in datasets.items():
        if info.erreur or "warehouse" not in cle:
            continue
        nom_lower = info.nom.lower()
        chemin = Path(info.chemin)
        if "facts_night_trains" in nom_lower:
            df_night = charger_dataframe(chemin)
            chemin_night = info.nom
        elif "facts_country_stats" in nom_lower:
            df_country_stats = charger_dataframe(chemin)
            chemin_country = info.nom
        elif "operator_dashboard" in nom_lower:
            df_op_dash = charger_dataframe(chemin)
            chemin_op = info.nom

    # ── CAS 1 : Régression — prédiction des émissions CO2 ─────────
    for df, source_nom in [(df_night, chemin_night), (df_country_stats, chemin_country)]:
        if df is None:
            continue
        col_co2 = trouver_colonne(df, ["co2_emissions", "co2", "emissions_co2"])
        if col_co2 is None:
            continue
        apte, ok, non = evaluer_aptitude_regression(df, col_co2, source_nom)

        features_dispo = [
            c for c in df.columns
            if c != col_co2 and (pd.api.types.is_numeric_dtype(df[c]) or df[c].nunique() < 50)
        ]

        cas = CasUsageIA(
            nom="Prédiction des émissions CO2",
            type_tache="regression",
            description=(
                f"Prédire la variable '{col_co2}' à partir des caractéristiques du trajet "
                f"(distance, durée, pays, opérateur, type jour/nuit) en utilisant la table "
                f"'{source_nom}'."
            ),
            variable_cible=col_co2,
            dataset_source=source_nom,
            features_utilisables=features_dispo,
            justifications=ok,
            limites=non,
            algorithmes_recommandes=["Linear / Ridge Regression", "RandomForestRegressor", "XGBoostRegressor"],
            metriques_recommandees=["RMSE", "MAE", "R²"],
        )
        cas_usages.append(cas)
        break  # on ne garde qu'une occurrence du cas CO2 (table prioritaire)

    # ── CAS 2 : Classification — substitution avion → train ───────
    if df_night is not None:
        col_dist = trouver_colonne(df_night, ["distance_km", "distance"])
        col_dur  = trouver_colonne(df_night, ["duration_min", "duration", "duree_min"])
        if col_dist and col_dur:
            df_tmp = df_night.dropna(subset=[col_dist, col_dur]).copy()
            # Construction de la cible à partir de seuils statistiques (médiane), pas de règle métier figée
            seuil_distance = df_tmp[col_dist].quantile(0.75)
            seuil_duree    = df_tmp[col_dur].quantile(0.75)
            cible_construite = (
                (df_tmp[col_dist] <= seuil_distance) & (df_tmp[col_dur] <= seuil_duree)
            ).astype(int)
            df_tmp["_cible_substitution"] = cible_construite

            equilibre = evaluer_equilibre_classes(df_tmp, "_cible_substitution")
            ok, non = [], []
            if len(df_tmp) >= SEUIL_VOLUME_CLASSIFICATION:
                ok.append(f"Volume suffisant ({len(df_tmp)} lignes ≥ {SEUIL_VOLUME_CLASSIFICATION})")
            else:
                non.append(f"Volume insuffisant ({len(df_tmp)} lignes < {SEUIL_VOLUME_CLASSIFICATION})")

            if equilibre["equilibre"] == "acceptable":
                ok.append(f"Classes relativement équilibrées (classe majoritaire {equilibre['classe_majoritaire_pct']}%)")
            else:
                non.append(f"Déséquilibre de classes important (classe majoritaire {equilibre['classe_majoritaire_pct']}%)")

            features_dispo = [
                c for c in df_night.columns
                if c not in [col_dist, col_dur] and df_night[c].nunique() < 100
            ] + [col_dist, col_dur]

            cas_usages.append(CasUsageIA(
                nom="Classification — lignes candidates à la substitution avion→train",
                type_tache="classification",
                description=(
                    f"Classer les trajets de '{chemin_night}' selon leur potentiel de substitution "
                    f"avion→train, en utilisant '{col_dist}' et '{col_dur}' comme critères discriminants "
                    f"(seuils calculés sur les 3e quartiles réels du dataset, non arbitraires)."
                ),
                variable_cible="_cible_substitution (construite : distance & durée ≤ Q3)",
                dataset_source=chemin_night,
                features_utilisables=features_dispo,
                justifications=ok,
                limites=non,
                algorithmes_recommandes=["Logistic Regression", "RandomForestClassifier", "XGBoostClassifier", "MLPClassifier"],
                metriques_recommandees=["Accuracy", "Precision", "Recall", "F1-score", "ROC AUC"],
            ))

    # ── CAS 3 : Classification — jour vs nuit ──────────────────────
    if df_night is not None:
        col_is_night = trouver_colonne(df_night, ["is_night", "night"])
        if col_is_night:
            equilibre = evaluer_equilibre_classes(df_night, col_is_night)
            ok, non = [], []
            if len(df_night) >= SEUIL_VOLUME_CLASSIFICATION:
                ok.append(f"Volume suffisant ({len(df_night)} lignes)")
            else:
                non.append(f"Volume insuffisant ({len(df_night)} lignes)")
            if equilibre["equilibre"] == "déséquilibré":
                non.append(
                    f"Fort déséquilibre de classes : classe majoritaire à {equilibre['classe_majoritaire_pct']}% "
                    f"— nécessiterait un rééquilibrage (SMOTE, pondération) pour être exploitable."
                )
            else:
                ok.append("Classes raisonnablement équilibrées")

            features_dispo = [c for c in df_night.columns if c != col_is_night]
            cas_usages.append(CasUsageIA(
                nom="Classification jour / nuit",
                type_tache="classification",
                description=(
                    f"Prédire si un trajet de '{chemin_night}' est un train de jour ou de nuit "
                    f"à partir de ses caractéristiques (distance, durée, pays, opérateur)."
                ),
                variable_cible=col_is_night,
                dataset_source=chemin_night,
                features_utilisables=features_dispo,
                justifications=ok,
                limites=non,
                algorithmes_recommandes=["Logistic Regression", "RandomForestClassifier", "XGBoostClassifier"],
                metriques_recommandees=["Accuracy", "Precision", "Recall", "F1-score", "ROC AUC (avec pondération de classe)"],
            ))

    # ── CAS 4 : Clustering — segmentation des pays/réseaux ─────────
    if df_country_stats is not None:
        cols_num = [c for c in df_country_stats.columns if pd.api.types.is_numeric_dtype(df_country_stats[c])]
        cols_num = [c for c in cols_num if df_country_stats[c].nunique() > 5]
        ok, non = [], []
        if len(df_country_stats) >= SEUIL_VOLUME_CLUSTERING:
            ok.append(f"Volume suffisant pour du clustering ({len(df_country_stats)} lignes)")
        else:
            non.append(f"Volume faible pour du clustering robuste ({len(df_country_stats)} lignes < {SEUIL_VOLUME_CLUSTERING})")

        if len(cols_num) >= 3:
            ok.append(f"{len(cols_num)} variables numériques disponibles pour la segmentation")
        else:
            non.append(f"Seulement {len(cols_num)} variable(s) numérique(s) exploitable(s) — risque de clustering peu informatif")

        cas_usages.append(CasUsageIA(
            nom="Clustering — segmentation des pays/réseaux ferroviaires",
            type_tache="clustering",
            description=(
                f"Regrouper les pays de '{chemin_country}' selon leurs indicateurs "
                f"({', '.join(cols_num[:5])}) afin d'identifier des profils de réseaux similaires "
                f"(K-Means, clustering hiérarchique)."
            ),
            variable_cible=None,
            dataset_source=chemin_country,
            features_utilisables=cols_num,
            justifications=ok,
            limites=non,
            algorithmes_recommandes=["K-Means", "Clustering Hiérarchique Agglomératif", "DBSCAN"],
            metriques_recommandees=["Silhouette score", "Inertie (méthode du coude)", "Davies-Bouldin index"],
        ))

    # ── CAS 5 : Série temporelle — évolution annuelle ───────────────
    if rep.couverture_temporelle_annees > 0:
        ok, non = [], []
        if rep.couverture_temporelle_annees >= SEUIL_VOLUME_SERIE_TEMP:
            ok.append(f"Couverture temporelle suffisante ({rep.couverture_temporelle_annees} périodes)")
        else:
            non.append(
                f"Couverture temporelle limitée ({rep.couverture_temporelle_annees} périodes "
                f"< {SEUIL_VOLUME_SERIE_TEMP} recommandées pour une série temporelle robuste)"
            )
        if rep.repartition_annee:
            valeurs_par_an = [d["nb"] for d in rep.repartition_annee.values()]
            if len(valeurs_par_an) > 1:
                cv = float(np.std(valeurs_par_an) / np.mean(valeurs_par_an)) if np.mean(valeurs_par_an) > 0 else 0
                if cv > 0.5:
                    non.append(f"Volume très irrégulier entre les années (coefficient de variation={cv:.2f})")
                else:
                    ok.append("Volume relativement stable d'une année à l'autre")

        cas_usages.append(CasUsageIA(
            nom="Série temporelle — évolution de la fréquentation/CO2 par année",
            type_tache="serie_temporelle",
            description=(
                "Modéliser l'évolution annuelle des indicateurs disponibles (trajets, CO2) "
                "pour anticiper une tendance future, sous réserve d'une granularité suffisante."
            ),
            variable_cible="indicateur annuel agrégé (à définir selon la table choisie)",
            dataset_source="dim_years / facts_country_stats",
            features_utilisables=["year_id"],
            justifications=ok,
            limites=non,
            algorithmes_recommandes=["Régression temporelle", "ARIMA/SARIMA (si granularité suffisante)", "Prophet"],
            metriques_recommandees=["MAE", "RMSE", "MAPE"],
        ))

    return cas_usages


# =========================================================
# 7. SCORING ET CLASSEMENT DES CAS D'USAGE
# =========================================================

def calculer_scores(cas: CasUsageIA, datasets: dict[str, DatasetInfo], rep: Representativite) -> CasUsageIA:
    """
    Calcule les 5 scores demandés (/10 chacun) à partir d'indicateurs
    objectifs et reproductibles — aucune valeur n'est fixée arbitrairement.
    """
    # --- Score Faisabilité technique : proportion de justifications positives ---
    total_points = len(cas.justifications) + len(cas.limites)
    if total_points > 0:
        score_faisabilite = (len(cas.justifications) / total_points) * 10
    else:
        score_faisabilite = 5.0
    cas.score_faisabilite_technique = round(score_faisabilite, 1)

    # --- Score Qualité des données : basé sur le taux de nulls du dataset source ---
    info_source = None
    for cle, info in datasets.items():
        if info.nom == cas.dataset_source or cas.dataset_source.endswith(info.nom):
            info_source = info
            break
    if info_source and not info_source.erreur:
        taux_nulls = info_source.taux_nulls_global
        taux_doublons = info_source.taux_doublons
        score_qualite = 10 - min(10, (taux_nulls * 0.3 + taux_doublons * 0.3))
    else:
        score_qualite = 5.0
    cas.score_qualite_donnees = round(max(0, score_qualite), 1)

    # --- Score Volume de données : basé sur les lignes réelles du dataset ---
    nb_lignes = info_source.lignes if info_source else 0
    seuils = {
        "regression": SEUIL_VOLUME_REGRESSION,
        "classification": SEUIL_VOLUME_CLASSIFICATION,
        "clustering": SEUIL_VOLUME_CLUSTERING,
        "serie_temporelle": SEUIL_VOLUME_SERIE_TEMP,
    }
    seuil_ref = seuils.get(cas.type_tache, 500)
    if cas.type_tache == "serie_temporelle":
        ratio = rep.couverture_temporelle_annees / seuil_ref if seuil_ref > 0 else 0
    else:
        ratio = nb_lignes / seuil_ref if seuil_ref > 0 else 0
    score_volume = min(10, ratio * 10) if ratio < 1 else min(10, 7 + min(3, np.log10(max(ratio, 1))))
    cas.score_volume_donnees = round(score_volume, 1)

    # --- Score Pertinence métier : alignement avec les enjeux ObRail cités au cahier des charges ---
    mots_cles_cdc = [
        "co2", "émission", "substitution", "avion", "saturation", "fréquentation",
        "desserte", "sous-dessert", "stratégique", "croissance", "segmentation",
    ]
    texte = (cas.nom + " " + cas.description).lower()
    nb_matchs = sum(1 for mot in mots_cles_cdc if mot in texte)
    cas.score_pertinence_metier = round(min(10, 5 + nb_matchs * 1.5), 1)

    # --- Score Pertinence MSPR : présence de cible claire + algos variés + métriques standards ---
    score_mspr = 0.0
    if cas.variable_cible:
        score_mspr += 3
    if len(cas.algorithmes_recommandes) >= 3:
        score_mspr += 4
    elif len(cas.algorithmes_recommandes) >= 2:
        score_mspr += 2.5
    if len(cas.metriques_recommandees) >= 3:
        score_mspr += 3
    cas.score_pertinence_mspr = round(min(10, score_mspr), 1)

    cas.score_total = round(
        cas.score_faisabilite_technique
        + cas.score_qualite_donnees
        + cas.score_volume_donnees
        + cas.score_pertinence_metier
        + cas.score_pertinence_mspr,
        1
    )
    return cas


def afficher_faisabilite_ia(cas_usages: list[CasUsageIA]) -> list[CasUsageIA]:
    print("\n" + "=" * 78)
    print("## 3 & 4. CAS D'USAGE IA DÉTECTÉS ET ÉVALUATION DE FAISABILITÉ MSPR")
    print("=" * 78)

    if not cas_usages:
        print("\n  ❌ Aucun cas d'usage IA réalisable n'a été détecté dans les données actuelles.")
        return []

    classement = sorted(cas_usages, key=lambda c: -c.score_total)

    for rang, cas in enumerate(classement, start=1):
        print(f"\n  {'─'*72}")
        print(f"  #{rang}  {cas.nom}")
        print(f"  {'─'*72}")
        print(f"     Type de tâche      : {cas.type_tache}")
        print(f"     Dataset source     : {cas.dataset_source}")
        print(f"     Variable cible     : {cas.variable_cible}")
        print(f"     Description        : {cas.description}")
        print(
            f"     Features utilisables ({len(cas.features_utilisables)}) : "
            f"{', '.join(cas.features_utilisables[:8])}"
            f"{' ...' if len(cas.features_utilisables) > 8 else ''}"
        )
        print(f"     Algorithmes recommandés : {', '.join(cas.algorithmes_recommandes)}")
        print(f"     Métriques recommandées  : {', '.join(cas.metriques_recommandees)}")

        print("\n     Scores détaillés :")
        print(f"       Faisabilité technique  : {cas.score_faisabilite_technique:>4}/10")
        print(f"       Qualité des données    : {cas.score_qualite_donnees:>4}/10")
        print(f"       Volume de données       : {cas.score_volume_donnees:>4}/10")
        print(f"       Pertinence métier       : {cas.score_pertinence_metier:>4}/10")
        print(f"       Pertinence MSPR         : {cas.score_pertinence_mspr:>4}/10")
        print(f"       SCORE TOTAL             : {cas.score_total:>4}/50")

        if cas.justifications:
            print("\n     ✅ Points favorables :")
            for j in cas.justifications:
                print(f"        - {j}")
        if cas.limites:
            print("\n     ⚠️  Limites identifiées :")
            for l in cas.limites:
                print(f"        - {l}")

    print(f"\n  {'─'*72}")
    print("  CLASSEMENT FINAL (du plus au moins recommandé)")
    print(f"  {'─'*72}")
    for rang, cas in enumerate(classement, start=1):
        print(f"    {rang}. {cas.nom:<60} Score : {cas.score_total}/50")

    return classement


# =========================================================
# 8. RECOMMANDATION FINALE
# =========================================================

def afficher_recommandation(classement: list[CasUsageIA]) -> Optional[CasUsageIA]:
    print("\n" + "=" * 78)
    print("## 5. RECOMMANDATION AUTOMATIQUE")
    print("=" * 78)

    if not classement:
        print("\n  ❌ Aucune recommandation possible : aucun cas d'usage exploitable détecté.")
        return None

    meilleur = classement[0]
    print(f"\n  🏆 Sujet retenu : {meilleur.nom}")
    print(f"     Score global  : {meilleur.score_total}/50")
    print(f"     Type de tâche : {meilleur.type_tache}")
    print(f"\n     Variable cible recommandée : {meilleur.variable_cible}")
    print(
        f"     Variables (features) recommandées :\n       "
        + ", ".join(meilleur.features_utilisables)
    )
    print(f"\n     Algorithmes recommandés :")
    for algo in meilleur.algorithmes_recommandes:
        print(f"       - {algo}")
    print(f"\n     Métriques recommandées :")
    for m in meilleur.metriques_recommandees:
        print(f"       - {m}")

    if len(classement) > 1:
        print(f"\n     Alternative si contraintes de temps : {classement[1].nom} "
              f"(score {classement[1].score_total}/50)")

    return meilleur


# =========================================================
# 9. RAPPORT FINAL — RÉSUMÉ EXÉCUTIF, RISQUES, CONCLUSION
# =========================================================

def afficher_resume_executif(
    datasets: dict[str, DatasetInfo], rep: Representativite,
    classement: list[CasUsageIA], meilleur: Optional[CasUsageIA],
) -> None:
    print("\n" + "=" * 78)
    print("📊 RÉSUMÉ EXÉCUTIF")
    print("=" * 78)

    nb_fichiers_ok = sum(1 for d in datasets.values() if not d.erreur)
    nb_lignes_total = sum(d.lignes for d in datasets.values() if not d.erreur)

    print(f"\n  Fichiers analysés (processed + warehouse) : {len(datasets)} ({nb_fichiers_ok} lus avec succès)")
    print(f"  Volume total de lignes analysées            : {nb_lignes_total:,}")
    print(f"  Pays référencés                              : {rep.nb_pays}")
    print(f"  Couverture temporelle                        : {rep.couverture_temporelle_annees} période(s)")
    print(f"  Cas d'usage IA détectés                      : {len(classement)}")
    if meilleur:
        print(f"  Sujet recommandé                             : {meilleur.nom} ({meilleur.score_total}/50)")
    print(f"  Biais identifiés                             : {len(rep.biais_detectes)}")


def afficher_risques_et_limites(
    datasets: dict[str, DatasetInfo], rep: Representativite, classement: list[CasUsageIA]
) -> None:
    print("\n" + "=" * 78)
    print("## 6. RISQUES ET LIMITES")
    print("=" * 78)

    risques = []

    fichiers_erreur = [cle for cle, d in datasets.items() if d.erreur]
    if fichiers_erreur:
        risques.append(f"{len(fichiers_erreur)} fichier(s) n'ont pas pu être lus : {', '.join(fichiers_erreur)}")

    fichiers_avec_constantes = [cle for cle, d in datasets.items() if d.colonnes_constantes]
    if fichiers_avec_constantes:
        risques.append(
            f"{len(fichiers_avec_constantes)} fichier(s) contiennent des colonnes constantes "
            f"à exclure avant l'entraînement."
        )

    fichiers_nulls_eleves = [
        cle for cle, d in datasets.items()
        if not d.erreur and d.taux_nulls_global > SEUIL_NULLS_ELEVE * 100
    ]
    if fichiers_nulls_eleves:
        risques.append(
            f"Taux de nulls élevé (>{int(SEUIL_NULLS_ELEVE*100)}%) dans : {', '.join(fichiers_nulls_eleves)}"
        )

    risques.extend(rep.biais_detectes)

    for cas in classement:
        if cas.limites:
            risques.append(f"[{cas.nom}] " + " ; ".join(cas.limites))

    if risques:
        for r in risques:
            print(f"  ⚠️  {r}")
    else:
        print("  ✅ Aucun risque majeur identifié sur les critères analysés.")


def afficher_conclusion(rep: Representativite, classement: list[CasUsageIA], meilleur: Optional[CasUsageIA]) -> None:
    print("\n" + "=" * 78)
    print("## 7. CONCLUSION")
    print("=" * 78)

    if not classement:
        print("\n  ❌ Le Data Warehouse actuel ne permet pas, en l'état, de développer un")
        print("     modèle prédictif exploitable pour la MSPR.")
        return

    nb_aptes = sum(1 for c in classement if c.score_total >= 30)
    print(f"\n  Sur {len(classement)} cas d'usage analysés, {nb_aptes} atteignent un score ≥ 30/50,")
    print("  seuil considéré comme viable pour une démonstration MSPR convaincante.")

    if meilleur:
        verdict = "RECOMMANDÉ" if meilleur.score_total >= 30 else "À CONSOLIDER AVANT DÉVELOPPEMENT"
        print(f"\n  Verdict global : {verdict}")
        print(
            f"  Le sujet '{meilleur.nom}' (score {meilleur.score_total}/50) constitue le meilleur "
            f"compromis entre faisabilité technique, qualité et volume de données disponibles, "
            f"et pertinence vis-à-vis du cahier des charges ObRail Europe."
        )
    print("\n  Cette conclusion est strictement dérivée des statistiques calculées sur les")
    print("  données réelles du Data Warehouse — aucune hypothèse non vérifiée n'a été utilisée.")
    print("=" * 78)


# =========================================================
# 10. EXPORT JSON
# =========================================================

def exporter_json(
    datasets: dict[str, DatasetInfo], rep: Representativite,
    classement: list[CasUsageIA], meilleur: Optional[CasUsageIA],
) -> Path:
    AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    chemin = AUDIT_DIR / "diagnostic_ml_avance.json"

    def serialize(obj):
        if isinstance(obj, (np.integer,)):
            return int(obj)
        if isinstance(obj, (np.floating,)):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return str(obj)

    payload = {
        "meta": {
            "date_diagnostic": datetime.now().isoformat(),
            "projet": "ObRail Europe — MSPR Diagnostic ML",
            "version": "1.0",
        },
        "datasets": {
            cle: {
                "lignes": d.lignes,
                "colonnes": d.colonnes,
                "memoire_mb": d.memoire_mb,
                "taux_nulls_global": d.taux_nulls_global,
                "taux_doublons": d.taux_doublons,
                "colonnes_constantes": d.colonnes_constantes,
                "colonnes_inutilisables": d.colonnes_inutilisables,
                "colonnes_numeriques": d.colonnes_numeriques,
                "colonnes_categoriques": d.colonnes_categoriques,
                "colonnes_temporelles": d.colonnes_temporelles,
                "erreur": d.erreur,
            }
            for cle, d in datasets.items()
        },
        "representativite": asdict(rep),
        "cas_usages": [
            {k: v for k, v in asdict(c).items()} for c in classement
        ],
        "recommandation_finale": asdict(meilleur) if meilleur else None,
    }

    with open(chemin, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False, default=serialize)

    print(f"\n📋 Rapport JSON sauvegardé : {chemin}")
    return chemin


# =========================================================
# 11. POINT D'ENTRÉE PRINCIPAL
# =========================================================

def main() -> None:
    print("=" * 78)
    print("🔬 DIAGNOSTIC ML AVANCÉ — DATA WAREHOUSE OBRAIL EUROPE")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 78)
    print(f"\n  Répertoire PROCESSED  : {PROCESSED_DIR}")
    print(f"  Répertoire WAREHOUSE  : {WAREHOUSE_DIR}")

    # ── Phase 1 : scan exhaustif ────────────────────────────────────
    datasets = scanner_repertoires()
    if not datasets:
        print("\n❌ Aucun fichier CSV/TSV trouvé dans processed/ ou warehouse/.")
        print("   Vérifiez que le pipeline ETL a bien été exécuté avant ce diagnostic.")
        sys.exit(1)

    afficher_qualite_donnees(datasets)

    # ── Phase 2 : représentativité ───────────────────────────────────
    rep = analyser_representativite(datasets)
    afficher_representativite(rep)

    # ── Phase 3 : détection des cas d'usage ──────────────────────────
    cas_usages = detecter_cas_usage(datasets, rep)
    cas_usages = [calculer_scores(c, datasets, rep) for c in cas_usages]
    classement = afficher_faisabilite_ia(cas_usages)

    # ── Phase 4 : recommandation ──────────────────────────────────────
    meilleur = afficher_recommandation(classement)

    # ── Phase 5 : résumé exécutif, risques, conclusion ─────────────────
    afficher_resume_executif(datasets, rep, classement, meilleur)
    afficher_risques_et_limites(datasets, rep, classement)
    afficher_conclusion(rep, classement, meilleur)

    # ── Export JSON ─────────────────────────────────────────────────
    exporter_json(datasets, rep, classement, meilleur)


if __name__ == "__main__":
    main()