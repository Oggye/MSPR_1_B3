# =========================================================
# etl/audit/diagnostic_complet.py
# Diagnostic avancé du pipeline ETL ObRail Europe
# v2.0 — Analyse complète : RAW, PROCESSED, WAREHOUSE
#         Couverture européenne, pertes, cohérence, jour/nuit
# =========================================================

import pandas as pd
import numpy as np
from pathlib import Path
import sys
import os
from datetime import datetime
import json
import warnings
warnings.filterwarnings('ignore')

# =========================================================
# CONFIGURATION DES CHEMINS
# =========================================================
BASE_DIR = Path(__file__).parent.parent.parent
RAW_DIR      = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"
WAREHOUSE_DIR = BASE_DIR / "data" / "warehouse"
AUDIT_DIR    = BASE_DIR / "data" / "audit"

RAW_SOURCES = {
    "back_on_track": RAW_DIR / "back_on_track",
    "eurostat":      RAW_DIR / "eurostat",
    "emission_co2":  RAW_DIR / "emission_co2",
    "gtfs_fr":       RAW_DIR / "gtfs_fr",
    "gtfs_ch":       RAW_DIR / "gtfs_ch",
    "gtfs_de":       RAW_DIR / "gtfs_de",
}

PROCESSED_SOURCES = {
    "back_on_track": PROCESSED_DIR / "back_on_track",
    "emissions":     PROCESSED_DIR / "emissions",
    "eurostat":      PROCESSED_DIR / "eurostat",
    "gtfs":          PROCESSED_DIR / "gtfs",
}

# Mapping RAW → PROCESSED (pour le calcul des pertes)
RAW_TO_PROCESSED_MAP = {
    "back_on_track": "back_on_track",
    "eurostat":      "eurostat",
    "emission_co2":  "emissions",
    "gtfs_fr":       "gtfs",
    "gtfs_ch":       "gtfs",
    "gtfs_de":       "gtfs",
}

# Pays ferroviaires majeurs de l'UE attendus dans le dataset
PAYS_MAJEURS_EU = [
    "France", "Germany", "Italy", "Spain", "Poland",
    "Netherlands", "Belgium", "Austria", "Switzerland",
    "Czech Republic", "Sweden", "Denmark", "Portugal",
    "Hungary", "Romania", "Slovakia",
]

# =========================================================
# 1. FONCTIONS DE LECTURE / ANALYSE DE FICHIERS
# =========================================================

def compter_lignes_exact(chemin: Path) -> int | None:
    """Compte exactement le nombre de lignes de données (hors en-tête)."""
    try:
        with open(chemin, "r", encoding="utf-8", errors="ignore") as f:
            return max(0, sum(1 for _ in f) - 1)
    except Exception:
        return None


def analyser_fichier(chemin: Path, max_apercu: int = 4) -> dict:
    """
    Analyse complète d'un fichier CSV ou TSV :
      - nombre exact de lignes (lecture ligne à ligne)
      - colonnes, taille, doublons, nulls par colonne
      - aperçu limité à max_apercu lignes
    Les statistiques portent sur 100 % des données.
    """
    info = {
        "nom":             Path(chemin).name,
        "chemin":          str(chemin),
        "lignes":          0,
        "colonnes":        0,
        "colonnes_noms":   [],
        "taille_kb":       0.0,
        "doublons":        0,
        "nulls_par_col":   {},
        "total_nulls":     0,
        "total_valeurs":   0,
        "apercu":          [],
        "erreur":          None,
    }
    try:
        info["taille_kb"] = chemin.stat().st_size / 1024
        info["lignes"]    = compter_lignes_exact(chemin)

        sep = "\t" if chemin.suffix == ".tsv" else ","
        df  = pd.read_csv(chemin, sep=sep, low_memory=False)

        info["colonnes"]      = len(df.columns)
        info["colonnes_noms"] = df.columns.tolist()
        info["doublons"]      = int(df.duplicated().sum())
        info["total_valeurs"] = int(df.size)

        for col in df.columns:
            n = int(df[col].isna().sum())
            if n > 0:
                info["nulls_par_col"][col] = n
        info["total_nulls"] = sum(info["nulls_par_col"].values())

        info["apercu"] = df.head(max_apercu).to_dict(orient="records")

    except Exception as exc:
        info["erreur"] = str(exc)[:250]

    return info


def analyser_dossier(dossier: Path, recursif: bool = True) -> list[dict]:
    """Retourne la liste des analyses pour tous les CSV/TSV d'un dossier."""
    if not dossier.exists():
        return []
    pattern = "**/*.csv" if recursif else "*.csv"
    fichiers = sorted(dossier.glob(pattern))
    # Inclure aussi les .tsv
    if recursif:
        fichiers += sorted(dossier.glob("**/*.tsv"))
    else:
        fichiers += sorted(dossier.glob("*.tsv"))
    return [analyser_fichier(f) for f in fichiers]


def _afficher_fichier(info: dict, indent: str = "   ") -> None:
    if info["erreur"]:
        print(f"{indent}⚠️  {info['nom']:<40} ERREUR : {info['erreur']}")
    else:
        print(
            f"{indent}✅ {info['nom']:<40} "
            f"{info['lignes']:>12,} lignes | "
            f"{info['colonnes']:>3} col | "
            f"{info['taille_kb']:>10.1f} KB"
        )


# =========================================================
# 2. PHASES DE DIAGNOSTIC
# =========================================================

