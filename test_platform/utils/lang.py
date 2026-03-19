"""
语言切换辅助模块 v5（最终稳定版）
核心策略：
  1. 点击用 Streamlit 原生 st.button + st.rerun()，不走 JS URL 跳转（避免崩溃）
  2. 位置定位：在侧边栏顶部放置按钮（100% 兼容，不依赖 CSS hack）
     - 侧边栏任何页面都可见，不会被 Streamlit 层级遮挡
     - 放在侧边栏最顶部，视觉上显眼
"""
import streamlit as st


def add_lang_switch() -> str:
    """
    在侧边栏顶部添加语言切换按钮，返回当前语言代码（'zh' 或 'en'）。
    点击切换后页面会正常重渲染，不会崩溃。
    """
    # 读取 URL query param，优先于 session_state
    query_lang = st.query_params.get("lang", None)
    if query_lang in ("zh", "en"):
        st.session_state.platform_lang = query_lang
    elif "platform_lang" not in st.session_state:
        st.session_state.platform_lang = "zh"

    current = st.session_state.platform_lang
    btn_label = "🌐 EN" if current == "zh" else "🌐 中"
    btn_title = "Switch to English" if current == "zh" else "切换为中文"

    # 样式：把侧边栏顶部的按钮改为小巧的切换按钮样式
    st.markdown("""
<style>
/* 侧边栏语言切换按钮：紧凑小按钮样式 */
section[data-testid="stSidebar"] div[data-testid="stButton"]:first-of-type button {
    background: transparent !important;
    border: 1px solid rgba(49,51,63,0.2) !important;
    border-radius: 4px !important;
    font-size: 12px !important;
    font-weight: 600 !important;
    padding: 2px 8px !important;
    color: rgb(49,51,63) !important;
    min-height: 26px !important;
    height: 26px !important;
    width: auto !important;
    min-width: unset !important;
}
section[data-testid="stSidebar"] div[data-testid="stButton"]:first-of-type button:hover {
    background: rgba(47,84,235,0.08) !important;
    border-color: #2f54eb !important;
    color: #2f54eb !important;
}
</style>
""", unsafe_allow_html=True)

    # 侧边栏顶部放按钮
    with st.sidebar:
        col1, col2 = st.columns([1, 3])
        with col1:
            if st.button(btn_label, key="_lang_btn", help=btn_title, use_container_width=False):
                new_lang = "en" if current == "zh" else "zh"
                st.session_state.platform_lang = new_lang
                st.query_params["lang"] = new_lang
                st.rerun()
        with col2:
            st.caption("Language / 语言")

    return current


def t(zh_text: str, en_text: str = "") -> str:
    """翻译辅助函数"""
    lang = st.session_state.get("platform_lang", "zh")
    if lang == "en" and en_text:
        return en_text
    return zh_text
