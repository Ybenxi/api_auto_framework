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

# 确保 reports 目录存在（静态文件服务需要）
mkdir -p reports

# 启动报告静态文件服务（8502 端口，后台运行）
STATIC_PORT=8502
echo "📂 启动报告静态文件服务 (端口 $STATIC_PORT)..."

# 检查 8502 端口是否已占用
if lsof -ti:$STATIC_PORT > /dev/null 2>&1; then
    echo "✓ 报告静态服务已在运行（端口 $STATIC_PORT）"
else
    # 后台启动 Python 静态文件服务，指向 reports/ 目录
    python3 -m http.server $STATIC_PORT --directory reports/ > /tmp/reports_server.log 2>&1 &
    STATIC_PID=$!
    echo "✓ 报告静态服务已启动 (PID: $STATIC_PID，端口 $STATIC_PORT)"
    echo "  访问地址: http://localhost:$STATIC_PORT"
fi

echo ""
echo "🚀 启动Streamlit测试平台..."
echo "📱 访问地址: http://localhost:8501"
echo "📂 报告服务: http://localhost:8502"
echo "📝 使用 Ctrl+C 停止服务"
echo ""

# 启动 Streamlit（前台运行，Ctrl+C 时同时停止）
streamlit run "test_platform/首页.py"
