"""
Account Opening 模块级配置
可在此添加模块特定的 fixture 或配置
"""
import pytest
from api.account_opening_api import AccountOpeningAPI


# 模块级 marker，自动应用到该目录下所有测试
pytestmark = pytest.mark.account_opening


@pytest.fixture
def account_opening_api(login_session):
    """
    Account Opening 模块专用的 AccountOpeningAPI 实例
    复用全局 login_session，避免在每个用例中重复初始化
    """
    return AccountOpeningAPI(session=login_session)


# 测试数据常量
# 加密的 SSN（用于个人申请）
ENCRYPTED_SSN = "iNxrXqIadmqyYIXQib4p77f7LcbrXDCWbx3sMHwvL2jLZa4gaXesvfPPwpr1V5coAdncmGk4UoDBUI5MH01sZCRs8TDDnJBg68MqKpJ+h3lAYvUUaS6l2KaoSeDWh75vOoQoNZE5deL98z9THHI3l/oXZdDW1FK3f8SVIBCK8DkrBLkLDPNgJfbbwHaHdRrjyKCM8tqmMKMYJCAZMRLHQtUeflqaiuKUbWyib7NhIzWZP7Q6ZN2XXQOwn8QzqGLKMa3FN2ftAXUm4PFM9JGLdPluj7z5owxLAKM8pu4th2lIQwR7IeHtT1+Q4WSMO2YDYu+vdw4sQGt9g8drgMipAQ=="
