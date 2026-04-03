"""历史报告浏览页面"""
import streamlit as st
from pathlib import Path
import sys
from datetime import datetime
import os

sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.auth import require_login, show_logout_button
from utils.i18n import t

st.set_page_config(page_title=t("report_page_title"), page_icon="📊", layout="wide", initial_sidebar_state="expanded")
st.markdown("<style>footer{visibility:hidden;}</style>", unsafe_allow_html=True)

require_login()
show_logout_button()

col_title, col_refresh = st.columns([8, 1])
with col_title:
    st.title(t("report_title"))
with col_refresh:
    st.write("")
    st.write("")
    if st.button(t("report_refresh"), key="btn_refresh_reports", use_container_width=True):
        st.rerun()

project_root = Path(__file__).parent.parent.parent
reports_dir = project_root / "reports"

if not reports_dir.exists():
    st.error(t("report_dir_missing"))
    st.stop()

REPORT_BASE_URL = os.environ.get("REPORT_BASE_URL", "http://localhost:8502")


def _safe_unlink(f):
    try:
        f.unlink()
        return True
    except Exception:
        return False


# ── HTML 报告 ──────────────────────────────────────────────────────
st.subheader(t("report_html_title"))
report_files = sorted(reports_dir.glob("benxi_report_*.html"),
                      key=lambda x: x.stat().st_mtime, reverse=True)

if not report_files:
    st.warning(t("report_no_html"))
    st.info(t("report_run_hint"))
else:
    display_files = report_files[:5]
    st.success(t("report_html_found", total=len(report_files), shown=len(display_files)))
    st.markdown("---")
    for idx, report_file in enumerate(display_files):
        stat = report_file.stat()
        file_time = datetime.fromtimestamp(stat.st_mtime)
        report_url = f"{REPORT_BASE_URL}/{report_file.name}"
        with st.container():
            c1, c2, c3, c4 = st.columns([3, 2, 1, 2])
            c1.markdown(f"**#{idx+1} {report_file.name}**")
            c2.text(f"📅 {file_time.strftime('%Y-%m-%d %H:%M')}")
            c3.text(f"💾 {stat.st_size/1024:.0f} KB")
            with c4:
                b1, b2 = st.columns(2)
                with b1:
                    try:
                        st.download_button(t("report_download"),
                                           data=report_file.read_text(encoding="utf-8"),
                                           file_name=report_file.name, mime="text/html",
                                           key=f"dl_html_{idx}")
                    except Exception:
                        st.error(t("report_read_fail"))
                with b2:
                    st.link_button(t("report_view"), url=report_url, use_container_width=True)
        st.markdown("---")

# ── PDF 报告 ───────────────────────────────────────────────────────
st.subheader(t("report_pdf_title"))
pdf_latest = reports_dir / "final_summary.pdf"
pdf_files = sorted(reports_dir.glob("summary_report_*.pdf"),
                   key=lambda x: x.stat().st_mtime, reverse=True)

if not pdf_latest.exists() and not pdf_files:
    st.warning(t("report_no_pdf"))
    st.info(t("report_pdf_hint"))
else:
    show_pdf = pdf_latest if pdf_latest.exists() else (pdf_files[0] if pdf_files else None)
    display_name = pdf_files[0].name if pdf_files else "final_summary.pdf"
    if show_pdf:
        stat = show_pdf.stat()
        pdf_time = datetime.fromtimestamp(stat.st_mtime)
        st.markdown("---")
        c1, c2, c3, c4 = st.columns([3, 2, 1, 2])
        c1.markdown(f"**{display_name}**")
        c2.text(f"📅 {pdf_time.strftime('%Y-%m-%d %H:%M')}")
        c3.text(f"💾 {stat.st_size/1024:.0f} KB")
        with c4:
            try:
                st.download_button(t("report_download_pdf"), data=show_pdf.read_bytes(),
                                   file_name=f"api_test_report_{pdf_time.strftime('%Y%m%d_%H%M')}.pdf",
                                   mime="application/pdf", key="dl_pdf_latest",
                                   use_container_width=True, type="primary")
            except Exception as e:
                st.error(f"{t('report_read_fail')}: {e}")
        st.markdown("---")

# ── Excel 报告 ─────────────────────────────────────────────────────
st.subheader(t("report_excel_title"))
excel_files = sorted(reports_dir.glob("test_cases_*.xlsx"),
                     key=lambda x: x.stat().st_mtime, reverse=True)

if not excel_files:
    st.warning(t("report_no_excel"))
    st.info(t("report_pdf_hint"))
else:
    display_excels = excel_files[:3]
    st.success(t("report_excel_found", total=len(excel_files), shown=len(display_excels)))
    st.markdown("---")
    for idx, excel_file in enumerate(display_excels):
        stat = excel_file.stat()
        file_time = datetime.fromtimestamp(stat.st_mtime)
        excel_url = f"{REPORT_BASE_URL}/{excel_file.name}"
        with st.container():
            ec1, ec2, ec3, ec4 = st.columns([3, 2, 1, 2])
            ec1.markdown(f"**#{idx+1} {excel_file.name}**")
            ec2.text(f"📅 {file_time.strftime('%Y-%m-%d %H:%M')}")
            ec3.text(f"💾 {stat.st_size/1024:.0f} KB")
            with ec4:
                b1, b2 = st.columns(2)
                with b1:
                    try:
                        st.download_button(t("report_download"), data=excel_file.read_bytes(),
                                           file_name=excel_file.name,
                                           mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                           key=f"dl_excel_{idx}")
                    except Exception:
                        st.error(t("report_read_fail"))
                with b2:
                    st.link_button(t("report_view"), url=excel_url, use_container_width=True)
        st.markdown("---")

# ── 报告管理 ───────────────────────────────────────────────────────
st.subheader(t("report_mgmt_title"))
all_report_files = (list(reports_dir.glob("benxi_report_*.html")) +
                    list(reports_dir.glob("summary_report_*.pdf")) +
                    list(reports_dir.glob("test_cases_*.xlsx")))
final_files = [reports_dir / "final_report.html", reports_dir / "final_summary.pdf"]

c1, c2, c3 = st.columns(3)
with c1:
    total_size = sum(f.stat().st_size for f in all_report_files if f.exists()) / 1024
    st.info(t("report_size_info", size=f"{total_size:.0f}", count=len(all_report_files)))
with c2:
    html_files = sorted(reports_dir.glob("benxi_report_*.html"),
                        key=lambda x: x.stat().st_mtime, reverse=True)
    if len(html_files) > 5:
        if st.button(t("report_clean_html"), type="secondary", key="btn_keep5"):
            deleted = sum(1 for f in html_files[5:] if _safe_unlink(f))
            if deleted:
                st.success(t("report_deleted_html", n=deleted))
                st.rerun()
    else:
        st.write("")
with c3:
    if st.button(t("report_delete_all"), type="secondary", key="btn_delete_all"):
        deleted = 0
        for f in all_report_files:
            try:
                f.unlink()
                deleted += 1
            except Exception as e:
                st.error(t("report_delete_fail", name=f.name, e=e))
        for f in final_files:
            try:
                if f.exists():
                    f.unlink()
                    deleted += 1
            except Exception:
                pass
        if deleted:
            st.success(t("report_deleted_all", n=deleted))
            st.rerun()

st.markdown("---")
st.caption(t("report_tip", url=REPORT_BASE_URL))
