import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
import os

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# 获取当前文件所在目录 (src/)
current_dir = os.path.dirname(__file__)
# 往上一级到 sniper_detection/
module_root = os.path.dirname(current_dir)


def plot_attack_window(session_id, orders_df=None, output_dir=None):
    """
    绘制单个攻击窗口的赔率曲线
    """
    if output_dir is None:
        output_dir = os.path.join(module_root, 'results', 'attack_windows')

    # 如果没有传入 orders_df，尝试从文件读取
    if orders_df is None:
        orders_path = os.path.join(module_root, 'orders_with_session.csv')
        if not os.path.exists(orders_path):
            print(f"❌ 找不到 orders_with_session.csv")
            return
        orders_df = pd.read_csv(orders_path)

    # 获取该会话的所有交易
    session_orders = orders_df[orders_df['session_id'] == session_id].sort_values('timestamp')

    if len(session_orders) == 0:
        print(f"❌ 找不到会话: {session_id}")
        return

    # 确保 timestamp 是 datetime 类型
    if session_orders['timestamp'].dtype == 'object':
        # 如果是字符串，直接转换
        session_orders['datetime'] = pd.to_datetime(session_orders['timestamp'])
        # 转换为 Unix 时间戳用于计算
        session_orders['timestamp_unix'] = session_orders['datetime'].astype('int64') // 10 ** 9
    else:
        # 如果是数字，当作 Unix 时间戳处理
        session_orders['datetime'] = pd.to_datetime(session_orders['timestamp'], unit='s')
        session_orders['timestamp_unix'] = session_orders['timestamp']

    # 获取该市场的更多上下文交易（前后各30分钟）
    market_id = session_orders['market_id'].iloc[0]
    session_start = session_orders['timestamp_unix'].min()
    session_end = session_orders['timestamp_unix'].max()

    # 获取上下文交易
    context_start = session_start - 1800  # 前30分钟
    context_end = session_end + 1800  # 后30分钟

    context_orders = orders_df[
        (orders_df['market_id'] == market_id)
    ].copy()

    # 处理上下文交易的时间戳
    if len(context_orders) > 0:
        if context_orders['timestamp'].dtype == 'object':
            context_orders['datetime'] = pd.to_datetime(context_orders['timestamp'])
            context_orders['timestamp_unix'] = context_orders['datetime'].astype('int64') // 10 ** 9
        else:
            context_orders['datetime'] = pd.to_datetime(context_orders['timestamp'], unit='s')
            context_orders['timestamp_unix'] = context_orders['timestamp']

        # 过滤时间范围
        context_orders = context_orders[
            (context_orders['timestamp_unix'] >= context_start) &
            (context_orders['timestamp_unix'] <= context_end)
            ]

    # 创建图表
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10),
                                   gridspec_kw={'height_ratios': [3, 1]})

    # 上半部分：价格曲线
    if len(context_orders) > 0:
        ax1.plot(context_orders['datetime'], context_orders['price'],
                 'o-', color='lightgray', alpha=0.5, markersize=3, label='其他交易', linewidth=1)

    ax1.plot(session_orders['datetime'], session_orders['price'],
             'ro-', linewidth=2, markersize=8, label='可疑会话', markerfacecolor='red')

    # 标注大额交易
    large_trades = session_orders[session_orders['amount_usd'] >= 5000]
    for _, trade in large_trades.iterrows():
        ax1.annotate(f'${trade["amount_usd"]:.0f}',
                     (trade['datetime'], trade['price']),
                     xytext=(10, 10), textcoords='offset points',
                     fontsize=10, color='darkred',
                     bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.7))

    # 标注买卖方向
    for _, trade in session_orders.iterrows():
        marker = '↑' if trade['side'] == 'BUY' else '↓'
        color = 'green' if trade['side'] == 'BUY' else 'red'
        ax1.annotate(marker, (trade['datetime'], trade['price']),
                     xytext=(0, 5), textcoords='offset points',
                     fontsize=14, color=color, fontweight='bold')

    ax1.set_xlabel('时间', fontsize=12)
    ax1.set_ylabel('赔率', fontsize=12)
    ax1.set_title(f'攻击窗口赔率曲线 - 会话 {session_id[:20]}...', fontsize=14, fontweight='bold')
    ax1.legend(loc='upper right')
    ax1.grid(True, alpha=0.3, linestyle='--')

    # 下半部分：交易量
    colors = ['green' if s == 'BUY' else 'red' for s in session_orders['side']]
    ax2.bar(session_orders['datetime'], session_orders['amount_usd'],
            color=colors, alpha=0.7, width=0.1)
    ax2.set_xlabel('时间', fontsize=12)
    ax2.set_ylabel('交易金额 (USD)', fontsize=12)
    ax2.set_title('交易量分布', fontsize=12)
    ax2.grid(True, alpha=0.3, linestyle='--', axis='y')

    # 添加图例
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='green', alpha=0.7, label='买入'),
        Patch(facecolor='red', alpha=0.7, label='卖出')
    ]
    ax2.legend(handles=legend_elements, loc='upper right')

    plt.tight_layout()

    # 保存图表
    os.makedirs(output_dir, exist_ok=True)
    safe_session_id = session_id.replace('/', '_').replace('\\', '_')[:20]
    filename = os.path.join(output_dir, f"attack_window_{safe_session_id}.png")
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    plt.close()

    print(f"✅ 已生成攻击窗口图: {filename}")
    return filename


