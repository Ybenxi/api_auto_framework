"""
Counterparty 模块级配置
可在此添加模块特定的 fixture 或配置
"""
import pytest
from api.counterparty_api import CounterpartyAPI


# 模块级 marker，自动应用到该目录下所有测试
pytestmark = pytest.mark.counterparty


@pytest.fixture
def counterparty_api(login_session):
    """
    Counterparty 模块专用的 CounterpartyAPI 实例
    复用全局 login_session，避免在每个用例中重复初始化
    """
    return CounterpartyAPI(session=login_session)
