"""
账户更新接口测试用例
测试 PUT /api/v1/cores/{core}/accounts/{account_id} 接口
"""
import pytest
from api.account_api import AccountAPI


@pytest.mark.update_api
class TestAccountUpdate:
    """
    账户更新接口测试用例集
    """

    def test_update_account_mailing_address_success(self, login_session):
        """
        测试场景1：成功更新账户邮寄地址
        验证点：
        1. 先从列表接口获取有效 account_id
        2. 构造更新数据（修改 mailing_city）
        3. 调用 Update 接口
        4. 验证状态码 200
        5. 验证返回体中 mailing_city 等于修改后的值
        6. 再次调用 Detail 接口确认数据落库
        """
        # 1. 初始化 API 对象
        account_api = AccountAPI(session=login_session)
        
        # 2. 获取一个有效的账户 ID
        print("\n[Step] 获取账户列表，提取账户 ID")
        list_response = account_api.list_accounts(size=1)
        assert list_response.status_code == 200, f"列表接口返回状态码错误: {list_response.status_code}"
        
        parsed_list = account_api.parse_list_response(list_response)
        assert not parsed_list.get("error"), f"列表响应解析失败: {parsed_list.get('message')}"
        
        accounts = parsed_list["content"]
        if len(accounts) == 0:
            pytest.skip("没有可用的账户数据，跳过更新测试")
        
        account_id = accounts[0]["id"]
        original_city = accounts[0].get("mailing_city", "")
        print(f"  账户 ID: {account_id}, 原始城市: {original_city}")
        
        # 3. 构造更新数据
        new_city = "New York"
        new_state = "NY"
        update_data = {
            "mailing_city": new_city,
            "mailing_state": new_state,
            "mailing_street": "123 Test Street",
            "mailing_postalcode": "10001",
            "mailing_country": "US"
        }
        
        # 4. 调用 Update 接口
        print(f"[Step] 调用 Update 接口，将 mailing_city 更新为 '{new_city}'")
        update_response = account_api.update_account(account_id, update_data)
        
        # 5. 验证状态码
        print("[Step] 验证 HTTP 状态码为 200")
        assert update_response.status_code == 200, \
            f"Update 接口返回状态码错误: {update_response.status_code}, 响应: {update_response.text}"
        
        # 6. 验证返回体中的数据
        print("[Step] 验证返回体中 mailing_city 已更新")
        try:
            updated_account = update_response.json()
            # 兼容不同的响应结构
            if "data" in updated_account:
                updated_account = updated_account["data"]
            
            assert updated_account.get("mailing_city") == new_city, \
                f"返回体中的 mailing_city 不正确: 期望 '{new_city}'，实际 '{updated_account.get('mailing_city')}'"
            assert updated_account.get("mailing_state") == new_state, \
                f"返回体中的 mailing_state 不正确: 期望 '{new_state}'，实际 '{updated_account.get('mailing_state')}'"
            
            print(f"✓ 更新成功，mailing_city: {updated_account.get('mailing_city')}, mailing_state: {updated_account.get('mailing_state')}")
        except Exception as e:
            pytest.fail(f"解析更新响应失败: {e}")
        
        # 7. 再次调用 Detail 接口确认数据落库
        print("[Step] 调用 Detail 接口确认数据已落库")
        detail_response = account_api.get_account_detail(account_id)
        assert detail_response.status_code == 200, f"Detail 接口返回状态码错误: {detail_response.status_code}"
        
        parsed_detail = account_api.parse_detail_response(detail_response)
        assert not parsed_detail.get("error"), f"Detail 响应解析失败: {parsed_detail.get('message')}"
        
        account_detail = parsed_detail["data"]
        assert account_detail.get("mailing_city") == new_city, \
            f"Detail 接口中的 mailing_city 不正确: 期望 '{new_city}'，实际 '{account_detail.get('mailing_city')}'"
        
        print(f"✓ 数据已落库确认，Detail 接口返回的 mailing_city: {account_detail.get('mailing_city')}")

    def test_update_account_register_address(self, login_session):
        """
        测试场景2：更新账户注册地址
        验证点：
        1. 更新 register_street, register_city 等字段
        2. 验证更新成功
        """
        # 1. 初始化 API 对象
        account_api = AccountAPI(session=login_session)
        
        # 2. 获取账户 ID
        print("\n[Step] 获取账户 ID")
        list_response = account_api.list_accounts(size=1)
        parsed_list = account_api.parse_list_response(list_response)
        
        if len(parsed_list["content"]) == 0:
            pytest.skip("没有可用的账户数据")
        
        account_id = parsed_list["content"][0]["id"]
        
        # 3. 构造注册地址更新数据
        update_data = {
            "register_street": "456 Register Avenue",
            "register_city": "Los Angeles",
            "register_state": "CA",
            "register_postalcode": "90001",
            "register_country": "US"
        }
        
        # 4. 调用 Update 接口
        print(f"[Step] 更新注册地址")
        update_response = account_api.update_account(account_id, update_data)
        
        # 5. 验证
        print("[Step] 验证更新成功")
        assert update_response.status_code == 200, \
            f"Update 接口返回状态码错误: {update_response.status_code}"
        
        updated_account = update_response.json()
        if "data" in updated_account:
            updated_account = updated_account["data"]
        
        assert updated_account.get("register_city") == "Los Angeles", \
            f"register_city 更新失败"
        
        print(f"✓ 注册地址更新成功: {updated_account.get('register_city')}, {updated_account.get('register_state')}")

    def test_update_account_partial_fields(self, login_session):
        """
        测试场景3：部分字段更新
        验证点：
        1. 只更新部分字段（如只更新 mailing_city）
        2. 验证其他字段不受影响
        """
        # 1. 初始化 API 对象
        account_api = AccountAPI(session=login_session)
        
        # 2. 获取账户详情（记录原始数据）
        print("\n[Step] 获取账户详情，记录原始数据")
        list_response = account_api.list_accounts(size=1)
        parsed_list = account_api.parse_list_response(list_response)
        
        if len(parsed_list["content"]) == 0:
            pytest.skip("没有可用的账户数据")
        
        account_id = parsed_list["content"][0]["id"]
        
        # 获取详情
        detail_response = account_api.get_account_detail(account_id)
        parsed_detail = account_api.parse_detail_response(detail_response)
        original_account = parsed_detail["data"]
        
        original_state = original_account.get("mailing_state")
        original_street = original_account.get("mailing_street")
        
        print(f"  原始 mailing_state: {original_state}")
        print(f"  原始 mailing_street: {original_street}")
        
        # 3. 只更新 mailing_city
        update_data = {
            "mailing_city": "Chicago"
        }
        
        print("[Step] 只更新 mailing_city 字段")
        update_response = account_api.update_account(account_id, update_data)
        
        # 4. 验证
        print("[Step] 验证更新成功且其他字段不受影响")
        assert update_response.status_code == 200, \
            f"Update 接口返回状态码错误: {update_response.status_code}"
        
        updated_account = update_response.json()
        if "data" in updated_account:
            updated_account = updated_account["data"]
        
        # 验证 mailing_city 已更新
        assert updated_account.get("mailing_city") == "Chicago", \
            f"mailing_city 更新失败"
        
        # 验证其他字段不变（如果原始值不为空）
        if original_state:
            assert updated_account.get("mailing_state") == original_state, \
                f"mailing_state 不应该改变"
        
        print(f"✓ 部分字段更新成功，mailing_city: {updated_account.get('mailing_city')}")

    def test_update_account_invalid_id(self, login_session):
        """
        测试场景4：使用无效的 account_id 更新
        验证点（基于真实业务行为）：
        1. 服务器出于安全考虑（防遍历），返回 200 OK
        2. 响应体包含特定的错误码：code=506, error_message="visibility permission deny"
        """
        # 1. 初始化 API 对象
        account_api = AccountAPI(session=login_session)
        
        # 2. 使用无效的 account_id
        invalid_id = "INVALID_ACCOUNT_ID_999999"
        update_data = {
            "mailing_city": "Test City"
        }
        
        print(f"\n[Step] 使用无效的账户 ID: {invalid_id}")
        update_response = account_api.update_account(invalid_id, update_data)
        
        # 3. 验证返回 200 状态码（服务器防遍历设计）
        print("[Step] 验证返回 200 状态码")
        assert update_response.status_code == 200, \
            f"服务器应该返回 200，但实际返回了 {update_response.status_code}"
        
        # 4. 验证响应体包含错误信息
        print("[Step] 验证响应体包含错误码")
        response_body = update_response.json()
        
        # 验证响应结构完全匹配
        expected_response = {
            "code": 506,
            "error_message": "visibility permission deny",
            "data": None
        }
        
        assert response_body == expected_response, \
            f"响应体不匹配\n期望: {expected_response}\n实际: {response_body}"
        
        print(f"✓ 使用无效 ID 正确返回错误信息: code=506, error_message='visibility permission deny'")
