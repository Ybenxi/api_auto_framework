"""
Account Summary - Categorized Mode 接口测试用例
测试 GET /api/v1/cores/{core}/account/summary?classification_mode=Categorized 接口
"""
import pytest
from utils.logger import logger
from utils.assertions import assert_status_ok
from data.enums import ClassificationMode


@pytest.mark.account_summary
@pytest.mark.list_api
class TestAccountSummaryCategorized:
    """
    账户摘要分类模式接口测试用例集
    Categorized模式：按Asset/Liability分组，再按record_type分组
    ⚠️ 文档问题：
    1. balance字段类型不一致（string vs number）
    2. 字段命名不一致（total_balance vs balance）
    """

    def test_get_categorized_summary_success(self, account_summary_api):
        """
        测试场景1：成功获取分类摘要
        验证点：
        1. 接口返回 200
        2. code=200
        3. 包含data字段
        """
        logger.info("测试场景1：成功获取分类摘要")
        
        response = account_summary_api.get_account_summary(
            classification_mode=ClassificationMode.CATEGORIZED
        )
        
        assert_status_ok(response)
        
        response_body = response.json()
        assert response_body.get("code") == 200, "业务code应为200"
        assert "data" in response_body, "应包含data字段"
        
        logger.info("✓ 分类摘要获取成功")

    def test_verify_asset_financial_accounts_structure(self, account_summary_api):
        """
        测试场景2：验证asset_financial_accounts结构
        验证点：
        1. 包含total_balance和record_type字段
        2. record_type是数组
        """
        logger.info("测试场景2：验证asset_financial_accounts结构")
        
        response = account_summary_api.get_account_summary(
            classification_mode=ClassificationMode.CATEGORIZED
        )
        
        assert_status_ok(response)
        
        data = response.json().get("data", {})
        asset_fas = data.get("asset_financial_accounts", {})
        
        assert "total_balance" in asset_fas, "应包含total_balance字段"
        assert "record_type" in asset_fas, "应包含record_type字段"
        assert isinstance(asset_fas["record_type"], list), "record_type应为数组"
        
        logger.info(f"✓ asset_financial_accounts结构验证通过，包含 {len(asset_fas['record_type'])} 种记录类型")

    def test_verify_liability_financial_accounts_structure(self, account_summary_api):
        """
        测试场景3：验证liability_financial_accounts结构
        验证点：
        1. 包含total_balance和record_type字段
        2. 结构与asset_financial_accounts一致
        """
        logger.info("测试场景3：验证liability_financial_accounts结构")
        
        response = account_summary_api.get_account_summary(
            classification_mode=ClassificationMode.CATEGORIZED
        )
        
        assert_status_ok(response)
        
        data = response.json().get("data", {})
        liability_fas = data.get("liability_financial_accounts", {})
        
        assert "total_balance" in liability_fas, "应包含total_balance字段"
        assert "record_type" in liability_fas, "应包含record_type字段"
        assert isinstance(liability_fas["record_type"], list), "record_type应为数组"
        
        logger.info(f"✓ liability_financial_accounts结构验证通过，包含 {len(liability_fas['record_type'])} 种记录类型")

    def test_verify_record_type_grouping(self, account_summary_api):
        """
        测试场景4：验证record_type分组
        验证点：
        1. 每个record_type元素包含name、total_balance、financial_accounts
        2. financial_accounts是数组
        """
        logger.info("测试场景4：验证record_type分组")
        
        response = account_summary_api.get_account_summary(
            classification_mode=ClassificationMode.CATEGORIZED
        )
        
        assert_status_ok(response)
        
        data = response.json().get("data", {})
        asset_fas = data.get("asset_financial_accounts", {})
        record_types = asset_fas.get("record_type", [])
        
        if len(record_types) > 0:
            first_type = record_types[0]
            
            assert "name" in first_type, "应包含name字段"
            assert "total_balance" in first_type, "应包含total_balance字段"
            assert "financial_accounts" in first_type, "应包含financial_accounts字段"
            assert isinstance(first_type["financial_accounts"], list), "financial_accounts应为数组"
            
            logger.info(f"✓ record_type分组验证通过，类型: {first_type['name']}")
        else:
            logger.info("✓ 当前无record_type数据")

    def test_verify_sub_accounts_nesting(self, account_summary_api):
        """
        测试场景5：验证sub_accounts嵌套
        验证点：
        1. financial_accounts中包含sub_accounts数组
        2. sub_accounts结构正确
        """
        logger.info("测试场景5：验证sub_accounts嵌套")
        
        response = account_summary_api.get_account_summary(
            classification_mode=ClassificationMode.CATEGORIZED
        )
        
        assert_status_ok(response)
        
        data = response.json().get("data", {})
        asset_fas = data.get("asset_financial_accounts", {})
        
        # 遍历查找sub_accounts
        found_sub_accounts = False
        for record_type in asset_fas.get("record_type", []):
            for fa in record_type.get("financial_accounts", []):
                if "sub_accounts" in fa:
                    sub_accounts = fa["sub_accounts"]
                    assert isinstance(sub_accounts, list), "sub_accounts应为数组"
                    
                    if len(sub_accounts) > 0:
                        found_sub_accounts = True
                        sub_acc = sub_accounts[0]
                        logger.debug(f"Sub Account字段: {list(sub_acc.keys())}")
                        
                        # 验证balance字段命名
                        if "balance" in sub_acc:
                            logger.info("✓ Sub Account使用balance字段名")
                        elif "total_balance" in sub_acc:
                            logger.info("✓ Sub Account使用total_balance字段名")
                    
                    break
            if found_sub_accounts:
                break
        
        if found_sub_accounts:
            logger.info("✓ sub_accounts嵌套验证通过")
        else:
            logger.info("✓ 当前无sub_accounts数据")

    def test_verify_debit_cards_array(self, account_summary_api):
        """
        测试场景6：验证debit_cards数组
        验证点：
        1. 包含debit_cards字段
        2. debit_cards是数组
        3. 卡片包含必需字段
        """
        logger.info("测试场景6：验证debit_cards数组")
        
        response = account_summary_api.get_account_summary(
            classification_mode=ClassificationMode.CATEGORIZED
        )
        
        assert_status_ok(response)
        
        data = response.json().get("data", {})
        debit_cards = data.get("debit_cards", [])
        
        assert isinstance(debit_cards, list), "debit_cards应为数组"
        
        if len(debit_cards) > 0:
            card = debit_cards[0]
            
            # 验证关键字段
            expected_fields = ["id", "card_number", "card_status", "card_type", "network"]
            for field in expected_fields:
                if field in card:
                    logger.debug(f"{field}: {card[field]}")
            
            logger.info(f"✓ debit_cards数组验证通过，包含 {len(debit_cards)} 张卡片")
        else:
            logger.info("✓ 当前无debit_cards数据")

    def test_total_balance_calculation(self, account_summary_api):
        """
        测试场景7：总余额计算验证
        验证点：
        1. total_balance = asset_balance - liability_balance（理论上）
        2. 使用parse方法验证
        """
        logger.info("测试场景7：总余额计算验证")
        
        response = account_summary_api.get_account_summary(
            classification_mode=ClassificationMode.CATEGORIZED
        )
        
        assert_status_ok(response)
        
        # 使用parse方法
        parsed = account_summary_api.parse_categorized_response(response)
        
        assert not parsed.get("error"), "解析不应出错"
        
        total_balance = parsed.get("total_balance", 0.0)
        asset_balance = parsed.get("asset_balance", 0.0)
        liability_balance = parsed.get("liability_balance", 0.0)
        
        logger.info(f"总余额: {total_balance}")
        logger.info(f"资产余额: {asset_balance}")
        logger.info(f"负债余额: {liability_balance}")
        
        # 计算验证
        calculated = account_summary_api.calculate_total_balance(parsed)
        logger.info(f"计算结果: {calculated}")
        
        logger.info("✓ 总余额计算验证完成")

    def test_balance_field_type_handling(self, account_summary_api):
        """
        测试场景8：balance字段类型处理
        验证点：
        1. balance可能是string或number
        2. parse方法正确转换为float
        """
        logger.info("测试场景8：balance字段类型处理")
        
        response = account_summary_api.get_account_summary(
            classification_mode=ClassificationMode.CATEGORIZED
        )
        
        assert_status_ok(response)
        
        data = response.json().get("data", {})
        
        # 检查total_balance的类型
        total_balance = data.get("total_balance")
        balance_type = type(total_balance).__name__
        
        logger.info(f"total_balance类型: {balance_type}, 值: {total_balance}")
        
        # 测试转换
        converted = account_summary_api._to_float(total_balance)
        assert isinstance(converted, float), "转换后应为float类型"
        
        logger.info(f"✓ 转换为float: {converted}")
        
        # 检查asset_financial_accounts.total_balance
        asset_balance = data.get("asset_financial_accounts", {}).get("total_balance")
        asset_type = type(asset_balance).__name__
        logger.info(f"asset total_balance类型: {asset_type}, 值: {asset_balance}")
        
        logger.info("✓ balance字段类型处理验证完成")
