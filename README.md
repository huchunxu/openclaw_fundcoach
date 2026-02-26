# OpenClaw FundCoach

中国公募基金量化组合研究与模拟智能体

## 功能特性
- 基金数据抓取（天天基金）
- 因子分析和基金打分
- 组合优化和权重分配
- 历史回测（3年+牛熊周期）
- 风险指标计算
- 现代化Web界面（React + Tailwind CSS）

## 一键运行

### 开发模式（推荐）
```bash
# 一键启动开发环境
./start.sh dev
```

### 生产模式
```bash
# 构建并启动生产版本
./start.sh build
./start.sh
```

## 手动运行

### 安装依赖
```bash
# Python依赖
pip install -r web_app/requirements_mac.txt

# Node.js依赖  
cd frontend && npm install
```

### 启动应用
```bash
# 开发模式（前后端分离）
npm run dev

# 生产模式（单进程）
npm start
```

## 访问应用
- 开发模式: `http://localhost:3000`
- 生产模式: `http://localhost:5000`

## 目录结构
```
openclaw_fundcoach/
├── backend/              # Flask API后端
├── frontend/             # React前端
├── tests/                # 单元测试
├── mvp_demo.py           # MVP演示脚本
├── start.sh              # 一键启动脚本
├── package.json          # 项目脚本
└── README.md             # 项目说明
```

## 注意事项
- 所有结果基于历史数据，**不构成投资建议**
- 系统需要网络连接以获取基金数据
- 首次运行可能需要几分钟来下载和处理数据