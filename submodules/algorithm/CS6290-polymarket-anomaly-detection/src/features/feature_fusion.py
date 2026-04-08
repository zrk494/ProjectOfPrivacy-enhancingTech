from __future__ import annotations

import pandas as pd


TRADE_REQUIRED = [
    "bucket",
    "trade_count",
    "size_sum",
    "amount_sum",
    "vwap",
]

SNAPSHOT_REQUIRED = [
    "bucket",
    "midpoint",
    "spread",
    "bid_depth_top5",
    "ask_depth_top5",
    "total_depth",
    "depth_imbalance",
]

SNAPSHOT_FEATURE_COLS = [
    "midpoint",
    "spread",
    "bid_depth_top5",
    "ask_depth_top5",
    "total_depth",
    "depth_imbalance",
]


def _check_columns(df: pd.DataFrame, required: list[str], name: str) -> None:
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns in {name}: {missing}")


def fuse_trade_and_timeseries(
    trade_bucket_df: pd.DataFrame,
    snapshot_bucket_df: pd.DataFrame,
    how: str = "left",
    fill_snapshot_forward: bool = True,
) -> pd.DataFrame:
    """
    Merge trade-level bucket features with snapshot-level bucket features.

    Parameters
    ----------
    trade_bucket_df : pd.DataFrame
        Output from aggregate_trades(...)
    snapshot_bucket_df : pd.DataFrame
        Output from aggregate_timeseries(...)
    how : str
        Merge strategy. For sparse snapshot data, "left" is recommended.
    fill_snapshot_forward : bool
        Whether to forward-fill snapshot columns after merge.

    Returns
    -------
    pd.DataFrame
        Fused bucket-level feature dataframe.
    """
    if trade_bucket_df.empty:
        return pd.DataFrame()

    _check_columns(trade_bucket_df, TRADE_REQUIRED, "trade_bucket_df")

    t = trade_bucket_df.copy().sort_values("bucket").reset_index(drop=True)

    if snapshot_bucket_df.empty:
        df = t.copy()
        for col in SNAPSHOT_FEATURE_COLS:
            df[col] = pd.NA
    else:
        _check_columns(snapshot_bucket_df, SNAPSHOT_REQUIRED, "snapshot_bucket_df")
        s = snapshot_bucket_df.copy().sort_values("bucket").reset_index(drop=True)
        df = pd.merge(t, s, on="bucket", how=how)

    if df.empty:
        return pd.DataFrame()

    df = df.sort_values("bucket").reset_index(drop=True)

    if fill_snapshot_forward:
        existing_snapshot_cols = [c for c in SNAPSHOT_FEATURE_COLS if c in df.columns]
        df[existing_snapshot_cols] = df[existing_snapshot_cols].ffill()

    # add datetime
    df["datetime"] = pd.to_datetime(df["bucket"], unit="s")


    # avg_trade_size: add if not already present
    if "avg_trade_size" not in df.columns:
        denom = df["trade_count"].replace(0, pd.NA)
        df["avg_trade_size"] = (df["amount_sum"] / denom).fillna(0.0)

    # max_trade_size: optional safeguard
    if "max_trade_size" not in df.columns:
        df["max_trade_size"] = pd.NA

    # midpoint_return and abs_midpoint_return
    if "midpoint" in df.columns:
        df["midpoint_return"] = df["midpoint"].pct_change(fill_method=None).fillna(0.0)
        df["abs_midpoint_return"] = df["midpoint_return"].abs()
    else:
        df["midpoint_return"] = 0.0
        df["abs_midpoint_return"] = 0.0

    # spread_pct
    if "spread" in df.columns and "midpoint" in df.columns:
        midpoint_denom = df["midpoint"].replace(0, pd.NA)
        df["spread_pct"] = (df["spread"] / midpoint_denom).fillna(0.0)
    else:
        df["spread_pct"] = 0.0

    # depth_change
    if "total_depth" in df.columns:
        df["depth_change"] = df["total_depth"].diff().fillna(0.0)
    else:
        df["depth_change"] = 0.0

    df["depth_drop"] = pd.to_numeric(df["depth_change"], errors="coerce").fillna(0.0)
    df["depth_drop"] = (-df["depth_drop"]).clip(lower=0)

    if "depth_imbalance" in df.columns:
        df["abs_depth_imbalance"] = df["depth_imbalance"].abs()
    else:
        df["abs_depth_imbalance"] = 0.0

    preferred_cols = [
        "bucket",
        "datetime",
        "trade_count",
        "size_sum",
        "amount_sum",
        "vwap",
        "avg_trade_size",
        "max_trade_size",
        "midpoint",
        "midpoint_return",
        "abs_midpoint_return",
        "spread",
        "spread_pct",
        "bid_depth_top5",
        "ask_depth_top5",
        "total_depth",
        "depth_change",
        "depth_imbalance",
        "depth_drop",
        "abs_depth_imbalance",
    ]

    existing_cols = [c for c in preferred_cols if c in df.columns]
    extra_cols = [c for c in df.columns if c not in existing_cols]

    return df[existing_cols + extra_cols].reset_index(drop=True)