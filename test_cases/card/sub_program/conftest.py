import pytest
from api.sub_program_api import SubProgramAPI

pytestmark = pytest.mark.sub_program


@pytest.fixture(scope="module")
def sub_program_api(login_session):
    """
    Sub Program API fixture
    提供 SubProgramAPI 实例供测试使用
    """
    return SubProgramAPI(session=login_session)
