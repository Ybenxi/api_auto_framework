#!/bin/bash
# API自动化测试管理平台 - 启动脚本

cd "$(dirname "$0")"

echo "🧪 启动API自动化测试管理平台..."
echo ""

# 检查虚拟环境
if [ -d ".venv" ]; then
    echo "✓ 检测到虚拟环境"
    source .venv/bin/activate
else
    echo "⚠️  未检测到虚拟环境"
fi

# 检查streamlit是否安装
if ! python3 -c "import streamlit" 2>/dev/null; then
    echo "⚠️  streamlit未安装，正在安装..."
    pip install streamlit
    echo ""
fi

echo "🚀 启动平台..."
echo "📱 浏览器将自动打开 http://localhost:8501"
echo "📝 使用 Ctrl+C 停止服务"
echo ""

streamlit run test_platform/app.py
