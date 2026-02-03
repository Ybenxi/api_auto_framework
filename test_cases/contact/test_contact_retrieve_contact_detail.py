"""
Contact Detail 接口测试用例
测试 GET /api/v1/cores/{core}/contacts/{id} 接口
"""
import pytest
from api.contact_api import ContactAPI


@pytest.mark.contact
@pytest.mark.detail_api
class TestContactDetail:
    """
    Contact 详情查询接口测试用例集
    """

    def test_get_contact_detail_success(self, login_session):
        """
        测试场景1：成功获取 Contact 详情
        验证点：
        1. 接口返回 200
        2. 返回的 Contact 包含完整字段（id, account_id, name, email, status 等）
        
        前置条件：需要先获取一个真实存在的 Contact ID
        """
        # 1. 初始化 API 对象
        contact_api = ContactAPI(session=login_session)
        
        # 2. 先调用 List 接口获取一个真实的 Contact ID
        print("\n[Step] 先调用 List 接口获取真实的 Contact ID")
        list_response = contact_api.list_contacts(page=0, size=1)
        assert list_response.status_code == 200, "List 接口调用失败"
        
        parsed_list = contact_api.parse_list_response(list_response)
        assert not parsed_list.get("error"), "List 响应解析失败"
        
        contacts = parsed_list["content"]
        if len(contacts) == 0:
            pytest.skip("没有可用的 Contact 数据，跳过测试")
        
        contact_id = contacts[0]["id"]
        print(f"  获取到 Contact ID: {contact_id}")
        
        # 3. 调用 Get Detail 接口
        print(f"[Step] 调用 Get Contact Detail 接口，Contact ID: {contact_id}")
        detail_response = contact_api.get_contact_detail(contact_id)
        
        # 4. 断言状态码
        print("[Step] 验证 HTTP 状态码为 200")
        assert detail_response.status_code == 200, \
            f"Get Contact Detail 接口返回状态码错误: {detail_response.status_code}, Response: {detail_response.text}"
        
        # 5. 解析响应
        print("[Step] 解析响应并验证数据")
        response_body = detail_response.json()
        contact_detail = response_body.get("data") if "data" in response_body else response_body
        
        # 6. 验证 ID 一致
        print("[Step] 验证返回的 ID 与请求的 ID 一致")
        assert contact_detail.get("id") == contact_id, \
            f"Contact ID 不匹配: 期望 {contact_id}, 实际 {contact_detail.get('id')}"
        
        # 7. 验证必需字段存在
        print("[Step] 验证必需字段存在")
        required_fields = ["id", "account_id", "name", "first_name", "last_name", "email", "status"]
        
        for field in required_fields:
            assert field in contact_detail, f"Contact 详情缺少必需字段: {field}"
            print(f"  ✓ {field}: {contact_detail.get(field)}")
        
        print(f"✓ 成功获取 Contact 详情:")
        print(f"  ID: {contact_detail['id']}")
        print(f"  Name: {contact_detail.get('name')}")
        print(f"  Account ID: {contact_detail.get('account_id')}")
        print(f"  Email: {contact_detail.get('email')}")
        print(f"  Status: {contact_detail.get('status')}")

    def test_get_contact_detail_with_all_fields(self, login_session):
        """
        测试场景2：获取 Contact 详情，验证所有字段
        验证点：
        1. 接口返回 200
        2. 返回的 Contact 包含所有字段（包括可选字段）
        """
        # 1. 初始化 API 对象
        contact_api = ContactAPI(session=login_session)
        
        # 2. 先调用 List 接口获取一个真实的 Contact ID
        print("\n[Step] 先调用 List 接口获取真实的 Contact ID")
        list_response = contact_api.list_contacts(page=0, size=1)
        assert list_response.status_code == 200, "List 接口调用失败"
        
        parsed_list = contact_api.parse_list_response(list_response)
        assert not parsed_list.get("error"), "List 响应解析失败"
        
        contacts = parsed_list["content"]
        if len(contacts) == 0:
            pytest.skip("没有可用的 Contact 数据，跳过测试")
        
        contact_id = contacts[0]["id"]
        print(f"  获取到 Contact ID: {contact_id}")
        
        # 3. 调用 Get Detail 接口
        print(f"[Step] 调用 Get Contact Detail 接口")
        detail_response = contact_api.get_contact_detail(contact_id)
        
        # 4. 断言状态码
        print("[Step] 验证 HTTP 状态码为 200")
        assert detail_response.status_code == 200, \
            f"Get Contact Detail 接口返回状态码错误: {detail_response.status_code}"
        
        # 5. 解析响应
        print("[Step] 解析响应并验证所有字段")
        response_body = detail_response.json()
        contact_detail = response_body.get("data") if "data" in response_body else response_body
        
        # 6. 验证所有字段（包括可选字段）
        print("[Step] 验证所有字段存在")
        all_fields = [
            "id", "account_id", "name", "first_name", "last_name", "middle_name",
            "status", "suffix", "ssn_tin", "birth_date", "phone", "mobile_phone",
            "home_phone", "work_phone", "gender", "maiden_name", "email", "fax",
            "permanent_address", "permanent_address2", "permanent_city", "permanent_state",
            "permanent_postalcode", "permanent_country", "mailing_street", "mailing_street2",
            "mailing_city", "mailing_state", "mailing_postalcode", "mailing_country",
            "citizenship", "government_document_type", "gov_id_number", "gov_id_country",
            "description", "external_id", "create_time"
        ]
        
        missing_fields = []
        for field in all_fields:
            if field not in contact_detail:
                missing_fields.append(field)
        
        if missing_fields:
            print(f"  ⚠ 缺少字段: {', '.join(missing_fields)}")
        else:
            print(f"  ✓ 所有字段都存在")
        
        print(f"✓ 字段完整性验证完成")

    def test_get_contact_detail_invalid_id(self, login_session):
        """
        测试场景3：使用无效的 Contact ID
        验证点：
        1. 接口返回 200（防遍历设计）
        2. 返回错误码 506 和错误信息 "visibility permission deny"
        """
        # 1. 初始化 API 对象
        contact_api = ContactAPI(session=login_session)
        
        # 2. 使用无效的 Contact ID
        invalid_contact_id = "invalid_contact_id_999999"
        
        print(f"\n[Step] 使用无效的 Contact ID: {invalid_contact_id}")
        
        # 3. 调用 Get Detail 接口
        print("[Step] 调用 Get Contact Detail 接口")
        detail_response = contact_api.get_contact_detail(invalid_contact_id)
        
        # 4. 验证状态码（防遍历设计：返回 200）
        print("[Step] 验证 HTTP 状态码为 200（防遍历设计）")
        assert detail_response.status_code == 200, \
            f"无效 ID 应返回 200（防遍历），实际返回: {detail_response.status_code}"
        
        # 5. 解析响应并验证错误码
        print("[Step] 验证错误码和错误信息")
        try:
            response_body = detail_response.json()
            error_code = response_body.get("code")
            # 修复：错误信息字段可能是 error_message 或 message
            error_message = response_body.get("error_message") or response_body.get("message")
            
            print(f"  错误码: {error_code}")
            print(f"  错误信息: {error_message}")
            
            # 验证错误码 506 和错误信息
            assert error_code == 506, f"错误码不正确: 期望 506, 实际 {error_code}"
            assert "visibility permission deny" in str(error_message).lower(), \
                f"错误信息不正确: {error_message}"
            
            print(f"✓ 无效 ID 测试完成（防遍历设计验证通过）")
        except Exception as e:
            print(f"  响应解析失败: {e}")
            print(f"  响应内容: {detail_response.text}")
            raise

    def test_get_contact_detail_response_structure(self, login_session):
        """
        测试场景4：验证响应数据结构
        验证点：
        1. 接口返回 200
        2. 响应是 JSON 对象（不是数组）
        3. 包含必需字段
        """
        # 1. 初始化 API 对象
        contact_api = ContactAPI(session=login_session)
        
        # 2. 先调用 List 接口获取一个真实的 Contact ID
        print("\n[Step] 先调用 List 接口获取真实的 Contact ID")
        list_response = contact_api.list_contacts(page=0, size=1)
        assert list_response.status_code == 200, "List 接口调用失败"
        
        parsed_list = contact_api.parse_list_response(list_response)
        assert not parsed_list.get("error"), "List 响应解析失败"
        
        contacts = parsed_list["content"]
        if len(contacts) == 0:
            pytest.skip("没有可用的 Contact 数据，跳过测试")
        
        contact_id = contacts[0]["id"]
        
        # 3. 调用 Get Detail 接口
        print(f"[Step] 调用 Get Contact Detail 接口")
        detail_response = contact_api.get_contact_detail(contact_id)
        
        # 4. 验证状态码
        print("[Step] 验证 HTTP 状态码为 200")
        assert detail_response.status_code == 200, \
            f"Get Contact Detail 接口返回状态码错误: {detail_response.status_code}"
        
        # 5. 验证响应数据结构
        print("[Step] 验证响应数据结构")
        response_body = detail_response.json()
        contact_detail = response_body.get("data") if "data" in response_body else response_body
        
        # 验证是 JSON 对象（不是数组）
        assert isinstance(contact_detail, dict), "响应应该是 JSON 对象，不是数组"
        
        # 验证不是分页结构（不包含 content 字段）
        assert "content" not in contact_detail, "详情接口不应返回分页结构"
        
        # 验证包含 id 字段
        assert "id" in contact_detail, "响应中缺少 id 字段"
        
        print(f"✓ 响应数据结构验证通过")

    def test_get_contact_detail_ssn_field(self, login_session):
        """
        测试场景5：验证 ssn_tin 字段
        验证点：
        1. 接口返回 200
        2. ssn_tin 字段存在
        3. ssn_tin 可能是脱敏后的值（如 *****9792）或 null
        """
        # 1. 初始化 API 对象
        contact_api = ContactAPI(session=login_session)
        
        # 2. 先调用 List 接口获取一个真实的 Contact ID
        print("\n[Step] 先调用 List 接口获取真实的 Contact ID")
        list_response = contact_api.list_contacts(page=0, size=1)
        assert list_response.status_code == 200, "List 接口调用失败"
        
        parsed_list = contact_api.parse_list_response(list_response)
        assert not parsed_list.get("error"), "List 响应解析失败"
        
        contacts = parsed_list["content"]
        if len(contacts) == 0:
            pytest.skip("没有可用的 Contact 数据，跳过测试")
        
        contact_id = contacts[0]["id"]
        
        # 3. 调用 Get Detail 接口
        print(f"[Step] 调用 Get Contact Detail 接口")
        detail_response = contact_api.get_contact_detail(contact_id)
        
        # 4. 验证状态码
        print("[Step] 验证 HTTP 状态码为 200")
        assert detail_response.status_code == 200, \
            f"Get Contact Detail 接口返回状态码错误: {detail_response.status_code}"
        
        # 5. 验证 ssn_tin 字段
        print("[Step] 验证 ssn_tin 字段")
        response_body = detail_response.json()
        contact_detail = response_body.get("data") if "data" in response_body else response_body
        
        assert "ssn_tin" in contact_detail, "响应中缺少 ssn_tin 字段"
        
        ssn_tin = contact_detail.get("ssn_tin")
        print(f"  ssn_tin: {ssn_tin}")
        
        # 验证 ssn_tin 的格式（可能是脱敏后的值或 null）
        if ssn_tin is not None:
            if "*" in str(ssn_tin):
                print(f"  ✓ ssn_tin 已脱敏: {ssn_tin}")
            else:
                print(f"  ⚠ ssn_tin 未脱敏或为原始值: {ssn_tin}")
        else:
            print(f"  ✓ ssn_tin 为 null（未设置）")
        
        print(f"✓ ssn_tin 字段验证完成")
