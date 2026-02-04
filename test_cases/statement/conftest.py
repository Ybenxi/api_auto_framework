"""
Statement 模块级配置
可在此添加模块特定的 fixture 或配置
"""
import pytest
from api.statement_api import StatementAPI


# 模块级 marker，自动应用到该目录下所有测试
pytestmark = pytest.mark.statement


@pytest.fixture
def statement_api(login_session):
    """
    Statement 模块专用的 StatementAPI 实例
    复用全局 login_session，避免在每个用例中重复初始化
    """
    return StatementAPI(session=login_session)
