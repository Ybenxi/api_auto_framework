"""
Client List 模块配置
提供 ClientListAPI fixture 和获取 account_id 的辅助 fixture
"""
import pytest
from api.client_list_api import ClientListAPI
from api.account_api import AccountAPI

pytestmark = pytest.mark.client_list


@pytest.fixture(scope="module")
def client_list_api(login_session):
    """Client List / Investment Positions API 实例"""
    return ClientListAPI(session=login_session)


@pytest.fixture(scope="module")
def real_account_id(login_session):
    """从 list_accounts 动态获取真实 account_id，供持仓接口使用"""
    acc_api = AccountAPI(session=login_session)
    accs = acc_api.list_accounts(page=0, size=1).json().get("data", {}).get("content", [])
    if not accs:
        return None
    return accs[0]["id"]
