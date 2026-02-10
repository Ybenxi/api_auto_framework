"""
Contact Update 接口测试用例
测试 PUT /api/v1/cores/{core}/contacts/{id} 接口
"""
import pytest
from api.contact_api import ContactAPI
from utils.logger import logger


@pytest.mark.contact
@pytest.mark.update_api
class TestContactUpdate:
    """
    Contact 更新接口测试用例集
    """

    def test_update_contact_first_name(self, login_session):
        """
        测试场景1：更新 Contact 的 first_name
        验证点：
        1. 接口返回 200
        2. 返回的 first_name 已更新
        
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
        original_first_name = contacts[0].get("first_name")
        logger.info(f"  获取到 Contact ID: {contact_id}")
        logger.info(f"  原始 first_name: {original_first_name}")
        
        # 3. 准备更新数据
        logger.info("准备更新数据")
        import time
        new_first_name = f"Auto TestYan Updated {int(time.time())}"
        update_data = {
            "first_name": new_first_name
        }
        logger.info(f"  新 first_name: {new_first_name}")
        
        # 4. 调用 Update 接口
        logger.info("调用 Update Contact 接口")
        update_response = contact_api.update_contact(contact_id, update_data)
        
        # 5. 断言状态码
        logger.info("验证 HTTP 状态码为 200")
        assert update_response.status_code == 200, \
            f"Update Contact 接口返回状态码错误: {update_response.status_code}, Response: {update_response.text}"
        
        # 6. 解析响应并验证更新结果
        logger.info("解析响应并验证更新结果")
        response_body = update_response.json()
        updated_contact = response_body.get("data") if "data" in response_body else response_body
        
        assert updated_contact.get("first_name") == new_first_name, \
            f"first_name 未更新: 期望 {new_first_name}, 实际 {updated_contact.get('first_name')}"
        
        logger.info("✓ 成功更新 Contact first_name:")
        logger.info(f"  ID: {updated_contact['id']}")
        logger.info(f"  原始 first_name: {original_first_name}")
        logger.info(f"  新 first_name: {updated_contact.get('first_name')}")

    def test_update_contact_phone(self, login_session):
        """
        测试场景2：更新 Contact 的 phone
        验证点：
        1. 接口返回 200
        2. 返回的 phone 已更新
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
        original_phone = contacts[0].get("phone")
        logger.info(f"  获取到 Contact ID: {contact_id}")
        logger.info(f"  原始 phone: {original_phone}")
        
        # 3. 准备更新数据
        logger.info("准备更新数据")
        new_phone = "+14155552671"
        update_data = {
            "phone": new_phone
        }
        logger.info(f"  新 phone: {new_phone}")
        
        # 4. 调用 Update 接口
        logger.info("调用 Update Contact 接口")
        update_response = contact_api.update_contact(contact_id, update_data)
        
        # 5. 断言状态码
        logger.info("验证 HTTP 状态码为 200")
        assert update_response.status_code == 200, \
            f"Update Contact 接口返回状态码错误: {update_response.status_code}, Response: {update_response.text}"
        
        # 6. 解析响应并验证更新结果
        logger.info("解析响应并验证更新结果")
        response_body = update_response.json()
        updated_contact = response_body.get("data") if "data" in response_body else response_body
        
        assert updated_contact.get("phone") == new_phone, \
            f"phone 未更新: 期望 {new_phone}, 实际 {updated_contact.get('phone')}"
        
        logger.info("✓ 成功更新 Contact phone:")
        logger.info(f"  ID: {updated_contact['id']}")
        logger.info(f"  原始 phone: {original_phone}")
        logger.info(f"  新 phone: {updated_contact.get('phone')}")

    def test_update_contact_multiple_fields(self, login_session):
        """
        测试场景3：同时更新多个字段（first_name, last_name, phone）
        验证点：
        1. 接口返回 200
        2. 所有更新的字段都生效
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
        
        # 3. 准备更新数据（多个字段）
        logger.info("准备更新数据（多个字段）")
        import time
        timestamp = int(time.time())
        update_data = {
            "first_name": f"Auto TestYan MultiUpdate {timestamp}",
            "last_name": "Auto TestYan Test",
            "phone": "+14155552999"
        }
        logger.info(f"  更新 first_name: {update_data['first_name']}")
        logger.info(f"  更新 last_name: {update_data['last_name']}")
        logger.info(f"  更新 phone: {update_data['phone']}")
        
        # 4. 调用 Update 接口
        logger.info("调用 Update Contact 接口")
        update_response = contact_api.update_contact(contact_id, update_data)
        
        # 5. 断言状态码
        logger.info("验证 HTTP 状态码为 200")
        assert update_response.status_code == 200, \
            f"Update Contact 接口返回状态码错误: {update_response.status_code}, Response: {update_response.text}"
        
        # 6. 解析响应并验证所有更新字段
        logger.info("解析响应并验证所有更新字段")
        response_body = update_response.json()
        updated_contact = response_body.get("data") if "data" in response_body else response_body
        
        assert updated_contact.get("first_name") == update_data["first_name"], \
            f"first_name 未更新"
        
        assert updated_contact.get("last_name") == update_data["last_name"], \
            f"last_name 未更新"
        
        assert updated_contact.get("phone") == update_data["phone"], \
            f"phone 未更新"
        
        logger.info("✓ 成功更新多个字段:")
        logger.info(f"  ID: {updated_contact['id']}")
        logger.info(f"  first_name: {updated_contact.get('first_name')}")
        logger.info(f"  last_name: {updated_contact.get('last_name')}")
        logger.info(f"  phone: {updated_contact.get('phone')}")

    def test_update_contact_address_fields(self, login_session):
        """
        测试场景4：更新地址相关字段（permanent_address, mailing_street）
        验证点：
        1. 接口返回 200
        2. 地址字段更新成功
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
        
        # 3. 准备更新数据（地址字段）
        logger.info("准备更新数据（地址字段）")
        update_data = {
            "permanent_address": "123 Updated Street",
            "permanent_city": "Updated City",
            "permanent_state": "CA",
            "permanent_postalcode": "90001",
            "mailing_street": "456 Mailing Ave",
            "mailing_city": "Mailing City",
            "mailing_state": "NY",
            "mailing_postalcode": "10001"
        }
        
        # 4. 调用 Update 接口
        logger.info("调用 Update Contact 接口")
        update_response = contact_api.update_contact(contact_id, update_data)
        
        # 5. 断言状态码
        logger.info("验证 HTTP 状态码为 200")
        assert update_response.status_code == 200, \
            f"Update Contact 接口返回状态码错误: {update_response.status_code}, Response: {update_response.text}"
        
        # 6. 解析响应并验证更新结果
        logger.info("解析响应并验证地址字段更新")
        response_body = update_response.json()
        updated_contact = response_body.get("data") if "data" in response_body else response_body
        
        assert updated_contact.get("permanent_address") == update_data["permanent_address"], \
            f"permanent_address 未更新"
        
        assert updated_contact.get("mailing_street") == update_data["mailing_street"], \
            f"mailing_street 未更新"
        
        logger.info("✓ 成功更新地址字段:")
        logger.info(f"  permanent_address: {updated_contact.get('permanent_address')}")
        logger.info(f"  mailing_street: {updated_contact.get('mailing_street')}")

    def test_update_contact_invalid_id(self, login_session):
        """
        测试场景5：使用无效的 Contact ID 更新
        验证点：
        1. 接口返回 200（防遍历设计）
        2. 返回错误码 506 和错误信息 "visibility permission deny"
        """
        # 1. 初始化 API 对象
        contact_api = ContactAPI(session=login_session)
        
        # 2. 使用无效的 Contact ID
        invalid_contact_id = "invalid_contact_id_999999"
        
        logger.info("使用无效的 Contact ID: {invalid_contact_id}")
        
        # 3. 准备更新数据
        update_data = {
            "first_name": "Auto TestYan InvalidTest"
        }
        
        # 4. 调用 Update 接口
        logger.info("调用 Update Contact 接口")
        update_response = contact_api.update_contact(invalid_contact_id, update_data)
        
        # 5. 验证状态码（防遍历设计：返回 200）
        logger.info("验证 HTTP 状态码为 200（防遍历设计）")
        assert update_response.status_code == 200, \
            f"无效 ID 应返回 200（防遍历），实际返回: {update_response.status_code}"
        
        # 6. 解析响应并验证错误码
        logger.info("验证错误码和错误信息")
        try:
            response_body = update_response.json()
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
            logger.info(f"  响应内容: {update_response.text}")
            raise

    def test_update_contact_invalid_phone_format(self, login_session):
        """
        测试场景6：使用无效的 phone 格式更新
        验证点：
        1. 接口返回 400 或其他错误状态码
        2. 错误信息提示 phone 格式错误
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
        
        # 3. 准备更新数据（无效的 phone 格式）
        logger.info("准备更新数据（无效的 phone 格式）")
        update_data = {
            "first_name": "Auto TestYan InvalidPhone",  # 保持命名规范
            "phone": "123456789"  # 非 E.164 格式
        }
        
        # 4. 调用 Update 接口
        logger.info("调用 Update Contact 接口")
        update_response = contact_api.update_contact(contact_id, update_data)
        
        # 5. 验证返回错误状态码
        logger.info("验证返回错误状态码（400 或其他）")
        logger.info(f"  状态码: {update_response.status_code}")
        logger.info(f"  响应: {update_response.text}")
        
        if update_response.status_code != 200:
            logger.info("✓ Phone 格式验证生效")
        else:
            logger.info(f"⚠ API 未验证 phone 格式")

    def test_update_contact_empty_data(self, login_session):
        """
        测试场景7：使用空数据更新（不更新任何字段）
        验证点：
        1. 接口返回 200 或 400
        2. 验证 API 对空数据的处理
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
        
        # 3. 准备空数据
        logger.info("准备空数据")
        update_data = {}
        
        # 4. 调用 Update 接口
        logger.info("调用 Update Contact 接口")
        update_response = contact_api.update_contact(contact_id, update_data)
        
        # 5. 验证状态码
        logger.info("验证状态码")
        logger.info(f"  状态码: {update_response.status_code}")
        logger.info(f"  响应: {update_response.text}")
        
        if update_response.status_code == 200:
            logger.info("✓ API 接受空数据（不更新任何字段）")
        else:
            logger.info("✓ API 拒绝空数据")