def diagnostiquer_raw() -> dict:
    print("\n" + "=" * 70)
    print("📥 PHASE 1 : DONNÉES BRUTES (RAW) — ANALYSE INTÉGRALE")
    print("=" * 70)

    raw_stats: dict[str, dict] = {}
    total_fichiers = total_lignes = 0

    for source, dossier in RAW_SOURCES.items():
        print(f"\n📁 {source.upper()}")
        if not dossier.exists():
            print(f"   ❌ Dossier introuvable : {dossier}")
            raw_stats[source] = {"fichiers": 0, "lignes": 0, "details": [], "erreur": "Dossier manquant"}
            continue

        fichiers = analyser_dossier(dossier, recursif=False)
        nb_lignes = sum(f["lignes"] for f in fichiers if f["lignes"] is not None)
        raw_stats[source] = {"fichiers": len(fichiers), "lignes": nb_lignes, "details": fichiers}
        total_fichiers += len(fichiers)
        total_lignes   += nb_lignes

        for f in fichiers:
            _afficher_fichier(f)

    print(f"\n📊 TOTAL RAW : {total_fichiers} fichiers | {total_lignes:,} lignes")
    return raw_stats


def diagnostiquer_processed() -> dict:
    print("\n" + "=" * 70)
    print("🔄 PHASE 2 : DONNÉES TRANSFORMÉES (PROCESSED) — ANALYSE INTÉGRALE")
    print("=" * 70)

    processed_stats: dict[str, dict] = {}
    total_fichiers = total_lignes = 0

    for source, dossier in PROCESSED_SOURCES.items():
        if not dossier.exists():
            continue
        print(f"\n📁 {source.upper()}")
        fichiers = analyser_dossier(dossier, recursif=True)
        nb_lignes = sum(f["lignes"] for f in fichiers if f["lignes"] is not None)
        processed_stats[source] = {"fichiers": len(fichiers), "lignes": nb_lignes, "details": fichiers}
        total_fichiers += len(fichiers)
        total_lignes   += nb_lignes

        for f in fichiers:
            _afficher_fichier(f)

    # Fallback : parcourir tout PROCESSED_DIR si les dossiers attendus n'existent pas
    if not processed_stats and PROCESSED_DIR.exists():
        print("\n📁 (parcours générique de PROCESSED_DIR)")
        for sub in sorted(PROCESSED_DIR.iterdir()):
            if not sub.is_dir():
                continue
            fichiers = analyser_dossier(sub, recursif=True)
            if not fichiers:
                continue
            nb_lignes = sum(f["lignes"] for f in fichiers if f["lignes"] is not None)
            processed_stats[sub.name] = {"fichiers": len(fichiers), "lignes": nb_lignes, "details": fichiers}
            total_fichiers += len(fichiers)
            total_lignes   += nb_lignes
            for f in fichiers:
                _afficher_fichier(f)

    print(f"\n📊 TOTAL PROCESSED : {total_fichiers} fichiers | {total_lignes:,} lignes")
    return processed_stats


def diagnostiquer_warehouse() -> dict:
    print("\n" + "=" * 70)
    print("💾 PHASE 3 : DATA WAREHOUSE — ANALYSE INTÉGRALE")
    print("=" * 70)

    warehouse: dict[str, list] = {"dimensions": [], "faits": [], "dashboard": [], "autres": []}

    if not WAREHOUSE_DIR.exists():
        print("   ❌ Dossier warehouse introuvable.")
        return warehouse

    for f in analyser_dossier(WAREHOUSE_DIR, recursif=True):
        nom = f["nom"].lower()
        if nom.startswith("dim_"):
            warehouse["dimensions"].append(f)
        elif nom.startswith("facts_"):
            warehouse["faits"].append(f)
        elif "dashboard" in nom or "operator" in nom:
            warehouse["dashboard"].append(f)
        else:
            warehouse["autres"].append(f)

    categories = [
        ("📐 DIMENSIONS",        warehouse["dimensions"]),
        ("📊 TABLES DE FAITS",   warehouse["faits"]),
        ("📈 DASHBOARD",         warehouse["dashboard"]),
        ("📎 AUTRES",            warehouse["autres"]),
    ]
    total_lignes = 0
    for titre, liste in categories:
        if not liste:
            continue
        print(f"\n{titre}")
        for f in liste:
            total_lignes += f["lignes"] if f["lignes"] else 0
            _afficher_fichier(f)
            if f["apercu"]:
                print(f"      ↳ Aperçu (4 premières lignes) : {f['apercu'][0]}")

    print(f"\n📊 TOTAL WAREHOUSE : {sum(len(v) for v in warehouse.values())} fichiers | {total_lignes:,} lignes")
    return warehouse


# =========================================================
# 3. ANALYSE DES PERTES DE DONNÉES
# =========================================================

def analyser_pertes(raw_stats: dict, processed_stats: dict, warehouse: dict) -> dict:
    """
    Calcule les pertes ligne par ligne entre chaque étape du pipeline.
    Inclut aussi les taux de nulls et de doublons dans les processed.
    """
    pertes = {"raw_to_processed": [], "processed_to_warehouse": {}, "enrichissements": []}

    # ── RAW → PROCESSED ──────────────────────────────────────────────
    sources_traitees = set()
    for raw_src, raw_info in raw_stats.items():
        proc_key = RAW_TO_PROCESSED_MAP.get(raw_src)
        if not proc_key or proc_key in sources_traitees:
            continue
        sources_traitees.add(proc_key)

        lignes_raw  = raw_info.get("lignes", 0) or 0
        lignes_proc = processed_stats.get(proc_key, {}).get("lignes", 0) or 0

        # Totaliser les nulls et doublons de la source processed correspondante
        details_proc = processed_stats.get(proc_key, {}).get("details", [])
        total_nulls     = sum(d.get("total_nulls", 0) for d in details_proc)
        total_doublons  = sum(d.get("doublons", 0)    for d in details_proc)
        total_valeurs   = sum(d.get("total_valeurs", 0) for d in details_proc)

        taux = round(lignes_proc / lignes_raw * 100, 2) if lignes_raw > 0 else 0.0
        taux_nulls = round(total_nulls / total_valeurs * 100, 2) if total_valeurs > 0 else 0.0

        pertes["raw_to_processed"].append({
            "source_raw":            raw_src,
            "source_processed":      proc_key,
            "lignes_raw":            lignes_raw,
            "lignes_processed":      lignes_proc,
            "taux_conservation":     taux,
            "taux_perte":            round(100 - taux, 2),
            "total_nulls_processed": total_nulls,
            "taux_nulls":            taux_nulls,
            "doublons":              total_doublons,
            "statut": (
                "⚠️  Perte forte (>50%)" if taux < 50
                else "✅ Conservation normale"
            ),
        })

    # ── PROCESSED → WAREHOUSE ────────────────────────────────────────
    total_proc = sum(s.get("lignes", 0) or 0 for s in processed_stats.values())
    total_wh   = sum(f.get("lignes", 0) or 0 for cat in warehouse.values() for f in cat)
    taux_glob  = round(total_wh / total_proc * 100, 2) if total_proc > 0 else 0.0

    pertes["processed_to_warehouse"] = {
        "lignes_processed":      total_proc,
        "lignes_warehouse":      total_wh,
        "taux_conservation":     taux_glob,
        "taux_perte":            round(100 - taux_glob, 2),
        "commentaire": (
            "Agrégation / consolidation (réduction attendue)"
            if taux_glob < 80
            else "Bonne conservation des données"
        ),
    }

    # ── Détection d'enrichissements (processed > raw) ────────────────
    for item in pertes["raw_to_processed"]:
        if item["lignes_processed"] > item["lignes_raw"] and item["lignes_raw"] > 0:
            pertes["enrichissements"].append(
                f"{item['source_raw']} → {item['source_processed']} : "
                f"+{item['lignes_processed'] - item['lignes_raw']:,} lignes (enrichissement)"
            )

    return pertes


