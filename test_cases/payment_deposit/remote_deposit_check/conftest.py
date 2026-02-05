import pytest
from api.remote_deposit_check_api import RemoteDepositCheckAPI

pytestmark = pytest.mark.remote_deposit_check


@pytest.fixture(scope="module")
def remote_deposit_check_api(login_session):
    """
    Remote Deposit Check API fixture
    提供 RemoteDepositCheckAPI 实例供测试使用
    """
    return RemoteDepositCheckAPI(session=login_session)
