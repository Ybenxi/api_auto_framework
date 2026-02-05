"""
Card Dispute - Dispute Detail 接口测试用例
测试 GET /api/v1/cores/{core}/card-issuance/disputes/:dispute_id 接口
"""
import pytest
from utils.logger import logger
from utils.assertions import assert_status_ok


@pytest.mark.card_dispute_risk
@pytest.mark.detail_api
class TestCardDisputeDetail:
    """
    争议详情接口测试用例集
    """

    @pytest.mark.skip(reason="需要真实的dispute_id")
    def test_get_dispute_detail_success(self, card_dispute_api):
        """
        测试场景1：成功获取争议详情
        验证点：
        1. 接口返回 200
        2. 返回详情数据
        """
        logger.info("测试场景1：成功获取争议详情")
        
        # 从列表获取dispute_id
        list_response = card_dispute_api.list_disputes(size=1)
        content = list_response.json().get("data", {}).get("content", [])
        dispute_id = content[0].get("id")
        
        # 获取详情
        response = card_dispute_api.get_dispute_detail(dispute_id)
        
        assert_status_ok(response)
        
        logger.info(f"✓ 争议详情获取成功，ID: {dispute_id}")

    def test_invalid_dispute_id(self, card_dispute_api):
        """
        测试场景2：无效的dispute_id
        验证点：
        1. 接口返回错误
        """
        logger.info("测试场景2：无效的dispute_id")
        
        response = card_dispute_api.get_dispute_detail("INVALID_DISPUTE_999")
        
        assert response.status_code == 200
        response_body = response.json()
        assert response_body.get("code") != 200
        
        logger.info(f"✓ 正确拒绝无效ID")

    @pytest.mark.skip(reason="需要真实数据")
    def test_field_completeness(self, card_dispute_api):
        """
        测试场景3：字段完整性验证
        验证点：
        1. 包含所有必需字段
        """
        logger.info("测试场景3：字段完整性验证")
        
        list_response = card_dispute_api.list_disputes(size=1)
        content = list_response.json().get("data", {}).get("content", [])
        dispute_id = content[0].get("id")
        
        response = card_dispute_api.get_dispute_detail(dispute_id)
        
        data = response.json().get("data", {})
        
        required_fields = ["id", "card_id", "original_transaction_id", "disputed_amount", "status"]
        for field in required_fields:
            assert field in data, f"缺少字段: {field}"
        
        logger.info("✓ 字段完整性验证通过")

    @pytest.mark.skip(reason="需要真实数据")
    def test_consistency_with_list(self, card_dispute_api):
        """
        测试场景4：详情与列表一致性
        验证点：
        1. 关键字段值一致
        """
        logger.info("测试场景4：详情与列表一致性")
        
        list_response = card_dispute_api.list_disputes(size=1)
        list_content = list_response.json().get("data", {}).get("content", [])
        list_dispute = list_content[0]
        dispute_id = list_dispute.get("id")
        
        detail_response = card_dispute_api.get_dispute_detail(dispute_id)
        detail_dispute = detail_response.json().get("data", {})
        
        # 验证一致性
        assert list_dispute.get("card_id") == detail_dispute.get("card_id")
        assert list_dispute.get("status") == detail_dispute.get("status")
        
        logger.info("✓ 一致性验证通过")
