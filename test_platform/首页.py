"""
API自动化测试管理平台 - 总览页面
基于Streamlit构建的轻量级测试管理工具
"""
import streamlit as st
from pathlib import Path
import sys

# 页面配置
st.set_page_config(
    page_title="总览 - API自动化测试平台",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "API自动化测试管理平台 v1.1"
    }
)

# 自定义CSS - 隐藏部分英文元素
st.markdown("""
<style>
    /* 主页面样式 */
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .success-badge {
        background-color: #d4edda;
        color: #155724;
        padding: 0.25rem 0.5rem;
        border-radius: 0.25rem;
        font-weight: 600;
    }
    .error-badge {
        background-color: #f8d7da;
        color: #721c24;
        padding: 0.25rem 0.5rem;
        border-radius: 0.25rem;
        font-weight: 600;
    }
    
    /* 只隐藏页脚，保留其他元素 */
    footer {visibility: hidden;}
    
    /* 侧边栏样式优化 */
    [data-testid="stSidebar"] {
        min-width: 250px;
    }
</style>
""", unsafe_allow_html=True)

import sys
sys.path.insert(0, str(Path(__file__).parent))
# 主页面
st.markdown('<div class="main-header">🧪 API自动化测试管理平台</div>', unsafe_allow_html=True)

st.markdown("""
### 欢迎使用测试管理平台！

这是一个基于Streamlit构建的轻量级测试管理工具，帮助你：
- 📋 **可视化查看**所有测试用例
- ▶️ **一键运行**指定测试（模块/文件/单个用例）
- 📊 **实时查看**测试执行过程和结果
- 📈 **分析统计**测试历史数据和趋势

---
""")

# 项目统计
project_root = Path(__file__).parent.parent
test_cases_dir = project_root / "test_cases"

# 扫描测试统计
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    # 统计模块数量
    modules = [d for d in test_cases_dir.iterdir() if d.is_dir() and not d.name.startswith('__')]
    st.metric("📁 测试模块", f"{len(modules)}个")
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    # 统计测试文件
    test_files = list(test_cases_dir.rglob("test_*.py"))
    st.metric("📄 测试文件", f"{len(test_files)}个")
    st.markdown('</div>', unsafe_allow_html=True)

with col3:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    # 统计历史报告
    reports_dir = project_root / "reports"
    reports = list(reports_dir.glob("benxi_report_*.html")) if reports_dir.exists() else []
    st.metric("📊 历史报告", f"{len(reports)}个")
    st.markdown('</div>', unsafe_allow_html=True)

with col4:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("🎯 框架版本", "v3.0")
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")

# 快速操作
st.subheader("🚀 快速操作")

quick_col1, quick_col2, quick_col3 = st.columns(3)

with quick_col1:
    if st.button("📋 查看测试用例", key="btn_test_cases"):
        st.switch_page("pages/1_🧪_测试用例.py")

with quick_col2:
    if st.button("▶️ 运行测试", key="btn_run_test"):
        st.switch_page("pages/2_▶️_运行测试.py")

with quick_col3:
    if st.button("📊 查看报告", key="btn_reports"):
        st.switch_page("pages/3_📊_历史报告.py")

st.markdown("---")

# 测试模块列表
st.subheader("📦 测试模块列表")

modules_data = []
for module_dir in sorted(modules, key=lambda x: x.name):
    module_name = module_dir.name
    test_files_in_module = list(module_dir.glob("test_*.py"))
    
    # 跳过没有测试文件的模块
    if len(test_files_in_module) == 0:
        continue
    
    # 读取README获取描述
    readme_file = module_dir / "README.md"
    description = "暂无描述"
    if readme_file.exists():
        try:
            with open(readme_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                if len(lines) > 0:
                    description = lines[0].strip('#').strip()[:50]
        except Exception:
            description = "暂无描述"
    
    modules_data.append({
        "模块": module_name,
        "测试文件": len(test_files_in_module),
        "描述": description
    })

if modules_data:
    st.dataframe(modules_data, use_container_width=True, hide_index=True)
else:
    st.info("暂无测试模块")

st.markdown("---")
st.caption("💡 提示：使用左侧导航栏切换不同功能页面")
