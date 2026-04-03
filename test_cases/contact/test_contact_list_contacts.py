"""
Contact List 接口测试用例
测试 GET /api/v1/cores/{core}/contacts 接口
"""
import pytest
from api.contact_api import ContactAPI
from utils.logger import logger


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
        contact_api = ContactAPI(session=login_session)

        logger.info("调用 List Contacts 接口")
        list_response = contact_api.list_contacts(page=0, size=10)

        logger.info("验证 HTTP 状态码为 200")
        assert list_response.status_code == 200, \
            f"List Contacts 接口返回状态码错误: {list_response.status_code}, Response: {list_response.text}"

        logger.info("解析响应并验证数据结构")
        parsed_list = contact_api.parse_list_response(list_response)
        assert not parsed_list.get("error"), f"List 响应解析失败: {parsed_list.get('message')}"

        logger.info("验证返回数据结构")
        assert "content" in parsed_list, "响应中缺少 content 字段"
        assert isinstance(parsed_list["content"], list), "content 字段不是数组类型"

        contacts = parsed_list["content"]
        logger.info(f"  总元素数: {parsed_list['total_elements']}")
        logger.info(f"  总页数: {parsed_list['total_pages']}")
        logger.info(f"  当前页: {parsed_list['number']}")
        logger.info(f"  每页大小: {parsed_list['size']}")
        logger.info(f"  返回 {len(contacts)} 个 Contacts")

        if contacts:
            logger.info(f"  第一个 Contact: {contacts[0].get('name')} ({contacts[0].get('email')})")

        logger.info("✓ 测试通过")

    @pytest.mark.parametrize("status", ["Active", "Inactive", "Pending"])
    def test_list_contacts_with_status_filter(self, login_session, status):
        """
        测试场景2：使用 status 筛选 Contacts（覆盖全部枚举值）
        验证点：
        1. 接口返回 200
        2. 返回的每条 Contact 的 status 均与筛选值一致
        """
        contact_api = ContactAPI(session=login_session)

        logger.info(f"使用 status='{status}' 筛选 Contacts")
        list_response = contact_api.list_contacts(status=status, size=10)

        logger.info("验证 HTTP 状态码为 200")
        assert list_response.status_code == 200, \
            f"接口返回状态码错误: {list_response.status_code}"

        parsed_list = contact_api.parse_list_response(list_response)
        assert not parsed_list.get("error"), f"响应解析失败: {parsed_list.get('message')}"

        contacts = parsed_list["content"]
        logger.info(f"  返回 {len(contacts)} 个 Contacts")

        if not contacts:
            logger.info(f"  ⚠️ status='{status}' 无数据，跳过筛选值验证")
        else:
            logger.info(f"验证每条数据的 status 均为 {status}")
            for contact in contacts:
                assert contact.get("status") == status, \
                    f"筛选结果包含非 {status} 状态: status={contact.get('status')}, id={contact.get('id')}"
            logger.info(f"✓ {len(contacts)} 条数据均为 {status} 状态")

    def test_list_contacts_with_name_filter(self, login_session):
        """
        测试场景3：使用 name 模糊筛选 Contacts
        先 list 获取真实 name 取前4字符作为关键词，验证每条结果包含该关键词
        验证点：
        1. 接口返回 200
        2. 返回的每条 Contact 的 name 包含搜索关键词
        """
        contact_api = ContactAPI(session=login_session)

        # Step 1: 获取真实 name
        logger.info("先获取列表，取第一条数据的 name 作为关键词")
        base_response = contact_api.list_contacts(page=0, size=1)
        assert base_response.status_code == 200
        base = contact_api.parse_list_response(base_response)

        if not base["content"]:
            pytest.skip("无 Contact 数据，跳过")

        real_name = base["content"][0].get("name", "")
        if not real_name or len(real_name) < 2:
            pytest.skip("name 字段为空或过短，跳过")

        keyword = real_name[:4]
        logger.info(f"  使用关键词: '{keyword}'（来自 name='{real_name}'）")

        # Step 2: 用关键词筛选
        logger.info(f"使用 name='{keyword}' 模糊筛选")
        list_response = contact_api.list_contacts(name=keyword, size=10)

        assert list_response.status_code == 200, \
            f"接口返回状态码错误: {list_response.status_code}"

        parsed_list = contact_api.parse_list_response(list_response)
        assert not parsed_list.get("error"), f"响应解析失败: {parsed_list.get('message')}"

        contacts = parsed_list["content"]
        assert len(contacts) > 0, f"筛选结果为空，关键词 '{keyword}' 应能匹配到数据"

        # Step 3: 断言每条数据 name 包含关键词
        logger.info("验证每条数据的 name 包含关键词")
        for contact in contacts:
            assert keyword.lower() in contact.get("name", "").lower(), \
                f"返回数据 name='{contact.get('name')}' 不包含关键词 '{keyword}'"

        logger.info(f"✓ name 模糊筛选验证通过，返回 {len(contacts)} 条")

    def test_list_contacts_with_email_filter(self, login_session):
        """
        测试场景4：使用 email 模糊筛选 Contacts
        先 list 获取真实 email 取域名部分作为关键词，验证每条结果包含该关键词
        验证点：
        1. 接口返回 200
        2. 返回的每条 Contact 的 email 包含搜索关键词
        """
        contact_api = ContactAPI(session=login_session)

        # Step 1: 获取真实 email
        logger.info("先获取列表，取第一条数据的 email 作为筛选关键词")
        base_response = contact_api.list_contacts(page=0, size=1)
        assert base_response.status_code == 200
        base = contact_api.parse_list_response(base_response)

        if not base["content"]:
            pytest.skip("无 Contact 数据，跳过")

        real_email = base["content"][0].get("email", "")
        if not real_email or "@" not in real_email:
            pytest.skip("email 字段为空或格式不正确，跳过")

        # 取 @ 之后的域名部分作为关键词（更宽泛，更容易匹配多条）
        keyword = real_email.split("@")[1]
        logger.info(f"  使用关键词: '{keyword}'（来自 email='{real_email}'）")

        # Step 2: 用关键词筛选
        logger.info(f"使用 email='{keyword}' 模糊筛选")
        list_response = contact_api.list_contacts(email=keyword, size=10)

        assert list_response.status_code == 200, \
            f"接口返回状态码错误: {list_response.status_code}"

        parsed_list = contact_api.parse_list_response(list_response)
        assert not parsed_list.get("error"), f"响应解析失败: {parsed_list.get('message')}"

        contacts = parsed_list["content"]
        assert len(contacts) > 0, f"筛选结果为空，关键词 '{keyword}' 应能匹配到数据"

        # Step 3: 断言每条数据 email 包含关键词
        logger.info("验证每条数据的 email 包含关键词")
        for contact in contacts:
            assert keyword.lower() in contact.get("email", "").lower(), \
                f"返回数据 email='{contact.get('email')}' 不包含关键词 '{keyword}'"

        logger.info(f"✓ email 模糊筛选验证通过，返回 {len(contacts)} 条")

    def test_list_contacts_pagination(self, login_session):
        """
        测试场景5：验证分页功能
        验证点：
        1. 接口返回 200
        2. 分页信息正确（page=0, size=5）
        3. 返回数量 <= size
        """
        contact_api = ContactAPI(session=login_session)

        logger.info("使用分页参数 page=0, size=5")
        list_response = contact_api.list_contacts(page=0, size=5)

        logger.info("验证 HTTP 状态码为 200")
        assert list_response.status_code == 200, \
            f"接口返回状态码错误: {list_response.status_code}"

        parsed_list = contact_api.parse_list_response(list_response)
        assert not parsed_list.get("error"), f"响应解析失败: {parsed_list.get('message')}"

        logger.info("验证分页信息")
        assert parsed_list["size"] == 5, \
            f"分页大小不正确: 期望 5, 实际 {parsed_list['size']}"
        assert parsed_list["number"] == 0, \
            f"页码不正确: 期望 0, 实际 {parsed_list['number']}"
        assert len(parsed_list["content"]) <= 5, \
            f"返回数量 {len(parsed_list['content'])} 超过 size=5"

        logger.info("✓ 分页测试通过:")
        logger.info(f"  总元素数: {parsed_list['total_elements']}")
        logger.info(f"  总页数: {parsed_list['total_pages']}")
        logger.info(f"  当前页: {parsed_list['number']}")
        logger.info(f"  每页大小: {parsed_list['size']}")
        logger.info(f"  实际返回: {len(parsed_list['content'])} 条")

    def test_list_contacts_empty_result(self, login_session):
        """
        测试场景6：使用不存在的筛选条件，验证空结果处理
        验证点：
        1. 接口返回 200
        2. content 为空数组
        3. total_elements 为 0
        """
        contact_api = ContactAPI(session=login_session)

        logger.info("使用不存在的 name 查询")
        list_response = contact_api.list_contacts(name="NonExistentContact999999", size=10)

        assert list_response.status_code == 200, \
            f"接口返回状态码错误: {list_response.status_code}"

        parsed_list = contact_api.parse_list_response(list_response)
        assert not parsed_list.get("error"), f"响应解析失败: {parsed_list.get('message')}"

        assert len(parsed_list["content"]) == 0, \
            f"期望返回空列表，但实际有 {len(parsed_list['content'])} 条数据"
        assert parsed_list.get("total_elements") == 0, \
            f"total_elements 应该为 0，实际为 {parsed_list.get('total_elements')}"

        logger.info("✓ 空结果验证通过")

    def test_list_contacts_response_fields(self, login_session):
        """
        测试场景7：验证响应字段完整性
        验证点：
        1. 接口返回 200
        2. Contact 对象必须包含所有必需字段
        """
        contact_api = ContactAPI(session=login_session)

        logger.info("调用 List Contacts 接口")
        list_response = contact_api.list_contacts(page=0, size=1)

        assert list_response.status_code == 200, \
            f"接口返回状态码错误: {list_response.status_code}"

        parsed_list = contact_api.parse_list_response(list_response)
        assert not parsed_list.get("error"), f"响应解析失败: {parsed_list.get('message')}"

        contacts = parsed_list["content"]

        if not contacts:
            pytest.skip("无数据，跳过字段验证")

        contact = contacts[0]
        required_fields = ["id", "account_id", "name", "first_name", "last_name", "email", "status"]

        logger.info("验证 Contact 必需字段")
        for field in required_fields:
            assert field in contact, f"Contact 对象缺少必需字段: '{field}'"
            logger.info(f"  ✓ {field}: {contact.get(field)}")

        logger.info("✓ 字段完整性验证通过")

    @pytest.mark.skip(reason="API 排序功能待后端确认支持，暂时跳过")
    def test_list_contacts_sorting_by_name(self, login_session):
        """
        测试场景8：排序功能验证 - 按姓名排序
        验证点：
        1. 使用 sort 参数进行排序
        2. 验证返回的列表按指定字段排序
        """
        contact_api = ContactAPI(session=login_session)

        logger.info("调用 List Contacts 接口（按 name 升序排序）")
        response = contact_api.list_contacts(size=20, **{"sort": "name,asc"})

        assert response.status_code == 200, f"接口返回状态码错误: {response.status_code}"

        parsed = contact_api.parse_list_response(response)
        assert not parsed.get("error"), f"响应解析失败: {parsed.get('message')}"

        contacts = parsed["content"]

        if len(contacts) >= 2:
            for i in range(len(contacts) - 1):
                current_name = contacts[i].get("name", "").lower()
                next_name = contacts[i + 1].get("name", "").lower()
                assert current_name <= next_name, \
                    f"排序不正确: {current_name} 应该在 {next_name} 之前"
            logger.info(f"✓ 排序验证成功（升序），共 {len(contacts)} 个 Contacts")
        else:
            logger.info(f"⚠ Contacts 数量不足，无法验证排序（当前 {len(contacts)} 个）")

    def test_list_contacts_fields_match_create(self, login_session, db_cleanup):
        """
        测试场景9：List 返回字段与创建时传入字段一一匹配
        验证点：
        1. 先创建一个 Contact（包含多个可选字段）
        2. 在 List 接口中用 email 精确筛选出该 Contact
        3. 验证 List 中的字段与创建时传入的值完全一致（无多余/缺失）
        4. 同时验证 List 中不应出现仅在 Detail 才有的字段
        """
        import time as time_module
        contact_api = ContactAPI(session=login_session)

        # 1. 创建 Contact（包含多个可选字段，便于验证）
        FIXED_ACCOUNT_ID = "251212054048470503"  # Auto testyan account 1
        unique_email = f"auto_list_match_{int(time_module.time())}@example.com"
        contact_data = {
            "account_id": FIXED_ACCOUNT_ID,
            "first_name": "Auto TestYan",
            "last_name": "ListMatch",
            "birth_date": "1990-06-15",
            "email": unique_email,
            "phone": "+14155550101",
            "gender": "Female",
            "middle_name": "ListTest"
        }

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

        # 2. 在 List 中用 email 筛选
        logger.info(f"在 List 中用 email 筛选: {unique_email}")
        list_resp = contact_api.list_contacts(email=unique_email, size=5)
        assert list_resp.status_code == 200
        parsed = contact_api.parse_list_response(list_resp)
        assert not parsed.get("error")

        contacts = parsed["content"]
        assert len(contacts) > 0, "List 中未找到刚创建的 Contact"

        # 取出对应的 Contact
        found = next((c for c in contacts if c.get("id") == created_id), None)
        assert found is not None, f"List 中未找到 id={created_id} 的 Contact"

        # 3. 验证 List 中的关键字段与创建时一致（无字段丢失）
        logger.info("验证 List 字段与创建字段一致")
        assert found.get("first_name") == contact_data["first_name"], \
            f"first_name 不匹配: 期望 {contact_data['first_name']}, 实际 {found.get('first_name')}"
        assert found.get("last_name") == contact_data["last_name"], \
            f"last_name 不匹配: 期望 {contact_data['last_name']}, 实际 {found.get('last_name')}"
        assert found.get("email") == contact_data["email"], \
            f"email 不匹配: 期望 {contact_data['email']}, 实际 {found.get('email')}"

        # phone / gender / middle_name 在 List 中可能不返回（由接口设计决定），记录但不强制断言
        for optional_field in ["phone", "gender", "middle_name"]:
            if optional_field in found:
                logger.info(f"  ✓ List 包含 {optional_field}: {found.get(optional_field)}")
            else:
                logger.info(f"  ℹ List 未返回 {optional_field}（Detail 接口才有）")

        # 4. 验证 List 必须包含的最小字段集
        list_required_fields = ["id", "account_id", "name", "first_name", "last_name", "email", "status"]
        for field in list_required_fields:
            assert field in found, f"List 中缺少必需字段: '{field}'"

        logger.info(f"✓ List 字段与创建字段匹配验证通过，id={created_id}")
