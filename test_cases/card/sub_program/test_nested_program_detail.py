"""
Sub Program - Nested Program Detail 接口测试用例
测试 GET /api/v1/cores/{core}/card-issuance/nested-programs/:id 接口
"""
import pytest
from utils.logger import logger
from utils.assertions import assert_status_ok


@pytest.mark.sub_program
@pytest.mark.detail_api
class TestNestedProgramDetail:
    """
    嵌套项目详情接口测试用例集
    """

    @pytest.mark.skip(reason="需要真实的nested_program_id")
    def test_get_nested_program_detail_success(self, sub_program_api):
        """
        测试场景1：成功获取嵌套项目详情
        验证点：
        1. 接口返回 200
        2. 返回详情数据
        """
        logger.info("测试场景1：成功获取嵌套项目详情")
        
        response = sub_program_api.get_nested_program_detail("test_nested_id")
        
        assert_status_ok(response)
        
        response_body = response.json()
        assert response_body.get("code") == 200
        
        logger.info(f"✓ 嵌套项目详情获取成功")

    def test_invalid_nested_program_id(self, sub_program_api):
        """
        测试场景2：无效的nested_program_id
        验证点：
        1. 接口返回错误
        """
        logger.info("测试场景2：无效的nested_program_id")
        
        response = sub_program_api.get_nested_program_detail("INVALID_NESTED_999")
        
        assert response.status_code == 200
        response_body = response.json()
        assert response_body.get("code") != 200
        
        logger.info(f"✓ 正确拒绝无效ID")

    @pytest.mark.skip(reason="需要真实数据")
    def test_field_completeness(self, sub_program_api):
        """
        测试场景3：字段完整性验证
        验证点：
        1. 包含所有必需字段
        """
        logger.info("测试场景3：字段完整性验证")
        
        response = sub_program_api.get_nested_program_detail("test_nested_id")
        
        data = response.json().get("data", {})
        
        required_fields = ["id", "name", "status", "spending_limit"]
        for field in required_fields:
            assert field in data, f"缺少字段: {field}"
        
        logger.info("✓ 字段完整性验证通过")

    @pytest.mark.skip(reason="需要真实数据")
    def test_consistency_with_list(self, sub_program_api):
        """
        测试场景4：详情与列表一致性
        验证点：
        1. 关键字段值一致
        """
        logger.info("测试场景4：详情与列表一致性")
        
        # 从列表获取
        list_response = sub_program_api.list_nested_programs("test_sub_program_id", size=1)
        list_content = list_response.json().get("data", {}).get("content", [])
        nested_id = list_content[0].get("id")
        
        # 获取详情
        detail_response = sub_program_api.get_nested_program_detail(nested_id)
        detail_data = detail_response.json().get("data", {})
        
        # 验证一致性
        assert list_content[0].get("name") == detail_data.get("name")
        assert list_content[0].get("status") == detail_data.get("status")
        
        logger.info("✓ 一致性验证通过")
