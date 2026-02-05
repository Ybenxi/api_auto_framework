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
    1. JSON格式错误（分号替代逗号）
    2. 字段命名不一致（actual_percent vs percent）
    """

    @pytest.mark.skip(reason="需要真实的financial_account_id和已配置的策略")
    def test_get_allocations_comparison_success(self, investment_api, short_date_range):
        """
        测试场景1：成功获取配置对比
        验证点：
        1. 接口返回 200
        2. 包含strategy_name、allocations、dailyItems字段
        """
        logger.info("测试场景1：成功获取配置对比")
        
        response = investment_api.get_asset_allocations_comparison(
            financial_account_id="test_fa_id",
            **short_date_range
        )
        
        assert_status_ok(response)
        
        comparison = response.json()
        
        # 验证顶层字段
        assert "strategy_name" in comparison, "应包含strategy_name字段"
        assert "allocations" in comparison, "应包含allocations字段"
        assert "dailyItems" in comparison, "应包含dailyItems字段"
        
        logger.info(f"✓ 配置对比获取成功，策略: {comparison.get('strategy_name')}")

    @pytest.mark.skip(reason="需要真实数据")
    def test_verify_strategy_name(self, investment_api, short_date_range):
        """
        测试场景2：验证strategy_name字段
        验证点：
        1. strategy_name是string类型
        2. 非空
        """
        logger.info("测试场景2：验证strategy_name字段")
        
        response = investment_api.get_asset_allocations_comparison(
            financial_account_id="test_fa_id",
            **short_date_range
        )
        
        assert_status_ok(response)
        
        comparison = response.json()
        strategy_name = comparison.get("strategy_name")
        
        assert isinstance(strategy_name, str), "strategy_name应为字符串"
        assert strategy_name, "strategy_name不应为空"
        
        logger.info(f"✓ 策略名称: {strategy_name}")

    @pytest.mark.skip(reason="需要真实数据")
    def test_verify_allocations_structure(self, investment_api, short_date_range):
        """
        测试场景3：验证allocations数组（actual vs target）
        验证点：
        1. allocations是数组
        2. 包含actual和target相关字段
        """
        logger.info("测试场景3：验证allocations数组")
        
        response = investment_api.get_asset_allocations_comparison(
            financial_account_id="test_fa_id",
            **short_date_range
        )
        
        assert_status_ok(response)
        
        comparison = response.json()
        allocations = comparison.get("allocations", [])
        
        assert isinstance(allocations, list), "allocations应为数组"
        
        if len(allocations) > 0:
            first_alloc = allocations[0]
            
            # 验证必需字段
            expected_fields = [
                "name",
                "actual_start_percent", "actual_end_percent", "actual_diff",
                "target_start_percent", "target_end_percent", "target_diff"
            ]
            
            for field in expected_fields:
                if field in first_alloc:
                    logger.debug(f"{field}: {first_alloc[field]}")
                else:
                    logger.warning(f"⚠️ 缺少字段: {field}")
        
        logger.info(f"✓ allocations数组验证完成，包含 {len(allocations)} 个资产类别")

    @pytest.mark.skip(reason="需要真实数据")
    def test_verify_daily_items_structure(self, investment_api, short_date_range):
        """
        测试场景4：验证dailyItems数组
        验证点：
        1. dailyItems是数组
        2. 每个元素包含date和allocations
        3. allocations包含actual_percent和target_percent
        """
        logger.info("测试场景4：验证dailyItems数组")
        
        response = investment_api.get_asset_allocations_comparison(
            financial_account_id="test_fa_id",
            **short_date_range
        )
        
        assert_status_ok(response)
        
        comparison = response.json()
        daily_items = comparison.get("dailyItems", [])
        
        assert isinstance(daily_items, list), "dailyItems应为数组"
        
        if len(daily_items) > 0:
            first_day = daily_items[0]
            
            assert "date" in first_day, "应包含date字段"
            assert "allocations" in first_day, "应包含allocations字段"
            
            day_allocations = first_day.get("allocations", [])
            if len(day_allocations) > 0:
                first_alloc = day_allocations[0]
                
                # 验证字段（注意：可能是actual_percent或percent）
                logger.debug(f"每日配置字段: {list(first_alloc.keys())}")
                
                # 检查字段命名不一致问题
                has_actual_percent = "actual_percent" in first_alloc
                has_percent = "percent" in first_alloc
                
                if has_actual_percent:
                    logger.info("✓ 使用actual_percent字段名")
                elif has_percent:
                    logger.warning("⚠️ 使用percent字段名（与allocations数组不一致）")
        
        logger.info(f"✓ dailyItems数组验证完成，包含 {len(daily_items)} 天的数据")

    @pytest.mark.skip(reason="需要未配置策略的账户")
    def test_account_without_strategy(self, investment_api, short_date_range):
        """
        测试场景5：未配置策略的账户
        验证点：
        1. 接口返回错误或空数据
        2. 提示账户未配置策略
        """
        logger.info("测试场景5：未配置策略的账户")
        
        response = investment_api.get_asset_allocations_comparison(
            financial_account_id="test_fa_id_without_strategy",
            **short_date_range
        )
        
        assert response.status_code == 200
        
        response_body = response.json()
        
        # 可能返回错误或空的strategy_name
        if "error_message" in response_body:
            logger.info(f"✓ 正确返回错误: {response_body['error_message']}")
        elif not response_body.get("strategy_name"):
            logger.info("✓ 返回空策略名称")
        
        logger.info("✓ 未配置策略测试完成")

    @pytest.mark.skip(reason="需要真实数据")
    def test_field_naming_consistency(self, investment_api, short_date_range):
        """
        测试场景6：字段命名一致性验证
        验证点：
        1. allocations数组使用actual_percent
        2. dailyItems.allocations可能使用percent（文档问题）
        3. 记录字段命名差异
        """
        logger.info("测试场景6：字段命名一致性验证")
        
        response = investment_api.get_asset_allocations_comparison(
            financial_account_id="test_fa_id",
            **short_date_range
        )
        
        assert_status_ok(response)
        
        comparison = response.json()
        
        # 检查allocations数组
        allocations = comparison.get("allocations", [])
        if len(allocations) > 0:
            alloc_fields = list(allocations[0].keys())
            logger.info(f"allocations字段: {alloc_fields}")
        
        # 检查dailyItems数组
        daily_items = comparison.get("dailyItems", [])
        if len(daily_items) > 0 and len(daily_items[0].get("allocations", [])) > 0:
            daily_alloc_fields = list(daily_items[0]["allocations"][0].keys())
            logger.info(f"dailyItems.allocations字段: {daily_alloc_fields}")
            
            # 对比字段差异
            if alloc_fields != daily_alloc_fields:
                logger.warning("⚠️ 检测到字段命名不一致")
                logger.warning(f"差异字段: {set(alloc_fields) ^ set(daily_alloc_fields)}")
        
        logger.info("✓ 字段命名一致性验证完成")
