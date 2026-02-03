"""
FBO Account 模块级配置
可在此添加模块特定的 fixture 或配置
"""
import pytest
from api.fbo_account_api import FboAccountAPI


# 模块级 marker，自动应用到该目录下所有测试
pytestmark = pytest.mark.fbo_account


@pytest.fixture
def fbo_account_api(login_session):
    """
    FBO Account 模块专用的 FboAccountAPI 实例
    复用全局 login_session，避免在每个用例中重复初始化
    """
    return FboAccountAPI(session=login_session)
