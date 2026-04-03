import pytest
import time
from api.remote_deposit_check_api import RemoteDepositCheckAPI
from test_cases.test_ids import ACCOUNT_1_ID
from utils.logger import logger

pytestmark = pytest.mark.remote_deposit_check


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
def check_cp_id(remote_deposit_check_api):
    """
    模块级别动态创建 Check CP，assign 到 Account 1。
    """
    ts   = int(time.time())
    resp = remote_deposit_check_api.create_counterparty(
        name=f"Auto TestYan Check CP {ts}",
        type="Company",
        address1="123 Auto TestYan Check Street",
        assign_account_ids=[ACCOUNT_1_ID],
    )
    return _cp_id_from_resp(resp, "Check CP")


@pytest.fixture(scope="module")
def remote_deposit_check_api(login_session):
    return RemoteDepositCheckAPI(session=login_session)
