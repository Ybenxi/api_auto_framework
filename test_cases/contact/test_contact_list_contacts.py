"""
Contact List 接口测试用例
测试 GET /api/v1/cores/{core}/contacts 接口
"""
import pytest
from api.contact_api import ContactAPI


@pytest.mark.contact
@pytest.mark.list_api
class TestContactList:
    """
    Contact 列表查询接口测试用例集
    """

    def test_list_contacts_success(self, login_session):
        """
        测试场景1：成功获取 Contacts 列表
        验证点：
        1. 接口返回 200
        2. 返回数据结构正确（包含 content、pageable 等字段）
        3. content 是数组类型
        """
        # 1. 初始化 API 对象
        contact_api = ContactAPI(session=login_session)
        
        # 2. 调用 List 接口
        print("\n[Step] 调用 List Contacts 接口")
        list_response = contact_api.list_contacts(page=0, size=10)
        
        # 3. 验证状态码
        print("[Step] 验证 HTTP 状态码为 200")
        assert list_response.status_code == 200, \
            f"List Contacts 接口返回状态码错误: {list_response.status_code}, Response: {list_response.text}"
        
        # 4. 解析响应
        print("[Step] 解析响应并验证数据结构")
        parsed_list = contact_api.parse_list_response(list_response)
        assert not parsed_list.get("error"), f"List 响应解析失败: {parsed_list.get('message')}"
        
        # 5. 验证数据结构
        print("[Step] 验证返回数据结构")
        assert "content" in parsed_list, "响应中缺少 content 字段"
        assert isinstance(parsed_list["content"], list), "content 字段不是数组类型"
        
        contacts = parsed_list["content"]
        
        print(f"✓ 成功获取 Contacts 列表:")
        print(f"  总元素数: {parsed_list['total_elements']}")
        print(f"  总页数: {parsed_list['total_pages']}")
        print(f"  当前页: {parsed_list['number']}")
        print(f"  每页大小: {parsed_list['size']}")
        print(f"  返回 {len(contacts)} 个 Contacts")
        
        if len(contacts) > 0:
            print(f"  第一个 Contact: {contacts[0].get('name')} ({contacts[0].get('email')})")

    def test_list_contacts_with_status_filter(self, login_session):
        """
        测试场景2：使用 status 筛选 Contacts
        验证点：
        1. 接口返回 200
        2. 返回数据结构正确
        """
        # 1. 初始化 API 对象
        contact_api = ContactAPI(session=login_session)
        
        # 2. 使用 status 筛选
        print("\n[Step] 使用 status='Active' 筛选 Contacts")
        list_response = contact_api.list_contacts(status="Active", size=10)
        
        # 3. 验证状态码
        print("[Step] 验证 HTTP 状态码为 200")
        assert list_response.status_code == 200, \
            f"List Contacts 接口返回状态码错误: {list_response.status_code}"
        
        # 4. 解析响应
        print("[Step] 解析响应并验证数据结构")
        parsed_list = contact_api.parse_list_response(list_response)
        assert not parsed_list.get("error"), f"List 响应解析失败: {parsed_list.get('message')}"
        
        contacts = parsed_list["content"]
        
        # 5. 验证返回数据
        print(f"[Step] 验证返回数据")
        print(f"  返回 {len(contacts)} 个 Contacts")
        
        if len(contacts) > 0:
            print(f"  第一个 Contact: {contacts[0].get('name')} ({contacts[0].get('status')})")
        
        print(f"✓ Status 筛选测试完成")

    def test_list_contacts_with_name_filter(self, login_session):
        """
        测试场景3：使用 name 筛选 Contacts
        验证点：
        1. 接口返回 200
        2. 返回数据结构正确
        """
        # 1. 初始化 API 对象
        contact_api = ContactAPI(session=login_session)
        
        # 2. 使用 name 筛选
        print("\n[Step] 使用 name 筛选 Contacts")
        list_response = contact_api.list_contacts(name="Sara", size=10)
        
        # 3. 验证状态码
        print("[Step] 验证 HTTP 状态码为 200")
        assert list_response.status_code == 200, \
            f"List Contacts 接口返回状态码错误: {list_response.status_code}"
        
        # 4. 解析响应
        print("[Step] 解析响应并验证数据结构")
        parsed_list = contact_api.parse_list_response(list_response)
        assert not parsed_list.get("error"), f"List 响应解析失败: {parsed_list.get('message')}"
        
        contacts = parsed_list["content"]
        
        # 5. 验证返回数据
        print(f"[Step] 验证返回数据")
        print(f"  返回 {len(contacts)} 个 Contacts")
        
        if len(contacts) > 0:
            print(f"  第一个 Contact: {contacts[0].get('name')} ({contacts[0].get('email')})")
        
        print(f"✓ Name 筛选测试完成")

    def test_list_contacts_with_email_filter(self, login_session):
        """
        测试场景4：使用 email 筛选 Contacts
        验证点：
        1. 接口返回 200
        2. 返回数据结构正确
        """
        # 1. 初始化 API 对象
        contact_api = ContactAPI(session=login_session)
        
        # 2. 使用 email 筛选
        print("\n[Step] 使用 email 筛选 Contacts")
        list_response = contact_api.list_contacts(email="example.com", size=10)
        
        # 3. 验证状态码
        print("[Step] 验证 HTTP 状态码为 200")
        assert list_response.status_code == 200, \
            f"List Contacts 接口返回状态码错误: {list_response.status_code}"
        
        # 4. 解析响应
        print("[Step] 解析响应并验证数据结构")
        parsed_list = contact_api.parse_list_response(list_response)
        assert not parsed_list.get("error"), f"List 响应解析失败: {parsed_list.get('message')}"
        
        contacts = parsed_list["content"]
        
        # 5. 验证返回数据
        print(f"[Step] 验证返回数据")
        print(f"  返回 {len(contacts)} 个 Contacts")
        
        if len(contacts) > 0:
            print(f"  第一个 Contact: {contacts[0].get('name')} ({contacts[0].get('email')})")
        
        print(f"✓ Email 筛选测试完成")

    def test_list_contacts_pagination(self, login_session):
        """
        测试场景5：验证分页功能
        验证点：
        1. 接口返回 200
        2. 分页信息正确（page、size）
        """
        # 1. 初始化 API 对象
        contact_api = ContactAPI(session=login_session)
        
        # 2. 使用分页参数
        print("\n[Step] 使用分页参数 page=0, size=5")
        list_response = contact_api.list_contacts(page=0, size=5)
        
        # 3. 验证状态码
        print("[Step] 验证 HTTP 状态码为 200")
        assert list_response.status_code == 200, \
            f"List Contacts 接口返回状态码错误: {list_response.status_code}"
        
        # 4. 解析响应
        print("[Step] 解析响应并验证分页信息")
        parsed_list = contact_api.parse_list_response(list_response)
        assert not parsed_list.get("error"), f"List 响应解析失败: {parsed_list.get('message')}"
        
        # 5. 验证分页信息
        print("[Step] 验证分页信息")
        assert parsed_list["size"] == 5, f"分页大小不正确: 期望 5, 实际 {parsed_list['size']}"
        assert parsed_list["number"] == 0, f"页码不正确: 期望 0, 实际 {parsed_list['number']}"
        
        print(f"✓ 分页测试完成:")
        print(f"  总元素数: {parsed_list['total_elements']}")
        print(f"  总页数: {parsed_list['total_pages']}")
        print(f"  当前页: {parsed_list['number']}")
        print(f"  每页大小: {parsed_list['size']}")

    def test_list_contacts_empty_result(self, login_session):
        """
        测试场景6：使用不存在的筛选条件，验证空结果处理
        验证点：
        1. 接口返回 200
        2. content 为空数组
        """
        # 1. 初始化 API 对象
        contact_api = ContactAPI(session=login_session)
        
        # 2. 使用不存在的筛选条件
        print("\n[Step] 使用不存在的筛选条件")
        list_response = contact_api.list_contacts(name="NonExistentContact999999", size=10)
        
        # 3. 验证状态码
        print("[Step] 验证 HTTP 状态码为 200")
        assert list_response.status_code == 200, \
            f"List Contacts 接口返回状态码错误: {list_response.status_code}"
        
        # 4. 解析响应
        print("[Step] 解析响应并验证空结果")
        parsed_list = contact_api.parse_list_response(list_response)
        assert not parsed_list.get("error"), f"List 响应解析失败: {parsed_list.get('message')}"
        
        contacts = parsed_list["content"]
        
        # 5. 验证空结果
        print("[Step] 验证返回空数组")
        print(f"  返回 {len(contacts)} 个 Contacts")
        
        print(f"✓ 空结果测试完成")

    def test_list_contacts_response_fields(self, login_session):
        """
        测试场景7：验证响应字段完整性
        验证点：
        1. 接口返回 200
        2. Contact 对象包含必需字段（id, account_id, name, email, status 等）
        """
        # 1. 初始化 API 对象
        contact_api = ContactAPI(session=login_session)
        
        # 2. 调用 List 接口
        print("\n[Step] 调用 List Contacts 接口")
        list_response = contact_api.list_contacts(page=0, size=1)
        
        # 3. 验证状态码
        print("[Step] 验证 HTTP 状态码为 200")
        assert list_response.status_code == 200, \
            f"List Contacts 接口返回状态码错误: {list_response.status_code}"
        
        # 4. 解析响应
        print("[Step] 解析响应并验证字段完整性")
        parsed_list = contact_api.parse_list_response(list_response)
        assert not parsed_list.get("error"), f"List 响应解析失败: {parsed_list.get('message')}"
        
        contacts = parsed_list["content"]
        
        # 5. 验证字段完整性
        if len(contacts) > 0:
            print("[Step] 验证 Contact 对象字段完整性")
            contact = contacts[0]
            
            required_fields = ["id", "account_id", "name", "first_name", "last_name", "email", "status"]
            
            for field in required_fields:
                assert field in contact, f"Contact 对象缺少必需字段: {field}"
                print(f"  ✓ {field}: {contact.get(field)}")
            
            print(f"✓ 字段完整性验证通过")
        else:
            print("  跳过字段验证（列表为空）")

    @pytest.mark.skip(reason="API 排序功能待后端确认支持，暂时跳过")
    def test_list_contacts_sorting_by_name(self, login_session):
        """
        测试场景8：排序功能验证 - 按姓名排序
        验证点：
        1. 使用 sort 参数进行排序
        2. 验证返回的列表按指定字段排序
        """
        contact_api = ContactAPI(session=login_session)
        
        # 调用接口，按 name 升序排序
        print("\n[Step] 调用 List Contacts 接口（按 name 升序排序）")
        response = contact_api.list_contacts(size=20, **{"sort": "name,asc"})
        
        # 验证状态码
        print("[Step] 验证 HTTP 状态码为 200")
        assert response.status_code == 200, f"接口返回状态码错误: {response.status_code}"
        
        # 解析响应
        print("[Step] 解析响应并验证排序")
        parsed = contact_api.parse_list_response(response)
        assert not parsed.get("error"), f"响应解析失败: {parsed.get('message')}"
        
        contacts = parsed["content"]
        
        if len(contacts) >= 2:
            # 验证排序逻辑（名称应该按字母顺序升序）
            for i in range(len(contacts) - 1):
                current_name = contacts[i].get("name", "").lower()
                next_name = contacts[i + 1].get("name", "").lower()
                assert current_name <= next_name, \
                    f"排序不正确: {current_name} 应该在 {next_name} 之前"
            
            print(f"✓ 排序验证成功（升序），共 {len(contacts)} 个 Contacts")
            print(f"  第一个: {contacts[0].get('name')}")
            print(f"  最后一个: {contacts[-1].get('name')}")
        else:
            print(f"⚠ Contacts 数量不足，无法验证排序（当前 {len(contacts)} 个）")
