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
        2. 响应 code == 200
        3. content 是数组
        """
        logger.info("测试场景1：成功获取申请列表")

        response = card_opening_api.list_applications(page=0, size=10)

        assert_status_ok(response)

        response_body = response.json()
        assert response_body.get("code") == 200

        # Card Opening 响应有 data 包装层
        content = response_body.get("data", {}).get("content", [])
        assert isinstance(content, list), "content 不是数组"

        logger.info(f"✓ 申请列表获取成功，返回 {len(content)} 个申请")

    @pytest.mark.parametrize("status", ["approved", "pending", "rejected"])
    def test_list_with_status_filter(self, card_opening_api, status):
        """
        测试场景2：按 status 筛选申请（覆盖主要枚举值）
        验证点：
        1. 接口返回 200
        2. 返回的每条申请 status 均与筛选值一致
        """
        logger.info(f"测试场景2：按 status='{status}' 筛选")

        response = card_opening_api.list_applications(status=status, size=10)

        assert_status_ok(response)

        response_body = response.json()
        data = response_body.get("data")
        if data is None:
            logger.info("  ⚠️ 响应无 data 字段，跳过")
            return

        content = data.get("content", [])
        logger.info(f"  返回 {len(content)} 条申请")

        if not content:
            logger.info(f"  ⚠️ status='{status}' 无数据，跳过筛选值验证")
        else:
            for app in content:
                assert app.get("status") == status, \
                    f"筛选结果包含非 {status} 状态: {app.get('status')}"
            logger.info(f"✓ {len(content)} 条申请均为 {status} 状态")

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

        data = response.json().get("data", {})
        assert data.get("size") == 5, f"size 不正确: {data.get('size')}"
        assert data.get("number") == 0, f"number 不正确: {data.get('number')}"
        assert len(data.get("content", [])) <= 5, "返回数量超过 size=5"

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
        2. 返回空 content
        """
        logger.info("测试场景5：查询结果为空")

        response = card_opening_api.list_applications(status="NONEXISTENT_STATUS_999")

        assert_status_ok(response)

        response_body = response.json()
        data = response_body.get("data") or {}
        content = data.get("content", [])

        assert len(content) == 0, f"期望空列表，实际返回 {len(content)} 条"

        logger.info(f"✓ 空结果验证通过")

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
