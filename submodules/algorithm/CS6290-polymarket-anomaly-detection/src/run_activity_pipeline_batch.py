from __future__ import annotations

from pathlib import Path
import pandas as pd
import traceback

from src.preprocessing.aggregate_trades import load_and_aggregate_trades
from src.preprocessing.aggregate_timeseries import load_and_aggregate_timeseries
from src.features.feature_fusion import fuse_trade_and_timeseries
from src.detectors.composite_anomaly import (
    add_market_stress_scores,
    add_pca_market_stress_scores,
)
from src.postprocessing.summarize_events import summarize_activity_events
from src.postprocessing.enrich_events import enrich_activity_events_with_snapshots
from src.config import (
    BUCKET_SECONDS,
    ACTIVITY_WINDOW,
    ACTIVITY_QUANTILE,
)


def safe_float(x):
    try:
        if pd.isna(x):
            return None
        return float(x)
    except Exception:
        return None


def run_pipeline_for_market(
    base: Path,
    market_file: str,
    bucket_seconds: int = 60,
    window: int = 60,
    quantile_threshold: float = 0.98,
    score_method: str = "additive",
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, dict]:
    """
    Run the full market-stress pipeline for one YES-side market file.

    Returns
    -------
    fused, scored, enriched_events, summary_row
    """
    trade_path = base / "data" / "polymarket_data" / "trades" / market_file
    ts_path = base / "data" / "polymarket_data" / "timeseries" / market_file

    if not trade_path.exists():
        raise FileNotFoundError(f"Trade file not found: {trade_path}")
    if not ts_path.exists():
        raise FileNotFoundError(f"Timeseries file not found: {ts_path}")

    # 1) aggregate trades
    trade_df = load_and_aggregate_trades(trade_path, bucket_seconds=bucket_seconds)

    # 2) aggregate timeseries
    ts_df = load_and_aggregate_timeseries(ts_path, bucket_seconds=bucket_seconds)

    # 3) fuse features
    fused = fuse_trade_and_timeseries(
        trade_df,
        ts_df,
        how="left",
        fill_snapshot_forward=True,
    )

    # 4) market stress scoring
    if score_method == "pca":
        scored = add_pca_market_stress_scores(
            fused,
            window=window,
            quantile_threshold=quantile_threshold,
        )
        scored["stress_score"] = scored["cmsi_pca_score"]
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

    # 5) summarize events
    events = summarize_activity_events(
        scored_for_events,
        flag_col="is_activity_anomaly",
        bucket_seconds=bucket_seconds,
    )

    # 6) enrich events with snapshot context
    enriched_events = enrich_activity_events_with_snapshots(events, scored)

    # outward-facing rename for consistency
    if "peak_activity_score" in enriched_events.columns:
        enriched_events = enriched_events.rename(
            columns={"peak_activity_score": "peak_stress_score"}
        )

    # add market id/file info to outputs
    market_stem = Path(market_file).stem

    fused = fused.copy()
    fused["market_file"] = market_file
    fused["market_stem"] = market_stem

    scored = scored.copy()
    scored["market_file"] = market_file
    scored["market_stem"] = market_stem

    enriched_events = enriched_events.copy()
    if not enriched_events.empty:
        enriched_events["market_file"] = market_file
        enriched_events["market_stem"] = market_stem

    summary_row = {
        "market_file": market_file,
        "market_stem": market_stem,
        "score_method": score_method,
        "trade_bucket_rows": int(len(trade_df)),
        "timeseries_bucket_rows": int(len(ts_df)),
        "fused_rows": int(len(fused)),
        "non_null_midpoint_rows": int(fused["midpoint"].notna().sum()) if "midpoint" in fused.columns else 0,
        "non_null_spread_rows": int(fused["spread"].notna().sum()) if "spread" in fused.columns else 0,
        "stress_anomalies": int(
            scored["is_stress_anomaly"].sum()
        ) if "is_stress_anomaly" in scored.columns else 0,
        "stress_events": int(len(enriched_events)),
        "anomaly_rate": (
            safe_float(scored["is_stress_anomaly"].sum() / len(trade_df))
            if len(trade_df) > 0 else None
        ),
        "event_rate": (
            safe_float(len(enriched_events) / len(trade_df))
            if len(trade_df) > 0 else None
        ),
        "snapshot_covered_events": int(
            enriched_events["snapshot_covered"].fillna(False).sum()
        ) if not enriched_events.empty else 0,
        "max_stress_score": safe_float(
            scored["stress_score"].max()
        ) if not scored.empty else None,
        "max_event_peak_stress_score": (
            safe_float(enriched_events["peak_stress_score"].max())
            if (not enriched_events.empty and "peak_stress_score" in enriched_events.columns)
            else (
                safe_float(enriched_events["peak_activity_score"].max())
                if (not enriched_events.empty and "peak_activity_score" in enriched_events.columns)
                else None
            )
        ),
        "top_event_total_amount": (
            safe_float(enriched_events["total_amount"].max())
            if (not enriched_events.empty and "total_amount" in enriched_events.columns)
            else None
        ),
        "pca_explained_variance_ratio": safe_float(
            scored.attrs.get("pca_explained_variance_ratio", None)
        ),
    }

    return fused, scored, enriched_events, summary_row


