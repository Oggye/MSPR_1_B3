# ia\src\ml\config.py

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

WAREHOUSE_DIR = (ROOT / ".." / "data" / "warehouse").resolve()

FACTS_FILE = WAREHOUSE_DIR / "facts_night_trains.csv"
COUNTRIES_FILE = WAREHOUSE_DIR / "dim_countries.csv"
OPERATORS_FILE = WAREHOUSE_DIR / "dim_operators.csv"

OUTPUT_DIR = (ROOT / ".." / "data" / "ml").resolve()

OUTPUT_DIR.mkdir(exist_ok=True)

OUTPUT_DATASET = OUTPUT_DIR / "substitution_dataset.csv"