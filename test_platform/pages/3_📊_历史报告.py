"""历史报告浏览页面"""
import streamlit as st
from pathlib import Path
from datetime import datetime

st.set_page_config(
    page_title="历史报告 - API自动化测试平台",
    page_icon="📊",
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

st.title("📊 历史报告")

project_root = Path(__file__).parent.parent.parent
reports_dir = project_root / "reports"

if not reports_dir.exists():
    st.error("❌ 报告目录不存在")
    st.stop()

# 获取所有报告文件（按时间倒序）
report_files = sorted(
    reports_dir.glob("benxi_report_*.html"),
    key=lambda x: x.stat().st_mtime,
    reverse=True
)

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
                badge = f"#{idx + 1}"
                st.markdown(f"**{badge} {report_file.name}**")
            
            with col2:
                st.text(f"📅 {file_time.strftime('%Y-%m-%d %H:%M:%S')}")
            
            with col3:
                st.text(f"💾 {file_size:.1f} KB")
            
            with col4:
                # 下载和查看按钮
                btn_col1, btn_col2 = st.columns(2)
                
                with btn_col1:
                    try:
                        with open(report_file, 'r', encoding='utf-8') as f:
                            report_content = f.read()
                        
                        st.download_button(
                            label="📥 下载",
                            data=report_content,
                            file_name=report_file.name,
                            mime="text/html",
                            key=f"download_{idx}"
                        )
                    except Exception as e:
                        st.error(f"读取失败")
                
                with btn_col2:
                    # 生成可访问的URL
                    file_url = report_file.absolute().as_uri()
                    st.markdown(f'<a href="{file_url}" target="_blank" style="display:inline-block;padding:0.25rem 0.75rem;background-color:#f0f2f6;border-radius:0.25rem;text-decoration:none;color:#262730;border:1px solid #e0e0e0;">🔗 查看</a>', unsafe_allow_html=True)
            
            st.markdown("---")
    
    # 报告管理
    st.subheader("🗑️ 报告管理")
    
    col1, col2 = st.columns(2)
    
    with col1:
        total_size = sum(f.stat().st_size for f in report_files) / 1024
        st.info(f"💾 报告总大小: {total_size:.1f} KB")
    
    with col2:
        # 计算可删除的报告数量
        if len(report_files) > 5:
            if st.button("🧹 清理旧报告（仅保留5个）", type="secondary", key="btn_cleanup"):
                to_keep = report_files[:5]
                to_delete = report_files[5:]
                
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
        
        # 删除所有报告
        if len(report_files) > 0:
            if st.button("🗑️ 删除所有报告", type="secondary", key="btn_delete_all"):
                deleted_count = 0
                for f in report_files:
                    try:
                        f.unlink()
                        deleted_count += 1
                    except Exception as e:
                        st.error(f"删除失败: {f.name} - {str(e)}")
                
                if deleted_count > 0:
                    st.success(f"✅ 已删除 {deleted_count} 个报告")
                    st.rerun()

st.markdown("---")
st.caption("💡 提示：点击'📥 下载'保存到本地，点击'🔗 查看'在新窗口打开")
