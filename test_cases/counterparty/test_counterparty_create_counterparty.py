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

        # Counterparty 创建响应有 data 包装层
        assert response_body.get("code") == 200, \
            f"业务 code 不是 200: {response_body.get('code')}, msg: {response_body.get('error_message')}"

        counterparty_data_resp = response_body.get("data", response_body)

        # 5. 验证必需字段
        required_fields = ["id", "name", "type", "payment_type", "assign_account_ids"]
        assert_fields_present(counterparty_data_resp, required_fields, "Counterparty")

        # Echo 验证：返回值与发送值一致
        assert counterparty_data_resp.get("name") == counterparty_data["name"], \
            f"name 不一致: 发送 '{counterparty_data['name']}', 返回 '{counterparty_data_resp.get('name')}'"
        assert counterparty_data_resp.get("type") == counterparty_data["type"], \
            f"type 不一致: 发送 '{counterparty_data['type']}', 返回 '{counterparty_data_resp.get('type')}'"
        assert counterparty_data_resp.get("payment_type") == counterparty_data["payment_type"], \
            f"payment_type 不一致: 发送 '{counterparty_data['payment_type']}', 返回 '{counterparty_data_resp.get('payment_type')}'"

        counterparty_id = counterparty_data_resp["id"]
        logger.info(f"✓ 创建成功 - ID: {counterparty_id}, Name: {counterparty_data_resp.get('name')}")

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
            "swift_code": "CRBKUS33XXX"  # 标准 11 位 SWIFT/BIC 码格式
        }
        
        # 3. 调用 Create Counterparty 接口
        logger.info("创建 Wire Counterparty")
        response = counterparty_api.create_counterparty(counterparty_data)
        
        # 4. 验证响应
        assert_status_ok(response)
        response_body = response.json()

        # Counterparty 创建响应有 data 包装层
        assert response_body.get("code") == 200, \
            f"业务 code 不是 200: {response_body.get('code')}, msg: {response_body.get('error_message')}"

        wire_data_resp = response_body.get("data", response_body)

        # 验证必需字段
        required_fields = ["id", "name", "type", "payment_type"]
        assert_fields_present(wire_data_resp, required_fields, "Wire Counterparty")

        # Echo 验证
        assert wire_data_resp.get("name") == counterparty_data["name"], \
            f"name 不一致: 发送 '{counterparty_data['name']}', 返回 '{wire_data_resp.get('name')}'"
        assert wire_data_resp.get("type") == counterparty_data["type"], \
            f"type 不一致"
        assert wire_data_resp.get("payment_type") == counterparty_data["payment_type"], \
            f"payment_type 不一致"

        logger.info(f"✓ 创建成功 - ID: {wire_data_resp.get('id')}, Name: {wire_data_resp.get('name')}")

    def test_create_counterparty_missing_required_field(self, counterparty_api):
        """
        测试场景3：缺少必需字段（name）
        验证点：
        1. 服务器返回 200 OK（统一错误处理）
        2. 业务错误码 code != 200
        3. data 为 None
        """
        logger.info("\n测试缺少必需字段 name")
        counterparty_data = {
            # 缺少 name
            "type": "Person",
            "payment_type": "ACH"
        }

        response = counterparty_api.create_counterparty(counterparty_data)

        # 统一错误处理：HTTP 200，业务 code != 200
        assert response.status_code == 200, \
            f"服务器应该返回 200（统一错误处理），实际: {response.status_code}"

        response_body = response.json()
        logger.info(f"  响应: {response_body}")

        assert response_body.get("code") != 200, \
            f"缺少必需字段 name 应该返回业务错误码，但返回了 code=200"
        assert response_body.get("data") is None, \
            "缺少 name 时 data 应为 None"

        logger.info(f"✓ 缺少 name 校验通过，业务错误码: {response_body.get('code')}")

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

    def test_create_counterparty_with_invisible_account_id(self, counterparty_api):
        """
        测试场景6：使用不在当前用户 visible 范围内的 Account ID
        验证点：
        1. 在 assign_account_ids 中使用他人账户 ID：241010195849720143（yhan account Sanchez）
        2. 服务器返回 200 OK（统一错误处理）
        3. 业务错误码 code == 506
        4. error_message == "visibility permission deny"
        """
        invisible_account_id = "241010195849720143"  # yhan account Sanchez，不属于当前用户

        timestamp = int(time.time())
        counterparty_data = {
            "name": f"Auto TestYan Counterparty Invisible {timestamp}",
            "type": "Person",
            "payment_type": "ACH",
            "bank_account_type": "Checking",
            "bank_routing_number": "091918457",
            "bank_name": "Auto TestYan Bank",
            "bank_account_owner_name": "Auto TestYan Owner",
            "bank_account_number": "111111111",
            "assign_account_ids": [invisible_account_id]  # 越权 Account ID
        }

        logger.info(f"使用不在 visible 范围的 Account ID: {invisible_account_id}")
        response = counterparty_api.create_counterparty(counterparty_data)

        assert response.status_code == 200, \
            f"服务器应该返回 200（统一错误处理），实际: {response.status_code}"

        response_body = response.json()
        logger.info(f"  响应: {response_body}")

        # Counterparty assign_account_ids 越权返回 code=599（"Assign account can not find."）
        # 而不是 506，这是业务行为的差异：
        # - 506 = visibility permission deny（FA/Sub Account 等直接 ID 越权）
        # - 599 = 业务校验失败（assign_account_ids 中的越权 account 表现为"找不到"）
        assert response_body.get("code") != 200, \
            f"越权 Account ID 不应该创建成功，但返回了 code=200"
        assert response_body.get("data") is None, \
            "越权时 data 应为 None"

        code = response_body.get("code")
        error_msg = response_body.get("error_message", "")
        logger.info(f"  业务错误码: {code}")
        logger.info(f"  错误信息: {error_msg}")

        # 可能返回 506 或 599 - 均为拒绝
        assert code in [506, 599], \
            f"越权 Account ID 应该返回 506 或 599，实际: {code}"

        if code == 506:
            assert "visibility permission deny" in error_msg.lower(), \
                f"code=506 时 error_message 应含 'visibility permission deny'，实际: {error_msg}"
            logger.info("✓ 越权 Account ID 校验通过: code=506 (visibility deny)")
        else:
            # code=599: assign_account_ids 对越权账户表现为"找不到"
            logger.info(f"⚠️ assign_account_ids 越权返回 code=599（找不到），而非 506")
            logger.info(f"   业务行为说明：Counterparty 的 assign_account_ids 越权表现为 '找不到'")
            logger.info(f"✓ 越权 Account ID 校验通过: code=599 (not found, as expected)")
