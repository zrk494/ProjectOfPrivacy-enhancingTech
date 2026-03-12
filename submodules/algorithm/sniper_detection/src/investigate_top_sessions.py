import pandas as pd
import webbrowser
import os

# 获取当前文件所在目录 (src/)
current_dir = os.path.dirname(__file__)
# 往上一级到 sniper_detection/
module_root = os.path.dirname(current_dir)

# 读取结果
results_path = os.path.join(module_root, 'sniper_detection_results.csv')
orders_path = os.path.join(module_root, 'orders_with_session.csv')

results = pd.read_csv(results_path)
orders = pd.read_csv(orders_path)

# 取Top 10最可疑（分数最低）
top10 = results.nsmallest(10, 'anomaly_score')

print("=" * 60)
print("Top 10 最可疑会话 - 人工核查清单")
print("=" * 60)

for idx, row in top10.iterrows():
    print(f"\n【Rank {row['suspicious_rank']}】")
    print(f"异常分数: {row['anomaly_score']:.4f}")
    print(f"交易数: {row['num_trades']}")
    print(f"总金额: ${row['total_volume']:.2f}")
    print(f"最大单笔: ${row['max_trade']:.2f}")
    print(f"是否有大额交易: {'✅ 是' if row['has_large_trade'] else '❌ 否'}")

    # 获取该会话的所有交易
    session_orders = orders[orders['session_id'] == row['session_id']].sort_values('timestamp')

    # 显示每条交易的哈希
    for _, o in session_orders.iterrows():
        tx_hash = o['transaction_hash']
        short_hash = tx_hash[:10] + '...' + tx_hash[-8:]
        print(f"  tx: {short_hash}")
        print(f"    方向: {o['side']}, 价格: {o['price']:.4f}, 金额: ${o['amount_usd']:.2f}")

        # 生成Polygonscan链接
        scan_url = f"https://polygonscan.com/tx/{tx_hash}"
        print(f"    链接: {scan_url}")

    print("-" * 40)

# 保存核查清单到 results 文件夹
output_path = os.path.join(module_root, 'results', 'top10_suspicious_sessions.csv')
top10.to_csv(output_path, index=False)
print(f"\n✅ 核查清单已保存到: {output_path}")