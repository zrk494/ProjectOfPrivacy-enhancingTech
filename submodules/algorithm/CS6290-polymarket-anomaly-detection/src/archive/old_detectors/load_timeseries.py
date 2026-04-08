from pathlib import Path
import pandas as pd


def load_market_timeseries(csv_path: Path) -> pd.DataFrame:
    df = pd.read_csv(csv_path)
    df = df.sort_values("timestamp").reset_index(drop=True)

    # 基础清洗
    for col in ["midpoint", "best_bid", "best_ask", "spread", "bid_depth_top5", "ask_depth_top5"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["timestamp"] = pd.to_numeric(df["timestamp"], errors="coerce").astype("Int64")
    return df
