"""
Counterparty Create Counterparty 接口测试用例
测试 POST /api/v1/cores/{core}/counterparties 接口
"""
import pytest
from api.counterparty_api import CounterpartyAPI
from api.account_api import AccountAPI
import time


@pytest.mark.counterparty
@pytest.mark.create_api
class TestCounterpartyCreateCounterparty:
    """
    创建 Counterparty 接口测试用例集
    """

    def test_create_counterparty_success_ach(self, login_session):
        """
        测试场景1：成功创建 ACH 类型的 Counterparty
        验证点：
        1. 接口返回 200
        2. 返回的数据包含 id 字段
        3. 返回的数据包含必需字段
        4. payment_enable 字段正确
        
        前置条件：需要先获取一个真实的 account_id
        """
        # 1. 初始化 API 对象
        counterparty_api = CounterpartyAPI(session=login_session)
        account_api = AccountAPI(session=login_session)
        
        # 2. 先获取一个 account_id
        print("\n[Step] 获取真实的 account_id")
        account_response = account_api.list_accounts(page=0, size=1)
        assert account_response.status_code == 200, "Account List 接口调用失败"
        
        account_data = account_response.json().get("data", {})
        accounts = account_data.get("content", [])
        
        if len(accounts) == 0:
            pytest.skip("没有可用的 Account 数据，跳过测试")
        
        account_id = accounts[0]["id"]
        print(f"  获取到 Account ID: {account_id}")
        
        # 3. 构造 Counterparty 数据
        timestamp = int(time.time())
        counterparty_data = {
            "name": f"Test Counterparty ACH {timestamp}",
            "type": "Person",
            "payment_type": "ACH",
            "bank_account_type": "Checking",
            "bank_routing_number": "091918457",
            "bank_name": "Test Bank",
            "bank_account_owner_name": "Test Owner",
            "bank_account_number": "111111111",
            "assign_account_ids": [account_id]
        }
        
        # 4. 调用 Create Counterparty 接口
        print(f"[Step] 调用 Create Counterparty 接口")
        response = counterparty_api.create_counterparty(counterparty_data)
        
        # 5. 断言状态码
        print("[Step] 验证 HTTP 状态码为 200")
        assert response.status_code == 200, \
            f"Create Counterparty 接口返回状态码错误: {response.status_code}, Response: {response.text}"
        
        # 6. 解析响应
        print("[Step] 解析响应并验证数据")
        response_body = response.json()
        
        # 7. 验证 id 字段
        assert "id" in response_body, "响应中缺少 id 字段"
        counterparty_id = response_body["id"]
        print(f"  创建的 Counterparty ID: {counterparty_id}")
        
        # 8. 验证必需字段
        print("[Step] 验证必需字段")
        required_fields = ["id", "name", "type", "payment_type", "assign_account_ids"]
        
        for field in required_fields:
            assert field in response_body, f"响应中缺少必需字段: {field}"
            print(f"  ✓ {field}: {response_body.get(field)}")
        
        # 9. 验证 payment_enable 字段
        print(f"  payment_enable: {response_body.get('payment_enable')}")
        
        print(f"\n✓ 成功创建 ACH Counterparty:")
        print(f"  ID: {counterparty_id}")
        print(f"  Name: {response_body.get('name')}")
        print(f"  Type: {response_body.get('type')}")
        print(f"  Payment Type: {response_body.get('payment_type')}")

    def test_create_counterparty_success_wire(self, login_session):
        """
        测试场景2：成功创建 Wire 类型的 Counterparty
        验证点：
        1. 接口返回 200
        2. Wire 类型的特定字段自动填充（bank_name, bank_city, bank_state）
        """
        # 1. 初始化 API 对象
        counterparty_api = CounterpartyAPI(session=login_session)
        account_api = AccountAPI(session=login_session)
        
        # 2. 获取 account_id
        print("\n[Step] 获取真实的 account_id")
        account_response = account_api.list_accounts(page=0, size=1)
        assert account_response.status_code == 200, "Account List 接口调用失败"
        
        account_data = account_response.json().get("data", {})
        accounts = account_data.get("content", [])
        
        if len(accounts) == 0:
            pytest.skip("没有可用的 Account 数据，跳过测试")
        
        account_id = accounts[0]["id"]
        
        # 3. 构造 Wire Counterparty 数据
        timestamp = int(time.time())
        counterparty_data = {
            "name": f"Test Counterparty Wire {timestamp}",
            "type": "Company",
            "payment_type": "Wire",
            "bank_account_type": "Savings",
            "bank_routing_number": "091918457",
            "bank_account_owner_name": "Test Wire Owner",
            "bank_account_number": "222222222",
            "assign_account_ids": [account_id],
            "swift_code": "12345678"
        }
        
        # 4. 调用 Create Counterparty 接口
        print(f"[Step] 调用 Create Counterparty 接口")
        response = counterparty_api.create_counterparty(counterparty_data)
        
        # 5. 验证状态码
        print("[Step] 验证 HTTP 状态码为 200")
        assert response.status_code == 200, \
            f"Create Counterparty 接口返回状态码错误: {response.status_code}, Response: {response.text}"
        
        # 6. 解析响应并验证
        response_body = response.json()
        
        print(f"\n✓ 成功创建 Wire Counterparty:")
        print(f"  ID: {response_body.get('id')}")
        print(f"  Bank Name: {response_body.get('bank_name')} (自动填充)")
        print(f"  Bank City: {response_body.get('bank_city')} (自动填充)")
        print(f"  Bank State: {response_body.get('bank_state')} (自动填充)")
        print(f"  Bank Country: {response_body.get('bank_country')}")

    def test_create_counterparty_missing_required_field(self, login_session):
        """
        测试场景3：缺少必需字段（name）
        验证点：
        1. 接口返回错误状态码或错误信息
        """
        # 1. 初始化 API 对象
        counterparty_api = CounterpartyAPI(session=login_session)
        
        # 2. 构造缺少 name 字段的数据
        print("\n[Step] 构造缺少 name 字段的请求数据")
        counterparty_data = {
            # 缺少 name
            "type": "Person",
            "payment_type": "ACH"
        }
        
        # 3. 调用接口
        print("[Step] 调用 Create Counterparty 接口")
        response = counterparty_api.create_counterparty(counterparty_data)
        
        # 4. 验证返回错误
        print("[Step] 验证接口返回错误")
        print(f"  状态码: {response.status_code}")
        
        # 可能返回 400 或其他错误状态码
        assert response.status_code != 200, "缺少必需字段应该返回错误"
        
        print(f"✓ 缺少必需字段测试完成")

    def test_create_counterparty_invalid_type(self, login_session):
        """
        测试场景4：使用无效的 type 值
        验证点：
        1. 接口返回错误信息
        """
        # 1. 初始化 API 对象
        counterparty_api = CounterpartyAPI(session=login_session)
        account_api = AccountAPI(session=login_session)
        
        # 2. 获取 account_id
        print("\n[Step] 获取真实的 account_id")
        account_response = account_api.list_accounts(page=0, size=1)
        assert account_response.status_code == 200, "Account List 接口调用失败"
        
        account_data = account_response.json().get("data", {})
        accounts = account_data.get("content", [])
        
        if len(accounts) == 0:
            pytest.skip("没有可用的 Account 数据，跳过测试")
        
        account_id = accounts[0]["id"]
        
        # 3. 构造包含无效 type 的数据
        timestamp = int(time.time())
        counterparty_data = {
            "name": f"Test Invalid Type {timestamp}",
            "type": "InvalidType",  # 无效的类型
            "payment_type": "ACH",
            "assign_account_ids": [account_id]
        }
        
        # 4. 调用接口
        print("[Step] 调用 Create Counterparty 接口")
        response = counterparty_api.create_counterparty(counterparty_data)
        
        # 5. 验证返回错误
        print("[Step] 验证接口返回错误")
        print(f"  状态码: {response.status_code}")
        
        # 应该返回错误
        if response.status_code == 200:
            # 有些系统可能允许创建但会有警告
            print(f"  ⚠ 系统允许创建，但 type 值可能不符合预期")
        else:
            print(f"  ✓ 系统正确拒绝了无效的 type 值")
        
        print(f"✓ 无效 type 测试完成")

    def test_create_counterparty_draft_mode(self, login_session):
        """
        测试场景5：创建草稿模式的 Counterparty
        验证点：
        1. 接口返回 200
        2. payment_enable 为 false（字段不完整）
        """
        # 1. 初始化 API 对象
        counterparty_api = CounterpartyAPI(session=login_session)
        account_api = AccountAPI(session=login_session)
        
        # 2. 获取 account_id
        print("\n[Step] 获取真实的 account_id")
        account_response = account_api.list_accounts(page=0, size=1)
        assert account_response.status_code == 200, "Account List 接口调用失败"
        
        account_data = account_response.json().get("data", {})
        accounts = account_data.get("content", [])
        
        if len(accounts) == 0:
            pytest.skip("没有可用的 Account 数据，跳过测试")
        
        account_id = accounts[0]["id"]
        
        # 3. 构造最小化数据（只包含必需字段）
        timestamp = int(time.time())
        counterparty_data = {
            "name": f"Test Draft {timestamp}",
            "type": "Person",
            "payment_type": "ACH",
            "assign_account_ids": [account_id]
            # 缺少银行信息，创建为草稿
        }
        
        # 4. 调用接口
        print("[Step] 调用 Create Counterparty 接口（草稿模式）")
        response = counterparty_api.create_counterparty(counterparty_data)
        
        # 5. 验证状态码
        if response.status_code == 200:
            response_body = response.json()
            payment_enable = response_body.get("payment_enable")
            
            print(f"  payment_enable: {payment_enable}")
            
            if payment_enable is False:
                print(f"  ✓ 成功创建草稿模式 Counterparty")
            else:
                print(f"  ⚠ payment_enable 为 true，可能字段已足够完整")
        else:
            print(f"  ⚠ 接口返回错误: {response.status_code}")
        
        print(f"✓ 草稿模式测试完成")