def save_market_outputs(
    base: Path,
    market_file: str,
    fused: pd.DataFrame,
    scored: pd.DataFrame,
    enriched_events: pd.DataFrame,
    score_method: str = "additive",
) -> None:
    market_stem = Path(market_file).stem
    out_dir = base / "results" / "activity_pipeline_batch" / market_stem
    out_dir.mkdir(parents=True, exist_ok=True)

    fused.to_csv(out_dir / f"bucket_features_{score_method}.csv", index=False)
    scored.to_csv(out_dir / f"bucket_scores_{score_method}.csv", index=False)
    enriched_events.to_csv(
        out_dir / f"stress_events_enriched_{score_method}.csv",
        index=False,
    )


def main():
    base = Path(__file__).resolve().parents[1]

    trade_dir = base / "data" / "polymarket_data" / "trades"
    ts_dir = base / "data" / "polymarket_data" / "timeseries"

    # final main model should be additive; PCA retained as comparison
    score_method = "additive"
    # score_method = "pca"

    # only use YES-side files that also exist in timeseries
    trade_yes_files = {p.name for p in trade_dir.glob("*_YES.csv")}
    ts_yes_files = {p.name for p in ts_dir.glob("*_YES.csv")}
    market_files = sorted(trade_yes_files & ts_yes_files)

    print("=" * 80)
    print("Batch market stress pipeline")
    print("score_method:", score_method)
    print("trade YES files:", len(trade_yes_files))
    print("timeseries YES files:", len(ts_yes_files))
    print("matched YES files:", len(market_files))

    if not market_files:
        raise FileNotFoundError(
            "No matched *_YES.csv files found in both trades/ and timeseries/."
        )

    all_summary_rows = []
    all_events = []

    for i, market_file in enumerate(market_files, start=1):
        print("\n" + "-" * 80)
        print(f"[{i}/{len(market_files)}] Running: {market_file}")

        try:
            fused, scored, enriched_events, summary_row = run_pipeline_for_market(
                base=base,
                market_file=market_file,
                bucket_seconds=BUCKET_SECONDS,
                window=ACTIVITY_WINDOW,
                quantile_threshold=ACTIVITY_QUANTILE,
                score_method=score_method,
            )

            save_market_outputs(
                base,
                market_file,
                fused,
                scored,
                enriched_events,
                score_method=score_method,
            )

            all_summary_rows.append(summary_row)

            if not enriched_events.empty:
                all_events.append(enriched_events)

            if score_method == "pca" and summary_row["pca_explained_variance_ratio"] is not None:
                print(
                    f"Done | buckets={summary_row['trade_bucket_rows']} "
                    f"| stress_anomalies={summary_row['stress_anomalies']} "
                    f"| stress_events={summary_row['stress_events']} "
                    f"| covered={summary_row['snapshot_covered_events']} "
                    f"| pca_var={summary_row['pca_explained_variance_ratio']:.4f}"
                )
            else:
                print(
                    f"Done | buckets={summary_row['trade_bucket_rows']} "
                    f"| stress_anomalies={summary_row['stress_anomalies']} "
                    f"| stress_events={summary_row['stress_events']} "
                    f"| covered={summary_row['snapshot_covered_events']}"
                )

        except Exception as e:
            print(f"FAILED for {market_file}: {e}")
            traceback.print_exc()
            all_summary_rows.append(
                {
                    "market_file": market_file,
                    "market_stem": Path(market_file).stem,
                    "score_method": score_method,
                    "error": str(e),
                }
            )

    summary_df = pd.DataFrame(all_summary_rows)

    if all_events:
        all_events_df = pd.concat(all_events, ignore_index=True)
        all_events_df = all_events_df.loc[:, ~all_events_df.columns.duplicated()].copy()
    else:
        all_events_df = pd.DataFrame()

    batch_out_dir = base / "results" / "activity_pipeline_batch"
    batch_out_dir.mkdir(parents=True, exist_ok=True)

    summary_path = batch_out_dir / f"market_stress_summary_{score_method}.csv"
    events_path = batch_out_dir / f"all_stress_events_{score_method}.csv"

    summary_df.to_csv(summary_path, index=False)
    all_events_df.to_csv(events_path, index=False)

    print("\n" + "=" * 80)
    print("Batch market stress run complete")
    print("Saved:")
    print(" -", summary_path)
    print(" -", events_path)

    # concise terminal summary
    if not summary_df.empty:
        print("\nTop markets by number of stress events:")
        cols = [
            "market_file",
            "score_method",
            "trade_bucket_rows",
            "stress_anomalies",
            "stress_events",
            "anomaly_rate",
            "event_rate",
            "snapshot_covered_events",
            "max_event_peak_stress_score",
            "top_event_total_amount",
            "pca_explained_variance_ratio",
        ]
        existing_cols = [c for c in cols if c in summary_df.columns]
        print(
            summary_df.sort_values(
                ["stress_events", "max_event_peak_stress_score"],
                ascending=[False, False],
                na_position="last",
            )[existing_cols].head(10).to_string(index=False)
        )

        if not all_events_df.empty:
            print("\nTop stress events across all markets:")
            cols2 = [
                "market_file",
                "start_datetime",
                "end_datetime",
                "peak_stress_score",
                "total_amount",
                "snapshot_covered",
                "num_snapshot_buckets",
                "max_spread",
                "min_total_depth",
                "max_abs_depth_imbalance",
            ]
            existing_cols2 = [c for c in cols2 if c in all_events_df.columns]
            print(
                all_events_df.sort_values(
                    ["peak_stress_score", "total_amount"],
                    ascending=[False, False],
                    na_position="last",
                )[existing_cols2].head(10).to_string(index=False)
            )


if __name__ == "__main__":
    main()