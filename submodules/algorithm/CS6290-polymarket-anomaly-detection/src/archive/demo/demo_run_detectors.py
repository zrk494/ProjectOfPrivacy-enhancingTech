from pathlib import Path
from src.archive.old_detectors.load_timeseries import load_market_timeseries
from src.archive.old_detectors.price_spike import detect_price_spikes
from src.archive.old_detectors.book_shock import detect_book_shocks


def main():
    base = Path(__file__).resolve().parents[1]
    data_dir = base / "data" / "polymarket_data" / "timeseries"

    csv_files = list(data_dir.glob("*.csv"))

    best = None
    best_n = -1

    for p in csv_files:
        # 统计行数（减去表头）
        n = sum(1 for _ in open(p, "r", encoding="utf-8", errors="ignore")) - 1
        if n > best_n:
            best_n = n
            best = p

    print("Chosen:", best.name, "rows:", best_n)

    df = load_market_timeseries(best)
    print("Rows:", len(df))
    print(df.tail(3))

    out1 = detect_price_spikes(df)
    out2 = detect_book_shocks(df)

    print("Market file:", best.name)
    print("Price spikes:", (out1["spike_type"] != "none").sum())
    print(out1.loc[out1["spike_type"] != "none", ["timestamp", "midpoint", "ret", "ret_z", "spread", "spread_z", "spike_type"]].head(10))

    print("Book shocks:", (out2["shock_type"] != "none").sum())
    print(out2.loc[out2["shock_type"] != "none", ["timestamp", "midpoint", "spread", "spread_z", "imbalance", "dimb_z", "shock_type"]].head(10))


if __name__ == "__main__":
    main()
