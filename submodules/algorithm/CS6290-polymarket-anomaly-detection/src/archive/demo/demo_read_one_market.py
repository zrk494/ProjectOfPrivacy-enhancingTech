from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data" / "polymarket_data" / "timeseries"

print("Looking in:", DATA_DIR)

if not DATA_DIR.exists():
    print("DATA DIR NOT FOUND ❌")
else:
    csv_files = list(DATA_DIR.glob("*.csv"))
    print("Found csv files:", len(csv_files))

    if len(csv_files) > 0:
        df = pd.read_csv(csv_files[0])
        print(df.head())
        print("Columns:", df.columns.tolist())
