# 异常检测接口规范文档

## 1. 概述
本文档定义了 Visualize 子模块与 Algorithm 子模块之间的接口规范，用于获取和处理异常检测数据。基于实际数据资源分析，本文档详细说明了两个检测机制的接口定义、数据格式和集成方案。

## 2. 检测机制概述

### 2.1 市场压力异常检测
**模块**：CS6290-polymarket-anomaly-detection
**功能**：检测市场压力异常事件（market stress events）
**检测维度**：
- 交易活跃度异常
- 流动性异常
- 价格行为异常

### 2.2 狙击手攻击检测
**模块**：sniper_detection
**功能**：检测狙击手攻击（Sniper attacks）
**定义**：大交易量 + 先买后卖 + 超短持有时间 + 2笔交易
**数据来源**：`submodules/visualize/frontend_sniper_detection/`（包含41条候选记录，3条已验证案例）

## 3. 数据获取接口

### 3.1 市场压力异常数据

#### 3.1.1 事件级别数据（Event-level）
**文件路径**：
```
{ALGORITHM_ROOT}/CS6290-polymarket-anomaly-detection/results/activity_pipeline_batch/{market_id}_YES/stress_events_enriched_{score_method}.csv
```

**核心字段**：
- `start_datetime`：事件开始时间
- `end_datetime`：事件结束时间
- `duration_minutes`：事件持续时间（分钟）
- `peak_stress_score`：峰值压力分数
- `total_amount`：事件期间总交易量
- `max_abs_midpoint_return`：最大绝对中点回报
- `max_spread`：最大点差
- `min_total_depth`：最小总深度
- `max_abs_depth_imbalance`：最大绝对深度失衡
- `snapshot_covered`：快照覆盖情况
- `num_snapshot_buckets`：快照桶数量
- `activity_component`：活跃度驱动成分
- `liquidity_component`：流动性驱动成分
- `price_component`：价格驱动成分
- `dominant_driver`：主导驱动因素
- `market_file`：市场文件名
- `market_stem`：市场标识

#### 3.1.2 时间桶级别特征数据（Bucket-level Features）
**文件路径**：
```
{ALGORITHM_ROOT}/CS6290-polymarket-anomaly-detection/results/activity_pipeline_batch/{market_id}_YES/bucket_features_{score_method}.csv
```

**核心字段**：
- `bucket`：时间桶编号
- `datetime`：时间戳
- `trade_count`：交易笔数
- `amount_sum`：交易总金额
- `avg_trade_size`：平均单笔交易额
- `midpoint`：中点价格
- `spread`：点差
- `total_depth`：总深度
- `depth_imbalance`：深度失衡
- `midpoint_return`：中点回报
- `abs_midpoint_return`：绝对中点回报
- `market_file`：市场文件名
- `market_stem`：市场标识

#### 3.1.3 时间桶级别分数数据（Bucket-level Scores）
**文件路径**：
```
{ALGORITHM_ROOT}/CS6290-polymarket-anomaly-detection/results/activity_pipeline_batch/{market_id}_YES/bucket_scores_{score_method}.csv
```

**核心字段**：
- `bucket`：时间桶编号
- `datetime`：时间戳
- `z_trade_count`：交易笔数 z-score
- `z_amount_sum`：交易金额 z-score
- `z_avg_trade_size`：平均交易大小 z-score
- `z_spread`：点差 z-score
- `z_depth_drop`：深度下降 z-score
- `z_abs_midpoint_return`：绝对中点回报 z-score
- `z_abs_depth_imbalance`：绝对深度失衡 z-score
- `activity_component`：活跃度成分
- `liquidity_component`：流动性成分
- `price_component`：价格成分
- `stress_score`：压力分数
- `is_stress_anomaly`：是否为异常桶
- `market_file`：市场文件名
- `market_stem`：市场标识

#### 3.1.4 市场汇总数据（Batch-level Summary）
**文件路径**：
```
{ALGORITHM_ROOT}/CS6290-polymarket-anomaly-detection/results/activity_pipeline_batch/market_stress_summary_{score_method}.csv
```

