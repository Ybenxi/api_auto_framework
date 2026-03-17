"""
账户详情接口测试用例
测试 GET /api/v1/cores/{core}/accounts/{account_id} 接口
"""
import pytest
from utils.logger import logger
from utils.assertions import (
    assert_status_ok,
    assert_response_parsed,
    assert_fields_present
)


class TestAccountDetail:
    """
    账户详情接口测试用例集
    """

    def test_get_account_detail_success(self, account_api):
        """
        测试场景1：成功获取账户详情
        依赖逻辑：先从列表接口获取一个有效的 account_id，然后获取详情
        验证点：
        1. 列表接口返回成功
        2. 详情接口返回 200
        3. 返回的 id 与请求的 id 一致
        4. 关键字段不为空
        """
        list_response = account_api.list_accounts(size=1)
        assert_status_ok(list_response)

        parsed_list = account_api.parse_list_response(list_response)
        assert_response_parsed(parsed_list)

        accounts = parsed_list["content"]
        if not accounts:
            pytest.skip("没有可用的账户数据，跳过详情测试")

        account_id = accounts[0]["id"]
        expected_account_number = accounts[0].get("account_number")

        detail_response = account_api.get_account_detail(account_id)
        assert_status_ok(detail_response)

        parsed_detail = account_api.parse_detail_response(detail_response)
        assert_response_parsed(parsed_detail)

        account_detail = parsed_detail["data"]

        assert account_detail.get("id") == account_id, \
            f"返回的 ID {account_detail.get('id')} 与请求的 ID {account_id} 不一致"
        assert account_detail.get("account_number") is not None, "account_number 字段为空"
        assert account_detail.get("account_name") is not None, "account_name 字段为空"
        assert account_detail.get("account_status") is not None, "account_status 字段为空"
        assert account_detail.get("account_number") == expected_account_number, \
            f"详情中的账户编号 {account_detail.get('account_number')} 与列表中的不一致"

        logger.info(f"✓ 成功获取账户详情: ID={account_detail.get('id')}, "
                    f"账户编号={account_detail.get('account_number')}, "
                    f"账户名称={account_detail.get('account_name')}")

    def test_get_account_detail_fields_completeness(self, account_api):
        """
        测试场景2：验证详情响应字段完整性
        验证点：
        1. 返回的账户详情包含所有必需字段
        2. 可选字段也应在响应中（可为 null）
        """
        list_response = account_api.list_accounts(size=1)
        assert_status_ok(list_response)
        parsed_list = account_api.parse_list_response(list_response)
        assert_response_parsed(parsed_list)

        if not parsed_list["content"]:
            pytest.skip("没有可用的账户数据")

        account_id = parsed_list["content"][0]["id"]

        detail_response = account_api.get_account_detail(account_id)
        assert_status_ok(detail_response)

        parsed_detail = account_api.parse_detail_response(detail_response)
        assert_response_parsed(parsed_detail)

        account_detail = parsed_detail["data"]

        required_fields = [
            "id", "account_name", "account_number",
            "account_status", "record_type", "create_time", "risk_level"
        ]
        assert_fields_present(account_detail, required_fields, obj_name="账户详情")

        optional_fields = [
            "business_entity_type", "account_email", "tax_id",
            "mailing_street", "mailing_city", "mailing_state",
            "mailing_postalcode", "mailing_country",
            "register_street", "register_city", "register_state",
            "register_postalcode", "register_country",
            "authorized_agent", "external_id"
        ]
        for field in optional_fields:
            assert field in account_detail, f"账户详情缺少字段: {field}"

        logger.info("✓ 字段完整性验证通过")

    def test_get_account_detail_invalid_id(self, account_api):
        """
        测试场景3：使用无效的 account_id（格式正确但不存在）
        验证点：
        1. 服务器返回 200 OK（防遍历设计）
        2. code=506, error_message="visibility permission deny", data=null
        """
        invalid_id = "INVALID_ACCOUNT_ID_999999"
        detail_response = account_api.get_account_detail(invalid_id)

        assert_status_ok(detail_response)

        response_body = detail_response.json()

        expected_response = {
            "code": 506,
            "error_message": "visibility permission deny",
            "data": None
        }

        assert response_body == expected_response, \
            f"响应体不匹配\n期望: {expected_response}\n实际: {response_body}"

        logger.info("✓ 使用无效 ID 正确返回错误信息: code=506")

    def test_get_account_detail_with_invisible_id(self, account_api):
        """
        测试场景4：使用不在当前用户 visible 范围内的 account_id
        验证点：
        1. 使用他人账户 241010195849720143（yhan account Sanchez）
        2. 服务器返回 200 OK
        3. code=506, error_message 包含 "visibility permission deny"
        4. data 为 null
        """
        invisible_account_id = "241010195849720143"  # yhan account Sanchez，不属于当前用户
        logger.info(f"使用不在 visible 范围内的 account_id: {invisible_account_id}")

        detail_response = account_api.get_account_detail(invisible_account_id)
        assert_status_ok(detail_response)

        response_body = detail_response.json()
        logger.info(f"  响应: {response_body}")

        assert response_body.get("code") == 506, \
            f"越权 account_id 应该返回 code=506，实际: {response_body.get('code')}"

        error_msg = response_body.get("error_message", "")
        assert "visibility permission deny" in error_msg.lower(), \
            f"error_message 应包含 'visibility permission deny'，实际: {error_msg}"

        assert response_body.get("data") is None, "visibility 拒绝时 data 应为 null"

        logger.info(f"✓ 越权 account_id 校验通过: code=506, msg={error_msg}")

    def test_get_account_detail_compare_with_list(self, account_api):
        """
        测试场景5：对比详情接口和列表接口返回的数据一致性
        验证点：
        1. 列表接口和详情接口返回的相同字段值一致
        """
        list_response = account_api.list_accounts(size=1)
        assert_status_ok(list_response)
        parsed_list = account_api.parse_list_response(list_response)
        assert_response_parsed(parsed_list)

        if not parsed_list["content"]:
            pytest.skip("没有可用的账户数据")

        account_from_list = parsed_list["content"][0]
        account_id = account_from_list["id"]

        detail_response = account_api.get_account_detail(account_id)
        assert_status_ok(detail_response)
        parsed_detail = account_api.parse_detail_response(detail_response)
        assert_response_parsed(parsed_detail)
        account_from_detail = parsed_detail["data"]

        fields_to_compare = ["id", "account_name", "account_number", "account_status", "record_type"]

        for field in fields_to_compare:
            list_value = account_from_list.get(field)
            detail_value = account_from_detail.get(field)
            assert list_value == detail_value, \
                f"字段 {field} 在列表和详情中不一致: 列表={list_value}, 详情={detail_value}"

        logger.info("✓ 列表和详情接口返回的数据一致")
