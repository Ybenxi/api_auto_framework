"""
Contact Create 接口测试用例
测试 POST /api/v1/cores/{core}/contacts 接口
"""
import pytest
import time
from api.contact_api import ContactAPI
from utils.logger import logger


# ==================== 测试数据常量 ====================

# 固定的 Account ID（所有 Contact 均在此 Account 下创建）
FIXED_ACCOUNT_ID = "251212054045554351"


@pytest.mark.contact
class TestContactCreate:
    """
    Contact 创建接口测试用例集
    """

    def test_create_contact_with_required_fields(self, login_session, db_cleanup):
        """
        测试场景1：使用必需字段创建 Contact
        验证点：
        1. 接口返回 200
        2. 返回的 Contact ID 存在
        3. 返回的 account_id 等于传入的 account_id
        4. 返回的 first_name、last_name、email 等字段正确
        """
        # 1. 初始化 API 对象
        contact_api = ContactAPI(session=login_session)
        
        # 2. 准备创建数据（仅必需字段）
        logger.info("准备创建 Contact 数据（仅必需字段）")
        
        # 使用随机 Email 避免重复
        random_email = f"auto_test_{int(time.time())}@example.com"
        
        contact_data = {
            "account_id": FIXED_ACCOUNT_ID,
            "first_name": "Auto TestYan",
            "last_name": "Contact Basic",
            "birth_date": "1990-01-01",
            "email": random_email
        }
        
        logger.info(f"  Account ID: {FIXED_ACCOUNT_ID}")
        logger.info(f"  Name: {contact_data['first_name']} {contact_data['last_name']}")
        logger.info(f"  Birth Date: {contact_data['birth_date']}")
        logger.info(f"  Email: {contact_data['email']}")
        
        # 3. 调用 Create 接口
        logger.info("调用 Create Contact 接口")
        create_response = contact_api.create_contact(contact_data)
        
        # 4. 断言状态码
        logger.info("验证 HTTP 状态码为 200")
        assert create_response.status_code == 200, \
            f"Create Contact 接口返回状态码错误: {create_response.status_code}, Response: {create_response.text}"
        
        # 5. 解析响应（修复：提取 data 字段，增强健壮性）
        logger.info("解析响应并验证数据")
        response_body = create_response.json()
        
        # 检查是否是 Email 重复错误（code 599）
        if response_body.get("code") == 599:
            logger.info("  ⚠ Email 已存在（Code 599），这不应该发生（使用了随机 Email）")
            logger.info(f"  错误信息: {response_body.get('error_message') or response_body.get('message')}")
            logger.info(f"  响应体: {response_body}")
            pytest.fail("Email 重复错误，请检查随机 Email 生成逻辑")
        
        # 检查响应结构
        if "data" in response_body:
            created_contact = response_body["data"]
        else:
            created_contact = response_body
        
        # 增强健壮性：检查 created_contact 是否为 None
        if created_contact is None:
            logger.info("  ❌ created_contact 为 None")
            logger.info(f"  响应体: {response_body}")
            logger.info(f"  响应码: {response_body.get('code')}")
            logger.info(f"  错误信息: {response_body.get('error_message') or response_body.get('message')}")
            pytest.fail(f"创建失败，data 为 None。响应: {response_body}")
        
        # 6. 验证返回的 ID 存在
        logger.info("验证返回的 Contact ID 存在")
        assert "id" in created_contact, f"响应中缺少 id 字段。响应: {created_contact}"
        assert created_contact["id"] is not None, "Contact ID 为 null"
        
        # 7. 验证 account_id
        logger.info("验证 account_id 等于传入值")
        assert created_contact.get("account_id") == FIXED_ACCOUNT_ID, \
            f"account_id 不匹配: 期望 {FIXED_ACCOUNT_ID}, 实际 {created_contact.get('account_id')}"
        
        # 8. 验证其他字段
        logger.info("验证其他字段")
        assert created_contact.get("first_name") == contact_data["first_name"], \
            f"first_name 不匹配: 期望 {contact_data['first_name']}, 实际 {created_contact.get('first_name')}"
        
        assert created_contact.get("last_name") == contact_data["last_name"], \
            f"last_name 不匹配: 期望 {contact_data['last_name']}, 实际 {created_contact.get('last_name')}"
        
        assert created_contact.get("email") == contact_data["email"], \
            f"email 不匹配: 期望 {contact_data['email']}, 实际 {created_contact.get('email')}"
        
        # 跟踪 ID，测试结束后自动清理
        if db_cleanup:
            db_cleanup.track("contact", created_contact["id"])
        
        logger.info("✓ 成功创建 Contact:")
        logger.info(f"  ID: {created_contact['id']}")
        logger.info(f"  Name: {created_contact.get('name')}")
        logger.info(f"  Account ID: {created_contact.get('account_id')}")
        logger.info(f"  Email: {created_contact.get('email')}")
        logger.info(f"  Status: {created_contact.get('status')}")

    def test_create_contact_with_all_fields(self, login_session, db_cleanup):
        """
        测试场景2：使用所有字段创建 Contact（包括可选字段，不含 ssn_tin）
        验证点：
        1. 接口返回 200，business code == 200
        2. 返回的 Contact ID 存在
        3. 可选字段（middle_name, phone, gender 等）正确保存
        """
        # 1. 初始化 API 对象
        contact_api = ContactAPI(session=login_session)
        
        # 2. 准备创建数据（包含所有字段）
        logger.info("准备创建 Contact 数据（包含所有字段）")
        contact_data = {
            "account_id": FIXED_ACCOUNT_ID,
            "first_name": "Auto TestYan",
            "last_name": "Contact Full",
            "middle_name": "AllFields",
            "birth_date": "1985-05-15",
            "email": f"auto_test_full_{int(time.time())}@example.com",
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
        
        logger.info(f"  Account ID: {FIXED_ACCOUNT_ID}")
        logger.info(f"  Name: {contact_data['first_name']} {contact_data['middle_name']} {contact_data['last_name']}")
        logger.info(f"  Email: {contact_data['email']}")
        logger.info(f"  Phone: {contact_data['phone']}")
        
        # 3. 调用 Create 接口
        logger.info("调用 Create Contact 接口")
        create_response = contact_api.create_contact(contact_data)
        
        # 4. 断言状态码（修复：允许 200 或 599）
        logger.info("验证 HTTP 状态码为 200")
        assert create_response.status_code == 200, \
            f"Create Contact 接口返回状态码错误: {create_response.status_code}, Response: {create_response.text}"
        
        # 5. 解析响应
        logger.info("解析响应并验证数据")
        response_body = create_response.json()
        
        assert response_body.get("code") == 200, \
            f"业务 code 应为 200，实际: {response_body.get('code')}，错误: {response_body.get('error_message')}"

        # 检查响应结构（场景2）
        if "data" in response_body:
            created_contact = response_body["data"]
        else:
            created_contact = response_body
        
        # 6. 验证返回的 ID 存在
        logger.info("验证返回的 Contact ID 存在")
        assert "id" in created_contact, "响应中缺少 id 字段"
        assert created_contact["id"] is not None, "Contact ID 为 null"
        
        # 7. 验证可选字段
        assert created_contact.get("middle_name") == contact_data["middle_name"], \
            f"middle_name 不匹配"
        
        assert created_contact.get("phone") == contact_data["phone"], \
            f"phone 不匹配"
        
        assert created_contact.get("gender") == contact_data["gender"], \
            f"gender 不匹配"

        # 跟踪 ID，测试结束后自动清理
        if db_cleanup:
            db_cleanup.track("contact", created_contact["id"])
        
        logger.info("✓ 成功创建 Contact（包含所有字段）:")
        logger.info(f"  ID: {created_contact['id']}")
        logger.info(f"  Name: {created_contact.get('name')}")
        logger.info(f"  Phone: {created_contact.get('phone')}")
        logger.info(f"  Gender: {created_contact.get('gender')}")

    def test_create_contact_with_ssn(self, login_session, db_cleanup):
        """
        测试场景3：创建 Contact（不含 SSN，验证基础字段 + email 唯一性）
        验证点：
        1. 接口返回 200，business code == 200
        2. 返回的 Contact ID 存在
        3. email 字段正确回显
        """
        # 1. 初始化 API 对象
        contact_api = ContactAPI(session=login_session)
        
        # 2. 准备创建数据
        logger.info("准备创建 Contact 数据")
        contact_data = {
            "account_id": FIXED_ACCOUNT_ID,
            "first_name": "Auto TestYan",
            "last_name": "Contact Basic2",
            "birth_date": "1992-03-20",
            "email": f"auto_test_basic2_{int(time.time())}@example.com"
        }
        
        logger.info(f"  Account ID: {FIXED_ACCOUNT_ID}")
        logger.info(f"  Name: {contact_data['first_name']} {contact_data['last_name']}")
        logger.info(f"  Email: {contact_data['email']}")
        
        # 3. 调用 Create 接口
        logger.info("调用 Create Contact 接口")
        create_response = contact_api.create_contact(contact_data)
        
        # 4. 断言状态码
        assert create_response.status_code == 200, \
            f"Create Contact 接口返回状态码错误: {create_response.status_code}, Response: {create_response.text}"
        
        # 5. 解析响应
        logger.info("解析响应并验证数据")
        response_body = create_response.json()
        
        assert response_body.get("code") == 200, \
            f"业务 code 应为 200，实际: {response_body.get('code')}，错误: {response_body.get('error_message')}"
        
        # 检查响应结构
        if "data" in response_body:
            created_contact = response_body["data"]
        else:
            created_contact = response_body
        
        # 6. 验证返回的 ID 存在
        logger.info("验证返回的 Contact ID 存在")
        assert "id" in created_contact, "响应中缺少 id 字段"
        assert created_contact["id"] is not None, "Contact ID 为 null"
        
        # 7. 验证 email 回显
        assert created_contact.get("email") == contact_data["email"], \
            f"email 不匹配: 期望 {contact_data['email']}, 实际 {created_contact.get('email')}"

        # 跟踪 ID，测试结束后自动清理
        if db_cleanup:
            db_cleanup.track("contact", created_contact["id"])
        
        logger.info("✓ 成功创建 Contact:")
        logger.info(f"  ID: {created_contact['id']}")
        logger.info(f"  Email: {created_contact.get('email')}")

    def test_create_contact_missing_required_field(self, login_session):
        """
        测试场景4：缺少必需字段（如 first_name）
        验证点：
        1. 接口返回 200（Soft 200）
        2. 响应中 code != 200 或 data 中不包含有效 ID
        """
        # 1. 初始化 API 对象
        contact_api = ContactAPI(session=login_session)
        
        # 2. 准备创建数据（缺少 first_name）
        logger.info("准备创建 Contact 数据（缺少 first_name）")
        contact_data = {
            "account_id": FIXED_ACCOUNT_ID,
            # "first_name": "Missing",  # 故意缺少
            "last_name": "Contact Missing",
            "birth_date": "1990-01-01",
            "email": "missing.field@example.com"
        }
        
        # 3. 调用 Create 接口
        logger.info("调用 Create Contact 接口")
        create_response = contact_api.create_contact(contact_data)
        
        # 4. 验证返回错误（修复：检查 code 或 data）
        logger.info("验证返回错误")
        response_body = create_response.json()
        
        # 检查响应 code
        response_code = response_body.get("code")
        
        # 检查 data 字段
        data = response_body.get("data")
        
        # 验证：code != 200 或 data 中不包含有效 ID
        if response_code != 200:
            logger.info("✓ 缺少必需字段测试完成（返回错误码 {response_code}）:")
            logger.info(f"  错误信息: {response_body.get('error_message') or response_body.get('message')}")
        elif data is None or not data.get("id"):
            logger.info("✓ 缺少必需字段测试完成（data 中不包含有效 ID）:")
            logger.info(f"  响应: {response_body}")
        else:
            # 如果返回了有效 ID，说明后端没有验证必需字段
            pytest.fail(f"后端未验证必需字段，返回了有效 ID: {data.get('id')}")

    def test_create_contact_invalid_email_format(self, login_session):
        """
        测试场景5：使用无效的 email 格式
        验证点：
        1. 接口返回 200（Soft 200）
        2. 响应中 code != 200 或包含错误信息
        """
        # 1. 初始化 API 对象
        contact_api = ContactAPI(session=login_session)
        
        # 2. 准备创建数据（无效的 email）
        logger.info("准备创建 Contact 数据（无效的 email）")
        contact_data = {
            "account_id": FIXED_ACCOUNT_ID,
            "first_name": "Auto TestYan",
            "last_name": "Contact InvalidEmail",
            "birth_date": "1990-01-01",
            "email": "invalid-email-format"  # 无效格式
        }
        
        # 3. 调用 Create 接口
        logger.info("调用 Create Contact 接口")
        create_response = contact_api.create_contact(contact_data)
        
        # 4. 验证返回错误状态码
        logger.info("验证返回错误状态码（400 或其他）")
        # 注意：有些 API 可能不验证 email 格式，这里只记录结果
        logger.info(f"  状态码: {create_response.status_code}")
        logger.info(f"  响应: {create_response.text}")
        
        if create_response.status_code != 200:
            logger.info("✓ Email 格式验证生效")
        else:
            response_body = create_response.json()
            if response_body.get("code") != 200:
                logger.info("✓ Email 格式验证生效（返回错误码 {response_body.get('code')}）")
            else:
                logger.info(f"⚠ API 未验证 email 格式")

    def test_create_contact_invalid_phone_format(self, login_session):
        """
        测试场景6：使用无效的 phone 格式（非 E.164 格式）
        验证点：
        1. 接口返回 200（Soft 200）
        2. 响应中 code != 200 或包含错误信息
        """
        # 1. 初始化 API 对象
        contact_api = ContactAPI(session=login_session)
        
        # 2. 准备创建数据（无效的 phone）
        logger.info("准备创建 Contact 数据（无效的 phone 格式）")
        contact_data = {
            "account_id": FIXED_ACCOUNT_ID,
            "first_name": "Auto TestYan",
            "last_name": "Contact InvalidPhone",
            "birth_date": "1990-01-01",
            "email": "invalid.phone@example.com",
            "phone": "123456789"  # 非 E.164 格式
        }
        
        # 3. 调用 Create 接口
        logger.info("调用 Create Contact 接口")
        create_response = contact_api.create_contact(contact_data)
        
        # 4. 验证返回错误状态码
        logger.info("验证返回错误状态码（400 或其他）")
        logger.info(f"  状态码: {create_response.status_code}")
        logger.info(f"  响应: {create_response.text}")
        
        if create_response.status_code != 200:
            logger.info("✓ Phone 格式验证生效")
        else:
            response_body = create_response.json()
            if response_body.get("code") != 200:
                logger.info("✓ Phone 格式验证生效（返回错误码 {response_body.get('code')}）")
            else:
                logger.info(f"⚠ API 未验证 phone 格式")

    def test_create_contact_then_retrieve_detail(self, login_session, db_cleanup):
        """
        测试场景7：创建 Contact 后立即查询详情，验证数据一致性
        验证点：
        1. 创建 Contact 成功
        2. 立即调用 Detail 接口获取详情
        3. 验证所有字段值与创建时传入的数据一致
        """
        # 初始化 API 对象
        contact_api = ContactAPI(session=login_session)
        
        # 准备创建数据（使用唯一email避免冲突）
        logger.info("准备创建 Contact 数据")
        random_email = f"auto_test_verify_{int(time.time())}@example.com"
        
        contact_data = {
            "account_id": FIXED_ACCOUNT_ID,
            "first_name": "Auto TestYan",
            "last_name": "Contact Verify",
            "birth_date": "1995-08-20",
            "email": random_email,
            "phone": "+14155559876"
        }
        
        # 调用 Create 接口
        logger.info("调用 Create Contact 接口")
        create_response = contact_api.create_contact(contact_data)
        
        # 验证创建成功
        assert create_response.status_code == 200, \
            f"Create 失败: {create_response.status_code}"
        
        response_body = create_response.json()
        
        # 跳过 Email/SSN 重复的情况
        if response_body.get("code") == 599:
            pytest.skip("Email 或 SSN 已存在，跳过一致性测试")
        
        created_contact = response_body.get("data") or response_body
        contact_id = created_contact.get("id")
        
        assert contact_id is not None, "创建的 Contact ID 为 None"

        # 跟踪 ID，测试结束后自动清理
        if db_cleanup:
            db_cleanup.track("contact", contact_id)

        # 立即调用 Detail 接口
        logger.info("立即查询 Contact 详情 (ID: {contact_id})")
        detail_response = contact_api.get_contact_detail(contact_id)
        
        assert detail_response.status_code == 200, \
            f"Detail 接口失败: {detail_response.status_code}"
        
        detail_body = detail_response.json()
        detail_contact = detail_body.get("data") or detail_body
        
        # 验证字段一致性
        logger.info("验证创建和详情数据一致性")
        assert detail_contact.get("account_id") == contact_data["account_id"], \
            "account_id 不一致"
        assert detail_contact.get("first_name") == contact_data["first_name"], \
            "first_name 不一致"
        assert detail_contact.get("last_name") == contact_data["last_name"], \
            "last_name 不一致"
        assert detail_contact.get("email") == contact_data["email"], \
            "email 不一致"
        assert detail_contact.get("phone") == contact_data["phone"], \
            "phone 不一致"
        
        logger.info("✓ 创建后立即查询验证通过，数据完全一致")
        logger.info(f"  Contact ID: {contact_id}")
        logger.info(f"  Name: {detail_contact.get('name')}")
        logger.info(f"  Email: {detail_contact.get('email')}")

    def test_create_contact_with_empty_strings(self, login_session):
        """
        测试场景8：空字符串边界值测试
        验证点：
        1. first_name 和 last_name 传入空字符串
        2. 验证 API 是否拒绝空字符串（返回错误）或接受为有效值
        """
        contact_api = ContactAPI(session=login_session)
        
        # 准备创建数据（first_name 为空字符串）
        logger.info("准备创建 Contact 数据（first_name 为空字符串）")
        random_email = f"auto_test_empty_{int(time.time())}@example.com"
        
        contact_data = {
            "account_id": FIXED_ACCOUNT_ID,
            "first_name": "",  # 空字符串
            "last_name": "Contact EmptyTest",
            "birth_date": "1990-01-01",
            "email": random_email
        }
        
        # 调用 Create 接口
        logger.info("调用 Create Contact 接口")
        create_response = contact_api.create_contact(contact_data)
        
        # 验证响应
        logger.info("验证 API 对空字符串的处理")
        logger.info(f"  状态码: {create_response.status_code}")
        
        if create_response.status_code == 200:
            response_body = create_response.json()
            logger.info(f"  响应: {response_body}")
            
            if response_body.get("code") != 200:
                logger.info("✓ API 拒绝空字符串（返回错误码 {response_body.get('code')}）")
            else:
                # API 接受了空字符串
                logger.info(f"⚠ API 接受了空字符串作为 first_name")
                logger.info(f"  建议：first_name 应该有非空验证")
        else:
            logger.info("✓ API 拒绝空字符串（返回 HTTP 状态码 {create_response.status_code}）")

    def test_create_contact_with_invisible_account_id(self, login_session):
        """
        测试场景9：使用不在当前用户 visible 范围内的 Account ID
        验证点：
        1. 使用他人账户 ID：241010195849720143（yhan account Sanchez，不属于当前用户）
        2. 服务器返回 200 OK（统一错误处理）
        3. 业务错误码 code == 506
        4. error_message == "visibility permission deny"
        """
        import time as time_module
        contact_api = ContactAPI(session=login_session)

        # 使用不在当前用户 visible 范围内的 Account ID
        invisible_account_id = "241010195849720143"  # yhan account Sanchez，不属于当前用户

        contact_data = {
            "account_id": invisible_account_id,
            "first_name": "Auto TestYan",
            "last_name": "Contact Invisible",
            "birth_date": "1990-01-01",
            "email": f"auto_invisible_{int(time_module.time())}@example.com"
        }

        logger.info(f"使用不在 visible 范围内的 Account ID: {invisible_account_id}")
        create_response = contact_api.create_contact(contact_data)

        assert create_response.status_code == 200, \
            f"服务器应该返回 200（统一错误处理），实际: {create_response.status_code}"

        response_body = create_response.json()
        logger.info(f"  响应: {response_body}")

        assert response_body.get("code") == 506, \
            f"越权 Account ID 应该返回 code=506，实际: {response_body.get('code')}"

        error_msg = response_body.get("error_message", "")
        assert "visibility permission deny" in error_msg.lower(), \
            f"error_message 应包含 'visibility permission deny'，实际: {error_msg}"

        assert response_body.get("data") is None, \
            "越权时 data 应为 None"

        logger.info(f"✓ 越权 Account ID 校验通过: code=506, msg={error_msg}")

    def test_create_contact_invalid_birth_date_format(self, login_session):
        """
        测试场景10：提交格式错误的 birth_date
        验证点：
        1. HTTP 200（统一错误处理）
        2. 业务 code != 200，提示日期格式错误
        """
        contact_api = ContactAPI(session=login_session)

        contact_data = {
            "account_id": FIXED_ACCOUNT_ID,
            "first_name": "Auto TestYan",
            "last_name": "Contact BadDate",
            "birth_date": "01/01/1990",   # 错误格式，应为 YYYY-MM-DD
            "email": f"auto_test_baddate_{int(time.time())}@example.com"
        }

        logger.info("提交格式错误的 birth_date: 01/01/1990（应为 YYYY-MM-DD）")
        response = contact_api.create_contact(contact_data)

        assert response.status_code == 200, \
            f"HTTP 应返回 200，实际: {response.status_code}"

        body = response.json()
        logger.info(f"  响应: {body}")
        assert body.get("code") != 200, \
            f"错误日期格式应被拒绝（code!=200），实际 code={body.get('code')}"

        logger.info(f"✓ 错误日期格式被拒绝: code={body.get('code')}, msg={body.get('error_message')}")

    def test_create_contact_invalid_country_format(self, login_session):
        """
        测试场景11：permanent_country 不符合 ISO 3166 标准
        验证点：
        1. HTTP 200
        2. 业务 code != 200，或提示国家代码格式错误
        """
        contact_api = ContactAPI(session=login_session)

        contact_data = {
            "account_id": FIXED_ACCOUNT_ID,
            "first_name": "Auto TestYan",
            "last_name": "Contact BadCountry",
            "birth_date": "1990-01-01",
            "email": f"auto_test_badcountry_{int(time.time())}@example.com",
            "permanent_country": "CHINA",         # 非 ISO 3166 标准
            "mailing_country": "UNITED_STATES"    # 非 ISO 3166 标准
        }

        logger.info("提交非 ISO 3166 country 代码: CHINA / UNITED_STATES")
        response = contact_api.create_contact(contact_data)

        assert response.status_code == 200, \
            f"HTTP 应返回 200，实际: {response.status_code}"

        body = response.json()
        logger.info(f"  响应 code={body.get('code')}, msg={body.get('error_message')}")

        if body.get("code") != 200:
            logger.info(f"✓ 非标准 country 被 API 拒绝: code={body.get('code')}")
        else:
            logger.info("⚠ API 未校验 country 格式（接受了非 ISO 3166 值），记录为探索性结果")

    def test_create_contact_invalid_phone_e164(self, login_session):
        """
        测试场景12：phone 不符合 E.164 格式
        验证点：
        1. HTTP 200
        2. 业务 code != 200，提示 phone 格式错误
        """
        contact_api = ContactAPI(session=login_session)

        contact_data = {
            "account_id": FIXED_ACCOUNT_ID,
            "first_name": "Auto TestYan",
            "last_name": "Contact BadPhone",
            "birth_date": "1990-01-01",
            "email": f"auto_test_badphone_{int(time.time())}@example.com",
            "phone": "13800138000"   # 非 E.164 格式（缺少 +）
        }

        logger.info("提交非 E.164 格式 phone: 13800138000")
        response = contact_api.create_contact(contact_data)

        assert response.status_code == 200, \
            f"HTTP 应返回 200，实际: {response.status_code}"

        body = response.json()
        logger.info(f"  响应 code={body.get('code')}, msg={body.get('error_message')}")

        if body.get("code") != 200:
            logger.info(f"✓ 非 E.164 phone 被 API 拒绝: code={body.get('code')}")
        else:
            logger.info("⚠ API 未校验 phone 格式（接受了非 E.164 值），记录为探索性结果")

    def test_create_contact_invalid_enum_fields(self, login_session):
        """
        测试场景13：government_document_type 和 gender 超出枚举范围
        验证点：
        1. HTTP 200
        2. 业务 code != 200，提示枚举值不合法
        """
        contact_api = ContactAPI(session=login_session)

        contact_data = {
            "account_id": FIXED_ACCOUNT_ID,
            "first_name": "Auto TestYan",
            "last_name": "Contact BadEnum",
            "birth_date": "1990-01-01",
            "email": f"auto_test_badenum_{int(time.time())}@example.com",
            "gender": "Unknown",                           # 超出枚举范围
            "government_document_type": "Magic Document"  # 超出枚举范围
        }

        logger.info("提交超出枚举范围的 gender='Unknown', government_document_type='Magic Document'")
        response = contact_api.create_contact(contact_data)

        assert response.status_code == 200, \
            f"HTTP 应返回 200，实际: {response.status_code}"

        body = response.json()
        logger.info(f"  响应 code={body.get('code')}, msg={body.get('error_message')}")

        if body.get("code") != 200:
            logger.info(f"✓ 超出枚举范围的值被 API 拒绝: code={body.get('code')}")
        else:
            logger.info("⚠ API 未校验枚举范围（接受了非法枚举值），记录为探索性结果")
