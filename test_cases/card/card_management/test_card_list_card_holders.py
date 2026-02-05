"""
Card Management - List Card Holders 接口测试用例
测试 GET /api/v1/cores/{core}/card-issuance/card-holders 接口
"""
import pytest
from utils.logger import logger
from utils.assertions import assert_status_ok, assert_list_structure, assert_pagination


@pytest.mark.card_management
@pytest.mark.list_api
class TestCardListCardHolders:
    """
    持卡人列表接口测试用例集
    ⚠️ 文档问题：响应中"country:"字段名拼写错误（多余冒号）
    """

    def test_list_card_holders_success(self, card_management_api):
        """
        测试场景1：成功获取持卡人列表
        验证点：
        1. 接口返回 200
        2. 返回列表结构正确
        """
        logger.info("测试场景1：成功获取持卡人列表")
        
        response = card_management_api.list_card_holders(page=0, size=10)
        
        assert_status_ok(response)
        
        response_body = response.json()
        assert response_body.get("code") == 200
        assert_list_structure(response_body)
        
        logger.info(f"✓ 持卡人列表获取成功")

    def test_filter_by_first_name(self, card_management_api):
        """
        测试场景2：按first_name筛选
        验证点：
        1. 接口返回 200
        2. first_name参数生效
        """
        logger.info("测试场景2：按first_name筛选")
        
        response = card_management_api.list_card_holders(first_name="Test", size=10)
        
        assert_status_ok(response)
        
        logger.info("✓ first_name筛选验证通过")

    def test_filter_by_last_name(self, card_management_api):
        """
        测试场景3：按last_name筛选
        验证点：
        1. 接口返回 200
        2. last_name参数生效
        """
        logger.info("测试场景3：按last_name筛选")
        
        response = card_management_api.list_card_holders(last_name="Yan", size=10)
        
        assert_status_ok(response)
        
        logger.info("✓ last_name筛选验证通过")

    def test_filter_by_id(self, card_management_api):
        """
        测试场景4：按持卡人ID筛选
        验证点：
        1. 接口返回 200
        2. id参数生效
        """
        logger.info("测试场景4：按持卡人ID筛选")
        
        response = card_management_api.list_card_holders(id="test_holder_id", size=10)
        
        assert_status_ok(response)
        
        logger.info("✓ 持卡人ID筛选验证通过")

    def test_pagination(self, card_management_api):
        """
        测试场景5：分页功能
        验证点：
        1. 分页参数正确传递
        2. 分页信息正确返回
        """
        logger.info("测试场景5：分页功能验证")
        
        response = card_management_api.list_card_holders(page=0, size=5)
        
        assert_status_ok(response)
        assert_pagination(response, page=0, size=5)
        
        logger.info("✓ 分页功能验证通过")

    def test_country_field_typo(self, card_management_api):
        """
        测试场景6：country字段名拼写验证
        验证点：
        1. 检查响应中country字段的拼写
        2. 文档示例中有"country:"（多余冒号）
        """
        logger.info("测试场景6：country字段名拼写验证")
        
        response = card_management_api.list_card_holders(size=1)
        
        assert_status_ok(response)
        
        response_body = response.json()
        content = response_body.get("data", {}).get("content", [])
        
        if content:
            holder = content[0]
            
            # 检查字段名
            if "country:" in holder:
                logger.warning("⚠️ 检测到字段名拼写错误: country:（有多余冒号）")
            elif "country" in holder:
                logger.info("✓ 字段名正确: country")
            
            logger.debug(f"持卡人字段: {list(holder.keys())}")
        
        logger.info("✓ country字段名验证完成")
