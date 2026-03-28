import pandas as pd
import numpy as np

def filter_timeseries_data(df, start_date=None, end_date=None):
    """过滤时间序列数据"""
    if df.empty:
        return df
    
    filtered_df = df.copy()
    
    if start_date:
        filtered_df = filtered_df[filtered_df['datetime'] >= start_date]
    if end_date:
        filtered_df = filtered_df[filtered_df['datetime'] <= end_date]
    
    return filtered_df

def aggregate_trade_data(df, time_freq='H'):
    """聚合交易数据"""
    if df.empty:
        return df
    
    df['datetime'] = pd.to_datetime(df['datetime'])
    
    # 按时间频率聚合
    aggregated = df.set_index('datetime').resample(time_freq).agg({
        'price': 'mean',
        'size': 'sum',
        'amount': 'sum'
    }).reset_index()
    
    return aggregated

def calculate_trade_statistics(df):
    """计算交易统计信息"""
    if df.empty:
        return {
            'total_trades': 0,
            'total_amount': 0,
            'avg_price': 0,
            'buy_volume': 0,
            'sell_volume': 0
        }
    
    buy_trades = df[df['side'] == 'BUY']
    sell_trades = df[df['side'] == 'SELL']
    
    return {
        'total_trades': len(df),
        'total_amount': df['amount'].sum(),
        'avg_price': df['price'].mean(),
        'buy_volume': buy_trades['amount'].sum(),
        'sell_volume': sell_trades['amount'].sum()
    }

def calculate_timeseries_statistics(df):
    """计算时间序列统计信息"""
    if df.empty:
        return {
            'data_points': 0,
            'time_range': None,
            'avg_midpoint': 0
        }
    
    return {
        'data_points': len(df),
        'time_range': (df['datetime'].min(), df['datetime'].max()),
        'avg_midpoint': df['midpoint'].mean()
    }

def merge_yes_no_data(yes_df, no_df):
    """合并YES和NO合约数据"""
    if yes_df.empty or no_df.empty:
        return pd.DataFrame()
    
    # 按时间合并
    merged = pd.merge(
        yes_df[['datetime', 'midpoint']],
        no_df[['datetime', 'midpoint']],
        on='datetime',
        suffixes=('_yes', '_no')
    )
    
    # 计算套利机会
    merged['arbitrage_opportunity'] = abs(merged['midpoint_yes'] + merged['midpoint_no'] - 1)
    
    return merged

def process_anomaly_data(df):
    """处理异常检测数据"""
    if df.empty:
        return df
    
    processed_df = df.copy()
    
    # 计算异常持续时间（如果有开始和结束时间）
    if 'start_datetime' in processed_df.columns and 'end_datetime' in processed_df.columns:
        processed_df['duration_minutes'] = (
            processed_df['end_datetime'] - processed_df['start_datetime']
        ).dt.total_seconds() / 60
    
    return processed_df