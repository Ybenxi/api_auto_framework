"""
语言切换辅助模块 v3
- 右上角固定位置的语言切换按钮
- 用 <a> 标签替代 <button>（<a> 的点击不被 Streamlit toolbar 层拦截）
- 通过 URL query param ?lang=en / ?lang=zh 保持语言状态
- 不使用 components.html（会占用页面内容区导致内容消失）
"""
import streamlit as st


def add_lang_switch() -> str:
    """
    在页面右上角注入固定定位的语言切换链接，返回当前语言代码（'zh' 或 'en'）。

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
    btn_label = "🌐 EN" if current == "zh" else "🌐 中"
    btn_title = "Switch to English" if current == "zh" else "切换为中文"
    target = "en" if current == "zh" else "zh"

    # 用 <a> 标签实现点击跳转（<a> 的点击不会被 Streamlit toolbar 拦截）
    # JS 用 location.href 而非 location.assign，兼容性更好
    st.markdown(f"""
<style>
#__lang_switch_anchor__ {{
    position: fixed;
    top: 0.6rem;
    right: 4.2rem;
    z-index: 999999;
    text-decoration: none;
    background: rgba(255, 255, 255, 0.92);
    border: 1.5px solid #d9d9d9;
    border-radius: 6px;
    padding: 4px 11px;
    font-size: 13px;
    font-weight: 600;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    color: #444 !important;
    cursor: pointer;
    box-shadow: 0 2px 6px rgba(0,0,0,0.12);
    transition: background 0.15s, color 0.15s, border-color 0.15s;
    line-height: 1.6;
    white-space: nowrap;
    display: inline-block;
    pointer-events: auto;
}}
#__lang_switch_anchor__:hover {{
    background: #f0f2ff;
    border-color: #2f54eb;
    color: #2f54eb !important;
    box-shadow: 0 3px 10px rgba(47,84,235,0.18);
}}
</style>
<a id="__lang_switch_anchor__"
   href="javascript:void(0)"
   title="{btn_title}"
   onclick="(function(){{
       var u=new URL(window.location.href);
       u.searchParams.set('lang','{target}');
       window.location.href=u.toString();
   }})()">
{btn_label}
</a>
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