def generate_attack_report():
    """
    生成攻击案例报告
    """
    # 读取数据
    results_path = os.path.join(module_root, 'sniper_detection_results.csv')
    orders_path = os.path.join(module_root, 'orders_with_session.csv')
    top10_path = os.path.join(module_root, 'results', 'top10_suspicious_sessions.csv')

    results = pd.read_csv(results_path)
    orders = pd.read_csv(orders_path)
    top10 = pd.read_csv(top10_path)

    print("\n" + "=" * 70)
    print("🔍 狙击手攻击案例报告")
    print("=" * 70)

    # 为每个Top 10会话生成攻击窗口图
    for idx, row in top10.iterrows():
        session_id = row['session_id']

        print(f"\n📌 案例 {idx + 1}: Rank {row['suspicious_rank']}")
        print(f"   会话ID: {session_id[:30]}...")
        print(f"   异常分数: {row['anomaly_score']:.4f}")
        print(f"   交易数: {row['num_trades']}")
        print(f"   总金额: ${row['total_volume']:.2f}")
        print(f"   最大单笔: ${row['max_trade']:.2f}")

        # 绘制攻击窗口图
        plot_attack_window(session_id, orders)

        # 获取交易哈希
        session_orders = orders[orders['session_id'] == session_id].sort_values('timestamp')
        print(f"   交易哈希:")
        for _, trade in session_orders.iterrows():
            tx_hash = trade['transaction_hash']
            scan_url = f"https://polygonscan.com/tx/{tx_hash}"
            print(f"     - {tx_hash[:20]}...")
            print(f"       {scan_url}")

        print(f"   {'=' * 50}")


def analyze_sniper_patterns():
    """
    分析狙击手模式
    """
    results_path = os.path.join(module_root, 'sniper_detection_results.csv')
    results = pd.read_csv(results_path)

    # 异常会话中大额交易的比例
    anomaly_with_large = results[results['is_sniper'] == 1]['has_large_trade'].sum()
    anomaly_total = (results['is_sniper'] == 1).sum()

    # 买入-卖出模式
    buy_sell_pattern = results[
        (results['is_sniper'] == 1) &
        (results['first_side'] == 'BUY') &
        (results['last_side'] == 'SELL')
        ]

    print("\n" + "=" * 70)
    print("📊 狙击手模式分析")
    print("=" * 70)
    print(f"\n异常会话总数: {anomaly_total}")
    print(f"包含大额交易的异常会话: {anomaly_with_large} ({anomaly_with_large / anomaly_total * 100:.1f}%)")
    print(f"买入→卖出模式: {len(buy_sell_pattern)} ({len(buy_sell_pattern) / anomaly_total * 100:.1f}%)")

    # 保存分析结果到 results 文件夹
    report_path = os.path.join(module_root, 'results', 'sniper_analysis_report.txt')
    with open(report_path, 'w') as f:
        f.write("狙击手攻击分析报告\n")
        f.write("=" * 50 + "\n")
        f.write(f"异常会话总数: {anomaly_total}\n")
        f.write(f"包含大额交易: {anomaly_with_large} ({anomaly_with_large / anomaly_total * 100:.1f}%)\n")
        f.write(f"买入→卖出模式: {len(buy_sell_pattern)} ({len(buy_sell_pattern) / anomaly_total * 100:.1f}%)\n")
    print(f"\n✅ 分析报告已保存到: {report_path}")


if __name__ == "__main__":
    # 创建输出目录
    output_dir = os.path.join(module_root, 'results', 'attack_windows')
    os.makedirs(output_dir, exist_ok=True)

    # 生成攻击窗口图
    generate_attack_report()

    # 分析模式
    analyze_sniper_patterns()

    print("\n✅ 攻击案例分析完成！")
    print(f"生成的文件保存在: {os.path.join(module_root, 'results')}")