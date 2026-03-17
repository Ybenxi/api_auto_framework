"""
Investment - Performance Returns 接口测试用例
测试 GET /api/v1/cores/{core}/reports/investments/performances/returns 接口
"""
import pytest
from utils.logger import logger
from utils.assertions import assert_status_ok
from data.enums import FeeType, IntervalType


@pytest.mark.investment
@pytest.mark.list_api
class TestInvestmentPerformanceReturns:
    """
    绩效回报率接口测试用例集
    支持 fee 和 interval 参数
    ⚠️ 业务规则：必须提供 account_id 或 financial_account_id 之一
    """

    def test_missing_both_account_ids(self, investment_api, short_date_range):
        """
        测试场景1：两个ID都不提供 → 业务错误
        验证点：
        1. 接口返回 HTTP 200（统一错误处理）
        2. 业务 code != 200
        3. data 为 null
        """
        logger.info("测试场景1：两个ID都不提供")

        response = investment_api.get_performance_returns(**short_date_range)

        assert response.status_code == 200
        response_body = response.json()
        logger.info(f"  响应: {response_body}")

        assert response_body.get("code") != 200, \
            "不提供ID应返回业务错误码，但返回了 code=200"
        assert response_body.get("data") is None

        logger.info(f"✓ 缺少必需参数校验通过，code={response_body.get('code')}")

    def test_invalid_fee_enum(self, investment_api, short_date_range):
        """
        测试场景2：无效的 fee 枚举值
        验证点：
        1. 接口返回 HTTP 200
        2. 业务 code != 200（枚举校验失败）或忽略无效参数（继续返回错误，因为无ID）
        """
        logger.info("测试场景2：无效的 fee 枚举值")

        response = investment_api.get_performance_returns(
            fee="INVALID_FEE_TYPE",
            **short_date_range
        )

        assert response.status_code == 200
        response_body = response.json()
        logger.info(f"  响应: {response_body}")

        # 无论是因为无效 fee 还是缺少 ID，code 都不应为 200
        assert response_body.get("code") != 200, \
            "无效 fee + 无ID应返回业务错误码，但返回了 code=200"

        logger.info(f"✓ 无效 fee 枚举值测试通过，code={response_body.get('code')}")

    def test_invalid_interval_enum(self, investment_api, short_date_range):
        """
        测试场景3：无效的 interval 枚举值
        验证点：
        1. 接口返回 HTTP 200
        2. 业务 code != 200
        """
        logger.info("测试场景3：无效的 interval 枚举值")

        response = investment_api.get_performance_returns(
            interval="INVALID_INTERVAL",
            **short_date_range
        )

        assert response.status_code == 200
        response_body = response.json()
        logger.info(f"  响应: {response_body}")

        assert response_body.get("code") != 200, \
            "无效 interval + 无ID应返回业务错误码，但返回了 code=200"

        logger.info(f"✓ 无效 interval 枚举值测试通过，code={response_body.get('code')}")

    @pytest.mark.skip(reason="需要真实 financial_account_id 且该账户须有投资数据")
    def test_get_performance_returns_default(self, investment_api, short_date_range):
        """
        测试场景4：成功获取回报率（默认参数，需要真实数据）
        验证点：
        1. 接口返回 200，业务 code=200
        2. 返回数组结构，包含 date 和 return_rate 字段
        """
        logger.info("测试场景4：成功获取回报率（默认参数）")

        response = investment_api.get_performance_returns(
            financial_account_id="<替换为真实FA ID>",
            **short_date_range
        )

        assert_status_ok(response)

        returns = response.json()
        assert isinstance(returns, list), "响应应为数组"

        if returns:
            assert "date" in returns[0]
            assert "return_rate" in returns[0]

        logger.info(f"✓ 回报率数据获取成功，返回 {len(returns)} 条记录")

    @pytest.mark.skip(reason="需要真实数据，验证 NET_OF_FEE 参数")
    def test_with_net_of_fee(self, investment_api, short_date_range):
        """
        测试场景5：使用 NET_OF_FEE 参数（需要真实数据）
        验证点：
        1. 接口返回 200，业务 code=200
        2. fee 参数正确传递
        """
        logger.info("测试场景5：使用 NET_OF_FEE 参数")

        response = investment_api.get_performance_returns(
            financial_account_id="<替换为真实FA ID>",
            fee=FeeType.NET_OF_FEE,
            **short_date_range
        )

        assert_status_ok(response)
        logger.info("✓ NET_OF_FEE 参数验证通过")

    @pytest.mark.skip(reason="需要真实数据，验证 GROSS_OF_FEE 参数")
    def test_with_gross_of_fee(self, investment_api, short_date_range):
        """
        测试场景6：使用 GROSS_OF_FEE 参数（需要真实数据）
        验证点：
        1. 接口返回 200，业务 code=200
        2. 费用计算方式不同可能影响回报率
        """
        logger.info("测试场景6：使用 GROSS_OF_FEE 参数")

        response = investment_api.get_performance_returns(
            financial_account_id="<替换为真实FA ID>",
            fee=FeeType.GROSS_OF_FEE,
            **short_date_range
        )

        assert_status_ok(response)
        logger.info("✓ GROSS_OF_FEE 参数验证通过")

    @pytest.mark.skip(reason="需要真实数据，验证 DAILY 间隔")
    def test_with_daily_interval(self, investment_api, short_date_range):
        """
        测试场景7：使用 DAILY 间隔（需要真实数据）
        验证点：
        1. 接口返回 200，业务 code=200
        2. 返回每日数据
        """
        logger.info("测试场景7：使用 DAILY 间隔")

        response = investment_api.get_performance_returns(
            financial_account_id="<替换为真实FA ID>",
            interval=IntervalType.DAILY,
            **short_date_range
        )

        assert_status_ok(response)
        returns = response.json()
        logger.info(f"✓ DAILY 间隔数据获取成功，返回 {len(returns)} 条记录")

    @pytest.mark.skip(reason="需要真实数据，验证 QUARTERLY 间隔")
    def test_with_quarterly_interval(self, investment_api):
        """
        测试场景8：使用 QUARTERLY 间隔（需要真实数据）
        验证点：
        1. 接口返回 200，业务 code=200
        2. 返回季度数据，数据点数量应更少
        """
        logger.info("测试场景8：使用 QUARTERLY 间隔")

        response = investment_api.get_performance_returns(
            financial_account_id="<替换为真实FA ID>",
            interval=IntervalType.QUARTERLY,
            begin_date="2023-01-01",
            end_date="2023-12-31"
        )

        assert_status_ok(response)
        returns = response.json()
        logger.info(f"✓ QUARTERLY 间隔数据获取成功，返回 {len(returns)} 条季度记录")
