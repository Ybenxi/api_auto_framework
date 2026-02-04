"""
Identity Security 模块级配置
可在此添加模块特定的 fixture 或配置
"""
import pytest
from api.identity_security_api import IdentitySecurityAPI


# 模块级 marker，自动应用到该目录下所有测试
pytestmark = pytest.mark.identity_security


@pytest.fixture
def identity_api(login_session):
    """
    Identity Security 模块专用的 IdentitySecurityAPI 实例
    复用全局 login_session，避免在每个用例中重复初始化
    """
    return IdentitySecurityAPI(session=login_session)
