import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
from tqdm import tqdm
import os

# 获取当前文件所在目录 (src/)
current_dir = os.path.dirname(__file__)
# 往上一级到 sniper_detection/
module_root = os.path.dirname(current_dir)


def session_to_text(session_df):
    """将会话内的交易序列转成自然语言描述"""
    texts = []
    for _, row in session_df.iterrows():
        side = "buy" if row['side'] == 'BUY' else "sell"
        text = (f"{side} amount_{int(row['amount_usd'])} "
                f"price_{float(row['price']):.4f} "
                f"wait_{int(row['next_interval'])}s")
        texts.append(text)
    return ' '.join(texts)


def generate_embeddings(input_file='orders_with_session.csv',
                        output_file='session_embeddings.csv',
                        model_name='all-MiniLM-L6-v2'):
    """使用Sentence-BERT生成会话的语义向量"""

    print("=" * 50)
    print("开始生成会话Embedding")
    print("=" * 50)

    # 1. 读取数据
    input_path = os.path.join(module_root, input_file)
    print(f"\n📂 正在读取数据: {input_path}")
    df = pd.read_csv(input_path)

    print(f"   总订单数: {len(df):,}")
    print(f"   总会话数: {df['session_id'].nunique():,}")

    # 2. 初始化模型 - 使用模块内的模型路径
    print(f"\n🤖 加载Sentence-BERT模型: {model_name}")
    model_path = os.path.join(module_root, 'models', 'all-MiniLM-L6-v2')
    model = SentenceTransformer(model_path)
    model_dim = model.get_sentence_embedding_dimension()
    print(f"   模型维度: {model_dim}")

    # 3. 按会话分组，生成文本描述
    print("\n📝 生成会话文本描述...")
    session_texts = []
    session_ids = []
    session_stats = []

    grouped = df.groupby('session_id')
    for session_id, group in tqdm(grouped, desc="处理会话"):
        session_df = group.sort_values('timestamp')
        session_ids.append(session_id)
        text = session_to_text(session_df)
        session_texts.append(text)

        stats = {
            'session_id': session_id,
            'num_trades': len(session_df),
            'total_volume': session_df['amount_usd'].sum(),
            'max_trade': session_df['amount_usd'].max(),
            'has_large_trade': (session_df['amount_usd'] >= 5000).any(),
            'first_price': session_df['price'].iloc[0],
            'last_price': session_df['price'].iloc[-1],
            'first_side': session_df['side'].iloc[0],
            'last_side': session_df['side'].iloc[-1]
        }
        session_stats.append(stats)

    # 4. 生成embedding
    print("\n🔢 生成embedding向量...")
    embeddings = model.encode(session_texts, show_progress_bar=True)

    # 5. 构建输出DataFrame
    print("\n💾 保存结果...")
    embed_cols = [f'embed_{i}' for i in range(embeddings.shape[1])]
    embed_df = pd.DataFrame(embeddings, columns=embed_cols)
    embed_df['session_id'] = session_ids

    stats_df = pd.DataFrame(session_stats)
    result_df = embed_df.merge(stats_df, on='session_id', how='left')

    # 6. 保存到文件
    output_path = os.path.join(module_root, output_file)
    result_df.to_csv(output_path, index=False)
    print(f"   ✅ Embedding已保存至: {output_path}")
    print(f"      形状: {embeddings.shape}")

    # 7. 保存文本描述
    text_df = pd.DataFrame({
        'session_id': session_ids,
        'text': session_texts
    })
    text_path = os.path.join(module_root, 'session_texts.csv')
    text_df.to_csv(text_path, index=False)
    print(f"   ✅ 文本描述已保存至: {text_path}")

    # 8. 统计信息
    print("\n📊 Embedding统计:")
    print(f"   总会话数: {len(result_df)}")
    print(f"   包含大额交易的会话: {result_df['has_large_trade'].sum()}")
    print(f"   平均交易数: {result_df['num_trades'].mean():.2f}")

    return result_df, session_texts


def load_or_generate_embeddings(data_file='orders_with_session.csv'):
    """如果已存在embedding文件则加载，否则生成"""
    embed_file = os.path.join(module_root, 'session_embeddings.csv')
    if os.path.exists(embed_file):
        print(f"📂 加载已存在的embedding: {embed_file}")
        embed_df = pd.read_csv(embed_file)
        return embed_df
    else:
        print("🆕 生成新的embedding...")
        embed_df, _ = generate_embeddings(data_file)
        return embed_df


def quick_analyze_embeddings(embed_file='session_embeddings.csv'):
    """快速分析embedding结果"""
    embed_path = os.path.join(module_root, embed_file)
    if not os.path.exists(embed_path):
        print(f"文件不存在: {embed_path}")
        return

    df = pd.read_csv(embed_path)
    print("\n" + "=" * 50)
    print("Embedding快速分析")
    print("=" * 50)
    print(f"\n总会话数: {len(df)}")
    print(f"包含大额交易的会话: {df['has_large_trade'].sum()}")
    print(f"平均交易数: {df['num_trades'].mean():.2f}")
    print(f"平均交易金额: ${df['total_volume'].mean():.2f}")

    large_sessions = df[df['has_large_trade'] == True]
    if len(large_sessions) > 0:
        print(f"\n大额交易会话 (≥5000 USD):")
        print(f"  数量: {len(large_sessions)}")
        print(f"  平均交易数: {large_sessions['num_trades'].mean():.2f}")
        print(f"  平均总金额: ${large_sessions['total_volume'].mean():.2f}")

        buy_sell = large_sessions[
            (large_sessions['first_side'] == 'BUY') &
            (large_sessions['last_side'] == 'SELL') &
            (large_sessions['num_trades'] == 2)
            ]
        print(f"  买入→卖出模式 (2笔交易): {len(buy_sell)} 个会话")
    return df


if __name__ == "__main__":
    orders_path = os.path.join(module_root, 'orders_with_session.csv')
    if not os.path.exists(orders_path):
        print("❌ 请先运行 session_split.py 生成 orders_with_session.csv")
    else:
        embed_df, texts = generate_embeddings()
        quick_analyze_embeddings()
        print("\n✅ Embedding生成完成！")