**核心字段**：
- `market_file`：市场文件名
- `market_stem`：市场标识
- `score_method`：评分方法
- `trade_bucket_rows`：交易桶数量
- `timeseries_bucket_rows`：时间序列桶数量
- `fused_rows`：融合后桶数量
- `non_null_midpoint_rows`：非空中点数据行数
- `non_null_spread_rows`：非空点差数据行数
- `stress_anomalies`：异常桶数量
- `stress_events`：异常事件数量
- `anomaly_rate`：异常率
- `event_rate`：事件率
- `snapshot_covered_events`：快照覆盖事件数
- `max_stress_score`：最大压力分数
- `max_event_peak_stress_score`：最大事件峰值压力分数
- `top_event_total_amount`：最大事件总金额
- `pca_explained_variance_ratio`：PCA 解释方差比（如适用）
- `error`：错误信息（如适用）

#### 3.1.5 所有市场事件总表（All Stress Events）
**文件路径**：
```
{ALGORITHM_ROOT}/CS6290-polymarket-anomaly-detection/results/activity_pipeline_batch/all_stress_events_{score_method}.csv
```

**核心字段**：
- 包含所有单个市场 stress_events_enriched_*.csv 的所有字段
- 用于跨市场比较和找出 top events

**数据状态**：✅ 文件夹存在，完整路径为：`C:\Users\26947\Desktop\course_note\SemB\CS6290\course_files_export (1)\group project\ProjectOfPrivacy-enhancingTech\submodules\algorithm\CS6290-polymarket-anomaly-detection\results`

### 3.2 狙击手攻击数据
**文件路径**：
```
{VISUALIZE_ROOT}/frontend_sniper_detection/
```

**核心文件**：
1. **strict_sniper_candidates.csv**：严格狙击手候选名单（41条记录）
   - `session_id`：会话ID
   - `num_trades`：交易数量
   - `total_volume`：总交易量
   - `max_trade`：最大单笔交易量
   - `has_large_trade`：是否有大交易
   - `first_side`：第一笔交易方向
   - `last_side`：最后一笔交易方向
   - `anomaly_score`：异常分数
   - `is_sniper`：是否为狙击手
   - `suspicious_rank`：可疑度排名

2. **all_cases.json**：所有候选案例（41条记录）
   - 包含与 CSV 相同的字段，以 JSON 格式存储

3. **detailed_cases.json**：3个已验证案例详情
   - `rank`：排名
   - `session_id`：会话ID
   - `duration_seconds`：持续时间（秒）
   - `anomaly_score`：异常分数
   - `buy`：买入详情（amount, price, time, date, tx_hash, polygonscan_url）
   - `sell`：卖出详情（amount, price, time, date, tx_hash, polygonscan_url）
   - `profit`：利润/损失
   - `image`：攻击窗口图片路径

