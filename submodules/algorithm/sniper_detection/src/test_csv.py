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

# 读取数据
orders_path = os.path.join(module_root, 'orders_with_session.csv')
print(f"📂 读取数据: {orders_path}")
orders = pd.read_csv(orders_path)

# 两个案例的会话ID
cases = [
    {
        'rank': 3,
        'session_id': '0x63b81ddc36a228f7431a534d67eb058b7cc0f906_1',
        'buy_tx': '0xe48675a9c5422d604956472b17d0f2785e7c8b13c6f2047a74004a53f1786b93',
        'sell_tx': '0xa58078148acb1371bdc0044fe9eabc6e7c2c7a032ff3a0056170e20134f328e0'
    },
    {
        'rank': 4,
        'session_id': '0x6a4aaf27bb285af2744c7def8ec447937fb07f69_1',
        'buy_tx': '0x4f133897f46bed815a1c7c6a95f04d4ab76eb688db3ec97b4af56ebbdae0190e',
        'sell_tx': '0x48ce73b8d175c579ea70269d35695259ebddb4e729066c70597049578481cd79'
    }
]


def plot_attack_window(case):
    """绘制单个攻击窗口图"""
    session_id = case['session_id']
    rank = case['rank']

    # 获取该会话的所有交易
    session_orders = orders[orders['session_id'] == session_id].sort_values('timestamp')

    if len(session_orders) == 0:
        print(f"❌ 找不到会话: {session_id}")
        return

    # 处理时间戳
    if session_orders['timestamp'].dtype == 'object':
        session_orders['datetime'] = pd.to_datetime(session_orders['timestamp'])
        session_orders['timestamp_unix'] = session_orders['datetime'].astype('int64') // 10 ** 9
    else:
        session_orders['datetime'] = pd.to_datetime(session_orders['timestamp'], unit='s')
        session_orders['timestamp_unix'] = session_orders['timestamp']

    # 获取市场ID和上下文交易
    market_id = session_orders['market_id'].iloc[0]
    session_start = session_orders['timestamp_unix'].min()
    session_end = session_orders['timestamp_unix'].max()

    # 前后各30分钟上下文
    context_start = session_start - 1800
    context_end = session_end + 1800

    context_orders = orders[orders['market_id'] == market_id].copy()
    if len(context_orders) > 0:
        if context_orders['timestamp'].dtype == 'object':
            context_orders['datetime'] = pd.to_datetime(context_orders['timestamp'])
            context_orders['timestamp_unix'] = context_orders['datetime'].astype('int64') // 10 ** 9
        else:
            context_orders['datetime'] = pd.to_datetime(context_orders['timestamp'], unit='s')
            context_orders['timestamp_unix'] = context_orders['timestamp']

        context_orders = context_orders[
            (context_orders['timestamp_unix'] >= context_start) &
            (context_orders['timestamp_unix'] <= context_end)
            ]

    # 创建图表
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10),
                                   gridspec_kw={'height_ratios': [3, 1]})

    # 上半图：价格曲线
    if len(context_orders) > 0:
        ax1.plot(context_orders['datetime'], context_orders['price'],
                 'o-', color='lightgray', alpha=0.5, markersize=3, label='其他交易', linewidth=1)

    # 可疑会话（红色）
    ax1.plot(session_orders['datetime'], session_orders['price'],
             'ro-', linewidth=2, markersize=12, label='可疑会话', markerfacecolor='red')

    # 标注买卖点和金额
    for _, trade in session_orders.iterrows():
        marker = '↑' if trade['side'] == 'BUY' else '↓'
        color = 'green' if trade['side'] == 'BUY' else 'red'

        ax1.annotate(marker, (trade['datetime'], trade['price']),
                     xytext=(0, 15), textcoords='offset points',
                     fontsize=18, color=color, fontweight='bold')

        ax1.annotate(f'${trade["amount_usd"]:.0f}',
                     (trade['datetime'], trade['price']),
                     xytext=(15, -20), textcoords='offset points',
                     fontsize=11, color='darkred',
                     bbox=dict(boxstyle='round,pad=0.4', facecolor='yellow', alpha=0.8))

    # 计算时间差
    time1 = session_orders['datetime'].iloc[0]
    time2 = session_orders['datetime'].iloc[-1]
    duration = (time2 - time1).total_seconds()

    # 标注持仓时间
    mid_time = time1 + (time2 - time1) / 2
    ax1.annotate(f'持仓 {duration:.0f} 秒',
                 (mid_time, session_orders['price'].min() - 0.0005),
                 xytext=(0, 40), textcoords='offset points',
                 fontsize=13, color='blue', fontweight='bold',
                 arrowprops=dict(arrowstyle='<->', color='blue', lw=2.5))

    ax1.set_xlabel('时间', fontsize=13)
    ax1.set_ylabel('赔率', fontsize=13)
    ax1.set_title(f'狙击手攻击案例 Rank {rank} - {duration:.0f}秒闪电战', fontsize=16, fontweight='bold')
    ax1.set_ylim(0.9970, 1.0005)
    ax1.legend(loc='upper right', fontsize=11)
    ax1.grid(True, alpha=0.3, linestyle='--')

    # 下半图：交易量
    colors = ['green' if s == 'BUY' else 'red' for s in session_orders['side']]
    bars = ax2.bar(session_orders['datetime'], session_orders['amount_usd'],
                   color=colors, alpha=0.8, width=0.001)

    for bar, trade in zip(bars, session_orders.itertuples()):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width() / 2., height + 800,
                 f'${trade.amount_usd:.0f}', ha='center', va='bottom',
                 fontsize=11, fontweight='bold')

    ax2.set_xlabel('时间', fontsize=13)
    ax2.set_ylabel('交易金额 (USD)', fontsize=13)
    ax2.set_title('交易量分布 (买入↑ 卖出↓)', fontsize=14)
    ax2.grid(True, alpha=0.3, linestyle='--', axis='y')

    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='green', alpha=0.8, label='买入'),
        Patch(facecolor='red', alpha=0.8, label='卖出')
    ]
    ax2.legend(handles=legend_elements, loc='upper right', fontsize=11)

    plt.tight_layout()

    # 保存到 results/attack_windows/
    output_dir = os.path.join(module_root, 'results', 'attack_windows')
    os.makedirs(output_dir, exist_ok=True)
    filename = os.path.join(output_dir, f'sniper_rank{rank}_{duration:.0f}seconds.png')
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    plt.close()

    print(f"✅ Rank {rank} 攻击窗口图已生成: {filename}")
    print(f"   买入: ${session_orders.iloc[0]['amount_usd']:.2f} @ {session_orders.iloc[0]['price']:.4f}")
    print(f"   卖出: ${session_orders.iloc[1]['amount_usd']:.2f} @ {session_orders.iloc[1]['price']:.4f}")
    print(f"   持仓: {duration:.0f} 秒")
    print(f"   盈亏: ${session_orders.iloc[1]['amount_usd'] - session_orders.iloc[0]['amount_usd']:.2f}")
    print("-" * 40)


# 批量生成
print("=" * 50)
print("开始生成攻击窗口图...")
print("=" * 50)

for case in cases:
    plot_attack_window(case)

print("\n✅ 所有攻击窗口图生成完成！")
output_dir = os.path.join(module_root, 'results', 'attack_windows')
print(f"文件保存在: {output_dir}")
print("  - sniper_rank3_76seconds.png")
print("  - sniper_rank4_72seconds.png")