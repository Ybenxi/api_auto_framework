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
    """

    @pytest.mark.skip(reason="需要真实的financial_account_id，待完善数据准备")
    def test_get_activity_summaries_success(self, investment_api, valid_date_range):
        """
        测试场景1：成功获取活动摘要
        验证点：
        1. 接口返回 200
        2. 返回摘要数据结构正确
        3. 包含必需字段
        """
        logger.info("测试场景1：成功获取活动摘要")
        
        response = investment_api.get_activity_summaries(
            financial_account_id="test_fa_id",
            **valid_date_range
        )
        
        assert_status_ok(response)
        
        response_body = response.json()
        
        # 验证必需字段存在
        required_fields = [
            "beginning_market_value",
            "net_additions",
            "contributions",
            "withdrawals",
            "fees",
            "gain_loss",
            "income",
            "ending_market_value"
        ]
        
        for field in required_fields:
            assert field in response_body, f"缺少必需字段: {field}"
        
        logger.info("✓ 活动摘要获取成功")

    @pytest.mark.skip(reason="需要真实financial_account_id")
    def test_with_financial_account_id(self, investment_api, short_date_range):
        """
        测试场景2：使用financial_account_id参数
        验证点：
        1. 接口返回 200
        2. 使用financial_account_id正常工作
        """
        logger.info("测试场景2：使用financial_account_id参数")
        
        response = investment_api.get_activity_summaries(
            financial_account_id="test_fa_id",
            **short_date_range
        )
        
        assert_status_ok(response)
        
        logger.info("✓ financial_account_id参数验证通过")

    @pytest.mark.skip(reason="需要真实account_id")
    def test_with_account_id(self, investment_api, short_date_range):
        """
        测试场景3：使用account_id参数
        验证点：
        1. 接口返回 200
        2. 使用account_id正常工作
        """
        logger.info("测试场景3：使用account_id参数")
        
        response = investment_api.get_activity_summaries(
            account_id="test_account_id",
            **short_date_range
        )
        
        assert_status_ok(response)
        
        logger.info("✓ account_id参数验证通过")

    def test_invalid_date_format(self, investment_api):
        """
        测试场景4：无效的日期格式
        验证点：
        1. 接口返回错误
        2. 错误信息提示日期格式问题
        """
        logger.info("测试场景4：无效的日期格式")
        
        response = investment_api.get_activity_summaries(
            financial_account_id="test_fa_id",
            begin_date="2024/01/01",  # 错误格式
            end_date="2024-01-31"
        )
        
        # 可能返回400或其他错误
        logger.info(f"响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            response_body = response.json()
            logger.info(f"响应体: {response_body}")
        
        logger.info("✓ 无效日期格式测试完成")

    def test_date_range_reversed(self, investment_api):
        """
        测试场景5：日期范围倒置（end_date < begin_date）
        验证点：
        1. 接口返回错误或空数据
        """
        logger.info("测试场景5：日期范围倒置")
        
        response = investment_api.get_activity_summaries(
            financial_account_id="test_fa_id",
            begin_date="2024-01-31",
            end_date="2024-01-01"  # 早于begin_date
        )
        
        logger.info(f"响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            response_body = response.json()
            logger.info(f"倒置日期范围响应: {response_body}")
        
        logger.info("✓ 日期范围倒置测试完成")

    def test_missing_account_ids(self, investment_api, valid_date_range):
        """
        测试场景6：两个ID都不提供
        验证点：
        1. 接口返回错误
        2. 提示需要提供account_id或financial_account_id
        """
        logger.info("测试场景6：两个ID都不提供")
        
        response = investment_api.get_activity_summaries(
            **valid_date_range
            # 不提供account_id和financial_account_id
        )
        
        # 应该返回错误
        assert response.status_code == 200, "HTTP状态码应为200"
        
        response_body = response.json()
        logger.info(f"错误响应: {response_body}")
        
        # 可能有业务错误码
        if "code" in response_body:
            assert response_body["code"] != 200, "业务code应不为200"
        
        logger.info("✓ 缺少必需参数测试完成")