# =========================================================
# 4. ANALYSE JOUR / NUIT
# =========================================================

def analyser_jour_nuit(warehouse: dict) -> dict:
    """
    Calcule les volumes de trains de jour et de nuit depuis :
      - facts_night_trains (is_night == True  → train de nuit)
      - operator_dashboard (nb_trains_jour / nb_trains_nuit)
    """
    result = {
        "trains_jour": 0,
        "trains_nuit": 0,
        "total": 0,
        "pct_jour": 0.0,
        "pct_nuit": 0.0,
        "ratio_jour_nuit": None,
        "source": "non déterminé",
    }

    # Priorité 1 : operator_dashboard (contient déjà nb_trains_jour / nb_trains_nuit)
    for f in warehouse.get("dashboard", []):
        if "operator_dashboard" in f["nom"].lower() and not f["erreur"]:
            try:
                df = pd.read_csv(f["chemin"])
                if "nb_trains_jour" in df.columns and "nb_trains_nuit" in df.columns:
                    result["trains_jour"] = int(df["nb_trains_jour"].sum())
                    result["trains_nuit"] = int(df["nb_trains_nuit"].sum())
                    result["source"] = "operator_dashboard"
            except Exception:
                pass

    # Priorité 2 : facts_night_trains si le dashboard ne couvre pas les trains de jour
    if result["trains_jour"] == 0:
        for f in warehouse.get("faits", []):
            if "facts_night_trains" in f["nom"].lower() and not f["erreur"]:
                try:
                    df = pd.read_csv(f["chemin"])
                    if "is_night" in df.columns:
                        result["trains_nuit"] = int(df[df["is_night"] == True].shape[0])
                        result["trains_jour"] = int(df[df["is_night"] == False].shape[0])
                        result["source"] = "facts_night_trains"
                except Exception:
                    pass

    result["total"] = result["trains_jour"] + result["trains_nuit"]
    if result["total"] > 0:
        result["pct_jour"] = round(result["trains_jour"] / result["total"] * 100, 2)
        result["pct_nuit"] = round(result["trains_nuit"] / result["total"] * 100, 2)
        if result["trains_nuit"] > 0:
            result["ratio_jour_nuit"] = round(result["trains_jour"] / result["trains_nuit"], 2)
        else:
            result["ratio_jour_nuit"] = float("inf")

    return result


# =========================================================
# 5. ANALYSE DE LA COUVERTURE GÉOGRAPHIQUE
# =========================================================

def analyser_couverture_pays(warehouse: dict) -> list[dict]:
    """
    Construit le tableau de couverture par pays depuis dashboard_metrics.
    Tente une jointure avec dim_countries si disponible.
    """
    couverture = []

    # Charger dashboard_metrics
    df_metrics = None
    for f in warehouse.get("dashboard", []):
        if "dashboard_metrics" in f["nom"].lower() and not f["erreur"]:
            try:
                df_metrics = pd.read_csv(f["chemin"])
            except Exception:
                pass

    if df_metrics is None:
        # Fallback : facts_country_stats + dim_countries
        df_facts = df_dim = None
        for f in warehouse.get("faits", []):
            if "facts_country_stats" in f["nom"].lower() and not f["erreur"]:
                try:
                    df_facts = pd.read_csv(f["chemin"])
                except Exception:
                    pass
        for f in warehouse.get("dimensions", []):
            if "dim_countries" in f["nom"].lower() and not f["erreur"]:
                try:
                    df_dim = pd.read_csv(f["chemin"])
                except Exception:
                    pass

        if df_facts is not None and df_dim is not None:
            # Agréger par pays
            agg = df_facts.groupby("country_id").agg(
                passengers=("passengers", "mean"),
                co2_emissions=("co2_emissions", "mean"),
                co2_per_passenger=("co2_per_passenger", "mean"),
            ).reset_index()
            df_metrics = agg.merge(df_dim, on="country_id", how="left")

    if df_metrics is None:
        return couverture

    # Construire la liste de couverture
    total_passagers = df_metrics["passengers"].sum() if "passengers" in df_metrics.columns else 1

    for _, row in df_metrics.iterrows():
        passagers = float(row.get("passengers", 0) or 0)
        pct = round(passagers / total_passagers * 100, 2) if total_passagers > 0 else 0.0
        couverture.append({
            "country_name":       str(row.get("country_name", "?")),
            "country_code":       str(row.get("country_code", "?")),
            "passengers":         passagers,
            "co2_emissions":      float(row.get("co2_emissions", 0) or 0),
            "co2_per_passenger":  float(row.get("co2_per_passenger", 0) or 0),
            "pct_dataset":        pct,
        })

    couverture.sort(key=lambda x: x["passengers"], reverse=True)
    return couverture


