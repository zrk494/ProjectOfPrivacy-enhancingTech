# 项目发现记录

## 数据资源分析

### 1. 狙击手检测模块数据资源（frontend_sniper_detection/）
**位置**：`submodules/visualize/frontend_sniper_detection/`

#### 1.1 可用数据文件
| 文件 | 类型 | 描述 | 行数/记录数 |
|------|------|------|-------------|
| `stats/strict_sniper_candidates.csv` | CSV | 严格狙击手候选名单 | 41条记录 |
| `stats/top10_suspicious_sessions.csv` | CSV | Top 10可疑会话 | 11条记录（含表头） |
| `all_cases.json` | JSON | 所有候选案例 | 41条记录 |
| `detailed_cases.json` | JSON | 3个已验证案例详情 | 3条记录 |
| `images/` | 图片 | 攻击窗口可视化 | 7张图片 |

#### 1.2 数据结构分析

**strict_sniper_candidates.csv 字段**：
- `session_id`：会话唯一标识
- `num_trades`：交易数量
- `total_volume`：总交易量
- `max_trade`：最大单笔交易
- `has_large_trade`：是否有大交易（布尔值）
- `first_side`：第一笔交易方向（BUY/SELL）
- `last_side`：最后一笔交易方向（BUY/SELL）
- `anomaly_score`：异常分数（负值，越低越异常）
- `is_sniper`：是否为狙击手（0/1）
- `suspicious_rank`：可疑度排名

**detailed_cases.json 字段**（已验证案例）：
- `rank`：排名
- `session_id`：会话ID
- `duration_seconds`：持续时间（秒）
- `anomaly_score`：异常分数
- `buy`：买入详情
  - `amount`：买入金额
  - `price`：买入价格
  - `time`：买入时间
  - `date`：买入日期
  - `tx_hash`：交易哈希
  - `polygonscan_url`：Polygonscan链接
- `sell`：卖出详情
  - `amount`：卖出金额
  - `price`：卖出价格
  - `time`：卖出时间
  - `date`：卖出日期
  - `tx_hash`：交易哈希
  - `polygonscan_url`：Polygonscan链接
- `profit`：利润/损失
- `image`：攻击窗口图片路径

#### 1.3 样本分布分析
- **严格狙击手候选**：41条记录
  - 已验证案例：3条（rank 2, 3, 4）
  - 候选案例：38条
- **Top 10可疑会话**：10条记录
- **时间范围**：2026-02-18 至 2026-02-19
- **交易量范围**：~9,700 至 ~339,471
- **持续时间**：72-76秒（已验证案例）

#### 1.4 数据完整性校验
✅ **文件格式验证**：
- CSV文件格式正确，表头完整
- JSON文件结构清晰，符合预期

✅ **数据范围确认**：
- 交易量：9,714.32 - 339,471.44
- 异常分数：-0.6072 - -0.4120
- 交易数量：2-229笔
- 可疑排名：1-23,589

✅ **异常值初步筛查**：
- 最大交易量：339,471.44（suspicious_rank 2,525）
- 最小异常分数：-0.6072（suspicious_rank 1）
- 最多交易数量：229笔（suspicious_rank 8）

### 2. 市场压力异常检测模块（CS6290-polymarket-anomaly-detection）
**位置**：`submodules/algorithm/CS6290-polymarket-anomaly-detection/`

#### 2.1 数据资源状态
✅ **Results文件夹存在**：完整路径为：`C:\Users\26947\Desktop\course_note\SemB\CS6290\course_files_export (1)\group project\ProjectOfPrivacy-enhancingTech\submodules\algorithm\CS6290-polymarket-anomaly-detection\results`
📝 **预期输出**：根据README文档，应输出以下文件：
- `bucket_features_*.csv`：时间桶特征表
- `bucket_scores_*.csv`：时间桶分数表
- `stress_events_enriched_*.csv`：丰富的压力事件表（主要可视化数据）

#### 2.2 预期数据格式（基于README）

**stress_events_enriched_{score_method}.csv 核心字段**：
- `start_datetime`：事件开始时间
- `end_datetime`：事件结束时间
- `duration_minutes`：持续时间（分钟）
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
- `dominant_driver`：主导驱动因素（activity/liquidity/price_dislocation/mixed）

#### 2.3 数据完整性规划
1. **文件格式验证**：
   - 验证CSV文件格式
   - 检查必需字段是否存在
   - 验证日期时间格式

