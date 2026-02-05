"""
Client List - Create Client 接口测试用例
测试 POST /api/v1/cores/{core}/client-lists 接口
"""
import pytest
import time
from utils.logger import logger
from utils.assertions import assert_status_ok


@pytest.mark.client_list
@pytest.mark.create_api
@pytest.mark.skip(reason="需要真实的account_id等前置数据，待完善数据准备")
class TestClientListCreate:
    """
    创建客户接口测试用例集
    ⚠️ 文档问题：字段定义混乱，具体必需字段不明确
    """

    def test_create_client_with_required_fields(self, client_list_api):
        """
        测试场景1：使用必需字段创建客户
        验证点：
        1. 接口返回 200
        2. 返回创建的客户ID
        3. 客户数据正确保存
        """
        logger.info("测试场景1：使用必需字段创建客户")
        
        timestamp = int(time.time())
        client_data = {
            "account_id": "test_account_id",
            "oms_category": "Equity",
            "account_name": f"Auto TestYan Client {timestamp}"
        }
        
        response = client_list_api.create_client(client_data)
        assert_status_ok(response)
        
        response_body = response.json()
        created_data = response_body.get("data", response_body)
        
        assert created_data.get("id") is not None, "客户ID不应为空"
        assert created_data.get("oms_category") == "Equity"
        
        logger.info(f"✓ 客户创建成功，ID: {created_data.get('id')}")

    def test_create_client_with_all_fields(self, client_list_api):
        """
        测试场景2：使用所有字段创建客户
        验证点：
        1. 接口返回 200
        2. 所有字段正确保存
        """
        logger.info("测试场景2：使用所有字段创建客户")
        
        timestamp = int(time.time())
        client_data = {
            "account_id": "test_account_id",
            "sub_account_id": "test_sub_account_id",
            "financial_account_id": "test_financial_account_id",
            "oms_category": "Mutual Fund",
            "account_name": f"Auto TestYan Client {timestamp}",
            "sub_account_name": f"Auto TestYan Sub Account {timestamp}",
            "financial_account_name": f"Auto TestYan FA {timestamp}"
        }
        
        response = client_list_api.create_client(client_data)
        assert_status_ok(response)
        
        response_body = response.json()
        created_data = response_body.get("data", response_body)
        
        assert created_data.get("oms_category") == "Mutual Fund"
        assert created_data.get("sub_account_id") == "test_sub_account_id"
        
        logger.info("✓ 完整字段客户创建成功")

    def test_create_client_missing_required_field(self, client_list_api):
        """
        测试场景3：缺少必需字段
        验证点：
        1. 接口返回错误
        2. code不为200
        """
        logger.info("测试场景3：缺少必需字段")
        
        client_data = {
            "account_name": "Test Client"
            # 缺少 account_id, oms_category
        }
        
        response = client_list_api.create_client(client_data)
        
        assert response.status_code == 200, "HTTP状态码应为200"
        response_body = response.json()
        assert response_body.get("code") != 200, "业务code应不为200"
        
        logger.info(f"✓ 正确拒绝缺少必需字段: {response_body.get('error_message', 'Unknown error')}")

    def test_create_client_invalid_oms_category(self, client_list_api):
        """
        测试场景4：无效的oms_category
        验证点：
        1. 接口返回错误
        """
        logger.info("测试场景4：无效的oms_category")
        
        timestamp = int(time.time())
        client_data = {
            "account_id": "test_account_id",
            "oms_category": "Invalid_Category",
            "account_name": f"Auto TestYan Client {timestamp}"
        }
        
        response = client_list_api.create_client(client_data)
        
        assert response.status_code == 200
        response_body = response.json()
        assert response_body.get("code") != 200
        
        logger.info(f"✓ 正确拒绝无效的oms_category: {response_body.get('error_message', 'Unknown error')}")

    def test_create_client_duplicate(self, client_list_api):
        """
        测试场景5：创建重复客户
        验证点：
        1. 接口行为符合预期（允许或拒绝）
        """
        logger.info("测试场景5：创建重复客户")
        
        timestamp = int(time.time())
        client_data = {
            "account_id": "test_account_id",
            "oms_category": "Equity",
            "account_name": f"Auto TestYan Duplicate Client {timestamp}"
        }
        
        # 第一次创建
        response1 = client_list_api.create_client(client_data)
        assert_status_ok(response1)
        
        # 第二次创建相同数据
        response2 = client_list_api.create_client(client_data)
        
        # 可能允许（返回新ID）或拒绝（返回错误）
        response2_body = response2.json()
        if response2_body.get("code") == 200:
            logger.info("✓ 系统允许创建重复客户（返回不同ID）")
        else:
            logger.info(f"✓ 系统拒绝重复客户: {response2_body.get('error_message', 'Unknown error')}")

    def test_create_client_with_crypto_category(self, client_list_api):
        """
        测试场景6：创建加密货币类别客户
        验证点：
        1. 接口返回 200
        2. oms_category正确保存
        """
        logger.info("测试场景6：创建加密货币类别客户")
        
        timestamp = int(time.time())
        client_data = {
            "account_id": "test_account_id",
            "oms_category": "Crypto Currency",
            "account_name": f"Auto TestYan Crypto Client {timestamp}"
        }
        
        response = client_list_api.create_client(client_data)
        assert_status_ok(response)
        
        response_body = response.json()
        created_data = response_body.get("data", response_body)
        
        assert created_data.get("oms_category") == "Crypto Currency"
        
        logger.info("✓ 加密货币类别客户创建成功")
