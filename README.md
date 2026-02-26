# OpenClaw FundCoach

中国公募基金量化组合研究与模拟智能体

## 功能特性
- 基金数据抓取（天天基金）
- 因子分析和基金打分
- 组合优化和权重分配
- 历史回测（3年+牛熊周期）
- 风险指标计算
- 用户交互界面

## 开发计划
两周内完成核心功能开发

## 安装指南 (Mac)

### 1. 系统要求
- macOS 10.15 或更高版本
- Python 3.8+ 
- Git

### 2. 克隆代码仓库
```bash
git clone https://github.com/huchunxu/openclaw_fundcoach.git
cd openclaw_fundcoach
```

### 3. 创建虚拟环境（推荐）
```bash
# 使用venv创建虚拟环境
python3 -m venv fundcoach-env
source fundcoach-env/bin/activate

# 或者使用conda（如果已安装）
conda create -n fundcoach python=3.9
conda activate fundcoach
```

### 4. 安装依赖
```bash
pip install -r requirements.txt
```

### 5. 运行MVP演示
```bash
python mvp_demo.py
```

### 6. 运行单元测试
```bash
# 运行所有测试
python -m unittest discover tests/

# 运行特定模块测试
python agents/data_backtest/test_backtest_engine.py
python agents/strategy_agent/test_strategy.py
python agents/portfolio_agent/test_portfolio.py
python agents/risk_agent/test_risk.py
python agents/ui_agent/test_ui.py
```

## 目录结构
```
openclaw_fundcoach/
├── agents/
│   ├── data_backtest/          # 数据抓取和回测引擎
│   ├── strategy_agent/         # 因子建模和基金打分
│   ├── portfolio_agent/        # 组合生成和权重优化
│   ├── risk_agent/             # 风险分析和控制
│   └── ui_agent/               # 用户界面和可视化
├── tests/                      # 单元测试
├── mvp_demo.py                 # MVP演示脚本
├── requirements.txt            # 依赖包列表
└── README.md                   # 项目说明
```

## 使用示例

### 自动模式（全市场筛选）
```python
from agents.ui_agent.user_interface import UserInterface

ui = UserInterface()
config = ui.get_auto_mode_config()
# 使用config进行自动分析
```

### 手动模式（指定基金）
```python
from agents.ui_agent.user_interface import UserInterface

ui = UserInterface()
fund_codes = ['000001', '000002', '000003']
config = ui.get_manual_mode_config(fund_codes)
# 使用config进行手动分析
```

## 注意事项
- 所有结果基于历史数据，**不构成投资建议**
- 系统需要网络连接以获取基金数据
- 首次运行可能需要几分钟来下载和处理数据
- 建议在虚拟环境中运行以避免依赖冲突

## 贡献
欢迎提交Issue和Pull Request！