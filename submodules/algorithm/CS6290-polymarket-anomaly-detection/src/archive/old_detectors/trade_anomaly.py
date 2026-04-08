import pandas as pd
from src.preprocessing.aggregate_trades import robust_zscore
import numpy as np



def detect_trade_burst(ts: pd.DataFrame, window: int = 60, z_thresh: float = 4.0) -> pd.DataFrame:
    x = ts.copy()

    # 只用 trade_count
    x["z_count"] = robust_zscore(
        x["trade_count"].astype(float),
        window,
        mad_floor=1.0   # 对整数序列必须给一个合理 floor
    )

    x["is_burst"] = x["z_count"] > z_thresh

    return x


def detect_trade_price_jump(ts: pd.DataFrame, window: int = 60, z_thresh: float = 3.5) -> pd.DataFrame:
    x = ts.copy()

    p = x["vwap"].clip(1e-6, 1 - 1e-6)
    x["logit_vwap"] = np.log(p / (1 - p))

    x["ret"] = x["logit_vwap"].diff()
    x["z_ret"] = robust_zscore(x["ret"], window, mad_floor=1e-3)

    x["is_jump"] = x["z_ret"].abs() > z_thresh
    return x