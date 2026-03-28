# 应用配置

# 页面配置
PAGE_TITLE = "Polymarket Signal Analysis"
PAGE_LAYOUT = "wide"
PAGE_ICON = "📊"

# 缓存配置
CACHE_TTL = 3600  # 缓存过期时间（秒）

# 数据加载配置
DEFAULT_TOKEN_TYPE = "YES"
PAGE_SIZE = 50  # 交易记录分页大小

# 异常检测配置
DEFAULT_SCORE_METHOD = "additive"  # 多市场异常检测评分方法

# 图表配置
PRICE_CHART_HEIGHT = 600
VOLUME_CHART_HEIGHT = 400

# 语言配置
DEFAULT_LANGUAGE = "en"
AVAILABLE_LANGUAGES = ["en", "zh"]

# 视图配置
VIEW_OPTIONS = ["metadata", "timeseries", "trade", "anomaly"]

# 异常检测模式
ANOMALY_PATTERNS = {
    "pattern_a": "Front-running/Insider Trading Detection",
    "pattern_b": "Arbitrage Opportunity Detection"
}

# 错误消息配置
ERROR_MESSAGES = {
    "metadata_not_found": "Market metadata file not found",
    "data_not_found": "No data found for the selected market",
    "load_failed": "Failed to load data"
}

# 警告消息配置
WARNING_MESSAGES = {
    "no_timeseries_data": "No time series data found for the selected market",
    "no_trade_data": "No trade data found for the selected market"
}