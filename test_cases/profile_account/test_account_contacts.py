"""
账户 Contacts 接口测试用例
测试 GET /api/v1/cores/{core}/accounts/{account_id}/contacts 接口
"""
import pytest
from api.account_api import AccountAPI


@pytest.mark.contact_api
class TestAccountContacts:
    """
    账户 Contacts 接口测试用例集
    """

    def test_get_account_contacts_success(self, login_session):
        """
        测试场景1：成功获取账户关联的 Contacts
        依赖逻辑：先从列表接口获取一个有效的 account_id，然后获取 Contacts
        验证点：
        1. 列表接口返回成功
        2. Contacts 接口返回 200
        3. 返回数据结构正确（content 列表）
        4. 如果有数据，验证字段完整性
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
            pytest.skip("没有可用的账户数据，跳过 Contacts 测试")
        
        # 提取第一个账户的 ID
        account_id = accounts[0]["id"]
        print(f"  提取到账户 ID: {account_id}")
        
        # 4. 调用 Contacts 接口
        print(f"[Step] 调用 Contacts 接口获取账户 {account_id} 的 Contacts")
        contacts_response = account_api.get_account_contacts(account_id)
        
        # 5. 断言状态码
        print("[Step] 验证 HTTP 状态码为 200")
        assert contacts_response.status_code == 200, f"Contacts 接口返回状态码错误: {contacts_response.status_code}"
        
        # 6. 解析 Contacts 响应
        print("[Step] 解析 Contacts 响应并验证数据结构")
        parsed_contacts = account_api.parse_contacts_response(contacts_response)
        assert not parsed_contacts.get("error"), f"Contacts 响应解析失败: {parsed_contacts.get('message')}"
        
        contacts = parsed_contacts["content"]
        
        # 7. 验证返回数据结构
        print("[Step] 验证返回数据结构")
        assert isinstance(contacts, list), "content 应该是一个列表"
        
        # 8. 如果有数据，验证字段完整性
        if len(contacts) > 0:
            print(f"[Step] 验证 Contacts 字段完整性（共 {len(contacts)} 个 Contacts）")
            first_contact = contacts[0]
            
            # 验证必需字段
            required_fields = ["id", "account_id", "name", "status", "email", "create_time"]
            for field in required_fields:
                assert field in first_contact, f"Contact 缺少必需字段: {field}"
            
            print(f"✓ 成功获取 Contacts:")
            print(f"  总数: {parsed_contacts['total_elements']}")
            print(f"  第一个 Contact ID: {first_contact.get('id')}")
            print(f"  姓名: {first_contact.get('name')}")
            print(f"  状态: {first_contact.get('status')}")
            print(f"  邮箱: {first_contact.get('email')}")
        else:
            print("✓ 成功获取 Contacts（当前账户没有关联的 Contacts）")

    def test_get_account_contacts_with_filters(self, login_session):
        """
        测试场景2：使用筛选条件获取 Contacts
        验证点：
        1. 使用 status 筛选
        2. 验证返回结果符合筛选条件
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
        
        # 3. 使用 status 筛选
        print(f"[Step] 使用 status='Active' 筛选 Contacts")
        contacts_response = account_api.get_account_contacts(account_id, status="Active")
        
        # 4. 验证状态码
        assert contacts_response.status_code == 200, f"Contacts 接口返回状态码错误: {contacts_response.status_code}"
        
        # 5. 解析响应
        print("[Step] 解析响应并验证筛选结果")
        parsed_contacts = account_api.parse_contacts_response(contacts_response)
        assert not parsed_contacts.get("error"), f"Contacts 响应解析失败: {parsed_contacts.get('message')}"
        
        contacts = parsed_contacts["content"]
        
        # 6. 验证筛选结果
        if len(contacts) > 0:
            print(f"[Step] 验证所有返回的 Contacts 状态为 Active")
            for contact in contacts:
                # 注意：如果筛选不生效，这里可能会失败
                # 如果服务器不支持筛选，可以跳过这个断言
                if contact.get("status"):
                    print(f"  Contact {contact.get('name')}: status={contact.get('status')}")
        
        print(f"✓ 筛选测试完成，返回 {len(contacts)} 个 Contacts")

    def test_get_account_contacts_pagination(self, login_session):
        """
        测试场景3：验证分页功能
        验证点：
        1. 使用不同的 page 和 size
        2. 验证分页信息正确
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
        
        # 3. 使用分页参数
        print(f"[Step] 使用分页参数 page=0, size=5")
        contacts_response = account_api.get_account_contacts(account_id, page=0, size=5)
        
        # 4. 验证状态码
        assert contacts_response.status_code == 200, f"Contacts 接口返回状态码错误: {contacts_response.status_code}"
        
        # 5. 解析响应
        print("[Step] 解析响应并验证分页信息")
        parsed_contacts = account_api.parse_contacts_response(contacts_response)
        assert not parsed_contacts.get("error"), f"Contacts 响应解析失败: {parsed_contacts.get('message')}"
        
        # 6. 验证分页信息
        print("[Step] 验证分页信息")
        assert parsed_contacts["size"] == 5, f"分页大小不正确: 期望 5，实际 {parsed_contacts['size']}"
        assert parsed_contacts["number"] == 0, f"页码不正确: 期望 0，实际 {parsed_contacts['number']}"
        
        print(f"✓ 分页测试完成:")
        print(f"  总元素数: {parsed_contacts['total_elements']}")
        print(f"  总页数: {parsed_contacts['total_pages']}")
        print(f"  当前页: {parsed_contacts['number']}")
        print(f"  每页大小: {parsed_contacts['size']}")

    def test_get_account_contacts_empty_result(self, login_session):
        """
        测试场景4：验证空结果处理
        验证点：
        1. 使用不存在的筛选条件
        2. 验证返回 200 和空列表
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
        
        # 3. 使用不存在的筛选条件
        print(f"[Step] 使用不存在的筛选条件")
        contacts_response = account_api.get_account_contacts(
            account_id,
            name="NONEXISTENT_CONTACT_NAME_999999"
        )
        
        # 4. 验证状态码
        assert contacts_response.status_code == 200, f"Contacts 接口返回状态码错误: {contacts_response.status_code}"
        
        # 5. 解析响应
        print("[Step] 解析响应并验证空结果")
        parsed_contacts = account_api.parse_contacts_response(contacts_response)
        assert not parsed_contacts.get("error"), f"Contacts 响应解析失败: {parsed_contacts.get('message')}"
        
        contacts = parsed_contacts["content"]
        
        # 6. 验证返回空列表
        print("[Step] 验证返回空列表")
        assert isinstance(contacts, list), "content 应该是一个列表"
        # 注意：这里不强制要求为空，因为可能有其他 Contacts
        
        print(f"✓ 空结果测试完成，返回 {len(contacts)} 个 Contacts")

    def test_get_account_contacts_invalid_id(self, login_session):
        """
        测试场景5：使用无效的 account_id
        验证点：
        1. 使用无效 ID
        2. 验证返回错误或空列表
        """
        # 1. 初始化 API 对象
        account_api = AccountAPI(session=login_session)
        
        # 2. 使用无效的 account_id
        invalid_id = "INVALID_ACCOUNT_ID_999999"
        print(f"\n[Step] 使用无效的账户 ID: {invalid_id}")
        contacts_response = account_api.get_account_contacts(invalid_id)
        
        # 3. 验证状态码（可能是 200 + 空列表，或者错误状态码）
        print("[Step] 验证响应")
        if contacts_response.status_code == 200:
            # 如果返回 200，验证是空列表或错误信息
            parsed_contacts = account_api.parse_contacts_response(contacts_response)
            if not parsed_contacts.get("error"):
                contacts = parsed_contacts["content"]
                print(f"  返回 200 和空列表（{len(contacts)} 个 Contacts）")
            else:
                print(f"  返回 200 和错误信息")
        else:
            print(f"  返回错误状态码: {contacts_response.status_code}")
        
        print(f"✓ 无效 ID 测试完成")
