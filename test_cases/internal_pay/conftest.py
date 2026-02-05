import pytest
from api.internal_pay_api import InternalPayAPI

pytestmark = pytest.mark.internal_pay


@pytest.fixture(scope="module")
def internal_pay_api(login_session):
    """
    Internal Pay API fixture
    提供 InternalPayAPI 实例供测试使用
    """
    return InternalPayAPI(session=login_session)
