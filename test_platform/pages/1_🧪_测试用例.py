"""测试用例浏览页面"""
import streamlit as st
from pathlib import Path
import re

st.set_page_config(
    page_title="测试用例 - API自动化测试平台",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

st.title("📋 测试用例浏览")

project_root = Path(__file__).parent.parent.parent
test_cases_dir = project_root / "test_cases"

# 模块选择 - 只显示有测试文件的模块
all_modules = [d for d in test_cases_dir.iterdir() if d.is_dir() and not d.name.startswith('__')]
modules_with_tests = []
for module_dir in all_modules:
    test_files = list(module_dir.glob("test_*.py"))
    if len(test_files) > 0:
        modules_with_tests.append(module_dir.name)

modules = sorted(modules_with_tests)

if not modules:
    st.error("❌ 未找到包含测试文件的模块")
    st.stop()

# 模块 + 文件选择放一行两列
sel_col1, sel_col2 = st.columns(2)

with sel_col1:
    selected_module = st.selectbox("📁 选择模块", modules, index=0)

module_path = test_cases_dir / selected_module
test_files = sorted(module_path.glob("test_*.py"))

with sel_col2:
    if test_files:
        selected_file = st.selectbox(
            "📄 选择测试文件",
            [f.name for f in test_files],
            index=0
        )
    else:
        st.warning("⚠️ 该模块暂无测试文件")
        st.stop()

st.markdown("---")

if not test_files:
    st.warning("⚠️ 该模块暂无测试文件")
else:
    file_path = module_path / selected_file

    # 文件名标题，用 HTML 避免 Streamlit markdown 自动生成锚点链接
    st.markdown(f"<h4 style='margin:0'>📝 {selected_file}</h4>", unsafe_allow_html=True)
    st.markdown(" ")

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        test_methods = re.findall(
            r'def (test_\w+)\([^)]*\):\s*"""(.*?)"""',
            content,
            re.DOTALL
        )

        if test_methods:
            total = len(test_methods)

            # 展开状态（默认收起）
            expanded = st.session_state.get("expand_all_state", False)

            st.info(f"共找到 **{total}** 个测试场景")

            btn_label = "📁 收起全部" if expanded else "📂 展开全部"
            if st.button(btn_label, key="toggle_all"):
                st.session_state["expand_all_state"] = not expanded
                st.rerun()

            for idx, (method_name, docstring) in enumerate(test_methods, 1):
                with st.expander(f"🧪 测试场景{idx}: {method_name}", expanded=expanded):
                    lines = docstring.strip().split('\n')
                    scenario_desc = lines[0].strip() if lines else "无描述"

                    st.markdown(f"**{scenario_desc}**")

                    verification_points = []
                    for line in lines[1:]:
                        stripped = line.strip()
                        if not stripped:
                            continue
                        if stripped in ("验证点：", "验证点:"):
                            continue
                        if stripped.startswith(('1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.', '-', '•')):
                            verification_points.append(stripped)

                    if verification_points:
                        st.markdown("**验证点：**")
                        for vp in verification_points:
                            clean_vp = re.sub(r'^[\d\.\-•\s]+', '', vp).strip()
                            if clean_vp:
                                st.markdown(f"- {clean_vp}")
        else:
            st.warning("⚠️ 未找到测试方法")

        with st.expander("📄 查看完整代码", expanded=False):
            st.code(content, language="python")

    except Exception as e:
        st.error(f"❌ 读取文件失败: {str(e)}")

st.markdown("---")
st.caption("💡 提示：点击展开查看测试场景详情，或使用一键展开/收起按钮")