def analyser_trains_par_pays(warehouse: dict) -> dict:
    """
    Retourne le nombre de trains de nuit ET de jour par pays (country_id → nb),
    en résolvant les noms de pays via dim_countries.
    Source : facts_night_trains (is_night True/False) + dim_countries.
    """
    resultat = {}  # country_id -> {"nuit": int, "jour": int, "country_name": str, "country_code": str}

    # Charger dim_countries pour avoir les noms
    df_dim = None
    for f in warehouse.get("dimensions", []):
        if "dim_countries" in f["nom"].lower() and not f["erreur"]:
            try:
                df_dim = pd.read_csv(f["chemin"])
            except Exception:
                pass

    id_to_name = {}
    id_to_code = {}
    if df_dim is not None:
        for _, row in df_dim.iterrows():
            cid = row.get("country_id")
            id_to_name[cid] = str(row.get("country_name", "?"))
            id_to_code[cid] = str(row.get("country_code", "?"))

    # Lire facts_night_trains pour les trains de nuit et les trains "non nuit"
    for f in warehouse.get("faits", []):
        if "facts_night_trains" not in f["nom"].lower() or f["erreur"]:
            continue
        try:
            df = pd.read_csv(f["chemin"])
            if "country_id" not in df.columns or "is_night" not in df.columns:
                continue
            for cid, grp in df.groupby("country_id"):
                nuit = int((grp["is_night"] == True).sum())
                jour = int((grp["is_night"] == False).sum())
                resultat[cid] = {
                    "nuit":         nuit,
                    "jour":         jour,
                    "country_name": id_to_name.get(cid, f"country_id={cid}"),
                    "country_code": id_to_code.get(cid, "?"),
                }
        except Exception:
            pass

    return resultat


def analyser_repartition_pays_gtfs() -> dict:
    """
    Compte les trains de jour par pays d'origine GTFS en lisant
    les trips_processed.csv depuis leur dossier pays parent (fr / ch / de).
    Retourne : {"FR": nb, "CH": nb, "DE": nb, ...}

    IMPORTANT : les trips_processed peuvent être limités (ex: 10 000 lignes cap).
    On signale aussi les trips RAW pour détecter la troncature.
    """
    gtfs_dir = PROCESSED_DIR / "gtfs"
    if not gtfs_dir.exists():
        return {}

    pays_trips: dict[str, dict] = {}

    # Chercher les trips_processed.csv dans les sous-dossiers pays
    for trips_file in sorted(gtfs_dir.rglob("trips_processed.csv")):
        # Le dossier parent doit être le code pays (fr, ch, de...)
        parent = trips_file.parent.name.upper()
        if len(parent) > 3:
            # Si le fichier est directement dans gtfs/ sans sous-dossier pays,
            # on essaie d'inférer depuis le chemin
            parent = "INCONNU"

        try:
            nb_lignes = compter_lignes_exact(trips_file)
            if parent not in pays_trips:
                pays_trips[parent] = {"trips_processed": 0, "fichiers": []}
            pays_trips[parent]["trips_processed"] += nb_lignes or 0
            pays_trips[parent]["fichiers"].append(str(trips_file))
        except Exception:
            pass

    # Comparer avec le RAW pour détecter la troncature
    raw_trips = {
        "FR": 0, "CH": 0, "DE": 0,
    }
    for src_name, src_dir in RAW_SOURCES.items():
        if not src_dir.exists():
            continue
        code = src_name.replace("gtfs_", "").upper()
        for f in src_dir.glob("trips.csv"):
            nb = compter_lignes_exact(f)
            if nb:
                raw_trips[code] = raw_trips.get(code, 0) + nb

    for code, raw_nb in raw_trips.items():
        if code in pays_trips:
            pays_trips[code]["trips_raw"] = raw_nb
            proc_nb = pays_trips[code]["trips_processed"]
            if raw_nb > 0:
                pays_trips[code]["taux_conservation"] = round(proc_nb / raw_nb * 100, 1)
                pays_trips[code]["tronque"] = proc_nb < raw_nb * 0.95
            else:
                pays_trips[code]["taux_conservation"] = 100.0
                pays_trips[code]["tronque"] = False
        else:
            pays_trips[code] = {
                "trips_processed": 0,
                "trips_raw": raw_nb,
                "taux_conservation": 0.0,
                "tronque": raw_nb > 0,
                "fichiers": [],
            }

    return pays_trips


# =========================================================
# 6. CONTRÔLES DE COHÉRENCE
# =========================================================

