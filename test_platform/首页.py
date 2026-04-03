"""API自动化测试管理平台 - 总览页面"""
import streamlit as st
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))
from utils.auth import require_login, show_logout_button
from utils.i18n import t

st.set_page_config(
    page_title=t("home_page_title"),
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={'About': "API Test Management Platform v1.1"},
)

st.markdown("""
<style>
    .main-header { font-size:2.5rem; font-weight:700; color:#1f77b4; margin-bottom:1rem; }
    .metric-card { background-color:#f0f2f6; padding:1rem; border-radius:.5rem; border-left:4px solid #1f77b4; }
    footer { visibility: hidden; }
    [data-testid="stSidebar"] { min-width: 250px; }
</style>
""", unsafe_allow_html=True)

require_login()
show_logout_button()

project_root = Path(__file__).parent.parent
test_cases_dir = project_root / "test_cases"

st.markdown(f'<div class="main-header">{t("home_header")}</div>', unsafe_allow_html=True)

st.markdown(f"""
{t("home_welcome")}

- {t("home_feat1")}
- {t("home_feat2")}
- {t("home_feat3")}
- {t("home_feat4")}

---
""")

col1, col2, col3, col4 = st.columns(4)
modules = [d for d in test_cases_dir.iterdir() if d.is_dir() and not d.name.startswith('__')]
test_files = list(test_cases_dir.rglob("test_*.py"))
reports_dir = project_root / "reports"
reports = list(reports_dir.glob("benxi_report_*.html")) if reports_dir.exists() else []

unit = t("home_metric_unit")
with col1:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric(t("home_metric_modules"), len(modules))
    st.markdown('</div>', unsafe_allow_html=True)
with col2:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric(t("home_metric_files"), len(test_files))
    st.markdown('</div>', unsafe_allow_html=True)
with col3:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric(t("home_metric_reports"), len(reports))
    st.markdown('</div>', unsafe_allow_html=True)
with col4:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric(t("home_metric_version"), "v3.0")
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")
st.subheader(t("home_quick_title"))

qc1, qc2, qc3 = st.columns(3)
with qc1:
    if st.button(t("home_btn_cases"), key="btn_test_cases"):
        st.switch_page("pages/1_🧪_Test_Cases.py")
with qc2:
    if st.button(t("home_btn_run"), key="btn_run_test"):
        st.switch_page("pages/2_▶️_运行测试.py")
with qc3:
    if st.button(t("home_btn_reports"), key="btn_reports"):
        st.switch_page("pages/3_📊_历史报告.py")

st.markdown("---")
st.subheader(t("home_module_title"))

modules_data = []
lang = st.session_state.get("lang", "zh")
for module_dir in sorted(modules, key=lambda x: x.name):
    if not list(module_dir.glob("test_*.py")):
        continue
    readme_file = module_dir / "README.md"
    description = t("home_no_desc")
    if readme_file.exists():
        try:
            with open(readme_file, encoding="utf-8") as f:
                lines = f.readlines()
            if lines:
                raw = lines[0].strip("#").strip()[:60]
                if lang == "en" and any('\u4e00' <= c <= '\u9fff' for c in raw):
                    description = t("home_no_desc")
                else:
                    description = raw
        except Exception:
            pass
    modules_data.append({
        t("home_col_module"): module_dir.name,
        t("home_col_files"): len(list(module_dir.glob("test_*.py"))),
        t("home_col_desc"): description,
    })

if modules_data:
    st.dataframe(modules_data, use_container_width=True, hide_index=True)
else:
    st.info(t("home_no_modules"))

st.markdown("---")
st.caption(t("home_tip"))
