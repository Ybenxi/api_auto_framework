"""系统设置页面 - 代码同步 & 邮箱白名单管理"""
import streamlit as st
import subprocess
import json
from pathlib import Path

st.set_page_config(
    page_title="系统设置 - API自动化测试平台",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

st.title("⚙️ 系统设置")

project_root = Path(__file__).parent.parent.parent
email_config_file = project_root / "email_config.json"

# ──────────────────────────────────────────────
# 第一区块：代码同步
# ──────────────────────────────────────────────
st.subheader("🔄 代码同步")
st.caption("从 GitHub 拉取最新代码。拉取后 Streamlit 会自动热重载，刷新浏览器即可看到最新平台界面。")

col_pull, col_status = st.columns([1, 3])

with col_pull:
    pull_btn = st.button("⬇️ 拉取最新代码 (git pull)", type="primary", use_container_width=True)

if pull_btn:
    with st.spinner("正在执行 git pull ..."):
        try:
            result = subprocess.run(
                ["git", "pull"],
                capture_output=True,
                text=True,
                cwd=str(project_root),
                timeout=60
            )
            if result.returncode == 0:
                output = result.stdout.strip()
                if "Already up to date" in output:
                    st.info(f"✅ 已是最新代码，无需更新\n```\n{output}\n```")
                else:
                    st.success(f"✅ 代码拉取成功！请刷新浏览器查看最新界面。\n```\n{output}\n```")
            else:
                st.error(f"❌ 拉取失败\n```\n{result.stderr.strip()}\n```")
        except subprocess.TimeoutExpired:
            st.error("❌ 拉取超时（60秒），请检查网络连接")
        except Exception as e:
            st.error(f"❌ 执行异常: {e}")

st.markdown("---")

# ──────────────────────────────────────────────
# 第二区块：邮箱白名单管理
# ──────────────────────────────────────────────
st.subheader("📧 邮箱白名单")
st.caption("配置定时测试报告的收件人列表。保存后需点击【推送到 GitHub】，下次 GitHub Actions 定时任务才会使用新列表。")

# 读取当前配置
def load_email_config() -> list:
    if email_config_file.exists():
        try:
            with open(email_config_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data.get("recipients", [])
        except Exception:
            return []
    return ["byan@fintechautomation.com"]


def save_email_config(recipients: list):
    with open(email_config_file, "w", encoding="utf-8") as f:
        json.dump({"recipients": recipients}, f, indent=2, ensure_ascii=False)


current_recipients = load_email_config()

# 展示当前收件人
st.markdown("**当前收件人列表：**")

# 用 session_state 管理编辑状态
if "email_list" not in st.session_state:
    st.session_state.email_list = list(current_recipients)

# 逐行展示 + 删除按钮
emails_to_remove = []
for i, email in enumerate(st.session_state.email_list):
    row_col1, row_col2 = st.columns([5, 1])
    with row_col1:
        new_val = st.text_input(
            f"邮箱 {i+1}",
            value=email,
            key=f"email_input_{i}",
            label_visibility="collapsed"
        )
        st.session_state.email_list[i] = new_val
    with row_col2:
        if st.button("🗑️", key=f"del_email_{i}", help="删除此邮箱"):
            emails_to_remove.append(i)

# 执行删除
if emails_to_remove:
    st.session_state.email_list = [
        e for idx, e in enumerate(st.session_state.email_list)
        if idx not in emails_to_remove
    ]
    st.rerun()

# 新增邮箱
st.markdown(" ")
add_col1, add_col2 = st.columns([4, 1])
with add_col1:
    new_email = st.text_input("新增邮箱地址", placeholder="example@company.com", key="new_email_input")
with add_col2:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("➕ 添加", use_container_width=True):
        addr = new_email.strip()
        if addr and "@" in addr:
            if addr not in st.session_state.email_list:
                st.session_state.email_list.append(addr)
                st.rerun()
            else:
                st.warning("该邮箱已存在")
        else:
            st.warning("请输入有效的邮箱地址")

st.markdown(" ")

# 保存 + 推送按钮
btn_col1, btn_col2 = st.columns(2)

with btn_col1:
    if st.button("💾 保存到本地", use_container_width=True):
        valid = [e.strip() for e in st.session_state.email_list if e.strip() and "@" in e]
        if not valid:
            st.error("❌ 至少需要一个有效邮箱")
        else:
            try:
                save_email_config(valid)
                st.success(f"✅ 已保存 {len(valid)} 个收件人到 email_config.json")
            except Exception as e:
                st.error(f"❌ 保存失败: {e}")

with btn_col2:
    if st.button("🚀 保存并推送到 GitHub", type="primary", use_container_width=True):
        valid = [e.strip() for e in st.session_state.email_list if e.strip() and "@" in e]
        if not valid:
            st.error("❌ 至少需要一个有效邮箱")
        else:
            try:
                save_email_config(valid)
                with st.spinner("正在推送到 GitHub ..."):
                    # git add
                    r1 = subprocess.run(
                        ["git", "add", "email_config.json"],
                        capture_output=True, text=True, cwd=str(project_root)
                    )
                    # git commit
                    r2 = subprocess.run(
                        ["git", "commit", "-m", "chore: 更新邮箱白名单收件人列表"],
                        capture_output=True, text=True, cwd=str(project_root)
                    )
                    # git push
                    r3 = subprocess.run(
                        ["git", "push"],
                        capture_output=True, text=True, cwd=str(project_root), timeout=60
                    )

                if r3.returncode == 0:
                    st.success(f"✅ 已保存并推送成功！下次定时任务将使用新的收件人列表（{len(valid)} 人）")
                elif "nothing to commit" in r2.stdout:
                    st.info("✅ 邮箱列表未变化，无需推送")
                else:
                    st.error(f"❌ 推送失败\n```\n{r3.stderr.strip()}\n```")
            except subprocess.TimeoutExpired:
                st.error("❌ 推送超时（60秒），请检查网络连接")
            except Exception as e:
                st.error(f"❌ 操作异常: {e}")

st.markdown("---")
st.caption("💡 提示：每次修改邮箱列表后，需点击【保存并推送到 GitHub】，GitHub Actions 定时任务才会读取到最新收件人。")

# ──────────────────────────────────────────────
# 第三区块：脏数据清理
# ──────────────────────────────────────────────
st.markdown("---")
st.subheader("🗑️ 测试脏数据清理")
st.caption("清理所有名称以 **Auto TestYan** 开头的测试数据（counterparty、contact、sub_account、fbo_account 等），操作前先备份。")

def _get_cleanup_stats():
    """扫描并返回 (stats_dict, total_count, error_msg)"""
    try:
        import sys
        sys.path.insert(0, str(project_root))
        from dao.db_manager import DBManager
        from utils.data_cleanup import DataCleanup
        from config.config import config as _cfg

        db_config = _cfg.db_config
        if db_config.get("host") == "localhost":
            return None, 0, "数据库未配置（使用默认 localhost），请在 .env 配置数据库连接信息"

        db = DBManager(db_config)
        cleaner = DataCleanup(db)
        # 添加 counterparty_group 规则（默认未内置）
        cleaner.CLEANUP_RULES['counterparty_group'] = {
            'main_table': 'actc.t_share_recipient_group',
            'id_field': 'id',
            'related_tables': [{'table': 'actc.t_share_recipient_group_relation', 'foreign_key': 'recipient_group_id'}],
            'name_field': 'name'
        }

        stats = cleaner.cleanup_all_test_data(dry_run=True)
        total = sum(sum(s.values()) for s in stats.values())
        return stats, total, None
    except Exception as e:
        return None, 0, str(e)

def _do_cleanup():
    """执行实际清理，返回 (actual_total, backup_tag, error_msg)"""
    try:
        import sys
        from datetime import datetime as _dt
        sys.path.insert(0, str(project_root))
        from dao.db_manager import DBManager
        from utils.data_cleanup import DataCleanup
        from config.config import config as _cfg

        db_config = _cfg.db_config
        db = DBManager(db_config)
        cleaner = DataCleanup(db)
        cleaner.CLEANUP_RULES['counterparty_group'] = {
            'main_table': 'actc.t_share_recipient_group',
            'id_field': 'id',
            'related_tables': [{'table': 'actc.t_share_recipient_group_relation', 'foreign_key': 'recipient_group_id'}],
            'name_field': 'name'
        }

        # 备份
        date_str = _dt.now().strftime("%m%d_%H%M")
        backup_sql = f"""
SELECT public.backup_tables_daily(
    ARRAY['t_share_recipient', 't_share_recipient_group',
          'contact', 't_share_sub_account', 't_share_fbo_account'],
    '{date_str}',
    ARRAY['actc']
);
"""
        db.execute_query(backup_sql)

        # 执行清理
        actual_stats = cleaner.cleanup_all_test_data(dry_run=False)
        actual_total = sum(sum(s.values()) for s in actual_stats.values())
        return actual_total, date_str, None
    except Exception as e:
        return 0, None, str(e)


# Session state 管理弹窗状态
if "show_cleanup_confirm" not in st.session_state:
    st.session_state.show_cleanup_confirm = False
if "cleanup_scan_stats" not in st.session_state:
    st.session_state.cleanup_scan_stats = None
if "cleanup_scan_total" not in st.session_state:
    st.session_state.cleanup_scan_total = 0
if "cleanup_done_msg" not in st.session_state:
    st.session_state.cleanup_done_msg = None

col_cleanup, col_cleanup_status = st.columns([1, 3])

with col_cleanup:
    if st.button("🔍 扫描并清理脏数据", type="primary", use_container_width=True, key="btn_cleanup_scan"):
        with st.spinner("正在扫描数据库中的测试数据..."):
            stats, total, err = _get_cleanup_stats()
        if err:
            st.error(f"❌ {err}")
        else:
            st.session_state.cleanup_scan_stats = stats
            st.session_state.cleanup_scan_total = total
            st.session_state.show_cleanup_confirm = True
            st.session_state.cleanup_done_msg = None
            st.rerun()

# 显示清理结果
if st.session_state.cleanup_done_msg:
    st.success(st.session_state.cleanup_done_msg)

# 确认弹窗（用 expander 模拟）
if st.session_state.show_cleanup_confirm:
    stats = st.session_state.cleanup_scan_stats
    total = st.session_state.cleanup_scan_total

    if total == 0:
        st.info("✅ 当前没有找到需要清理的测试数据（名称以 Auto TestYan 开头），数据库已干净！")
        st.session_state.show_cleanup_confirm = False
    else:
        with st.container():
            st.warning(f"⚠️ 发现 **{total}** 条测试数据（名称以 Auto TestYan 开头）")

            # 展示详细统计
            with st.expander("📊 查看详细统计", expanded=True):
                if stats:
                    for module, module_stats in stats.items():
                        module_total = sum(module_stats.values())
                        if module_total > 0:
                            st.markdown(f"**{module.upper()}** — 共 {module_total} 条")
                            for table, count in module_stats.items():
                                if count > 0:
                                    st.text(f"   • {table}: {count} 条")

            st.markdown("**操作前会先自动备份所有数据到 `backup_data` schema。**")
            st.markdown("确认要删除这些测试数据吗？")

            btn_col1, btn_col2, _ = st.columns([1, 1, 2])
            with btn_col1:
                if st.button("✅ 确认清理", type="primary", use_container_width=True, key="btn_confirm_cleanup"):
                    with st.spinner("正在备份并清理数据..."):
                        actual_total, date_str, err = _do_cleanup()
                    if err:
                        st.error(f"❌ 清理失败: {err}")
                    else:
                        st.session_state.cleanup_done_msg = (
                            f"✅ 清理完成！共删除 {actual_total} 条记录。"
                            f"备份位置: backup_data.actc_*_{date_str}"
                        )
                    st.session_state.show_cleanup_confirm = False
                    st.session_state.cleanup_scan_stats = None
                    st.rerun()

            with btn_col2:
                if st.button("❌ 取消", use_container_width=True, key="btn_cancel_cleanup"):
                    st.session_state.show_cleanup_confirm = False
                    st.session_state.cleanup_scan_stats = None
                    st.rerun()
