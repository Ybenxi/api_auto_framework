import pytest
from api.ach_processing_api import ACHProcessingAPI

pytestmark = pytest.mark.ach_processing


@pytest.fixture(scope="module")
def ach_processing_api(login_session):
    """
    ACH Processing API fixture
    提供 ACHProcessingAPI 实例供测试使用
    """
    return ACHProcessingAPI(session=login_session)
