"""配置管理页面 - API 凭据管理 & 邮箱白名单 & 测试数据"""
import streamlit as st
import json
import subprocess
import sys
import os
import base64
import binascii
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.auth import require_login, show_logout_button
from utils.i18n import t

st.set_page_config(page_title=t("config_page_title"), page_icon="🔧", layout="wide", initial_sidebar_state="expanded")
st.markdown("<style>footer{visibility:hidden;}</style>", unsafe_allow_html=True)

require_login()
show_logout_button()

project_root = Path(__file__).parent.parent.parent
_CRED_FILE      = project_root / "api_credentials.json"
_EMAIL_FILE     = project_root / "email_config.json"
_TESTDATA_FILE  = project_root / "test_data_config.json"


def _load_creds() -> dict:
    if _CRED_FILE.exists():
        try:
            return json.loads(_CRED_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"profiles": [], "active_profile": None}


def _save_creds(data: dict):
    _CRED_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def _load_emails() -> list:
    if _EMAIL_FILE.exists():
        try:
            return json.loads(_EMAIL_FILE.read_text(encoding="utf-8")).get("recipients", [])
        except Exception:
            pass
    return []


def _save_emails(recipients: list):
    _EMAIL_FILE.write_text(json.dumps({"recipients": recipients}, indent=2, ensure_ascii=False), encoding="utf-8")


def _load_testdata() -> dict:
    if _TESTDATA_FILE.exists():
        try:
            return json.loads(_TESTDATA_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"environments": {}}


def _save_testdata(data: dict):
    _TESTDATA_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


_ENV_CFG_FILE = project_root / "environment_config.json"


def _load_envs() -> dict:
    if _ENV_CFG_FILE.exists():
        try:
            return json.loads(_ENV_CFG_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"environments": [], "active_env": None}


def _save_envs(data: dict):
    _ENV_CFG_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def _get_env_names() -> list[str]:
    """返回所有已配置的环境名称列表；若未配置则返回默认值。"""
    try:
        if _ENV_CFG_FILE.exists():
            data = json.loads(_ENV_CFG_FILE.read_text(encoding="utf-8"))
            names = [e.get("name", "") for e in data.get("environments", []) if e.get("name")]
            if names:
                return names
    except Exception:
        pass
    return ["DEV ACTC", "UAT ACTC", "UAT FTA"]


st.title(t("config_title"))
tab_ops, tab_cred, tab_email, tab_testdata, tab_env = st.tabs([
    "⚙️ Operations",
    t("config_tab_cred"),
    t("config_tab_email"),
    t("config_tab_testdata"),
    t("config_tab_env"),
])

# ════════════════════════════════════════════════════
# Tab 0：Operations（Code Sync + Clean Test Data）
# ════════════════════════════════════════════════════
_VENV_PYTHON_OPS = str(project_root / ".venv" / "bin" / "python3")
if not os.path.exists(_VENV_PYTHON_OPS):
    _VENV_PYTHON_OPS = "python3"

with tab_ops:
    # ── Code Sync ────────────────────────────────────────────────
    st.subheader(t("settings_sync_title"))
    st.caption(t("settings_sync_desc"))

    col_pull, _ = st.columns([1, 3])
    with col_pull:
        pull_btn = st.button(t("settings_sync_btn"), type="primary", use_container_width=True, key="ops_pull_btn")

    if pull_btn:
        with st.spinner(t("settings_syncing")):
            try:
                result = subprocess.run(["git", "pull"], capture_output=True, text=True,
                                        cwd=str(project_root), timeout=60)
                if result.returncode == 0:
                    out = result.stdout.strip()
                    if "Already up to date" in out:
                        st.info(t("settings_sync_ok", out=out))
                    else:
                        st.success(t("settings_sync_pulled", out=out))
                else:
                    st.error(t("settings_sync_fail", err=result.stderr.strip()))
            except subprocess.TimeoutExpired:
                st.error(t("settings_sync_timeout"))
            except Exception as e:
                st.error(t("settings_sync_err", e=e))

    st.markdown("---")

    # ── Clean Test Data ───────────────────────────────────────────
    st.subheader(t("settings_clean_title"))
    st.caption(t("settings_clean_desc"))

    def _run_cleanup_script_ops(dry_run: bool):
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
dry_run = {str(dry_run)}
if not dry_run:
    from datetime import datetime
    date_str = datetime.now().strftime("%m%d_%H%M")
    backup_sql = f\"\"\"
