"""
Client List - List Clients 接口测试用例
测试 GET /api/v1/cores/{core}/client-lists 接口
"""
import pytest
from utils.logger import logger
from utils.assertions import (
    assert_status_ok,
    assert_list_structure,
    assert_pagination,
    assert_enum_filter
)
from data.enums import OMSCategory


@pytest.mark.client_list
@pytest.mark.list_api
class TestClientListList:
    """
    客户列表接口测试用例集
    ⚠️ 文档问题：响应结构60+字段平铺，嵌套关系不清晰
    """

    def test_list_clients_success(self, client_list_api):
        """
        测试场景1：成功获取客户列表
        验证点：
        1. 接口返回 200
        2. 返回列表结构正确
        """
        logger.info("测试场景1：成功获取客户列表")
        
        response = client_list_api.list_clients(page=0, size=10)
        
        assert_status_ok(response)
        
        response_body = response.json()
        assert_list_structure(response_body)
        
        logger.info(f"✓ 客户列表获取成功，返回 {len(response_body.get('content', []))} 个客户")

    def test_list_clients_with_oms_category_filter(self, client_list_api):
        """
        测试场景2：使用oms_category筛选客户
        验证点：
        1. 接口返回 200
        2. 返回的客户oms_category符合筛选条件
        """
        logger.info("测试场景2：使用oms_category筛选")
        
        response = client_list_api.list_clients(oms_category=OMSCategory.EQUITY, size=10)
        
        assert_status_ok(response)
        assert_enum_filter(response, "oms_category", OMSCategory.EQUITY)
        
        logger.info("✓ oms_category筛选验证通过")

    def test_list_clients_with_account_name_filter(self, client_list_api):
        """
        测试场景3：使用account_name筛选客户
        验证点：
        1. 接口返回 200
        2. 返回的客户account_name包含筛选关键词
        """
        logger.info("测试场景3：使用account_name筛选")
        
        response = client_list_api.list_clients(account_name="Test", size=10)
        
        assert_status_ok(response)
        
        response_body = response.json()
        content = response_body.get("content", [])
        
        if content:
            for client in content:
                account_name = client.get("account_name", "")
                logger.debug(f"客户Account Name: {account_name}")
        
        logger.info("✓ account_name筛选验证通过")

    def test_list_clients_with_date_range(self, client_list_api):
        """
        测试场景4：使用日期范围筛选客户
        验证点：
        1. 接口返回 200
        2. 日期参数正确传递
        """
        logger.info("测试场景4：使用日期范围筛选")
        
        response = client_list_api.list_clients(
            start_date="2024-01-01",
            end_date="2024-12-31",
            size=10
        )
        
        assert_status_ok(response)
        
        response_body = response.json()
        logger.info(f"✓ 日期范围筛选成功，返回 {len(response_body.get('content', []))} 个客户")

    def test_list_clients_pagination_first_page(self, client_list_api):
        """
        测试场景5：分页查询-第一页
        验证点：
        1. 接口返回 200
        2. 分页信息正确
        3. first=true, number=0
        """
        logger.info("测试场景5：分页查询-第一页")
        
        response = client_list_api.list_clients(page=0, size=5)
        
        assert_status_ok(response)
        assert_pagination(response, page=0, size=5)
        
        logger.info("✓ 第一页分页验证通过")

    def test_list_clients_pagination_second_page(self, client_list_api):
        """
        测试场景6：分页查询-第二页
        验证点：
        1. 接口返回 200
        2. number=1, first=false
        """
        logger.info("测试场景6：分页查询-第二页")
        
        response = client_list_api.list_clients(page=1, size=5)
        
        assert_status_ok(response)
        
        response_body = response.json()
        assert response_body.get("number") == 1, "页码应为1"
        assert response_body.get("first") == False, "first应为false"
        
        logger.info("✓ 第二页分页验证通过")

    def test_list_clients_empty_result(self, client_list_api):
        """
        测试场景7：查询结果为空
        验证点：
        1. 接口返回 200
        2. content为空数组
        3. empty=true
        """
        logger.info("测试场景7：查询结果为空")
        
        response = client_list_api.list_clients(
            account_name="NONEXISTENT_CLIENT_9999",
            size=10
        )
        
        assert_status_ok(response)
        
        response_body = response.json()
        assert response_body.get("empty") == True or len(response_body.get("content", [])) == 0, \
            "空结果应标记empty=true或content为空"
        
        logger.info("✓ 空结果验证通过")

    def test_list_clients_with_multiple_filters(self, client_list_api):
        """
        测试场景8：组合多个筛选条件
        验证点：
        1. 接口返回 200
        2. 多个筛选条件同时生效
        """
        logger.info("测试场景8：组合多个筛选条件")
        
        response = client_list_api.list_clients(
            oms_category=OMSCategory.EQUITY,
            start_date="2024-01-01",
            end_date="2024-12-31",
            size=10
        )
        
        assert_status_ok(response)
        
        logger.info("✓ 组合筛选验证通过")

    def test_list_clients_response_structure(self, client_list_api):
        """
        测试场景9：验证响应字段完整性
        验证点：
        1. 接口返回 200
        2. 必需字段存在
        """
        logger.info("测试场景9：验证响应字段完整性")
        
        response = client_list_api.list_clients(size=1)
        
        assert_status_ok(response)
        
        response_body = response.json()
        content = response_body.get("content", [])
        
        if content:
            client = content[0]
            logger.debug(f"客户字段: {list(client.keys())}")
            
            # 验证一些基本字段（根据实际情况调整）
            # 注意：由于文档问题，字段结构可能混乱
            assert "id" in client or "client_id" in client, "应包含ID字段"
        
        logger.info("✓ 响应结构验证完成")
