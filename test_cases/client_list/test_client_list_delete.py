"""
Client List - Delete Client 接口测试用例
测试 DELETE /api/v1/cores/{core}/client-lists/{client_id} 接口
"""
import pytest
from utils.logger import logger
from utils.assertions import assert_status_ok


@pytest.mark.client_list
@pytest.mark.delete_api
@pytest.mark.no_rerun
class TestClientListDelete:
    """
    删除客户接口测试用例集
    ⚠️ 破坏性操作：删除客户是不可逆的，大部分测试标记为skip
    """

    @pytest.mark.skip(reason="破坏性操作，需要真实数据，待完善数据准备")
    def test_delete_client_success(self, client_list_api):
        """
        测试场景1：成功删除客户
        验证点：
        1. 接口返回 200
        2. 客户被成功删除
        3. 再次查询返回404
        """
        logger.info("测试场景1：成功删除客户")
        
        # 步骤1：创建一个客户
        import time
        timestamp = int(time.time())
        client_data = {
            "account_id": "test_account_id",
            "oms_category": "Equity",
            "account_name": f"Auto TestYan Delete Client {timestamp}"
        }
        
        create_response = client_list_api.create_client(client_data)
        assert_status_ok(create_response)
        
        client_id = create_response.json().get("data", create_response.json()).get("id")
        
        # 步骤2：删除客户
        delete_response = client_list_api.delete_client(client_id)
        assert_status_ok(delete_response)
        
        logger.info(f"✓ 客户删除成功，ID: {client_id}")
        
        # 步骤3：验证删除（再次查询应返回404）
        detail_response = client_list_api.get_client_detail(client_id)
        detail_body = detail_response.json()
        assert detail_body.get("code") != 200, "删除后查询应返回错误"
        
        logger.info("✓ 删除验证通过")

    def test_delete_client_invalid_id(self, client_list_api):
        """
        测试场景2：删除不存在的客户ID
        验证点：
        1. 接口返回错误
        2. code为404或其他错误码
        """
        logger.info("测试场景2：删除不存在的客户ID")
        
        invalid_client_id = "INVALID_CLIENT_ID_999"
        
        response = client_list_api.delete_client(invalid_client_id)
        
        assert response.status_code == 200, "HTTP状态码应为200"
        response_body = response.json()
        assert response_body.get("code") != 200, "业务code应不为200"
        
        logger.info(f"✓ 正确拒绝无效的客户ID: {response_body.get('error_message', 'Unknown error')}")

    @pytest.mark.skip(reason="破坏性操作，需要真实数据")
    def test_delete_client_idempotent(self, client_list_api):
        """
        测试场景3：重复删除客户（幂等性测试）
        验证点：
        1. 第二次删除返回错误或幂等成功
        """
        logger.info("测试场景3：重复删除客户")
        
        # 需要一个已删除的客户ID
        deleted_client_id = "test_deleted_client_id"
        
        response = client_list_api.delete_client(deleted_client_id)
        
        assert response.status_code == 200
        response_body = response.json()
        
        # 可能返回错误（客户不存在）或幂等成功
        if response_body.get("code") == 200:
            logger.info("✓ 重复删除幂等成功")
        else:
            logger.info(f"✓ 重复删除返回错误: {response_body.get('error_message', 'Unknown error')}")

    @pytest.mark.skip(reason="破坏性操作，需要真实数据")
    def test_delete_client_with_dependencies(self, client_list_api):
        """
        测试场景4：删除有关联数据的客户
        验证点：
        1. 接口行为符合预期
        2. 可能级联删除或拒绝删除
        """
        logger.info("测试场景4：删除有关联数据的客户")
        
        # 需要一个有关联数据的客户ID
        client_with_dependencies = "test_client_with_deps"
        
        response = client_list_api.delete_client(client_with_dependencies)
        
        assert response.status_code == 200
        response_body = response.json()
        
        if response_body.get("code") == 200:
            logger.info("✓ 系统允许删除（可能级联删除关联数据）")
        else:
            logger.info(f"✓ 系统拒绝删除有关联数据的客户: {response_body.get('error_message', 'Unknown error')}")
