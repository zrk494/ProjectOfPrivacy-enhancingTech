import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.metrics import precision_score, recall_score, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns
import os
from datetime import datetime

# 获取当前文件所在目录 (src/)
current_dir = os.path.dirname(__file__)
# 往上一级到 sniper_detection/
module_root = os.path.dirname(current_dir)


def load_data(embed_file='session_embeddings.csv', session_file='orders_with_session.csv'):
    """
    加载embedding和会话数据
    """
    print("=" * 50)
    print("加载数据")
    print("=" * 50)

    # 加载embedding
    embed_path = os.path.join(module_root, embed_file)
    print(f"\n📂 加载embedding: {embed_path}")
    embed_df = pd.read_csv(embed_path)
    print(f"   会话数: {len(embed_df)}")

    # 加载原始会话数据（用于获取更多特征）
    session_path = os.path.join(module_root, session_file)
    print(f"\n📂 加载会话数据: {session_path}")
    session_df = pd.read_csv(session_path)

    # 合并数据
    # 从session_df提取每个会话的统计特征
    session_stats = session_df.groupby('session_id').agg({
        'amount_usd': ['sum', 'max', 'mean', 'std', 'count'],
        'price': ['first', 'last', 'max', 'min', 'mean', 'std'],
        'next_interval': ['sum', 'mean', 'max'],
        'trader_address': 'first',
        'market_id': 'first'
    }).round(4)

    # 扁平化列名
    session_stats.columns = ['_'.join(col).strip() for col in session_stats.columns.values]
    session_stats = session_stats.reset_index()

    # 合并embedding和统计特征
    merged_df = embed_df.merge(session_stats, on='session_id', how='left')

    print(f"\n✅ 合并完成: {len(merged_df)} 个会话")
    return merged_df


def prepare_features(df, use_embedding=True, use_stats=True):
    """
    准备训练特征
    """
    features = []
    feature_names = []

    # 1. embedding特征
    if use_embedding:
        embed_cols = [col for col in df.columns if col.startswith('embed_')]
        features.append(df[embed_cols].values)
        feature_names.extend(embed_cols)
        print(f"   embedding特征: {len(embed_cols)} 维")

    # 2. 统计特征
    if use_stats:
        stats_cols = [
            'amount_usd_sum', 'amount_usd_max', 'amount_usd_mean',
            'amount_usd_std', 'amount_usd_count',
            'price_mean', 'price_std', 'next_interval_mean',
            'next_interval_max'
        ]
        # 只保留存在的列
        stats_cols = [col for col in stats_cols if col in df.columns]
        features.append(df[stats_cols].fillna(0).values)
        feature_names.extend(stats_cols)
        print(f"   统计特征: {len(stats_cols)} 维")

    # 合并所有特征
    if len(features) == 1:
        X = features[0]
    else:
        X = np.hstack(features)

    print(f"   总特征维度: {X.shape[1]}")
    return X, feature_names


def pseudo_label_sniper(df, amount_threshold=5000, time_threshold=300):
    """
    用规则生成伪标签（用于评估）
    满足以下条件之一标记为可疑：
    1. 大额交易 + 交易数=2（可能是买入+卖出）
    2. 大额交易 + 快速反向（短时间内的买卖）
    """
    labels = []

    for _, row in df.iterrows():
        suspicious = False

        # 规则1：有大额交易且会话只有2笔交易
        if row['has_large_trade'] and row['num_trades'] == 2:
            suspicious = True

        # 规则2：第一笔是买入，最后一笔是卖出，且总金额大
        if (row['first_side'] == 'BUY' and
                row['last_side'] == 'SELL' and
                row['total_volume'] > amount_threshold):
            suspicious = True

        labels.append(1 if suspicious else 0)

    return np.array(labels)


def train_isolation_forest(X, contamination=0.05, random_state=42):
    """
    训练孤立森林模型
    """
    print("\n" + "=" * 50)
    print("训练孤立森林模型")
    print("=" * 50)

    model = IsolationForest(
        contamination=contamination,
        random_state=random_state,
        n_estimators=100,
        max_samples='auto',
        bootstrap=False,
        n_jobs=-1
    )

    print(f"\n参数设置:")
    print(f"   contamination: {contamination} (预期异常比例)")
    print(f"   n_estimators: 100")
    print(f"   特征维度: {X.shape[1]}")

    # 训练模型
    print("\n🔄 训练中...")
    model.fit(X)

    # 预测
    print("🔄 预测中...")
    y_pred = model.predict(X)
    y_scores = model.score_samples(X)

    # 转换预测结果：-1为异常(1)，1为正常(0)
    y_pred_binary = (y_pred == -1).astype(int)

    print(f"\n✅ 训练完成")
    print(f"   检测到的异常数: {y_pred_binary.sum()}")
    print(f"   异常比例: {y_pred_binary.mean():.2%}")

    return model, y_pred_binary, y_scores


def evaluate_model(y_true, y_pred, y_scores=None):
    """
    评估模型性能
    """
    print("\n" + "=" * 50)
    print("模型评估")
    print("=" * 50)

    if y_true is not None:
        precision = precision_score(y_true, y_pred, zero_division=0)
        recall = recall_score(y_true, y_pred, zero_division=0)
        if precision + recall > 0:
            f1 = 2 * (precision * recall) / (precision + recall)
        else:
            f1 = 0

        print(f"\n基于规则标签的评估:")
        print(f"   Precision: {precision:.3f}")
        print(f"   Recall: {recall:.3f}")
        print(f"   F1-Score: {f1:.3f}")

    # 异常分数分布
    if y_scores is not None:
        print(f"\n异常分数统计:")
        print(f"   平均分: {y_scores.mean():.4f}")
        print(f"   标准差: {y_scores.std():.4f}")
        print(f"   最小分: {y_scores.min():.4f}")
        print(f"   最大分: {y_scores.max():.4f}")


