from __future__ import annotations
from sklearn.decomposition import PCA

import pandas as pd
import numpy as np

REQUIRED_COLUMNS = [
    "bucket",
    "trade_count",
    "amount_sum",
    "avg_trade_size",
]


def _check_columns(df: pd.DataFrame, required: list[str], name: str) -> None:
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns in {name}: {missing}")


def _rolling_zscore(
    s: pd.Series,
    window: int,
    min_periods: int | None = None,
) -> pd.Series:
    """
    Rolling z-score using past+current window statistics.
    """
    if min_periods is None:
        min_periods = max(5, window // 3)

    s = pd.to_numeric(s, errors="coerce")

    roll_mean = s.rolling(window=window, min_periods=min_periods).mean()
    roll_std = s.rolling(window=window, min_periods=min_periods).std()

    z = (s - roll_mean) / roll_std.replace(0, pd.NA)
    z = pd.to_numeric(z, errors="coerce")

    return z.fillna(0.0)

def add_market_stress_scores(
    df: pd.DataFrame,
    window: int = 60,
    quantile_threshold: float = 0.98,
) -> pd.DataFrame:
    """
    Add market stress scores using trade-side features plus optional
    price/liquidity enrichment features.
    """
    if df.empty:
        return df.copy()

    out = df.copy().sort_values("bucket").reset_index(drop=True)

    # --- trade-side core signals ---
    out["z_trade_count"] = _rolling_zscore(out["trade_count"], window=window)
    out["z_amount_sum"] = _rolling_zscore(out["amount_sum"], window=window)
    out["z_avg_trade_size"] = _rolling_zscore(out["avg_trade_size"], window=window)

    # --- snapshot-side optional signals ---
    if "spread" in out.columns:
        out["z_spread"] = _rolling_zscore(out["spread"], window=window)
    else:
        out["z_spread"] = 0.0

    if "depth_drop" in out.columns:
        out["z_depth_drop"] = _rolling_zscore(out["depth_drop"], window=window)
    else:
        out["z_depth_drop"] = 0.0

    if "abs_midpoint_return" in out.columns:
        out["z_abs_midpoint_return"] = _rolling_zscore(out["abs_midpoint_return"], window=window)
    else:
        out["z_abs_midpoint_return"] = 0.0

    if "abs_depth_imbalance" in out.columns:
        out["z_abs_depth_imbalance"] = _rolling_zscore(out["abs_depth_imbalance"], window=window)
    else:
        out["z_abs_depth_imbalance"] = 0.0

    # make sure optional columns don't propagate NaN
    optional_cols = [
        "z_spread",
        "z_depth_drop",
        "z_abs_midpoint_return",
        "z_abs_depth_imbalance",
    ]
    for c in optional_cols:
        out[c] = pd.to_numeric(out[c], errors="coerce").fillna(0.0)

    # --- component scores ---
    out["activity_score"] = (
        out["z_trade_count"]
        + out["z_amount_sum"]
        + out["z_avg_trade_size"]
    )

    out["liquidity_score"] = (
        out["z_spread"]
        + out["z_depth_drop"]
        + out["z_abs_depth_imbalance"]
    )

    out["price_dislocation_score"] = out["z_abs_midpoint_return"]

    # --- final market stress score ---
    out["stress_score"] = (
        out["activity_score"]
        + out["liquidity_score"]
        + out["price_dislocation_score"]
    )

    cutoff = out["stress_score"].quantile(quantile_threshold)
    out["is_stress_anomaly"] = out["stress_score"] >= cutoff

    return out


def add_market_stress_scores(
    df: pd.DataFrame,
    window: int = 60,
    quantile_threshold: float = 0.98,
) -> pd.DataFrame:
    """
    Add market stress scores using trade-side features plus optional
    price/liquidity enrichment features.
    """
    if df.empty:
        return df.copy()

    required = ["bucket", "trade_count", "amount_sum", "avg_trade_size"]
    _check_columns(df, required, "market stress feature df")

    out = df.copy().sort_values("bucket").reset_index(drop=True)

    # --- trade-side core signals ---
    out["z_trade_count"] = _rolling_zscore(out["trade_count"], window=window)
    out["z_amount_sum"] = _rolling_zscore(out["amount_sum"], window=window)
    out["z_avg_trade_size"] = _rolling_zscore(out["avg_trade_size"], window=window)

    # --- optional snapshot-side signals ---
    if "spread" in out.columns:
        out["z_spread"] = _rolling_zscore(
            pd.to_numeric(out["spread"], errors="coerce"),
            window=window,
        )
    else:
        out["z_spread"] = 0.0

    if "depth_drop" in out.columns:
        out["z_depth_drop"] = _rolling_zscore(
            pd.to_numeric(out["depth_drop"], errors="coerce"),
            window=window,
        )
    else:
        out["z_depth_drop"] = 0.0

    if "abs_midpoint_return" in out.columns:
        out["z_abs_midpoint_return"] = _rolling_zscore(
            pd.to_numeric(out["abs_midpoint_return"], errors="coerce"),
            window=window,
        )
    else:
        out["z_abs_midpoint_return"] = 0.0

    if "abs_depth_imbalance" in out.columns:
        out["z_abs_depth_imbalance"] = _rolling_zscore(
            pd.to_numeric(out["abs_depth_imbalance"], errors="coerce"),
            window=window,
        )
    else:
        out["z_abs_depth_imbalance"] = 0.0

    # clean optional columns
    optional_cols = [
        "z_spread",
        "z_depth_drop",
        "z_abs_midpoint_return",
        "z_abs_depth_imbalance",
    ]
    for c in optional_cols:
        out[c] = pd.to_numeric(out[c], errors="coerce").fillna(0.0)

    # --- component scores ---
    out["activity_score"] = (
        out["z_trade_count"]
        + out["z_amount_sum"]
        + out["z_avg_trade_size"]
    )

    out["liquidity_score"] = (
        out["z_spread"]
        + out["z_depth_drop"]
        + out["z_abs_depth_imbalance"]
    )

    out["price_dislocation_score"] = out["z_abs_midpoint_return"]

    # --- final score ---
    out["stress_score"] = (
        out["activity_score"]
        + out["liquidity_score"]
        + out["price_dislocation_score"]
    )

    cutoff = out["stress_score"].quantile(quantile_threshold)
    out["is_stress_anomaly"] = out["stress_score"] >= cutoff

    return out


def add_activity_anomaly_scores(
    df: pd.DataFrame,
    window: int = 60,
    score_mode: str = "sum",
    quantile_threshold: float = 0.98,
) -> pd.DataFrame:
    """
    Add activity anomaly scores based on trade_count, amount_sum, avg_trade_size.

    Parameters
    ----------
    df : pd.DataFrame
        Bucket-level fused feature dataframe.
    window : int
        Rolling window size for z-score computation.
    score_mode : str
        "sum" or "max" for combining activity z-scores.
    quantile_threshold : float
        Percentile threshold for anomaly flagging, e.g. 0.98 means top 2%.

    Returns
    -------
    pd.DataFrame
        DataFrame with added columns:
        - z_trade_count
        - z_amount_sum
        - z_avg_trade_size
        - activity_score
        - is_activity_anomaly
    """
    if df.empty:
        return df.copy()

    _check_columns(df, REQUIRED_COLUMNS, "activity feature df")

    out = df.copy().sort_values("bucket").reset_index(drop=True)

    out["z_trade_count"] = _rolling_zscore(out["trade_count"], window=window)
    out["z_amount_sum"] = _rolling_zscore(out["amount_sum"], window=window)
    out["z_avg_trade_size"] = _rolling_zscore(out["avg_trade_size"], window=window)

    if score_mode == "max":
        out["activity_score"] = out[
            ["z_trade_count", "z_amount_sum", "z_avg_trade_size"]
        ].max(axis=1)
    else:
        out["activity_score"] = (
            out["z_trade_count"]
            + out["z_amount_sum"]
            + out["z_avg_trade_size"]
        )

    cutoff = out["activity_score"].quantile(quantile_threshold)
    out["is_activity_anomaly"] = out["activity_score"] >= cutoff

    return out

def add_pca_market_stress_scores(
    df: pd.DataFrame,
    window: int = 60,
    quantile_threshold: float = 0.98,
) -> pd.DataFrame:
    """
    Add PCA-based Composite Market Stress Index (CMSI).

    This function first computes the same z-score features used by the additive
    stress detector, then applies PCA to extract the first principal component
    as a latent market-stress factor.

    Parameters
    ----------
    df : pd.DataFrame
        Bucket-level fused feature dataframe.
    window : int
        Rolling window size for z-score computation.
    quantile_threshold : float
        Percentile threshold for anomaly flagging.

    Returns
    -------
    pd.DataFrame
        DataFrame with:
        - z_* feature columns
        - activity_score
        - liquidity_score
        - price_dislocation_score
        - stress_score (additive reference)
        - cmsi_pca_score
        - is_stress_anomaly
    """
    if df.empty:
        return df.copy()

    required = ["bucket", "trade_count", "amount_sum", "avg_trade_size"]
    _check_columns(df, required, "market stress feature df")

    out = df.copy().sort_values("bucket").reset_index(drop=True)

    # --- trade-side core signals ---
    out["z_trade_count"] = _rolling_zscore(out["trade_count"], window=window)
    out["z_amount_sum"] = _rolling_zscore(out["amount_sum"], window=window)
    out["z_avg_trade_size"] = _rolling_zscore(out["avg_trade_size"], window=window)

    # --- optional snapshot-side signals ---
    if "spread" in out.columns:
        out["z_spread"] = _rolling_zscore(
            pd.to_numeric(out["spread"], errors="coerce"),
            window=window,
        )
    else:
        out["z_spread"] = 0.0

    if "depth_drop" in out.columns:
        out["z_depth_drop"] = _rolling_zscore(
            pd.to_numeric(out["depth_drop"], errors="coerce"),
            window=window,
        )
    else:
        out["z_depth_drop"] = 0.0

    if "abs_midpoint_return" in out.columns:
        out["z_abs_midpoint_return"] = _rolling_zscore(
            pd.to_numeric(out["abs_midpoint_return"], errors="coerce"),
            window=window,
        )
    else:
        out["z_abs_midpoint_return"] = 0.0

    if "abs_depth_imbalance" in out.columns:
        out["z_abs_depth_imbalance"] = _rolling_zscore(
            pd.to_numeric(out["abs_depth_imbalance"], errors="coerce"),
            window=window,
        )
    else:
        out["z_abs_depth_imbalance"] = 0.0

    feature_cols = [
        "z_trade_count",
        "z_amount_sum",
        "z_avg_trade_size",
        "z_spread",
        "z_depth_drop",
        "z_abs_midpoint_return",
        "z_abs_depth_imbalance",
    ]

    for c in feature_cols:
        out[c] = pd.to_numeric(out[c], errors="coerce").fillna(0.0)

    # --- keep additive version as baseline/reference ---
    out["activity_score"] = (
        out["z_trade_count"]
        + out["z_amount_sum"]
        + out["z_avg_trade_size"]
    )

    out["liquidity_score"] = (
        out["z_spread"]
        + out["z_depth_drop"]
        + out["z_abs_depth_imbalance"]
    )

    out["price_dislocation_score"] = out["z_abs_midpoint_return"]

    out["stress_score"] = (
        out["activity_score"]
        + out["liquidity_score"]
        + out["price_dislocation_score"]
    )

    # --- PCA CMSI ---
    X = out[feature_cols].to_numpy(dtype=float)

    pca = PCA(n_components=1)
    pc1 = pca.fit_transform(X).reshape(-1)

    # align direction with additive stress score for interpretability
    ref = out["stress_score"].to_numpy(dtype=float)
    if np.std(pc1) > 0 and np.std(ref) > 0:
        corr = np.corrcoef(pc1, ref)[0, 1]
        if not np.isnan(corr) and corr < 0:
            pc1 = -pc1

    out["cmsi_pca_score"] = pc1

    cutoff = out["cmsi_pca_score"].quantile(quantile_threshold)
    out["is_stress_anomaly"] = out["cmsi_pca_score"] >= cutoff

    # optional metadata for analysis/debugging
    out.attrs["pca_feature_cols"] = feature_cols
    out.attrs["pca_explained_variance_ratio"] = float(
        pca.explained_variance_ratio_[0]
    )

    return out