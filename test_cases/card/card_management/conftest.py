import pytest
from api.card_management_api import CardManagementAPI

pytestmark = pytest.mark.card_management


@pytest.fixture(scope="module")
def card_management_api(login_session):
    """
    Card Management API fixture
    提供 CardManagementAPI 实例供测试使用
    """
    return CardManagementAPI(session=login_session)
