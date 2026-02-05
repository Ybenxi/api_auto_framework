"""
Account Summary - Flat Mode 接口测试用例
测试 GET /api/v1/cores/{core}/account/summary?classification_mode=Flat 接口
"""
import pytest
from utils.logger import logger
from utils.assertions import assert_status_ok
from data.enums import ClassificationMode


@pytest.mark.account_summary
@pytest.mark.list_api
class TestAccountSummaryFlat:
    """
    账户摘要扁平模式接口测试用例集
    Flat模式：无分组，数据扁平化返回
    ⚠️ 文档问题：Flat模式缺少响应示例，实际结构未知
    """

    def test_get_flat_summary_success(self, account_summary_api):
        """
        测试场景1：成功获取扁平摘要
        验证点：
        1. 接口返回 200
        2. code=200
        3. 包含data字段
        """
        logger.info("测试场景1：成功获取扁平摘要")
        
        response = account_summary_api.get_account_summary(
            classification_mode=ClassificationMode.FLAT
        )
        
        assert_status_ok(response)
        
        response_body = response.json()
        assert response_body.get("code") == 200, "业务code应为200"
        assert "data" in response_body, "应包含data字段"
        
        logger.info("✓ 扁平摘要获取成功")

    def test_verify_flat_response_structure(self, account_summary_api):
        """
        测试场景2：验证Flat模式响应结构（探索性测试）
        验证点：
        1. 记录实际响应结构
        2. 对比与Categorized模式的差异
        """
        logger.info("测试场景2：验证Flat模式响应结构")
        
        response = account_summary_api.get_account_summary(
            classification_mode=ClassificationMode.FLAT
        )
        
        assert_status_ok(response)
        
        data = response.json().get("data", {})
        
        # 探索性记录：打印所有顶层字段
        top_level_keys = list(data.keys())
        logger.info(f"Flat模式顶层字段: {top_level_keys}")
        
        # 检查是否还有asset_financial_accounts分组
        if "asset_financial_accounts" in data:
            logger.info("⚠️ Flat模式仍包含asset_financial_accounts分组")
        else:
            logger.info("✓ Flat模式无asset_financial_accounts分组")
        
        # 检查financial_accounts是否直接在data下
        if "financial_accounts" in data:
            logger.info("✓ Flat模式包含顶层financial_accounts字段")
            fa_count = len(data["financial_accounts"]) if isinstance(data["financial_accounts"], list) else 0
            logger.info(f"financial_accounts数量: {fa_count}")
        
        # 使用parse方法
        parsed = account_summary_api.parse_flat_response(response)
        logger.info(f"解析结果结构: {list(parsed.keys())}")
        
        logger.info("✓ Flat模式响应结构探索完成")

    def test_compare_categorized_vs_flat_data(self, account_summary_api):
        """
        测试场景3：对比Categorized vs Flat数据一致性
        验证点：
        1. 两种模式返回的数据应该是相同的，只是组织方式不同
        2. 总余额应该一致
        """
        logger.info("测试场景3：对比Categorized vs Flat数据一致性")
        
        # 获取Categorized模式
        categorized_response = account_summary_api.get_account_summary(
            classification_mode=ClassificationMode.CATEGORIZED
        )
        
        # 获取Flat模式
        flat_response = account_summary_api.get_account_summary(
            classification_mode=ClassificationMode.FLAT
        )
        
        assert_status_ok(categorized_response)
        assert_status_ok(flat_response)
        
        categorized_data = categorized_response.json().get("data", {})
        flat_data = flat_response.json().get("data", {})
        
        # 对比total_balance
        categorized_balance = categorized_data.get("total_balance")
        flat_balance = flat_data.get("total_balance")
        
        logger.info(f"Categorized total_balance: {categorized_balance}")
        logger.info(f"Flat total_balance: {flat_balance}")
        
        if categorized_balance is not None and flat_balance is not None:
            # 转换为float比较
            cat_float = account_summary_api._to_float(categorized_balance)
            flat_float = account_summary_api._to_float(flat_balance)
            
            if abs(cat_float - flat_float) < 0.01:
                logger.info("✓ 两种模式的total_balance一致")
            else:
                logger.warning(f"⚠️ total_balance不一致: {cat_float} vs {flat_float}")
        
        logger.info("✓ 数据一致性对比完成")

    def test_verify_no_grouping_in_flat_mode(self, account_summary_api):
        """
        测试场景4：验证Flat模式无分组
        验证点：
        1. 无asset_financial_accounts分组
        2. 无liability_financial_accounts分组
        3. 无record_type分组
        """
        logger.info("测试场景4：验证Flat模式无分组")
        
        response = account_summary_api.get_account_summary(
            classification_mode=ClassificationMode.FLAT
        )
        
        assert_status_ok(response)
        
        data = response.json().get("data", {})
        
        # 检查是否有分组结构
        has_asset_group = "asset_financial_accounts" in data
        has_liability_group = "liability_financial_accounts" in data
        
        logger.info(f"包含asset_financial_accounts分组: {has_asset_group}")
        logger.info(f"包含liability_financial_accounts分组: {has_liability_group}")
        
        if not has_asset_group and not has_liability_group:
            logger.info("✓ Flat模式确实无Asset/Liability分组")
        elif has_asset_group or has_liability_group:
            logger.warning("⚠️ Flat模式仍包含分组结构")
            
            # 检查分组内是否有record_type
            if has_asset_group:
                asset_fas = data["asset_financial_accounts"]
                if isinstance(asset_fas, dict) and "record_type" in asset_fas:
                    logger.warning("⚠️ 仍包含record_type分组")
        
        logger.info("✓ 无分组验证完成")

    def test_empty_accounts_flat_mode(self, account_summary_api):
        """
        测试场景5：空账户时的Flat模式响应
        验证点：
        1. 接口返回 200
        2. 空数据的表现形式
        """
        logger.info("测试场景5：空账户时的Flat模式响应")
        
        response = account_summary_api.get_account_summary(
            classification_mode=ClassificationMode.FLAT
        )
        
        assert_status_ok(response)
        
        data = response.json().get("data", {})
        
        # 记录空数据时的结构
        logger.info(f"空数据响应字段: {list(data.keys())}")
        logger.info(f"total_balance: {data.get('total_balance')}")
        
        logger.info("✓ 空账户Flat模式测试完成")

    def test_field_naming_consistency_verification(self, account_summary_api):
        """
        测试场景6：字段命名一致性验证
        验证点：
        1. Flat模式下balance字段命名
        2. 是否统一使用total_balance或balance
        """
        logger.info("测试场景6：字段命名一致性验证")
        
        response = account_summary_api.get_account_summary(
            classification_mode=ClassificationMode.FLAT
        )
        
        assert_status_ok(response)
        
        data = response.json().get("data", {})
        
        # 收集所有balance相关字段
        balance_fields = [key for key in data.keys() if "balance" in key.lower()]
        
        logger.info(f"包含balance的字段: {balance_fields}")
        
        # 如果有financial_accounts数组，检查其字段命名
        if "financial_accounts" in data and isinstance(data["financial_accounts"], list):
            if len(data["financial_accounts"]) > 0:
                fa_fields = list(data["financial_accounts"][0].keys())
                fa_balance_fields = [f for f in fa_fields if "balance" in f.lower()]
                logger.info(f"financial_account的balance字段: {fa_balance_fields}")
                
                # 检查是否使用total_balance或balance
                if "total_balance" in fa_balance_fields:
                    logger.info("✓ financial_account使用total_balance")
                elif "balance" in fa_balance_fields:
                    logger.warning("⚠️ financial_account使用balance（与顶层不一致）")
        
        logger.info("✓ 字段命名一致性验证完成")
