import pytest
from api.user_signup_api import UserSignUpAPI

pytestmark = pytest.mark.user_signup


@pytest.fixture(scope="module")
def user_signup_api():
    """
    User Sign Up API fixture
    提供 UserSignUpAPI 实例供测试使用
    
    Note:
        ⚠️ 此模块需要Client-Id，从环境变量或配置获取
        暂时使用测试Client-Id
    """
    test_client_id = "test_client_id_12345"
    return UserSignUpAPI(client_id=test_client_id)
