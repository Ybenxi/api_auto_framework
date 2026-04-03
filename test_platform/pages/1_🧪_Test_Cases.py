"""测试用例浏览页面"""
import streamlit as st
from pathlib import Path
import sys
import re
import json

sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.auth import require_login, show_logout_button
from utils.i18n import t

st.set_page_config(page_title=t("cases_page_title"), page_icon="📋", layout="wide", initial_sidebar_state="expanded")
st.markdown("<style>footer{visibility:hidden;}</style>", unsafe_allow_html=True)

require_login()
show_logout_button()

st.title(t("cases_title"))

project_root = Path(__file__).parent.parent.parent
test_cases_dir = project_root / "test_cases"
cache_dir = Path(__file__).parent.parent / ".cache"
cache_file = cache_dir / "cases_doc_cache.json"

# ── 模块显示名称 ──────────────────────────────────────────────────────
MODULE_DISPLAY_NAMES = {
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

# 指定排列顺序（folder name 顺序）
_MODULE_ORDER = [
    "user_sign_up", "account_opening", "identity_security", "tenant",
    "profile_account", "contact", "financial_account", "sub_account",
    "fbo_account", "open_banking", "payment_deposit",
    "card", "card_opening",
    "trading_order", "statement", "counterparty",
    "investment", "account_summary", "card_report", "client_list",
]


def _display_name(folder: str) -> str:
    return MODULE_DISPLAY_NAMES.get(folder, folder.replace("_", " ").title())


def _sort_key(folder: str) -> int:
    try:
        return _MODULE_ORDER.index(folder)
    except ValueError:
        return len(_MODULE_ORDER)


def _has_chinese(text: str) -> bool:
    return any("\u4e00" <= c <= "\u9fff" for c in (text or ""))


def _method_to_title(method_name: str) -> str:
    title = method_name.replace("test_", "").replace("_", " ").strip()
    return title.capitalize() if title else method_name


_ZH_EN_MAP = {
    # Scenario markers
    "测试场景": "Test Scenario",
    "验证点": "Validation Points",
    # High-priority full phrases
    "详情与列表一致性": "Consistency with list",
    "成功获取卡片详情": "Successfully retrieve card detail",
    "接口返回 200": "API returns code 200",
    "返回卡片详情": "Return card detail",
    "响应字段完整性验证": "Response fields completeness verification",
    "字段完整性验证": "Fields completeness verification",
    "对比详情接口和列表接口返回的数据一致性": "Compare consistency between detail and list responses",
    "创建后立即查询详情，验证数据一致性": "Create then query detail immediately to verify data consistency",
    "创建后立即在列表中查询，验证数据一致性": "Create then query in list immediately to verify data consistency",
    "使用不存在的筛选条件，验证空结果处理": "Verify empty result with non-existent filter",
    "基础列表查询 - 验证接口可用性": "Basic list query - verify API availability",
    "排序功能验证 - 按姓名排序": "Sorting verification - sort by name",
    "排序功能验证 - 按账户名称排序": "Sorting verification - sort by account name",
    "分页功能验证": "Pagination verification",
    "空结果验证": "Empty result verification",
    "多条件组合筛选": "Multiple filters combined",
    "名称筛选查询 - 验证筛选逻辑": "Name filter query - verify filtering logic",
    "名称筛选查询": "Name filter query",
    "枚举类型筛选": "Enum type filter",
    "状态筛选": "Status filter",
    "缺少必需字段时创建失败": "Create failed with missing required fields",
    "使用必需字段创建": "Create with required fields",
    "使用所有字段创建": "Create with all fields",
    "创建后立即查询详情": "Query detail immediately after creation",
    "创建后立即在列表中查询": "Query in list immediately after creation",
    "验证数据一致性": "Verify data consistency",
    "数据一致性": "Data consistency",
    "验证响应字段完整性": "Validate response field completeness",
    "成功获取": "Successfully get",
    "成功创建": "Successfully create",
    "成功更新": "Successfully update",
    "成功删除": "Successfully delete",
    "缺少必需字段": "Missing required fields",
    "使用无效": "Use invalid",
    "使用不存在": "Use non-existent",
    "无效": "Invalid",
    "不存在": "Not found",
    "验证": "Validate",
    "筛选": "Filter",
    "查询": "Query",
    "获取": "Retrieve",
    "更新": "Update",
    "创建": "Create",
    "删除": "Delete",
    "排序": "Sort",
    "字段": "fields",
    "结构": "structure",
    "分页": "pagination",
    "列表": "list",
    "详情": "detail",
    "卡片": "card",
    "账户": "account",
    "交易": "transaction",
    "响应": "response",
    "返回": "return",
    "数据": "data",
    "内容": "content",
    "类型": "type",
    "状态": "status",
    "参数": "parameter",
    "条件": "condition",
    "范围": "range",
    "完整性": "completeness",
    "对手方": "counterparty",
    "交易对手": "counterparty",
    "身份": "identity",
    "安全": "security",
    "认证": "authentication",
    "授权": "authorization",
    "功能": "function",
    "模块": "module",
    "接口": "API",
    "场景": "scenario",
    "成功": "success",
    "失败": "failed",
    "空": "empty",
    "全部": "all",
    "所有": "all",
    "多个": "multiple",
    "单个": "single",
    "必需": "required",
    "可选": "optional",
    "并": " and ",
    "与": " and ",
    "和": " and ",
    "或": " or ",
    "使用": "with ",
    "按": "by ",
    "通过": "via ",
    "包括": "including",
    "包含": "contains",
    "：": ": ",
    "，": ", ",
    "（": " (",
    "）": ")",
    "返回": "return",
    "一致性": "consistency",
}


def _translate_zh_to_en(text: str) -> str:
    out = text or ""
    for k in sorted(_ZH_EN_MAP.keys(), key=len, reverse=True):
        out = out.replace(k, _ZH_EN_MAP[k])
    out = re.sub(r"测试场景\s*\d+\s*[：:]\s*", "", out).strip()
    out = re.sub(r"验证点\s*[：:]\s*", "Validation Points: ", out)
    out = re.sub(r"\s+", " ", out).strip()
    return out


def _translate_docstring_block(docstring: str, method_name: str, lang: str) -> str:
    """
    仅翻译 docstring 第一行（场景描述），验证点逐行独立翻译，避免整段拼接后
    验证点内容混入标题。
    """
    raw = (docstring or "").strip()
    if not raw:
        return ""
    if lang != "en":
        return raw

    raw_lines = [x.strip() for x in raw.split("\n")]
    result_lines = []
    for i, line in enumerate(raw_lines):
        if not _has_chinese(line):
            result_lines.append(line)
            continue
        translated = _translate_zh_to_en(line)
        # 兜底清除残留中文
        if _has_chinese(translated):
            translated = re.sub(r"[\u4e00-\u9fff]+", "", translated).strip()
        translated = re.sub(r"\s+", " ", translated).strip()
        # 第一行为空时用方法名
        if i == 0 and not translated:
            translated = _method_to_title(method_name)
        result_lines.append(translated)

    return "\n".join(result_lines).strip()


def _extract_scenario_desc(method_name: str, lines: list[str], lang: str) -> str:
    first = lines[0].strip() if lines else ""
    if lang == "en":
        first = re.sub(r"^Test Scenario\s*\d+\s*:\s*", "", first, flags=re.IGNORECASE).strip()
    else:
        first = re.sub(r"^测试场景\s*\d+\s*[：:]\s*", "", first).strip()
    if not first:
        return _method_to_title(method_name) if lang == "en" else method_name
    return first


def _load_cases_cache() -> dict:
    if not cache_file.exists():
        return {}
    try:
        return json.loads(cache_file.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _save_cases_cache(cache: dict):
    try:
        cache_dir.mkdir(parents=True, exist_ok=True)
        cache_file.write_text(json.dumps(cache, ensure_ascii=False), encoding="utf-8")
    except Exception:
        pass


def _extract_validation_points(lines: list[str], lang: str) -> list[str]:
    verification_points = []
    in_validation = False
    for line in lines[1:]:
        stripped = line.strip()
        if not stripped:
            continue
        if stripped in ("验证点：", "验证点:") or stripped.lower().startswith("validation points"):
            in_validation = True
            continue
        if in_validation:
            verification_points.append(stripped)
            continue
        if stripped.startswith(("1.", "2.", "3.", "4.", "5.", "6.", "7.", "8.", "9.", "-", "•")):
            verification_points.append(stripped)

    cleaned_points = []
    for vp in verification_points:
        clean_vp = re.sub(r"^[\d\.\-•\s]+", "", vp).strip()
        if clean_vp:
            if lang == "en" and _has_chinese(clean_vp):
                clean_vp = _translate_zh_to_en(clean_vp)
                clean_vp = re.sub(r"[\u4e00-\u9fff]+", "", clean_vp).strip()
                clean_vp = re.sub(r"\s+", " ", clean_vp).strip()
            if lang == "en" and not clean_vp:
                clean_vp = t("cases_validation_item")
            cleaned_points.append(clean_vp)
    return cleaned_points


def _parse_methods_for_display(content: str, lang: str):
    test_methods = re.findall(r'def (test_\w+)\([^)]*\):\s*"""(.*?)"""', content, re.DOTALL)
    parsed = []
    for method_name, docstring in test_methods:
        display_docstring = _translate_docstring_block(docstring, method_name, lang)
        lines = [x.strip() for x in display_docstring.split("\n")] if display_docstring else []
        scenario_desc = _extract_scenario_desc(method_name, lines, lang)
        parsed.append(
            {
                "method_name": method_name,
                "scenario_desc": scenario_desc,
                "validation_points": _extract_validation_points(lines, lang),
            }
        )
    return parsed

all_modules = [d for d in test_cases_dir.iterdir() if d.is_dir() and not d.name.startswith("__")]
modules_with_tests = [m.name for m in all_modules if list(m.rglob("test_*.py"))]
# 按指定顺序排列，未在列表内的追加到末尾（按字母）
modules = sorted(modules_with_tests, key=_sort_key)
display_to_folder = {_display_name(m): m for m in modules}
display_names = list(display_to_folder.keys())

if not modules:
    st.error(t("cases_no_modules"))
    st.stop()

# ── 持久化选中的模块，切换语言后保持选中状态 ─────────────────────────
_SEL_MODULE_KEY = "cases_selected_module"
_SEL_FILE_KEY   = "cases_selected_file"

# 语言切换后 display_names 顺序不变，只需记住 folder name（不受语言影响）
saved_folder = st.session_state.get(_SEL_MODULE_KEY, "")
saved_idx = 0
if saved_folder and saved_folder in display_to_folder.values():
    try:
        saved_idx = list(display_to_folder.values()).index(saved_folder)
    except ValueError:
        saved_idx = 0

sel_col1, sel_col2 = st.columns(2)
with sel_col1:
    selected_display = st.selectbox(t("cases_select_module"), display_names, index=saved_idx)
    selected_module = display_to_folder[selected_display]
    st.session_state[_SEL_MODULE_KEY] = selected_module  # 持久化

module_path = test_cases_dir / selected_module
test_files = sorted(module_path.rglob("test_*.py"))

with sel_col2:
    if test_files:
        file_display_names = [str(f.relative_to(module_path)) for f in test_files]
        saved_file = st.session_state.get(_SEL_FILE_KEY, "")
        file_idx = 0
        if saved_file in file_display_names:
            file_idx = file_display_names.index(saved_file)
        selected_file_display = st.selectbox(
            t("cases_select_file"), file_display_names, index=file_idx)
        st.session_state[_SEL_FILE_KEY] = selected_file_display  # 持久化
        selected_file_path = test_files[file_display_names.index(selected_file_display)]
        selected_file = selected_file_display
    else:
        st.warning(t("cases_no_files"))
        st.stop()

st.markdown("---")

if not test_files:
    st.warning(t("cases_no_files"))
else:
    file_path = module_path / selected_file
    st.markdown(f"<h4 style='margin:0'>📝 {selected_file}</h4>", unsafe_allow_html=True)
    st.markdown(" ")

    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        lang = st.session_state.get("lang", "en")
        stat = file_path.stat()
        cache_key = f"v2::{file_path}::{lang}::{stat.st_mtime_ns}::{stat.st_size}"
        cache = _load_cases_cache()
        parsed_methods = cache.get(cache_key)
        if not parsed_methods:
            parsed_methods = _parse_methods_for_display(content, lang)
            cache[cache_key] = parsed_methods
            _save_cases_cache(cache)

        if parsed_methods:
            total = len(parsed_methods)
            expanded = st.session_state.get("expand_all_state", False)
            st.info(t("cases_found", n=total))

            btn_label = t("cases_collapse_all") if expanded else t("cases_expand_all")
            if st.button(btn_label, key="toggle_all"):
                st.session_state["expand_all_state"] = not expanded
                st.rerun()

            for idx, item in enumerate(parsed_methods, 1):
                method_name = item.get("method_name", "")
                scenario_desc = item.get("scenario_desc", method_name or t("cases_no_desc"))
                validation_points = item.get("validation_points", [])
                with st.expander(
                    t("cases_scenario_with_desc", i=idx, name=method_name, desc=scenario_desc),
                    expanded=expanded,
                ):
                    st.markdown(f"**{scenario_desc}**")
                    if validation_points:
                        st.markdown(t("cases_validation"))
                        for vp in validation_points:
                            st.markdown(f"- {vp}")
        else:
            st.warning(t("cases_no_methods"))

        with st.expander(t("cases_view_code"), expanded=False):
            st.code(content, language="python")

    except Exception as e:
        st.error(t("cases_read_err", e=e))

st.markdown("---")
st.caption(t("cases_tip"))
