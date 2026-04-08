from pathlib import Path
import pandas as pd

from src.preprocessing.aggregate_trades import aggregate_trades
from src.archive.old_detectors.postprocess import merge_boolean_runs
from src.archive.old_detectors.trade_anomaly import detect_trade_burst


def main():
    base = Path(__file__).resolve().parents[1]
    trade_dir = base / "data" / "polymarket_data" / "trades"

    print("base:", base)
    print("trade_dir:", trade_dir)
    print("trade_dir exists:", trade_dir.exists())

    files = sorted(trade_dir.glob("*.csv"))
    print("trade files:", len(files))

    if not files:
        raise FileNotFoundError(f"No CSV files found in {trade_dir}")

    p = files[0]
    df = pd.read_csv(p)
    print("using:", p.name, "rows:", len(df))

    # 聚合成 60s 桶
    ts = aggregate_trades(df, bucket_seconds=60)
    print("aggregated rows:", len(ts))
    print(ts.head())

    # 窗口：数据短就用 20，否则 60
    w = 20 if len(ts) < 200 else 60

    # 只跑 trade_count burst
    b = detect_trade_burst(ts, window=w, z_thresh=4.0)

    print("burst points:", int(b["is_burst"].sum()))

    print("top bursts (by z_count):")
    print(
        b.sort_values("z_count", ascending=False)
         .head(10)[["bucket", "trade_count", "z_count"]]
    )

    # 合并成事件
    burst_events = merge_boolean_runs(b, "is_burst")

    print("burst events:", len(burst_events))
    print(burst_events.head())


if __name__ == "__main__":
    main()