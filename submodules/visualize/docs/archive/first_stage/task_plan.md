# Visualize子模块开发计划

## 目标声明
- 优化市场数据可视化功能，提升代码质量和性能
- 开发异常可视化功能，与algorithm子模块集成
- 确保所有功能与现有系统兼容，提供一致的用户体验

## 阶段规划

### 阶段1：代码结构分析与优化规划
- **状态**：completed
- **目标**：分析现有代码结构，制定优化方案
- **任务**：
  - 分析当前app.py的代码结构和依赖关系
  - 识别代码中的可优化点和架构问题
  - 制定代码重构和架构改进方案
  - 确定优化后的模块划分和文件结构

### 阶段2：市场数据可视化功能优化
- **状态**：completed
- **目标**：重构代码，提升可维护性、可扩展性和性能
- **任务**：
  - 重构代码结构，采用模块化设计
  - 优化数据加载和缓存机制
  - 改进UI组件和交互体验
  - 确保与现有系统的兼容性
  - 性能测试和优化

### 阶段3：异常检测接口设计
- **状态**：completed
- **目标**：设计与algorithm子模块的接口规范，基于实际数据资源
- **任务**：
  - 分析algorithm子模块的两个检测机制
  - **狙击手检测模块**：
    - 使用 frontend_sniper_detection/ 文件夹中的全部可用数据
    - 分析数据结构（41条候选，3条已验证案例）
    - 确认时间范围（2026-02-18 至 2026-02-19）
    - 分析样本分布（交易量、异常分数等）
    - 确保数据完整性校验（文件格式验证、数据范围确认、异常值初步筛查）
  - **市场压力异常检测模块**：
    - 使用 CS6290-polymarket-anomaly-detection/results 文件夹下的全部可用数据
    - 确认 results 文件夹存在（完整路径：`C:\Users\26947\Desktop\course_note\SemB\CS6290\course_files_export (1)\group project\ProjectOfPrivacy-enhancingTech\submodules\algorithm\CS6290-polymarket-anomaly-detection\results`）
    - 分析预期数据格式（基于 README 文档）
    - 确保数据完整性校验（文件格式验证、数据范围确认、异常值初步筛查）
  - 设计异常数据获取的接口规范
  - 定义数据格式和传输协议
  - 制定接口文档

### 阶段4：异常可视化功能开发
- **状态**：in_progress
- **目标**：实现异常展示功能，包含两个数据维度
- **任务**：
  - 实现与algorithm子模块的接口集成
    - 狙击手检测：基于 frontend_sniper_detection/ 数据
    - 市场压力检测：基于 CS6290-polymarket-anomaly-detection/results 数据
  - 开发异常数据的可视化组件
    - 狙击手检测可视化：41条候选列表、3条已验证案例详情
    - 市场压力检测可视化：压力事件列表、时间序列图表
  - 设计异常展示界面，确保与市场数据展示风格统一
  - 实现异常详情查看和分析功能
  - 测试异常数据的展示效果

### 阶段5：集成测试与优化
- **状态**：in_progress
- **目标**：确保所有功能正常运行，性能达到要求
- **任务**：
  - 进行集成测试，验证各模块间的协作
  - 性能测试和优化
  - 用户体验测试
  - 修复发现的问题
  - 文档完善

## 技术选型
- **前端框架**：Streamlit, Plotly, Pandas
- **代码结构**：模块化设计，配置管理，优化缓存
- **接口设计**：直接文件读取，标准化数据格式

## 资源分配
- **工具环境**：Python 3.10.11, pip, Git

## 质量保障
- **代码质量**：PEP 8规范，代码审查，单元测试
- **性能优化**：数据加载优化，渲染优化，内存管理
- **用户体验**：响应速度，界面一致性，错误处理

## 验收标准
- **市场数据可视化**：代码结构清晰，数据加载快，UI美观，兼容现有系统，支持多语言
- **异常可视化**：集成algorithm子模块，异常数据展示清晰，界面风格统一，支持筛选排序
- **整体功能**：所有功能正常，性能满足要求，用户体验良好，代码质量高，文档完善

## 风险评估
- **潜在风险**：接口兼容性问题，性能问题，UI一致性问题，数据质量问题
- **应对策略**：提前研究algorithm子模块输出格式，性能优化，统一设计规范，数据验证

## 数据路径
- **市场元数据**：C:\Users\26947\Desktop\course_note\SemB\CS6290\course_files_export (1)\group project\ProjectOfPrivacy-enhancingTech\submodules\data\polymarket_data
- **狙击手检测数据**：submodules/visualize/frontend_sniper_detection/
  - `stats/strict_sniper_candidates.csv`：41条严格狙击手候选
  - `stats/top10_suspicious_sessions.csv`：Top 10可疑会话
  - `all_cases.json`：所有候选案例（41条）
  - `detailed_cases.json`：3个已验证案例详情
  - `images/`：攻击窗口可视化图片（7张）
- **市场压力异常检测数据**：submodules/algorithm/CS6290-polymarket-anomaly-detection/results/
  - 预期文件：stress_events_enriched_{score_method}.csv
  - 预期文件：bucket_features_*.csv
  - 预期文件：bucket_scores_*.csv

## 代码重构和架构改进方案

### 1. 模块划分
- **config/**：配置管理
  - `settings.py`：应用配置
  - `paths.py`：路径配置
  - `language.py`：语言字典
- **data/**：数据处理
  - `data_loader.py`：数据加载函数
  - `data_processor.py`：数据处理函数
- **views/**：视图展示
  - `metadata_view.py`：元数据视图
  - `timeseries_view.py`：时间序列视图
  - `trade_view.py`：交易数据视图
  - `anomaly_view.py`：异常数据视图
- **utils/**：工具函数
  - `cache_utils.py`：缓存工具
  - `error_handling.py`：错误处理
  - `ui_utils.py`：UI工具
- **app.py**：主应用入口

### 2. 配置管理
- **集中配置**：使用配置文件管理所有配置参数
- **环境变量**：支持通过环境变量覆盖配置
- **路径管理**：使用绝对路径和相对路径相结合的方式

### 3. 性能优化
- **缓存策略**：
  - 全局数据缓存
  - 按需加载数据
  - 缓存过期策略
- **数据处理**：
  - 数据预处理
  - 数据过滤和聚合
  - 延迟加载
- **渲染优化**：
  - 图表数据采样
  - 异步渲染
  - 按需渲染

### 4. 代码组织
- **命名规范**：遵循PEP 8规范
- **代码注释**：添加详细的代码注释
- **函数职责**：单一职责原则
- **错误处理**：统一的错误处理机制

### 5. 异常检测集成
- **数据格式标准化**：定义统一的异常数据格式
- **接口实现**：直接从文件读取异常数据
- **可视化组件**：为两种检测机制分别开发可视化组件

### 6. 测试策略
- **单元测试**：为核心功能编写单元测试
- **集成测试**：测试模块间的协作
- **性能测试**：测试数据加载和渲染性能

### 7. 部署策略
- **依赖管理**：使用requirements.txt管理依赖
- **环境配置**：提供环境配置示例
- **部署文档**：编写部署指南

## 交付物
1. 优化后的市场数据可视化代码
2. 异常可视化功能代码
3. 接口规范文档
4. 测试报告
5. 用户使用文档

## 遇到的错误
| 错误 | 尝试次数 | 解决方案 |
|------|---------|---------|
| Market metadata file not found: ...\\submodules\\submodules\\data\\polymarket_data\\market_metadata.csv | 1 | 修复 paths.py 中的 PROJECT_ROOT 计算，从 parents[2] 改为 parents[3] |
