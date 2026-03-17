"""
Investment - Asset Allocations Comparison 接口测试用例
测试 GET /api/v1/cores/{core}/reports/investments/asset-allocations/comparison 接口
"""
import pytest
from utils.logger import logger
from utils.assertions import assert_status_ok


@pytest.mark.investment
@pytest.mark.detail_api
class TestInvestmentAssetAllocationsComparison:
    """
    资产配置对比接口测试用例集
    返回实际配置 vs 目标配置的对比数据
    ⚠️ 文档问题：
    1. JSON 格式错误（分号替代逗号）
    2. 字段命名不一致（actual_percent vs percent）
    ⚠️ 业务规则：必须提供 account_id 或 financial_account_id，且账户需已配置策略
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

        response = investment_api.get_asset_allocations_comparison(**short_date_range)

        assert response.status_code == 200
        response_body = response.json()
        logger.info(f"  响应: {response_body}")

        assert response_body.get("code") != 200, \
            "不提供ID应返回业务错误码，但返回了 code=200"
        assert response_body.get("data") is None

        logger.info(f"✓ 缺少必需参数校验通过，code={response_body.get('code')}")

    @pytest.mark.skip(reason="需要真实 financial_account_id 且账户已配置投资策略")
    def test_get_allocations_comparison_success(self, investment_api, short_date_range):
        """
        测试场景2：成功获取配置对比（需要真实数据和已配置策略）
        验证点：
        1. 接口返回 200，业务 code=200
        2. 包含 strategy_name、allocations、dailyItems 字段
        """
        logger.info("测试场景2：成功获取配置对比")

        response = investment_api.get_asset_allocations_comparison(
            financial_account_id="<替换为真实FA ID>",
            **short_date_range
        )

        assert_status_ok(response)

        comparison = response.json()
        assert "strategy_name" in comparison, "应包含 strategy_name 字段"
        assert "allocations" in comparison, "应包含 allocations 字段"
        assert "dailyItems" in comparison, "应包含 dailyItems 字段"

        logger.info(f"✓ 配置对比获取成功，策略: {comparison.get('strategy_name')}")

    @pytest.mark.skip(reason="需要真实数据，验证 allocations 结构")
    def test_verify_allocations_structure(self, investment_api, short_date_range):
        """
        测试场景3：验证 allocations 数组（actual vs target，需要真实数据）
        验证点：
        1. allocations 是数组
        2. 包含 actual 和 target 相关字段
        """
        logger.info("测试场景3：验证 allocations 数组")

        response = investment_api.get_asset_allocations_comparison(
            financial_account_id="<替换为真实FA ID>",
            **short_date_range
        )

        assert_status_ok(response)

        comparison = response.json()
        allocations = comparison.get("allocations", [])
        assert isinstance(allocations, list), "allocations 应为数组"

        if allocations:
            expected_fields = [
                "name",
                "actual_start_percent", "actual_end_percent", "actual_diff",
                "target_start_percent", "target_end_percent", "target_diff"
            ]
            for field in expected_fields:
                if field not in allocations[0]:
                    logger.warning(f"⚠️ 缺少字段: {field}")

        logger.info(f"✓ allocations 数组验证完成，包含 {len(allocations)} 个资产类别")

    @pytest.mark.skip(reason="需要真实数据，验证 dailyItems 结构")
    def test_verify_daily_items_structure(self, investment_api, short_date_range):
        """
        测试场景4：验证 dailyItems 数组（需要真实数据）
        验证点：
        1. dailyItems 是数组
        2. 每个元素包含 date 和 allocations
        3. 关注 actual_percent vs percent 字段命名不一致问题
        """
        logger.info("测试场景4：验证 dailyItems 数组")

        response = investment_api.get_asset_allocations_comparison(
            financial_account_id="<替换为真实FA ID>",
            **short_date_range
        )

        assert_status_ok(response)

        comparison = response.json()
        daily_items = comparison.get("dailyItems", [])
        assert isinstance(daily_items, list), "dailyItems 应为数组"

        if daily_items:
            first_day = daily_items[0]
            assert "date" in first_day, "应包含 date 字段"
            assert "allocations" in first_day, "应包含 allocations 字段"

            day_allocations = first_day.get("allocations", [])
            if day_allocations:
                first_alloc = day_allocations[0]
                if "actual_percent" in first_alloc:
                    logger.info("✓ 使用 actual_percent 字段名")
                elif "percent" in first_alloc:
                    logger.warning("⚠️ 使用 percent 字段名（与 allocations 数组不一致）")

        logger.info(f"✓ dailyItems 数组验证完成，包含 {len(daily_items)} 天的数据")

    @pytest.mark.skip(reason="需要字段命名不一致的真实数据来验证")
    def test_field_naming_consistency(self, investment_api, short_date_range):
        """
        测试场景5：字段命名一致性验证（需要真实数据）
        验证点：
        1. allocations 数组使用 actual_percent
        2. dailyItems.allocations 可能使用 percent（文档问题）
        3. 记录字段命名差异
        """
        logger.info("测试场景5：字段命名一致性验证")

        response = investment_api.get_asset_allocations_comparison(
            financial_account_id="<替换为真实FA ID>",
            **short_date_range
        )

        assert_status_ok(response)

        comparison = response.json()
        allocations = comparison.get("allocations", [])
        daily_items = comparison.get("dailyItems", [])

        if allocations:
            alloc_fields = list(allocations[0].keys())
            logger.info(f"allocations 字段: {alloc_fields}")

        if daily_items and daily_items[0].get("allocations"):
            daily_alloc_fields = list(daily_items[0]["allocations"][0].keys())
            logger.info(f"dailyItems.allocations 字段: {daily_alloc_fields}")

            if allocations and set(alloc_fields) != set(daily_alloc_fields):
                logger.warning("⚠️ 检测到字段命名不一致")

        logger.info("✓ 字段命名一致性验证完成")
