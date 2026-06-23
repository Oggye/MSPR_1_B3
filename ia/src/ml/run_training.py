# ia/src/ml/run_training.py
#
# Lance l'entraînement complet des deux axes :
#   - Classification : logistic, random_forest, xgboost, mlp
#   - Régression     : ridge, random_forest, xgboost

import sys
import traceback
import importlib

from .config import (
    REGRESSION_DATASET_PATH, CLASSIF_DATASET_PATH,
    MODELS_DIR, REPORTS_DIR
)


def check_prerequisites():
    errors = []
    if not REGRESSION_DATASET_PATH.exists():
        errors.append(f"Dataset régression introuvable : {REGRESSION_DATASET_PATH}")
    if not CLASSIF_DATASET_PATH.exists():
        errors.append(f"Dataset classification introuvable : {CLASSIF_DATASET_PATH}")
    if errors:
        print("❌ Prérequis manquants :")
        for e in errors:
            print(f"  - {e}")
        print("  → Lancez d'abord build_dataset.py")
        return False
    return True


def run(module_path, func_name):
    try:
        module = importlib.import_module(module_path, package="ia.src.ml")
        getattr(module, func_name)()
        return True
    except Exception:
        print(f"❌ Erreur dans {func_name} :")
        traceback.print_exc()
        return False


def main():
    print("🚀 Phase 4 — Entraînement des modèles candidats")
    print("=" * 60)

    if not check_prerequisites():
        sys.exit(1)

    # ----------------------------------------------------------
    # Axe 1 — Classification : détection des pays en déclin
    # ----------------------------------------------------------
    print("\n" + "─" * 60)
    print("AXE 1 — CLASSIFICATION (en_declin)")
    print("─" * 60)

    clf_tasks = [
        (".models.train_logistic",      "train_logistic"),
        (".models.train_random_forest", "train_random_forest"),
        (".models.train_xgboost",       "train_xgboost"),
        (".models.train_mlp",           "train_mlp"),
    ]
    for module_path, func_name in clf_tasks:
        run(module_path, func_name)

    # ----------------------------------------------------------
    # Axe 2 — Régression : prévision de fréquentation
    # ----------------------------------------------------------
    print("\n" + "─" * 60)
    print("AXE 2 — RÉGRESSION (passengers)")
    print("─" * 60)

    reg_tasks = [
        (".models.train_ridge",         "train_ridge"),
        (".models.train_random_forest", "train_random_forest_regressor"),
        (".models.train_xgboost",       "train_xgboost_regressor"),
    ]
    for module_path, func_name in reg_tasks:
        run(module_path, func_name)

    # ----------------------------------------------------------
    # Rapport comparatif
    # ----------------------------------------------------------
    print("\n" + "=" * 60)
    print("📊 Génération des rapports comparatifs...")
    try:
        from .evaluate_model import main as evaluate_main
        evaluate_main()
    except Exception:
        print("❌ Erreur lors de la génération des rapports :")
        traceback.print_exc()

    print("\n✅ Phase 4 terminée.")
    print(f"   Modèles     → {MODELS_DIR}")
    print(f"   Rapports    → {REPORTS_DIR}")


if __name__ == "__main__":
    main()