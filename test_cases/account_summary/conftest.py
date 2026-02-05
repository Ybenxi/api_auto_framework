import pytest
from api.account_summary_api import AccountSummaryAPI

pytestmark = pytest.mark.account_summary


@pytest.fixture(scope="module")
def account_summary_api(login_session):
    """
    Account Summary API fixture
    提供 AccountSummaryAPI 实例供测试使用
    """
    return AccountSummaryAPI(session=login_session)
