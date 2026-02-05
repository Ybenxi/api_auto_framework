"""历史报告浏览页面"""
import streamlit as st
from pathlib import Path
from datetime import datetime
import base64

st.set_page_config(page_title="历史报告", page_icon="📊", layout="wide")

# 隐藏顶部菜单
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

st.title("📊 历史报告")

project_root = Path(__file__).parent.parent.parent
reports_dir = project_root / "reports"

if not reports_dir.exists():
    st.error("❌ 报告目录不存在")
    st.stop()

# 获取所有报告文件
report_files = sorted(
    reports_dir.glob("benxi_report_*.html"),
    key=lambda x: x.stat().st_mtime,
    reverse=True
)

# 加上final_report.html
final_report = reports_dir / "final_report.html"
if final_report.exists():
    report_files.insert(0, final_report)

if not report_files:
    st.warning("⚠️ 暂无测试报告")
    st.info("💡 运行测试后会自动生成报告")
else:
    st.success(f"共找到 **{len(report_files)}** 个测试报告")
    
    st.markdown("---")
    
    # 报告列表
    for idx, report_file in enumerate(report_files):
        file_stat = report_file.stat()
        file_size = file_stat.st_size / 1024  # KB
        file_time = datetime.fromtimestamp(file_stat.st_mtime)
        
        with st.container():
            col1, col2, col3, col4 = st.columns([3, 2, 2, 2])
            
            with col1:
                is_final = report_file.name == "final_report.html"
                badge = "🌟 最新" if is_final else f"#{idx}"
                st.markdown(f"**{badge} {report_file.name}**")
            
            with col2:
                st.text(f"📅 {file_time.strftime('%Y-%m-%d %H:%M:%S')}")
            
            with col3:
                st.text(f"💾 {file_size:.1f} KB")
            
            with col4:
                # 使用下载按钮（更可靠）
                try:
                    with open(report_file, 'r', encoding='utf-8') as f:
                        report_content = f.read()
                    
                    st.download_button(
                        label="📥 下载报告",
                        data=report_content,
                        file_name=report_file.name,
                        mime="text/html",
                        key=f"download_{idx}"
                    )
                except Exception as e:
                    st.error(f"读取失败: {str(e)}")
            
            st.markdown("---")
    
    # 报告管理
    st.subheader("🗑️ 报告管理")
    
    col1, col2 = st.columns(2)
    
    with col1:
        total_size = sum(f.stat().st_size for f in report_files) / 1024
        st.info(f"💾 报告总大小: {total_size:.1f} KB")
    
    with col2:
        # 计算可删除的报告数量（排除final_report.html）
        deletable_reports = [f for f in report_files if f.name != "final_report.html"]
        if len(deletable_reports) > 5:
            if st.button("🧹 清理旧报告（仅保留5个）", type="secondary", key="btn_cleanup"):
                # 排除final_report.html
                to_keep = deletable_reports[:5]
                to_delete = deletable_reports[5:]
                
                # 删除旧报告
                deleted_count = 0
                for f in to_delete:
                    try:
                        f.unlink()
                        deleted_count += 1
                    except Exception as e:
                        st.error(f"删除失败: {f.name} - {str(e)}")
                
                if deleted_count > 0:
                    st.success(f"✅ 已删除 {deleted_count} 个旧报告")
                    st.rerun()

st.markdown("---")

# 查看报告功能
if report_files:
    st.subheader("👀 查看报告")
    
    selected_report_name = st.selectbox(
        "选择要查看的报告",
        [f.name for f in report_files],
        key="select_view_report"
    )
    
    if st.button("📖 在此查看", key="btn_view_inline"):
        selected_report_file = next(f for f in report_files if f.name == selected_report_name)
        
        try:
            with open(selected_report_file, 'r', encoding='utf-8') as f:
                report_html = f.read()
            
            # 使用iframe内嵌显示
            st.components.v1.html(report_html, height=800, scrolling=True)
            
        except Exception as e:
            st.error(f"❌ 读取报告失败: {str(e)}")

st.markdown("---")
st.caption("💡 提示：点击'下载报告'按钮保存到本地，或点击'在此查看'直接浏览")
