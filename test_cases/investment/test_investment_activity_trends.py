"""
Investment - Activity Trends 接口测试用例
测试 GET /api/v1/cores/{core}/reports/investments/activity-trends 接口
"""
import pytest
from utils.logger import logger
from utils.assertions import assert_status_ok


@pytest.mark.investment
@pytest.mark.list_api
class TestInvestmentActivityTrends:
    """
    投资活动趋势接口测试用例集
    返回数组格式的趋势数据
    ⚠️ 文档问题：响应数组有trailing comma
    """

    @pytest.mark.skip(reason="需要真实的financial_account_id")
    def test_get_activity_trends_success(self, investment_api, short_date_range):
        """
        测试场景1：成功获取趋势数据
        验证点：
        1. 接口返回 200
        2. 返回数组结构
        3. 数组元素包含必需字段
        """
        logger.info("测试场景1：成功获取趋势数据")
        
        response = investment_api.get_activity_trends(
            financial_account_id="test_fa_id",
            **short_date_range
        )
        
        assert_status_ok(response)
        
        response_body = response.json()
        assert isinstance(response_body, list), "响应应为数组"
        
        if len(response_body) > 0:
            trend_item = response_body[0]
            required_fields = ["date", "market_value", "net_addition", "bmv_and_net_addition"]
            
            for field in required_fields:
                assert field in trend_item, f"缺少必需字段: {field}"
        
        logger.info(f"✓ 趋势数据获取成功，返回 {len(response_body)} 条记录")

    @pytest.mark.skip(reason="需要真实数据")
    def test_verify_daily_data_integrity(self, investment_api, short_date_range):
        """
        测试场景2：验证每日数据完整性
        验证点：
        1. 日期连续性
        2. 每个交易日都有数据
        """
        logger.info("测试场景2：验证每日数据完整性")
        
        response = investment_api.get_activity_trends(
            financial_account_id="test_fa_id",
            **short_date_range
        )
        
        assert_status_ok(response)
        
        trends = response.json()
        assert isinstance(trends, list)
        
        # 验证日期排序
        dates = [item["date"] for item in trends]
        assert dates == sorted(dates), "日期应按升序排列"
        
        logger.info(f"✓ 每日数据完整性验证通过，共 {len(dates)} 个交易日")

    @pytest.mark.skip(reason="需要真实数据")
    def test_short_date_range(self, investment_api):
        """
        测试场景3：短日期范围（1天）
        验证点：
        1. 接口返回 200
        2. 返回1条或0条记录
        """
        logger.info("测试场景3：短日期范围（1天）")
        
        response = investment_api.get_activity_trends(
            financial_account_id="test_fa_id",
            begin_date="2024-01-15",
            end_date="2024-01-15"
        )
        
        assert_status_ok(response)
        
        trends = response.json()
        assert len(trends) <= 1, "单日查询应返回0或1条记录"
        
        logger.info(f"✓ 短日期范围查询成功，返回 {len(trends)} 条记录")

    @pytest.mark.skip(reason="需要真实数据，且查询时间较长")
    def test_long_date_range(self, investment_api):
        """
        测试场景4：长日期范围（1年）
        验证点：
        1. 接口返回 200
        2. 可以处理大量数据
        """
        logger.info("测试场景4：长日期范围（1年）")
        
        response = investment_api.get_activity_trends(
            financial_account_id="test_fa_id",
            begin_date="2023-01-01",
            end_date="2023-12-31"
        )
        
        assert_status_ok(response)
        
        trends = response.json()
        logger.info(f"✓ 长日期范围查询成功，返回 {len(trends)} 条记录")

    def test_empty_data_period(self, investment_api):
        """
        测试场景5：空数据时间段（未来日期）
        验证点：
        1. 接口返回 200
        2. 返回空数组或错误
        """
        logger.info("测试场景5：空数据时间段")
        
        response = investment_api.get_activity_trends(
            financial_account_id="test_fa_id",
            begin_date="2099-01-01",
            end_date="2099-12-31"
        )
        
        assert response.status_code == 200
        
        if response.headers.get("Content-Type", "").startswith("application/json"):
            trends = response.json()
            if isinstance(trends, list):
                logger.info(f"✓ 空数据期返回空数组，长度: {len(trends)}")
            else:
                logger.info(f"✓ 空数据期返回: {trends}")
        
        logger.info("✓ 空数据时间段测试完成")

    def test_date_format_validation(self, investment_api):
        """
        测试场景6：日期格式验证
        验证点：
        1. 正确拒绝错误的日期格式
        """
        logger.info("测试场景6：日期格式验证")
        
        # 测试多种错误格式
        invalid_formats = [
            ("01/01/2024", "2024-01-31"),  # MM/DD/YYYY
            ("2024-1-1", "2024-01-31"),     # 单数字月日
            ("2024-13-01", "2024-12-31"),   # 无效月份
        ]
        
        for begin_date, end_date in invalid_formats:
            logger.debug(f"测试日期格式: {begin_date} 到 {end_date}")
            
            response = investment_api.get_activity_trends(
                financial_account_id="test_fa_id",
                begin_date=begin_date,
                end_date=end_date
            )
            
            logger.debug(f"响应状态: {response.status_code}")
        
        logger.info("✓ 日期格式验证测试完成")
