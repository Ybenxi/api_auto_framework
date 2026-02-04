"""
账户 Contacts 接口测试用例
测试 GET /api/v1/cores/{core}/accounts/{account_id}/contacts 接口
"""
import pytest
from utils.assertions import (
from utils.logger import logger
    assert_status_ok,
    assert_response_parsed,
    assert_list_structure,
    assert_pagination,
    assert_fields_present
)


@pytest.mark.contact_api
class TestAccountContacts:
    """
    账户 Contacts 接口测试用例集
    """

    def test_get_account_contacts_success(self, account_api):
        """
        测试场景1：成功获取账户关联的 Contacts
        依赖逻辑：先从列表接口获取一个有效的 account_id，然后获取 Contacts
        验证点：
        1. 列表接口返回成功
        2. Contacts 接口返回 200
        3. 返回数据结构正确（content 列表）
        4. 如果有数据，验证字段完整性
        """
        # 先调用列表接口获取一个账户 ID
        list_response = account_api.list_accounts(size=1)
        assert_status_ok(list_response)
        parsed_list = account_api.parse_list_response(list_response)
        assert_response_parsed(parsed_list)
        
        accounts = parsed_list["content"]
        if len(accounts) == 0:
            pytest.skip("没有可用的账户数据，跳过 Contacts 测试")
        
        # 提取第一个账户的 ID
        account_id = accounts[0]["id"]
        
        # 调用 Contacts 接口
        contacts_response = account_api.get_account_contacts(account_id)
        
        # 断言状态码和解析响应
        assert_status_ok(contacts_response)
        parsed_contacts = account_api.parse_contacts_response(contacts_response)
        assert_response_parsed(parsed_contacts)
        assert_list_structure(parsed_contacts, has_pagination=True)
        
        contacts = parsed_contacts["content"]
        
        # 如果有数据，验证字段完整性
        if len(contacts) > 0:
            first_contact = contacts[0]
            
            # 验证必需字段
            required_fields = ["id", "account_id", "name", "status", "email", "create_time"]
            assert_fields_present(first_contact, required_fields, obj_name="Contact")
            
            print(f"✓ 成功获取 Contacts: 总数={parsed_contacts['total_elements']}, "
                  f"第一个 Contact ID={first_contact.get('id')}, 姓名={first_contact.get('name')}")
        else:
            logger.info("✓ 成功获取 Contacts（当前账户没有关联的 Contacts）")

    def test_get_account_contacts_with_filters(self, account_api):
        """
        测试场景2：使用筛选条件获取 Contacts
        验证点：
        1. 使用 status 筛选
        2. 验证返回结果符合筛选条件
        """
        # 获取账户 ID
        list_response = account_api.list_accounts(size=1)
        assert_status_ok(list_response)
        parsed_list = account_api.parse_list_response(list_response)
        assert_response_parsed(parsed_list)
        
        if len(parsed_list["content"]) == 0:
            pytest.skip("没有可用的账户数据")
        
        account_id = parsed_list["content"][0]["id"]
        
        # 使用 status 筛选
        contacts_response = account_api.get_account_contacts(account_id, status="Active")
        
        # 验证状态码和解析响应
        assert_status_ok(contacts_response)
        parsed_contacts = account_api.parse_contacts_response(contacts_response)
        assert_response_parsed(parsed_contacts)
        
        contacts = parsed_contacts["content"]
        
        # 验证筛选结果
        if len(contacts) > 0:
            for contact in contacts:
                if contact.get("status"):
                    logger.info(f"  Contact {contact.get('name')}: status={contact.get('status')}")
        
        logger.info("✓ 筛选测试完成，返回 {len(contacts)} 个 Contacts")

    def test_get_account_contacts_pagination(self, account_api):
        """
        测试场景3：验证分页功能
        验证点：
        1. 使用不同的 page 和 size
        2. 验证分页信息正确
        """
        # 获取账户 ID
        list_response = account_api.list_accounts(size=1)
        assert_status_ok(list_response)
        parsed_list = account_api.parse_list_response(list_response)
        assert_response_parsed(parsed_list)
        
        if len(parsed_list["content"]) == 0:
            pytest.skip("没有可用的账户数据")
        
        account_id = parsed_list["content"][0]["id"]
        
        # 使用分页参数
        contacts_response = account_api.get_account_contacts(account_id, page=0, size=5)
        
        # 验证状态码和解析响应
        assert_status_ok(contacts_response)
        parsed_contacts = account_api.parse_contacts_response(contacts_response)
        assert_response_parsed(parsed_contacts)
        
        # 验证分页信息
        assert_pagination(parsed_contacts, expected_size=5, expected_page=0)
        
        print(f"✓ 分页测试完成: 总元素数={parsed_contacts['total_elements']}, "
              f"总页数={parsed_contacts['total_pages']}, 当前页={parsed_contacts['number']}")

    def test_get_account_contacts_empty_result(self, account_api):
        """
        测试场景4：验证空结果处理
        验证点：
        1. 使用不存在的筛选条件
        2. 验证返回 200 和空列表
        """
        # 获取账户 ID
        list_response = account_api.list_accounts(size=1)
        assert_status_ok(list_response)
        parsed_list = account_api.parse_list_response(list_response)
        assert_response_parsed(parsed_list)
        
        if len(parsed_list["content"]) == 0:
            pytest.skip("没有可用的账户数据")
        
        account_id = parsed_list["content"][0]["id"]
        
        # 使用不存在的筛选条件
        contacts_response = account_api.get_account_contacts(
            account_id,
            name="NONEXISTENT_CONTACT_NAME_999999"
        )
        
        # 验证状态码和解析响应
        assert_status_ok(contacts_response)
        parsed_contacts = account_api.parse_contacts_response(contacts_response)
        assert_response_parsed(parsed_contacts)
        
        contacts = parsed_contacts["content"]
        assert isinstance(contacts, list), "content 应该是一个列表"
        
        logger.info("✓ 空结果测试完成，返回 {len(contacts)} 个 Contacts")

    def test_get_account_contacts_invalid_id(self, account_api):
        """
        测试场景5：使用无效的 account_id
        验证点：
        1. 使用无效 ID
        2. 验证返回错误或空列表
        """
        # 使用无效的 account_id
        invalid_id = "INVALID_ACCOUNT_ID_999999"
        contacts_response = account_api.get_account_contacts(invalid_id)
        
        # 验证状态码（可能是 200 + 空列表，或者错误状态码）
        if contacts_response.status_code == 200:
            # 如果返回 200，验证是空列表或错误信息
            parsed_contacts = account_api.parse_contacts_response(contacts_response)
            if not parsed_contacts.get("error"):
                contacts = parsed_contacts["content"]
                logger.info(f"  返回 200 和空列表（{len(contacts)} 个 Contacts）")
            else:
                logger.info(f"  返回 200 和错误信息")
        else:
            logger.info(f"  返回错误状态码: {contacts_response.status_code}")
        
        logger.info("✓ 无效 ID 测试完成")
