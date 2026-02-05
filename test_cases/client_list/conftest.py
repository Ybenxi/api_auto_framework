import pytest
from api.client_list_api import ClientListAPI

pytestmark = pytest.mark.client_list


@pytest.fixture(scope="module")
def client_list_api(login_session):
    """
    Client List API fixture
    提供 ClientListAPI 实例供测试使用
    """
    return ClientListAPI(session=login_session)
