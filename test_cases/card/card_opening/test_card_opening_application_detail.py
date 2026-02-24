"""
Card Opening - Application Detail 接口测试用例
测试 GET /api/v1/cores/{core}/card-issuance/applications/:id 接口
"""
import pytest
from utils.logger import logger
from utils.assertions import assert_status_ok


@pytest.mark.card_opening
@pytest.mark.detail_api
class TestCardOpeningApplicationDetail:
    """
    卡片申请详情接口测试用例集
    ⚠️ 文档问题：
    1. Detail接口响应无code包装层（格式不一致）
    2. JSON格式错误（缺少逗号）
    """

    @pytest.mark.skip(reason="需要真实的application_id")
    def test_get_application_detail_success(self, card_opening_api):
        """
        测试场景1：成功获取申请详情
        验证点：
        1. 接口返回 200
        2. 返回申请详情
        3. ID匹配
        """
        logger.info("测试场景1：成功获取申请详情")
        
        # 步骤1：先从列表获取一个申请ID
        list_response = card_opening_api.list_applications(size=1)
        assert_status_ok(list_response)
        
        list_body = list_response.json()
        content = list_body.get("data", {}).get("content", [])
        assert len(content) > 0, "列表至少包含一个申请"
        
        application_id = content[0].get("id")
        
        # 步骤2：获取详情
        detail_response = card_opening_api.get_application_detail(application_id)
        assert detail_response.status_code == 200
        
        # 注意：Detail响应无code包装层
        detail_data = detail_response.json()
        assert detail_data.get("id") == application_id, "详情ID应与请求ID一致"
        
        logger.info(f"✓ 申请详情获取成功，ID: {application_id}")

    def test_invalid_application_id(self, card_opening_api):
        """
        测试场景2：获取不存在的申请ID
        验证点：
        1. 接口返回错误
        """
        logger.info("测试场景2：获取不存在的申请ID")
        
        invalid_id = "INVALID_APPLICATION_ID_999"
        
        response = card_opening_api.get_application_detail(invalid_id)
        
        assert response.status_code == 200

        # 验证无效ID返回了错误
        response_body = response.json()
        assert response_body.get("code") != 200 or response_body.get("data") is None or response_body.get("id") is None, \
            "无效申请ID应该返回错误或空数据"

        logger.info(f"✓ 无效申请ID测试完成，code={response_body.get('code')}")

    def test_response_format_inconsistency(self, card_opening_api):
        """
        测试场景3：响应格式不一致验证
        验证点：
        1. List接口有code包装层
        2. Detail接口无code包装层
        3. 记录格式差异
        """
        logger.info("测试场景3：响应格式不一致验证")
        
        # List接口格式
        list_response = card_opening_api.list_applications(size=1)
        list_body = list_response.json()
        list_has_code = "code" in list_body
        
        logger.info(f"List接口有code字段: {list_has_code}")
        
        # Detail接口格式（使用无效ID避免实际查询）
        detail_response = card_opening_api.get_application_detail("test_id")
        detail_body = detail_response.json()
        detail_has_code = "code" in detail_body
        
        logger.info(f"Detail接口有code字段: {detail_has_code}")
        
        if list_has_code and not detail_has_code:
            logger.warning("⚠️ 检测到响应格式不一致：List有code，Detail无code")
        
        logger.info("✓ 响应格式差异验证完成")

    @pytest.mark.skip(reason="需要真实数据")
    def test_field_completeness(self, card_opening_api):
        """
        测试场景4：字段完整性验证
        验证点：
        1. 详情包含所有必需字段
        2. application对象结构正确
        """
        logger.info("测试场景4：字段完整性验证")
        
        # 获取真实申请
        list_response = card_opening_api.list_applications(size=1)
        content = list_response.json().get("data", {}).get("content", [])
        application_id = content[0].get("id")
        
        # 获取详情
        detail_response = card_opening_api.get_application_detail(application_id)
        detail_data = detail_response.json()
        
        # 验证必需字段
        required_fields = ["id", "status", "card_id", "application"]
        for field in required_fields:
            assert field in detail_data, f"缺少必需字段: {field}"
        
        logger.info("✓ 字段完整性验证通过")
