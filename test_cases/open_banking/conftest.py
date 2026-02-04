"""
Open Banking 模块的 Pytest 配置
自动为该目录下的所有测试用例添加 open_banking marker
"""
import pytest
from api.open_banking_api import OpenBankingAPI


pytestmark = pytest.mark.open_banking


@pytest.fixture
def open_banking_api(login_session):
    """
    Open Banking API 对象 fixture
    
    Args:
        login_session: 已登录的 session
        
    Returns:
        OpenBankingAPI: 初始化好的 Open Banking API 对象
    """
    return OpenBankingAPI(session=login_session)
