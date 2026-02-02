"""
账户详情接口测试用例
测试 GET /api/v1/cores/{core}/accounts/{account_id} 接口
"""
import pytest
from api.account_api import AccountAPI


class TestAccountDetail:
    """
    账户详情接口测试用例集
    """

    def test_get_account_detail_success(self, login_session):
        """
        测试场景1：成功获取账户详情
        依赖逻辑：先从列表接口获取一个有效的 account_id，然后获取详情
        验证点：
        1. 列表接口返回成功
        2. 详情接口返回 200
        3. 返回的 id 与请求的 id 一致
        4. 关键字段不为空（account_number, account_name 等）
        """
        # 1. 初始化 API 对象
        account_api = AccountAPI(session=login_session)
        
        # 2. 先调用列表接口获取一个账户 ID
        print("\n[Step] 调用列表接口获取账户 ID")
        list_response = account_api.list_accounts(size=1)
        assert list_response.status_code == 200, f"列表接口返回状态码错误: {list_response.status_code}"
        
        # 3. 解析列表响应
        print("[Step] 解析列表响应，提取账户 ID")
        parsed_list = account_api.parse_list_response(list_response)
        assert not parsed_list.get("error"), f"列表响应解析失败: {parsed_list.get('message')}"
        
        accounts = parsed_list["content"]
        if len(accounts) == 0:
            pytest.skip("没有可用的账户数据，跳过详情测试")
        
        # 提取第一个账户的 ID
        account_id = accounts[0]["id"]
        expected_account_number = accounts[0].get("account_number")
        print(f"  提取到账户 ID: {account_id}, 账户编号: {expected_account_number}")
        
        # 4. 调用详情接口
        print(f"[Step] 调用详情接口获取账户 {account_id} 的详情")
        detail_response = account_api.get_account_detail(account_id)
        
        # 5. 断言状态码
        print("[Step] 验证 HTTP 状态码为 200")
        assert detail_response.status_code == 200, f"详情接口返回状态码错误: {detail_response.status_code}"
        
        # 6. 解析详情响应
        print("[Step] 解析详情响应并验证数据")
        parsed_detail = account_api.parse_detail_response(detail_response)
        assert not parsed_detail.get("error"), f"详情响应解析失败: {parsed_detail.get('message')}"
        
        account_detail = parsed_detail["data"]
        
        # 7. 验证返回的 ID 一致
        print("[Step] 验证返回的 ID 与请求的 ID 一致")
        assert account_detail.get("id") == account_id, \
            f"返回的 ID {account_detail.get('id')} 与请求的 ID {account_id} 不一致"
        
        # 8. 验证关键字段不为空
        print("[Step] 验证关键字段不为空")
        assert account_detail.get("account_number") is not None, "account_number 字段为空"
        assert account_detail.get("account_name") is not None, "account_name 字段为空"
        assert account_detail.get("account_status") is not None, "account_status 字段为空"
        
        # 9. 验证账户编号一致
        assert account_detail.get("account_number") == expected_account_number, \
            f"详情中的账户编号 {account_detail.get('account_number')} 与列表中的不一致"
        
        print(f"✓ 成功获取账户详情:")
        print(f"  ID: {account_detail.get('id')}")
        print(f"  账户编号: {account_detail.get('account_number')}")
        print(f"  账户名称: {account_detail.get('account_name')}")
        print(f"  账户状态: {account_detail.get('account_status')}")

    def test_get_account_detail_fields_completeness(self, login_session):
        """
        测试场景2：验证详情响应字段完整性
        验证点：
        1. 返回的账户详情包含所有必需字段
        2. 字段类型正确
        """
        # 1. 初始化 API 对象
        account_api = AccountAPI(session=login_session)
        
        # 2. 先获取一个账户 ID
        print("\n[Step] 获取账户 ID")
        list_response = account_api.list_accounts(size=1)
        parsed_list = account_api.parse_list_response(list_response)
        
        if len(parsed_list["content"]) == 0:
            pytest.skip("没有可用的账户数据")
        
        account_id = parsed_list["content"][0]["id"]
        
        # 3. 获取详情
        print(f"[Step] 获取账户 {account_id} 的详情")
        detail_response = account_api.get_account_detail(account_id)
        assert detail_response.status_code == 200, f"详情接口返回状态码错误: {detail_response.status_code}"
        
        # 4. 解析响应
        print("[Step] 解析响应并验证字段完整性")
        parsed_detail = account_api.parse_detail_response(detail_response)
        assert not parsed_detail.get("error"), f"详情响应解析失败: {parsed_detail.get('message')}"
        
        account_detail = parsed_detail["data"]
        
        # 5. 验证必需字段
        required_fields = [
            "id",
            "account_name",
            "account_number",
            "account_status",
            "record_type",
            "create_time",
            "risk_level"
        ]
        
        print("[Step] 验证必需字段存在")
        for field in required_fields:
            assert field in account_detail, f"账户详情缺少必需字段: {field}"
        
        # 6. 验证可选字段（可能为 null）
        optional_fields = [
            "business_entity_type",
            "account_email",
            "tax_id",
            "mailing_street",
            "mailing_city",
            "mailing_state",
            "mailing_postalcode",
            "mailing_country",
            "register_street",
            "register_city",
            "register_state",
            "register_postalcode",
            "register_country",
            "authorized_agent",
            "external_id"
        ]
        
        print("[Step] 验证可选字段存在（可能为 null）")
        for field in optional_fields:
            assert field in account_detail, f"账户详情缺少字段: {field}"
        
        print(f"✓ 字段完整性验证通过，账户详情包含所有必需字段和可选字段")

    def test_get_account_detail_invalid_id(self, login_session):
        """
        测试场景3：使用无效的 account_id 获取详情
        验证点（基于真实业务行为）：
        1. 服务器出于安全考虑（防遍历），返回 200 OK
        2. 响应体包含特定的错误码：code=506, error_message="visibility permission deny"
        """
        # 1. 初始化 API 对象
        account_api = AccountAPI(session=login_session)
        
        # 2. 使用一个不存在的 account_id
        invalid_id = "INVALID_ACCOUNT_ID_999999"
        print(f"\n[Step] 使用无效的账户 ID: {invalid_id}")
        detail_response = account_api.get_account_detail(invalid_id)
        
        # 3. 验证返回 200 状态码（服务器防遍历设计）
        print("[Step] 验证返回 200 状态码")
        assert detail_response.status_code == 200, \
            f"服务器应该返回 200，但实际返回了 {detail_response.status_code}"
        
        # 4. 验证响应体包含错误信息
        print("[Step] 验证响应体包含错误码")
        response_body = detail_response.json()
        
        # 验证响应结构完全匹配
        expected_response = {
            "code": 506,
            "error_message": "visibility permission deny",
            "data": None
        }
        
        assert response_body == expected_response, \
            f"响应体不匹配\n期望: {expected_response}\n实际: {response_body}"
        
        print(f"✓ 使用无效 ID 正确返回错误信息: code=506, error_message='visibility permission deny'")

    def test_get_account_detail_compare_with_list(self, login_session):
        """
        测试场景4：对比详情接口和列表接口返回的数据一致性
        验证点：
        1. 列表接口和详情接口返回的相同字段值一致
        """
        # 1. 初始化 API 对象
        account_api = AccountAPI(session=login_session)
        
        # 2. 获取账户列表
        print("\n[Step] 获取账户列表")
        list_response = account_api.list_accounts(size=1)
        parsed_list = account_api.parse_list_response(list_response)
        
        if len(parsed_list["content"]) == 0:
            pytest.skip("没有可用的账户数据")
        
        account_from_list = parsed_list["content"][0]
        account_id = account_from_list["id"]
        
        # 3. 获取账户详情
        print(f"[Step] 获取账户 {account_id} 的详情")
        detail_response = account_api.get_account_detail(account_id)
        parsed_detail = account_api.parse_detail_response(detail_response)
        account_from_detail = parsed_detail["data"]
        
        # 4. 对比关键字段
        print("[Step] 对比列表和详情中的关键字段")
        fields_to_compare = [
            "id",
            "account_name",
            "account_number",
            "account_status",
            "record_type"
        ]
        
        for field in fields_to_compare:
            list_value = account_from_list.get(field)
            detail_value = account_from_detail.get(field)
            assert list_value == detail_value, \
                f"字段 {field} 在列表和详情中不一致: 列表={list_value}, 详情={detail_value}"
        
        print(f"✓ 列表和详情接口返回的数据一致")
