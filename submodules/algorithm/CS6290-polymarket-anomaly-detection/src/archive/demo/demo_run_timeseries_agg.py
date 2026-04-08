from pathlib import Path

from src.preprocessing.aggregate_trades import load_and_aggregate_trades
from src.preprocessing.aggregate_timeseries import load_and_aggregate_timeseries
from src.features.feature_fusion import fuse_trade_and_timeseries


def main():
    base = Path(__file__).resolve().parents[2]

    trade_path = base / "data" / "polymarket_data" / "trades" / "1273610_YES.csv"
    ts_path = base / "data" / "polymarket_data" / "timeseries" / "1273610_YES.csv"

    print("trade_path:", trade_path)
    print("trade exists:", trade_path.exists())
    print("ts_path:", ts_path)
    print("ts exists:", ts_path.exists())

    trade_df = load_and_aggregate_trades(trade_path, bucket_seconds=60)
    ts_df = load_and_aggregate_timeseries(ts_path, bucket_seconds=60)

    print("trade bucket rows:", len(trade_df))
    print("timeseries bucket rows:", len(ts_df))

    fused = fuse_trade_and_timeseries(trade_df, ts_df, how="inner")

    print("fused rows:", len(fused))
    print(fused.head())
    print(fused.columns.tolist())


if __name__ == "__main__":
    main()