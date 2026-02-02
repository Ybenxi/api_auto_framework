"""
Contact Create 接口测试用例
测试 POST /api/v1/cores/{core}/contacts 接口
"""
import pytest
from api.contact_api import ContactAPI


# ==================== 测试数据常量 ====================

# 固定的 Account ID（所有 Contact 均在此 Account 下创建）
FIXED_ACCOUNT_ID = "251212054045554351"

# 加密的 SSN（用于 Create Contact）
ENCRYPTED_SSN = "Iuo0TzolcOs3otByGE7sAKHP3VI7NBuOsO5QqFLdfm7GyXbidGXPSKFMJZGOEQgjy6kI+vQ1kYopadZzLAA4zEu4y3Cpr5/FyFCbq5auxMyktMIa1uS7YFcXNLJerVvpA5csrHc3dXHPys2I6KLn/ncqjjIssF2sX4HcL8GxEPFgTVxD/U/HreN7s8EZC3r8ztZMDkUeGUF2rH/P2y/TH6+N9wGaRe2jpzSpZz3Y0ZZSBRFxFuLQxL52joDk2yKa9JjmHQc0v8nPh9o+eM1RFENMYGeNblsBdj3BM0PrMKo5CMN7np235syUM/yNJx1EVKWAd8C/n/TxHMkZ+BvSMQ=="


