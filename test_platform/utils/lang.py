"""
语言切换辅助模块
在每个页面顶部调用 add_lang_switch() 即可在侧边栏底部显示中/英切换开关
"""
import streamlit as st


TRANSLATIONS = {
    # 首页
    "API自动化测试管理平台": {"en": "API Automation Test Platform"},
    "欢迎使用测试管理平台！": {"en": "Welcome to the Test Management Platform!"},
    "测试模块": {"en": "Test Modules"},
    "测试文件": {"en": "Test Files"},
    "历史报告": {"en": "Reports"},
    # 页面标题
    "📊 历史报告": {"en": "📊 Reports"},
    "⚙️ 系统设置": {"en": "⚙️ Settings"},
    "🧪 测试用例": {"en": "🧪 Test Cases"},
    "▶️ 运行测试": {"en": "▶️ Run Tests"},
}


def add_lang_switch():
    """
    在侧边栏底部添加中/英语言切换开关，并返回当前语言代码（'zh' 或 'en'）。
    在页面顶部调用：
        from utils.lang import add_lang_switch
        lang = add_lang_switch()
    """
    if "platform_lang" not in st.session_state:
        st.session_state.platform_lang = "zh"

    with st.sidebar:
        st.divider()
        cols = st.columns([1, 2, 1])
        with cols[0]:
            st.write("🌐")
        with cols[1]:
            is_en = st.toggle(
                "English",
                value=(st.session_state.platform_lang == "en"),
                key="_lang_toggle",
                help="Switch between Chinese / English"
            )
            if is_en:
                st.session_state.platform_lang = "en"
            else:
                st.session_state.platform_lang = "zh"

    return st.session_state.platform_lang


def t(zh_text: str) -> str:
    """
    翻译辅助函数：根据当前语言返回对应文字。
    lang = add_lang_switch() 后可直接用 t("中文")
    """
    lang = st.session_state.get("platform_lang", "zh")
    if lang == "en":
        return TRANSLATIONS.get(zh_text, {}).get("en", zh_text)
    return zh_text