4. **images/**：攻击窗口可视化图片（7张）
   - 包含已验证案例的攻击窗口图表

## 4. 数据格式规范

### 4.1 时间格式
- 所有时间字段应使用 ISO 8601 格式：`YYYY-MM-DD HH:MM:SS`
- 时区应统一为 UTC
- **狙击手检测数据**：时间字段分为 `date` (YYYY-MM-DD) 和 `time` (HH:MM:SS) 两个字段

### 4.2 数值格式
- 价格、金额等数值应使用浮点数
- 百分比应使用小数形式（如 0.05 表示 5%）
- **狙击手检测数据**：
  - 交易量范围：9,714.32 - 339,471.44
  - 异常分数范围：-0.6072 - -0.4120

### 4.3 分类字段
- `dominant_driver`：取值为 `activity`、`liquidity`、`price_dislocation`、`mixed`
- `first_side`/`last_side`：取值为 `BUY`、`SELL`
- `is_sniper`：取值为 `0`（否）、`1`（是）
- `has_large_trade`：取值为 `True`/`False`

## 5. 接口实现

### 5.1 数据加载函数
```python
# 加载市场压力异常事件数据（Event-level）
def load_polymarket_anomaly_data(market_id, score_method="additive"):
    """加载多市场异常检测数据"""
    # 实现逻辑...

# 加载 bucket 特征数据（Bucket-level Features）
def load_bucket_features(market_id, score_method="additive"):
    """加载 bucket 特征数据
    
    Args:
        market_id: str, 市场ID
        score_method: str, 评分方法 ("additive" 或 "pca")
    
    Returns:
        DataFrame: 包含融合后的 bucket 特征数据
    """
    # 实现逻辑...

# 加载 bucket 分数数据（Bucket-level Scores）
def load_bucket_scores(market_id, score_method="additive"):
    """加载 bucket 分数数据
    
    Args:
        market_id: str, 市场ID
        score_method: str, 评分方法 ("additive" 或 "pca")
    
    Returns:
        DataFrame: 包含 bucket 级别分数和异常标记
    """
    # 实现逻辑...

# 加载市场压力汇总数据（Batch-level Summary）
def load_market_stress_summary(score_method="additive"):
    """加载市场压力汇总数据
    
    Args:
        score_method: str, 评分方法 ("additive" 或 "pca")
    
    Returns:
        DataFrame: 包含所有市场的汇总信息
    """
    # 实现逻辑...

# 加载所有压力事件总表（All Stress Events）
def load_all_stress_events(score_method="additive"):
    """加载所有压力事件总表
    
    Args:
        score_method: str, 评分方法 ("additive" 或 "pca")
    
    Returns:
        DataFrame: 包含所有市场的 stress events
    """
    # 实现逻辑...

# 加载狙击手检测数据
def load_sniper_detection_data(data_type="all"):
    """加载狙击手检测数据
    
    Args:
        data_type: str, 数据类型
            - "all": 加载所有41条候选（从all_cases.json）
            - "strict": 加载严格候选（从strict_sniper_candidates.csv）
            - "detailed": 加载3个已验证案例（从detailed_cases.json）
    """
    # 实现逻辑...

# 加载狙击手攻击窗口图片
def load_sniper_image(session_id):
    """加载狙击手攻击窗口图片"""
    # 实现逻辑...
```

### 5.2 数据处理函数
```python
# 处理异常数据
def process_anomaly_data(anomaly_df, market_id=None):
    """处理异常数据，添加必要的计算字段"""
    # 实现逻辑...

# 处理狙击手检测数据
def process_sniper_data(sniper_data, data_type="all"):
    """处理狙击手检测数据
    
    Args:
        sniper_data: DataFrame 或 dict, 狙击手检测数据
        data_type: str, 数据类型
    """
    # 实现逻辑...
```

## 6. 错误处理

### 6.1 常见错误
- **文件不存在**：返回空 DataFrame，并记录警告
- **格式错误**：尝试修复格式，无法修复则返回空 DataFrame
- **数据缺失**：填充默认值或标记为缺失
- **市场压力数据缺失**：提示 results 文件夹不存在，建议先生成数据
- **狙击手数据格式错误**：检查 JSON/CSV 格式，尝试修复

### 6.2 错误处理策略
- 使用 try-except 捕获异常
- 记录详细的错误日志
- 提供友好的错误提示
- 确保系统在数据缺失时仍能正常运行
- 对于市场压力数据缺失，提供明确的生成指南

## 7. 性能优化

### 7.1 缓存策略
- 使用 Streamlit 的缓存机制缓存数据
- 设置合理的缓存过期时间
- 避免重复加载相同数据
- **狙击手数据**：缓存 JSON/CSV 文件内容，减少文件 I/O

### 7.2 数据处理优化
- 按需加载数据
- 只加载必要的字段
- 使用 pandas 的向量化操作
- **狙击手数据**：预加载详细案例数据，提高响应速度

## 8. 集成测试

### 8.1 测试用例
- 测试文件路径正确性
- 测试数据加载功能
- 测试数据处理功能
- 测试错误处理功能
- **狙击手数据**：测试不同数据类型的加载
- **市场压力数据**：测试 results 文件夹缺失的处理

### 8.2 测试环境
- 使用真实的算法子模块输出文件
- 模拟各种错误场景
- 验证数据可视化效果
- **狙击手数据**：使用 frontend_sniper_detection 中的实际数据

## 9. 版本控制

### 9.1 接口版本
- 初始版本：v1.0
- 变更记录：
  - v1.0：初始接口规范
  - v1.1：更新狙击手检测数据路径和格式

### 9.2 兼容性
- 确保与算法子模块的输出格式兼容
- 支持不同版本的算法输出
- **狙击手数据**：兼容 frontend_sniper_detection 中的数据格式

## 10. 数据完整性校验

### 10.1 狙击手检测数据校验
- **文件格式验证**：
  - CSV 文件格式正确，表头完整
  - JSON 文件结构清晰，符合预期
- **数据范围确认**：
  - 交易量：9,714.32 - 339,471.44
  - 异常分数：-0.6072 - -0.4120
  - 交易数量：2-229笔
  - 可疑排名：1-23,589
- **异常值初步筛查**：
  - 最大交易量：339,471.44（suspicious_rank 2,525）
  - 最小异常分数：-0.6072（suspicious_rank 1）
  - 最多交易数量：229笔（suspicious_rank 8）

### 10.2 市场压力异常数据校验
- **文件格式验证**：
  - 验证 CSV 文件格式
  - 检查必需字段是否存在
  - 验证日期时间格式
- **数据范围确认**：
  - 确认时间戳范围
  - 验证压力分数范围
  - 确认交易量范围
- **异常值初步筛查**：
  - 检查缺失值
  - 识别极端值
  - 验证数据一致性

## 11. 附录

### 11.1 示例数据
**市场压力异常数据示例：**
| start_datetime       | end_datetime         | duration_minutes | peak_stress_score | total_amount |
|----------------------|----------------------|-----------------|-------------------|-------------|
| 2026-02-14 00:00:00 | 2026-02-14 00:05:00 | 5.0             | 9.8               | 100000.0    |
| 2026-02-14 01:30:00 | 2026-02-14 01:32:00 | 2.0             | 7.5               | 50000.0     |

**狙击手攻击数据示例：**
| session_id                          | num_trades | total_volume | max_trade  | is_sniper |
|-------------------------------------|------------|--------------|------------|-----------|
| 0x28d47763e7a53ef2c1e0d6fabfc59d9dfff3ba55_1 | 2          | 35770.35     | 17894.13   | 1         |
| 0x63b81ddc36a228f7431a534d67eb058b7cc0f906_1 | 2          | 35490.45     | 17754.11   | 1         |

**详细狙击手案例示例：**
```json
{
  "rank": 2,
  "session_id": "0x28d47763e7a53ef2c1e0d6fabfc59d9dfff3ba55_1",
  "duration_seconds": 74,
  "anomaly_score": -0.4933,
  "buy": {
    "amount": 17894.13,
    "price": 0.9990,
    "time": "20:57:50",
    "date": "2026-02-18",
    "tx_hash": "0x733305afcdfd53e4331fd2164fd36fc6796e2df96134782100df23dda926ff69",
    "polygonscan_url": "https://polygonscan.com/tx/0x733305afcdfd53e4331fd2164fd36fc6796e2df96134782100df23dda926ff69"
  },
  "sell": {
    "amount": 17876.22,
    "price": 0.9980,
    "time": "20:59:04",
    "date": "2026-02-18",
    "tx_hash": "0x6addf209ed9f4a3ec8d21cf76dde171aef1947adca47d6da947a213de23f6cca",
    "polygonscan_url": "https://polygonscan.com/tx/0x6addf209ed9f4a3ec8d21cf76dde171aef1947adca47d6da947a213de23f6cca"
  },
  "profit": -17.91,
  "image": "images/sniper_rank2_74seconds.png"
}
```
