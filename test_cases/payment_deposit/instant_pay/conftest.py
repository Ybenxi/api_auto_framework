import pytest
from api.instant_pay_api import InstantPayAPI

pytestmark = pytest.mark.instant_pay


@pytest.fixture(scope="module")
def instant_pay_api(login_session):
    """
    Instant Pay API fixture
    提供 InstantPayAPI 实例供测试使用
    """
    return InstantPayAPI(session=login_session)
