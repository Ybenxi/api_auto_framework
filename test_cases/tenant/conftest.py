"""
Tenant 模块级配置
可在此添加模块特定的 fixture 或配置
"""
import pytest
from api.tenant_api import TenantAPI


# 模块级 marker，自动应用到该目录下所有测试
pytestmark = pytest.mark.tenant


@pytest.fixture
def tenant_api(login_session):
    """
    Tenant 模块专用的 TenantAPI 实例
    复用全局 login_session，避免在每个用例中重复初始化
    """
    return TenantAPI(session=login_session)
