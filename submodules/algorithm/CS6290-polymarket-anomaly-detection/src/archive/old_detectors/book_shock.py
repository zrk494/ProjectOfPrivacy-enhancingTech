import pandas as pd
from src.features.microstructure import robust_zscore, add_basic_features


def detect_book_shocks(
    df: pd.DataFrame,
    spread_window: int = 120,
    spread_z_thresh: float = 3.5,
    imb_window: int = 120,
    imb_z_thresh: float = 3.5,
    depth_drop_ratio: float = 0.5
) -> pd.DataFrame:
    x = add_basic_features(df)

    x["spread_z"] = robust_zscore(x["spread"], window=spread_window)
    x["dimb_z"] = robust_zscore(x["dimbalance"], window=imb_window)

    depth_med = x["depth_total"].rolling(spread_window, min_periods=spread_window).median()
    x["depth_drop"] = x["depth_total"] < (depth_med * depth_drop_ratio)

    x["shock_type"] = "none"

    liquidity_crunch = (x["spread_z"] > spread_z_thresh) & (x["depth_drop"])
    imbalance_shock = (x["dimb_z"].abs() > imb_z_thresh)

    x.loc[liquidity_crunch, "shock_type"] = "liquidity_crunch"
    x.loc[imbalance_shock & ~liquidity_crunch, "shock_type"] = "order_imbalance_shock"

    return x
