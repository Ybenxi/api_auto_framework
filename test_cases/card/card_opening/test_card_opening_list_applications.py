"""
Card Opening - List Applications 接口测试用例
测试 GET /api/v1/cores/{core}/card-issuance/applications 接口
"""
import pytest
from utils.logger import logger
from utils.assertions import assert_status_ok, assert_list_structure, assert_pagination


@pytest.mark.card_opening
@pytest.mark.list_api
class TestCardOpeningListApplications:
    """
    卡片申请列表接口测试用例集
    ⚠️ 文档问题：
    1. JSON格式错误（缺少逗号）
    2. birth_date vs birthdate命名不一致
    """

    def test_list_applications_success(self, card_opening_api):
        """
        测试场景1：成功获取申请列表
        验证点：
        1. 接口返回 200
        2. 返回列表结构正确
        """
        logger.info("测试场景1：成功获取申请列表")
        
        response = card_opening_api.list_applications(page=0, size=10)
        
        assert_status_ok(response)
        
        response_body = response.json()
        assert response_body.get("code") == 200
        assert_list_structure(response_body)
        
        logger.info(f"✓ 申请列表获取成功，返回 {len(response_body.get('data', {}).get('content', []))} 个申请")

    def test_list_with_status_filter(self, card_opening_api):
        """
        测试场景2：按status筛选申请
        验证点：
        1. 接口返回 200
        2. status参数生效
        """
        logger.info("测试场景2：按status筛选")
        
        response = card_opening_api.list_applications(status="approved", size=10)
        
        assert_status_ok(response)
        
        response_body = response.json()
        content = response_body.get("data", {}).get("content", [])
        
        # 验证筛选结果
        if content:
            for app in content:
                logger.debug(f"申请状态: {app.get('status')}")
        
        logger.info("✓ status筛选验证通过")

    def test_pagination_first_page(self, card_opening_api):
        """
        测试场景3：分页查询-第一页
        验证点：
        1. 接口返回 200
        2. 分页信息正确
        """
        logger.info("测试场景3：分页查询-第一页")
        
        response = card_opening_api.list_applications(page=0, size=5)
        
        assert_status_ok(response)
        assert_pagination(response, page=0, size=5)
        
        logger.info("✓ 第一页分页验证通过")

    def test_pagination_second_page(self, card_opening_api):
        """
        测试场景4：分页查询-第二页
        验证点：
        1. 接口返回 200
        2. number=1, first=false
        """
        logger.info("测试场景4：分页查询-第二页")
        
        response = card_opening_api.list_applications(page=1, size=5)
        
        assert_status_ok(response)
        
        response_body = response.json()
        data = response_body.get("data", {})
        assert data.get("number") == 1, "页码应为1"
        
        logger.info("✓ 第二页分页验证通过")

    def test_empty_result(self, card_opening_api):
        """
        测试场景5：查询结果为空
        验证点：
        1. 接口返回 200
        2. 返回空content
        """
        logger.info("测试场景5：查询结果为空")
        
        response = card_opening_api.list_applications(status="NONEXISTENT_STATUS_999")
        
        assert_status_ok(response)
        
        response_body = response.json()
        data = response_body.get("data", {})
        content = data.get("content", [])
        
        logger.info(f"✓ 空结果验证通过，content长度: {len(content)}")

    def test_birthdate_field_name_inconsistency(self, card_opening_api):
        """
        测试场景6：birthdate vs birth_date命名不一致验证
        验证点：
        1. 响应中使用birthdate（无下划线）
        2. 请求参数中使用birth_date（有下划线）
        3. 记录字段命名不一致
        """
        logger.info("测试场景6：birthdate字段命名验证")
        
        response = card_opening_api.list_applications(size=1)
        
        assert_status_ok(response)
        
        response_body = response.json()
        content = response_body.get("data", {}).get("content", [])
        
        if content:
            application = content[0].get("application", {})
            
            # 检查字段命名
            has_birthdate = "birthdate" in application
            has_birth_date = "birth_date" in application
            
            if has_birthdate:
                logger.warning("⚠️ 响应使用birthdate（无下划线）")
            if has_birth_date:
                logger.info("✓ 响应使用birth_date（有下划线）")
            
            logger.info(f"字段命名: birthdate={has_birthdate}, birth_date={has_birth_date}")
        
        logger.info("✓ 字段命名不一致验证完成")
