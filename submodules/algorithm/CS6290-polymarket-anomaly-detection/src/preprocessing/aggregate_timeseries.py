from __future__ import annotations

from pathlib import Path
import pandas as pd

REQUIRED_COLUMNS = [
    "timestamp",
    "midpoint",
    "spread",
    "bid_depth_top5",
    "ask_depth_top5",
]


def _validate_columns(df: pd.DataFrame) -> None:
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns in timeseries data: {missing}")


def aggregate_timeseries(
    df: pd.DataFrame,
    bucket_seconds: int = 60,
) -> pd.DataFrame:
    """
    Aggregate snapshot-style timeseries data into fixed time buckets.

    Parameters
    ----------
    df : pd.DataFrame
        Raw timeseries dataframe containing snapshot records.
    bucket_seconds : int
        Bucket size in seconds. Default is 60.

    Returns
    -------
    pd.DataFrame
        Bucket-level snapshot features with columns:
        - bucket
        - midpoint
        - spread
        - bid_depth_top5
        - ask_depth_top5
        - total_depth
        - depth_imbalance
    """
    if df.empty:
        return pd.DataFrame(
            columns=[
                "bucket",
                "midpoint",
                "spread",
                "bid_depth_top5",
                "ask_depth_top5",
                "total_depth",
                "depth_imbalance",
            ]
        )

    _validate_columns(df)

    x = df.copy()

    # keep only required columns first
    x = x[REQUIRED_COLUMNS].copy()

    # numeric conversion
    for col in REQUIRED_COLUMNS:
        x[col] = pd.to_numeric(x[col], errors="coerce")

    # drop bad rows
    x = x.dropna(subset=REQUIRED_COLUMNS).copy()

    if x.empty:
        return pd.DataFrame(
            columns=[
                "bucket",
                "midpoint",
                "spread",
                "bid_depth_top5",
                "ask_depth_top5",
                "total_depth",
                "depth_imbalance",
            ]
        )

    # sort by timestamp to ensure "last snapshot in bucket" is correct
    x = x.sort_values("timestamp").copy()

    # build bucket
    x["bucket"] = (x["timestamp"] // bucket_seconds) * bucket_seconds

    # snapshot-style aggregation: keep the last observation in each bucket
    agg = (
        x.groupby("bucket", as_index=False)
         .last()
    )

    # derive liquidity features
    agg["total_depth"] = agg["bid_depth_top5"] + agg["ask_depth_top5"]

    denom = agg["total_depth"].replace(0, pd.NA)
    agg["depth_imbalance"] = (
        (agg["bid_depth_top5"] - agg["ask_depth_top5"]) / denom
    ).fillna(0.0)

    # keep only final columns
    out = agg[
        [
            "bucket",
            "midpoint",
            "spread",
            "bid_depth_top5",
            "ask_depth_top5",
            "total_depth",
            "depth_imbalance",
        ]
    ].reset_index(drop=True)

    return out



def load_and_aggregate_timeseries(
    csv_path: str | Path,
    bucket_seconds: int = 60,
) -> pd.DataFrame:
    """
    Convenience wrapper to load a CSV and aggregate it.
    """
    csv_path = Path(csv_path)
    df = pd.read_csv(csv_path)
    return aggregate_timeseries(df, bucket_seconds=bucket_seconds)