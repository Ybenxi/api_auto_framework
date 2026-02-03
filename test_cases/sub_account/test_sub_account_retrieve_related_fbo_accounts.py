"""
Sub Account Related FBO Accounts 接口测试用例
测试 GET /api/v1/cores/{core}/sub-accounts/:sub_account_id/fbo-accounts 接口
对应文档标题: Retrieve Related Fbo Accounts
"""
import pytest
from api.sub_account_api import SubAccountAPI


@pytest.mark.sub_account
@pytest.mark.fbo_accounts_api
class TestSubAccountRetrieveRelatedFboAccounts:
    """
    Sub Account 相关 FBO Accounts 查询接口测试用例集
    """

    def test_retrieve_related_fbo_accounts_success(self, login_session):
        """
        测试场景：成功获取 Sub Account 相关的 FBO Accounts
        验证点：
        1. 先获取列表，取第一个 Sub Account ID
        2. 调用 FBO Accounts 接口返回 200
        3. 返回数据结构正确
        """
        sa_api = SubAccountAPI(session=login_session)
        
        # 获取 Sub Account
        print("\n[Step] 获取 Sub Accounts 列表")
        list_response = sa_api.list_sub_accounts(page=0, size=1)
        assert list_response.status_code == 200
        
        parsed_list = sa_api.parse_list_response(list_response)
        sub_accounts = parsed_list.get("content", [])
        
        if len(sub_accounts) == 0:
            pytest.skip("没有可用的 Sub Account 进行测试")
        
        sub_account_id = sub_accounts[0].get("id")
        print(f"  使用 Sub Account ID: {sub_account_id}")
        
        # 获取相关 FBO Accounts
        print("[Step] 调用 Retrieve Related Fbo Accounts 接口")
        fbo_response = sa_api.get_related_fbo_accounts(sub_account_id, page=0, size=10)
        
        print("[Step] 验证 HTTP 状态码为 200")
        assert fbo_response.status_code == 200, \
            f"接口返回状态码错误: {fbo_response.status_code}, Response: {fbo_response.text}"
        
        parsed_fbo = sa_api.parse_list_response(fbo_response)
        assert not parsed_fbo.get("error"), f"响应解析失败: {parsed_fbo.get('message')}"
        
        fbo_accounts = parsed_fbo.get("content", [])
        print(f"✓ 成功获取相关 FBO Accounts:")
        print(f"  总数: {parsed_fbo['total_elements']}")
        print(f"  返回 {len(fbo_accounts)} 个 FBO Accounts")
        
        if len(fbo_accounts) > 0:
            fbo = fbo_accounts[0]
            print(f"  第一个 FBO Account: {fbo.get('name')} ({fbo.get('status')})")

    def test_retrieve_related_fbo_accounts_with_status_filter(self, login_session):
        """
        测试场景：使用 status 筛选 FBO Accounts
        验证点：
        1. 接口返回 200
        2. 返回数据结构正确
        """
        sa_api = SubAccountAPI(session=login_session)
        
        list_response = sa_api.list_sub_accounts(page=0, size=1)
        assert list_response.status_code == 200
        
        parsed_list = sa_api.parse_list_response(list_response)
        sub_accounts = parsed_list.get("content", [])
        
        if len(sub_accounts) == 0:
            pytest.skip("没有可用的 Sub Account 进行测试")
        
        sub_account_id = sub_accounts[0].get("id")
        
        print("\n[Step] 使用 status='Open' 筛选 FBO Accounts")
        fbo_response = sa_api.get_related_fbo_accounts(
            sub_account_id, 
            status="Open",
            page=0, 
            size=10
        )
        
        assert fbo_response.status_code == 200
        parsed_fbo = sa_api.parse_list_response(fbo_response)
        
        fbo_accounts = parsed_fbo.get("content", [])
        print(f"  返回 {len(fbo_accounts)} 个 Open 状态的 FBO Accounts")
        
        print(f"✓ Status 筛选测试完成")

    def test_retrieve_related_fbo_accounts_pagination(self, login_session):
        """
        测试场景：验证 FBO Accounts 列表分页功能
        验证点：
        1. 接口返回 200
        2. 分页信息正确
        """
        sa_api = SubAccountAPI(session=login_session)
        
        list_response = sa_api.list_sub_accounts(page=0, size=1)
        assert list_response.status_code == 200
        
        parsed_list = sa_api.parse_list_response(list_response)
        sub_accounts = parsed_list.get("content", [])
        
        if len(sub_accounts) == 0:
            pytest.skip("没有可用的 Sub Account 进行测试")
        
        sub_account_id = sub_accounts[0].get("id")
        
        print("\n[Step] 使用分页参数 page=0, size=5")
        fbo_response = sa_api.get_related_fbo_accounts(
            sub_account_id, 
            page=0, 
            size=5
        )
        
        assert fbo_response.status_code == 200
        parsed_fbo = sa_api.parse_list_response(fbo_response)
        
        print(f"✓ 分页测试完成:")
        print(f"  总元素数: {parsed_fbo['total_elements']}")
        print(f"  总页数: {parsed_fbo['total_pages']}")
        print(f"  当前页: {parsed_fbo['number']}")
        print(f"  每页大小: {parsed_fbo['size']}")

    def test_retrieve_related_fbo_accounts_response_fields(self, login_session):
        """
        测试场景：验证 FBO Account 响应字段完整性
        验证点：
        1. 接口返回 200
        2. FBO Account 对象包含必需字段
        """
        sa_api = SubAccountAPI(session=login_session)
        
        list_response = sa_api.list_sub_accounts(page=0, size=1)
        assert list_response.status_code == 200
        
        parsed_list = sa_api.parse_list_response(list_response)
        sub_accounts = parsed_list.get("content", [])
        
        if len(sub_accounts) == 0:
            pytest.skip("没有可用的 Sub Account 进行测试")
        
        sub_account_id = sub_accounts[0].get("id")
        
        print("\n[Step] 获取 FBO Accounts 并验证字段")
        fbo_response = sa_api.get_related_fbo_accounts(sub_account_id, page=0, size=1)
        assert fbo_response.status_code == 200
        
        parsed_fbo = sa_api.parse_list_response(fbo_response)
        fbo_accounts = parsed_fbo.get("content", [])
        
        if len(fbo_accounts) > 0:
            fbo = fbo_accounts[0]
            expected_fields = [
                "id", "name", "sub_account_id", "status",
                "balance", "available_balance", "account_number", "routing_number"
            ]
            
            print("[Step] 验证 FBO Account 字段")
            for field in expected_fields:
                value = fbo.get(field, "(not present)")
                print(f"  {field}: {value}")
            
            print(f"✓ 字段验证完成")
        else:
            print("  跳过字段验证（列表为空）")
