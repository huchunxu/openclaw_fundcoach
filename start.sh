#!/bin/bash

# OpenClaw FundCoach 一键启动脚本

echo "🚀 启动 OpenClaw FundCoach..."

# 检查Python依赖
echo "🔍 检查Python依赖..."
if ! python3 -c "import flask" &> /dev/null; then
    echo "❌ Flask未安装，正在安装..."
    pip3 install -r web_app/requirements_mac.txt
fi

# 检查Node.js依赖
echo "🔍 检查Node.js依赖..."
if [ ! -d "frontend/node_modules" ]; then
    echo "📦 安装前端依赖..."
    cd frontend && npm install && cd ..
fi

# 启动应用
echo "🚀 启动应用..."
if [ "$1" = "dev" ]; then
    echo "🔧 开发模式：前后端分离运行"
    npm run dev
elif [ "$1" = "build" ]; then
    echo "🏗️  构建生产版本..."
    cd frontend && npm run build && cd ..
    echo "✅ 构建完成，运行 npm start 启动生产服务器"
else
    echo "🚀 生产模式：单进程运行"
    npm start
fi