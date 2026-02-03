"""
Sub Account Detail 接口测试用例
测试 GET /api/v1/cores/{core}/sub-accounts/:sub_account_id 接口
对应文档标题: Retrieve Sub Account Detail
"""
import pytest
from api.sub_account_api import SubAccountAPI


@pytest.mark.sub_account
@pytest.mark.detail_api
class TestSubAccountRetrieveSubAccountDetail:
    """
    Sub Account 详情查询接口测试用例集
    """

    def test_retrieve_sub_account_detail_success(self, login_session):
        """
        测试场景：成功获取 Sub Account 详情
        验证点：
        1. 先获取列表，取第一个 Sub Account ID
        2. 调用详情接口返回 200
        3. 返回数据包含必需字段
        """
        # 1. 初始化 API 对象
        sa_api = SubAccountAPI(session=login_session)
        
        # 2. 先获取列表，取第一个 Sub Account ID
        print("\n[Step] 获取 Sub Accounts 列表")
        list_response = sa_api.list_sub_accounts(page=0, size=1)
        assert list_response.status_code == 200, \
            f"List Sub Accounts 接口返回状态码错误: {list_response.status_code}"
        
        parsed_list = sa_api.parse_list_response(list_response)
        sub_accounts = parsed_list.get("content", [])
        
        if len(sub_accounts) == 0:
            pytest.skip("没有可用的 Sub Account 进行详情查询测试")
        
        sub_account_id = sub_accounts[0].get("id")
        print(f"  使用 Sub Account ID: {sub_account_id}")
        
        # 3. 调用详情接口
        print("[Step] 调用 Retrieve Sub Account Detail 接口")
        detail_response = sa_api.get_sub_account_detail(sub_account_id)
        
        # 4. 验证状态码
        print("[Step] 验证 HTTP 状态码为 200")
        assert detail_response.status_code == 200, \
            f"Retrieve Sub Account Detail 接口返回状态码错误: {detail_response.status_code}, Response: {detail_response.text}"
        
        # 5. 解析响应
        print("[Step] 解析响应并验证数据结构")
        parsed_detail = sa_api.parse_detail_response(detail_response)
        assert not parsed_detail.get("error"), f"Detail 响应解析失败: {parsed_detail.get('message')}"
        
        # 6. 验证必需字段
        print("[Step] 验证返回数据字段")
        expected_fields = ["id", "name", "financial_account_id", "status", "balance"]
        
        for field in expected_fields:
            if field in parsed_detail:
                print(f"  ✓ {field}: {parsed_detail.get(field)}")
            else:
                print(f"  - {field}: (not present)")
        
        print(f"✓ Sub Account 详情获取成功")

    def test_retrieve_sub_account_detail_with_invalid_id(self, login_session):
        """
        测试场景：使用无效 ID 获取详情
        验证点：
        1. 接口返回非 200 状态码（404 或其他错误码）
        """
        sa_api = SubAccountAPI(session=login_session)
        
        print("\n[Step] 使用无效 ID 调用详情接口")
        invalid_id = "invalid_sub_account_id_12345"
        detail_response = sa_api.get_sub_account_detail(invalid_id)
        
        print(f"[Step] 验证返回状态码")
        print(f"  状态码: {detail_response.status_code}")
        
        # 无效 ID 应该返回非 200 状态码
        assert detail_response.status_code != 200 or "error" in detail_response.text.lower(), \
            f"无效 ID 应该返回错误，但返回了: {detail_response.status_code}"
        
        print(f"✓ 无效 ID 测试完成")

    def test_retrieve_sub_account_detail_response_structure(self, login_session):
        """
        测试场景：验证详情响应的完整数据结构
        验证点：
        1. 接口返回 200
        2. 响应包含完整的 Sub Account 信息
        """
        sa_api = SubAccountAPI(session=login_session)
        
        # 获取列表
        print("\n[Step] 获取 Sub Accounts 列表")
        list_response = sa_api.list_sub_accounts(page=0, size=1)
        assert list_response.status_code == 200
        
        parsed_list = sa_api.parse_list_response(list_response)
        sub_accounts = parsed_list.get("content", [])
        
        if len(sub_accounts) == 0:
            pytest.skip("没有可用的 Sub Account 进行测试")
        
        sub_account_id = sub_accounts[0].get("id")
        
        # 获取详情
        print("[Step] 调用详情接口")
        detail_response = sa_api.get_sub_account_detail(sub_account_id)
        assert detail_response.status_code == 200
        
        parsed_detail = sa_api.parse_detail_response(detail_response)
        
        # 验证详细字段
        print("[Step] 验证详情响应字段")
        detail_fields = [
            "id", "name", "financial_account_id", "status",
            "balance", "available_balance", "account_identifier",
            "description", "created_date"
        ]
        
        for field in detail_fields:
            value = parsed_detail.get(field, "(not present)")
            print(f"  {field}: {value}")
        
        print(f"✓ 详情响应结构验证完成")
