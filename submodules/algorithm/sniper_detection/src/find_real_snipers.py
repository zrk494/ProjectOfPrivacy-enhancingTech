import pandas as pd
import numpy as np
import os

# 获取当前文件所在目录 (src/)
current_dir = os.path.dirname(__file__)
# 往上一级到 sniper_detection/
module_root = os.path.dirname(current_dir)

# 读取数据
results_path = os.path.join(module_root, 'sniper_detection_results.csv')
orders_path = os.path.join(module_root, 'orders_with_session.csv')

results = pd.read_csv(results_path)
orders = pd.read_csv(orders_path)

# 严格狙击手定义
snipers = results[
    (results['has_large_trade'] == True) &  # 有大额交易
    (results['first_side'] == 'BUY') &  # 先买
    (results['last_side'] == 'SELL') &  # 后卖
    (results['num_trades'] >= 2)  # 至少2笔交易
    ].copy()

print("=" * 60)
print("🔍 严格定义的狙击手候选")
print("=" * 60)
print(f"\n符合条件的会话数: {len(snipers)}")

# 按异常分数排序
snipers = snipers.sort_values('anomaly_score')

# 显示详细信息
for idx, row in snipers.head(10).iterrows():
    print(f"\n【Rank {row['suspicious_rank']}】")
    print(f"异常分数: {row['anomaly_score']:.4f}")
    print(f"交易数: {row['num_trades']}")
    print(f"总金额: ${row['total_volume']:.2f}")
    print(f"最大单笔: ${row['max_trade']:.2f}")

    # 获取具体交易
    session_orders = orders[orders['session_id'] == row['session_id']].sort_values('timestamp')
    for _, trade in session_orders.iterrows():
        print(f"  {trade['side']}: ${trade['amount_usd']:.2f} @ {trade['price']:.4f}")
        print(f"  tx: https://polygonscan.com/tx/{trade['transaction_hash']}")

# 保存结果到 results 文件夹
output_path = os.path.join(module_root, 'results', 'strict_sniper_candidates.csv')
snipers.to_csv(output_path, index=False)
print(f"\n✅ 已保存到: {output_path}")