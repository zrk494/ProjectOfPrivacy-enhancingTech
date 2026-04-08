from pathlib import Path

from src.preprocessing.aggregate_trades import load_and_aggregate_trades
from src.preprocessing.aggregate_timeseries import load_and_aggregate_timeseries
from src.features.feature_fusion import fuse_trade_and_timeseries


def main():
    base = Path(__file__).resolve().parents[2]

    trade_path = base / "data" / "polymarket_data" / "trades" / "1273610_YES.csv"
    ts_path = base / "data" / "polymarket_data" / "timeseries" / "1273610_YES.csv"

    trade_df = load_and_aggregate_trades(trade_path, bucket_seconds=60)
    ts_df = load_and_aggregate_timeseries(ts_path, bucket_seconds=60)

    print("trade bucket rows:", len(trade_df))
    print("timeseries bucket rows:", len(ts_df))

    fused = fuse_trade_and_timeseries(
        trade_df,
        ts_df,
        how="left",
        fill_snapshot_forward=True,
    )

    print("fused rows:", len(fused))
    print("non-null midpoint rows:", fused["midpoint"].notna().sum())
    print("non-null spread rows:", fused["spread"].notna().sum())
    print(fused.head(10))
    print(fused.tail(10))
    print(fused.head())
    print(fused.columns.tolist())


if __name__ == "__main__":
    main()