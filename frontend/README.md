# OpenClaw FundCoach Frontend

React前端应用，提供现代化的用户界面和交互体验。

## 技术栈
- React 18
- Vite (开发服务器)
- Tailwind CSS (样式框架)
- React Router (路由管理)
- Axios (HTTP客户端)

## 开发环境

### 安装依赖
```bash
cd frontend
npm install
```

### 启动开发服务器
```bash
npm run dev
```

开发服务器将运行在 `http://localhost:3000`，并自动代理API请求到后端 `http://localhost:5000`。

## 项目结构
```
frontend/
├── public/              # 静态资源
├── src/
│   ├── components/      # UI组件
│   ├── pages/          # 页面组件
│   ├── services/       # API服务
│   ├── utils/          # 工具函数
│   ├── App.jsx         # 根组件
│   └── main.jsx        # 应用入口
├── vite.config.js      # Vite配置
└── tailwind.config.js  # Tailwind配置
```

## 构建生产版本
```bash
npm run build
```

构建后的文件将输出到 `dist/` 目录。