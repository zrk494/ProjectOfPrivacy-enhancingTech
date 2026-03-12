import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# 获取当前文件所在目录 (src/)
current_dir = os.path.dirname(__file__)
# 往上一级到 sniper_detection/
module_root = os.path.dirname(current_dir)


def fix_anomaly_scores_plot():
    """重新生成异常分数分布图"""
    results_path = os.path.join(module_root, 'sniper_detection_results.csv')
    if not os.path.exists(results_path):
        print("❌ 找不到 sniper_detection_results.csv")
        return

    # 读取数据
    df = pd.read_csv(results_path)

    plt.figure(figsize=(12, 6))

    # 绘制直方图
    n, bins, patches = plt.hist(df['anomaly_score'], bins=50, alpha=0.7,
                                color='steelblue', edgecolor='black', linewidth=0.5)

    # 标注异常阈值（5%分位数）
    threshold = np.percentile(df['anomaly_score'], 5)
    plt.axvline(x=threshold, color='red', linestyle='--', linewidth=2,
                label=f'异常阈值 (5%): {threshold:.4f}')

    # 标注最异常的点
    min_score = df['anomaly_score'].min()
    plt.scatter([min_score], [5], color='darkred', s=100, zorder=5,
                label=f'最异常: {min_score:.4f}')

    plt.xlabel('异常分数 (越低越异常)', fontsize=12)
    plt.ylabel('频次', fontsize=12)
    plt.title('异常分数分布', fontsize=14, fontweight='bold')
    plt.legend(fontsize=10)
    plt.grid(True, alpha=0.3, linestyle='--')

    # 添加统计信息
    stats_text = f'总会话数: {len(df)}\n异常数: {(df["anomaly_score"] <= threshold).sum()}\n异常比例: 5%'
    plt.text(0.02, 0.98, stats_text, transform=plt.gca().transAxes,
             fontsize=10, verticalalignment='top',
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

    plt.tight_layout()

    # 保存到 plots 文件夹
    plots_dir = os.path.join(module_root, 'plots')
    os.makedirs(plots_dir, exist_ok=True)

    plt.savefig(os.path.join(plots_dir, 'anomaly_scores_fixed.png'), dpi=150, bbox_inches='tight')
    plt.savefig(os.path.join(plots_dir, 'anomaly_scores_fixed.pdf'), format='pdf', bbox_inches='tight')
    plt.close()
    print(f"✅ 已生成: {os.path.join(plots_dir, 'anomaly_scores_fixed.png')}")


def fix_amount_comparison_plot():
    """重新生成金额对比图"""
    results_path = os.path.join(module_root, 'sniper_detection_results.csv')
    if not os.path.exists(results_path):
        print("❌ 找不到 sniper_detection_results.csv")
        return

    # 读取数据
    df = pd.read_csv(results_path)

    # 区分正常和异常（用5%分位数）
    threshold = np.percentile(df['anomaly_score'], 5)
    df['is_anomaly'] = df['anomaly_score'] <= threshold

    plt.figure(figsize=(10, 6))

    # 准备数据
    normal_amounts = df[~df['is_anomaly']]['total_volume']
    anomaly_amounts = df[df['is_anomaly']]['total_volume']

    # 绘制箱线图
    bp = plt.boxplot([normal_amounts, anomaly_amounts],
                     labels=['正常会话', '异常会话'],
                     patch_artist=True,
                     showfliers=True,
                     flierprops=dict(marker='o', markerfacecolor='gray', markersize=3, alpha=0.3))

    # 设置颜色
    bp['boxes'][0].set_facecolor('lightblue')
    bp['boxes'][1].set_facecolor('lightcoral')

    plt.yscale('log')
    plt.ylabel('交易总金额 (USD, 对数坐标)', fontsize=12)
    plt.title('正常会话 vs 异常会话 - 交易金额对比', fontsize=14, fontweight='bold')
    plt.grid(True, alpha=0.3, axis='y', linestyle='--')

    # 添加统计信息
    stats_text = f'正常会话数: {len(normal_amounts)}\n异常会话数: {len(anomaly_amounts)}'
    plt.text(0.02, 0.98, stats_text, transform=plt.gca().transAxes,
             fontsize=10, verticalalignment='top',
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

    plt.tight_layout()

    # 保存到 plots 文件夹
    plots_dir = os.path.join(module_root, 'plots')
    os.makedirs(plots_dir, exist_ok=True)

    plt.savefig(os.path.join(plots_dir, 'amount_comparison_fixed.png'), dpi=150, bbox_inches='tight')
    plt.savefig(os.path.join(plots_dir, 'amount_comparison_fixed.pdf'), format='pdf', bbox_inches='tight')
    plt.close()
    print(f"✅ 已生成: {os.path.join(plots_dir, 'amount_comparison_fixed.png')}")


def fix_large_trade_distribution():
    """重新生成大额交易分布图"""
    results_path = os.path.join(module_root, 'sniper_detection_results.csv')
    if not os.path.exists(results_path):
        print("❌ 找不到 sniper_detection_results.csv")
        return

    # 读取数据
    df = pd.read_csv(results_path)

    # 区分正常和异常
    threshold = np.percentile(df['anomaly_score'], 5)
    df['is_anomaly'] = df['anomaly_score'] <= threshold

    plt.figure(figsize=(10, 6))

    # 分类统计
    normal_no_large = len(df[~df['is_anomaly'] & ~df['has_large_trade']])
    normal_with_large = len(df[~df['is_anomaly'] & df['has_large_trade']])
    anomaly_no_large = len(df[df['is_anomaly'] & ~df['has_large_trade']])
    anomaly_with_large = len(df[df['is_anomaly'] & df['has_large_trade']])

    # 绘制堆叠柱状图
    categories = ['正常会话', '异常会话']
    no_large = [normal_no_large, anomaly_no_large]
    with_large = [normal_with_large, anomaly_with_large]

    bar_width = 0.6
    x = np.arange(len(categories))

    p1 = plt.bar(x, no_large, bar_width, label='无大额交易', color='lightblue', edgecolor='black', linewidth=0.5)
    p2 = plt.bar(x, with_large, bar_width, bottom=no_large, label='含大额交易', color='lightcoral', edgecolor='black',
                 linewidth=0.5)

    plt.xlabel('')
    plt.ylabel('会话数', fontsize=12)
    plt.title('大额交易会话分布', fontsize=14, fontweight='bold')
    plt.xticks(x, categories, fontsize=11)
    plt.legend(fontsize=10)
    plt.grid(True, alpha=0.3, axis='y', linestyle='--')

    # 添加数值标签
    for i, (n, w) in enumerate(zip(no_large, with_large)):
        if n > 0:
            plt.text(i, n / 2, str(n), ha='center', va='center', fontsize=10)
        if w > 0:
            plt.text(i, n + w / 2, str(w), ha='center', va='center', fontsize=10)
        plt.text(i, n + w + 10, str(n + w), ha='center', va='bottom', fontsize=10, fontweight='bold')

    plt.tight_layout()

    # 保存到 plots 文件夹
    plots_dir = os.path.join(module_root, 'plots')
    os.makedirs(plots_dir, exist_ok=True)

    plt.savefig(os.path.join(plots_dir, 'large_trade_distribution_fixed.png'), dpi=150, bbox_inches='tight')
    plt.savefig(os.path.join(plots_dir, 'large_trade_distribution_fixed.pdf'), format='pdf', bbox_inches='tight')
    plt.close()
    print(f"✅ 已生成: {os.path.join(plots_dir, 'large_trade_distribution_fixed.png')}")


def show_top_sessions():
    """显示Top 10可疑会话的详细信息"""
    results_path = os.path.join(module_root, 'sniper_detection_results.csv')
    orders_path = os.path.join(module_root, 'orders_with_session.csv')

    if not os.path.exists(results_path):
        print("❌ 找不到 sniper_detection_results.csv")
        return

    df = pd.read_csv(results_path)
    orders = pd.read_csv(orders_path)

    print("\n" + "=" * 60)
    print("Top 10 最可疑会话详细分析")
    print("=" * 60)

    for idx, row in df.head(10).iterrows():
        print(f"\n【Rank {row['suspicious_rank']}】")
        print(f"会话ID: {row['session_id'][:30]}...")
        print(f"异常分数: {row['anomaly_score']:.4f}")
        print(f"交易数: {row['num_trades']}")
        print(f"总金额: ${row['total_volume']:.2f}")
        print(f"最大单笔: ${row['max_trade']:.2f}")
        print(f"是否有大额交易: {'是' if row['has_large_trade'] else '否'}")
        print(f"首笔方向: {row['first_side']}, 末笔方向: {row['last_side']}")

        # 显示该会话的具体交易
        session_orders = orders[orders['session_id'] == row['session_id']].sort_values('timestamp')
        print(f"交易详情 (前3笔):")
        for _, o in session_orders.head(3).iterrows():
            print(f"  tx_hash: {o['transaction_hash'][:20]}...")
            print(f"  方向: {o['side']}, 价格: {o['price']:.4f}, 金额: ${o['amount_usd']:.2f}")
            if 'next_interval' in o:
                print(f"  间隔: {o['next_interval']:.0f}秒")


if __name__ == "__main__":
    # 重新生成所有图表
    print("🔄 重新生成图表...")
    fix_anomaly_scores_plot()
    fix_amount_comparison_plot()
    fix_large_trade_distribution()

    # 显示详细分析
    show_top_sessions()

    print("\n✅ 所有图表已重新生成！")
    print(f"新文件保存在 {os.path.join(module_root, 'plots')} 目录下")