def plot_results(df, y_pred, y_scores, output_dir='plots'):
    """
    生成可视化图表
    """
    plots_dir = os.path.join(module_root, output_dir)
    os.makedirs(plots_dir, exist_ok=True)

    # 1. 异常分数分布图
    plt.figure(figsize=(10, 6))
    plt.hist(y_scores, bins=50, alpha=0.7, color='blue', edgecolor='black')
    plt.axvline(x=np.percentile(y_scores, 5), color='red', linestyle='--', label='异常阈值 (5%)')
    plt.xlabel('异常分数')
    plt.ylabel('频次')
    plt.title('异常分数分布')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.savefig(os.path.join(plots_dir, 'anomaly_scores.png'), dpi=150)
    plt.close()
    print(f"✅ 已保存: {os.path.join(plots_dir, 'anomaly_scores.png')}")

    # 2. 异常vs正常交易金额对比
    plt.figure(figsize=(10, 6))
    df_copy = df.copy()
    df_copy['pred'] = y_pred
    normal_amounts = df_copy[df_copy['pred'] == 0]['total_volume']
    anomaly_amounts = df_copy[df_copy['pred'] == 1]['total_volume']

    plt.boxplot([normal_amounts, anomaly_amounts], labels=['正常', '异常'])
    plt.ylabel('交易总金额 (USD)')
    plt.title('正常会话 vs 异常会话 - 交易金额对比')
    plt.yscale('log')
    plt.grid(True, alpha=0.3)
    plt.savefig(os.path.join(plots_dir, 'amount_comparison.png'), dpi=150)
    plt.close()
    print(f"✅ 已保存: {os.path.join(plots_dir, 'amount_comparison.png')}")

    # 3. 大额交易分布
    plt.figure(figsize=(10, 6))
    large_trades = df_copy[df_copy['has_large_trade']]
    normal_large = large_trades[large_trades['pred'] == 0]
    anomaly_large = large_trades[large_trades['pred'] == 1]

    x = ['正常 (含大额)', '异常 (含大额)']
    y = [len(normal_large), len(anomaly_large)]

    plt.bar(x, y, color=['blue', 'red'])
    plt.ylabel('会话数')
    plt.title('大额交易会话的分布')
    for i, v in enumerate(y):
        plt.text(i, v + 1, str(v), ha='center')
    plt.grid(True, alpha=0.3, axis='y')
    plt.savefig(os.path.join(plots_dir, 'large_trade_distribution.png'), dpi=150)
    plt.close()
    print(f"✅ 已保存: {os.path.join(plots_dir, 'large_trade_distribution.png')}")


def save_results(df, y_pred, y_scores, output_file='sniper_detection_results.csv'):
    """
    保存检测结果
    """
    results_df = df[['session_id', 'num_trades', 'total_volume', 'max_trade',
                     'has_large_trade', 'first_side', 'last_side']].copy()
    results_df['anomaly_score'] = y_scores
    results_df['is_sniper'] = y_pred
    results_df = results_df.sort_values('anomaly_score')

    # 添加排名
    results_df['suspicious_rank'] = range(1, len(results_df) + 1)

    output_path = os.path.join(module_root, output_file)
    results_df.to_csv(output_path, index=False)
    print(f"\n✅ 结果已保存: {output_path}")

    # 显示top10最可疑的会话
    print("\n🔍 Top 10 最可疑会话:")
    top10 = results_df.head(10)
    for idx, row in top10.iterrows():
        print(f"   Rank {row['suspicious_rank']}: {row['session_id'][:20]}... "
              f"金额: ${row['total_volume']:.2f}, "
              f"交易数: {row['num_trades']}, "
              f"大额: {'是' if row['has_large_trade'] else '否'}")

    return results_df


def main():
    # 1. 加载数据
    df = load_data()

    # 2. 准备特征
    print("\n" + "=" * 50)
    print("准备特征")
    print("=" * 50)
    X, feature_names = prepare_features(df, use_embedding=True, use_stats=True)

    # 3. 生成伪标签（用于评估）
    y_true = pseudo_label_sniper(df)
    print(f"\n规则标记的异常数: {y_true.sum()}")
    print(f"异常比例: {y_true.mean():.2%}")

    # 4. 训练模型
    model, y_pred, y_scores = train_isolation_forest(X, contamination=0.05)

    # 5. 评估模型
    evaluate_model(y_true, y_pred, y_scores)

    # 6. 生成可视化
    plot_results(df, y_pred, y_scores)

    # 7. 保存结果
    results = save_results(df, y_pred, y_scores)

    print("\n" + "=" * 50)
    print("🎉 检测完成！")
    print("=" * 50)
    print("\n生成的文件:")
    print(f"   - {os.path.join(module_root, 'sniper_detection_results.csv')}")
    print(f"   - {os.path.join(module_root, 'plots', 'anomaly_scores.png')}")
    print(f"   - {os.path.join(module_root, 'plots', 'amount_comparison.png')}")
    print(f"   - {os.path.join(module_root, 'plots', 'large_trade_distribution.png')}")


if __name__ == "__main__":
    main()