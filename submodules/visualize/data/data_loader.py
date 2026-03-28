import streamlit as st
import pandas as pd
import os
from config import (
    MARKET_METADATA_PATH,
    get_timeseries_path,
    get_trade_path,
    CACHE_TTL,
    LANGUAGES
)

@st.cache_data(ttl=CACHE_TTL)
def load_market_metadata(lang):
    """加载市场元数据"""
    if os.path.exists(MARKET_METADATA_PATH):
        df = pd.read_csv(MARKET_METADATA_PATH)
        return df
    else:
        st.error(f"{LANGUAGES[lang]['error_file_not_found']}: {MARKET_METADATA_PATH}")
        return pd.DataFrame()

@st.cache_data(ttl=CACHE_TTL)
def load_timeseries_data(market_id, token_type="YES"):
    """加载时间序列数据"""
    data_path = get_timeseries_path(market_id, token_type)
    if os.path.exists(data_path):
        df = pd.read_csv(data_path)
        df['datetime'] = pd.to_datetime(df['datetime'])
        return df
    else:
        return pd.DataFrame()

@st.cache_data(ttl=CACHE_TTL)
def load_trade_data(market_id, token_type="YES"):
    """加载交易数据"""
    data_path = get_trade_path(market_id, token_type)
    if os.path.exists(data_path):
        df = pd.read_csv(data_path)
        df['datetime'] = pd.to_datetime(df['datetime'])
        return df
    else:
        return pd.DataFrame()

@st.cache_data(ttl=CACHE_TTL)
def load_polymarket_anomaly_data(market_id, score_method="additive"):
    """加载多市场异常检测数据"""
    from config import get_polymarket_anomaly_path
    data_path = get_polymarket_anomaly_path(market_id, score_method)
    if os.path.exists(data_path):
        df = pd.read_csv(data_path)
        if 'start_datetime' in df.columns:
            df['start_datetime'] = pd.to_datetime(df['start_datetime'])
        if 'end_datetime' in df.columns:
            df['end_datetime'] = pd.to_datetime(df['end_datetime'])
        return df
    else:
        return pd.DataFrame()

@st.cache_data(ttl=CACHE_TTL)
def load_sniper_detection_data():
    """加载狙击手检测数据"""
    from config import SNIPER_CANDIDATES_PATH
    data_path = SNIPER_CANDIDATES_PATH
    if os.path.exists(data_path):
        df = pd.read_csv(data_path)
        return df
    else:
        return pd.DataFrame()

@st.cache_data(ttl=CACHE_TTL)
def load_sniper_detailed_cases():
    """加载狙击手检测详细案例"""
    import json
    from config import SNIPER_DETAILED_CASES_PATH
    data_path = SNIPER_DETAILED_CASES_PATH
    if os.path.exists(data_path):
        with open(data_path, 'r', encoding='utf-8') as f:
            cases = json.load(f)
        return cases
    else:
        return []

@st.cache_data(ttl=CACHE_TTL)
def load_sniper_all_cases():
    """加载所有狙击手候选案例"""
    import json
    from config import SNIPER_ALL_CASES_PATH
    data_path = SNIPER_ALL_CASES_PATH
    if os.path.exists(data_path):
        with open(data_path, 'r', encoding='utf-8') as f:
            cases = json.load(f)
        return cases
    else:
        return []

@st.cache_data(ttl=CACHE_TTL)
def load_bucket_features(market_id, score_method="additive"):
    """加载 bucket 特征数据"""
    from config import get_bucket_features_path
    data_path = get_bucket_features_path(market_id, score_method)
    if os.path.exists(data_path):
        df = pd.read_csv(data_path)
        if 'datetime' in df.columns:
            df['datetime'] = pd.to_datetime(df['datetime'])
        return df
    else:
        return pd.DataFrame()

@st.cache_data(ttl=CACHE_TTL)
def load_bucket_scores(market_id, score_method="additive"):
    """加载 bucket 分数数据"""
    from config import get_bucket_scores_path
    data_path = get_bucket_scores_path(market_id, score_method)
    if os.path.exists(data_path):
        df = pd.read_csv(data_path)
        if 'datetime' in df.columns:
            df['datetime'] = pd.to_datetime(df['datetime'])
        return df
    else:
        return pd.DataFrame()

@st.cache_data(ttl=CACHE_TTL)
def load_market_stress_summary(score_method="additive"):
    """加载市场压力汇总数据"""
    from config import get_market_stress_summary_path
    data_path = get_market_stress_summary_path(score_method)
    if os.path.exists(data_path):
        df = pd.read_csv(data_path)
        return df
    else:
        return pd.DataFrame()

@st.cache_data(ttl=CACHE_TTL)
def load_all_stress_events(score_method="additive"):
    """加载所有压力事件总表"""
    from config import get_all_stress_events_path
    data_path = get_all_stress_events_path(score_method)
    if os.path.exists(data_path):
        df = pd.read_csv(data_path)
        if 'start_datetime' in df.columns:
            df['start_datetime'] = pd.to_datetime(df['start_datetime'])
        if 'end_datetime' in df.columns:
            df['end_datetime'] = pd.to_datetime(df['end_datetime'])
        return df
    else:
        return pd.DataFrame()