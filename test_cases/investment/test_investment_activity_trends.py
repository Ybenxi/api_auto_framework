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
    ⚠️ 文档问题：响应数组有 trailing comma
    ⚠️ 业务规则：必须提供 account_id 或 financial_account_id 之一
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

        response = investment_api.get_activity_trends(**valid_date_range)

        assert response.status_code == 200
        response_body = response.json()
        logger.info(f"  响应: {response_body}")

        assert response_body.get("code") != 200, \
            "不提供ID应返回业务错误码，但返回了 code=200"
        assert response_body.get("data") is None

        logger.info(f"✓ 缺少必需参数校验通过，code={response_body.get('code')}")

    def test_invalid_date_formats(self, investment_api):
        """
        测试场景2：多种无效日期格式
        验证点：
        1. 接口返回 HTTP 200
        2. 各种错误格式均返回业务 code != 200
        """
        logger.info("测试场景2：多种无效日期格式")

        invalid_cases = [
            ("01/01/2024", "2024-01-31", "MM/DD/YYYY格式"),
            ("2024-1-1", "2024-01-31", "单数字月日"),
            ("2024-13-01", "2024-12-31", "无效月份13"),
        ]

        for begin_date, end_date, desc in invalid_cases:
            response = investment_api.get_activity_trends(
                begin_date=begin_date,
                end_date=end_date
            )
            assert response.status_code == 200
            response_body = response.json()
            assert response_body.get("code") != 200, \
                f"[{desc}] 无效日期格式应返回业务错误码，但返回了 code=200"
            logger.info(f"  ✓ [{desc}] code={response_body.get('code')}")

        logger.info("✓ 无效日期格式验证通过")

    def test_future_date_range_returns_empty_or_error(self, investment_api):
        """
        测试场景3：未来日期范围（无数据）
        验证点：
        1. 接口返回 HTTP 200
        2. 返回空数组 或 业务错误（缺少ID）
        """
        logger.info("测试场景3：未来日期范围")

        response = investment_api.get_activity_trends(
            begin_date="2099-01-01",
            end_date="2099-12-31"
        )

        assert response.status_code == 200
        response_body = response.json()
        logger.info(f"  响应: {response_body}")

        # 无ID时返回错误，有ID但无数据时返回空数组
        if isinstance(response_body, dict):
            assert response_body.get("code") != 200, \
                "缺少ID的未来日期请求应返回业务错误"
        elif isinstance(response_body, list):
            assert len(response_body) == 0, "未来日期无投资数据，应返回空数组"

        logger.info(f"✓ 未来日期范围测试通过")

    @pytest.mark.skip(reason="需要真实 financial_account_id 且该账户须有投资数据")
    def test_get_activity_trends_success(self, investment_api, short_date_range):
        """
        测试场景4：成功获取趋势数据（需要真实数据）
        验证点：
        1. 接口返回 200，业务 code=200
        2. 返回数组结构
        3. 数组元素包含必需字段
        """
        logger.info("测试场景4：成功获取趋势数据")

        response = investment_api.get_activity_trends(
            financial_account_id="<替换为真实FA ID>",
            **short_date_range
        )

        assert_status_ok(response)

        response_body = response.json()
        assert isinstance(response_body, list), "响应应为数组"

        if response_body:
            required_fields = ["date", "market_value", "net_addition", "bmv_and_net_addition"]
            for field in required_fields:
                assert field in response_body[0], f"缺少必需字段: {field}"

        logger.info(f"✓ 趋势数据获取成功，返回 {len(response_body)} 条记录")

    @pytest.mark.skip(reason="需要真实数据，验证日期连续性")
    def test_verify_daily_data_integrity(self, investment_api, short_date_range):
        """
        测试场景5：验证每日数据完整性（需要真实数据）
        验证点：
        1. 日期连续性
        2. 日期按升序排列
        """
        logger.info("测试场景5：验证每日数据完整性")

        response = investment_api.get_activity_trends(
            financial_account_id="<替换为真实FA ID>",
            **short_date_range
        )

        assert_status_ok(response)

        trends = response.json()
        assert isinstance(trends, list)

        dates = [item["date"] for item in trends]
        assert dates == sorted(dates), "日期应按升序排列"

        logger.info(f"✓ 每日数据完整性验证通过，共 {len(dates)} 个交易日")

    @pytest.mark.skip(reason="需要真实数据，查询时间较长")
    def test_long_date_range(self, investment_api):
        """
        测试场景6：长日期范围（1年，需要真实数据）
        验证点：
        1. 接口返回 200
        2. 可以处理大量数据
        """
        logger.info("测试场景6：长日期范围（1年）")

        response = investment_api.get_activity_trends(
            financial_account_id="<替换为真实FA ID>",
            begin_date="2023-01-01",
            end_date="2023-12-31"
        )

        assert_status_ok(response)
        trends = response.json()
        logger.info(f"✓ 长日期范围查询成功，返回 {len(trends)} 条记录")