SELECT public.backup_tables_daily(
    ARRAY['t_share_recipient','t_share_recipient_group','contact','t_share_sub_account','t_share_fbo_account'],
    '{{date_str}}', ARRAY['actc']
);
\"\"\"
    try:
        db.execute_query(backup_sql)
        backup_tag = date_str
    except Exception as be:
        print(json.dumps({{"error": f"Backup failed: {{be}}"}}))
        sys.exit(0)
else:
    backup_tag = None
stats = cleaner.cleanup_all_test_data(dry_run=dry_run)
total = sum(sum(s.values()) for s in stats.values())
print(json.dumps({{"stats": stats, "total": total, "backup_tag": backup_tag}}))
"""
        result = subprocess.run([_VENV_PYTHON_OPS, "-c", script], capture_output=True,
                                text=True, cwd=str(project_root), timeout=120)
        if result.returncode != 0:
            return None, result.stderr.strip() or result.stdout.strip() or "Unknown error"
        out = result.stdout.strip()
        if not out:
            return None, "No output from script"
        try:
            return json.loads(out), None
        except Exception:
            return None, f"Parse failed: {out[:200]}"

    for _k in ["ops_show_cleanup_confirm", "ops_cleanup_scan_stats", "ops_cleanup_scan_total", "ops_cleanup_done_msg"]:
        if _k not in st.session_state:
            st.session_state[_k] = False if _k == "ops_show_cleanup_confirm" else \
                (None if "stats" in _k else (0 if "total" in _k else None))

    col_cleanup, _ = st.columns([1, 3])
    with col_cleanup:
        if st.button(t("settings_clean_btn"), type="primary", use_container_width=True, key="ops_btn_cleanup_scan"):
            with st.spinner(t("settings_scanning")):
                data, err = _run_cleanup_script_ops(dry_run=True)
            if err:
                st.error(f"❌ {err}")
            elif "error" in (data or {}):
                st.error(f"❌ {data['error']}")
            else:
                st.session_state.ops_cleanup_scan_stats = data.get("stats", {})
                st.session_state.ops_cleanup_scan_total = data.get("total", 0)
                st.session_state.ops_show_cleanup_confirm = True
                st.session_state.ops_cleanup_done_msg = None
                st.rerun()

    if st.session_state.ops_cleanup_done_msg:
        st.success(st.session_state.ops_cleanup_done_msg)

    if st.session_state.ops_show_cleanup_confirm:
        ops_stats = st.session_state.ops_cleanup_scan_stats
        ops_total = st.session_state.ops_cleanup_scan_total
        if ops_total == 0:
            st.info(t("settings_clean_empty"))
            st.session_state.ops_show_cleanup_confirm = False
        else:
            st.warning(t("settings_clean_found", n=ops_total))
            with st.expander(t("settings_clean_detail"), expanded=True):
                if ops_stats:
                    for module, module_stats in ops_stats.items():
                        module_total = sum(module_stats.values())
                        if module_total > 0:
                            st.markdown(f"**{module.upper()}** — {module_total}")
                            for table, count in module_stats.items():
                                if count > 0:
                                    st.text(f"   • {table}: {count}")
            st.markdown(t("settings_clean_backup"))
            st.markdown(t("settings_clean_confirm_q"))
            bc1, bc2, _ = st.columns([1, 1, 2])
            with bc1:
                if st.button(t("settings_clean_confirm"), type="primary", use_container_width=True, key="ops_btn_confirm_cleanup"):
                    with st.spinner(t("settings_cleaning")):
                        data, err = _run_cleanup_script_ops(dry_run=False)
                    if err:
                        st.error(t("settings_clean_fail", e=err))
                    elif "error" in (data or {}):
                        st.error(t("settings_clean_fail", e=data["error"]))
                    else:
                        st.session_state.ops_cleanup_done_msg = t("settings_clean_done",
                                                                   n=data.get("total", 0),
                                                                   tag=data.get("backup_tag", ""))
                        dirty_records_file = project_root / "reports" / "dirty_data_records.json"
                        try:
                            if dirty_records_file.exists():
                                dirty_records_file.unlink()
                        except Exception:
                            pass
                        run_status_file = project_root / "reports" / "run_status.json"
                        try:
                            if run_status_file.exists():
                                rs = json.loads(run_status_file.read_text(encoding="utf-8"))
                                rs["dirty_delta_total"] = 0
                                rs["dirty_ignored_total"] = 0
                                rs["dirty_items"] = []
                                rs["dirty_raw_items"] = []
                                run_status_file.write_text(json.dumps(rs, ensure_ascii=False), encoding="utf-8")
                        except Exception:
                            pass
                    st.session_state.ops_show_cleanup_confirm = False
                    st.session_state.ops_cleanup_scan_stats = None
                    st.rerun()
            with bc2:
                if st.button(t("settings_clean_cancel"), use_container_width=True, key="ops_btn_cancel_cleanup"):
                    st.session_state.ops_show_cleanup_confirm = False
                    st.session_state.ops_cleanup_scan_stats = None
                    st.rerun()

# ════════════════════════════════════════════════════
# Tab 1：API 凭据
# ════════════════════════════════════════════════════
with tab_cred:
    st.caption(t("config_cred_desc"))
    st.info(t("config_portal_hint"))

    cred_data = _load_creds()
    profiles: list = cred_data.get("profiles", [])
    active_name: str = cred_data.get("active_profile") or ""

    if active_name:
        active_p = next((p for p in profiles if p.get("name") == active_name), None)
        if active_p:
            st.success(t("config_active_ok", name=active_name, env=active_p.get("env", "DEV")))
        else:
            st.warning(t("config_active_missing", name=active_name))
            cred_data["active_profile"] = None
            _save_creds(cred_data)
            active_name = ""
    else:
        st.info(t("config_no_active"))

    st.markdown("---")

    if profiles:
        c1, c2, c3, c4, c5 = st.columns([3, 2, 2, 2, 2])
        c1.markdown(t("config_col_name"))
        c2.markdown("**Env**")
        c3.markdown(t("config_col_created"))
        c4.markdown(t("config_col_status"))
        c5.markdown(t("config_col_actions"))
        st.markdown('<hr style="margin:4px 0 8px;">', unsafe_allow_html=True)

        for i, p in enumerate(profiles):
            pname = p.get("name", f"{t('config_profile_prefix')} {i+1}")
            created_at = p.get("created_at", "—")
            penv = p.get("env", "—")
            is_active = pname == active_name

            r1, r2, r3, r4, r5 = st.columns([3, 2, 2, 2, 2])
            r1.markdown(f"{'🟢 ' if is_active else '⚪ '}**{pname}**")
            r2.caption(f"`{penv}`")
            r3.caption(created_at)
            with r4:
                if is_active:
                    st.caption(t("config_is_active"))
                else:
                    if st.button(t("config_set_active_btn"), key=f"activate_{i}", use_container_width=True):
                        cred_data["active_profile"] = pname
                        _save_creds(cred_data)
                        st.rerun()
            with r5:
                a1, a2 = st.columns(2)
                with a1:
                    if st.button(t("config_edit_btn"), key=f"edit_cred_{i}", use_container_width=True):
                        st.session_state["editing_profile_name"] = pname
                        st.rerun()
                with a2:
                    if st.button(t("config_del_btn"), key=f"del_cred_{i}", use_container_width=True):
                        cred_data["profiles"] = [x for x in profiles if x.get("name") != pname]
                        if cred_data.get("active_profile") == pname:
                            cred_data["active_profile"] = None
                        _save_creds(cred_data)
                        if st.session_state.get("editing_profile_name") == pname:
                            st.session_state.pop("editing_profile_name", None)
                        st.rerun()
    else:
        st.caption(t("config_no_creds"))

    editing_name = st.session_state.get("editing_profile_name", "")
    editing_profile = next((p for p in profiles if p.get("name") == editing_name), None) if editing_name else None
    if editing_profile:
        st.markdown(" ")
        with st.expander(t("config_edit_title", name=editing_name), expanded=True):
            def _decode_basic_auth(auth_b64: str):
                if not auth_b64:
                    return "", ""
                try:
                    decoded = base64.b64decode(auth_b64).decode("utf-8")
                    if ":" in decoded:
                        cid, sec = decoded.split(":", 1)
                        return cid, sec
                except (binascii.Error, UnicodeDecodeError, ValueError):
                    pass
                return "", ""

            fallback_client, fallback_secret = _decode_basic_auth(editing_profile.get("basic_auth", ""))

            ec1, ec2 = st.columns(2)
            with ec1:
                ed_name = st.text_input(t("config_name_label"),
                                        value=editing_profile.get("name", ""),
                                        key="edit_name")
            with ec2:
                _edit_env_names = _get_env_names()
                _current_env = editing_profile.get("env", _edit_env_names[0] if _edit_env_names else "")
                _edit_env_idx = _edit_env_names.index(_current_env) if _current_env in _edit_env_names else 0
                ed_env = st.selectbox(
                    t("config_env_label"),
                    _edit_env_names,
                    index=_edit_env_idx,
                    key="edit_env",
                )

            ec3, ec4 = st.columns(2)
            with ec3:
                ed_user = st.text_input(
                    t("config_user_label"),
                    value=editing_profile.get("user_id", ""),
                    key="edit_user",
                )
            with ec4:
                ed_account = st.text_input(
                    t("config_account_label"),
                    value=editing_profile.get("account_id", editing_profile.get("tenant_id", "")),
                    key="edit_account",
                )

            ed_client_id = st.text_area(
                t("config_client_id_label"),
                value=editing_profile.get("client_id", fallback_client),
                height=90,
                key="edit_client_id",
            )
            ed_secret = st.text_area(
                t("config_secret_label"),
                value=editing_profile.get("secret", fallback_secret),
                height=110,
                key="edit_secret",
            )

            ec5, ec6 = st.columns(2)
            with ec5:
                ed_core = st.text_input(
                    t("config_core_label"),
                    value=editing_profile.get("core", "actc"),
                    key="edit_core",
                )
            with ec6:
                ed_encryption = st.text_area(
                    t("config_encryption_label"),
                    value=editing_profile.get("encryption_key", ""),
                    height=110,
                    key="edit_encryption",
                )

            st.caption(t("config_required_hint"))
            sc1, sc2 = st.columns(2)
            with sc1:
                if st.button(t("config_save_edit_btn"), type="primary", key="btn_save_edit_cred"):
                    name_v = (ed_name or "").strip()
                    user_v = (ed_user or "").strip()
                    account_v = (ed_account or "").strip()
                    client_id_v = (ed_client_id or "").strip()
                    secret_v = (ed_secret or "").strip()
                    core_v = (ed_core or "").strip()
                    encryption_v = (ed_encryption or "").strip()
                    if not name_v:
                        st.error(t("config_name_empty"))
                    elif any(p.get("name") == name_v for p in profiles if p.get("name") != editing_name):
                        st.error(t("config_name_dup", name=name_v))
                    elif not user_v or not account_v or not client_id_v or not secret_v or not core_v:
                        st.error(t("config_fields_required"))
                    else:
                        basic_auth_v = base64.b64encode(f"{client_id_v}:{secret_v}".encode("utf-8")).decode("utf-8")
                        updated = dict(editing_profile)
                        updated.update({
                            "name": name_v,
                            "env": ed_env,
                            "user_id": user_v,
                            "account_id": account_v,
                            "client_id": client_id_v,
                            "secret": secret_v,
                            "core": core_v,
                            "encryption_key": encryption_v,
                            "tenant_id": account_v,
                            "basic_auth": basic_auth_v,
                        })
                        cred_data["profiles"] = [
                            updated if p.get("name") == editing_name else p
                            for p in profiles
                        ]
                        if cred_data.get("active_profile") == editing_name:
                            cred_data["active_profile"] = name_v
                        _save_creds(cred_data)
                        st.session_state.pop("editing_profile_name", None)
                        st.success(t("config_updated_ok", name=name_v))
                        st.rerun()
            with sc2:
                if st.button(t("config_cancel_edit_btn"), key="btn_cancel_edit_cred"):
                    st.session_state.pop("editing_profile_name", None)
                    st.rerun()

    st.markdown(" ")
    with st.expander(t("config_add_title"), expanded=len(profiles) == 0):
        _env_names = _get_env_names()
        nc1, nc2 = st.columns(2)
        with nc1:
            new_name = st.text_input(t("config_name_label"), placeholder=t("config_name_ph"), key="nc_name")
        with nc2:
            new_env = st.selectbox(t("config_env_label"), _env_names, key="nc_env")

        f1, f2 = st.columns(2)
        with f1:
            new_user = st.text_input(t("config_user_label"), placeholder=t("config_user_ph"), key="nc_user")
        with f2:
            new_account = st.text_input(t("config_account_label"), placeholder=t("config_account_ph"), key="nc_account")

        new_client_id = st.text_area(t("config_client_id_label"),
                                     placeholder=t("config_client_id_ph"),
                                     height=90,
                                     key="nc_client_id")
        new_secret = st.text_area(t("config_secret_label"),
                                  placeholder=t("config_secret_ph"),
                                  height=110,
                                  key="nc_secret")

        f3, f4 = st.columns(2)
        with f3:
            new_core = st.text_input(t("config_core_label"), placeholder=t("config_core_ph"), value="actc", key="nc_core")
        with f4:
            new_encryption_key = st.text_area(t("config_encryption_label"),
                                              placeholder=t("config_encryption_ph"),
                                              height=110,
                                              key="nc_encryption")

        st.caption(t("config_required_hint"))

        if st.button(t("config_save_btn"), type="primary", key="btn_save_cred"):
            name_v = (new_name or "").strip()
            user_v = (new_user or "").strip()
            account_v = (new_account or "").strip()
            client_id_v = (new_client_id or "").strip()
            secret_v = (new_secret or "").strip()
            core_v = (new_core or "").strip()
            encryption_v = (new_encryption_key or "").strip()

            if not name_v:
                st.error(t("config_name_empty"))
            elif any(p.get("name") == name_v for p in profiles):
                st.error(t("config_name_dup", name=name_v))
            elif not user_v or not account_v or not client_id_v or not secret_v or not core_v:
                st.error(t("config_fields_required"))
            else:
                # 兼容现有登录实现：由 client_id:secret 计算 BASIC_AUTH
                basic_auth_v = base64.b64encode(f"{client_id_v}:{secret_v}".encode("utf-8")).decode("utf-8")
                new_profile = {
                    "name": name_v, "env": new_env,
                    "user_id": user_v,
                    "account_id": account_v,
                    "client_id": client_id_v,
                    "secret": secret_v,
                    "core": core_v,
                    "encryption_key": encryption_v,
                    # 兼容字段（供老代码路径继续可用）
                    "tenant_id": account_v,
                    "basic_auth": basic_auth_v,
                    "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
                }
                cred_data["profiles"].append(new_profile)
                if not cred_data.get("active_profile"):
                    cred_data["active_profile"] = name_v
                _save_creds(cred_data)
                st.success(t("config_saved_ok", name=name_v))
                st.rerun()

# ════════════════════════════════════════════════════
# Tab 2：邮箱白名单
# ════════════════════════════════════════════════════
with tab_email:
    st.caption(t("config_email_desc"))

    if "email_list" not in st.session_state:
        st.session_state.email_list = _load_emails()

    to_remove = []
    for i, email in enumerate(st.session_state.email_list):
        r1, r2 = st.columns([6, 1])
        with r1:
            new_val = st.text_input(f"Email {i+1}", value=email, key=f"email_{i}", label_visibility="collapsed")
            st.session_state.email_list[i] = new_val
        with r2:
            if st.button("🗑️", key=f"del_email_{i}", help=t("common_delete")):
                to_remove.append(i)

    if to_remove:
        st.session_state.email_list = [e for idx, e in enumerate(st.session_state.email_list) if idx not in to_remove]
        st.rerun()

    st.markdown(" ")
    a1, a2 = st.columns([5, 1])
    with a1:
        new_email = st.text_input(t("config_email_input_label"), placeholder=t("config_email_add_ph"),
                                  key="new_email", label_visibility="collapsed")
    with a2:
        if st.button(t("config_email_add_btn"), use_container_width=True):
            addr = (new_email or "").strip()
            if addr and "@" in addr:
                if addr not in st.session_state.email_list:
                    st.session_state.email_list.append(addr)
                    st.rerun()
                else:
                    st.warning(t("config_email_dup"))
            else:
                st.warning(t("config_email_invalid"))

    st.markdown(" ")
    b1, b2 = st.columns(2)
    with b1:
        if st.button(t("config_email_save"), use_container_width=True):
            valid = [e.strip() for e in st.session_state.email_list if e.strip() and "@" in e]
            if not valid:
                st.error(t("config_email_min_one"))
            else:
                _save_emails(valid)
                st.success(t("config_email_saved", n=len(valid)))

    with b2:
        if st.button(t("config_email_push"), type="primary", use_container_width=True):
            valid = [e.strip() for e in st.session_state.email_list if e.strip() and "@" in e]
            if not valid:
                st.error(t("config_email_min_one"))
            else:
                _save_emails(valid)
                with st.spinner(t("common_pushing")):
                    try:
                        subprocess.run(["git", "add", "email_config.json"], cwd=str(project_root), capture_output=True)
                        r_commit = subprocess.run(["git", "commit", "-m", "chore: update email whitelist"],
                                                  cwd=str(project_root), capture_output=True, text=True)
                        r_push   = subprocess.run(["git", "push"], cwd=str(project_root),
                                                  capture_output=True, text=True, timeout=60)
                        if r_push.returncode == 0:
                            st.success(t("config_email_push_ok", n=len(valid)))
                        elif "nothing to commit" in r_commit.stdout:
                            st.info(t("config_email_no_change"))
                        else:
                            st.error(t("config_email_push_fail", err=r_push.stderr.strip()))
                    except Exception as e:
                        st.error(f"❌ {e}")

# ════════════════════════════════════════════════════
# Tab 3：测试数据管理
# ════════════════════════════════════════════════════
_CATEGORY_KEYS = [
    ("accounts",          "config_testdata_accounts"),
    ("financial_accounts","config_testdata_fas"),
    ("sub_accounts",      "config_testdata_subs"),
    ("bank_infos",        "config_testdata_bankinfos"),
]

with tab_testdata:
    st.caption(t("config_testdata_desc"))

    td_data = _load_testdata()
    envs = list(td_data.get("environments", {}).keys())

    # ── 环境选择 + 新增环境 ────────────────────────────────────
    env_col, add_col, del_col = st.columns([3, 1, 1])
    with env_col:
        if envs:
            sel_env = st.selectbox(
                t("config_testdata_env_label"),
                envs,
                key="td_env_selector",
                label_visibility="collapsed",
            )
        else:
            sel_env = None
            st.info(t("config_testdata_no_envs"))

    with add_col:
        if st.button(t("config_testdata_add_env_btn"), use_container_width=True, key="btn_add_env"):
            st.session_state["td_show_add_env"] = True

    with del_col:
        if sel_env and st.button(t("config_testdata_del_env_btn"), use_container_width=True, key="btn_del_env"):
            del td_data["environments"][sel_env]
            _save_testdata(td_data)
            st.success(t("config_testdata_env_deleted"))
            st.rerun()

    # ── 新增环境表单 ──────────────────────────────────────────
    if st.session_state.get("td_show_add_env"):
        with st.form("form_add_env"):
            new_env_name = st.text_input(
                t("config_testdata_env_label"),
                placeholder=t("config_testdata_new_env_ph"),
                key="td_new_env_name",
            )
            submitted = st.form_submit_button(t("config_testdata_save_entry"))
            if submitted:
                name_v = (new_env_name or "").strip()
                if not name_v:
                    st.error(t("config_testdata_name_required"))
                elif name_v in td_data.get("environments", {}):
                    st.error(t("config_testdata_env_exists"))
                else:
                    td_data.setdefault("environments", {})[name_v] = {
                        "accounts": [], "financial_accounts": [], "sub_accounts": [], "bank_infos": []
                    }
                    _save_testdata(td_data)
                    st.session_state.pop("td_show_add_env", None)
                    st.success(t("config_testdata_env_saved"))
                    st.rerun()

    st.markdown("---")

    if sel_env and sel_env in td_data.get("environments", {}):
        env_data = td_data["environments"][sel_env]

        # ── 每个数据类别 ──────────────────────────────────────
        for cat_key, cat_label_key in _CATEGORY_KEYS:
            entries = env_data.get(cat_key, [])
            with st.expander(f"{t(cat_label_key)}  ({len(entries)})", expanded=True):

                # 列表
                if entries:
                    h1, h2, h3, h4 = st.columns([3, 4, 3, 1])
                    h1.markdown(f"**{t('config_testdata_col_name')}**")
                    h2.markdown(f"**{t('config_testdata_col_id')}**")
                    h3.markdown(f"**{t('config_testdata_col_memo')}**")
                    h4.markdown("**&nbsp;**", unsafe_allow_html=True)
                    st.markdown('<hr style="margin:4px 0 8px;">', unsafe_allow_html=True)

                    to_del = None
                    for ei, entry in enumerate(entries):
                        c1, c2, c3, c4 = st.columns([3, 4, 3, 1])
                        c1.markdown(f"`{entry.get('name', '')}`")
                        c2.code(entry.get("id", ""), language=None)
                        c3.caption(entry.get("memo", ""))
                        with c4:
                            if st.button(
                                t("config_testdata_del_entry"),
                                key=f"del_{cat_key}_{ei}",
                                use_container_width=True,
                            ):
                                to_del = ei

                    if to_del is not None:
                        entries.pop(to_del)
                        env_data[cat_key] = entries
                        td_data["environments"][sel_env] = env_data
                        _save_testdata(td_data)
                        st.rerun()
                else:
                    st.caption("—")

                # 新增表单
                add_key = f"td_add_{cat_key}"
                if st.button(t("config_testdata_add_entry"), key=f"btn_{add_key}", use_container_width=False):
                    st.session_state[add_key] = True

                if st.session_state.get(add_key):
                    with st.form(f"form_{add_key}"):
                        na, ia, ma = st.columns([3, 4, 3])
                        new_name = na.text_input(
                            t("config_testdata_col_name"),
                            placeholder=t("config_testdata_name_ph"),
                            key=f"inp_name_{add_key}",
                        )
                        new_id = ia.text_input(
                            t("config_testdata_col_id"),
                            placeholder=t("config_testdata_id_ph"),
                            key=f"inp_id_{add_key}",
                        )
                        new_memo = ma.text_input(
                            t("config_testdata_col_memo"),
                            placeholder=t("config_testdata_memo_ph"),
                            key=f"inp_memo_{add_key}",
                        )
                        if st.form_submit_button(t("config_testdata_save_entry")):
                            n_v = (new_name or "").strip()
                            i_v = (new_id or "").strip()
                            if not n_v or not i_v:
                                st.error(t("config_testdata_name_required"))
                            else:
                                env_data.setdefault(cat_key, []).append({
                                    "name": n_v, "id": i_v, "memo": (new_memo or "").strip()
                                })
                                td_data["environments"][sel_env] = env_data
                                _save_testdata(td_data)
                                st.session_state.pop(add_key, None)
                                st.success(t("config_testdata_entry_saved"))
                                st.rerun()

# ════════════════════════════════════════════════════
# Tab 4：环境配置
# ════════════════════════════════════════════════════
with tab_env:
    st.caption(t("config_env_desc"))

    env_cfg = _load_envs()
    envs_list: list = env_cfg.get("environments", [])
    active_env_name: str = env_cfg.get("active_env") or ""
    active_env_obj = next((e for e in envs_list if e.get("name") == active_env_name), None)

    # ── Active Environment Banner ──────────────────────────────────
    st.subheader(t("config_env_active_title"))
    if active_env_obj:
        a_url  = active_env_obj.get("base_url", "")
        a_core = active_env_obj.get("core", "")
        preview_url = f"{a_url}/api/v1/cores/{a_core}/accounts"
        ba1, ba2, ba3 = st.columns(3)
        ba1.metric(t("config_env_col_name"), active_env_name)
        ba2.metric(t("config_env_col_core"), a_core)
        ba3.metric("Base URL", a_url)
        st.caption(f"{t('config_env_active_url')}: `{preview_url}`")
    else:
        st.info(t("config_env_no_active"))

    st.markdown("---")

    # ── Environments List ──────────────────────────────────────────
    st.subheader(t("config_env_list_title"))

    if envs_list:
        hc1, hc2, hc3, hc4, hc5, hc6 = st.columns([3, 5, 2, 2, 1, 1])
        hc1.markdown(f"**{t('config_env_col_name')}**")
        hc2.markdown(f"**{t('config_env_col_url')}**")
        hc3.markdown(f"**{t('config_env_col_core')}**")
        hc4.markdown(f"**{t('config_env_col_actions')}**")
        hc5.markdown("&nbsp;", unsafe_allow_html=True)
        hc6.markdown("&nbsp;", unsafe_allow_html=True)
        st.markdown('<hr style="margin:4px 0 8px;">', unsafe_allow_html=True)

        editing_env = st.session_state.get("env_editing_name", "")

        for ei, env_item in enumerate(envs_list):
            ename = env_item.get("name", "")
            eurl  = env_item.get("base_url", "")
            ecore = env_item.get("core", "")
            is_active = ename == active_env_name

            if editing_env == ename:
                # Inline edit form
                with st.form(f"form_edit_env_{ei}"):
                    ec1, ec2, ec3 = st.columns([3, 5, 2])
                    ed_name = ec1.text_input(t("config_env_name_label"), value=ename,  key=f"edit_ename_{ei}")
                    ed_url  = ec2.text_input(t("config_env_url_label"),  value=eurl,   key=f"edit_eurl_{ei}")
                    ed_core = ec3.text_input(t("config_env_core_label"), value=ecore,  key=f"edit_ecore_{ei}")
                    sb1, sb2 = st.columns(2)
                    if sb1.form_submit_button(t("config_env_save_btn"), type="primary"):
                        n_v = (ed_name  or "").strip()
                        u_v = (ed_url   or "").strip()
                        c_v = (ed_core  or "").strip()
                        if not n_v or not u_v or not c_v:
                            st.error(t("config_env_fields_required"))
                        elif n_v != ename and any(e.get("name") == n_v for e in envs_list):
                            st.error(t("config_env_name_dup"))
                        else:
                            envs_list[ei] = {"name": n_v, "base_url": u_v, "core": c_v}
                            if env_cfg.get("active_env") == ename:
                                env_cfg["active_env"] = n_v
                            env_cfg["environments"] = envs_list
                            _save_envs(env_cfg)
                            st.session_state.pop("env_editing_name", None)
                            st.success(t("config_env_saved"))
                            st.rerun()
                    if sb2.form_submit_button(t("config_env_cancel_btn")):
                        st.session_state.pop("env_editing_name", None)
                        st.rerun()
            else:
                # 6 列：Name | URL | Core | SetActive/Active | Edit | Del
                rc1, rc2, rc3, rc4, rc5, rc6 = st.columns([3, 5, 2, 2, 1, 1])
                rc1.markdown(f"**{ename}**")
                rc2.caption(eurl)
                rc3.caption(ecore)
                with rc4:
                    if is_active:
                        st.markdown("✅ **Active**")
                    else:
                        if st.button("Set Active", key=f"activate_env_{ei}", use_container_width=True):
                            env_cfg["active_env"] = ename
                            _save_envs(env_cfg)
                            st.success(t("config_env_activated", name=ename))
                            st.rerun()
                with rc5:
                    if st.button("✏️", key=f"edit_env_{ei}", help=t("config_env_edit_btn"), use_container_width=True):
                        st.session_state["env_editing_name"] = ename
                        st.rerun()
                with rc6:
                    if st.button("🗑️", key=f"del_env_{ei}", help=t("config_env_del_btn"), use_container_width=True):
                        envs_list.pop(ei)
                        if env_cfg.get("active_env") == ename:
                            env_cfg["active_env"] = envs_list[0]["name"] if envs_list else None
                        env_cfg["environments"] = envs_list
                        _save_envs(env_cfg)
                        st.success(t("config_env_deleted"))
                        st.rerun()
    else:
        st.caption(t("config_env_no_envs"))

    st.markdown(" ")

    # ── Add Environment Form ───────────────────────────────────────
    if st.button(t("config_env_add_btn"), key="btn_add_new_env"):
        st.session_state["env_show_add"] = True

    if st.session_state.get("env_show_add"):
        with st.form("form_add_new_env"):
            nc1, nc2, nc3 = st.columns([3, 5, 2])
            new_ename = nc1.text_input(t("config_env_name_label"), placeholder=t("config_env_name_ph"), key="add_env_name")
            new_eurl  = nc2.text_input(t("config_env_url_label"),  placeholder=t("config_env_url_ph"),  key="add_env_url")
            new_ecore = nc3.text_input(t("config_env_core_label"), placeholder=t("config_env_core_ph"), key="add_env_core")
            if st.form_submit_button(t("config_env_save_btn"), type="primary"):
                n_v = (new_ename or "").strip()
                u_v = (new_eurl  or "").strip()
                c_v = (new_ecore or "").strip()
                if not n_v or not u_v or not c_v:
                    st.error(t("config_env_fields_required"))
                elif any(e.get("name") == n_v for e in envs_list):
                    st.error(t("config_env_name_dup"))
                else:
                    envs_list.append({"name": n_v, "base_url": u_v, "core": c_v})
                    if not env_cfg.get("active_env"):
                        env_cfg["active_env"] = n_v
                    env_cfg["environments"] = envs_list
                    _save_envs(env_cfg)
                    st.session_state.pop("env_show_add", None)
                    st.success(t("config_env_saved"))
                    st.rerun()
