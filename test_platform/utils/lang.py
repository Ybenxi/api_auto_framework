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

    # Step1: 把 components.html 渲染的 iframe 容器用 CSS 固定到右上角
    st.markdown("""
<style>
/* 把语言切换按钮的 iframe 容器固定到右上角 */
div[data-testid="stCustomComponentV1"]:has(iframe#lang-iframe) {
    position: fixed !important;
    top: 0.5rem !important;
    right: 4rem !important;
    width: 80px !important;
    height: 32px !important;
    z-index: 9999999 !important;
    overflow: visible !important;
    border: none !important;
    background: transparent !important;
}
</style>
""", unsafe_allow_html=True)

    # Step2: 用 components.html 渲染真正可点击的按钮（在 iframe 里，绕过 Streamlit 层级限制）
    import streamlit.components.v1 as components
    components.html(f"""
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
html, body {{ background: transparent; overflow: hidden; width: 100%; height: 100%; }}
#lang-btn {{
    display: inline-block;
    background: rgba(255,255,255,0.95);
    border: 1.5px solid #d9d9d9;
    border-radius: 6px;
    padding: 3px 10px;
    font-size: 13px;
    font-weight: 600;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    color: #444;
    cursor: pointer;
    box-shadow: 0 2px 6px rgba(0,0,0,0.15);
    white-space: nowrap;
    transition: all 0.15s;
    line-height: 1.6;
}}
#lang-btn:hover {{
    background: #f0f2ff;
    border-color: #2f54eb;
    color: #2f54eb;
    box-shadow: 0 3px 10px rgba(47,84,235,0.2);
}}
</style>
<button id="lang-btn" title="{btn_title}" onclick="switchLang()">🌐 {btn_label}</button>
<script>
function switchLang() {{
    try {{
        // Streamlit 页面运行在 iframe 里，需要通过 window.parent 操作父窗口 URL
        var url = new URL(window.parent.location.href);
        url.searchParams.set('lang', '{target}');
        window.parent.location.href = url.toString();
    }} catch(e) {{
        var url = new URL(window.location.href);
        url.searchParams.set('lang', '{target}');
        window.location.href = url.toString();
    }}
}}
// 用 JS 直接把父 iframe 容器固定到右上角（比 CSS :has() 兼容性更好）
(function positionFrame() {{
    try {{
        var frame = window.frameElement;
        if (!frame) return;
        // 找到 Streamlit 包裹这个 iframe 的最近 div 容器
        var container = frame.parentElement;
        while (container && container.tagName !== 'SECTION' && container.getAttribute('data-testid') !== 'stCustomComponentV1') {{
            container = container.parentElement;
        }}
        // 直接操作 iframe 本身
        frame.style.cssText = 'position:fixed!important;top:0.5rem!important;right:4rem!important;width:80px!important;height:32px!important;z-index:9999999!important;border:none!important;background:transparent!important;overflow:visible!important;';
        if (container && container !== document.body) {{
            container.style.cssText += ';position:fixed!important;top:0.5rem!important;right:4rem!important;width:80px!important;height:32px!important;z-index:9999999!important;';
        }}
    }} catch(e) {{ console.log('lang position err:', e); }}
}})();
</script>
""", height=32, scrolling=False)

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
