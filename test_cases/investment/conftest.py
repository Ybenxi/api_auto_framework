import pytest
from api.investment_api import InvestmentAPI

pytestmark = pytest.mark.investment


@pytest.fixture(scope="module")
def investment_api(login_session):
    """
    Investment API fixture
    提供 InvestmentAPI 实例供测试使用
    """
    return InvestmentAPI(session=login_session)


@pytest.fixture
def valid_date_range():
    """
    提供有效的日期范围
    用于测试的标准日期范围
    """
    return {
        "begin_date": "2024-01-01",
        "end_date": "2024-01-31"
    }


@pytest.fixture
def short_date_range():
    """
    提供短日期范围
    用于快速测试，减少响应数据量
    """
    return {
        "begin_date": "2024-01-01",
        "end_date": "2024-01-03"
    }
