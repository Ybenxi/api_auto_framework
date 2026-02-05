import pytest
from api.wire_processing_api import WireProcessingAPI

pytestmark = pytest.mark.wire_processing


@pytest.fixture(scope="module")
def wire_processing_api(login_session):
    """
    Wire Processing API fixture
    提供 WireProcessingAPI 实例供测试使用
    """
    return WireProcessingAPI(session=login_session)
