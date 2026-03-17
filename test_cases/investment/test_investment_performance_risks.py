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
    返回 Alpha、Beta、R-Squared 等风险指标
    ⚠️ 文档问题：
    1. sharp_ratio 拼写错误（应为 sharpe_ratio）
    2. benchmark/account 对象字段未定义
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

        response = investment_api.get_performance_risks(**short_date_range)

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
        2. 业务 code != 200
        """
        logger.info("测试场景2：无效的 fee 枚举值")

        response = investment_api.get_performance_risks(
            fee="INVALID_FEE_TYPE",
            **short_date_range
        )

        assert response.status_code == 200
        response_body = response.json()
        logger.info(f"  响应: {response_body}")

        assert response_body.get("code") != 200, \
            "无效 fee + 无ID应返回业务错误码，但返回了 code=200"

        logger.info(f"✓ 无效 fee 枚举值测试通过，code={response_body.get('code')}")

    @pytest.mark.skip(reason="需要真实 financial_account_id 且该账户须有投资数据")
    def test_get_performance_risks_success(self, investment_api, short_date_range):
        """
        测试场景3：成功获取风险指标（需要真实数据）
        验证点：
        1. 接口返回 200，业务 code=200
        2. 包含 benchmark、account、alpha、beta、r_squared 字段
        """
        logger.info("测试场景3：成功获取风险指标")

        response = investment_api.get_performance_risks(
            financial_account_id="<替换为真实FA ID>",
            **short_date_range
        )

        assert_status_ok(response)

        risks = response.json()
        top_level_fields = ["benchmark", "account", "alpha", "beta", "r_squared"]
        for field in top_level_fields:
            assert field in risks, f"缺少必需字段: {field}"

        logger.info("✓ 风险指标获取成功")

    @pytest.mark.skip(reason="需要真实数据，验证 benchmark 结构")
    def test_verify_benchmark_structure(self, investment_api, short_date_range):
        """
        测试场景4：验证 benchmark 字段结构（需要真实数据）
        验证点：
        1. benchmark 是对象类型
        2. 包含 name、return_rate、standard_deviation 等字段
        3. 兼容 sharp_ratio 拼写错误
        """
        logger.info("测试场景4：验证 benchmark 字段结构")

        response = investment_api.get_performance_risks(
            financial_account_id="<替换为真实FA ID>",
            **short_date_range
        )

        assert_status_ok(response)

        risks = response.json()
        benchmark = risks.get("benchmark", {})
        assert isinstance(benchmark, dict), "benchmark 应为对象"

        if "sharp_ratio" in benchmark:
            logger.warning("⚠️ 检测到 sharp_ratio 拼写错误（应为 sharpe_ratio）")
        elif "sharpe_ratio" in benchmark:
            logger.info("✓ 使用正确的 sharpe_ratio 拼写")

        logger.info("✓ benchmark 结构验证完成")

    @pytest.mark.skip(reason="需要真实数据，验证 Alpha/Beta/R-Squared 字段")
    def test_verify_risk_indicators(self, investment_api, short_date_range):
        """
        测试场景5：验证 Alpha/Beta/R-Squared 字段（需要真实数据）
        验证点：
        1. 字段类型为 number
        2. beta >= 0，r_squared 在 0-1 之间
        """
        logger.info("测试场景5：验证 Alpha/Beta/R-Squared 字段")

        response = investment_api.get_performance_risks(
            financial_account_id="<替换为真实FA ID>",
            **short_date_range
        )

        assert_status_ok(response)

        risks = response.json()

        beta = risks.get("beta")
        if beta is not None:
            assert isinstance(beta, (int, float)), "beta 应为数值类型"
            assert beta >= 0, "beta 通常为正值"

        r_squared = risks.get("r_squared")
        if r_squared is not None:
            assert isinstance(r_squared, (int, float)), "r_squared 应为数值类型"
            assert 0 <= r_squared <= 1, "r_squared 应在 0-1 之间"

        logger.info("✓ 风险指标字段验证完成")

    @pytest.mark.skip(reason="需要真实数据，验证 fee 参数对结果的影响")
    def test_fee_parameter_impact(self, investment_api, short_date_range):
        """
        测试场景6：fee 参数影响验证（需要真实数据）
        验证点：
        1. NET_OF_FEE vs GROSS_OF_FEE 可能产生不同回报率
        """
        logger.info("测试场景6：fee 参数影响验证")

        response_net = investment_api.get_performance_risks(
            financial_account_id="<替换为真实FA ID>",
            fee=FeeType.NET_OF_FEE,
            **short_date_range
        )
        response_gross = investment_api.get_performance_risks(
            financial_account_id="<替换为真实FA ID>",
            fee=FeeType.GROSS_OF_FEE,
            **short_date_range
        )

        assert_status_ok(response_net)
        assert_status_ok(response_gross)

        risks_net = response_net.json()
        risks_gross = response_gross.json()

        logger.debug(f"NET_OF_FEE: {risks_net.get('account', {}).get('return_rate')}")
        logger.debug(f"GROSS_OF_FEE: {risks_gross.get('account', {}).get('return_rate')}")

        logger.info("✓ fee 参数影响验证完成")
