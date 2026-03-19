"""历史报告浏览页面"""
import streamlit as st
from pathlib import Path
from datetime import datetime
import os

st.set_page_config(
    page_title="历史报告 - API自动化测试平台",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

col_title, col_refresh = st.columns([8, 1])
with col_title:
    st.title("📊 历史报告")
with col_refresh:
    st.write("")
    st.write("")
    if st.button("🔄 刷新", key="btn_refresh_reports", use_container_width=True):
        st.rerun()

project_root = Path(__file__).parent.parent.parent
reports_dir = project_root / "reports"

if not reports_dir.exists():
    st.error("❌ 报告目录不存在")
    st.stop()

REPORT_BASE_URL = os.environ.get("REPORT_BASE_URL", "http://localhost:8502")


def _safe_unlink(f):
    try:
        f.unlink()
        return True
    except Exception:
        return False


# ──────────────────────────────────────────────────────────────────
# HTML 报告（最新5个）
# ──────────────────────────────────────────────────────────────────
st.subheader("📄 HTML 测试报告")

report_files = sorted(
    reports_dir.glob("benxi_report_*.html"),
    key=lambda x: x.stat().st_mtime,
    reverse=True
)

if not report_files:
    st.warning("⚠️ 暂无 HTML 测试报告")
    st.info("💡 运行测试后会自动生成报告")
else:
    display_files = report_files[:5]
    total_count = len(report_files)
    st.success(f"共找到 **{total_count}** 个测试报告，显示最新 **{len(display_files)}** 个")
    st.markdown("---")

    for idx, report_file in enumerate(display_files):
        file_stat = report_file.stat()
        file_size = file_stat.st_size / 1024
        file_time = datetime.fromtimestamp(file_stat.st_mtime)
        report_url = f"{REPORT_BASE_URL}/{report_file.name}"

        with st.container():
            col1, col2, col3, col4 = st.columns([3, 2, 1, 2])
            with col1:
                st.markdown(f"**#{idx + 1} {report_file.name}**")
            with col2:
                st.text(f"📅 {file_time.strftime('%Y-%m-%d %H:%M')}")
            with col3:
                st.text(f"💾 {file_size:.0f} KB")
            with col4:
                btn_col1, btn_col2 = st.columns(2)
                with btn_col1:
                    try:
                        with open(report_file, "r", encoding="utf-8") as f:
                            report_content = f.read()
                        st.download_button(
                            label="📥 下载",
                            data=report_content,
                            file_name=report_file.name,
                            mime="text/html",
                            key=f"dl_html_{idx}"
                        )
                    except Exception:
                        st.error("读取失败")
                with btn_col2:
                    st.link_button("🔗 查看", url=report_url, use_container_width=True)
            st.markdown("---")

# ──────────────────────────────────────────────────────────────────
# PDF 报告（最新1个）
# ──────────────────────────────────────────────────────────────────
st.subheader("📑 PDF 报告")

pdf_latest = reports_dir / "final_summary.pdf"
pdf_files = sorted(
    reports_dir.glob("summary_report_*.pdf"),
    key=lambda x: x.stat().st_mtime,
    reverse=True
)

if not pdf_latest.exists() and not pdf_files:
    st.warning("⚠️ 暂无 PDF 报告")
    st.info("💡 运行测试后会自动生成")
else:
    # 取最新的1个（优先用 final_summary.pdf）
    show_pdf = pdf_latest if pdf_latest.exists() else (pdf_files[0] if pdf_files else None)
    # 显示名用带时间戳的原始文件名（如果存在）
    display_name = pdf_files[0].name if pdf_files else "final_summary.pdf"

    if show_pdf:
        pdf_stat = show_pdf.stat()
        pdf_time = datetime.fromtimestamp(pdf_stat.st_mtime)
        pdf_size = pdf_stat.st_size / 1024
        st.markdown("---")

        col1, col2, col3, col4 = st.columns([3, 2, 1, 2])
        with col1:
            st.markdown(f"**{display_name}**")
        with col2:
            st.text(f"📅 {pdf_time.strftime('%Y-%m-%d %H:%M')}")
        with col3:
            st.text(f"💾 {pdf_size:.0f} KB")
        with col4:
            try:
                with open(show_pdf, "rb") as f:
                    pdf_bytes = f.read()
                out_name = f"api_test_report_{pdf_time.strftime('%Y%m%d_%H%M')}.pdf"
                st.download_button(
                    label="📥 下载 PDF",
                    data=pdf_bytes,
                    file_name=out_name,
                    mime="application/pdf",
                    key="dl_pdf_latest",
                    use_container_width=True,
                    type="primary"
                )
            except Exception as e:
                st.error(f"读取失败: {e}")
        st.markdown("---")

# ──────────────────────────────────────────────────────────────────
# Excel 报告（最新3个）
# ──────────────────────────────────────────────────────────────────
st.subheader("📊 Excel 测试用例清单")

excel_files = sorted(
    reports_dir.glob("test_cases_*.xlsx"),
    key=lambda x: x.stat().st_mtime,
    reverse=True
)

if not excel_files:
    st.warning("⚠️ 暂无 Excel 测试用例清单")
    st.info("💡 运行测试后会自动生成")
else:
    display_excels = excel_files[:3]
    st.success(f"共找到 **{len(excel_files)}** 个 Excel 清单，显示最新 **{len(display_excels)}** 个")
    st.markdown("---")

    for idx, excel_file in enumerate(display_excels):
        file_stat = excel_file.stat()
        file_time = datetime.fromtimestamp(file_stat.st_mtime)
        file_size = file_stat.st_size / 1024
        excel_url = f"{REPORT_BASE_URL}/{excel_file.name}"

        with st.container():
            ex_col1, ex_col2, ex_col3, ex_col4 = st.columns([3, 2, 1, 2])
            with ex_col1:
                st.markdown(f"**#{idx + 1} {excel_file.name}**")
            with ex_col2:
                st.text(f"📅 {file_time.strftime('%Y-%m-%d %H:%M')}")
            with ex_col3:
                st.text(f"💾 {file_size:.0f} KB")
            with ex_col4:
                btn_col1, btn_col2 = st.columns(2)
                with btn_col1:
                    try:
                        with open(excel_file, "rb") as f:
                            excel_content = f.read()
                        st.download_button(
                            label="📥 下载",
                            data=excel_content,
                            file_name=excel_file.name,
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            key=f"dl_excel_{idx}"
                        )
                    except Exception:
                        st.error("读取失败")
                with btn_col2:
                    st.link_button("🔗 查看", url=excel_url, use_container_width=True)
            st.markdown("---")

# ──────────────────────────────────────────────────────────────────
# 报告管理
# ──────────────────────────────────────────────────────────────────
st.subheader("🗑️ 报告管理")

all_report_files = (
    list(reports_dir.glob("benxi_report_*.html")) +
    list(reports_dir.glob("summary_report_*.pdf")) +
    list(reports_dir.glob("test_cases_*.xlsx"))
)
final_files = [reports_dir / "final_report.html",
               reports_dir / "final_summary.pdf"]

col1, col2, col3 = st.columns(3)

with col1:
    total_size = sum(f.stat().st_size for f in all_report_files if f.exists()) / 1024
    total_count_all = len(all_report_files)
    st.info(f"💾 本地报告总大小: {total_size:.0f} KB（HTML/PDF/Excel 共 {total_count_all} 个）")

with col2:
    html_files = sorted(reports_dir.glob("benxi_report_*.html"),
                        key=lambda x: x.stat().st_mtime, reverse=True)
    if len(html_files) > 5:
        if st.button("🧹 清理旧 HTML（保留最新5个）", type="secondary", key="btn_keep5"):
            to_delete = html_files[5:]
            deleted = sum(1 for f in to_delete if _safe_unlink(f))
            if deleted:
                st.success(f"✅ 已删除 {deleted} 个旧 HTML 报告")
                st.rerun()
    else:
        st.write(" ")

with col3:
    if st.button("🗑️ 删除全部报告（HTML + Excel + PDF）", type="secondary", key="btn_delete_all"):
        deleted = 0
        for f in all_report_files:
            try:
                f.unlink()
                deleted += 1
            except Exception as e:
                st.error(f"删除失败: {f.name} - {e}")
        # 也删除 final_* 固定文件
        for f in final_files:
            try:
                if f.exists():
                    f.unlink()
                    deleted += 1
            except Exception:
                pass
        if deleted:
            st.success(f"✅ 已删除 {deleted} 个报告文件")
            st.rerun()

st.markdown("---")
st.caption(f"💡 报告通过 {REPORT_BASE_URL} 静态服务访问 | 如需修改地址，设置环境变量 REPORT_BASE_URL")
