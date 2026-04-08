from __future__ import annotations

from pathlib import Path
import pandas as pd

from src.config import (
    BUCKET_SECONDS,
    ACTIVITY_WINDOW,
    ACTIVITY_QUANTILE,
)
from src.preprocessing.aggregate_trades import load_and_aggregate_trades
from src.preprocessing.aggregate_timeseries import load_and_aggregate_timeseries
from src.features.feature_fusion import fuse_trade_and_timeseries
from src.postprocessing.summarize_events import summarize_activity_events
from src.postprocessing.enrich_events import enrich_activity_events_with_snapshots
from src.detectors.composite_anomaly import (
    add_market_stress_scores,
    add_pca_market_stress_scores,
)


def run_pipeline_for_market(
    market_file: str,
    bucket_seconds: int = 60,
    window: int = 60,
    quantile_threshold: float = 0.98,
    score_method: str = "additive",
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Run the full market-stress pipeline for one YES-side market file.

    Parameters
    ----------
    market_file : str
        File name like '572469_YES.csv'
    bucket_seconds : int
        Bucket size in seconds.
    window : int
        Rolling window size for stress z-scores.
    quantile_threshold : float
        Percentile threshold for anomaly flagging.
    score_method : str
        "additive" for additive CMSI baseline,
        "pca" for PCA-based CMSI.

    Returns
    -------
    fused : pd.DataFrame
        Bucket-level fused feature dataframe.
    scored : pd.DataFrame
        Bucket-level scored dataframe.
    enriched_events : pd.DataFrame
        Event-level dataframe with snapshot enrichment.
    """
    base = Path(__file__).resolve().parents[1]

    trade_path = base / "data" / "polymarket_data" / "trades" / market_file
    ts_path = base / "data" / "polymarket_data" / "timeseries" / market_file

    print("=" * 80)
    print(f"Running pipeline for: {market_file}")
    print("score_method:", score_method)
    print("trade_path:", trade_path)
    print("trade exists:", trade_path.exists())
    print("ts_path:", ts_path)
    print("ts exists:", ts_path.exists())

    if not trade_path.exists():
        raise FileNotFoundError(f"Trade file not found: {trade_path}")
    if not ts_path.exists():
        raise FileNotFoundError(f"Timeseries file not found: {ts_path}")

    # 1) aggregate trades
    trade_df = load_and_aggregate_trades(trade_path, bucket_seconds=bucket_seconds)
    print("trade bucket rows:", len(trade_df))

    # 2) aggregate timeseries
    ts_df = load_and_aggregate_timeseries(ts_path, bucket_seconds=bucket_seconds)
    print("timeseries bucket rows:", len(ts_df))

    # 3) fuse features
    fused = fuse_trade_and_timeseries(
        trade_df,
        ts_df,
        how="left",
        fill_snapshot_forward=True,
    )
    print("fused rows:", len(fused))
    print(
        "non-null midpoint rows:",
        int(fused["midpoint"].notna().sum()) if "midpoint" in fused.columns else 0,
    )
    print(
        "non-null spread rows:",
        int(fused["spread"].notna().sum()) if "spread" in fused.columns else 0,
    )

    # 4) market stress scoring
    if score_method == "pca":
        scored = add_pca_market_stress_scores(
            fused,
            window=window,
            quantile_threshold=quantile_threshold,
        )
        # for downstream compatibility
        scored["stress_score"] = scored["cmsi_pca_score"]

        if "pca_explained_variance_ratio" in scored.attrs:
            print(
                "PCA explained variance ratio:",
                scored.attrs["pca_explained_variance_ratio"],
            )
    else:
        scored = add_market_stress_scores(
            fused,
            window=window,
            quantile_threshold=quantile_threshold,
        )

    # compatibility layer for event summarizer:
    # IMPORTANT: do NOT overwrite the real activity_score column,
    # otherwise attribution will be corrupted.
    scored_for_events = scored.copy()
    scored_for_events["is_activity_anomaly"] = scored_for_events["is_stress_anomaly"]

    # Only create a fallback activity_score if it truly does not exist.
    if "activity_score" not in scored_for_events.columns:
        scored_for_events["activity_score"] = scored_for_events["stress_score"]

    print("stress anomalies:", int(scored["is_stress_anomaly"].sum()))

    # 5) summarize events
    events = summarize_activity_events(
        scored_for_events,
        flag_col="is_activity_anomaly",
        bucket_seconds=bucket_seconds,
    )
    print("stress events:", len(events))

    # 6) enrich events with snapshot context
    enriched_events = enrich_activity_events_with_snapshots(events, scored)

    # rename event-level score for outward-facing consistency
    if "peak_activity_score" in enriched_events.columns:
        enriched_events = enriched_events.rename(
            columns={"peak_activity_score": "peak_stress_score"}
        )

    covered = (
        int(enriched_events["snapshot_covered"].fillna(False).sum())
        if not enriched_events.empty else 0
    )
    print("snapshot-covered stress events:", covered)

    return fused, scored, enriched_events


def save_outputs(
    market_file: str,
    fused: pd.DataFrame,
    scored: pd.DataFrame,
    enriched_events: pd.DataFrame,
    score_method: str = "additive",
) -> None:
    """
    Save pipeline outputs to results/activity_pipeline/<market_stem>/,
    with score_method-specific filenames to avoid overwriting results.
    """
    base = Path(__file__).resolve().parents[1]
    market_stem = Path(market_file).stem
    out_dir = base / "results" / "activity_pipeline" / market_stem
    out_dir.mkdir(parents=True, exist_ok=True)

    fused_path = out_dir / f"bucket_features_{score_method}.csv"
    scored_path = out_dir / f"bucket_scores_{score_method}.csv"
    events_path = out_dir / f"stress_events_enriched_{score_method}.csv"

    fused.to_csv(fused_path, index=False)
    scored.to_csv(scored_path, index=False)
    enriched_events.to_csv(events_path, index=False)

    print("\nSaved outputs:")
    print(" -", fused_path)
    print(" -", scored_path)
    print(" -", events_path)


def print_summary(
    scored: pd.DataFrame,
    enriched_events: pd.DataFrame,
    top_k: int = 10,
) -> None:
    """
    Print a concise summary of top buckets and top stress events.
    """
    print("\n" + "=" * 80)
    print("Top market stress buckets")

    bucket_cols = [
        "bucket",
        "datetime",
        "trade_count",
        "amount_sum",
        "avg_trade_size",
        "z_trade_count",
        "z_amount_sum",
        "z_avg_trade_size",
        "z_spread",
        "z_depth_drop",
        "z_abs_midpoint_return",
        "z_abs_depth_imbalance",
        "stress_score",
        "is_stress_anomaly",
    ]
    existing_bucket_cols = [c for c in bucket_cols if c in scored.columns]

    print(
        scored.sort_values("stress_score", ascending=False)
        .head(top_k)[existing_bucket_cols]
        .to_string(index=False)
    )

    print("\n" + "=" * 80)
    print("Top market stress events")
    if enriched_events.empty:
        print("No stress events detected.")
    else:
        cols = [
            "start_datetime",
            "end_datetime",
            "duration_minutes",
            "peak_stress_score",
            "peak_trade_count",
            "peak_amount_sum",
            "peak_avg_trade_size",
            "total_amount",
            "snapshot_covered",
            "num_snapshot_buckets",
            "max_abs_midpoint_return",
            "max_spread",
            "min_total_depth",
            "max_abs_depth_imbalance",
            "peak_activity_component",
            "peak_liquidity_component",
            "peak_price_component",
            "dominant_driver",
        ]
        existing_cols = [c for c in cols if c in enriched_events.columns]
        print(
            enriched_events.head(top_k)[existing_cols].to_string(index=False)
        )

        covered = enriched_events[
            enriched_events["snapshot_covered"] == True
        ].copy()

        print("\n" + "=" * 80)
        print("Snapshot-covered stress events only")
        if covered.empty:
            print("No snapshot-covered stress events.")
        else:
            print(covered[existing_cols].to_string(index=False))


def main():
    # choose a matched YES-side market file
    market_file = "572469_YES.csv"

    # final main model should be additive; PCA is retained as comparison
    score_method = "additive"
    # score_method = "pca"

    fused, scored, enriched_events = run_pipeline_for_market(
        market_file=market_file,
        bucket_seconds=BUCKET_SECONDS,
        window=ACTIVITY_WINDOW,
        quantile_threshold=ACTIVITY_QUANTILE,
        score_method=score_method,
    )

    print_summary(scored, enriched_events, top_k=10)
    save_outputs(
        market_file,
        fused,
        scored,
        enriched_events,
        score_method=score_method,
    )


if __name__ == "__main__":
    main()