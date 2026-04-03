"""运行测试页面"""
import streamlit as st
from pathlib import Path
import subprocess
import sys
import time
import json
import os
import re
import threading
import base64
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.auth import require_login, show_logout_button
from utils.i18n import t

st.set_page_config(page_title=t("run_page_title"), page_icon="▶️", layout="wide", initial_sidebar_state="expanded")
st.markdown("""
<style>
    footer {visibility:hidden;}
    .terminal-box {
        background-color:#0d1117; color:#e6edf3;
        font-family:'JetBrains Mono','Fira Code','Consolas',monospace;
        font-size:13px; line-height:1.6; padding:16px 18px;
        border-radius:8px; border:1px solid #30363d;
        white-space:pre-wrap; word-break:break-all;
        overflow-y:auto; max-height:600px;
    }
    .log-passed  { color:#3fb950; font-weight:bold; }
    .log-failed  { color:#f85149; font-weight:bold; }
    .log-error   { color:#ff7b72; font-weight:bold; }
    .log-warning { color:#d29922; }
    .log-skipped { color:#8b949e; }
    .log-line-passed { background-color:rgba(63,185,80,0.07); display:block; border-radius:3px; }
    .log-line-failed { background-color:rgba(248,81,73,0.10); display:block; border-radius:3px; }
    .log-summary { color:#58a6ff; font-weight:bold; }
    .log-normal  { color:#e6edf3; }
    .log-sep     { color:#30363d; }
</style>
""", unsafe_allow_html=True)

require_login()
show_logout_button()

st.title(t("run_title"))

project_root = Path(__file__).parent.parent.parent
test_cases_dir = project_root / "test_cases"
reports_dir = project_root / "reports"
reports_dir.mkdir(exist_ok=True)
RUN_LOG = reports_dir / "running.log"
RUN_STATUS = reports_dir / "run_status.json"
DIRTY_RECORDS = reports_dir / "dirty_data_records.json"


