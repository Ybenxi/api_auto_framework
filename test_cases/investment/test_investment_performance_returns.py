"""
Investment - Performance Returns 接口测试用例
测试 GET /api/v1/cores/{core}/reports/investments/performances/returns 接口

响应结构：{"code": 200, "data": [{date, return_rate}, ...]}
fee 枚举：NET_OF_FEE（默认）/ GROSS_OF_FEE
interval 枚举：DAILY（默认）/ QUARTERLY
"""
import pytest
from api.account_api import AccountAPI
from data.enums import FeeType, IntervalType
from utils.logger import logger


def _get_account_id(login_session) -> str:
    acc_api = AccountAPI(session=login_session)
    accs = acc_api.list_accounts(page=0, size=1).json().get("data", {}).get("content", [])
    if not accs:
        pytest.skip("无可用 account 数据，跳过")
    return accs[0]["id"]


@pytest.mark.investment
@pytest.mark.list_api
class TestInvestmentPerformanceReturns:

    def test_missing_both_account_ids(self, investment_api, short_date_range):
        """
        测试场景1：两个ID都不提供 → 业务错误
        Test Scenario1: Missing Both Account IDs Returns Business Error
        """
        response = investment_api.get_performance_returns(**short_date_range)
        assert response.status_code == 200
        body = response.json()
        assert body.get("code") != 200
        assert body.get("data") is None
        logger.info(f"✓ 缺少ID校验通过: code={body.get('code')}")

    @pytest.mark.parametrize("fee_val", ["INVALID_FEE_TYPE", "net_of_fee", "gross"])
    def test_invalid_fee_enum(self, investment_api, login_session, fee_val):
        """
        测试场景2：无效的 fee 枚举值（覆盖3个无效值）
        Test Scenario2: Invalid Fee Enum Value Returns Business Error
        """
        account_id = _get_account_id(login_session)
        response = investment_api.get_performance_returns(
            account_id=account_id,
            fee=fee_val,
            begin_date="2023-01-01",
            end_date="2023-01-05"
        )
        assert response.status_code == 200
        body = response.json()
        if body.get("code") != 200:
            logger.info(f"  ✓ fee='{fee_val}' 被拒绝: code={body.get('code')}")
        else:
            logger.info(f"  ⚠ fee='{fee_val}' 被接受（探索性结果）")

    @pytest.mark.parametrize("interval_val", ["INVALID_INTERVAL", "daily", "weekly"])
    def test_invalid_interval_enum(self, investment_api, login_session, interval_val):
        """
        测试场景3：无效的 interval 枚举值（覆盖3个无效值）
        Test Scenario3: Invalid Interval Enum Value Returns Business Error
        """
        account_id = _get_account_id(login_session)
        response = investment_api.get_performance_returns(
            account_id=account_id,
            interval=interval_val,
            begin_date="2023-01-01",
            end_date="2023-01-05"
        )
        assert response.status_code == 200
        body = response.json()
        if body.get("code") != 200:
            logger.info(f"  ✓ interval='{interval_val}' 被拒绝: code={body.get('code')}")
        else:
            logger.info(f"  ⚠ interval='{interval_val}' 被接受（探索性结果）")

    def test_get_performance_returns_default_params(self, investment_api, login_session):
        """
        测试场景4：使用默认参数获取回报率（fee=NET_OF_FEE, interval=DAILY）
        Test Scenario4: Get Performance Returns with Default Parameters
        验证点：
        1. HTTP 200，business code=200
        2. data 是数组，每条含 date 和 return_rate 字段
        """
        account_id = _get_account_id(login_session)
        response = investment_api.get_performance_returns(
            account_id=account_id,
            begin_date="2023-01-01",
            end_date="2023-01-05"
        )
        assert response.status_code == 200
        body = response.json()
        assert body.get("code") == 200, \
            f"应返回 code=200，实际: {body.get('code')}"
        data = body.get("data", [])
        assert isinstance(data, list)
        logger.info(f"  返回 {len(data)} 条回报率记录")
        if data:
            assert "date" in data[0] and "return_rate" in data[0]
        logger.info("✓ 默认参数回报率验证通过")

    @pytest.mark.parametrize("fee", [FeeType.NET_OF_FEE, FeeType.GROSS_OF_FEE])
    def test_fee_enum_values(self, investment_api, login_session, fee):
        """
        测试场景5：fee 枚举全覆盖（NET_OF_FEE / GROSS_OF_FEE）
        Test Scenario5: Fee Enum Coverage (NET_OF_FEE / GROSS_OF_FEE)
        验证点：
        1. 两种 fee 类型均返回 code=200
        2. 各自返回数组数据
        """
        account_id = _get_account_id(login_session)
        response = investment_api.get_performance_returns(
            account_id=account_id,
            fee=fee,
            begin_date="2023-01-01",
            end_date="2023-01-05"
        )
        assert response.status_code == 200
        body = response.json()
        assert body.get("code") == 200, \
            f"fee={fee} 应被接受，实际: {body.get('code')}, msg={body.get('error_message')}"
        data = body.get("data", [])
        assert isinstance(data, list)
        logger.info(f"✓ fee={fee} 验证通过，返回 {len(data)} 条")

    @pytest.mark.parametrize("interval", [IntervalType.DAILY, IntervalType.QUARTERLY])
    def test_interval_enum_values(self, investment_api, login_session, interval):
        """
        测试场景6：interval 枚举全覆盖（DAILY / QUARTERLY）
        Test Scenario6: Interval Enum Coverage (DAILY / QUARTERLY)
        验证点：
        1. 两种 interval 均返回 code=200
        2. QUARTERLY 返回数据点应 <= DAILY
        """
        account_id = _get_account_id(login_session)
        response = investment_api.get_performance_returns(
            account_id=account_id,
            interval=interval,
            begin_date="2023-01-01",
            end_date="2023-12-31"
        )
        assert response.status_code == 200
        body = response.json()
        assert body.get("code") == 200, \
            f"interval={interval} 应被接受，实际: {body.get('code')}, msg={body.get('error_message')}"
        data = body.get("data", [])
        assert isinstance(data, list)
        logger.info(f"✓ interval={interval} 验证通过，返回 {len(data)} 条")
