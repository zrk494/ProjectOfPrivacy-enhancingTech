import pandas as pd
from datetime import timedelta
import numpy as np
import os

# 获取当前文件所在目录 (src/)
current_dir = os.path.dirname(__file__)
# 往上一级到 sniper_detection/
module_root = os.path.dirname(current_dir)


def create_sessions(input_file='all_orders_processed.csv',
                    output_file='orders_with_session.csv',
                    session_threshold_minutes=30):
    """
    将原始订单数据按地址和时间切割成会话

    Parameters:
    -----------
    input_file : str
        处理后的订单CSV文件路径（含trader_address）
    output_file : str
        输出文件路径
    session_threshold_minutes : int
        会话切割阈值（分钟），超过此时间间隔则切分为新会话

    Returns:
    --------
    df : DataFrame
        添加了session_id的订单数据
    """

    # 1. 读取数据（使用模块根目录的路径）
    input_path = os.path.join(module_root, input_file)
    print(f"正在读取数据: {input_path}")
    df = pd.read_csv(input_path)

    # 必要字段检查
    required_cols = ['transaction_hash', 'trader_address', 'price',
                     'amount_usd', 'timestamp', 'market_id']
    for col in required_cols:
        if col not in df.columns:
            # 尝试可能的替代列名
            if col == 'transaction_hash' and 'tx_hash' in df.columns:
                df.rename(columns={'tx_hash': 'transaction_hash'}, inplace=True)
            elif col == 'amount_usd' and 'amount' in df.columns:
                df.rename(columns={'amount': 'amount_usd'}, inplace=True)
            else:
                raise ValueError(f"缺少必要字段: {col}")

    # 2. 时间格式处理
    print("处理时间格式...")
    if 'datetime' in df.columns:
        df['timestamp'] = pd.to_datetime(df['datetime'])
    else:
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')

    df = df.sort_values(['trader_address', 'timestamp'])

    # 3. 计算相邻交易时间差
    print("计算交易间隔...")
    df['time_diff'] = df.groupby('trader_address')['timestamp'].diff()

    # 4. 会话切割：超过阈值或第一条交易标记为新会话
    threshold = timedelta(minutes=session_threshold_minutes)
    df['new_session'] = (df['time_diff'] > threshold) | (df['time_diff'].isna())

    # 5. 生成会话ID (地址_会话序号)
    print("生成会话ID...")
    df['session_id'] = df.groupby('trader_address')['new_session'].cumsum().astype(str)
    df['session_id'] = df['trader_address'] + '_' + df['session_id']

    # 6. 计算会话内订单间隔（用于后续特征工程）
    df['next_timestamp'] = df.groupby('session_id')['timestamp'].shift(-1)
    df['next_interval'] = (df['next_timestamp'] - df['timestamp']).dt.total_seconds()
    df['next_interval'] = df['next_interval'].fillna(0)

    # 7. 计算会话内的一些统计特征（立即可用）
    print("计算会话内统计...")
    session_stats = df.groupby('session_id').agg({
        'amount_usd': ['count', 'sum', 'max'],
        'price': ['first', 'last', 'max', 'min'],
        'timestamp': ['min', 'max']
    })
    session_stats.columns = ['_'.join(col).strip() for col in session_stats.columns.values]

    # 将会话统计合并回原数据
    df = df.merge(session_stats, on='session_id', how='left')

    # 8. 添加一些有用的标记
    df['session_duration'] = (df['timestamp_max'] - df['timestamp_min']).dt.total_seconds()
    df['session_price_change'] = df['price_last'] - df['price_first']
    df['session_price_change_pct'] = (df['session_price_change'] / df['price_first']) * 100
    df['is_large_trade'] = df['amount_usd'] >= 5000

    # 9. 统计信息
    total_sessions = df['session_id'].nunique()
    avg_orders_per_session = len(df) / total_sessions

    print(f"\n=== 会话切割完成 ===")
    print(f"原始订单数: {len(df)}")
    print(f"会话数: {total_sessions}")
    print(f"平均每会话订单数: {avg_orders_per_session:.2f}")
    print(f"最大会话订单数: {df.groupby('session_id').size().max()}")
    print(f"会话持续时间范围: {df['session_duration'].min():.0f} - {df['session_duration'].max():.0f} 秒")

    # 10. 保存结果到模块根目录
    output_path = os.path.join(module_root, output_file)
    df.to_csv(output_path, index=False)
    print(f"结果已保存至: {output_path}")

    return df


def get_session_summary(df):
    """
    生成会话级别摘要统计（用于快速查看）
    """
    session_summary = df.groupby('session_id').agg({
        'trader_address': 'first',
        'market_id': 'first',
        'timestamp': ['min', 'max'],
        'amount_usd': ['sum', 'max', 'mean', 'count'],
        'price': ['first', 'last', 'max', 'min', 'mean'],
        'next_interval': ['sum', 'mean'],
        'session_duration': 'first',
        'session_price_change': 'first',
        'is_large_trade': 'max'
    }).round(4)

    # 扁平化列名
    session_summary.columns = ['_'.join(col).strip() for col in session_summary.columns.values]
    session_summary = session_summary.reset_index()

    # 重新命名一些列使其更清晰
    session_summary = session_summary.rename(columns={
        'amount_usd_sum': 'total_volume',
        'amount_usd_max': 'max_trade',
        'amount_usd_mean': 'avg_trade',
        'amount_usd_count': 'num_trades',
        'next_interval_mean': 'avg_interval_seconds',
        'is_large_trade_max': 'has_large_trade'
    })

    return session_summary


def filter_sessions_by_activity(df, min_trades=2, max_trades=20):
    """
    过滤出符合条件的会话（用于后续分析）
    """
    session_sizes = df.groupby('session_id').size()
    valid_sessions = session_sizes[
        (session_sizes >= min_trades) &
        (session_sizes <= max_trades)
        ].index

    filtered_df = df[df['session_id'].isin(valid_sessions)]
    print(f"过滤后: {len(filtered_df)} 条订单, {len(valid_sessions)} 个会话")
    return filtered_df


if __name__ == "__main__":
    # 检查文件是否存在
    input_path = os.path.join(module_root, 'all_orders_processed.csv')
    if os.path.exists(input_path):
        # 1. 创建会话
        df = create_sessions('all_orders_processed.csv')

        # 2. 生成会话摘要
        summary = get_session_summary(df)
        summary_path = os.path.join(module_root, 'session_summary.csv')
        summary.to_csv(summary_path, index=False)
        print(f"\n会话摘要已保存至: {summary_path}")

        # 3. 显示一些基本统计
        print("\n=== 会话统计 ===")
        print(f"总会话数: {len(summary)}")
        print(f"包含大额交易的会话数: {summary['has_large_trade'].sum()}")
        print(f"平均会话交易数: {summary['num_trades'].mean():.2f}")
        print(f"平均会话金额: ${summary['total_volume'].mean():.2f}")
        print(f"最大单笔交易: ${summary['max_trade'].max():.2f}")

        # 4. 可选：过滤出有意义的会话
        filtered_df = filter_sessions_by_activity(df, min_trades=2)
        filtered_path = os.path.join(module_root, 'orders_filtered.csv')
        filtered_df.to_csv(filtered_path, index=False)
        print(f"过滤后的订单已保存至: {filtered_path}")
    else:
        print(f"❌ 请先运行 prepare_data.py 生成 all_orders_processed.csv")
        print(f"查找路径: {input_path}")