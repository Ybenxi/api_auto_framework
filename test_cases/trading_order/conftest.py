import pytest
from api.trading_order_api import TradingOrderAPI

pytestmark = pytest.mark.trading_order


@pytest.fixture(scope="module")
def trading_order_api(login_session):
    """
    Trading Order API fixture
    提供 TradingOrderAPI 实例供测试使用
    """
    return TradingOrderAPI(session=login_session)
