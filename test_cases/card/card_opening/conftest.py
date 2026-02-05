import pytest
from api.card_opening_api import CardOpeningAPI

pytestmark = pytest.mark.card_opening


@pytest.fixture(scope="module")
def card_opening_api(login_session):
    """
    Card Opening API fixture
    提供 CardOpeningAPI 实例供测试使用
    """
    return CardOpeningAPI(session=login_session)
