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

# 隐藏顶部菜单
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
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

selected_module = st.selectbox("📁 选择模块", modules, index=0)

module_path = test_cases_dir / selected_module

# 读取README
readme_file = module_path / "README.md"
if readme_file.exists():
    with st.expander("📖 模块说明", expanded=False):
        try:
            with open(readme_file, 'r', encoding='utf-8') as f:
                st.markdown(f.read())
        except Exception as e:
            st.error(f"读取README失败: {str(e)}")

st.markdown("---")

# 测试文件列表
test_files = sorted(module_path.glob("test_*.py"))

if not test_files:
    st.warning("⚠️ 该模块暂无测试文件")
else:
    # 选择测试文件
    selected_file = st.selectbox(
        "📄 选择测试文件", 
        [f.name for f in test_files],
        index=0
    )
    
    file_path = module_path / selected_file
    
    # 解析测试用例
    st.subheader(f"📝 {selected_file}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 提取测试方法和docstring
        # 匹配 def test_xxx(self, ...): """docstring"""
        test_methods = re.findall(
            r'def (test_\w+)\([^)]*\):\s*"""(.*?)"""', 
            content, 
            re.DOTALL
        )
        
        if test_methods:
            st.info(f"共找到 **{len(test_methods)}** 个测试场景")
            
            for idx, (method_name, docstring) in enumerate(test_methods, 1):
                with st.expander(f"🧪 测试场景{idx}: {method_name}", expanded=False):
                    # 提取场景描述
                    lines = docstring.strip().split('\n')
                    scenario_desc = lines[0] if lines else "无描述"
                    
                    st.markdown(f"**{scenario_desc}**")
                    
                    # 验证点
                    verification_points = [
                        line.strip() for line in lines 
                        if line.strip() and (
                            line.strip().startswith(('1.', '2.', '3.', '4.', '5.', '-', '•'))
                            or '验证' in line
                        )
                    ]
                    
                    if verification_points:
                        st.markdown("**验证点：**")
                        for vp in verification_points:
                            # 清理行首的数字和符号
                            clean_vp = re.sub(r'^[\d\.\-•\s]+', '', vp).strip()
                            if clean_vp:
                                st.markdown(f"- {clean_vp}")
                    
                    # 显示完整docstring
                    with st.expander("查看完整描述", expanded=False):
                        st.code(docstring.strip(), language="text")
        else:
            st.warning("⚠️ 未找到测试方法")
        
        # 代码预览
        with st.expander("📄 查看完整代码", expanded=False):
            st.code(content, language="python")
            
    except Exception as e:
        st.error(f"❌ 读取文件失败: {str(e)}")

st.markdown("---")
st.caption("💡 提示：点击展开查看测试场景详情")
