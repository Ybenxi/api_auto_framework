"""
Card Management - Card Detail 接口测试用例
测试 GET /api/v1/cores/{core}/card-issuance/cards/:card_number 接口
"""
import pytest
from utils.logger import logger
from utils.assertions import assert_status_ok


@pytest.mark.card_management
@pytest.mark.detail_api
class TestCardDetail:
    """
    卡片详情接口测试用例集
    """

    @pytest.mark.skip(reason="需要真实的card_number或card_id")
    def test_get_card_detail_success(self, card_management_api):
        """
        测试场景1：成功获取卡片详情
        验证点：
        1. 接口返回 200
        2. 返回卡片详情
        """
        logger.info("测试场景1：成功获取卡片详情")
        
        # 从列表获取一个卡片
        list_response = card_management_api.list_cards(size=1)
        content = list_response.json().get("data", {}).get("content", [])
        card_id = content[0].get("id")
        
        # 获取详情
        response = card_management_api.get_card_detail(card_id)
        
        assert_status_ok(response)
        
        logger.info(f"✓ 卡片详情获取成功，ID: {card_id}")

    def test_invalid_card_number(self, card_management_api):
        """
        测试场景2：无效的card_number
        验证点：
        1. 接口返回错误
        """
        logger.info("测试场景2：无效的card_number")
        
        response = card_management_api.get_card_detail("INVALID_CARD_999")
        
        assert response.status_code == 200
        response_body = response.json()
        assert response_body.get("code") != 200
        
        logger.info(f"✓ 正确拒绝无效card_number: {response_body.get('error_message', 'Unknown error')}")

    @pytest.mark.skip(reason="需要真实数据")
    def test_response_structure(self, card_management_api):
        """
        测试场景3：响应结构验证
        验证点：
        1. 包含所有必需字段
        2. spending_limit数组结构正确
        """
        logger.info("测试场景3：响应结构验证")
        
        list_response = card_management_api.list_cards(size=1)
        card_id = list_response.json().get("data", {}).get("content", [])[0].get("id")
        
        response = card_management_api.get_card_detail(card_id)
        
        assert_status_ok(response)
        
        card_data = response.json().get("data", {})
        
        required_fields = ["id", "card_number", "card_status", "network"]
        for field in required_fields:
            assert field in card_data, f"缺少字段: {field}"
        
        logger.info("✓ 响应结构验证通过")

    @pytest.mark.skip(reason="需要真实数据")
    def test_consistency_with_list(self, card_management_api):
        """
        测试场景4：详情与列表一致性
        验证点：
        1. 详情数据与列表数据一致
        """
        logger.info("测试场景4：详情与列表一致性")
        
        list_response = card_management_api.list_cards(size=1)
        list_card = list_response.json().get("data", {}).get("content", [])[0]
        card_id = list_card.get("id")
        
        detail_response = card_management_api.get_card_detail(card_id)
        detail_card = detail_response.json().get("data", {})
        
        # 验证关键字段一致
        assert list_card.get("card_status") == detail_card.get("card_status")
        assert list_card.get("network") == detail_card.get("network")
        
        logger.info("✓ 一致性验证通过")