def controle_coherence(warehouse: dict) -> dict:
    """
    Vérifie :
    - Distances et durées positives
    - Vitesses réalistes (< 360 km/h pour les trains à grande vitesse)
    - Nulls dans les clés étrangères
    - Doublons dans les dimensions
    - Cohérence des coordonnées géographiques
    """
    rapport = {"erreurs": [], "avertissements": [], "ok": []}

    # ── facts_night_trains ──────────────────────────────────────────
    for f in warehouse.get("faits", []):
        if "facts_night_trains" not in f["nom"].lower() or f["erreur"]:
            continue
        try:
            df = pd.read_csv(f["chemin"])

            # Distances nulles ou négatives
            if "distance_km" in df.columns:
                nb_zero = int((df["distance_km"] <= 0).sum())
                if nb_zero > 0:
                    pct = round(nb_zero / len(df) * 100, 1)
                    rapport["avertissements"].append(
                        f"facts_night_trains : {nb_zero:,} trajets avec distance_km ≤ 0 ({pct}%)"
                    )

            # Durées nulles ou négatives
            if "duration_min" in df.columns:
                nb_zero_d = int((df["duration_min"] <= 0).sum())
                if nb_zero_d > 0:
                    rapport["avertissements"].append(
                        f"facts_night_trains : {nb_zero_d:,} trajets avec duration_min ≤ 0"
                    )

            # Vitesses réalistes
            if "distance_km" in df.columns and "duration_min" in df.columns:
                df_v = df[(df["distance_km"] > 0) & (df["duration_min"] > 0)].copy()
                df_v["vitesse"] = df_v["distance_km"] / (df_v["duration_min"] / 60)
                v_max = df_v["vitesse"].max()
                v_med = df_v["vitesse"].median()
                nb_anormal = int((df_v["vitesse"] > 360).sum())
                if nb_anormal > 0:
                    rapport["erreurs"].append(
                        f"facts_night_trains : {nb_anormal} trajets avec vitesse > 360 km/h (max={v_max:.1f})"
                    )
                elif v_max > 0:
                    rapport["ok"].append(
                        f"Vitesses OK (médiane={v_med:.1f} km/h, max={v_max:.1f} km/h)"
                    )

            # Clés étrangères nulles
            for col in ["country_id", "year_id", "operator_id"]:
                if col in df.columns:
                    nb_null = int(df[col].isna().sum())
                    if nb_null > 0:
                        rapport["erreurs"].append(
                            f"facts_night_trains.{col} : {nb_null:,} valeurs nulles (clé étrangère invalide)"
                        )
                    else:
                        rapport["ok"].append(f"facts_night_trains.{col} : aucune valeur nulle ✓")

        except Exception as exc:
            rapport["erreurs"].append(f"Erreur lecture facts_night_trains : {exc}")

    # ── Dimensions ──────────────────────────────────────────────────
    for f in warehouse.get("dimensions", []):
        if f["erreur"]:
            continue
        if f["doublons"] > 0:
            rapport["avertissements"].append(
                f"{f['nom']} : {f['doublons']:,} lignes dupliquées"
            )
        else:
            rapport["ok"].append(f"{f['nom']} : aucun doublon ✓")

        # Coordonnées géographiques (dim_stops)
        if "dim_stops" in f["nom"].lower():
            try:
                df = pd.read_csv(f["chemin"])
                if "stop_lat" in df.columns and "stop_lon" in df.columns:
                    hors_europe = df[
                        (df["stop_lat"] < 35) | (df["stop_lat"] > 72) |
                        (df["stop_lon"] < -25) | (df["stop_lon"] > 50)
                    ]
                    if not hors_europe.empty:
                        rapport["avertissements"].append(
                            f"dim_stops : {len(hors_europe):,} arrêts aux coordonnées hors Europe"
                        )
                    else:
                        rapport["ok"].append("dim_stops : coordonnées géographiques cohérentes ✓")
            except Exception:
                pass

    # ── Dashboard / operator ────────────────────────────────────────
    for f in warehouse.get("dashboard", []):
        if "operator_dashboard" in f["nom"].lower() and not f["erreur"]:
            try:
                df = pd.read_csv(f["chemin"])
                if "nb_trains_jour" in df.columns and "nb_trains_nuit" in df.columns:
                    incoh = df[(df["nb_trains_jour"] < 0) | (df["nb_trains_nuit"] < 0)]
                    if not incoh.empty:
                        rapport["erreurs"].append(
                            f"operator_dashboard : {len(incoh)} opérateurs avec nb_trains négatif"
                        )
                    else:
                        rapport["ok"].append("operator_dashboard : volumes cohérents ✓")
            except Exception:
                pass

    return rapport


# =========================================================
# 7. COMPARAISON AVEC LA RÉALITÉ EUROPÉENNE
# =========================================================

def evaluer_representativite(couverture: list[dict], jour_nuit: dict) -> dict:
    """Donne un avis qualitatif sur la représentativité du dataset."""
    pays_presents = {p["country_name"] for p in couverture}
    manquants  = [p for p in PAYS_MAJEURS_EU if p not in pays_presents]
    presents   = [p for p in PAYS_MAJEURS_EU if p in pays_presents]

    bilan = {
        "pays_majeurs_presents": presents,
        "pays_majeurs_absents":  manquants,
        "couverture_pct": round(len(presents) / len(PAYS_MAJEURS_EU) * 100, 1),
        "commentaires": [],
        "alertes": [],
    }

    if manquants:
        bilan["alertes"].append(
            f"Pays ferroviaires majeurs absents : {', '.join(manquants)}"
        )
    else:
        bilan["commentaires"].append("Tous les grands pays ferroviaires sont représentés.")

    pct_nuit = jour_nuit.get("pct_nuit", 0)
    if pct_nuit == 0:
        bilan["alertes"].append("Aucun train de nuit détecté — données incomplètes ?")
    elif pct_nuit < 5:
        bilan["alertes"].append(
            f"Proportion trains de nuit très faible ({pct_nuit}%) — peut sous-représenter "
            "les réseaux EuroNight / ÖBB NightJet."
        )
    elif pct_nuit > 30:
        bilan["alertes"].append(
            f"Proportion trains de nuit élevée ({pct_nuit}%) — possible surreprésentation."
        )
    else:
        bilan["commentaires"].append(
            f"Proportion nuit/jour cohérente ({pct_nuit}% de nuit) avec les tendances EU."
        )

    # Équilibre Ouest / Centre / Nord
    ouest   = {"France", "Belgium", "Netherlands", "Spain", "Portugal"}
    centre  = {"Germany", "Austria", "Switzerland", "Czech Republic", "Slovakia", "Hungary"}
    nord    = {"Sweden", "Denmark", "Poland", "Romania"}
    prs     = pays_presents

    nb_ouest  = len(prs & ouest)
    nb_centre = len(prs & centre)
    nb_nord   = len(prs & nord)

    bilan["commentaires"].append(
        f"Répartition régionale — Ouest : {nb_ouest}/{len(ouest)}, "
        f"Centre : {nb_centre}/{len(centre)}, Nord/Est : {nb_nord}/{len(nord)}"
    )

    return bilan


