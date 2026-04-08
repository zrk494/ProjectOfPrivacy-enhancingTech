from __future__ import annotations

import pandas as pd


BASE_REQUIRED_COLUMNS = [
    "bucket",
    "datetime",
    "trade_count",
    "amount_sum",
    "avg_trade_size",
]


def _check_columns(df: pd.DataFrame, required: list[str], name: str) -> None:
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns in {name}: {missing}")


def summarize_activity_events(
    df: pd.DataFrame,
    flag_col: str = "is_activity_anomaly",
    bucket_seconds: int = 60,
) -> pd.DataFrame:
    """
    Merge consecutive anomalous buckets into event windows and summarize them.

    This function is backward-compatible with the original activity-based pipeline,
    but can also summarize stress-based pipelines if `stress_score` is present.

    Parameters
    ----------
    df : pd.DataFrame
        Bucket-level scored dataframe.
    flag_col : str
        Boolean anomaly flag column.
    bucket_seconds : int
        Bucket size in seconds. Default 60.

    Returns
    -------
    pd.DataFrame
        Event-level summary dataframe.
    """
    if df.empty:
        return pd.DataFrame(
            columns=[
                "start",
                "end",
                "start_datetime",
                "end_datetime",
                "duration_buckets",
                "duration_minutes",
                "num_anomalous_buckets",
                "peak_activity_score",
                "peak_stress_score",
                "peak_trade_count",
                "peak_amount_sum",
                "peak_avg_trade_size",
                "total_amount",
            ]
        )

    required = BASE_REQUIRED_COLUMNS + [flag_col]
    _check_columns(df, required, "scored df")

    # choose score column dynamically
    if "stress_score" in df.columns:
        score_col = "stress_score"
    elif "activity_score" in df.columns:
        score_col = "activity_score"
    else:
        raise ValueError("Input dataframe must contain either 'stress_score' or 'activity_score'.")

    x = df.copy().sort_values("bucket").reset_index(drop=True)

    # keep only anomalous rows
    x = x[x[flag_col].fillna(False)].copy()
    if x.empty:
        return pd.DataFrame(
            columns=[
                "start",
                "end",
                "start_datetime",
                "end_datetime",
                "duration_buckets",
                "duration_minutes",
                "num_anomalous_buckets",
                "peak_activity_score",
                "peak_stress_score",
                "peak_trade_count",
                "peak_amount_sum",
                "peak_avg_trade_size",
                "total_amount",
            ]
        )

    # new event whenever the current anomalous bucket is not exactly 1 bucket after the previous
    x["prev_bucket"] = x["bucket"].shift(1)
    x["new_event"] = (x["bucket"] - x["prev_bucket"]) != bucket_seconds
    x["event_id"] = x["new_event"].cumsum()

    event_rows = []
    for _, g in x.groupby("event_id"):
        g = g.sort_values("bucket").reset_index(drop=True)
        peak_score = float(g[score_col].max())

        event_rows.append(
            {
                "start": int(g["bucket"].iloc[0]),
                "end": int(g["bucket"].iloc[-1]),
                "start_datetime": g["datetime"].iloc[0],
                "end_datetime": g["datetime"].iloc[-1],
                "duration_buckets": int(len(g)),
                "duration_minutes": int(len(g) * bucket_seconds / 60),
                "num_anomalous_buckets": int(len(g)),
                # keep old field for backward compatibility
                "peak_activity_score": peak_score,
                # add explicit field for stress pipeline
                "peak_stress_score": peak_score,
                "peak_trade_count": float(g["trade_count"].max()),
                "peak_amount_sum": float(g["amount_sum"].max()),
                "peak_avg_trade_size": float(g["avg_trade_size"].max()),
                "total_amount": float(g["amount_sum"].sum()),
            }
        )

    out = pd.DataFrame(event_rows)

    if not out.empty:
        out = out.sort_values(
            ["peak_stress_score", "total_amount"],
            ascending=[False, False],
        ).reset_index(drop=True)

    return out