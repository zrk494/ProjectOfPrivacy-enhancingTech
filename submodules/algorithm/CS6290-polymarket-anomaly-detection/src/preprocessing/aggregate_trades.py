from __future__ import annotations
from dataclasses import dataclass
import pandas as pd
import numpy as np

from pathlib import Path


def load_and_aggregate_trades(
    csv_path: str | Path,
    bucket_seconds: int = 60,
) -> pd.DataFrame:
    """
    Convenience wrapper to load a trade CSV and aggregate it.
    """
    csv_path = Path(csv_path)
    df = pd.read_csv(csv_path)
    return aggregate_trades(df, bucket_seconds=bucket_seconds)
def aggregate_trades(df: pd.DataFrame, bucket_seconds: int = 60) -> pd.DataFrame:
    """
    把逐笔成交聚合成固定时间桶（支持同一秒多笔成交）。
    需要字段：timestamp, price, size, amount(可选)
    """
    x = df.copy()

    x["timestamp"] = pd.to_numeric(x["timestamp"], errors="coerce")
    x = x.dropna(subset=["timestamp", "price", "size"])

    # 时间桶：例如 60s
    x["bucket"] = (x["timestamp"] // bucket_seconds) * bucket_seconds

    # amount 若缺失就补
    if "amount" not in x.columns:
        x["amount"] = x["price"] * x["size"]

    # VWAP
    x["px_size"] = x["price"] * x["size"]

    g = x.groupby("bucket").agg(
        trade_count=("timestamp", "count"),
        size_sum=("size", "sum"),
        amount_sum=("amount", "sum"),
        px_size_sum=("px_size", "sum"),
    ).reset_index()

    g["vwap"] = g["px_size_sum"] / (g["size_sum"] + 1e-9)
    g = g.drop(columns=["px_size_sum"])

    return g.sort_values("bucket").reset_index(drop=True)


def robust_zscore(s: pd.Series, window: int, mad_floor: float = 1e-6) -> pd.Series:
    med = s.rolling(window, min_periods=window).median()
    mad = (s - med).abs().rolling(window, min_periods=window).median()

    # 关键：避免 MAD = 0 导致 z 爆炸
    mad = mad.clip(lower=mad_floor)

    return (s - med) / (1.4826 * mad + 1e-12)
