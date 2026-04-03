import pytest
import time
from api.instant_pay_api import InstantPayAPI
from test_cases.test_ids import ACCOUNT_1_ID
from utils.logger import logger

pytestmark = pytest.mark.instant_pay

IP_ROUTING = "091918450"


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
def ip_cp_id(instant_pay_api):
    """
    模块级别动态创建 Instant Pay CP，assign 到 Account 1。
    """
    ts   = int(time.time())
    resp = instant_pay_api.create_counterparty(
        name=f"Auto TestYan IP CP {ts}",
        type="Company",
        bank_account_type="Checking",
        bank_routing_number=IP_ROUTING,
        bank_name="Auto TestYan IP Bank",
        bank_account_owner_name="Auto TestYan IP Owner",
        bank_account_number=f"5{ts % 10000000:07d}",
        assign_account_ids=[ACCOUNT_1_ID],
    )
    return _cp_id_from_resp(resp, "Instant Pay CP")


@pytest.fixture(scope="module")
def instant_pay_api(login_session):
    return InstantPayAPI(session=login_session)
