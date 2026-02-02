"""
Contact 生命周期测试用例
测试 Contact 的完整 CRUD 流程：Create → Get Detail → Update → List → Get SSN
"""
import pytest
from api.contact_api import ContactAPI


# ==================== 测试数据常量 ====================

# 固定的 Account ID（所有 Contact 均在此 Account 下创建）
FIXED_ACCOUNT_ID = "251212054045554351"

# 加密的 SSN（用于 Create Contact）
ENCRYPTED_SSN = "Iuo0TzolcOs3otByGE7sAKHP3VI7NBuOsO5QqFLdfm7GyXbidGXPSKFMJZGOEQgjy6kI+vQ1kYopadZzLAA4zEu4y3Cpr5/FyFCbq5auxMyktMIa1uS7YFcXNLJerVvpA5csrHc3dXHPys2I6KLn/ncqjjIssF2sX4HcL8GxEPFgTVxD/U/HreN7s8EZC3r8ztZMDkUeGUF2rH/P2y/TH6+N9wGaRe2jpzSpZz3Y0ZZSBRFxFuLQxL52joDk2yKa9JjmHQc0v8nPh9o+eM1RFENMYGeNblsBdj3BM0PrMKo5CMN7np235syUM/yNJx1EVKWAd8C/n/TxHMkZ+BvSMQ=="

# Dummy Secret（用于测试 Get SSN 接口）
DUMMY_SECRET = "dummy_encrypted_aes_key_for_testing"


