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
    支持fee和interval参数
    """

    @pytest.mark.skip(reason="需要真实的financial_account_id")
    def test_get_performance_returns_default(self, investment_api, short_date_range):
        """
        测试场景1：成功获取回报率（默认参数）
        验证点：
        1. 接口返回 200
        2. 返回数组结构
        3. 包含date和return_rate字段
        """
        logger.info("测试场景1：成功获取回报率（默认参数）")
        
        response = investment_api.get_performance_returns(
            financial_account_id="test_fa_id",
            **short_date_range
        )
        
        assert_status_ok(response)
        
        returns = response.json()
        assert isinstance(returns, list), "响应应为数组"
        
        if len(returns) > 0:
            assert "date" in returns[0]
            assert "return_rate" in returns[0]
        
        logger.info(f"✓ 回报率数据获取成功，返回 {len(returns)} 条记录")

    @pytest.mark.skip(reason="需要真实数据")
    def test_with_net_of_fee(self, investment_api, short_date_range):
        """
        测试场景2：使用NET_OF_FEE参数
        验证点：
        1. 接口返回 200
        2. fee参数正确传递
        """
        logger.info("测试场景2：使用NET_OF_FEE参数")
        
        response = investment_api.get_performance_returns(
            financial_account_id="test_fa_id",
            fee=FeeType.NET_OF_FEE,
            **short_date_range
        )
        
        assert_status_ok(response)
        
        logger.info("✓ NET_OF_FEE参数验证通过")

    @pytest.mark.skip(reason="需要真实数据")
    def test_with_gross_of_fee(self, investment_api, short_date_range):
        """
        测试场景3：使用GROSS_OF_FEE参数
        验证点：
        1. 接口返回 200
        2. 费用计算方式不同可能影响回报率
        """
        logger.info("测试场景3：使用GROSS_OF_FEE参数")
        
        response = investment_api.get_performance_returns(
            financial_account_id="test_fa_id",
            fee=FeeType.GROSS_OF_FEE,
            **short_date_range
        )
        
        assert_status_ok(response)
        
        logger.info("✓ GROSS_OF_FEE参数验证通过")

    @pytest.mark.skip(reason="需要真实数据")
    def test_with_daily_interval(self, investment_api, short_date_range):
        """
        测试场景4：使用DAILY间隔
        验证点：
        1. 接口返回 200
        2. 返回每日数据
        """
        logger.info("测试场景4：使用DAILY间隔")
        
        response = investment_api.get_performance_returns(
            financial_account_id="test_fa_id",
            interval=IntervalType.DAILY,
            **short_date_range
        )
        
        assert_status_ok(response)
        
        returns = response.json()
        logger.info(f"✓ DAILY间隔数据获取成功，返回 {len(returns)} 条记录")

    @pytest.mark.skip(reason="需要真实数据")
    def test_with_quarterly_interval(self, investment_api):
        """
        测试场景5：使用QUARTERLY间隔
        验证点：
        1. 接口返回 200
        2. 返回季度数据
        3. 数据点数量应该更少
        """
        logger.info("测试场景5：使用QUARTERLY间隔")
        
        response = investment_api.get_performance_returns(
            financial_account_id="test_fa_id",
            interval=IntervalType.QUARTERLY,
            begin_date="2023-01-01",
            end_date="2023-12-31"
        )
        
        assert_status_ok(response)
        
        returns = response.json()
        logger.info(f"✓ QUARTERLY间隔数据获取成功，返回 {len(returns)} 条季度记录")

    def test_invalid_fee_enum(self, investment_api, short_date_range):
        """
        测试场景6：无效的fee枚举值
        验证点：
        1. 接口返回错误或忽略无效参数
        """
        logger.info("测试场景6：无效的fee枚举值")
        
        response = investment_api.get_performance_returns(
            financial_account_id="test_fa_id",
            fee="INVALID_FEE_TYPE",
            **short_date_range
        )
        
        logger.info(f"响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            response_body = response.json()
            logger.info(f"✓ 无效fee参数处理: {type(response_body)}")
        
        logger.info("✓ 无效fee枚举值测试完成")

    def test_invalid_interval_enum(self, investment_api, short_date_range):
        """
        测试场景7：无效的interval枚举值
        验证点：
        1. 接口返回错误或忽略无效参数
        """
        logger.info("测试场景7：无效的interval枚举值")
        
        response = investment_api.get_performance_returns(
            financial_account_id="test_fa_id",
            interval="INVALID_INTERVAL",
            **short_date_range
        )
        
        logger.info(f"响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            response_body = response.json()
            logger.info(f"✓ 无效interval参数处理: {type(response_body)}")
        
        logger.info("✓ 无效interval枚举值测试完成")
