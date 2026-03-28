import os
from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).resolve().parents[3]

# 数据路径
DATA_ROOT = PROJECT_ROOT / "submodules" / "data" / "polymarket_data"
MARKET_METADATA_PATH = DATA_ROOT / "market_metadata.csv"
TIMESERIES_DIR = DATA_ROOT / "timeseries"
TRADES_DIR = DATA_ROOT / "trades"

# Algorithm子模块路径
ALGORITHM_ROOT = PROJECT_ROOT / "submodules" / "algorithm"

# 异常检测数据路径
POLYMARKET_ANOMALY_DIR = ALGORITHM_ROOT / "CS6290-polymarket-anomaly-detection" / "results" / "activity_pipeline_batch"
# 狙击手检测数据路径（使用frontend_sniper_detection）
FRONTEND_SNIPER_DIR = PROJECT_ROOT / "submodules" / "visualize" / "frontend_sniper_detection"
SNIPER_CANDIDATES_PATH = FRONTEND_SNIPER_DIR / "stats" / "strict_sniper_candidates.csv"
SNIPER_DETAILED_CASES_PATH = FRONTEND_SNIPER_DIR / "detailed_cases.json"
SNIPER_ALL_CASES_PATH = FRONTEND_SNIPER_DIR / "all_cases.json"
SNIPER_IMAGES_DIR = FRONTEND_SNIPER_DIR / "images"

# 确保目录存在
os.makedirs(TIMESERIES_DIR, exist_ok=True)
os.makedirs(TRADES_DIR, exist_ok=True)
os.makedirs(POLYMARKET_ANOMALY_DIR, exist_ok=True)
os.makedirs(FRONTEND_SNIPER_DIR, exist_ok=True)

# 获取时间序列数据文件路径
def get_timeseries_path(market_id, token_type="YES"):
    """获取时间序列数据文件路径"""
    return TIMESERIES_DIR / f"{market_id}_{token_type}.csv"

# 获取交易数据文件路径
def get_trade_path(market_id, token_type="YES"):
    """获取交易数据文件路径"""
    return TRADES_DIR / f"{market_id}_{token_type}.csv"

# 获取多市场异常检测结果文件路径
def get_polymarket_anomaly_path(market_id, score_method="additive"):
    """获取多市场异常检测结果文件路径"""
    market_dir = POLYMARKET_ANOMALY_DIR / f"{market_id}_YES"
    os.makedirs(market_dir, exist_ok=True)
    return market_dir / f"stress_events_enriched_{score_method}.csv"

# 获取 bucket 特征文件路径
def get_bucket_features_path(market_id, score_method="additive"):
    """获取 bucket 特征文件路径"""
    market_dir = POLYMARKET_ANOMALY_DIR / f"{market_id}_YES"
    os.makedirs(market_dir, exist_ok=True)
    return market_dir / f"bucket_features_{score_method}.csv"

# 获取 bucket 分数文件路径
def get_bucket_scores_path(market_id, score_method="additive"):
    """获取 bucket 分数文件路径"""
    market_dir = POLYMARKET_ANOMALY_DIR / f"{market_id}_YES"
    os.makedirs(market_dir, exist_ok=True)
    return market_dir / f"bucket_scores_{score_method}.csv"

# 获取市场压力汇总文件路径
def get_market_stress_summary_path(score_method="additive"):
    """获取市场压力汇总文件路径"""
    return POLYMARKET_ANOMALY_DIR / f"market_stress_summary_{score_method}.csv"

# 获取所有压力事件总表文件路径
def get_all_stress_events_path(score_method="additive"):
    """获取所有压力事件总表文件路径"""
    return POLYMARKET_ANOMALY_DIR / f"all_stress_events_{score_method}.csv"

