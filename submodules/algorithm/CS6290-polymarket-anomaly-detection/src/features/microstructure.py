import numpy as np
import pandas as pd


def add_basic_features(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()

    # 价格变化（1分钟粒度）
    out["ret"] = out["midpoint"].diff()

    # 总深度 & 失衡
    out["depth_total"] = out["bid_depth_top5"] + out["ask_depth_top5"]
    out["imbalance"] = (out["bid_depth_top5"] - out["ask_depth_top5"]) / (out["depth_total"] + 1e-9)
    out["dimbalance"] = out["imbalance"].diff()

    return out


def robust_zscore(s: pd.Series, window: int) -> pd.Series:
    """rolling median + MAD 的 robust z-score"""
    med = s.rolling(window, min_periods=window).median()
    mad = (s - med).abs().rolling(window, min_periods=window).median()
    return (s - med) / (1.4826 * mad + 1e-9)