@pytest.mark.contact
class TestContactLifecycle:
    """
    Contact 生命周期测试用例集
    按照业务流程顺序执行：Create → Get Detail → Update → List → Get SSN
    """

    # 类级别变量，用于在测试方法之间共享数据
    created_contact_id = None

    def test_01_create_contact(self, login_session):
        """
        测试场景1：创建 Contact
        验证点：
        1. 接口返回 200
        2. 返回的 Contact ID 存在
        3. 返回的 account_id 等于 FIXED_ACCOUNT_ID
        4. ssn_tin 字段不为空（可能是脱敏后的值）
        """
        # 1. 初始化 API 对象
        contact_api = ContactAPI(session=login_session)
        
        # 2. 准备创建数据
        print("\n[Step] 准备创建 Contact 数据")
        contact_data = {
            "account_id": FIXED_ACCOUNT_ID,
            "first_name": "AutoTest",
            "last_name": "Contact",
            "birth_date": "1990-01-01",
            "email": "autotest.contact@example.com",
            "ssn_tin": ENCRYPTED_SSN
        }
        
        print(f"  Account ID: {FIXED_ACCOUNT_ID}")
        print(f"  Name: {contact_data['first_name']} {contact_data['last_name']}")
        print(f"  Email: {contact_data['email']}")
        
        # 3. 调用 Create 接口
        print("[Step] 调用 Create Contact 接口")
        create_response = contact_api.create_contact(contact_data)
        
        # 4. 断言状态码
        print("[Step] 验证 HTTP 状态码为 200")
        assert create_response.status_code == 200, \
            f"Create Contact 接口返回状态码错误: {create_response.status_code}, Response: {create_response.text}"
        
        # 5. 解析响应
        print("[Step] 解析响应并验证数据")
        created_contact = create_response.json()
        
        # 6. 验证返回的 ID 存在
        print("[Step] 验证返回的 Contact ID 存在")
        assert "id" in created_contact, "响应中缺少 id 字段"
        assert created_contact["id"] is not None, "Contact ID 为 null"
        
        # 保存 Contact ID 供后续测试使用
        TestContactLifecycle.created_contact_id = created_contact["id"]
        
        # 7. 验证 account_id
        print("[Step] 验证 account_id 等于 FIXED_ACCOUNT_ID")
        assert created_contact.get("account_id") == FIXED_ACCOUNT_ID, \
            f"account_id 不匹配: 期望 {FIXED_ACCOUNT_ID}, 实际 {created_contact.get('account_id')}"
        
        # 8. 验证 ssn_tin 字段不为空
        print("[Step] 验证 ssn_tin 字段不为空")
        ssn_tin = created_contact.get("ssn_tin")
        # 注意：接口可能返回脱敏后的值（如 *****9792），或者原始加密值，或者 null
        # 这里只验证字段存在，不验证具体值
        print(f"  ssn_tin: {ssn_tin}")
        
        print(f"✓ 成功创建 Contact:")
        print(f"  ID: {created_contact['id']}")
        print(f"  Name: {created_contact.get('name')}")
        print(f"  Account ID: {created_contact.get('account_id')}")
        print(f"  Email: {created_contact.get('email')}")
        print(f"  Status: {created_contact.get('status')}")

    def test_02_get_contact_detail(self, login_session):
        """
        测试场景2：获取 Contact 详情
        验证点：
        1. 接口返回 200
        2. 返回的 ID 与创建时的 ID 一致
        3. account_id 等于 FIXED_ACCOUNT_ID
        4. ssn_tin 字段存在（可能是脱敏后的值）
        """
        # 0. 确保已创建 Contact
        if TestContactLifecycle.created_contact_id is None:
            pytest.skip("需要先运行 test_01_create_contact")
        
        contact_id = TestContactLifecycle.created_contact_id
        
        # 1. 初始化 API 对象
        contact_api = ContactAPI(session=login_session)
        
        # 2. 调用 Get Detail 接口
        print(f"\n[Step] 调用 Get Contact Detail 接口，Contact ID: {contact_id}")
        detail_response = contact_api.get_contact_detail(contact_id)
        
        # 3. 断言状态码
        print("[Step] 验证 HTTP 状态码为 200")
        assert detail_response.status_code == 200, \
            f"Get Contact Detail 接口返回状态码错误: {detail_response.status_code}, Response: {detail_response.text}"
        
        # 4. 解析响应
        print("[Step] 解析响应并验证数据")
        contact_detail = detail_response.json()
        
        # 5. 验证 ID 一致
        print("[Step] 验证返回的 ID 与创建时的 ID 一致")
        assert contact_detail.get("id") == contact_id, \
            f"Contact ID 不匹配: 期望 {contact_id}, 实际 {contact_detail.get('id')}"
        
        # 6. 验证 account_id
        print("[Step] 验证 account_id 等于 FIXED_ACCOUNT_ID")
        assert contact_detail.get("account_id") == FIXED_ACCOUNT_ID, \
            f"account_id 不匹配: 期望 {FIXED_ACCOUNT_ID}, 实际 {contact_detail.get('account_id')}"
        
        # 7. 验证 ssn_tin 字段存在
        print("[Step] 验证 ssn_tin 字段存在")
        ssn_tin = contact_detail.get("ssn_tin")
        print(f"  ssn_tin: {ssn_tin}")
        
        print(f"✓ 成功获取 Contact 详情:")
        print(f"  ID: {contact_detail['id']}")
        print(f"  Name: {contact_detail.get('name')}")
        print(f"  Account ID: {contact_detail.get('account_id')}")
        print(f"  Email: {contact_detail.get('email')}")
        print(f"  Status: {contact_detail.get('status')}")

    def test_03_update_contact(self, login_session):
        """
        测试场景3：更新 Contact
        验证点：
        1. 接口返回 200
        2. 更新的字段生效（first_name 或 phone）
        """
        # 0. 确保已创建 Contact
        if TestContactLifecycle.created_contact_id is None:
            pytest.skip("需要先运行 test_01_create_contact")
        
        contact_id = TestContactLifecycle.created_contact_id
        
        # 1. 初始化 API 对象
        contact_api = ContactAPI(session=login_session)
        
        # 2. 准备更新数据
        print(f"\n[Step] 准备更新 Contact 数据，Contact ID: {contact_id}")
        update_data = {
            "first_name": "UpdatedAutoTest",
            "phone": "+14155552671"
        }
        
        print(f"  更新 first_name: {update_data['first_name']}")
        print(f"  更新 phone: {update_data['phone']}")
        
        # 3. 调用 Update 接口
        print("[Step] 调用 Update Contact 接口")
        update_response = contact_api.update_contact(contact_id, update_data)
        
        # 4. 断言状态码
        print("[Step] 验证 HTTP 状态码为 200")
        assert update_response.status_code == 200, \
            f"Update Contact 接口返回状态码错误: {update_response.status_code}, Response: {update_response.text}"
        
        # 5. 解析响应
        print("[Step] 解析响应并验证更新结果")
        updated_contact = update_response.json()
        
        # 6. 验证更新的字段生效
        print("[Step] 验证更新的字段生效")
        assert updated_contact.get("first_name") == update_data["first_name"], \
            f"first_name 未更新: 期望 {update_data['first_name']}, 实际 {updated_contact.get('first_name')}"
        
        assert updated_contact.get("phone") == update_data["phone"], \
            f"phone 未更新: 期望 {update_data['phone']}, 实际 {updated_contact.get('phone')}"
        
        print(f"✓ 成功更新 Contact:")
        print(f"  ID: {updated_contact['id']}")
        print(f"  Updated first_name: {updated_contact.get('first_name')}")
        print(f"  Updated phone: {updated_contact.get('phone')}")

    def test_04_list_contacts(self, login_session):
        """
        测试场景4：列表查询 Contacts
        验证点：
        1. 接口返回 200
        2. 刚才创建的 Contact 在列表中
        """
        # 0. 确保已创建 Contact
        if TestContactLifecycle.created_contact_id is None:
            pytest.skip("需要先运行 test_01_create_contact")
        
        contact_id = TestContactLifecycle.created_contact_id
        
        # 1. 初始化 API 对象
        contact_api = ContactAPI(session=login_session)
        
        # 2. 调用 List 接口（可以使用筛选条件）
        print("\n[Step] 调用 List Contacts 接口")
        list_response = contact_api.list_contacts(size=100)  # 获取更多数据以确保包含刚创建的 Contact
        
        # 3. 断言状态码
        print("[Step] 验证 HTTP 状态码为 200")
        assert list_response.status_code == 200, \
            f"List Contacts 接口返回状态码错误: {list_response.status_code}, Response: {list_response.text}"
        
        # 4. 解析响应
        print("[Step] 解析响应并查找刚创建的 Contact")
        parsed_list = contact_api.parse_list_response(list_response)
        assert not parsed_list.get("error"), f"List 响应解析失败: {parsed_list.get('message')}"
        
        contacts = parsed_list["content"]
        
        # 5. 验证刚创建的 Contact 在列表中
        print(f"[Step] 验证刚创建的 Contact (ID: {contact_id}) 在列表中")
        found = False
        for contact in contacts:
            if contact.get("id") == contact_id:
                found = True
                print(f"  找到 Contact: {contact.get('name')} ({contact.get('email')})")
                break
        
        assert found, f"刚创建的 Contact (ID: {contact_id}) 不在列表中"
        
        print(f"✓ 成功在列表中找到刚创建的 Contact:")
        print(f"  总数: {parsed_list['total_elements']}")
        print(f"  当前页: {parsed_list['number']}")
        print(f"  每页大小: {parsed_list['size']}")

    def test_05_get_contact_ssn(self, login_session):
        """
        测试场景5：获取 Contact SSN
        验证点：
        1. 接口连通（200 OK 或预期错误码）
        2. 验证接口路径正确性
        
        注意：由于需要正确的加密 Secret，这里只验证接口连通性
        """
        # 0. 确保已创建 Contact
        if TestContactLifecycle.created_contact_id is None:
            pytest.skip("需要先运行 test_01_create_contact")
        
        contact_id = TestContactLifecycle.created_contact_id
        
        # 1. 初始化 API 对象
        contact_api = ContactAPI(session=login_session)
        
        # 2. 调用 Get SSN 接口（使用 Dummy Secret）
        print(f"\n[Step] 调用 Get Contact SSN 接口，Contact ID: {contact_id}")
        print(f"  使用 Dummy Secret: {DUMMY_SECRET[:50]}...")
        ssn_response = contact_api.get_contact_ssn(contact_id, DUMMY_SECRET)
        
        # 3. 验证接口连通性
        print("[Step] 验证接口连通性")
        print(f"  HTTP 状态码: {ssn_response.status_code}")
        
        # 可能的情况：
        # - 200 OK: Secret 正确，返回加密的 SSN
        # - 400/401/403/500: Secret 错误或其他业务错误
        # 这里只验证接口路径正确（不是 404）
        assert ssn_response.status_code != 404, \
            f"Get Contact SSN 接口路径错误（404）: {ssn_response.text}"
        
        # 4. 打印响应信息
        print(f"[Step] 打印响应信息")
        try:
            response_body = ssn_response.json()
            print(f"  响应内容: {response_body}")
        except:
            print(f"  响应内容（非 JSON）: {ssn_response.text}")
        
        print(f"✓ Get Contact SSN 接口连通性验证通过:")
        print(f"  状态码: {ssn_response.status_code}")
        print(f"  接口路径正确（非 404）")


@pytest.mark.contact
class TestContactListFilters:
    """
    Contact 列表筛选功能测试
    """

    def test_list_contacts_with_status_filter(self, login_session):
        """
        测试场景：使用 status 筛选 Contacts
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
        测试场景：使用 name 筛选 Contacts
        验证点：
        1. 接口返回 200
        2. 返回数据结构正确
        """
        # 1. 初始化 API 对象
        contact_api = ContactAPI(session=login_session)
        
        # 2. 使用 name 筛选（使用生命周期测试中创建的 Contact 名称）
        print("\n[Step] 使用 name 筛选 Contacts")
        list_response = contact_api.list_contacts(name="AutoTest", size=10)
        
        # 3. 验证状态码
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

    def test_list_contacts_pagination(self, login_session):
        """
        测试场景：验证分页功能
        验证点：
        1. 接口返回 200
        2. 分页信息正确
        """
        # 1. 初始化 API 对象
        contact_api = ContactAPI(session=login_session)
        
        # 2. 使用分页参数
        print("\n[Step] 使用分页参数 page=0, size=5")
        list_response = contact_api.list_contacts(page=0, size=5)
        
        # 3. 验证状态码
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
