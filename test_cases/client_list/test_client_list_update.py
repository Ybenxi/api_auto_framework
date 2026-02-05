"""
Client List - Update Client 接口测试用例
测试 PATCH /api/v1/cores/{core}/client-lists/{client_id} 接口
"""
import pytest
from utils.logger import logger
from utils.assertions import assert_status_ok


@pytest.mark.client_list
@pytest.mark.update_api
@pytest.mark.skip(reason="需要真实的client_id，待完善数据准备")
class TestClientListUpdate:
    """
    更新客户接口测试用例集
    """

    def test_update_client_single_field(self, client_list_api):
        """
        测试场景1：更新单个字段
        验证点：
        1. 接口返回 200
        2. 字段更新成功
        3. 其他字段保持不变
        """
        logger.info("测试场景1：更新单个字段")
        
        # 步骤1：创建客户
        import time
        timestamp = int(time.time())
        client_data = {
            "account_id": "test_account_id",
            "oms_category": "Equity",
            "account_name": f"Auto TestYan Client {timestamp}"
        }
        
        create_response = client_list_api.create_client(client_data)
        assert_status_ok(create_response)
        
        client_id = create_response.json().get("data", create_response.json()).get("id")
        
        # 步骤2：更新account_name
        update_data = {
            "account_name": f"Auto TestYan Updated Client {timestamp}"
        }
        
        update_response = client_list_api.update_client(client_id, update_data)
        assert_status_ok(update_response)
        
        update_body = update_response.json()
        updated_data = update_body.get("data", update_body)
        
        assert updated_data.get("account_name") == update_data["account_name"], \
            "account_name应更新成功"
        assert updated_data.get("oms_category") == "Equity", \
            "oms_category应保持不变"
        
        logger.info("✓ 单字段更新成功")

    def test_update_client_multiple_fields(self, client_list_api):
        """
        测试场景2：同时更新多个字段
        验证点：
        1. 接口返回 200
        2. 所有字段都正确更新
        """
        logger.info("测试场景2：同时更新多个字段")
        
        # 步骤1：创建客户
        import time
        timestamp = int(time.time())
        client_data = {
            "account_id": "test_account_id",
            "oms_category": "Equity",
            "account_name": f"Auto TestYan Client {timestamp}"
        }
        
        create_response = client_list_api.create_client(client_data)
        client_id = create_response.json().get("data", create_response.json()).get("id")
        
        # 步骤2：更新多个字段
        update_data = {
            "account_name": f"Auto TestYan Updated Client {timestamp}",
            "oms_category": "Mutual Fund"
        }
        
        update_response = client_list_api.update_client(client_id, update_data)
        assert_status_ok(update_response)
        
        updated_data = update_response.json().get("data", update_response.json())
        
        assert updated_data.get("account_name") == update_data["account_name"]
        assert updated_data.get("oms_category") == "Mutual Fund"
        
        logger.info("✓ 多字段同时更新成功")

    def test_update_client_invalid_id(self, client_list_api):
        """
        测试场景3：更新不存在的客户ID
        验证点：
        1. 接口返回错误
        2. code为404或其他错误码
        """
        logger.info("测试场景3：更新不存在的客户ID")
        
        invalid_client_id = "INVALID_CLIENT_ID_999"
        update_data = {
            "account_name": "Updated Name"
        }
        
        response = client_list_api.update_client(invalid_client_id, update_data)
        
        assert response.status_code == 200, "HTTP状态码应为200"
        response_body = response.json()
        assert response_body.get("code") != 200, "业务code应不为200"
        
        logger.info(f"✓ 正确拒绝无效的客户ID: {response_body.get('error_message', 'Unknown error')}")

    def test_update_client_invalid_field_value(self, client_list_api):
        """
        测试场景4：更新为无效的字段值
        验证点：
        1. 接口返回错误
        2. 提示字段值无效
        """
        logger.info("测试场景4：更新为无效的字段值")
        
        fake_client_id = "fake_client_id"
        update_data = {
            "oms_category": "Invalid_Category"
        }
        
        response = client_list_api.update_client(fake_client_id, update_data)
        
        assert response.status_code == 200
        response_body = response.json()
        assert response_body.get("code") != 200
        
        logger.info(f"✓ 正确拒绝无效字段值: {response_body.get('error_message', 'Unknown error')}")

    def test_update_client_oms_category(self, client_list_api):
        """
        测试场景5：更新oms_category
        验证点：
        1. 接口返回 200
        2. oms_category正确更新
        """
        logger.info("测试场景5：更新oms_category")
        
        # 步骤1：创建客户
        import time
        timestamp = int(time.time())
        client_data = {
            "account_id": "test_account_id",
            "oms_category": "Equity",
            "account_name": f"Auto TestYan Client {timestamp}"
        }
        
        create_response = client_list_api.create_client(client_data)
        client_id = create_response.json().get("data", create_response.json()).get("id")
        
        # 步骤2：更新为Bond类别
        update_data = {
            "oms_category": "Bond"
        }
        
        update_response = client_list_api.update_client(client_id, update_data)
        assert_status_ok(update_response)
        
        updated_data = update_response.json().get("data", update_response.json())
        assert updated_data.get("oms_category") == "Bond"
        
        logger.info("✓ oms_category更新成功")
