from pathlib import Path

from src.preprocessing.aggregate_trades import load_and_aggregate_trades
from src.preprocessing.aggregate_timeseries import load_and_aggregate_timeseries
from src.features.feature_fusion import fuse_trade_and_timeseries
from src.detectors.composite_anomaly import add_activity_anomaly_scores


def main():
    base = Path(__file__).resolve().parents[2]

    trade_path = base / "data" / "polymarket_data" / "trades" / "1273610_YES.csv"
    ts_path = base / "data" / "polymarket_data" / "timeseries" / "1273610_YES.csv"

    trade_df = load_and_aggregate_trades(trade_path, bucket_seconds=60)
    ts_df = load_and_aggregate_timeseries(ts_path, bucket_seconds=60)

    fused = fuse_trade_and_timeseries(
        trade_df,
        ts_df,
        how="left",
        fill_snapshot_forward=True,
    )

    scored = add_activity_anomaly_scores(
        fused,
        window=60,
        score_mode="sum",
        quantile_threshold=0.98,
    )

    print("rows:", len(scored))
    print("activity anomalies:", int(scored["is_activity_anomaly"].sum()))

    print("\ntop activity anomalies:")
    print(
        scored.sort_values("activity_score", ascending=False)
        .head(10)[
            [
                "bucket",
                "datetime",
                "trade_count",
                "amount_sum",
                "avg_trade_size",
                "z_trade_count",
                "z_amount_sum",
                "z_avg_trade_size",
                "activity_score",
                "is_activity_anomaly",
            ]
        ]
    )


if __name__ == "__main__":
    main()