def read_run_status() -> dict:
    if RUN_STATUS.exists():
        try:
            return json.loads(RUN_STATUS.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def _load_dirty_records() -> list:
    if not DIRTY_RECORDS.exists():
        return []
    try:
        data = json.loads(DIRTY_RECORDS.read_text(encoding="utf-8"))
        if isinstance(data, list):
            return data
    except Exception:
        pass
    return []


def _save_dirty_records(records: list):
    DIRTY_RECORDS.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")


def _scan_dirty_data_stats() -> tuple[dict, int, str]:
    """
    复用清理逻辑 dry-run 统计脏数据数量。
    返回 (stats, total, err_msg)。
    """
    venv_python3 = project_root / ".venv" / "bin" / "python3"
    py = str(venv_python3) if venv_python3.exists() else "python3"
    script = f"""
import sys, json
sys.path.insert(0, {repr(str(project_root))})
from dao.db_manager import DBManager
from utils.data_cleanup import DataCleanup
from config.config import config

db_config = config.db_config
if db_config.get("host") == "localhost":
    print(json.dumps({{"error": "DB not configured (localhost)"}}))
    sys.exit(0)

db = DBManager(db_config)
cleaner = DataCleanup(db)
stats = cleaner.cleanup_all_test_data(dry_run=True)
total = sum(sum(s.values()) for s in stats.values())
print(json.dumps({{"stats": stats, "total": total}}))
"""
    try:
        result = subprocess.run(
            [py, "-c", script],
            capture_output=True,
            text=True,
            cwd=str(project_root),
            timeout=60,
        )
        if result.returncode != 0:
            return {}, 0, (result.stderr.strip() or result.stdout.strip() or "Unknown error")
        out = result.stdout.strip()
        if not out:
            return {}, 0, "No output from dirty-data scanner"
        data = json.loads(out)
        if "error" in data:
            return {}, 0, str(data["error"])
        stats = data.get("stats", {}) or {}
        total = int(data.get("total", 0) or 0)
        return stats, total, ""
    except Exception as e:
        return {}, 0, str(e)


def _flatten_stats(stats: dict) -> dict:
    flat = {}
    for module, module_stats in (stats or {}).items():
        if not isinstance(module_stats, dict):
            continue
        for table, count in module_stats.items():
            try:
                c = int(count or 0)
            except Exception:
                c = 0
            flat[(str(module), str(table))] = c
    return flat


def _calc_dirty_delta(before: dict, after: dict) -> list:
    b = _flatten_stats(before)
    a = _flatten_stats(after)
    items = []
    for key, after_count in a.items():
        diff = after_count - b.get(key, 0)
        if diff > 0:
            module, table = key
            items.append({"module": module, "table": table, "count": diff})
    items.sort(key=lambda x: (x["module"], x["table"]))
    return items


def _target_module_from_test_path(test_path: str) -> str:
    """
    从 pytest 目标路径提取模块名：
    - test_cases/contact/ -> contact
    - test_cases/contact/test_xxx.py -> contact
    - test_cases/ -> all
    """
    p = (test_path or "").strip()
    if p == "test_cases/" or p == "test_cases":
        return "all"
    m = re.match(r"^test_cases/([^/]+)/?.*$", p)
    return m.group(1) if m else "all"


def _filter_dirty_items_for_target(items: list, target_module: str) -> tuple[list, int]:
    """
    只保留与本次运行模块相关的脏数据，避免把并发/其他模块写入算进来。
    v2 方案的 stats 分组键为：money_movements / groups / contacts / counterparties / subs
    返回 (filtered_items, ignored_total)
    """
    if target_module == "all":
        return items, 0

    # 测试模块名 → v2 stats 分组键映射
    _module_to_groups = {
        "contact":           {"contacts"},
        "counterparty":      {"counterparties", "groups"},
        "sub_account":       {"subs"},
        "fbo_account":       {"subs"},
        "payment_deposit":   {"money_movements", "counterparties", "subs"},
        "card":              {"money_movements"},
        "card_opening":      {"money_movements"},
        "identity_security": {"contacts", "counterparties"},
    }
    allowed = _module_to_groups.get(
        target_module,
        {"money_movements", "groups", "contacts", "counterparties", "subs"}
    )

    filtered = [x for x in items if x.get("module") in allowed]
    filtered_total = sum(x.get("count", 0) for x in filtered)
    total = sum(x.get("count", 0) for x in items)
    ignored = max(0, total - filtered_total)
    return filtered, ignored


def _html_escape(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _colorize_line(raw: str) -> str:
    line = _html_escape(raw.rstrip("\n"))
    stripped = raw.strip()
    if not stripped or set(stripped) <= set("=-_"):
        return f'<span class="log-sep">{line}</span>'
    if re.search(r'\d+ (passed|failed|error)', stripped):
        line = re.sub(r'(\d+ passed)', r'<span class="log-passed">\1</span>', line)
        line = re.sub(r'(\d+ failed)', r'<span class="log-failed">\1</span>', line)
        line = re.sub(r'(\d+ error)', r'<span class="log-error">\1</span>', line)
        line = re.sub(r'(\d+ skipped)', r'<span class="log-skipped">\1</span>', line)
        return f'<span class="log-summary">{line}</span>'
    if " PASSED" in stripped:
        line = line.replace(" PASSED", ' <span class="log-passed">PASSED</span>')
        return f'<span class="log-line-passed">{line}</span>'
    if " FAILED" in stripped:
        line = line.replace(" FAILED", ' <span class="log-failed">FAILED</span>')
        return f'<span class="log-line-failed">{line}</span>'
    if stripped.startswith("ERROR") or "ERROR" in stripped[:20]:
        return f'<span class="log-error">{line}</span>'
    if "WARNING" in stripped or "WARN" in stripped:
        return f'<span class="log-warning">{line}</span>'
    if " SKIPPED" in stripped or stripped.startswith("SKIP"):
        return f'<span class="log-skipped">{line}</span>'
    return f'<span class="log-normal">{line}</span>'


def render_log_terminal(log_content: str, reverse: bool = True):
    lines = log_content.splitlines(keepends=True)
    if reverse:
        lines = list(reversed(lines))
    inner_html = "\n".join(_colorize_line(l) for l in lines)
    st.markdown(f'<div class="terminal-box">{inner_html}</div>', unsafe_allow_html=True)


def render_result(status: dict):
    state = status.get("state", "")
    start_time = status.get("start_time", "")
    cmd = status.get("cmd", "")
    if cmd:
        st.code(f"$ {cmd}", language="bash")

    if state == "running":
        elapsed = time.time() - status.get("start_ts", time.time())
        st.info(t("run_running_info", start=start_time, elapsed=f"{elapsed:.0f}"))
        log_content = RUN_LOG.read_text(encoding="utf-8", errors="replace") if RUN_LOG.exists() else ""
        if log_content:
            st.markdown(t("run_live_output"))
            render_log_terminal(log_content, reverse=True)
        else:
            st.caption(t("run_waiting"))

    elif state == "done":
        duration = status.get("duration", 0)
        if status.get("returncode", -1) == 0:
            st.success(t("run_done_ok", dur=f"{duration:.1f}", start=start_time))
        else:
            st.error(t("run_done_fail", dur=f"{duration:.1f}", start=start_time))
        passed = status.get("passed", 0)
        failed = status.get("failed", 0)
        skipped = status.get("skipped", 0)
        total = passed + failed + skipped
        if total > 0:
            st.markdown("---")
            st.subheader(t("run_stat_title"))
            c1, c2, c3, c4 = st.columns(4)
            c1.metric(t("run_stat_passed"), passed)
            c2.metric(t("run_stat_failed"), failed)
            c3.metric(t("run_stat_skipped"), skipped)
            c4.metric(t("run_stat_rate"), f"{(passed/total)*100:.1f}%")
        log_content = RUN_LOG.read_text(encoding="utf-8", errors="replace") if RUN_LOG.exists() else ""
        if log_content:
            with st.expander(t("run_full_output"), expanded=False):
                render_log_terminal(log_content, reverse=True)

    elif state == "error":
        st.error(t("run_error", msg=status.get("error", "")))


current_status = read_run_status()
is_running = current_status.get("state") == "running"

if is_running:
    st.markdown("---")
    st.subheader(t("run_status_title"))
    render_result(current_status)

# ── 配置区 ─────────────────────────────────────────────────────────
st.subheader(t("run_mode_title"))
run_mode = st.selectbox(
    "run_mode",
    [t("run_mode_module"), t("run_mode_file"), t("run_mode_all")],
    index=2,
    label_visibility="collapsed",
)
st.markdown("---")

col1, col2 = st.columns(2)

_MODULE_DISPLAY = {
    "user_sign_up":      "User Sign Up",
    "account_opening":   "Account Opening",
    "identity_security": "Identity Security",
    "tenant":            "Tenant",
    "profile_account":   "Profile Account",
    "contact":           "Contact",
    "financial_account": "Financial Account",
    "sub_account":       "Sub Account",
    "fbo_account":       "FBO Account",
    "open_banking":      "Open Banking",
    "payment_deposit":   "Payment & Deposit",
    "card":              "Card Issuance",
    "card_opening":      "Card Opening",
    "trading_order":     "Trading Order",
    "statement":         "Statement",
    "counterparty":      "Counterparty Management",
    "investment":        "Report & Analytics (Investment)",
    "account_summary":   "Report & Analytics (Account Summary)",
    "card_report":       "Report & Analytics (Card Report)",
    "client_list":       "Client List",
}

_MODULE_ORDER_RUN = [
    "user_sign_up", "account_opening", "identity_security", "tenant",
    "profile_account", "contact", "financial_account", "sub_account",
    "fbo_account", "open_banking", "payment_deposit",
    "card", "card_opening",
    "trading_order", "statement", "counterparty",
    "investment", "account_summary", "card_report", "client_list",
]


def _dn(f):
    return _MODULE_DISPLAY.get(f, f.replace("_", " ").title())


def _run_sort_key(f):
    try:
        return _MODULE_ORDER_RUN.index(f)
    except ValueError:
        return len(_MODULE_ORDER_RUN)

all_modules = [d for d in test_cases_dir.iterdir() if d.is_dir() and not d.name.startswith("__")]
modules_with_tests = sorted([m.name for m in all_modules if list(m.rglob("test_*.py"))], key=_run_sort_key)
display_to_folder_run = {_dn(m): m for m in modules_with_tests}
display_names_run = list(display_to_folder_run.keys())

with col1:
    if run_mode == t("run_mode_module"):
        if not modules_with_tests:
            st.error(t("run_no_modules"))
            st.stop()
        sel_disp = st.selectbox(t("run_select_module"), display_names_run)
        selected_module = display_to_folder_run[sel_disp]
        test_path = f"test_cases/{selected_module}/"
    elif run_mode == t("run_mode_file"):
        if not modules_with_tests:
            st.error(t("run_no_modules"))
            st.stop()
        sel_disp = st.selectbox(t("run_select_module"), display_names_run)
        selected_module = display_to_folder_run[sel_disp]
        module_path = test_cases_dir / selected_module
        test_files_rglob = sorted(module_path.rglob("test_*.py"))
        test_files = [str(f.relative_to(module_path)) for f in test_files_rglob]
        if test_files:
            selected_file = st.selectbox(t("run_select_file"), test_files)
            test_path = f"test_cases/{selected_module}/{selected_file}"
        else:
            st.warning(t("run_no_files"))
            st.stop()
    else:
        test_path = "test_cases/"
target_module = _target_module_from_test_path(test_path)

with col2:
    lang = st.session_state.get("lang", "zh")
    opt_choices = [t("run_opt_v"), t("run_opt_s"), t("run_opt_tb"), t("run_opt_x")]
    # 语言切换后 session_state 里缓存的旧语言选项无法匹配新选项，需要过滤
    _stored = st.session_state.get(f"pytest_opts_{lang}", [t("run_opt_v")])
    _valid_stored = [o for o in _stored if o in opt_choices]
    if not _valid_stored:
        _valid_stored = [t("run_opt_v")]
    pytest_options = st.multiselect(t("run_pytest_opts"), opt_choices,
                                    default=_valid_stored, key=f"pytest_opts_{lang}")
    actual_options = [opt.split()[0] for opt in pytest_options]

cmd_parts = ["pytest", test_path] + actual_options
cmd_display = " ".join(cmd_parts)
st.code(f"$ {cmd_display}", language="bash")

start_disabled = is_running
if st.button(t("run_start_btn"), type="primary", key="btn_start_run", disabled=start_disabled):
    _cred_file_check = project_root / "api_credentials.json"
    if _cred_file_check.exists():
        try:
            _cd = json.loads(_cred_file_check.read_text(encoding="utf-8"))
            _an = _cd.get("active_profile")
            _active_cred_obj = next((p for p in _cd.get("profiles", []) if p.get("name") == _an), None) if _an else None
            if _an:
                st.info(t("run_cred_info", name=_an))
            else:
                st.info(t("run_no_cred"))
        except Exception:
            _active_cred_obj = None

    # Show active environment — and warn if credential env doesn't match
    _env_cfg_check = project_root / "environment_config.json"
    if _env_cfg_check.exists():
        try:
            _ec = json.loads(_env_cfg_check.read_text(encoding="utf-8"))
            _ae = _ec.get("active_env")
            _ae_obj = next((e for e in _ec.get("environments", []) if e.get("name") == _ae), None)
            if _ae_obj:
                st.info(f"🌐 Environment: **{_ae}**  |  `{_ae_obj.get('base_url','')}` / core: `{_ae_obj.get('core','')}`")
            # Warn if the active credential is bound to a different environment
            if _ae and _active_cred_obj:
                cred_env = _active_cred_obj.get("env", "")
                if cred_env and cred_env != _ae:
                    st.warning(
                        f"⚠️ Credential **{_active_cred_obj.get('name','')}** is bound to `{cred_env}`, "
                        f"but the active environment is `{_ae}`. "
                        f"Consider switching to a credential for `{_ae}`."
                    )
        except Exception:
            pass

    RUN_LOG.write_text("", encoding="utf-8")
    now = datetime.now()
    dirty_before_stats, dirty_before_total, dirty_scan_err = _scan_dirty_data_stats()
    RUN_STATUS.write_text(json.dumps({
        "state": "running",
        "start_time": now.strftime("%Y-%m-%d %H:%M:%S"),
        "start_ts": time.time(),
        "cmd": cmd_display,
        "target_module": target_module,
        "dirty_before_stats": dirty_before_stats,
        "dirty_before_total": dirty_before_total,
        "dirty_scan_error": dirty_scan_err,
    }, ensure_ascii=False), encoding="utf-8")

    venv_python = project_root / ".venv" / "bin" / "python"
    full_cmd = [str(venv_python), "-m", "pytest"] + cmd_parts[1:] if venv_python.exists() else cmd_parts
    env = os.environ.copy()
    env["PYTHONPATH"] = str(project_root)

    _cred_file = project_root / "api_credentials.json"
    if _cred_file.exists():
        try:
            _cred_data = json.loads(_cred_file.read_text(encoding="utf-8"))
            _active = _cred_data.get("active_profile")
            if _active:
                _p = next((x for x in _cred_data.get("profiles", []) if x.get("name") == _active), None)
                if _p:
                    # 新模型：user_id / account_id / client_id / secret / core / encryption_key
                    user_id = _p.get("user_id", "")
                    account_id = _p.get("account_id", _p.get("tenant_id", ""))
                    client_id = _p.get("client_id", "")
                    secret = _p.get("secret", "")
                    core = _p.get("core", "")
                    encryption_key = _p.get("encryption_key", "")

                    basic_auth = _p.get("basic_auth", "")
                    if (not basic_auth) and client_id and secret:
                        basic_auth = base64.b64encode(f"{client_id}:{secret}".encode("utf-8")).decode("utf-8")

                    # 兼容现有 config/conftest 读取
                    env["USER_ID"] = user_id
                    env["TENANT_ID"] = account_id
                    env["BASIC_AUTH"] = basic_auth

                    # 新字段直传，供后续接口或工具直接使用
                    env["ACCOUNT_ID"] = account_id
                    env["CLIENT_ID"] = client_id
                    env["CLIENT_SECRET"] = secret
                    env["CORE"] = core
                    env["ENCRYPTION_KEY"] = encryption_key
                    env["ENV"] = _p.get("env", "DEV")
        except Exception:
            pass

    # ── Inject active environment (BASE_URL + CORE override) ─────────
    _env_cfg_file = project_root / "environment_config.json"
    if _env_cfg_file.exists():
        try:
            _env_cfg = json.loads(_env_cfg_file.read_text(encoding="utf-8"))
            _active_env_name = _env_cfg.get("active_env")
            _active_env = next(
                (e for e in _env_cfg.get("environments", []) if e.get("name") == _active_env_name),
                None,
            )
            if _active_env:
                env["BASE_URL"] = _active_env.get("base_url", "")
                env["CORE"]     = _active_env.get("core", "")  # overrides credential-level core
        except Exception:
            pass

    def run_pytest():
        start_ts = time.time()
        try:
            process = subprocess.Popen(full_cmd, cwd=str(project_root),
                                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                       text=True, env=env, bufsize=1)
            collected_output = []
            for line in process.stdout:
                collected_output.append(line)
                with open(RUN_LOG, "a", encoding="utf-8") as f:
                    f.write(line)
            process.wait()
            duration = time.time() - start_ts
            full_output = "".join(collected_output)
            passed  = int(m.group(1)) if (m := re.search(r'(\d+) passed',  full_output)) else 0
            failed  = int(m.group(1)) if (m := re.search(r'(\d+) failed',  full_output)) else 0
            skipped = int(m.group(1)) if (m := re.search(r'(\d+) skipped', full_output)) else 0
            prev = json.loads(RUN_STATUS.read_text(encoding="utf-8"))
            dirty_after_stats, dirty_after_total, dirty_scan_err2 = _scan_dirty_data_stats()
            raw_dirty_items = _calc_dirty_delta(prev.get("dirty_before_stats", {}), dirty_after_stats)
            target = prev.get("target_module", "all")
            dirty_items, ignored_total = _filter_dirty_items_for_target(raw_dirty_items, target)
            dirty_delta_total = sum(x.get("count", 0) for x in dirty_items)
            prev.update({"state": "done", "duration": round(duration, 1),
                         "returncode": process.returncode,
                         "passed": passed, "failed": failed, "skipped": skipped,
                         "dirty_after_stats": dirty_after_stats,
                         "dirty_after_total": dirty_after_total,
                         "dirty_raw_items": raw_dirty_items,
                         "dirty_items": dirty_items,
                         "dirty_delta_total": dirty_delta_total,
                         "dirty_ignored_total": ignored_total,
                         "dirty_scan_error": dirty_scan_err2 or prev.get("dirty_scan_error", "")})
            RUN_STATUS.write_text(json.dumps(prev, ensure_ascii=False), encoding="utf-8")

            if dirty_delta_total > 0:
                records = _load_dirty_records()
                run_target = cmd_display.replace("pytest ", "", 1).strip() if cmd_display.startswith("pytest ") else cmd_display
                ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                for item in dirty_items:
                    records.append({
                        "time": ts,
                        "target": run_target,
                        "module": item.get("module", ""),
                        "type": item.get("table", ""),
                        "count": int(item.get("count", 0) or 0),
                    })
                _save_dirty_records(records)
        except Exception as e:
            prev = json.loads(RUN_STATUS.read_text(encoding="utf-8")) if RUN_STATUS.exists() else {}
            prev.update({"state": "error", "error": str(e)})
            RUN_STATUS.write_text(json.dumps(prev, ensure_ascii=False), encoding="utf-8")

    threading.Thread(target=run_pytest, daemon=True).start()
    time.sleep(0.5)
    st.rerun()

st.markdown("---")

if current_status.get("state") == "done":
    with st.expander(t("run_last_result"), expanded=False):
        render_result(current_status)
    st.markdown("---")

st.subheader(t("run_dirty_title"))
st.caption(t("run_dirty_net_note"))
if current_status.get("state") == "done":
    if current_status.get("dirty_scan_error"):
        st.warning(t("run_dirty_scan_warn", msg=current_status.get("dirty_scan_error")))
    ignored_total = int(current_status.get("dirty_ignored_total", 0) or 0)
    if ignored_total > 0:
        st.warning(t("run_dirty_ignored", n=ignored_total))

dirty_records = list(reversed(_load_dirty_records()))

# ── 统计摘要：本次 + 历史总计 ──────────────────────────────────────
this_run_total = int(current_status.get("dirty_delta_total", 0) or 0) if current_status.get("state") == "done" else 0
history_total  = sum(int(r.get("count", 0) or 0) for r in dirty_records)
lang = st.session_state.get("lang", "en")
if lang == "en":
    st.markdown(
        f"> 🧹 This run generated &nbsp;**{this_run_total}**&nbsp; dirty records. &nbsp;&nbsp;"
        f"History total: &nbsp;**{history_total}**&nbsp; dirty records.",
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        f"> 🧹 本次运行共产生 &nbsp;**{this_run_total}**&nbsp; 条脏数据，&nbsp;&nbsp;"
        f"历史累计共产生 &nbsp;**{history_total}**&nbsp; 条脏数据。",
        unsafe_allow_html=True,
    )

if dirty_records:
    st.caption(t("run_dirty_hist_caption"))
    st.dataframe(
        [
            {
                t("run_dirty_col_time"): r.get("time", ""),
                t("run_dirty_col_target"): r.get("target", ""),
                t("run_dirty_col_module"): r.get("module", ""),
                t("run_dirty_col_type"): r.get("type", ""),
                t("run_dirty_col_count"): r.get("count", 0),
            }
            for r in dirty_records
        ],
        use_container_width=True,
        hide_index=True,
    )
else:
    st.caption(t("run_dirty_hist_empty"))

st.caption(t("run_tip"))

if is_running:
    time.sleep(2)
    st.rerun()
