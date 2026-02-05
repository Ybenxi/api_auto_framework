import pytest
from api.card_dispute_api import CardDisputeAPI

pytestmark = pytest.mark.card_dispute_risk


@pytest.fixture(scope="module")
def card_dispute_api(login_session):
    """
    Card Dispute API fixture
    提供 CardDisputeAPI 实例供测试使用
    """
    return CardDisputeAPI(session=login_session)
