"""
Profile Account 模块级配置
可在此添加模块特定的 fixture 或配置
"""
import pytest
from api.account_api import AccountAPI


# 模块级 marker，自动应用到该目录下所有测试
pytestmark = pytest.mark.profile_account


@pytest.fixture
def account_api(login_session):
    """
    Profile Account 模块专用的 AccountAPI 实例
    复用全局 login_session，避免在每个用例中重复初始化
    """
    return AccountAPI(session=login_session)
