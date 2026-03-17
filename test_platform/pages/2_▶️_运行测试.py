"""运行测试页面"""
import streamlit as st
from pathlib import Path
import subprocess
import time
from datetime import datetime
import re
import sys
import os

st.set_page_config(
    page_title="运行测试 - API自动化测试平台",
    page_icon="▶️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 隐藏页脚
st.markdown("""
<style>
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

st.title("▶️ 运行测试")

project_root = Path(__file__).parent.parent.parent
test_cases_dir = project_root / "test_cases"

# 运行模式选择（使用选择框代替单选按钮）
st.subheader("🎯 选择运行模式")
run_mode = st.selectbox(
    "运行方式",
    ["按模块运行", "按文件运行", "运行全部"],
    index=2,
    label_visibility="collapsed"
)

st.markdown("---")

# 运行配置
col1, col2 = st.columns(2)

with col1:
    # 只显示有测试文件的模块
    all_modules = [d for d in test_cases_dir.iterdir() if d.is_dir() and not d.name.startswith('__')]
    modules_with_tests = []
    for module_dir in all_modules:
        test_files_count = list(module_dir.glob("test_*.py"))
        if len(test_files_count) > 0:
            modules_with_tests.append(module_dir.name)
    
    modules = sorted(modules_with_tests)
    
    if run_mode == "按模块运行":
        if not modules:
            st.error("❌ 未找到包含测试文件的模块")
            st.stop()
        selected_module = st.selectbox("📁 选择模块", modules)
        test_path = f"test_cases/{selected_module}/"
        
    elif run_mode == "按文件运行":
        if not modules:
            st.error("❌ 未找到包含测试文件的模块")
            st.stop()
        selected_module = st.selectbox("📁 选择模块", modules)
        module_path = test_cases_dir / selected_module
        test_files = sorted([f.name for f in module_path.glob("test_*.py")])
        
        if test_files:
            selected_file = st.selectbox("📄 选择文件", test_files)
            test_path = f"test_cases/{selected_module}/{selected_file}"
        else:
            st.warning("⚠️ 该模块暂无测试文件")
            st.stop()
    else:
        test_path = "test_cases/"

with col2:
    pytest_options = st.multiselect(
        "🔧 pytest参数",
        ["-v (详细输出)", "-s (显示print)", "--tb=short (简短回溯)", "-x (首次失败停止)"],
        default=["-v (详细输出)"]
    )
    
    # 转换为实际参数
    actual_options = []
    for opt in pytest_options:
        actual_options.append(opt.split()[0])

# 显示将要执行的命令
cmd_parts = ["pytest", test_path] + actual_options
cmd_display = " ".join(cmd_parts)

st.code(f"$ {cmd_display}", language="bash")

st.markdown("---")

# 运行按钮
if st.button("🚀 开始运行", type="primary", key="btn_start_run"):
    
    # 运行信息
    st.subheader("📊 运行状态")
    
    status_placeholder = st.empty()
    output_placeholder = st.empty()
    
    with status_placeholder.container():
        st.info(f"⏳ 正在运行测试... 开始时间: {datetime.now().strftime('%H:%M:%S')}")
    
    # 执行命令
    start_time = time.time()
    
    try:
        # 构建完整的执行命令，包含环境变量设置
        venv_python = project_root / ".venv" / "bin" / "python"
        
        if venv_python.exists():
            # 使用虚拟环境的python -m pytest
            full_cmd = [
                str(venv_python),
                "-m", "pytest"
            ] + cmd_parts[1:]  # 跳过原来的pytest命令
        else:
            # 回退到系统pytest
            full_cmd = cmd_parts
        
        # 设置PYTHONPATH确保能导入项目模块
        env = os.environ.copy()
        env["PYTHONPATH"] = str(project_root)
        
        # 切换到项目根目录执行
        result = subprocess.run(
            full_cmd,
            cwd=str(project_root),
            capture_output=True,
            text=True,
            timeout=300,  # 5分钟超时
            env=env
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        # 显示结果
        with status_placeholder.container():
            if result.returncode == 0:
                st.success(f"✅ 测试完成！耗时: {duration:.2f}秒")
            else:
                st.error(f"❌ 测试失败！耗时: {duration:.2f}秒")
        
        # 输出详情
        with output_placeholder.container():
            st.subheader("📝 测试输出")
            
            tab1, tab2 = st.tabs(["标准输出", "错误输出"])
            
            with tab1:
                if result.stdout:
                    st.code(result.stdout, language="bash")
                else:
                    st.info("无标准输出")
            
            with tab2:
                if result.stderr:
                    st.code(result.stderr, language="bash")
                else:
                    st.info("无错误输出")
        
        # 提取统计信息
        output = result.stdout + result.stderr
        
        # 使用正则提取统计数据
        passed_match = re.search(r'(\d+) passed', output)
        failed_match = re.search(r'(\d+) failed', output)
        skipped_match = re.search(r'(\d+) skipped', output)
        
        passed = int(passed_match.group(1)) if passed_match else 0
        failed = int(failed_match.group(1)) if failed_match else 0
        skipped = int(skipped_match.group(1)) if skipped_match else 0
        
        if passed > 0 or failed > 0 or skipped > 0:
            st.markdown("---")
            st.subheader("📈 测试统计")
            
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("✅ 通过", passed)
            col2.metric("❌ 失败", failed)
            col3.metric("⏭️ 跳过", skipped)
            
            total = passed + failed + skipped
            if total > 0:
                pass_rate = (passed / total) * 100
                col4.metric("📊 通过率", f"{pass_rate:.1f}%")
        
    except subprocess.TimeoutExpired:
        with status_placeholder.container():
            st.error("❌ 测试超时！（超过5分钟）")
    
    except Exception as e:
        with status_placeholder.container():
            st.error(f"❌ 运行出错：{str(e)}")

st.markdown("---")
st.caption("💡 提示：运行大量测试可能需要几分钟时间，请耐心等待")