# =========================================================
# 8. RAPPORT CONSOLE
# =========================================================

def afficher_rapport(
    raw_stats, processed_stats, warehouse,
    pertes, jour_nuit, couverture, trains_nuit_pays, repartition_gtfs,
    coherence, representativite,
):
    SEP = "=" * 70

    # ── Résumé exécutif ────────────────────────────────────────────
    print(f"\n{SEP}")
    print("📊 RAPPORT FINAL — DIAGNOSTIC OBRAIL EUROPE")
    print(SEP)
    print("\n## 1. RÉSUMÉ EXÉCUTIF\n")

    total_raw  = sum(s.get("lignes", 0) or 0 for s in raw_stats.values())
    total_proc = sum(s.get("lignes", 0) or 0 for s in processed_stats.values())
    total_wh   = sum(f.get("lignes", 0) or 0 for cat in warehouse.values() for f in cat)
    nb_pays    = len(couverture)

    print(f"  Fichiers RAW analysés      : {sum(s.get('fichiers',0) for s in raw_stats.values())}")
    print(f"  Fichiers PROCESSED         : {sum(s.get('fichiers',0) for s in processed_stats.values())}")
    print(f"  Fichiers WAREHOUSE         : {sum(len(v) for v in warehouse.values())}")
    print(f"  Lignes RAW                 : {total_raw:>15,}")
    print(f"  Lignes PROCESSED           : {total_proc:>15,}")
    print(f"  Lignes WAREHOUSE           : {total_wh:>15,}")
    print(f"  Trains identifiés          : {jour_nuit['total']:>15,}")
    print(f"    dont trains de nuit      : {jour_nuit['trains_nuit']:>15,} ({jour_nuit['pct_nuit']}%)")
    print(f"    dont trains de jour      : {jour_nuit['trains_jour']:>15,} ({jour_nuit['pct_jour']}%)")
    print(f"  Pays couverts              : {nb_pays}")
    taux_global = pertes["processed_to_warehouse"].get("taux_conservation", 0)
    print(f"  Conservation proc→wh       : {taux_global}%")
    nb_err  = len(coherence["erreurs"])
    nb_warn = len(coherence["avertissements"])
    print(f"  Anomalies détectées        : {nb_err} erreur(s), {nb_warn} avertissement(s)")

    # ── Couverture géographique ────────────────────────────────────
    print(f"\n{'─'*70}")
    print("## 2. COUVERTURE GÉOGRAPHIQUE\n")
    if couverture:
        en_tete = f"{'Pays':<28} {'Passagers':>14} {'CO2 (t)':>14} {'CO2/pass':>10} {'% dataset':>10}"
        print(en_tete)
        print("─" * len(en_tete))
        for p in couverture[:20]:
            print(
                f"  {p['country_name']:<26} "
                f"{p['passengers']:>14,.1f} "
                f"{p['co2_emissions']:>14,.0f} "
                f"{p['co2_per_passenger']:>10.4f} "
                f"{p['pct_dataset']:>9.1f}%"
            )
    else:
        print("  Aucune donnée de couverture pays disponible.")

    manquants = representativite.get("pays_majeurs_absents", [])
    if manquants:
        print(f"\n  ⚠️  Pays majeurs absents : {', '.join(manquants)}")
    print(f"  Couverture pays majeurs : {representativite['couverture_pct']}%")

    # ── Analyse jour / nuit ────────────────────────────────────────
    print(f"\n{'─'*70}")
    print("## 3. ANALYSE JOUR / NUIT\n")
    print(f"  Source utilisée   : {jour_nuit['source']}")
    print(f"  Trains de jour    : {jour_nuit['trains_jour']:>10,}  ({jour_nuit['pct_jour']}%)")
    print(f"  Trains de nuit    : {jour_nuit['trains_nuit']:>10,}  ({jour_nuit['pct_nuit']}%)")
    print(f"  Total             : {jour_nuit['total']:>10,}")
    ratio = jour_nuit.get("ratio_jour_nuit")
    print(f"  Ratio jour/nuit   : {ratio if ratio != float('inf') else '∞ (pas de trains de nuit)'}")

    # ── Tableau jour/nuit par pays (depuis facts_night_trains) ─────
    if trains_nuit_pays:
        total_j = sum(p["jour"] for p in trains_nuit_pays.values())
        total_n = sum(p["nuit"] for p in trains_nuit_pays.values())
        total_t = total_j + total_n

        print(f"\n  {'─'*72}")
        print("  Répartition des trains PAR PAYS (source : facts_night_trains)\n")
        hdr = (
            f"  {'Pays':<28} {'Jour':>8} {'%Jour':>7} "
            f"{'Nuit':>8} {'%Nuit':>7} {'Total':>8} {'%Dataset':>9}"
        )
        print(hdr)
        print(f"  {'─'*72}")

        lignes_pays = sorted(
            trains_nuit_pays.values(),
            key=lambda x: x["jour"] + x["nuit"],
            reverse=True,
        )
        for p in lignes_pays:
            tot = p["jour"] + p["nuit"]
            pct_j  = round(p["jour"] / total_j  * 100, 1) if total_j  > 0 else 0.0
            pct_n  = round(p["nuit"] / total_n  * 100, 1) if total_n  > 0 else 0.0
            pct_ds = round(tot       / total_t   * 100, 1) if total_t  > 0 else 0.0
            nom = p["country_name"][:26]
            print(
                f"  {nom:<28} {p['jour']:>8,} {pct_j:>6.1f}% "
                f"{p['nuit']:>8,} {pct_n:>6.1f}% {tot:>8,} {pct_ds:>8.1f}%"
            )

        print(f"  {'─'*72}")
        print(
            f"  {'TOTAL':<28} {total_j:>8,} {'100%':>7} "
            f"{total_n:>8,} {'100%':>7} {total_t:>8,} {'100%':>9}"
        )

        # Alerte si un pays monopolise les trains de jour
        if total_j > 0:
            dominant_jour = max(trains_nuit_pays.values(), key=lambda x: x["jour"])
            pct_dom = round(dominant_jour["jour"] / total_j * 100, 1)
            if pct_dom > 70:
                print(
                    f"\n  ⚠️  BIAIS DÉTECTÉ : {dominant_jour['country_name']} représente "
                    f"{pct_dom}% de tous les trains de JOUR du dataset.\n"
                    f"     Cause probable : les trips_processed.csv des autres pays sont\n"
                    f"     tronqués ou non intégrés dans facts_night_trains."
                )

    # ── Tableau GTFS : trips par pays + détection de troncature ───
    if repartition_gtfs:
        print(f"\n  {'─'*72}")
        print("  Trips GTFS par pays (trains de jour — vérification troncature)\n")
        hdr2 = f"  {'Pays':>6} {'Trips RAW':>14} {'Trips PROCESSED':>16} {'Conservation':>14} {'Tronqué ?':>11}"
        print(hdr2)
        print(f"  {'─'*72}")
        total_raw_gtfs  = sum(v.get("trips_raw", 0) for v in repartition_gtfs.values())
        total_proc_gtfs = sum(v.get("trips_processed", 0) for v in repartition_gtfs.values())
        for code, info in sorted(repartition_gtfs.items()):
            r_raw  = info.get("trips_raw", 0)
            r_proc = info.get("trips_processed", 0)
            taux   = info.get("taux_conservation", 0.0)
            tronq  = "⚠️  OUI" if info.get("tronque") else "✅ NON"
            pct_r  = round(r_raw  / total_raw_gtfs  * 100, 1) if total_raw_gtfs  > 0 else 0
            pct_p  = round(r_proc / total_proc_gtfs * 100, 1) if total_proc_gtfs > 0 else 0
            print(
                f"  {code:>6}  {r_raw:>10,} ({pct_r:>4.1f}%)  "
                f"{r_proc:>10,} ({pct_p:>4.1f}%)  "
                f"{taux:>10.1f}%  {tronq:>11}"
            )
        print(f"  {'─'*72}")
        print(
            f"  {'TOTAL':>6}  {total_raw_gtfs:>10,} (100%)  "
            f"{total_proc_gtfs:>10,} (100%)"
        )
        if any(v.get("tronque") for v in repartition_gtfs.values()):
            print(
                "\n  ⚠️  Des trips_processed.csv sont tronqués par rapport au RAW.\n"
                "     Cela explique la sur-représentation de certains pays dans les trains de jour.\n"
                "     Action requise : supprimer les caps (nrows=10000) dans le script ETL GTFS."
            )

    # ── Pertes de données ──────────────────────────────────────────
    print(f"\n{'─'*70}")
    print("## 4. ANALYSE DES PERTES\n")
    print("  ### RAW → PROCESSED")
    for p in pertes["raw_to_processed"]:
        print(
            f"  {p['source_raw']:<20} → {p['source_processed']:<18} | "
            f"RAW {p['lignes_raw']:>10,} | PROC {p['lignes_processed']:>10,} | "
            f"Conservation {p['taux_conservation']:>5.1f}% | "
            f"Nulls {p['taux_nulls']:>5.1f}% | "
            f"{p['statut']}"
        )
    if pertes["enrichissements"]:
        print("\n  Enrichissements détectés :")
        for e in pertes["enrichissements"]:
            print(f"    ➕ {e}")

    print("\n  ### PROCESSED → WAREHOUSE")
    p2w = pertes["processed_to_warehouse"]
    print(
        f"  PROCESSED {p2w['lignes_processed']:>12,} → WAREHOUSE {p2w['lignes_warehouse']:>12,} | "
        f"Conservation {p2w['taux_conservation']:>5.1f}% | {p2w['commentaire']}"
    )

    # ── Contrôles de cohérence ────────────────────────────────────
    print(f"\n{'─'*70}")
    print("## 5. CONTRÔLES DE COHÉRENCE\n")
    if coherence["erreurs"]:
        print("  ❌ ERREURS :")
        for e in coherence["erreurs"]:
            print(f"    - {e}")
    if coherence["avertissements"]:
        print("  ⚠️  AVERTISSEMENTS :")
        for w in coherence["avertissements"]:
            print(f"    - {w}")
    if coherence["ok"]:
        print("  ✅ Contrôles réussis :")
        for o in coherence["ok"]:
            print(f"    - {o}")
    if not coherence["erreurs"] and not coherence["avertissements"]:
        print("  ✅ Aucune anomalie détectée.")

    # ── Représentativité ──────────────────────────────────────────
    print(f"\n{'─'*70}")
    print("## 6. REPRÉSENTATIVITÉ EUROPÉENNE\n")
    for c in representativite["commentaires"]:
        print(f"  ✅ {c}")
    for a in representativite["alertes"]:
        print(f"  ⚠️  {a}")

    # ── Recommandations ───────────────────────────────────────────
    print(f"\n{'─'*70}")
    print("## 7. RECOMMANDATIONS\n")
    recs = []
    manquants = representativite.get("pays_majeurs_absents", [])
    pertes_fortes = [p for p in pertes["raw_to_processed"] if p["taux_conservation"] < 50]
    if pertes_fortes:
        recs.append(
            "Revoir les transformations des sources avec forte perte : "
            + ", ".join(p["source_raw"] for p in pertes_fortes)
        )
    if jour_nuit["trains_nuit"] == 0:
        recs.append("Aucun train de nuit détecté — vérifier l'intégration des données Back on Track.")
    if manquants:
        recs.append(
            "Enrichir le dataset avec les GTFS ou statistiques Eurostat des pays manquants : "
            + ", ".join(manquants[:5])
        )
    nulls_eleves = [
        p for p in pertes["raw_to_processed"] if p["taux_nulls"] > 10
    ]
    if nulls_eleves:
        recs.append(
            "Taux de valeurs nulles élevé (>10%) dans : "
            + ", ".join(p["source_processed"] for p in nulls_eleves)
            + " — nettoyer ou compléter les champs manquants."
        )
    if repartition_gtfs and any(v.get("tronque") for v in repartition_gtfs.values()):
        pays_tronques = [code for code, v in repartition_gtfs.items() if v.get("tronque")]
        recs.append(
            f"Trips GTFS tronqués détectés pour : {', '.join(pays_tronques)}. "
            "Supprimer les caps nrows= dans les scripts ETL GTFS pour rétablir "
            "la représentativité de ces pays dans les trains de jour."
        )
    if not recs:
        recs.append("Pipeline globalement sain — aucune action corrective urgente identifiée.")
    for i, r in enumerate(recs, 1):
        print(f"  {i}. {r}")

    # ── Conclusion ────────────────────────────────────────────────
    print(f"\n{'─'*70}")
    print("## 8. CONCLUSION\n")
    statut_global = "✅ OK" if not coherence["erreurs"] else "⚠️  À CORRIGER"
    print(f"  Statut global : {statut_global}")
    print(
        f"  Le pipeline ETL ObRail Europe couvre {nb_pays} pays, "
        f"{jour_nuit['total']:,} trains identifiés "
        f"({jour_nuit['pct_nuit']}% de nuit)."
    )
    print(
        f"  Conservation RAW→PROCESSED : variable selon la source ; "
        f"PROCESSED→WAREHOUSE : {taux_global}% (agrégation attendue)."
    )
    print("  Dataset adapté à l'analyse exploratoire ; améliorations de couverture recommandées.")
    print(f"\n{SEP}")


