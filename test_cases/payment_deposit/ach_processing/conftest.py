import pytest
import time
from api.ach_processing_api import ACHProcessingAPI
from api.financial_account_api import FinancialAccountAPI
from test_cases.test_ids import ACCOUNT_1_ID
from utils.logger import logger

pytestmark = pytest.mark.ach_processing

# ── FA / SUB 常量（不会被删除）──────────────────────────────────────────────
ACH_FP_FALSE_FA  = "251212054048470574"  # FA 2，用于 Credit fp=False
ACH_FP_FALSE_SUB = "251212054048470660"  # 固定 Sub（FA1 下）

ACH_DEBIT_FP_FALSE_FA  = "251212054048470568"  # FA 1，用于 Debit fp=False
ACH_DEBIT_FP_FALSE_SUB = "251212054048470660"  # 固定 Sub
ACH_DEBIT_PROFILE_ACCOUNT_ID = ACCOUNT_1_ID    # FA1 profile account


# ── 公共工具函数 ─────────────────────────────────────────────────────────────

def _ach_list_content(response) -> list:
    body = response.json()
    if body.get("code") != 200:
        return []
    data = body.get("data", body) or {}
    return data.get("content") or [] if isinstance(data, dict) else []


def _cp_id_from_resp(resp, name: str) -> str:
    """从创建 CP 的响应里提取 id，失败则 pytest.fail"""
    if resp.status_code != 200:
        pytest.fail(f"创建 {name} 失败: HTTP {resp.status_code}\n{resp.text[:300]}")
    body = resp.json()
    # ACH counterparty 响应无 code 包装层，但有时有，兼容处理
    if "code" in body:
        if body.get("code") != 200:
            pytest.fail(f"创建 {name} 失败: code={body.get('code')}, {body.get('error_message')}")
        data = body.get("data") or body
    else:
        data = body
    cp_id = str(data.get("id") or "")
    if not cp_id:
        pytest.fail(f"创建 {name} 返回无 id: {body}")
    logger.info(f"✓ {name}: id={cp_id}")
    return cp_id


def _profile_account_id_for_fa(ach_processing_api, fa_id: str) -> str:
    """查询 FA 对应的 profile account_id。"""
    r = ach_processing_api.list_financial_accounts(size=100)
    for row in _ach_list_content(r):
        if str(row.get("id")) == str(fa_id) and row.get("account_id"):
            return str(row["account_id"])
    fa_api = FinancialAccountAPI(session=ach_processing_api.session)
    d = fa_api.get_financial_account_detail(fa_id).json()
    if d.get("code") != 200:
        logger.warning(f"无法解析 FA {fa_id} 的 account_id, detail code={d.get('code')}")
        return ACCOUNT_1_ID
    data = d.get("data", d) or {}
    return str(data.get("account_id") or ACCOUNT_1_ID)


def _cp_has_approved_assign_to_account(cp: dict, profile_account_id: str) -> bool:
    for item in cp.get("assign_account_ids") or []:
        if not isinstance(item, dict):
            continue
        if (item.get("status") or "").strip() != "Approved":
            continue
        aid = item.get("account_id") or item.get("id")
        if aid is not None and str(aid) == str(profile_account_id):
            return True
    return False


# ── Module-scoped CP fixtures（动态创建，用完等 v2 清理）─────────────────────

@pytest.fixture(scope="module")
def ach_fp_false_ctx(ach_processing_api):
    """
    ACH Credit fp=False 上下文：(fa, sub, cp)。
    每次模块运行时动态创建一个 ACH CP，assign 到 FA2 的 profile account。
    """
    fa  = ACH_FP_FALSE_FA
    sub = ACH_FP_FALSE_SUB
    profile_aid = _profile_account_id_for_fa(ach_processing_api, fa)
    if not profile_aid:
        profile_aid = ACCOUNT_1_ID

    ts   = int(time.time())
    resp = ach_processing_api.create_counterparty(
        name=f"Auto TestYan ACH Credit CP {ts}",
        type="Company",
        bank_account_type="Checking",
        bank_routing_number="091918450",
        bank_name="Auto TestYan Bank",
        bank_account_owner_name="Auto TestYan Owner",
        bank_account_number=f"9{ts % 10000000:07d}",
        assign_account_ids=[profile_aid],
    )
    cp_id = _cp_id_from_resp(resp, "ACH Credit CP")
    logger.info(f"ACH fp=False Credit: FA={fa}, SUB={sub}, CP={cp_id}, profile={profile_aid}")
    return {"fa": fa, "sub": sub, "cp": cp_id, "profile_account_id": profile_aid}


@pytest.fixture(scope="module")
def ach_debit_fp_false_ctx(ach_processing_api):
    """
    ACH Debit fp=False 上下文：(fa, sub, cp)。
    每次模块运行时动态创建一个 ACH CP，assign 到 Account 1。
    """
    fa  = ACH_DEBIT_FP_FALSE_FA
    sub = ACH_DEBIT_FP_FALSE_SUB
    profile_aid = ACH_DEBIT_PROFILE_ACCOUNT_ID

    ts   = int(time.time())
    resp = ach_processing_api.create_counterparty(
        name=f"Auto TestYan ACH Debit CP {ts}",
        type="Company",
        bank_account_type="Checking",
        bank_routing_number="091918450",
        bank_name="Auto TestYan Debit Bank",
        bank_account_owner_name="Auto TestYan Debit Owner",
        bank_account_number=f"8{ts % 10000000:07d}",
        assign_account_ids=[profile_aid],
    )
    cp_id = _cp_id_from_resp(resp, "ACH Debit CP")
    logger.info(f"ACH fp=False Debit: FA={fa}, SUB={sub}, CP={cp_id}, profile={profile_aid}")
    return {"fa": fa, "sub": sub, "cp": cp_id, "profile_account_id": profile_aid}


@pytest.fixture(scope="module")
def ach_processing_api(login_session):
    return ACHProcessingAPI(session=login_session)
