import pandas as pd
import numpy as np
import os

# 获取当前文件所在目录 (src/)
current_dir = os.path.dirname(__file__)
# 往上一级到 sniper_detection/
module_root = os.path.dirname(current_dir)

# 读取合并后的数据（从模块根目录）
data_path = os.path.join(module_root, 'all_orders_processed.csv')
df = pd.read_csv(data_path)

print("="*50)
print("数据质量检查报告")
print("="*50)

# 1. 基本统计
print(f"\n1. 基本统计:")
print(f"   总订单数: {len(df):,}")
print(f"   唯一市场数: {df['market_id'].nunique()}")
print(f"   唯一地址数: {df['trader_address'].nunique():,}")
print(f"   时间范围: {df['datetime'].min()} 到 {df['datetime'].max()}")

# 2. 缺失值检查
print(f"\n2. 缺失值检查:")
for col in ['transaction_hash', 'trader_address', 'price', 'amount_usd', 'side']:
    missing = df[col].isna().sum()
    pct = (missing/len(df))*100
    print(f"   {col}: {missing} 条缺失 ({pct:.2f}%)")

# 3. 交易方向分布
print(f"\n3. 交易方向分布:")
print(df['side'].value_counts())

# 4. 金额分布
print(f"\n4. 金额分布 (USD):")
print(f"   最小值: ${df['amount_usd'].min():.2f}")
print(f"   25分位: ${df['amount_usd'].quantile(0.25):.2f}")
print(f"   中位数: ${df['amount_usd'].median():.2f}")
print(f"   75分位: ${df['amount_usd'].quantile(0.75):.2f}")
print(f"   最大值: ${df['amount_usd'].max():.2f}")
print(f"   平均值: ${df['amount_usd'].mean():.2f}")

# 5. 大额交易统计（≥5000 USD）
large_trades = df[df['amount_usd'] >= 5000]
print(f"\n5. 大额交易统计 (≥5000 USD):")
print(f"   数量: {len(large_trades)} 条")
print(f"   占比: {(len(large_trades)/len(df))*100:.2f}%")
print(f"   总金额: ${large_trades['amount_usd'].sum():,.2f}")

# 6. 按市场统计
print(f"\n6. 前10个最活跃市场:")
market_stats = df.groupby('market_id').agg({
    'transaction_hash': 'count',
    'amount_usd': 'sum',
    'trader_address': 'nunique'
}).rename(columns={
    'transaction_hash': '交易数',
    'amount_usd': '总金额',
    'trader_address': '独立地址数'
}).sort_values('交易数', ascending=False).head(10)
print(market_stats)

# 7. 按地址统计
print(f"\n7. 前10个最活跃地址:")
addr_stats = df.groupby('trader_address').agg({
    'transaction_hash': 'count',
    'amount_usd': ['sum', 'max']
}).round(2)
addr_stats.columns = ['交易数', '总金额', '最大单笔']
addr_stats = addr_stats.sort_values('交易数', ascending=False).head(10)
print(addr_stats)

# 8. 检查是否有狙击手候选
print(f"\n8. 狙击手候选统计:")
# 新地址特征（需要额外数据，这里先简单统计）
addr_first_seen = df.groupby('trader_address')['timestamp'].min().to_dict()
df['is_first_trade'] = df.apply(
    lambda row: row['timestamp'] == addr_first_seen.get(row['trader_address'], 0),
    axis=1
)

sniper_candidates = df[
    (df['amount_usd'] >= 5000) &  # 大额
    (df['is_first_trade'])         # 可能是新地址
]
print(f"   大额且可能是首次交易: {len(sniper_candidates)} 条")
print(f"   涉及地址数: {sniper_candidates['trader_address'].nunique()}")

print("\n" + "="*50)
print("检查完成！")