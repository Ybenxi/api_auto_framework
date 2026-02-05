import pytest
from api.account_transfer_api import AccountTransferAPI

pytestmark = pytest.mark.account_transfer


@pytest.fixture(scope="module")
def account_transfer_api(login_session):
    """
    Account Transfer API fixture
    提供 AccountTransferAPI 实例供测试使用
    """
    return AccountTransferAPI(session=login_session)
