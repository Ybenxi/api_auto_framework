import pytest
import time
from api.wire_processing_api import WireProcessingAPI
from test_cases.test_ids import ACCOUNT_1_ID
from utils.logger import logger

pytestmark = pytest.mark.wire_processing

# 固定 Wire 路由号（真实可用）
WIRE_ROUTING = "091918450"
# 有效 SWIFT（8 位或 11 位字母数字）
WIRE_SWIFT   = "CRBKUS33XXX"


def _cp_id_from_resp(resp, name: str) -> str:
    if resp.status_code != 200:
        pytest.fail(f"创建 {name} 失败: HTTP {resp.status_code}\n{resp.text[:300]}")
    body = resp.json()
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


@pytest.fixture(scope="module")
def wire_cp_id(wire_processing_api):
    """
    模块级别动态创建 Wire 类型 CP，assign 到 Account 1。
    用完后由 v2 清理方案覆盖（CP 绑在 Account 1 下）。
    """
    ts   = int(time.time())
    resp = wire_processing_api.create_counterparty(
        name=f"Auto TestYan Wire CP {ts}",
        type="Company",
        bank_account_type="Checking",
        bank_account_owner_name="Auto TestYan Wire Owner",
        bank_account_number=f"7{ts % 10000000:07d}",
        payment_type="Wire",
        bank_routing_number=WIRE_ROUTING,
        bank_name="Auto TestYan Wire Bank",
        bank_city="Test City",
        bank_state="CA",
        assign_account_ids=[ACCOUNT_1_ID],
    )
    return _cp_id_from_resp(resp, "Wire CP")


@pytest.fixture(scope="module")
def intl_wire_cp_id(wire_processing_api):
    """
    模块级别动态创建 International_Wire 类型 CP，assign 到 Account 1。
    """
    ts   = int(time.time())
    resp = wire_processing_api.create_counterparty(
        name=f"Auto TestYan IntlWire CP {ts}",
        type="Company",
        bank_account_type="Checking",
        bank_account_owner_name="Auto TestYan Intl Owner",
        bank_account_number=f"6{ts % 10000000:07d}",
        payment_type="International_Wire",
        country="US",
        address1="123 Test Blvd",
        city="New York",
        state="NY",
        zip_code="10001",
        bank_name="Auto TestYan Intl Bank",
        bank_address="456 Bank Ave",
        bank_city="New York",
        bank_state="NY",
        bank_zip_code="10002",
        bank_country="US",
        swift_code=WIRE_SWIFT,
        assign_account_ids=[ACCOUNT_1_ID],
    )
    return _cp_id_from_resp(resp, "IntlWire CP")


@pytest.fixture(scope="module")
def wire_processing_api(login_session):
    return WireProcessingAPI(session=login_session)
