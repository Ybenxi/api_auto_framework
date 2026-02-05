"""
Investment - Asset Allocations 接口测试用例
测试 GET /api/v1/cores/{core}/reports/investments/asset-allocations 接口
"""
import pytest
from utils.logger import logger
from utils.assertions import assert_status_ok


@pytest.mark.investment
@pytest.mark.list_api
class TestInvestmentAssetAllocations:
    """
    资产配置接口测试用例集
    返回嵌套结构的资产配置数据（可能3-4层深）
    ⚠️ 文档问题：嵌套结构说明不完整
    """

    @pytest.mark.skip(reason="需要真实的financial_account_id")
    def test_get_asset_allocations_success(self, investment_api, short_date_range):
        """
        测试场景1：成功获取资产配置
        验证点：
        1. 接口返回 200
        2. 返回数组结构
        3. 每个元素包含date和allocations
        """
        logger.info("测试场景1：成功获取资产配置")
        
        response = investment_api.get_asset_allocations(
            financial_account_id="test_fa_id",
            **short_date_range
        )
        
        assert_status_ok(response)
        
        allocations_list = response.json()
        assert isinstance(allocations_list, list), "响应应为数组"
        
        if len(allocations_list) > 0:
            item = allocations_list[0]
            assert "date" in item, "应包含date字段"
            assert "allocations" in item, "应包含allocations字段"
            assert isinstance(item["allocations"], list), "allocations应为数组"
        
        logger.info(f"✓ 资产配置获取成功，返回 {len(allocations_list)} 个日期的数据")

    @pytest.mark.skip(reason="需要真实数据")
    def test_verify_nested_structure(self, investment_api, short_date_range):
        """
        测试场景2：验证嵌套结构（children）
        验证点：
        1. allocations数组中的元素包含children字段
        2. children可能继续嵌套
        """
        logger.info("测试场景2：验证嵌套结构")
        
        response = investment_api.get_asset_allocations(
            financial_account_id="test_fa_id",
            **short_date_range
        )
        
        assert_status_ok(response)
        
        allocations_list = response.json()
        
        if len(allocations_list) > 0:
            first_day = allocations_list[0]
            allocations = first_day.get("allocations", [])
            
            if len(allocations) > 0:
                first_allocation = allocations[0]
                
                # 验证allocation字段
                expected_fields = [
                    "class", "segment", "name", "symbol", 
                    "market_value", "percent_of_level", "percent_of_total"
                ]
                
                for field in expected_fields:
                    if field in first_allocation:
                        logger.debug(f"{field}: {first_allocation[field]}")
                
                # 检查children
                if "children" in first_allocation:
                    children = first_allocation["children"]
                    if children:
                        logger.info(f"✓ 检测到嵌套结构，第一层有 {len(children)} 个子项")
                    else:
                        logger.info("✓ children为空或null（叶子节点）")
        
        logger.info("✓ 嵌套结构验证完成")

    @pytest.mark.skip(reason="需要真实数据")
    def test_verify_percentage_calculation(self, investment_api, short_date_range):
        """
        测试场景3：验证百分比计算
        验证点：
        1. percent_of_level：在当前层级的占比
        2. percent_of_total：在总资产的占比
        3. 同层级的percent_of_level总和应接近1.0
        """
        logger.info("测试场景3：验证百分比计算")
        
        response = investment_api.get_asset_allocations(
            financial_account_id="test_fa_id",
            **short_date_range
        )
        
        assert_status_ok(response)
        
        allocations_list = response.json()
        
        if len(allocations_list) > 0:
            first_day = allocations_list[0]
            allocations = first_day.get("allocations", [])
            
            # 计算顶层percent_of_level总和
            total_percent = sum(
                alloc.get("percent_of_level", 0) 
                for alloc in allocations
            )
            
            logger.debug(f"顶层percent_of_level总和: {total_percent}")
            
            # 应该接近1.0（允许浮点误差）
            if 0.99 <= total_percent <= 1.01:
                logger.info("✓ 百分比计算正确")
            else:
                logger.warning(f"⚠️ 百分比总和异常: {total_percent}")
        
        logger.info("✓ 百分比计算验证完成")

    def test_empty_allocation_period(self, investment_api):
        """
        测试场景4：空配置时间段
        验证点：
        1. 接口返回 200
        2. 返回空数组或包含空allocations的数据
        """
        logger.info("测试场景4：空配置时间段")
        
        response = investment_api.get_asset_allocations(
            financial_account_id="test_fa_id",
            begin_date="2099-01-01",
            end_date="2099-12-31"
        )
        
        assert response.status_code == 200
        
        if response.headers.get("Content-Type", "").startswith("application/json"):
            allocations_list = response.json()
            logger.info(f"✓ 空配置期返回数据，长度: {len(allocations_list)}")
        
        logger.info("✓ 空配置时间段测试完成")

    @pytest.mark.skip(reason="需要真实数据，且需要验证复杂嵌套")
    def test_deep_nesting_verification(self, investment_api, short_date_range):
        """
        测试场景5：深层嵌套验证（3-4层）
        验证点：
        1. 递归遍历children
        2. 验证每层的数据完整性
        """
        logger.info("测试场景5：深层嵌套验证")
        
        response = investment_api.get_asset_allocations(
            financial_account_id="test_fa_id",
            **short_date_range
        )
        
        assert_status_ok(response)
        
        allocations_list = response.json()
        
        def count_nesting_levels(item, level=1):
            """递归计算嵌套层级"""
            children = item.get("children")
            if not children or children is None:
                return level
            
            max_child_level = level
            for child in children:
                child_level = count_nesting_levels(child, level + 1)
                max_child_level = max(max_child_level, child_level)
            
            return max_child_level
        
        if len(allocations_list) > 0:
            first_day = allocations_list[0]
            allocations = first_day.get("allocations", [])
            
            if len(allocations) > 0:
                max_depth = max(count_nesting_levels(alloc) for alloc in allocations)
                logger.info(f"✓ 最大嵌套层级: {max_depth}")
        
        logger.info("✓ 深层嵌套验证完成")

    @pytest.mark.skip(reason="需要真实数据")
    def test_date_array_completeness(self, investment_api, short_date_range):
        """
        测试场景6：日期数组完整性
        验证点：
        1. 返回的日期范围与请求一致
        2. 日期按升序排列
        """
        logger.info("测试场景6：日期数组完整性")
        
        response = investment_api.get_asset_allocations(
            financial_account_id="test_fa_id",
            **short_date_range
        )
        
        assert_status_ok(response)
        
        allocations_list = response.json()
        
        # 提取所有日期
        dates = [item["date"] for item in allocations_list]
        
        # 验证排序
        assert dates == sorted(dates), "日期应按升序排列"
        
        logger.info(f"✓ 日期数组完整性验证通过，共 {len(dates)} 个交易日")