# =========================================================
# 9. RAPPORT JSON
# =========================================================

def sauvegarder_rapport_json(
    raw_stats, processed_stats, warehouse,
    pertes, jour_nuit, couverture, trains_nuit_pays, repartition_gtfs,
    coherence, representativite,
) -> Path:
    """Sérialise l'ensemble des résultats en JSON structuré."""
    AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    chemin = AUDIT_DIR / "diagnostic_report_avance.json"

    def to_serializable(obj):
        if isinstance(obj, (np.integer,)):
            return int(obj)
        if isinstance(obj, (np.floating,)):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return str(obj)

    def simplifier_stats(stats_dict: dict) -> dict:
        out = {}
        for key, val in stats_dict.items():
            if isinstance(val, dict):
                out[key] = {
                    "fichiers": val.get("fichiers", 0),
                    "lignes":   val.get("lignes", 0),
                    "details": [
                        {
                            "nom":       d.get("nom", ""),
                            "lignes":    d.get("lignes", 0),
                            "colonnes":  d.get("colonnes", 0),
                            "taille_kb": round(d.get("taille_kb", 0), 2),
                            "doublons":  d.get("doublons", 0),
                            "erreur":    d.get("erreur"),
                        }
                        for d in val.get("details", [])
                    ],
                }
            else:
                out[key] = val
        return out

    rapport = {
        "meta": {
            "date_diagnostic": datetime.now().isoformat(),
            "projet":          "ObRail Europe — MSPR E6.1",
            "version":         "2.1",
        },
        "raw":        simplifier_stats(raw_stats),
        "processed":  simplifier_stats(processed_stats),
        "warehouse": {
            cat: [
                {k: v for k, v in f.items() if k not in ("apercu",)}
                for f in liste
            ]
            for cat, liste in warehouse.items()
        },
        "jour_nuit":               jour_nuit,
        "couverture_pays":         couverture,
        "trains_par_pays":         {str(k): v for k, v in trains_nuit_pays.items()},
        "repartition_gtfs":        {
            code: {k: v for k, v in info.items() if k != "fichiers"}
            for code, info in repartition_gtfs.items()
        },
        "pertes":                  pertes,
        "coherence":               coherence,
        "representativite":        representativite,
    }

    with open(chemin, "w", encoding="utf-8") as f:
        json.dump(rapport, f, indent=2, ensure_ascii=False, default=to_serializable)

    print(f"\n📋 Rapport JSON sauvegardé : {chemin}")
    return chemin


