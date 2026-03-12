import pandas as pd
import glob
import json
import os
from tqdm import tqdm

# 获取当前文件所在目录 (src/)
current_dir = os.path.dirname(__file__)
# 往上一级到 sniper_detection/
module_root = os.path.dirname(current_dir)


def find_all_data_files():
    """
    递归查找所有 _YES.csv 和 _NO.csv 文件
    自动处理多级嵌套目录
    """
    all_files = []

    # 获取项目根目录（可能需要根据实际情况调整）
    # 假设原始数据在项目根目录的 polymarket_data/ 下
    search_path = os.path.join(module_root, '..', '..', '..', 'data')  # 根据实际结构调整
    if not os.path.exists(search_path):
        # 如果找不到，就在当前目录找
        search_path = "."

    print(f"搜索路径: {os.path.abspath(search_path)}")

    for root, dirs, files in os.walk(search_path):
        for file in files:
            # 匹配各种大小写组合的 YES/NO 文件
            if (file.endswith("_YES.csv") or
                    file.endswith("_YES.CSV") or
                    file.endswith("_NO.csv") or
                    file.endswith("_NO.CSV")):
                full_path = os.path.join(root, file)
                all_files.append(full_path)
                print(f"发现文件: {full_path}")

    return all_files


def parse_raw_field(raw_str):
    """
    解析raw字段，提取交易者地址(proxyWallet)
    """
    try:
        # 如果raw是字符串，解析JSON
        if isinstance(raw_str, str):
            # 处理可能存在的引号问题
            if raw_str.startswith('"') and raw_str.endswith('"'):
                raw_str = raw_str[1:-1].replace('\\"', '"')
            data = json.loads(raw_str)
        else:
            data = raw_str

        # 提取需要的字段
        return {
            'trader_address': data.get('proxyWallet', ''),
            'outcome': data.get('outcome', ''),
            'outcome_index': data.get('outcomeIndex', ''),
            'name': data.get('name', ''),
            'pseudonym': data.get('pseudonym', '')
        }
    except Exception as e:
        # 如果解析失败，返回空值
        return {
            'trader_address': '',
            'outcome': '',
            'outcome_index': '',
            'name': '',
            'pseudonym': ''
        }


def process_file(file_path):
    """
    处理单个CSV文件
    """
    try:
        # 从文件名提取market_id和outcome
        filename = os.path.basename(file_path)

        # 处理各种命名格式
        if '_YES' in filename.upper():
            market_id = filename.upper().replace('_YES.CSV', '').replace('_YES.CSV', '').replace('_YES.CSV', '')
            file_outcome = 'YES'
        elif '_NO' in filename.upper():
            market_id = filename.upper().replace('_NO.CSV', '').replace('_NO.CSV', '').replace('_NO.CSV', '')
            file_outcome = 'NO'
        else:
            print(f"跳过无法识别的文件: {filename}")
            return None

        # 读取CSV
        print(f"正在处理: {filename}")
        df = pd.read_csv(file_path)

        # 检查列数，如果列数不够11列，可能是格式问题
        if len(df.columns) < 11:
            print(f"  警告: {filename} 只有 {len(df.columns)} 列，跳过")
            return None

        # 确保有足够的列，重命名
        expected_cols = ['timestamp', 'datetime', 'trade_id', 'market_id_col',
                         'token_id', 'side', 'price', 'size', 'amount', 'tx_hash', 'raw']
        df.columns = expected_cols[:len(df.columns)]

        # 添加market_id和outcome
        df['market_id'] = market_id
        df['file_outcome'] = file_outcome

        # 解析raw字段
        parsed = df['raw'].apply(parse_raw_field)

        # 提取解析结果
        df['trader_address'] = parsed.apply(lambda x: x['trader_address'])
        df['outcome'] = parsed.apply(lambda x: x['outcome'])

        # 处理时间戳
        df['datetime_parsed'] = pd.to_datetime(df['timestamp'], unit='s')

        # 确保amount是数值类型
        df['amount'] = pd.to_numeric(df['amount'], errors='coerce')

        # 删除全为空的列
        df = df.dropna(axis=1, how='all')

        print(f"  ✅ {filename}: {len(df)} 条订单")
        return df

    except Exception as e:
        print(f"处理文件 {file_path} 时出错: {e}")
        return None


