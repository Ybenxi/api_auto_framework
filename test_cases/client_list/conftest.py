"""
Client List 模块配置
提供 ClientListAPI fixture 和获取 account_id 的辅助 fixture

已验证的测试数据（dev actc 环境）：
  account_id: 251212054048267357 （有持仓数据，settled transactions 可查）
  证券数据：
    PEG  (Common Stock)    security_id: 1716455162056W2Hhd
    SYK  (Common Stock)    security_id: 17152871457341FiHf
    BTC  (Crypto Currency) security_id: a71a11117a510v0v5L
    DEMSX (Mutual Funds)   security_id: a0A5f00000NrxT5EAJ
  注：account_id 241119172641010686 对当前 token 不可见（506），暂不使用
"""
import pytest
from api.client_list_api import ClientListAPI

pytestmark = pytest.mark.client_list

# 已验证有持仓数据的 account_id（dev actc 环境）
VERIFIED_ACCOUNT_ID = "251212054048267357"


@pytest.fixture(scope="module")
def client_list_api(login_session):
    """Client List / Investment Positions API 实例"""
    return ClientListAPI(session=login_session)


@pytest.fixture(scope="module")
def real_account_id(login_session):
    """
    返回已验证有投资数据的 account_id。
    优先使用固定已验证的 account_id，避免每次动态查找。
    """
    return VERIFIED_ACCOUNT_ID