# =========================================================
# 10. POINT D'ENTRÉE PRINCIPAL
# =========================================================

def main():
    print("=" * 70)
    print("🔬 DIAGNOSTIC AVANCÉ DU PIPELINE ETL OBRAIL EUROPE  v2.1")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    # ── Phases de lecture ──────────────────────────────────────────
    raw_stats       = diagnostiquer_raw()
    processed_stats = diagnostiquer_processed()
    warehouse       = diagnostiquer_warehouse()

    # ── Analyses métier ────────────────────────────────────────────
    pertes            = analyser_pertes(raw_stats, processed_stats, warehouse)
    jour_nuit         = analyser_jour_nuit(warehouse)
    couverture        = analyser_couverture_pays(warehouse)
    trains_nuit_pays  = analyser_trains_par_pays(warehouse)
    repartition_gtfs  = analyser_repartition_pays_gtfs()
    coherence         = controle_coherence(warehouse)
    representativite  = evaluer_representativite(couverture, jour_nuit)

    # ── Rapport console ────────────────────────────────────────────
    afficher_rapport(
        raw_stats, processed_stats, warehouse,
        pertes, jour_nuit, couverture, trains_nuit_pays, repartition_gtfs,
        coherence, representativite,
    )

    # ── Rapport JSON ───────────────────────────────────────────────
    sauvegarder_rapport_json(
        raw_stats, processed_stats, warehouse,
        pertes, jour_nuit, couverture, trains_nuit_pays, repartition_gtfs,
        coherence, representativite,
    )


if __name__ == "__main__":
    main()