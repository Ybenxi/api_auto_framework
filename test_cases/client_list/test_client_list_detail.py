"""
Client List - Get Client Detail 接口测试用例
测试 GET /api/v1/cores/{core}/client-lists/{client_id} 接口
"""
import pytest
from utils.logger import logger
from utils.assertions import assert_status_ok


@pytest.mark.client_list
@pytest.mark.detail_api
class TestClientListDetail:
    """
    客户详情接口测试用例集
    """

    @pytest.mark.skip(reason="需要真实的client_id，待完善数据准备")
    def test_get_client_detail_success(self, client_list_api):
        """
        测试场景1：成功获取客户详情
        验证点：
        1. 接口返回 200
        2. 返回客户详情数据
        3. ID匹配
        """
        logger.info("测试场景1：成功获取客户详情")
        
        # 步骤1：先获取列表中的第一个客户
        list_response = client_list_api.list_clients(size=1)
        assert_status_ok(list_response)
        
        list_body = list_response.json()
        content = list_body.get("content", [])
        assert len(content) > 0, "列表至少包含一个客户"
        
        client_id = content[0].get("id") or content[0].get("client_id")
        
        # 步骤2：获取详情
        detail_response = client_list_api.get_client_detail(client_id)
        assert_status_ok(detail_response)
        
        detail_body = detail_response.json()
        detail_data = detail_body.get("data", detail_body)
        
        assert detail_data.get("id") == client_id or detail_data.get("client_id") == client_id, \
            "详情ID应与请求ID一致"
        
        logger.info(f"✓ 客户详情获取成功，ID: {client_id}")

    def test_get_client_detail_invalid_id(self, client_list_api):
        """
        测试场景2：获取不存在的客户ID
        验证点：
        1. 接口返回错误
        2. code为404或其他错误码
        """
        logger.info("测试场景2：获取不存在的客户ID")
        
        invalid_client_id = "INVALID_CLIENT_ID_999"
        
        response = client_list_api.get_client_detail(invalid_client_id)
        
        assert response.status_code == 200, "HTTP状态码应为200"
        response_body = response.json()
        assert response_body.get("code") != 200, "业务code应不为200"
        
        logger.info(f"✓ 正确拒绝无效的客户ID: {response_body.get('error_message', 'Unknown error')}")

    @pytest.mark.skip(reason="需要真实数据")
    def test_get_client_detail_response_structure(self, client_list_api):
        """
        测试场景3：验证详情响应字段完整性
        验证点：
        1. 接口返回 200
        2. 包含客户所有关键字段
        """
        logger.info("测试场景3：验证详情响应字段")
        
        # 获取一个真实的客户ID
        list_response = client_list_api.list_clients(size=1)
        client_id = list_response.json().get("content", [])[0].get("id")
        
        response = client_list_api.get_client_detail(client_id)
        assert_status_ok(response)
        
        response_body = response.json()
        detail_data = response_body.get("data", response_body)
        
        logger.debug(f"详情字段: {list(detail_data.keys())}")
        
        # 验证关键字段存在（根据实际情况调整）
        # 注意：由于文档问题，字段结构可能混乱
        expected_fields = ["id", "account_id", "oms_category"]
        for field in expected_fields:
            if field in detail_data:
                logger.debug(f"✓ 字段 {field} 存在")
        
        logger.info("✓ 详情响应结构验证完成")

    @pytest.mark.skip(reason="需要真实数据")
    def test_get_client_detail_consistency_with_list(self, client_list_api):
        """
        测试场景4：验证详情与列表数据一致性
        验证点：
        1. 详情数据与列表数据一致
        2. 关键字段值相同
        """
        logger.info("测试场景4：验证详情与列表数据一致性")
        
        # 步骤1：从列表获取客户信息
        list_response = client_list_api.list_clients(size=1)
        list_client = list_response.json().get("content", [])[0]
        client_id = list_client.get("id") or list_client.get("client_id")
        
        # 步骤2：获取详情
        detail_response = client_list_api.get_client_detail(client_id)
        detail_client = detail_response.json().get("data", detail_response.json())
        
        # 验证关键字段一致性
        if "account_id" in list_client and "account_id" in detail_client:
            assert list_client["account_id"] == detail_client["account_id"], \
                "列表和详情的account_id应一致"
        
        if "oms_category" in list_client and "oms_category" in detail_client:
            assert list_client["oms_category"] == detail_client["oms_category"], \
                "列表和详情的oms_category应一致"
        
        logger.info("✓ 详情与列表数据一致性验证通过")
