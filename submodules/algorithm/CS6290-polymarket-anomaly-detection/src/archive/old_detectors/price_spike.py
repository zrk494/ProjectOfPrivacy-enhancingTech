import pandas as pd
from src.features.microstructure import robust_zscore, add_basic_features


def detect_price_spikes(
    df: pd.DataFrame,
    z_window: int = 60,          # 60分钟 baseline
    z_thresh: float = 3.5,
    spread_window: int = 120,    # 用更长窗口判断“spread是否异常”
    spread_z_thresh: float = 3.0,
    depth_drop_ratio: float = 0.5  # 总深度 < 过去中位数的50% 认为薄盘
) -> pd.DataFrame:
    x = add_basic_features(df)

    # 对 ret 做 robust z
    x["ret_z"] = robust_zscore(x["ret"], window=z_window)

    # spread 异常程度
    x["spread_z"] = robust_zscore(x["spread"], window=spread_window)

    # depth 是否塌陷（用滚动中位数做基线）
    depth_med = x["depth_total"].rolling(spread_window, min_periods=spread_window).median()
    x["depth_drop"] = x["depth_total"] < (depth_med * depth_drop_ratio)

    # spike 候选点
    x["is_spike"] = x["ret_z"].abs() > z_thresh

    # 分类：薄盘假跳 vs 信息驱动
    x["spike_type"] = "none"
    thin = x["is_spike"] & (x["spread_z"] > spread_z_thresh) & (x["depth_drop"])
    informed = x["is_spike"] & (~thin)

    x.loc[thin, "spike_type"] = "price_spike_thin_book"
    x.loc[informed, "spike_type"] = "price_spike_informed"

    return x
