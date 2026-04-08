from __future__ import annotations

import pandas as pd


def _safe_numeric(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce")


def _get_component_series(
    scored: pd.DataFrame,
    preferred_col: str,
    fallback_cols: list[str],
) -> pd.Series:
    """
    Return a numeric component series.

    Priority:
    1) preferred component column if present
    2) sum of fallback z-score columns if present
    3) zeros
    """
    if preferred_col in scored.columns:
        return _safe_numeric(scored[preferred_col]).fillna(0.0)

    existing = [c for c in fallback_cols if c in scored.columns]
    if existing:
        out = pd.Series(0.0, index=scored.index, dtype="float64")
        for c in existing:
            out = out + _safe_numeric(scored[c]).fillna(0.0)
        return out

    return pd.Series(0.0, index=scored.index, dtype="float64")


def _dominant_driver_label(
    peak_activity: float,
    peak_liquidity: float,
    peak_price: float,
    dominance_ratio: float = 1.15,
) -> str:
    """
    Decide which component dominates the event.

    If the top component is not sufficiently larger than the second-largest
    component, label it as 'mixed'.
    """
    vals = {
        "activity": float(peak_activity) if pd.notna(peak_activity) else 0.0,
        "liquidity": float(peak_liquidity) if pd.notna(peak_liquidity) else 0.0,
        "price_dislocation": float(peak_price) if pd.notna(peak_price) else 0.0,
    }

    ranked = sorted(vals.items(), key=lambda x: x[1], reverse=True)
    top_name, top_val = ranked[0]
    second_name, second_val = ranked[1]

    if top_val <= 0:
        return "mixed"

    # If top is only slightly above second, treat as mixed
    if second_val > 0 and top_val < dominance_ratio * second_val:
        return "mixed"

    return top_name


def enrich_activity_events_with_snapshots(
    events: pd.DataFrame,
    scored: pd.DataFrame,
) -> pd.DataFrame:
    """
    Enrich event-level summaries with snapshot diagnostics and component-level
    attribution.

    Required columns in events:
    - start
    - end

    Useful columns in scored:
    - bucket
    - midpoint
    - spread
    - total_depth
    - abs_midpoint_return
    - abs_depth_imbalance
    - activity_score / liquidity_score / price_dislocation_score
      OR their fallback z-score columns

    Returns
    -------
    pd.DataFrame
        Original event table plus snapshot context and attribution columns.
    """
    if events is None or events.empty:
        return events.copy()

    if scored is None or scored.empty:
        out = events.copy()
        # snapshot enrichment placeholders
        out["snapshot_covered"] = False
        out["num_snapshot_buckets"] = 0
        out["max_abs_midpoint_return"] = pd.NA
        out["max_spread"] = pd.NA
        out["min_total_depth"] = pd.NA
        out["max_abs_depth_imbalance"] = pd.NA

        # attribution placeholders
        out["peak_activity_component"] = pd.NA
        out["peak_liquidity_component"] = pd.NA
        out["peak_price_component"] = pd.NA
        out["mean_activity_component"] = pd.NA
        out["mean_liquidity_component"] = pd.NA
        out["mean_price_component"] = pd.NA
        out["dominant_driver"] = pd.NA
        return out

    if "bucket" not in scored.columns:
        raise ValueError("scored dataframe must contain column 'bucket'")

    if "start" not in events.columns or "end" not in events.columns:
        raise ValueError("events dataframe must contain columns 'start' and 'end'")

    out = events.copy()
    scored = scored.copy().sort_values("bucket").reset_index(drop=True)

    # -------------------------------------------------
    # Build component series for attribution
    # -------------------------------------------------
    scored["_activity_component"] = _get_component_series(
        scored,
        preferred_col="activity_score",
        fallback_cols=["z_trade_count", "z_amount_sum", "z_avg_trade_size"],
    )

    scored["_liquidity_component"] = _get_component_series(
        scored,
        preferred_col="liquidity_score",
        fallback_cols=["z_spread", "z_depth_drop", "z_abs_depth_imbalance"],
    )

    scored["_price_component"] = _get_component_series(
        scored,
        preferred_col="price_dislocation_score",
        fallback_cols=["z_abs_midpoint_return"],
    )

    # -------------------------------------------------
    # Snapshot coverage mask
    # -------------------------------------------------
    snapshot_signal_cols = [
        c for c in ["midpoint", "spread", "total_depth", "depth_imbalance"]
        if c in scored.columns
    ]

    if snapshot_signal_cols:
        scored["_has_snapshot"] = scored[snapshot_signal_cols].notna().any(axis=1)
    else:
        scored["_has_snapshot"] = False

    # -------------------------------------------------
    # Event-level enrichment
    # -------------------------------------------------
    snapshot_covered = []
    num_snapshot_buckets = []
    max_abs_midpoint_return = []
    max_spread = []
    min_total_depth = []
    max_abs_depth_imbalance = []

    peak_activity_component = []
    peak_liquidity_component = []
    peak_price_component = []

    mean_activity_component = []
    mean_liquidity_component = []
    mean_price_component = []

    dominant_driver = []

    for _, row in out.iterrows():
        start_bucket = row["start"]
        end_bucket = row["end"]

        window_df = scored[
            (scored["bucket"] >= start_bucket) & (scored["bucket"] <= end_bucket)
        ].copy()

        if window_df.empty:
            snapshot_covered.append(False)
            num_snapshot_buckets.append(0)
            max_abs_midpoint_return.append(pd.NA)
            max_spread.append(pd.NA)
            min_total_depth.append(pd.NA)
            max_abs_depth_imbalance.append(pd.NA)

            peak_activity_component.append(pd.NA)
            peak_liquidity_component.append(pd.NA)
            peak_price_component.append(pd.NA)

            mean_activity_component.append(pd.NA)
            mean_liquidity_component.append(pd.NA)
            mean_price_component.append(pd.NA)

            dominant_driver.append(pd.NA)
            continue

        snap_df = window_df[window_df["_has_snapshot"]].copy()

        snapshot_covered.append(not snap_df.empty)
        num_snapshot_buckets.append(int(len(snap_df)))

        if not snap_df.empty:
            if "abs_midpoint_return" in snap_df.columns:
                max_abs_midpoint_return.append(
                    _safe_numeric(snap_df["abs_midpoint_return"]).max()
                )
            else:
                max_abs_midpoint_return.append(pd.NA)

            if "spread" in snap_df.columns:
                max_spread.append(_safe_numeric(snap_df["spread"]).max())
            else:
                max_spread.append(pd.NA)

            if "total_depth" in snap_df.columns:
                min_total_depth.append(_safe_numeric(snap_df["total_depth"]).min())
            else:
                min_total_depth.append(pd.NA)

            if "abs_depth_imbalance" in snap_df.columns:
                max_abs_depth_imbalance.append(
                    _safe_numeric(snap_df["abs_depth_imbalance"]).max()
                )
            elif "depth_imbalance" in snap_df.columns:
                max_abs_depth_imbalance.append(
                    _safe_numeric(snap_df["depth_imbalance"]).abs().max()
                )
            else:
                max_abs_depth_imbalance.append(pd.NA)
        else:
            max_abs_midpoint_return.append(pd.NA)
            max_spread.append(pd.NA)
            min_total_depth.append(pd.NA)
            max_abs_depth_imbalance.append(pd.NA)

        # ------------------------------
        # Component attribution
        # ------------------------------
        a = _safe_numeric(window_df["_activity_component"]).fillna(0.0)
        l = _safe_numeric(window_df["_liquidity_component"]).fillna(0.0)
        p = _safe_numeric(window_df["_price_component"]).fillna(0.0)

        pa = float(a.max()) if len(a) > 0 else 0.0
        pl = float(l.max()) if len(l) > 0 else 0.0
        pp = float(p.max()) if len(p) > 0 else 0.0

        ma = float(a.mean()) if len(a) > 0 else 0.0
        ml = float(l.mean()) if len(l) > 0 else 0.0
        mp = float(p.mean()) if len(p) > 0 else 0.0

        peak_activity_component.append(pa)
        peak_liquidity_component.append(pl)
        peak_price_component.append(pp)

        mean_activity_component.append(ma)
        mean_liquidity_component.append(ml)
        mean_price_component.append(mp)

        dominant_driver.append(
            _dominant_driver_label(
                peak_activity=pa,
                peak_liquidity=pl,
                peak_price=pp,
                dominance_ratio=1.15,
            )
        )

    out["snapshot_covered"] = snapshot_covered
    out["num_snapshot_buckets"] = num_snapshot_buckets
    out["max_abs_midpoint_return"] = max_abs_midpoint_return
    out["max_spread"] = max_spread
    out["min_total_depth"] = min_total_depth
    out["max_abs_depth_imbalance"] = max_abs_depth_imbalance

    out["peak_activity_component"] = peak_activity_component
    out["peak_liquidity_component"] = peak_liquidity_component
    out["peak_price_component"] = peak_price_component

    out["mean_activity_component"] = mean_activity_component
    out["mean_liquidity_component"] = mean_liquidity_component
    out["mean_price_component"] = mean_price_component

    out["dominant_driver"] = dominant_driver

    return out