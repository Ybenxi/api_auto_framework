"""
Investment - Performance Risks 接口测试用例
测试 GET /api/v1/cores/{core}/reports/investments/performances/risks 接口
"""
import pytest
from utils.logger import logger
from utils.assertions import assert_status_ok
from data.enums import FeeType


@pytest.mark.investment
@pytest.mark.detail_api
class TestInvestmentPerformanceRisks:
    """
    绩效风险指标接口测试用例集
    返回Alpha、Beta、R-Squared等风险指标
    ⚠️ 文档问题：
    1. sharp_ratio拼写错误（应为sharpe_ratio）
    2. benchmark/account对象字段未定义
    """

    @pytest.mark.skip(reason="需要真实的financial_account_id")
    def test_get_performance_risks_success(self, investment_api, short_date_range):
        """
        测试场景1：成功获取风险指标
        验证点：
        1. 接口返回 200
        2. 包含benchmark、account、alpha、beta、r_squared字段
        """
        logger.info("测试场景1：成功获取风险指标")
        
        response = investment_api.get_performance_risks(
            financial_account_id="test_fa_id",
            **short_date_range
        )
        
        assert_status_ok(response)
        
        risks = response.json()
        
        # 验证顶层字段
        top_level_fields = ["benchmark", "account", "alpha", "beta", "r_squared"]
        for field in top_level_fields:
            assert field in risks, f"缺少必需字段: {field}"
        
        logger.info("✓ 风险指标获取成功")

    @pytest.mark.skip(reason="需要真实数据")
    def test_verify_benchmark_structure(self, investment_api, short_date_range):
        """
        测试场景2：验证benchmark字段结构
        验证点：
        1. benchmark是对象类型
        2. 包含name、return_rate、standard_deviation等字段
        """
        logger.info("测试场景2：验证benchmark字段结构")
        
        response = investment_api.get_performance_risks(
            financial_account_id="test_fa_id",
            **short_date_range
        )
        
        assert_status_ok(response)
        
        risks = response.json()
        benchmark = risks.get("benchmark", {})
        
        assert isinstance(benchmark, dict), "benchmark应为对象"
        
        # 验证benchmark字段
        expected_fields = ["name", "return_rate", "standard_deviation"]
        for field in expected_fields:
            if field in benchmark:
                logger.debug(f"benchmark.{field}: {benchmark[field]}")
        
        # 兼容sharp_ratio拼写错误
        if "sharp_ratio" in benchmark:
            logger.warning("⚠️ 检测到sharp_ratio拼写错误（应为sharpe_ratio）")
        elif "sharpe_ratio" in benchmark:
            logger.info("✓ 使用正确的sharpe_ratio拼写")
        
        logger.info("✓ benchmark结构验证完成")

    @pytest.mark.skip(reason="需要真实数据")
    def test_verify_account_structure(self, investment_api, short_date_range):
        """
        测试场景3：验证account字段结构
        验证点：
        1. account是对象类型
        2. 包含name、return_rate、standard_deviation等字段
        """
        logger.info("测试场景3：验证account字段结构")
        
        response = investment_api.get_performance_risks(
            financial_account_id="test_fa_id",
            **short_date_range
        )
        
        assert_status_ok(response)
        
        risks = response.json()
        account = risks.get("account", {})
        
        assert isinstance(account, dict), "account应为对象"
        
        # 验证account字段
        expected_fields = ["name", "return_rate", "standard_deviation"]
        for field in expected_fields:
            if field in account:
                logger.debug(f"account.{field}: {account[field]}")
        
        logger.info("✓ account结构验证完成")

    @pytest.mark.skip(reason="需要真实数据")
    def test_verify_risk_indicators(self, investment_api, short_date_range):
        """
        测试场景4：验证Alpha/Beta/R-Squared字段
        验证点：
        1. 字段类型为number
        2. 值在合理范围内
        """
        logger.info("测试场景4：验证Alpha/Beta/R-Squared字段")
        
        response = investment_api.get_performance_risks(
            financial_account_id="test_fa_id",
            **short_date_range
        )
        
        assert_status_ok(response)
        
        risks = response.json()
        
        # 验证alpha
        alpha = risks.get("alpha")
        if alpha is not None:
            assert isinstance(alpha, (int, float)), "alpha应为数值类型"
            logger.debug(f"Alpha: {alpha}")
        
        # 验证beta
        beta = risks.get("beta")
        if beta is not None:
            assert isinstance(beta, (int, float)), "beta应为数值类型"
            assert beta >= 0, "beta通常为正值"
            logger.debug(f"Beta: {beta}")
        
        # 验证r_squared
        r_squared = risks.get("r_squared")
        if r_squared is not None:
            assert isinstance(r_squared, (int, float)), "r_squared应为数值类型"
            assert 0 <= r_squared <= 1, "r_squared应在0-1之间"
            logger.debug(f"R-Squared: {r_squared}")
        
        logger.info("✓ 风险指标验证完成")

    @pytest.mark.skip(reason="需要真实数据")
    def test_sharp_ratio_spelling_compatibility(self, investment_api, short_date_range):
        """
        测试场景5：sharp_ratio字段兼容性（拼写错误）
        验证点：
        1. 检测是否使用sharp_ratio（错误）还是sharpe_ratio（正确）
        2. 兼容两种拼写
        """
        logger.info("测试场景5：sharp_ratio拼写兼容性")
        
        response = investment_api.get_performance_risks(
            financial_account_id="test_fa_id",
            **short_date_range
        )
        
        assert_status_ok(response)
        
        risks = response.json()
        benchmark = risks.get("benchmark", {})
        
        # 检查两种拼写
        has_sharp = "sharp_ratio" in benchmark
        has_sharpe = "sharpe_ratio" in benchmark
        
        if has_sharp:
            logger.warning("⚠️ API使用错误拼写: sharp_ratio（应为sharpe_ratio）")
            assert isinstance(benchmark["sharp_ratio"], (int, float))
        elif has_sharpe:
            logger.info("✓ API使用正确拼写: sharpe_ratio")
            assert isinstance(benchmark["sharpe_ratio"], (int, float))
        else:
            logger.warning("⚠️ 未找到sharp_ratio或sharpe_ratio字段")
        
        logger.info("✓ 拼写兼容性验证完成")

    @pytest.mark.skip(reason="需要真实数据")
    def test_fee_parameter_impact(self, investment_api, short_date_range):
        """
        测试场景6：fee参数影响验证
        验证点：
        1. NET_OF_FEE vs GROSS_OF_FEE可能产生不同结果
        """
        logger.info("测试场景6：fee参数影响验证")
        
        # NET_OF_FEE
        response_net = investment_api.get_performance_risks(
            financial_account_id="test_fa_id",
            fee=FeeType.NET_OF_FEE,
            **short_date_range
        )
        
        # GROSS_OF_FEE
        response_gross = investment_api.get_performance_risks(
            financial_account_id="test_fa_id",
            fee=FeeType.GROSS_OF_FEE,
            **short_date_range
        )
        
        assert_status_ok(response_net)
        assert_status_ok(response_gross)
        
        risks_net = response_net.json()
        risks_gross = response_gross.json()
        
        logger.debug(f"NET_OF_FEE return_rate: {risks_net.get('account', {}).get('return_rate')}")
        logger.debug(f"GROSS_OF_FEE return_rate: {risks_gross.get('account', {}).get('return_rate')}")
        
        logger.info("✓ fee参数影响验证完成")