def main():
    print("=" * 50)
    print("开始查找数据文件...")
    print("=" * 50)

    # 1. 查找所有文件
    all_files = find_all_data_files()

    print(f"\n总共找到 {len(all_files)} 个文件")

    if not all_files:
        print("\n❌ 没有找到任何 *_YES.csv 或 *_NO.csv 文件")
        print("当前搜索目录: " + os.path.abspath("."))
        return

    # 2. 分拣YES和NO文件
    yes_files = [f for f in all_files if '_YES' in os.path.basename(f).upper()]
    no_files = [f for f in all_files if '_NO' in os.path.basename(f).upper()]

    print(f"\nYES文件: {len(yes_files)} 个")
    print(f"NO文件: {len(no_files)} 个")

    # 3. 处理所有文件
    print("\n" + "=" * 50)
    print("开始处理文件...")
    print("=" * 50)

    all_dfs = []
    for file_path in tqdm(all_files, desc="处理进度"):
        df = process_file(file_path)
        if df is not None and len(df) > 0:
            all_dfs.append(df)

    if not all_dfs:
        print("\n❌ 没有成功处理任何文件")
        return

    # 4. 合并所有数据
    print("\n" + "=" * 50)
    print("合并所有数据...")
    print("=" * 50)

    combined_df = pd.concat(all_dfs, ignore_index=True)

    # 5. 选择需要的列
    available_cols = combined_df.columns.tolist()
    print(f"可用列: {available_cols}")

    # 核心列（必须有的）
    core_cols = ['timestamp', 'tx_hash', 'trader_address', 'price', 'amount', 'side', 'market_id']

    # 只保留存在的核心列
    final_cols = [col for col in core_cols if col in combined_df.columns]

    # 添加可选列
    optional_cols = ['datetime_parsed', 'outcome', 'file_outcome', 'token_id', 'size']
    for col in optional_cols:
        if col in combined_df.columns:
            final_cols.append(col)

    final_df = combined_df[final_cols].copy()

    # 6. 重命名列
    rename_map = {
        'tx_hash': 'transaction_hash',
        'amount': 'amount_usd',
        'datetime_parsed': 'datetime',
        'size': 'size_tokens'
    }

    # 只重命名存在的列
    rename_cols = {k: v for k, v in rename_map.items() if k in final_df.columns}
    final_df = final_df.rename(columns=rename_cols)

    # 7. 排序
    final_df = final_df.sort_values('timestamp')

    # 8. 保存结果到模块根目录
    output_file = os.path.join(module_root, 'all_orders_processed.csv')
    final_df.to_csv(output_file, index=False)

    print(f"\n✅ 处理完成！")
    print(f"  总订单数: {len(final_df):,}")
    print(f"  唯一市场数: {final_df['market_id'].nunique()}")

    if 'trader_address' in final_df.columns:
        print(f"  唯一地址数: {final_df['trader_address'].nunique():,}")

    if 'datetime' in final_df.columns:
        print(f"  时间范围: {final_df['datetime'].min()} 到 {final_df['datetime'].max()}")

    if 'amount_usd' in final_df.columns:
        print(f"  总金额: ${final_df['amount_usd'].sum():,.2f}")
        print(f"  平均订单金额: ${final_df['amount_usd'].mean():.2f}")
        print(f"  最大订单金额: ${final_df['amount_usd'].max():.2f}")

    print(f"\n📁 结果已保存到: {output_file}")

    # 9. 显示预览
    print("\n📊 数据预览 (前5行):")
    print(final_df.head())

    # 10. 保存处理日志
    log_file = os.path.join(module_root, 'processing_log.txt')
    with open(log_file, 'w') as f:
        f.write(f"处理时间: {pd.Timestamp.now()}\n")
        f.write(f"找到文件数: {len(all_files)}\n")
        f.write(f"成功处理文件数: {len(all_dfs)}\n")
        f.write(f"总订单数: {len(final_df)}\n")
    print(f"\n📁 日志已保存到: {log_file}")


if __name__ == "__main__":
    main()