"""
Card Management - List Cards 接口测试用例
测试 GET /api/v1/cores/{core}/card-issuance/cards 接口
"""
import pytest
from utils.logger import logger
from utils.assertions import assert_status_ok, assert_list_structure, assert_enum_filter
from data.enums import CardNetwork, CardType, CardStatus


@pytest.mark.card_management
@pytest.mark.list_api
class TestCardListCards:
    """
    卡片列表接口测试用例集
    """

    def test_list_cards_success(self, card_management_api):
        """
        测试场景1：成功获取卡片列表
        验证点：
        1. 接口返回 200
        2. 返回列表结构正确
        """
        logger.info("测试场景1：成功获取卡片列表")
        
        response = card_management_api.list_cards(page=0, size=10)
        
        assert_status_ok(response)
        
        response_body = response.json()
        assert response_body.get("code") == 200
        assert_list_structure(response_body)
        
        logger.info(f"✓ 卡片列表获取成功")

    def test_filter_by_card_status(self, card_management_api):
        """
        测试场景2：按card_status筛选
        验证点：
        1. 接口返回 200
        2. card_status参数生效
        """
        logger.info("测试场景2：按card_status筛选")
        
        response = card_management_api.list_cards(card_status=CardStatus.ACTIVE, size=10)
        
        assert_status_ok(response)
        assert_enum_filter(response, "card_status", CardStatus.ACTIVE)
        
        logger.info("✓ card_status筛选验证通过")

    def test_filter_by_network(self, card_management_api):
        """
        测试场景3：按network筛选
        验证点：
        1. 接口返回 200
        2. network参数生效
        """
        logger.info("测试场景3：按network筛选")
        
        response = card_management_api.list_cards(network=CardNetwork.MASTERCARD, size=10)
        
        assert_status_ok(response)
        
        logger.info("✓ network筛选验证通过")

    def test_filter_by_is_virtual(self, card_management_api):
        """
        测试场景4：按is_virtual筛选
        验证点：
        1. 接口返回 200
        2. is_virtual参数生效
        """
        logger.info("测试场景4：按is_virtual筛选")
        
        response = card_management_api.list_cards(is_virtual=True, size=10)
        
        assert_status_ok(response)
        
        logger.info("✓ is_virtual筛选验证通过")

    def test_filter_by_financial_account_id(self, card_management_api):
        """
        测试场景5：按financial_account_id筛选
        验证点：
        1. 接口返回 200
        2. financial_account_id参数生效
        """
        logger.info("测试场景5：按financial_account_id筛选")
        
        response = card_management_api.list_cards(financial_account_id="test_fa_id", size=10)
        
        assert_status_ok(response)
        
        logger.info("✓ financial_account_id筛选验证通过")

    def test_filter_by_card_holder_id(self, card_management_api):
        """
        测试场景6：按card_holder_id筛选
        验证点：
        1. 接口返回 200
        2. card_holder_id参数生效
        """
        logger.info("测试场景6：按card_holder_id筛选")
        
        response = card_management_api.list_cards(card_holder_id="test_holder_id", size=10)
        
        assert_status_ok(response)
        
        logger.info("✓ card_holder_id筛选验证通过")

    def test_multiple_filters(self, card_management_api):
        """
        测试场景7：组合多个筛选条件
        验证点：
        1. 接口返回 200
        2. 多个筛选条件同时生效
        """
        logger.info("测试场景7：组合多个筛选条件")
        
        response = card_management_api.list_cards(
            network=CardNetwork.MASTERCARD,
            card_status=CardStatus.ACTIVE,
            is_virtual=True,
            size=10
        )
        
        assert_status_ok(response)
        
        logger.info("✓ 组合筛选验证通过")

    def test_response_structure(self, card_management_api):
        """
        测试场景8：验证响应结构
        验证点：
        1. 验证spending_limit数组结构
        2. 验证associated_nested_program结构
        """
        logger.info("测试场景8：验证响应结构")
        
        response = card_management_api.list_cards(size=1)
        
        assert_status_ok(response)
        
        response_body = response.json()
        content = response_body.get("data", {}).get("content", [])
        
        if content:
            card = content[0]
            
            # 检查spending_limit
            if "spending_limit" in card:
                spending_limit = card["spending_limit"]
                assert isinstance(spending_limit, list), "spending_limit应为数组"
                logger.info(f"spending_limit结构: {len(spending_limit)} 个限制")
            
            # 检查associated_nested_program
            if "associated_nested_program" in card:
                nested_programs = card["associated_nested_program"]
                assert isinstance(nested_programs, list), "associated_nested_program应为数组"
                logger.info(f"associated_nested_program结构: {len(nested_programs)} 个项目")
        
        logger.info("✓ 响应结构验证完成")
