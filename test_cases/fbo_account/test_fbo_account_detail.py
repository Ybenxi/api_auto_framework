"""
FBO Account 详情接口测试用例
测试 GET /api/v1/cores/{core}/fbo-accounts/{id} 接口
"""
import pytest
from utils.assertions import (
    assert_status_ok,
    assert_response_parsed,
    assert_fields_present
)


class TestFboAccountDetail:
    """
    FBO Account 详情接口测试用例集
    """

    def test_get_fbo_account_detail_success(self, fbo_account_api):
        """
        测试场景1：成功获取 FBO Account 详情
        依赖逻辑：先从列表接口获取一个有效的 fbo_account_id，然后获取详情
        验证点：
        1. 列表接口返回成功
        2. 详情接口返回 200
        3. 返回的 id 与请求的 id 一致
        4. 关键字段不为空（name, account_identifier, status 等）
        """
        # 先调用列表接口获取一个 FBO Account ID
        list_response = fbo_account_api.list_fbo_accounts(size=1)
        assert_status_ok(list_response)
        
        parsed_list = fbo_account_api.parse_list_response(list_response)
        assert_response_parsed(parsed_list)
        
        fbo_accounts = parsed_list["content"]
        if len(fbo_accounts) == 0:
            pytest.skip("没有可用的 FBO Account 数据，跳过详情测试")
        
        # 提取第一个 FBO Account 的 ID
        fbo_account_id = fbo_accounts[0]["id"]
        expected_name = fbo_accounts[0].get("name")
        
        # 调用详情接口
        detail_response = fbo_account_api.get_fbo_account_detail(fbo_account_id)
        
        # 断言状态码和解析响应
        assert_status_ok(detail_response)
        parsed_detail = fbo_account_api.parse_detail_response(detail_response)
        assert_response_parsed(parsed_detail)
        
        fbo_detail = parsed_detail["data"]
        
        # 验证返回的 ID 一致
        assert fbo_detail.get("id") == fbo_account_id, \
            f"返回的 ID {fbo_detail.get('id')} 与请求的 ID {fbo_account_id} 不一致"
        
        # 验证关键字段不为空
        assert fbo_detail.get("name") is not None, "name 字段为空"
        assert fbo_detail.get("account_identifier") is not None, "account_identifier 字段为空"
        assert fbo_detail.get("status") is not None, "status 字段为空"
        
        # 验证名称一致
        assert fbo_detail.get("name") == expected_name, \
            f"详情中的名称 {fbo_detail.get('name')} 与列表中的不一致"
        
        print(f"✓ 成功获取 FBO Account 详情: ID={fbo_detail.get('id')}, "
              f"Name={fbo_detail.get('name')}, "
              f"Account Identifier={fbo_detail.get('account_identifier')}")

    def test_get_fbo_account_detail_fields_completeness(self, fbo_account_api):
        """
        测试场景2：验证详情响应字段完整性
        验证点：
        1. 返回的 FBO Account 详情包含所有必需字段
        2. 字段类型正确
        """
        # 先获取一个 FBO Account ID
        list_response = fbo_account_api.list_fbo_accounts(size=1)
        assert_status_ok(list_response)
        parsed_list = fbo_account_api.parse_list_response(list_response)
        assert_response_parsed(parsed_list)
        
        if len(parsed_list["content"]) == 0:
            pytest.skip("没有可用的 FBO Account 数据")
        
        fbo_account_id = parsed_list["content"][0]["id"]
        
        # 获取详情
        detail_response = fbo_account_api.get_fbo_account_detail(fbo_account_id)
        assert_status_ok(detail_response)
        
        parsed_detail = fbo_account_api.parse_detail_response(detail_response)
        assert_response_parsed(parsed_detail)
        
        fbo_detail = parsed_detail["data"]
        
        # 验证必需字段
        required_fields = [
            "id",
            "name",
            "account_identifier",
            "sub_account_id",
            "status",
            "balance",
            "available_balance",
            "minimum_balance",
            "pending_deposits",
            "pending_withdrawals",
            "created_date"
        ]
        
        assert_fields_present(fbo_detail, required_fields, obj_name="FBO Account 详情")
        
        print(f"✓ 字段完整性验证通过，FBO Account 详情包含所有必需字段")

    def test_get_fbo_account_detail_invalid_id(self, fbo_account_api):
        """
        测试场景3：使用无效的 fbo_account_id 获取详情
        验证点（基于真实业务行为）：
        1. 服务器返回 200 OK（统一错误处理设计）
        2. 响应体包含错误信息
        """
        # 使用一个不存在的 fbo_account_id
        invalid_id = "INVALID_FBO_ACCOUNT_ID_999999"
        detail_response = fbo_account_api.get_fbo_account_detail(invalid_id)
        
        # 验证返回 200 状态码（统一错误处理）
        assert_status_ok(detail_response)
        
        # 验证响应包含错误信息
        response_body = detail_response.json()
        assert "error" in detail_response.text.lower() or response_body.get("code") != 200, \
            f"无效 ID 应该返回错误信息"
        
        print(f"✓ 使用无效 ID 测试完成")

    def test_get_fbo_account_detail_compare_with_list(self, fbo_account_api):
        """
        测试场景4：对比详情接口和列表接口返回的数据一致性
        验证点：
        1. 列表接口和详情接口返回的相同字段值一致
        """
        # 获取 FBO Accounts 列表
        list_response = fbo_account_api.list_fbo_accounts(size=1)
        assert_status_ok(list_response)
        parsed_list = fbo_account_api.parse_list_response(list_response)
        assert_response_parsed(parsed_list)
        
        if len(parsed_list["content"]) == 0:
            pytest.skip("没有可用的 FBO Account 数据")
        
        fbo_from_list = parsed_list["content"][0]
        fbo_account_id = fbo_from_list["id"]
        
        # 获取 FBO Account 详情
        detail_response = fbo_account_api.get_fbo_account_detail(fbo_account_id)
        assert_status_ok(detail_response)
        parsed_detail = fbo_account_api.parse_detail_response(detail_response)
        assert_response_parsed(parsed_detail)
        fbo_from_detail = parsed_detail["data"]
        
        # 对比关键字段
        fields_to_compare = [
            "id",
            "name",
            "account_identifier",
            "sub_account_id",
            "status",
            "balance"
        ]
        
        for field in fields_to_compare:
            list_value = fbo_from_list.get(field)
            detail_value = fbo_from_detail.get(field)
            assert list_value == detail_value, \
                f"字段 {field} 在列表和详情中不一致: 列表={list_value}, 详情={detail_value}"
        
        print(f"✓ 列表和详情接口返回的数据一致")
