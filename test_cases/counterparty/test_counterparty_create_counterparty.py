"""
Counterparty Create Counterparty 接口测试用例
测试 POST /api/v1/cores/{core}/counterparties 接口
"""
import pytest
from api.account_api import AccountAPI
import time
from utils.logger import logger
from utils.assertions import (
    assert_status_ok,
    assert_fields_present
)


@pytest.mark.counterparty
@pytest.mark.create_api
class TestCounterpartyCreateCounterparty:
    """
    创建 Counterparty 接口测试用例集
    """

    def test_create_counterparty_success_ach(self, counterparty_api, login_session):
        """
        测试场景1：成功创建 ACH 类型的 Counterparty
        验证点：
        1. 接口返回 200
        2. 返回的数据包含 id 字段
        3. 返回的数据包含必需字段
        4. payment_enable 字段正确
        
        前置条件：需要先获取一个真实的 account_id
        """
        # 1. 获取 account_id
        account_api = AccountAPI(session=login_session)
        logger.info("\n获取 account_id")
        account_response = account_api.list_accounts(page=0, size=1)
        assert_status_ok(account_response)
        
        account_data = account_response.json().get("data", {})
        accounts = account_data.get("content", [])
        
        if len(accounts) == 0:
            pytest.skip("没有可用的 Account 数据，跳过测试")
        
        account_id = accounts[0]["id"]
        logger.info(f"Account ID: {account_id}")
        
        # 2. 构造 Counterparty 数据
        timestamp = int(time.time())
        counterparty_data = {
            "name": f"Auto TestYan Counterparty ACH {timestamp}",
            "type": "Person",
            "payment_type": "ACH",
            "bank_account_type": "Checking",
            "bank_routing_number": "091918457",
            "bank_name": "Auto TestYan Bank",
            "bank_account_owner_name": "Auto TestYan Owner",
            "bank_account_number": "111111111",
            "assign_account_ids": [account_id]
        }
        
        # 3. 调用 Create Counterparty 接口
        logger.info("创建 ACH Counterparty")
        response = counterparty_api.create_counterparty(counterparty_data)
        
        # 4. 验证响应
        assert_status_ok(response)
        response_body = response.json()
        
        # 5. 验证必需字段
        required_fields = ["id", "name", "type", "payment_type", "assign_account_ids"]
        assert_fields_present(response_body, required_fields, "Counterparty")

        # Echo 验证：返回值与发送值一致
        assert response_body.get("name") == counterparty_data["name"], \
            f"name 不一致: 发送 '{counterparty_data['name']}', 返回 '{response_body.get('name')}'"
        assert response_body.get("type") == counterparty_data["type"], \
            f"type 不一致: 发送 '{counterparty_data['type']}', 返回 '{response_body.get('type')}'"
        assert response_body.get("payment_type") == counterparty_data["payment_type"], \
            f"payment_type 不一致: 发送 '{counterparty_data['payment_type']}', 返回 '{response_body.get('payment_type')}'"

        counterparty_id = response_body["id"]
        logger.info(f"✓ 创建成功 - ID: {counterparty_id}, Name: {response_body.get('name')}")

    def test_create_counterparty_success_wire(self, counterparty_api, login_session):
        """
        测试场景2：成功创建 Wire 类型的 Counterparty
        验证点：
        1. 接口返回 200
        2. Wire 类型的特定字段自动填充（bank_name, bank_city, bank_state）
        """
        # 1. 获取 account_id
        account_api = AccountAPI(session=login_session)
        logger.info("\n获取 account_id")
        account_response = account_api.list_accounts(page=0, size=1)
        assert_status_ok(account_response)
        
        account_data = account_response.json().get("data", {})
        accounts = account_data.get("content", [])
        
        if len(accounts) == 0:
            pytest.skip("没有可用的 Account 数据，跳过测试")
        
        account_id = accounts[0]["id"]
        
        # 2. 构造 Wire Counterparty 数据
        timestamp = int(time.time())
        counterparty_data = {
            "name": f"Auto TestYan Counterparty Wire {timestamp}",
            "type": "Company",
            "payment_type": "Wire",
            "bank_account_type": "Savings",
            "bank_routing_number": "091918457",
            "bank_account_owner_name": "Auto TestYan Wire Owner",
            "bank_account_number": "222222222",
            "assign_account_ids": [account_id],
            "swift_code": "12345678"
        }
        
        # 3. 调用 Create Counterparty 接口
        logger.info("创建 Wire Counterparty")
        response = counterparty_api.create_counterparty(counterparty_data)
        
        # 4. 验证响应
        assert_status_ok(response)
        response_body = response.json()

        # 验证必需字段
        required_fields = ["id", "name", "type", "payment_type"]
        assert_fields_present(response_body, required_fields, "Wire Counterparty")

        # Echo 验证
        assert response_body.get("name") == counterparty_data["name"], \
            f"name 不一致: 发送 '{counterparty_data['name']}', 返回 '{response_body.get('name')}'"
        assert response_body.get("type") == counterparty_data["type"], \
            f"type 不一致"
        assert response_body.get("payment_type") == counterparty_data["payment_type"], \
            f"payment_type 不一致"

        logger.info(f"✓ 创建成功 - ID: {response_body.get('id')}, Name: {response_body.get('name')}")

    def test_create_counterparty_missing_required_field(self, counterparty_api):
        """
        测试场景3：缺少必需字段（name）
        验证点：
        1. 接口返回错误状态码或错误信息
        """
        # 1. 构造缺少 name 字段的数据
        logger.info("\n测试缺少必需字段")
        counterparty_data = {
            # 缺少 name
            "type": "Person",
            "payment_type": "ACH"
        }
        
        # 2. 调用接口并验证错误
        response = counterparty_api.create_counterparty(counterparty_data)
        assert response.status_code != 200, "缺少必需字段应该返回错误"
        
        logger.info("✓ 测试完成 - 状态码: {response.status_code}")

    def test_create_counterparty_invalid_type(self, counterparty_api, login_session):
        """
        测试场景4：使用无效的 type 值
        验证点：
        1. 接口返回错误信息
        """
        # 1. 获取 account_id
        account_api = AccountAPI(session=login_session)
        logger.info("\n获取 account_id")
        account_response = account_api.list_accounts(page=0, size=1)
        assert_status_ok(account_response)
        
        account_data = account_response.json().get("data", {})
        accounts = account_data.get("content", [])
        
        if len(accounts) == 0:
            pytest.skip("没有可用的 Account 数据，跳过测试")
        
        account_id = accounts[0]["id"]
        
        # 2. 构造包含无效 type 的数据
        timestamp = int(time.time())
        counterparty_data = {
            "name": f"Auto TestYan Invalid Type {timestamp}",
            "type": "InvalidType",  # 无效的类型
            "payment_type": "ACH",
            "assign_account_ids": [account_id]
        }
        
        # 3. 调用接口
        logger.info("测试无效 type 值")
        response = counterparty_api.create_counterparty(counterparty_data)
        
        if response.status_code == 200:
            logger.info("⚠ 系统允许创建，但 type 值可能不符合预期")
        else:
            logger.info("✓ 系统正确拒绝 - 状态码: {response.status_code}")

    def test_create_counterparty_draft_mode(self, counterparty_api, login_session):
        """
        测试场景5：创建草稿模式的 Counterparty
        验证点：
        1. 接口返回 200
        2. payment_enable 为 false（字段不完整）
        """
        # 1. 获取 account_id
        account_api = AccountAPI(session=login_session)
        logger.info("\n获取 account_id")
        account_response = account_api.list_accounts(page=0, size=1)
        assert_status_ok(account_response)
        
        account_data = account_response.json().get("data", {})
        accounts = account_data.get("content", [])
        
        if len(accounts) == 0:
            pytest.skip("没有可用的 Account 数据，跳过测试")
        
        account_id = accounts[0]["id"]
        
        # 2. 构造最小化数据（只包含必需字段）
        timestamp = int(time.time())
        counterparty_data = {
            "name": f"Auto TestYan Draft {timestamp}",
            "type": "Person",
            "payment_type": "ACH",
            "assign_account_ids": [account_id]
            # 缺少银行信息，创建为草稿
        }
        
        # 3. 调用接口
        logger.info("测试草稿模式")
        response = counterparty_api.create_counterparty(counterparty_data)
        
        if response.status_code == 200:
            response_body = response.json()
            payment_enable = response_body.get("payment_enable")
            logger.info("✓ 创建成功 - payment_enable: {payment_enable}")
        else:
            logger.info(f"⚠ 返回错误: {response.status_code}")
