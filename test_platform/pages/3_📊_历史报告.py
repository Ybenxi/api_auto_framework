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


# ──────────────────────────────────────────────────────────────────
# PDF 摘要报告（管理层用）
# ──────────────────────────────────────────────────────────────────
st.subheader("📑 PDF 摘要报告（管理层）")

pdf_files = sorted(
    reports_dir.glob("summary_report_*.pdf"),
    key=lambda x: x.stat().st_mtime,
    reverse=True
)
pdf_latest = reports_dir / "final_summary.pdf"

if not pdf_files and not pdf_latest.exists():
    st.warning("⚠️ 暂无 PDF 摘要报告")
    st.info("💡 运行测试后会自动生成 PDF 摘要报告")
else:
    display_pdfs = pdf_files[:3]
    total_pdf = len(pdf_files)
    if total_pdf > 0:
        st.success(f"共找到 **{total_pdf}** 个 PDF 报告，显示最新 **{len(display_pdfs)}** 个")
    st.markdown("---")

    for idx, pdf_file in enumerate(display_pdfs):
        file_stat = pdf_file.stat()
        file_size = file_stat.st_size / 1024
        file_time = datetime.fromtimestamp(file_stat.st_mtime)

        with st.container():
            col1, col2, col3, col4 = st.columns([3, 2, 1, 2])
            with col1:
                st.markdown(f"**#{idx + 1} {pdf_file.name}**")
            with col2:
                st.text(f"📅 {file_time.strftime('%Y-%m-%d %H:%M')}")
            with col3:
                st.text(f"💾 {file_size:.0f} KB")
            with col4:
                try:
                    with open(pdf_file, "rb") as f:
                        pdf_bytes = f.read()
                    st.download_button(
                        label="📥 下载 PDF",
                        data=pdf_bytes,
                        file_name=pdf_file.name,
                        mime="application/pdf",
                        key=f"dl_pdf_{idx}",
                        use_container_width=True
                    )
                except Exception:
                    st.error("读取失败")
            st.markdown("---")

    # 固定最新 PDF 快速下载
    if pdf_latest.exists():
        pdf_stat = pdf_latest.stat()
        pdf_time = datetime.fromtimestamp(pdf_stat.st_mtime)
        st.info(f"📌 最新 PDF：final_summary.pdf（更新于 {pdf_time.strftime('%Y-%m-%d %H:%M')}）")
        try:
            with open(pdf_latest, "rb") as f:
                latest_bytes = f.read()
            st.download_button(
                label="⬇️ 下载最新 PDF 摘要报告",
                data=latest_bytes,
                file_name=f"api_test_summary_{pdf_time.strftime('%Y%m%d')}.pdf",
                mime="application/pdf",
                key="dl_pdf_latest",
                type="primary"
            )
        except Exception as e:
            st.error(f"读取失败: {e}")

st.markdown("---")

# ──────────────────────────────────────────────────────────────────
# HTML 报告
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
# Excel 报告（带时间戳，显示最新3个）
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
if report_files:
    st.subheader("🗑️ 报告管理")
    col1, col2, col3 = st.columns(3)
    with col1:
        total_size = sum(f.stat().st_size for f in report_files) / 1024
        st.info(f"💾 HTML 报告总大小: {total_size:.0f} KB（共 {len(report_files)} 个）")
    with col2:
        if len(report_files) > 5:
            if st.button("🧹 清理旧 HTML（保留最新5个）", type="secondary", key="btn_keep5"):
                to_delete = report_files[5:]
                deleted = 0
                for f in to_delete:
                    try:
                        f.unlink()
                        deleted += 1
                    except Exception as e:
                        st.error(f"删除失败: {f.name} - {e}")
                if deleted:
                    st.success(f"✅ 已删除 {deleted} 个旧报告")
                    st.rerun()
        else:
            st.write(" ")
    with col3:
        if st.button("🗑️ 删除全部 HTML 报告", type="secondary", key="btn_delete_all"):
            deleted = 0
            for f in report_files:
                try:
                    f.unlink()
                    deleted += 1
                except Exception as e:
                    st.error(f"删除失败: {f.name} - {e}")
            if deleted:
                st.success(f"✅ 已删除 {deleted} 个报告")
                st.rerun()

st.markdown("---")
st.caption(f"💡 报告通过 {REPORT_BASE_URL} 静态服务访问 | 如需修改地址，设置环境变量 REPORT_BASE_URL")