2. **数据范围确认**：
   - 确认时间戳范围
   - 验证压力分数范围
   - 确认交易量范围

3. **异常值初步筛查**：
   - 检查缺失值
   - 识别极端值
   - 验证数据一致性

## 代码结构分析
- **Visualize子模块**：app.py（主应用）、frontend_sniper_detection/（狙击手检测前端）、Visualize.md（文档）
- **Algorithm子模块**：
  - CS6290-polymarket-anomaly-detection/：多市场异常检测，输出stress_events_enriched_{score_method}.csv
  - sniper_detection/：狙击手检测，输出strict_sniper_candidates.csv

## 技术发现
- **前端技术**：Streamlit（Web应用框架）、Plotly（交互式图表）、Pandas（数据处理）
- **现有功能**：多语言支持、市场元数据展示、时间序列数据展示、交易数据展示
- **待完善功能**：异常检测功能（当前处于开发中状态）

## 数据路径
- **市场元数据**：C:\Users\26947\Desktop\course_note\SemB\CS6290\course_files_export (1)\group project\ProjectOfPrivacy-enhancingTech\submodules\data\polymarket_data
- **狙击手检测数据**：`submodules/visualize/frontend_sniper_detection/`
- **市场压力异常检测数据**：待检查 `submodules/algorithm/CS6290-polymarket-anomaly-detection/results/`

## 问题发现
- **代码结构**：单文件结构，缺乏模块化设计
- **数据路径**：硬编码路径，不适用所有环境
- **缓存机制**：已使用但可进一步优化
- **接口设计**：与algorithm子模块的接口未明确定义
- **狙击手数据**：有完整前端数据（41条候选，3条已验证）
- **市场压力数据**：results文件夹待确认

## 优化机会
- **代码重构**：采用模块化设计，集中管理配置
- **性能优化**：优化数据加载和缓存策略
- **用户体验**：统一界面风格，优化响应速度
- **功能完整性**：完善异常检测功能
- **狙击手可视化**：基于现有41条候选和3条已验证案例
- **市场压力可视化**：待确认results数据

## 风险评估
- **接口兼容性**：algorithm子模块接口可能与设计不符
- **数据质量**：异常数据可能存在质量问题
- **性能挑战**：大量数据处理可能导致性能下降
- **市场压力数据缺失**：需要确认是否生成了results数据

## 解决方案
- **代码结构**：模块化设计，配置文件管理，统一错误处理
- **接口设计**：RESTful API，标准化JSON数据格式
- **性能优化**：多级缓存，优化数据处理流程
- **用户体验**：统一设计风格，清晰错误提示
- **狙击手数据**：使用frontend_sniper_detection中的完整数据集
- **市场压力数据**：确认是否需要先生成results数据

## 后续研究
- **技术探索**：更先进的可视化库，实时数据处理技术
- **功能扩展**：更多数据可视化类型，机器学习模型集成
- **部署选项**：评估不同部署方案的扩展性
- **数据生成**：确认市场压力异常检测results数据生成流程

## 代码优化点

### 1. 代码结构问题
- **单文件结构**：所有功能都在app.py一个文件中，缺乏模块化设计
- **函数职责不清晰**：main函数较长，职责过多
- **缺乏目录结构**：没有合理的文件组织

### 2. 数据管理问题
- **硬编码路径**：数据加载路径硬编码，不适用所有环境
- **路径不统一**：使用了相对路径，可能导致跨平台问题
- **配置分散**：配置信息分散在代码各处

### 3. 性能问题
- **缓存策略**：虽然使用了@st.cache_data，但可进一步优化缓存策略
- **数据加载**：每次请求都重新加载数据，没有全局缓存
- **渲染性能**：图表渲染可能在大数据量时性能下降

### 4. 可维护性问题
- **缺乏注释**：代码注释较少，难以理解
- **硬编码字符串**：语言字典直接硬编码在文件中
- **错误处理**：错误处理机制可以更完善

### 5. 扩展性问题
- **异常检测集成**：异常检测功能只是占位符，未实现与algorithm子模块的集成
- **新功能添加**：难以添加新的可视化功能
- **接口设计**：缺乏与其他模块的标准接口

### 6. 架构问题
- **状态管理**：缺乏统一的状态管理机制
- **依赖管理**：依赖项管理可以更规范
- **测试覆盖**：缺乏单元测试
