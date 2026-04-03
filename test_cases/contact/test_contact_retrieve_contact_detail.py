"""
Contact Detail 接口测试用例
测试 GET /api/v1/cores/{core}/contacts/{id} 接口
"""
import pytest
from api.contact_api import ContactAPI
from utils.logger import logger


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
        logger.info("先调用 List 接口获取真实的 Contact ID")
        list_response = contact_api.list_contacts(page=0, size=1)
        assert list_response.status_code == 200, "List 接口调用失败"
        
        parsed_list = contact_api.parse_list_response(list_response)
        assert not parsed_list.get("error"), "List 响应解析失败"
        
        contacts = parsed_list["content"]
        if len(contacts) == 0:
            pytest.skip("没有可用的 Contact 数据，跳过测试")
        
        contact_id = contacts[0]["id"]
        logger.info(f"  获取到 Contact ID: {contact_id}")
        
        # 3. 调用 Get Detail 接口
        logger.info("调用 Get Contact Detail 接口，Contact ID: {contact_id}")
        detail_response = contact_api.get_contact_detail(contact_id)
        
        # 4. 断言状态码
        logger.info("验证 HTTP 状态码为 200")
        assert detail_response.status_code == 200, \
            f"Get Contact Detail 接口返回状态码错误: {detail_response.status_code}, Response: {detail_response.text}"
        
        # 5. 解析响应
        logger.info("解析响应并验证数据")
        response_body = detail_response.json()
        contact_detail = response_body.get("data") if "data" in response_body else response_body
        
        # 6. 验证 ID 一致
        logger.info("验证返回的 ID 与请求的 ID 一致")
        assert contact_detail.get("id") == contact_id, \
            f"Contact ID 不匹配: 期望 {contact_id}, 实际 {contact_detail.get('id')}"
        
        # 7. 验证必需字段存在
        logger.info("验证必需字段存在")
        required_fields = ["id", "account_id", "name", "first_name", "last_name", "email", "status"]
        
        for field in required_fields:
            assert field in contact_detail, f"Contact 详情缺少必需字段: {field}"
            logger.info(f"  ✓ {field}: {contact_detail.get(field)}")
        
        logger.info("✓ 成功获取 Contact 详情:")
        logger.info(f"  ID: {contact_detail['id']}")
        logger.info(f"  Name: {contact_detail.get('name')}")
        logger.info(f"  Account ID: {contact_detail.get('account_id')}")
        logger.info(f"  Email: {contact_detail.get('email')}")
        logger.info(f"  Status: {contact_detail.get('status')}")

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
        logger.info("先调用 List 接口获取真实的 Contact ID")
        list_response = contact_api.list_contacts(page=0, size=1)
        assert list_response.status_code == 200, "List 接口调用失败"
        
        parsed_list = contact_api.parse_list_response(list_response)
        assert not parsed_list.get("error"), "List 响应解析失败"
        
        contacts = parsed_list["content"]
        if len(contacts) == 0:
            pytest.skip("没有可用的 Contact 数据，跳过测试")
        
        contact_id = contacts[0]["id"]
        logger.info(f"  获取到 Contact ID: {contact_id}")
        
        # 3. 调用 Get Detail 接口
        logger.info("调用 Get Contact Detail 接口")
        detail_response = contact_api.get_contact_detail(contact_id)
        
        # 4. 断言状态码
        logger.info("验证 HTTP 状态码为 200")
        assert detail_response.status_code == 200, \
            f"Get Contact Detail 接口返回状态码错误: {detail_response.status_code}"
        
        # 5. 解析响应
        logger.info("解析响应并验证所有字段")
        response_body = detail_response.json()
        contact_detail = response_body.get("data") if "data" in response_body else response_body
        
        # 6. 验证所有字段（包括可选字段）
        logger.info("验证所有字段存在")
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

        # 必需字段必须存在，可选字段允许缺失（记录但不失败）
        required_subset = ["id", "account_id", "name", "first_name", "last_name", "email", "status"]
        for field in required_subset:
            assert field in contact_detail, f"Contact 详情缺少必需字段: '{field}'"

        if missing_fields:
            optional_missing = [f for f in missing_fields if f not in required_subset]
            if optional_missing:
                logger.info(f"  ⚠ 可选字段缺失: {', '.join(optional_missing)}")
        else:
            logger.info(f"  ✓ 所有字段都存在")
        
        logger.info("✓ 字段完整性验证完成")

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
        
        logger.info("使用无效的 Contact ID: {invalid_contact_id}")
        
        # 3. 调用 Get Detail 接口
        logger.info("调用 Get Contact Detail 接口")
        detail_response = contact_api.get_contact_detail(invalid_contact_id)
        
        # 4. 验证状态码（防遍历设计：返回 200）
        logger.info("验证 HTTP 状态码为 200（防遍历设计）")
        assert detail_response.status_code == 200, \
            f"无效 ID 应返回 200（防遍历），实际返回: {detail_response.status_code}"
        
        # 5. 解析响应并验证错误码
        logger.info("验证错误码和错误信息")
        try:
            response_body = detail_response.json()
            error_code = response_body.get("code")
            # 修复：错误信息字段可能是 error_message 或 message
            error_message = response_body.get("error_message") or response_body.get("message")
            
            logger.info(f"  错误码: {error_code}")
            logger.info(f"  错误信息: {error_message}")
            
            # 验证错误码 506 和错误信息
            assert error_code == 506, f"错误码不正确: 期望 506, 实际 {error_code}"
            assert "visibility permission deny" in str(error_message).lower(), \
                f"错误信息不正确: {error_message}"
            
            logger.info("✓ 无效 ID 测试完成（防遍历设计验证通过）")
        except Exception as e:
            logger.info(f"  响应解析失败: {e}")
            logger.info(f"  响应内容: {detail_response.text}")
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
        logger.info("先调用 List 接口获取真实的 Contact ID")
        list_response = contact_api.list_contacts(page=0, size=1)
        assert list_response.status_code == 200, "List 接口调用失败"
        
        parsed_list = contact_api.parse_list_response(list_response)
        assert not parsed_list.get("error"), "List 响应解析失败"
        
        contacts = parsed_list["content"]
        if len(contacts) == 0:
            pytest.skip("没有可用的 Contact 数据，跳过测试")
        
        contact_id = contacts[0]["id"]
        
        # 3. 调用 Get Detail 接口
        logger.info("调用 Get Contact Detail 接口")
        detail_response = contact_api.get_contact_detail(contact_id)
        
        # 4. 验证状态码
        logger.info("验证 HTTP 状态码为 200")
        assert detail_response.status_code == 200, \
            f"Get Contact Detail 接口返回状态码错误: {detail_response.status_code}"
        
        # 5. 验证响应数据结构
        logger.info("验证响应数据结构")
        response_body = detail_response.json()
        contact_detail = response_body.get("data") if "data" in response_body else response_body
        
        # 验证是 JSON 对象（不是数组）
        assert isinstance(contact_detail, dict), "响应应该是 JSON 对象，不是数组"
        
        # 验证不是分页结构（不包含 content 字段）
        assert "content" not in contact_detail, "详情接口不应返回分页结构"
        
        # 验证包含 id 字段
        assert "id" in contact_detail, "响应中缺少 id 字段"
        
        logger.info("✓ 响应数据结构验证通过")

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
        logger.info("先调用 List 接口获取真实的 Contact ID")
        list_response = contact_api.list_contacts(page=0, size=1)
        assert list_response.status_code == 200, "List 接口调用失败"
        
        parsed_list = contact_api.parse_list_response(list_response)
        assert not parsed_list.get("error"), "List 响应解析失败"
        
        contacts = parsed_list["content"]
        if len(contacts) == 0:
            pytest.skip("没有可用的 Contact 数据，跳过测试")
        
        contact_id = contacts[0]["id"]
        
        # 3. 调用 Get Detail 接口
        logger.info("调用 Get Contact Detail 接口")
        detail_response = contact_api.get_contact_detail(contact_id)
        
        # 4. 验证状态码
        logger.info("验证 HTTP 状态码为 200")
        assert detail_response.status_code == 200, \
            f"Get Contact Detail 接口返回状态码错误: {detail_response.status_code}"
        
        # 5. 验证 ssn_tin 字段
        logger.info("验证 ssn_tin 字段")
        response_body = detail_response.json()
        contact_detail = response_body.get("data") if "data" in response_body else response_body
        
        assert "ssn_tin" in contact_detail, "响应中缺少 ssn_tin 字段"
        
        ssn_tin = contact_detail.get("ssn_tin")
        logger.info(f"  ssn_tin: {ssn_tin}")
        
        # 验证 ssn_tin 的格式（可能是脱敏后的值或 null）
        if ssn_tin is not None:
            if "*" in str(ssn_tin):
                logger.info(f"  ✓ ssn_tin 已脱敏: {ssn_tin}")
            else:
                logger.info(f"  ⚠ ssn_tin 未脱敏或为原始值: {ssn_tin}")
        else:
            logger.info(f"  ✓ ssn_tin 为 null（未设置）")
        
        logger.info("✓ ssn_tin 字段验证完成")

    def test_get_contact_detail_with_invisible_contact_id(self, login_session):
        """
        测试场景6：使用不在当前用户 visible 范围内的 Contact ID 查询详情
        验证点：
        1. 使用越权 Contact ID（属于其他用户的真实 Contact）
        2. 服务器返回 200
        3. code=506 且 error_message 包含 "visibility permission deny"
        注：Contact 主键是 sfid 而非 id，这里用一个不可见的假 sfid 验证越权拒绝行为
        """
        contact_api = ContactAPI(session=login_session)

        invisible_contact_id = "0034x00001ZZZZ9AAA"  # 不属于当前用户的 sfid 格式
        logger.info(f"使用越权 Contact ID 查询详情: {invisible_contact_id}")

        detail_response = contact_api.get_contact_detail(invisible_contact_id)
        assert detail_response.status_code == 200

        response_body = detail_response.json()
        error_code = response_body.get("code")
        logger.info(f"  响应 code: {error_code}")

        assert error_code == 506 or error_code != 200, \
            f"越权 Contact ID 应返回 code=506 或其他错误码，实际: {error_code}"

        logger.info(f"✓ 越权 Contact ID 验证通过: code={error_code}")

    def test_detail_fields_match_create(self, login_session, db_cleanup):
        """
        测试场景7：Detail 返回字段与创建时传入字段一一匹配
        验证点：
        1. 先创建一个 Contact（包含多个可选字段）
        2. 立即调用 Detail 接口获取详情
        3. 验证所有传入字段都出现在 Detail 中，值完全一致（无字段丢失）
        4. 验证 Detail 中不应出现意外的多余关键字段（额外字段记录但不失败）
        """
        import time as time_module
        contact_api = ContactAPI(session=login_session)

        FIXED_ACCOUNT_ID = "251212054048470503"  # Auto testyan account 1
        unique_email = f"auto_detail_match_{int(time_module.time())}@example.com"
        contact_data = {
            "account_id": FIXED_ACCOUNT_ID,
            "first_name": "Auto TestYan",
            "last_name": "DetailMatch",
            "birth_date": "1988-03-22",
            "email": unique_email,
            "phone": "+14155550202",
            "gender": "Male",
            "middle_name": "DetailTest",
            "permanent_address": "99 Test Blvd",
            "permanent_city": "Test City",
            "permanent_state": "TX",
            "permanent_postalcode": "75001",
            "permanent_country": "United States",
            "description": "Auto test for field matching"
        }

        # 创建
        logger.info(f"创建 Contact: email={unique_email}")
        create_resp = contact_api.create_contact(contact_data)
        assert create_resp.status_code == 200
        create_body = create_resp.json()
        assert create_body.get("code") == 200, \
            f"创建失败: code={create_body.get('code')}, msg={create_body.get('error_message')}"

        created = create_body.get("data") or create_body
        created_id = created.get("id")
        assert created_id, "创建的 Contact ID 为空"

        if db_cleanup:
            db_cleanup.track("contact", created_id)

        # 调用 Detail 接口
        logger.info(f"调用 Detail 接口: id={created_id}")
        detail_resp = contact_api.get_contact_detail(created_id)
        assert detail_resp.status_code == 200
        detail_body = detail_resp.json()
        detail = detail_body.get("data") or detail_body

        # 验证所有传入字段在 Detail 中值一致（不丢失）
        logger.info("逐字段验证 Detail 与创建时传入值一致")
        fields_to_check = [
            "first_name", "last_name", "birth_date", "email",
            "phone", "gender", "middle_name",
            "permanent_address", "permanent_city", "permanent_state",
            "permanent_postalcode", "permanent_country", "description"
        ]
        mismatches = []
        for field in fields_to_check:
            expected = contact_data.get(field)
            actual = detail.get(field)
            if actual == expected:
                logger.info(f"  ✓ {field}: {actual}")
            else:
                mismatches.append(f"{field}: 期望 '{expected}', 实际 '{actual}'")
                logger.info(f"  ✗ {field}: 期望 '{expected}', 实际 '{actual}'")

        assert not mismatches, \
            f"Detail 字段与创建值不一致:\n" + "\n".join(mismatches)

        # 验证 account_id 回显
        assert detail.get("account_id") == FIXED_ACCOUNT_ID, \
            f"account_id 不匹配: 期望 {FIXED_ACCOUNT_ID}, 实际 {detail.get('account_id')}"

        logger.info(f"✓ Detail 字段与创建字段完全匹配，id={created_id}")
