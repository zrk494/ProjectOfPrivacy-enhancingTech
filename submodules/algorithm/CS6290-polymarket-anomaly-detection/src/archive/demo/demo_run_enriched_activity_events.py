from pathlib import Path

from src.preprocessing.aggregate_trades import load_and_aggregate_trades
from src.preprocessing.aggregate_timeseries import load_and_aggregate_timeseries
from src.features.feature_fusion import fuse_trade_and_timeseries
from src.detectors.composite_anomaly import add_activity_anomaly_scores
from src.postprocessing.summarize_events import summarize_activity_events
from src.postprocessing.enrich_events import enrich_activity_events_with_snapshots


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

    events = summarize_activity_events(
        scored,
        flag_col="is_activity_anomaly",
        bucket_seconds=60,
    )

    enriched = enrich_activity_events_with_snapshots(events, scored)

    covered = enriched[enriched["snapshot_covered"] == True].copy()

    print("activity events:", len(events))
    print("snapshot-covered events:", int(enriched["snapshot_covered"].fillna(False).sum()))

    print("\ncovered events only:")
    print(
        covered[
            [
                "start_datetime",
                "end_datetime",
                "peak_activity_score",
                "total_amount",
                "snapshot_covered",
                "num_snapshot_buckets",
                "max_abs_midpoint_return",
                "max_spread",
                "min_total_depth",
                "max_abs_depth_imbalance",
            ]
        ]
    )


if __name__ == "__main__":
    main()