"""
共享认证模块
所有页面调用 require_login() 来拦截未登录用户
"""
import streamlit as st
import streamlit.components.v1 as components
import yaml
import bcrypt
import hmac
import hashlib
from pathlib import Path

_PROJECT_ROOT = Path(__file__).parent.parent.parent
_AUTH_CONFIG_PATH = _PROJECT_ROOT / "auth_config.yaml"


def _load_auth_config() -> dict:
    if not _AUTH_CONFIG_PATH.exists():
        return {}
    with open(_AUTH_CONFIG_PATH, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _verify_password(username: str, password: str) -> tuple[bool, str]:
    """验证用户名密码，返回 (是否成功, 显示名)"""
    cfg = _load_auth_config()
    users = cfg.get("credentials", {}).get("usernames", {})
    user = users.get(username)
    if not user:
        return False, ""
    hashed = user.get("password", "")
    try:
        ok = bcrypt.checkpw(password.encode(), hashed.encode())
    except Exception:
        ok = False
    return ok, user.get("name", username) if ok else ""


def _auth_secret() -> str:
    cfg = _load_auth_config()
    cookie_cfg = cfg.get("cookie", {}) if isinstance(cfg, dict) else {}
    return str(cookie_cfg.get("key") or "api_auto_framework_auth_secret_v1")


def _make_auth_sig(username: str) -> str:
    return hmac.new(_auth_secret().encode("utf-8"), username.encode("utf-8"), hashlib.sha256).hexdigest()


def _restore_auth_from_query() -> bool:
    """在 session 丢失时，尝试从 query 参数恢复登录态。"""
    q_user = st.query_params.get("auth_user")
    q_sig = st.query_params.get("auth_sig")
    if not q_user or not q_sig:
        return False
    if not hmac.compare_digest(str(q_sig), _make_auth_sig(str(q_user))):
        return False

    cfg = _load_auth_config()
    users = cfg.get("credentials", {}).get("usernames", {})
    user = users.get(str(q_user))
    if not user:
        return False

    st.session_state["authenticated"] = True
    st.session_state["username"] = str(q_user)
    st.session_state["name"] = user.get("name", str(q_user))
    return True


def require_login():
    """
    检查登录状态，未登录则显示登录表单并阻断页面渲染。
    """
    if st.session_state.get("authenticated"):
        return

    if _restore_auth_from_query():
        return

    _show_login_page()
    st.stop()


def _show_login_page():
    """Render custom login page in English only."""

    st.markdown("""
    <style>
        .stApp { background: #ffffff; }
        [data-testid="stSidebar"] { display: none !important; }
        [data-testid="collapsedControl"] { display: none !important; }
        header[data-testid="stHeader"] { display: none !important; }
        footer { display: none !important; }
        #MainMenu { display: none !important; }
        .block-container {
            max-width: 420px !important;
            padding-top: 80px !important;
            padding-bottom: 0 !important;
            margin: 0 auto !important;
        }
    </style>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style="text-align:center; margin-bottom:32px;">
        <div style="font-size:2.5rem; margin-bottom:12px;">🧪</div>
        <div style="font-size:1.5rem; font-weight:700; color:#1D2129; margin-bottom:6px;">
            API Test Platform
        </div>
        <div style="font-size:0.875rem; color:#86909C;">
            Sign in to continue
        </div>
    </div>
    """, unsafe_allow_html=True)

    with st.form("login_form"):
        username = st.text_input("Username", placeholder="Enter username")
        password = st.text_input("Password", type="password", placeholder="Enter password")
        submitted = st.form_submit_button("Sign In", use_container_width=True, type="primary")

    if submitted:
        if not username or not password:
            st.error("Username and password are required")
        else:
            ok, display_name = _verify_password(username, password)
            if ok:
                st.session_state["authenticated"] = True
                st.session_state["username"] = username
                st.session_state["name"] = display_name
                st.query_params["auth_user"] = username
                st.query_params["auth_sig"] = _make_auth_sig(username)
                st.session_state["lang"] = "en"
                st.query_params["lang"] = "en"
                st.rerun()
            else:
                st.error("❌ Incorrect username or password")


def show_logout_button():
    """注入右上角固定顶栏：翻译按钮 + 用户名 + 退出按钮"""
    # 初始化语言：优先使用 URL 上的 lang，其次 session_state
    query_lang = st.query_params.get("lang")
    if query_lang in ("zh", "en"):
        st.session_state["lang"] = query_lang
    elif st.session_state.get("lang") not in ("zh", "en"):
        st.session_state["lang"] = "en"
        st.query_params["lang"] = "en"

    # ── 处理 logout ────────────────────────────────────────────────
    if st.query_params.get("logout") == "1":
        for key in ["authenticated", "name", "username", "lang"]:
            st.session_state.pop(key, None)
        st.query_params.clear()
        st.rerun()

    # ── 处理语言切换（触发 Python rerun，让所有 t() 重新渲染）────────
    if st.query_params.get("lang_toggle") == "1":
        current = st.session_state.get("lang", "zh")
        new_lang = "en" if current == "zh" else "zh"
        st.session_state["lang"] = new_lang
        st.query_params["lang"] = new_lang
        if "lang_toggle" in st.query_params:
            del st.query_params["lang_toggle"]
        st.rerun()

    # 已登录时，确保 query 参数始终携带可恢复登录态（防止切换语言/切页后 session 丢失）
    if st.session_state.get("authenticated"):
        username = st.session_state.get("username", "")
        if username:
            expected_sig = _make_auth_sig(username)
            if st.query_params.get("auth_user") != username:
                st.query_params["auth_user"] = username
            if st.query_params.get("auth_sig") != expected_sig:
                st.query_params["auth_sig"] = expected_sig

    name = st.session_state.get("name", "User")
    lang = st.session_state.get("lang", "zh")
    btn_title = "Switch Language / 切换语言"

    # ── 通过 iframe → window.parent 注入 position:fixed 顶栏 ────────
    components.html(f"""
    <script>
    (function() {{
        var doc = window.parent.document;
        var win = window.parent;
        var currentLang = '{lang}';

        // ── 侧边栏导航翻译（仅作用于 sidebar nav，避免污染正文）───────────
        var sidebarDict = {{
            '首页': 'Home',
            '测试用例': 'Test Cases',
            '运行测试': 'Run Tests',
            '历史报告': 'Reports',
            '系统设置': 'Settings',
            '配置管理': 'Config',
        }};

        function applySidebarLang() {{
            var nav = doc.querySelector('[data-testid="stSidebarNav"]');
            if (!nav) return;
            var nodes = nav.querySelectorAll('a span, a div, a p');
            for (var i = 0; i < nodes.length; i++) {{
                var text = (nodes[i].textContent || '').trim();
                if (!text) continue;
                if (currentLang === 'en' && sidebarDict[text]) {{
                    nodes[i].textContent = sidebarDict[text];
                }}
                if (currentLang === 'zh') {{
                    for (var zh in sidebarDict) {{
                        if (sidebarDict[zh] === text) {{
                            nodes[i].textContent = zh;
                            break;
                        }}
                    }}
                }}
            }}
        }}

        // ── 清除旧版本遗留的 JS 翻译（MutationObserver + sessionStorage）─
        // 旧版本用 sessionStorage.st_lang 控制 DOM 替换翻译，会造成中英混杂
        if (win._stTranslateObs) {{
            try {{ win._stTranslateObs.disconnect(); }} catch(e) {{}}
            win._stTranslateObs = null;
        }}
        if (win._stSidebarLangObs) {{
            try {{ win._stSidebarLangObs.disconnect(); }} catch(e) {{}}
            win._stSidebarLangObs = null;
        }}
        // 清掉旧版本的 sessionStorage 标记，防止旧 Observer 在热重载后复活
        try {{ sessionStorage.removeItem('st_lang'); }} catch(e) {{}}

        var old = doc.getElementById('st-topbar-user');
        if (old) old.remove();

        var bar = doc.createElement('div');
        bar.id = 'st-topbar-user';
        bar.style.cssText = 'position:fixed;top:12px;right:16px;z-index:9999999;display:flex;align-items:center;gap:8px;background:rgba(255,255,255,0.93);padding:4px 10px 4px 8px;border-radius:20px;box-shadow:0 1px 6px rgba(0,0,0,0.10);backdrop-filter:blur(4px);';

        // ── 翻译按钮（点击后导航至 ?lang_toggle=1，触发 Python rerun）─
        var langBtn = doc.createElement('a');
        var params = new URLSearchParams(win.location.search || '');
        params.set('lang_toggle', '1');
        langBtn.href = '?' + params.toString();
        langBtn.title = '{btn_title}';
        langBtn.innerHTML = '<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#4E5969" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 12h18"/><path d="M12 3a15 15 0 0 1 0 18"/><path d="M12 3a15 15 0 0 0 0 18"/><circle cx="12" cy="12" r="9"/></svg>';
        langBtn.style.cssText = 'width:26px;height:26px;border-radius:50%;border:1.5px solid #C9CDD4;background:#fff;cursor:pointer;text-decoration:none;display:flex;align-items:center;justify-content:center;';
        langBtn.onmouseover = function() {{ this.style.borderColor='#1634A4'; this.style.color='#1634A4'; }};
        langBtn.onmouseout  = function() {{ this.style.borderColor='#C9CDD4'; this.style.color='#4E5969'; }};

        // ── 用户名 ──────────────────────────────────────────────────
        var nameEl = doc.createElement('span');
        nameEl.style.cssText = 'font-size:13px;color:#4E5969;font-weight:600;white-space:nowrap;';
        nameEl.textContent = '👤 {name}';

        // ── 退出按钮（电源图标圆圈）────────────────────────────────
        var logoutBtn = doc.createElement('a');
        logoutBtn.href = '?logout=1';
        logoutBtn.title = 'Sign Out';
        logoutBtn.style.cssText = 'width:26px;height:26px;border-radius:50%;border:1.5px solid #C9CDD4;background:#fff;display:flex;align-items:center;justify-content:center;text-decoration:none;cursor:pointer;flex-shrink:0;';
        logoutBtn.innerHTML = '<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#86909C" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3v9"/><path d="M18.36 6.64A9 9 0 1 1 5.64 6.64"/></svg>';
        logoutBtn.onmouseover = function() {{ this.style.borderColor='#f83939'; this.style.background='#fff1f0'; this.querySelector('svg').style.stroke='#f83939'; }};
        logoutBtn.onmouseout  = function() {{ this.style.borderColor='#C9CDD4'; this.style.background='#fff'; this.querySelector('svg').style.stroke='#86909C'; }};

        bar.appendChild(langBtn);
        bar.appendChild(nameEl);
        bar.appendChild(logoutBtn);
        doc.body.appendChild(bar);

        // 初始化并监听侧边栏导航（切页后也能保持正确语言）
        applySidebarLang();
        win._stSidebarLangObs = new MutationObserver(function() {{
            applySidebarLang();
        }});
        win._stSidebarLangObs.observe(doc.body, {{ childList: true, subtree: true }});
    }})();
    </script>
    """, height=0)
