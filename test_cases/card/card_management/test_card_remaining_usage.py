"""
Card Management - Card Remaining Usage 接口测试用例
测试 GET /api/v1/cores/{core}/card-issuance/cards/:card_number/remaining-usage 接口
"""
import pytest
from utils.logger import logger
from utils.assertions import assert_status_ok


@pytest.mark.card_management
@pytest.mark.detail_api
class TestCardRemainingUsage:
    """
    卡片剩余额度接口测试用例集
    """

    @pytest.mark.skip(reason="需要真实的card_number")
    def test_get_remaining_usage_success(self, card_management_api):
        """
        测试场景1：成功获取剩余额度
        验证点：
        1. 接口返回 200
        2. 返回spending_limit和associated_nested_program
        """
        logger.info("测试场景1：成功获取剩余额度")
        
        response = card_management_api.get_card_remaining_usage("test_card_number")
        
        assert_status_ok(response)
        
        response_body = response.json()
        data = response_body.get("data", {})
        
        assert "spending_limit" in data
        assert "associated_nested_program" in data
        
        logger.info("✓ 剩余额度获取成功")

    @pytest.mark.skip(reason="需要真实数据")
    def test_with_nested_program_id(self, card_management_api):
        """
        测试场景2：指定nested_program_id
        验证点：
        1. nested_program_id参数生效
        """
        logger.info("测试场景2：指定nested_program_id")
        
        response = card_management_api.get_card_remaining_usage(
            "test_card_number",
            nested_program_id="test_nested_id"
        )
        
        assert_status_ok(response)
        
        logger.info("✓ nested_program_id参数验证通过")

    def test_invalid_card_number(self, card_management_api):
        """
        测试场景3：无效的card_number
        验证点：
        1. 接口返回错误
        """
        logger.info("测试场景3：无效的card_number")
        
        response = card_management_api.get_card_remaining_usage("INVALID_CARD_999")
        
        assert response.status_code == 200
        response_body = response.json()
        assert response_body.get("code") != 200
        
        logger.info(f"✓ 正确拒绝无效card_number")

    @pytest.mark.skip(reason="需要真实数据")
    def test_spending_limit_structure(self, card_management_api):
        """
        测试场景4：spending_limit结构验证
        验证点：
        1. amount和count字段存在
        2. interval字段有效
        3. MCC类型包含category
        """
        logger.info("测试场景4：spending_limit结构验证")
        
        response = card_management_api.get_card_remaining_usage("test_card_number")
        
        data = response.json().get("data", {})
        spending_limit = data.get("spending_limit", [])
        
        for limit in spending_limit:
            assert "amount" in limit
            assert "interval" in limit
            
            if limit.get("interval") == "MCC":
                assert "category" in limit, "MCC类型应包含category字段"
        
        logger.info("✓ spending_limit结构验证通过")

    @pytest.mark.skip(reason="需要真实数据")
    def test_nested_program_limits(self, card_management_api):
        """
        测试场景5：嵌套项目限额验证
        验证点：
        1. associated_nested_program数组结构
        2. 每个项目包含id, amount, interval
        """
        logger.info("测试场景5：嵌套项目限额验证")
        
        response = card_management_api.get_card_remaining_usage("test_card_number")
        
        data = response.json().get("data", {})
        nested_programs = data.get("associated_nested_program", [])
        
        for program in nested_programs:
            assert "id" in program
            assert "amount" in program
            assert "interval" in program
        
        logger.info(f"✓ 嵌套项目限额验证通过，共 {len(nested_programs)} 个项目")
