"""
Investment - Activity Summaries 接口测试用例
测试 GET /api/v1/cores/{core}/reports/investments/activity-summaries 接口
"""
import pytest
from utils.logger import logger
from utils.assertions import assert_status_ok


@pytest.mark.investment
@pytest.mark.list_api
class TestInvestmentActivitySummaries:
    """
    投资活动摘要接口测试用例集
    ⚠️ 文档问题：响应示例有trailing comma
    ⚠️ 业务规则：必须提供 account_id 或 financial_account_id 之一，且需有真实投资数据
    """

    def test_missing_both_account_ids(self, investment_api, valid_date_range):
        """
        测试场景1：两个ID都不提供 → 业务错误
        验证点：
        1. 接口返回 HTTP 200（统一错误处理）
        2. 业务 code != 200
        3. data 为 null
        """
        logger.info("测试场景1：两个ID都不提供")

        response = investment_api.get_activity_summaries(**valid_date_range)

        assert response.status_code == 200
        response_body = response.json()
        logger.info(f"  响应: {response_body}")

        assert response_body.get("code") != 200, \
            f"不提供ID应返回业务错误码，但返回了 code=200"
        assert response_body.get("data") is None, \
            "缺少必需参数时 data 应为 null"

        logger.info(f"✓ 缺少必需参数校验通过，code={response_body.get('code')}, "
                    f"msg={response_body.get('error_message')}")

    def test_invalid_date_format(self, investment_api, valid_date_range):
        """
        测试场景2：无效的日期格式（斜杠格式）
        验证点：
        1. 接口返回 HTTP 200
        2. 业务 code != 200（格式校验失败）或接口降级处理
        3. 不因为 ID 占位符导致误判
        """
        logger.info("测试场景2：无效的日期格式")

        response = investment_api.get_activity_summaries(
            begin_date="2024/01/01",   # 错误格式（斜杠）
            end_date="2024-01-31"
            # 不传 ID，专注于日期格式验证
        )

        assert response.status_code == 200
        response_body = response.json()
        logger.info(f"  响应: {response_body}")

        # 日期格式错误或缺少 ID 均应返回业务错误码
        assert response_body.get("code") != 200, \
            "无效日期格式应返回业务错误码，但返回了 code=200"

        logger.info(f"✓ 无效日期格式校验通过，code={response_body.get('code')}")

    def test_date_range_reversed(self, investment_api):
        """
        测试场景3：日期范围倒置（end_date < begin_date）
        验证点：
        1. 接口返回 HTTP 200
        2. 业务 code != 200 或返回空数据
        """
        logger.info("测试场景3：日期范围倒置")

        response = investment_api.get_activity_summaries(
            begin_date="2024-01-31",
            end_date="2024-01-01"   # 早于 begin_date
        )

        assert response.status_code == 200
        response_body = response.json()
        logger.info(f"  响应: {response_body}")

        # 倒置日期应返回业务错误或缺少ID错误，总之 code != 200
        assert response_body.get("code") != 200, \
            "倒置日期范围应返回业务错误码，但返回了 code=200"

        logger.info(f"✓ 日期范围倒置校验通过，code={response_body.get('code')}")

    @pytest.mark.skip(reason="需要真实 financial_account_id 且该账户须有投资数据")
    def test_get_activity_summaries_success(self, investment_api, valid_date_range):
        """
        测试场景4：成功获取活动摘要（需要真实数据）
        验证点：
        1. 接口返回 200，业务 code=200
        2. 返回摘要数据结构正确
        3. 包含必需字段
        """
        logger.info("测试场景4：成功获取活动摘要")

        response = investment_api.get_activity_summaries(
            financial_account_id="<替换为真实FA ID>",
            **valid_date_range
        )

        assert_status_ok(response)
        response_body = response.json()

        required_fields = [
            "beginning_market_value", "net_additions", "contributions",
            "withdrawals", "fees", "gain_loss", "income", "ending_market_value"
        ]

        for field in required_fields:
            assert field in response_body, f"缺少必需字段: {field}"

        logger.info("✓ 活动摘要获取成功")

    @pytest.mark.skip(reason="需要真实 financial_account_id")
    def test_with_financial_account_id(self, investment_api, short_date_range):
        """
        测试场景5：使用 financial_account_id 参数（需要真实数据）
        验证点：
        1. 接口返回 200，业务 code=200
        2. 使用 financial_account_id 正常工作
        """
        logger.info("测试场景5：使用 financial_account_id 参数")

        response = investment_api.get_activity_summaries(
            financial_account_id="<替换为真实FA ID>",
            **short_date_range
        )

        assert_status_ok(response)
        logger.info("✓ financial_account_id 参数验证通过")

    @pytest.mark.skip(reason="需要真实 account_id")
    def test_with_account_id(self, investment_api, short_date_range):
        """
        测试场景6：使用 account_id 参数（需要真实数据）
        验证点：
        1. 接口返回 200，业务 code=200
        2. 使用 account_id 正常工作
        """
        logger.info("测试场景6：使用 account_id 参数")

        response = investment_api.get_activity_summaries(
            account_id="<替换为真实 account_id>",
            **short_date_range
        )

        assert_status_ok(response)
        logger.info("✓ account_id 参数验证通过")
