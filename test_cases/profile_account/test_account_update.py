"""
账户更新接口测试用例
测试 PUT /api/v1/cores/{core}/accounts/{account_id} 接口
"""
import pytest
from utils.logger import logger
from utils.assertions import (
    assert_status_ok,
    assert_response_parsed
)


@pytest.mark.update_api
class TestAccountUpdate:
    """
    账户更新接口测试用例集
    """

    def test_update_account_mailing_address_success(self, account_api):
        """
        测试场景1：成功更新账户邮寄地址
        验证点：
        1. 先从列表接口获取有效 account_id
        2. 构造更新数据（修改 mailing_city）
        3. 调用 Update 接口
        4. 验证状态码 200
        5. 验证返回体中 mailing_city 等于修改后的值
        6. 再次调用 Detail 接口确认数据落库
        """
        # 获取一个有效的账户 ID
        list_response = account_api.list_accounts(size=1)
        assert_status_ok(list_response)
        parsed_list = account_api.parse_list_response(list_response)
        assert_response_parsed(parsed_list)
        
        accounts = parsed_list["content"]
        if len(accounts) == 0:
            pytest.skip("没有可用的账户数据，跳过更新测试")
        
        account_id = accounts[0]["id"]
        
        # 构造更新数据
        new_city = "New York"
        new_state = "NY"
        update_data = {
            "mailing_city": new_city,
            "mailing_state": new_state,
            "mailing_street": "123 Test Street",
            "mailing_postalcode": "10001",
            "mailing_country": "US"
        }
        
        # 调用 Update 接口
        update_response = account_api.update_account(account_id, update_data)
        
        # 验证状态码
        assert_status_ok(update_response)
        
        # 验证返回体中的数据
        updated_account = update_response.json()
        if "data" in updated_account:
            updated_account = updated_account["data"]
        
        assert updated_account.get("mailing_city") == new_city, \
            f"返回体中的 mailing_city 不正确: 期望 '{new_city}'，实际 '{updated_account.get('mailing_city')}'"
        assert updated_account.get("mailing_state") == new_state, \
            f"返回体中的 mailing_state 不正确: 期望 '{new_state}'，实际 '{updated_account.get('mailing_state')}'"
        
        # 再次调用 Detail 接口确认数据落库
        detail_response = account_api.get_account_detail(account_id)
        assert_status_ok(detail_response)
        parsed_detail = account_api.parse_detail_response(detail_response)
        assert_response_parsed(parsed_detail)
        
        account_detail = parsed_detail["data"]
        assert account_detail.get("mailing_city") == new_city, \
            f"Detail 接口中的 mailing_city 不正确: 期望 '{new_city}'，实际 '{account_detail.get('mailing_city')}'"
        
        logger.info("✓ 更新成功并已落库确认: mailing_city={account_detail.get('mailing_city')}")

    def test_update_account_register_address(self, account_api):
        """
        测试场景2：更新账户注册地址
        验证点：
        1. 更新 register_street, register_city 等字段
        2. 验证更新成功
        """
        # 获取账户 ID
        list_response = account_api.list_accounts(size=1)
        assert_status_ok(list_response)
        parsed_list = account_api.parse_list_response(list_response)
        assert_response_parsed(parsed_list)
        
        if len(parsed_list["content"]) == 0:
            pytest.skip("没有可用的账户数据")
        
        account_id = parsed_list["content"][0]["id"]
        
        # 构造注册地址更新数据
        update_data = {
            "register_street": "456 Register Avenue",
            "register_city": "Los Angeles",
            "register_state": "CA",
            "register_postalcode": "90001",
            "register_country": "US"
        }
        
        # 调用 Update 接口
        update_response = account_api.update_account(account_id, update_data)
        
        # 验证
        assert_status_ok(update_response)
        
        updated_account = update_response.json()
        if "data" in updated_account:
            updated_account = updated_account["data"]
        
        assert updated_account.get("register_city") == "Los Angeles", \
            f"register_city 更新失败"
        
        logger.info("✓ 注册地址更新成功: {updated_account.get('register_city')}, {updated_account.get('register_state')}")

    def test_update_account_partial_fields(self, account_api):
        """
        测试场景3：部分字段更新
        验证点：
        1. 只更新部分字段（如只更新 mailing_city）
        2. 验证其他字段不受影响
        """
        # 获取账户详情（记录原始数据）
        list_response = account_api.list_accounts(size=1)
        assert_status_ok(list_response)
        parsed_list = account_api.parse_list_response(list_response)
        assert_response_parsed(parsed_list)
        
        if len(parsed_list["content"]) == 0:
            pytest.skip("没有可用的账户数据")
        
        account_id = parsed_list["content"][0]["id"]
        
        # 获取详情
        detail_response = account_api.get_account_detail(account_id)
        assert_status_ok(detail_response)
        parsed_detail = account_api.parse_detail_response(detail_response)
        assert_response_parsed(parsed_detail)
        original_account = parsed_detail["data"]
        
        original_state = original_account.get("mailing_state")
        
        # 只更新 mailing_city
        update_data = {
            "mailing_city": "Chicago"
        }
        
        update_response = account_api.update_account(account_id, update_data)
        
        # 验证
        assert_status_ok(update_response)
        
        updated_account = update_response.json()
        if "data" in updated_account:
            updated_account = updated_account["data"]
        
        # 验证 mailing_city 已更新
        assert updated_account.get("mailing_city") == "Chicago", \
            f"mailing_city 更新失败"
        
        # 验证其他字段不变（如果原始值不为空）
        if original_state:
            assert updated_account.get("mailing_state") == original_state, \
                f"mailing_state 不应该改变"
        
        logger.info("✓ 部分字段更新成功，mailing_city: {updated_account.get('mailing_city')}")

    def test_update_account_invalid_id(self, account_api):
        """
        测试场景4：使用无效的 account_id 更新
        验证点：
        1. 服务器返回 200 OK（防遍历设计）
        2. code=506, error_message="visibility permission deny"
        """
        invalid_id = "INVALID_ACCOUNT_ID_999999"
        update_data = {
            "mailing_city": "Test City"
        }

        update_response = account_api.update_account(invalid_id, update_data)
        assert_status_ok(update_response)

        response_body = update_response.json()

        expected_response = {
            "code": 506,
            "error_message": "visibility permission deny",
            "data": None
        }

        assert response_body == expected_response, \
            f"响应体不匹配\n期望: {expected_response}\n实际: {response_body}"

        logger.info("✓ 使用无效 ID 正确返回错误信息: code=506")

    def test_update_account_with_invalid_country_code(self, account_api):
        """
        测试场景5：使用非 ISO 3166 标准的国家代码更新 mailing_country / register_country
        文档说明：we followed country code standard in ISO 3166（2位大写字母代码，如 US/CN/GB）
        验证点：
        1. 传入不符合 ISO 3166 的国家代码（如 "USA"、"China"、"123"）
        2. 服务器返回 200
        3. code != 200（业务层校验失败）或字段值被忽略/原样存入
        """
        list_response = account_api.list_accounts(size=1)
        assert_status_ok(list_response)
        parsed_list = account_api.parse_list_response(list_response)
        assert_response_parsed(parsed_list)

        if not parsed_list["content"]:
            pytest.skip("没有可用的账户数据")

        account_id = parsed_list["content"][0]["id"]

        # 使用非标准国家代码（3字母、完整单词、数字）
        invalid_country_code = "USA"  # ISO 3166-1 alpha-3，不是 alpha-2
        update_data = {
            "mailing_country": invalid_country_code,
            "register_country": "China"  # 完整单词，非2位代码
        }

        logger.info(f"  使用非标准国家代码: mailing_country='{invalid_country_code}', register_country='China'")
        update_response = account_api.update_account(account_id, update_data)

        assert update_response.status_code == 200, \
            f"服务器应该返回 200，实际: {update_response.status_code}"

        response_body = update_response.json()
        logger.info(f"  响应: {response_body}")

        if isinstance(response_body, dict) and "code" in response_body and response_body.get("code") != 200:
            logger.info(f"  非标准国家代码被拒绝: code={response_body.get('code')}, msg={response_body.get('error_message')}")
        else:
            updated = response_body.get("data") if "data" in response_body else response_body
            actual_country = updated.get("mailing_country") if updated else None
            logger.warning(f"  ⚠️ 非标准国家代码被接受，mailing_country 实际存储为: '{actual_country}'")

        logger.info("✓ 非 ISO 3166 国家代码更新测试完成")

    def test_update_account_with_non_documented_field(self, account_api):
        """
        测试场景6：传入非文档指定的更新字段
        文档指定的可更新字段：mailing_*/register_* 共10个地址字段
        非文档字段：如 account_name、tax_id、account_status 等
        验证点：
        1. 传入 account_name（非文档指定字段）进行更新
        2. 服务器返回 200
        3. account_name 不被更新（忽略非文档字段）或返回错误
        """
        list_response = account_api.list_accounts(size=1)
        assert_status_ok(list_response)
        parsed_list = account_api.parse_list_response(list_response)
        assert_response_parsed(parsed_list)

        if not parsed_list["content"]:
            pytest.skip("没有可用的账户数据")

        account_id = parsed_list["content"][0]["id"]
        original_name = parsed_list["content"][0].get("account_name")

        # 尝试更新非文档指定字段
        fake_name = "Auto TestYan Should Not Change"
        update_data = {
            "account_name": fake_name,     # 非文档指定字段
            "account_status": "Terminated" # 非文档指定字段
        }

        logger.info(f"  尝试更新非文档指定字段: account_name='{fake_name}', account_status='Terminated'")
        update_response = account_api.update_account(account_id, update_data)

        assert update_response.status_code == 200, \
            f"服务器应该返回 200，实际: {update_response.status_code}"

        response_body = update_response.json()
        logger.info(f"  响应: {response_body}")

        # 验证 account_name 没有被修改
        detail_response = account_api.get_account_detail(account_id)
        assert_status_ok(detail_response)
        parsed_detail = account_api.parse_detail_response(detail_response)
        current_name = parsed_detail["data"].get("account_name")

        assert current_name == original_name, \
            f"非文档字段 account_name 被意外修改！原始='{original_name}'，当前='{current_name}'"

        logger.info(f"✓ 非文档指定字段未被更新，account_name 保持原值: '{current_name}'")
