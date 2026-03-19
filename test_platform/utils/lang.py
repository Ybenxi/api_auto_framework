"""
语言切换辅助模块 v2
- 右上角固定位置的语言切换按钮（CSS fixed + HTML button）
- 通过 URL query param ?lang=en / ?lang=zh 保持语言状态
- 页面刷新和跳转后语言不丢失
"""
import streamlit as st
from pathlib import Path


def add_lang_switch() -> str:
    """
    在页面右上角注入固定定位的语言切换按钮，返回当前语言代码（'zh' 或 'en'）。

    用法（在每个页面 set_page_config 之后立即调用）：
        from utils.lang import add_lang_switch
        lang = add_lang_switch()
    """
    # 读取 URL query param，优先于 session_state
    query_lang = st.query_params.get("lang", None)
    if query_lang in ("zh", "en"):
        st.session_state.platform_lang = query_lang
    elif "platform_lang" not in st.session_state:
        st.session_state.platform_lang = "zh"

    current = st.session_state.platform_lang
    # 点击按钮后切换到的目标语言
    target = "en" if current == "zh" else "zh"
    btn_label = "EN" if current == "zh" else "中"
    btn_title = "Switch to English" if current == "zh" else "切换为中文"

    # 注入固定定位按钮 + 点击时修改 URL query param 并刷新
    st.markdown(f"""
<style>
#lang-switch-btn {{
    position: fixed;
    top: 0.55rem;
    right: 5.5rem;          /* 避开 Streamlit 自身右上角的菜单图标 */
    z-index: 999999;
    background: #fff;
    border: 1.5px solid #d9d9d9;
    border-radius: 6px;
    padding: 4px 12px;
    font-size: 13px;
    font-weight: 600;
    color: #444;
    cursor: pointer;
    box-shadow: 0 2px 6px rgba(0,0,0,0.12);
    transition: all 0.2s;
    line-height: 1.6;
}}
#lang-switch-btn:hover {{
    background: #f0f2ff;
    border-color: #2f54eb;
    color: #2f54eb;
    box-shadow: 0 3px 10px rgba(47,84,235,0.18);
}}
</style>
<button id="lang-switch-btn"
    title="{btn_title}"
    onclick="
        const url = new URL(window.location.href);
        url.searchParams.set('lang', '{target}');
        window.location.href = url.toString();
    ">
    🌐 {btn_label}
</button>
""", unsafe_allow_html=True)

    return current


def t(zh_text: str, en_text: str = "") -> str:
    """
    翻译辅助函数：根据当前语言返回对应文字。
    示例：st.title(t("测试平台", "Test Platform"))
    """
    lang = st.session_state.get("platform_lang", "zh")
    if lang == "en" and en_text:
        return en_text
    return zh_text
