"""运行测试页面 - 支持实时输出 + 切换页面后恢复状态"""
import streamlit as st
from pathlib import Path
import subprocess
import time
import json
import os
import re
from datetime import datetime

st.set_page_config(
    page_title="运行测试 - API自动化测试平台",
    page_icon="▶️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

st.title("▶️ 运行测试")

project_root = Path(__file__).parent.parent.parent
test_cases_dir = project_root / "test_cases"
reports_dir = project_root / "reports"
reports_dir.mkdir(exist_ok=True)

RUN_LOG = reports_dir / "running.log"
RUN_STATUS = reports_dir / "run_status.json"


def read_run_status() -> dict:
    """读取运行状态文件，不存在则返回空"""
    if RUN_STATUS.exists():
        try:
            return json.loads(RUN_STATUS.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def render_result(status: dict):
    """根据 run_status.json 渲染结果区域"""
    state = status.get("state", "")
    start_time = status.get("start_time", "")
    cmd = status.get("cmd", "")

    if cmd:
        st.code(f"$ {cmd}", language="bash")

    if state == "running":
        elapsed = time.time() - status.get("start_ts", time.time())
        st.info(f"⏳ 测试运行中... 开始时间: {start_time}  已用时: {elapsed:.0f}s")
        log_content = RUN_LOG.read_text(encoding="utf-8", errors="replace") if RUN_LOG.exists() else ""
        if log_content:
            st.markdown("**📺 实时输出：**")
            st.code(log_content, language="bash")
        else:
            st.caption("等待输出...")
        # 2秒后自动刷新
        time.sleep(2)
        st.rerun()

    elif state == "done":
        duration = status.get("duration", 0)
        returncode = status.get("returncode", -1)
        if returncode == 0:
            st.success(f"✅ 测试完成！耗时: {duration:.1f}s  开始时间: {start_time}")
        else:
            st.error(f"❌ 测试有失败项！耗时: {duration:.1f}s  开始时间: {start_time}")

        # 统计信息
        passed = status.get("passed", 0)
        failed = status.get("failed", 0)
        skipped = status.get("skipped", 0)
        total = passed + failed + skipped
        if total > 0:
            st.markdown("---")
            st.subheader("📈 测试统计")
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("✅ 通过", passed)
            c2.metric("❌ 失败", failed)
            c3.metric("⏭️ 跳过", skipped)
            pass_rate = (passed / total) * 100
            c4.metric("📊 通过率", f"{pass_rate:.1f}%")

        # 完整输出
        log_content = RUN_LOG.read_text(encoding="utf-8", errors="replace") if RUN_LOG.exists() else ""
        if log_content:
            with st.expander("📝 查看完整输出", expanded=False):
                st.code(log_content, language="bash")

    elif state == "error":
        st.error(f"❌ 运行出错：{status.get('error', '未知错误')}")


# ──────────────────────────────────────────────
# 读取当前运行状态
# ──────────────────────────────────────────────
current_status = read_run_status()
is_running = current_status.get("state") == "running"

# 如果当前是 running，先展示进度（占整页），不显示配置区
if is_running:
    st.markdown("---")
    st.subheader("📊 运行状态")
    render_result(current_status)
    st.stop()

# ──────────────────────────────────────────────
# 配置区（非运行中才显示）
# ──────────────────────────────────────────────
st.subheader("🎯 选择运行模式")
run_mode = st.selectbox(
    "运行方式",
    ["按模块运行", "按文件运行", "运行全部"],
    index=2,
    label_visibility="collapsed"
)

st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    all_modules = [d for d in test_cases_dir.iterdir() if d.is_dir() and not d.name.startswith('__')]
    modules_with_tests = []
    for module_dir in all_modules:
        if list(module_dir.glob("test_*.py")):
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
    actual_options = [opt.split()[0] for opt in pytest_options]

cmd_parts = ["pytest", test_path] + actual_options
cmd_display = " ".join(cmd_parts)
st.code(f"$ {cmd_display}", language="bash")
st.markdown("---")

# 上次结果（如果有）
if current_status.get("state") == "done":
    with st.expander("📋 上次运行结果", expanded=False):
        render_result(current_status)
    st.markdown("---")

# ──────────────────────────────────────────────
# 开始运行按钮
# ──────────────────────────────────────────────
if st.button("🚀 开始运行", type="primary", key="btn_start_run"):

    # 清空旧日志
    RUN_LOG.write_text("", encoding="utf-8")

    # 写入"运行中"状态
    now = datetime.now()
    RUN_STATUS.write_text(json.dumps({
        "state": "running",
        "start_time": now.strftime("%Y-%m-%d %H:%M:%S"),
        "start_ts": time.time(),
        "cmd": cmd_display,
    }, ensure_ascii=False), encoding="utf-8")

    # 构建完整命令
    venv_python = project_root / ".venv" / "bin" / "python"
    if venv_python.exists():
        full_cmd = [str(venv_python), "-m", "pytest"] + cmd_parts[1:]
    else:
        full_cmd = cmd_parts

    env = os.environ.copy()
    env["PYTHONPATH"] = str(project_root)

    # 用后台线程执行，主线程继续渲染
    import threading

    def run_pytest():
        start_ts = time.time()
        try:
            process = subprocess.Popen(
                full_cmd,
                cwd=str(project_root),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                env=env,
                bufsize=1
            )
            collected_output = []
            for line in process.stdout:
                collected_output.append(line)
                # 实时追加写入日志文件
                with open(RUN_LOG, "a", encoding="utf-8") as f:
                    f.write(line)
            process.wait()

            duration = time.time() - start_ts
            full_output = "".join(collected_output)

            # 解析统计
            passed = int(m.group(1)) if (m := re.search(r'(\d+) passed', full_output)) else 0
            failed = int(m.group(1)) if (m := re.search(r'(\d+) failed', full_output)) else 0
            skipped = int(m.group(1)) if (m := re.search(r'(\d+) skipped', full_output)) else 0

            # 更新状态为完成
            prev = json.loads(RUN_STATUS.read_text(encoding="utf-8"))
            prev.update({
                "state": "done",
                "duration": round(duration, 1),
                "returncode": process.returncode,
                "passed": passed,
                "failed": failed,
                "skipped": skipped,
            })
            RUN_STATUS.write_text(json.dumps(prev, ensure_ascii=False), encoding="utf-8")

        except Exception as e:
            prev = json.loads(RUN_STATUS.read_text(encoding="utf-8")) if RUN_STATUS.exists() else {}
            prev.update({"state": "error", "error": str(e)})
            RUN_STATUS.write_text(json.dumps(prev, ensure_ascii=False), encoding="utf-8")

    t = threading.Thread(target=run_pytest, daemon=True)
    t.start()

    # 立即刷新页面进入"运行中"模式
    time.sleep(0.5)
    st.rerun()

st.markdown("---")
st.caption("💡 提示：运行中可切换其他页面，回来后仍可查看进度")
