# ia/src/ml/config.py

from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]

WAREHOUSE_DIR = ROOT / "data" / "warehouse"
DATA_ML_DIR   = ROOT / "data" / "ml"
MODELS_DIR    = ROOT / "ia" / "models"
REPORTS_DIR   = ROOT / "ia" / "reports"

DATA_ML_DIR.mkdir(parents=True, exist_ok=True)
MODELS_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

# Sources warehouse
STATS_FILE    = WAREHOUSE_DIR / "facts_country_stats.csv"
COUNTRIES_FILE = WAREHOUSE_DIR / "dim_countries.csv"
YEARS_FILE    = WAREHOUSE_DIR / "dim_years.csv"

# Datasets ML produits
REGRESSION_DATASET_PATH    = DATA_ML_DIR / "regression_dataset.csv"
CLASSIF_DATASET_PATH       = DATA_ML_DIR / "classification_dataset.csv"

# Preprocesseurs
PREPROCESSOR_REG_PATH      = DATA_ML_DIR / "preprocessor_regression.joblib"
PREPROCESSOR_CLF_PATH      = DATA_ML_DIR / "preprocessor_classification.joblib"