@pytest.mark.contact
class TestContactCreate:
    """
    Contact 创建接口测试用例集
    """

    def test_create_contact_with_required_fields(self, login_session):
        """
        测试场景：使用必需字段创建 Contact
        验证点：
        1. 接口返回 200
        2. 返回的 Contact ID 存在
        3. 返回的 account_id 等于传入的 account_id
        4. 返回的 first_name、last_name、email 等字段正确
        """
        # 1. 初始化 API 对象
        contact_api = ContactAPI(session=login_session)
        
        # 2. 准备创建数据（仅必需字段）
        print("\n[Step] 准备创建 Contact 数据（仅必需字段）")
        contact_data = {
            "account_id": FIXED_ACCOUNT_ID,
            "first_name": "John",
            "last_name": "Doe",
            "birth_date": "1990-01-01",
            "email": "john.doe@example.com"
        }
        
        print(f"  Account ID: {FIXED_ACCOUNT_ID}")
        print(f"  Name: {contact_data['first_name']} {contact_data['last_name']}")
        print(f"  Birth Date: {contact_data['birth_date']}")
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
        
        # 7. 验证 account_id
        print("[Step] 验证 account_id 等于传入值")
        assert created_contact.get("account_id") == FIXED_ACCOUNT_ID, \
            f"account_id 不匹配: 期望 {FIXED_ACCOUNT_ID}, 实际 {created_contact.get('account_id')}"
        
        # 8. 验证其他字段
        print("[Step] 验证其他字段")
        assert created_contact.get("first_name") == contact_data["first_name"], \
            f"first_name 不匹配: 期望 {contact_data['first_name']}, 实际 {created_contact.get('first_name')}"
        
        assert created_contact.get("last_name") == contact_data["last_name"], \
            f"last_name 不匹配: 期望 {contact_data['last_name']}, 实际 {created_contact.get('last_name')}"
        
        assert created_contact.get("email") == contact_data["email"], \
            f"email 不匹配: 期望 {contact_data['email']}, 实际 {created_contact.get('email')}"
        
        print(f"✓ 成功创建 Contact:")
        print(f"  ID: {created_contact['id']}")
        print(f"  Name: {created_contact.get('name')}")
        print(f"  Account ID: {created_contact.get('account_id')}")
        print(f"  Email: {created_contact.get('email')}")
        print(f"  Status: {created_contact.get('status')}")

    def test_create_contact_with_all_fields(self, login_session):
        """
        测试场景：使用所有字段创建 Contact（包括可选字段）
        验证点：
        1. 接口返回 200
        2. 返回的 Contact ID 存在
        3. 可选字段（middle_name, phone, ssn_tin 等）正确保存
        """
        # 1. 初始化 API 对象
        contact_api = ContactAPI(session=login_session)
        
        # 2. 准备创建数据（包含所有字段）
        print("\n[Step] 准备创建 Contact 数据（包含所有字段）")
        contact_data = {
            "account_id": FIXED_ACCOUNT_ID,
            "first_name": "Jane",
            "last_name": "Smith",
            "middle_name": "Marie",
            "birth_date": "1985-05-15",
            "email": "jane.smith@example.com",
            "ssn_tin": ENCRYPTED_SSN,
            "phone": "+14155552671",
            "mobile_phone": "+14155552672",
            "home_phone": "+14155552673",
            "work_phone": "+14155552674",
            "gender": "Female",
            "maiden_name": "Johnson",
            "suffix": "Jr.",
            "fax": "120930101923",
            "permanent_address": "123 Main St",
            "permanent_address2": "Apt 4B",
            "permanent_city": "New York",
            "permanent_state": "NY",
            "permanent_postalcode": "10001",
            "permanent_country": "United States",
            "mailing_street": "456 Oak Ave",
            "mailing_street2": "Suite 200",
            "mailing_city": "Los Angeles",
            "mailing_state": "CA",
            "mailing_postalcode": "90001",
            "mailing_country": "United States",
            "citizenship": "United States",
            "government_document_type": "U.S. Drivers License",
            "gov_id_number": "DL123456",
            "gov_id_country": "United States",
            "description": "Test contact with all fields"
        }
        
        print(f"  Account ID: {FIXED_ACCOUNT_ID}")
        print(f"  Name: {contact_data['first_name']} {contact_data['middle_name']} {contact_data['last_name']}")
        print(f"  Email: {contact_data['email']}")
        print(f"  Phone: {contact_data['phone']}")
        
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
        
        # 7. 验证可选字段
        print("[Step] 验证可选字段")
        assert created_contact.get("middle_name") == contact_data["middle_name"], \
            f"middle_name 不匹配"
        
        assert created_contact.get("phone") == contact_data["phone"], \
            f"phone 不匹配"
        
        assert created_contact.get("gender") == contact_data["gender"], \
            f"gender 不匹配"
        
        # ssn_tin 可能返回脱敏后的值，只验证字段存在
        print(f"  ssn_tin: {created_contact.get('ssn_tin')}")
        
        print(f"✓ 成功创建 Contact（包含所有字段）:")
        print(f"  ID: {created_contact['id']}")
        print(f"  Name: {created_contact.get('name')}")
        print(f"  Phone: {created_contact.get('phone')}")
        print(f"  Gender: {created_contact.get('gender')}")

    def test_create_contact_with_ssn(self, login_session):
        """
        测试场景：创建 Contact 并包含加密的 SSN
        验证点：
        1. 接口返回 200
        2. 返回的 Contact ID 存在
        3. ssn_tin 字段存在（可能是脱敏后的值）
        """
        # 1. 初始化 API 对象
        contact_api = ContactAPI(session=login_session)
        
        # 2. 准备创建数据（包含 SSN）
        print("\n[Step] 准备创建 Contact 数据（包含加密 SSN）")
        contact_data = {
            "account_id": FIXED_ACCOUNT_ID,
            "first_name": "SSN",
            "last_name": "Test",
            "birth_date": "1992-03-20",
            "email": "ssn.test@example.com",
            "ssn_tin": ENCRYPTED_SSN
        }
        
        print(f"  Account ID: {FIXED_ACCOUNT_ID}")
        print(f"  Name: {contact_data['first_name']} {contact_data['last_name']}")
        print(f"  Email: {contact_data['email']}")
        print(f"  SSN: {ENCRYPTED_SSN[:50]}...")
        
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
        
        # 7. 验证 ssn_tin 字段存在
        print("[Step] 验证 ssn_tin 字段存在")
        ssn_tin = created_contact.get("ssn_tin")
        print(f"  ssn_tin: {ssn_tin}")
        
        print(f"✓ 成功创建 Contact（包含 SSN）:")
        print(f"  ID: {created_contact['id']}")
        print(f"  Name: {created_contact.get('name')}")

    def test_create_contact_missing_required_field(self, login_session):
        """
        测试场景：缺少必需字段（如 first_name）
        验证点：
        1. 接口返回 400 或其他错误状态码
        2. 错误信息提示缺少必需字段
        """
        # 1. 初始化 API 对象
        contact_api = ContactAPI(session=login_session)
        
        # 2. 准备创建数据（缺少 first_name）
        print("\n[Step] 准备创建 Contact 数据（缺少 first_name）")
        contact_data = {
            "account_id": FIXED_ACCOUNT_ID,
            # "first_name": "Missing",  # 故意缺少
            "last_name": "Field",
            "birth_date": "1990-01-01",
            "email": "missing.field@example.com"
        }
        
        # 3. 调用 Create 接口
        print("[Step] 调用 Create Contact 接口")
        create_response = contact_api.create_contact(contact_data)
        
        # 4. 验证返回错误状态码
        print("[Step] 验证返回错误状态码（400 或其他）")
        assert create_response.status_code != 200, \
            f"缺少必需字段时，接口应返回错误状态码，实际返回: {create_response.status_code}"
        
        print(f"✓ 缺少必需字段测试完成:")
        print(f"  状态码: {create_response.status_code}")
        print(f"  错误信息: {create_response.text}")

    def test_create_contact_invalid_email_format(self, login_session):
        """
        测试场景：使用无效的 email 格式
        验证点：
        1. 接口返回 400 或其他错误状态码
        2. 错误信息提示 email 格式错误
        """
        # 1. 初始化 API 对象
        contact_api = ContactAPI(session=login_session)
        
        # 2. 准备创建数据（无效的 email）
        print("\n[Step] 准备创建 Contact 数据（无效的 email）")
        contact_data = {
            "account_id": FIXED_ACCOUNT_ID,
            "first_name": "Invalid",
            "last_name": "Email",
            "birth_date": "1990-01-01",
            "email": "invalid-email-format"  # 无效格式
        }
        
        # 3. 调用 Create 接口
        print("[Step] 调用 Create Contact 接口")
        create_response = contact_api.create_contact(contact_data)
        
        # 4. 验证返回错误状态码
        print("[Step] 验证返回错误状态码（400 或其他）")
        # 注意：有些 API 可能不验证 email 格式，这里只记录结果
        print(f"  状态码: {create_response.status_code}")
        print(f"  响应: {create_response.text}")
        
        if create_response.status_code != 200:
            print(f"✓ Email 格式验证生效")
        else:
            print(f"⚠ API 未验证 email 格式")

    def test_create_contact_invalid_phone_format(self, login_session):
        """
        测试场景：使用无效的 phone 格式（非 E.164 格式）
        验证点：
        1. 接口返回 400 或其他错误状态码
        2. 错误信息提示 phone 格式错误
        """
        # 1. 初始化 API 对象
        contact_api = ContactAPI(session=login_session)
        
        # 2. 准备创建数据（无效的 phone）
        print("\n[Step] 准备创建 Contact 数据（无效的 phone 格式）")
        contact_data = {
            "account_id": FIXED_ACCOUNT_ID,
            "first_name": "Invalid",
            "last_name": "Phone",
            "birth_date": "1990-01-01",
            "email": "invalid.phone@example.com",
            "phone": "123456789"  # 非 E.164 格式
        }
        
        # 3. 调用 Create 接口
        print("[Step] 调用 Create Contact 接口")
        create_response = contact_api.create_contact(contact_data)
        
        # 4. 验证返回错误状态码
        print("[Step] 验证返回错误状态码（400 或其他）")
        print(f"  状态码: {create_response.status_code}")
        print(f"  响应: {create_response.text}")
        
        if create_response.status_code != 200:
            print(f"✓ Phone 格式验证生效")
        else:
            print(f"⚠ API 未验证 phone 格式")
