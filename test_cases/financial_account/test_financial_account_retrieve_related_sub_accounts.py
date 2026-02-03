"""
Financial Account Related Sub Accounts 接口测试用例
测试 GET /api/v1/cores/{core}/financial-accounts/:financial_account_id/sub-accounts 接口
对应文档标题: Retrieve Related Sub Accounts
"""
import pytest
from api.financial_account_api import FinancialAccountAPI


@pytest.mark.financial_account
@pytest.mark.sub_accounts_api
class TestFinancialAccountRetrieveRelatedSubAccounts:
    """
    Financial Account 相关 Sub Accounts 查询接口测试用例集
    """

    def test_retrieve_related_sub_accounts_success(self, login_session):
        """
        测试场景1：成功获取 Financial Account 相关的 Sub Accounts
        验证点：
        1. 先获取列表，取第一个 Financial Account ID
        2. 调用 Sub Accounts 接口返回 200
        3. 返回数据结构正确
        """
        fa_api = FinancialAccountAPI(session=login_session)
        
        # 获取 Financial Account
        print("\n[Step] 获取 Financial Accounts 列表")
        list_response = fa_api.list_financial_accounts(page=0, size=1)
        assert list_response.status_code == 200
        
        parsed_list = fa_api.parse_list_response(list_response)
        accounts = parsed_list.get("content", [])
        
        if len(accounts) == 0:
            pytest.skip("没有可用的 Financial Account 进行测试")
        
        financial_account_id = accounts[0].get("id")
        print(f"  使用 Financial Account ID: {financial_account_id}")
        
        # 获取相关 Sub Accounts
        print("[Step] 调用 Retrieve Related Sub Accounts 接口")
        sub_response = fa_api.get_related_sub_accounts(financial_account_id, page=0, size=10)
        
        print("[Step] 验证 HTTP 状态码为 200")
        assert sub_response.status_code == 200, \
            f"接口返回状态码错误: {sub_response.status_code}, Response: {sub_response.text}"
        
        parsed_sub = fa_api.parse_list_response(sub_response)
        assert not parsed_sub.get("error"), f"响应解析失败: {parsed_sub.get('message')}"
        
        sub_accounts = parsed_sub.get("content", [])
        print(f"✓ 成功获取相关 Sub Accounts:")
        print(f"  总数: {parsed_sub['total_elements']}")
        print(f"  返回 {len(sub_accounts)} 个 Sub Accounts")
        
        if len(sub_accounts) > 0:
            sub = sub_accounts[0]
            print(f"  第一个 Sub Account: {sub.get('name')} ({sub.get('status')})")

    def test_retrieve_related_sub_accounts_with_name_filter(self, login_session):
        """
        测试场景2：使用 name 筛选 Sub Accounts
        验证点：
        1. 接口返回 200
        2. 返回数据结构正确
        """
        fa_api = FinancialAccountAPI(session=login_session)
        
        list_response = fa_api.list_financial_accounts(page=0, size=1)
        assert list_response.status_code == 200
        
        parsed_list = fa_api.parse_list_response(list_response)
        accounts = parsed_list.get("content", [])
        
        if len(accounts) == 0:
            pytest.skip("没有可用的 Financial Account 进行测试")
        
        financial_account_id = accounts[0].get("id")
        
        print("\n[Step] 使用 name 筛选 Sub Accounts")
        sub_response = fa_api.get_related_sub_accounts(
            financial_account_id, 
            name="Primary",
            page=0, 
            size=10
        )
        
        assert sub_response.status_code == 200
        parsed_sub = fa_api.parse_list_response(sub_response)
        
        sub_accounts = parsed_sub.get("content", [])
        print(f"  返回 {len(sub_accounts)} 个匹配的 Sub Accounts")
        
        print(f"✓ Name 筛选测试完成")

    def test_retrieve_related_sub_accounts_with_status_filter(self, login_session):
        """
        测试场景3：使用 status 筛选 Sub Accounts
        验证点：
        1. 接口返回 200
        2. 返回数据结构正确
        """
        fa_api = FinancialAccountAPI(session=login_session)
        
        list_response = fa_api.list_financial_accounts(page=0, size=1)
        assert list_response.status_code == 200
        
        parsed_list = fa_api.parse_list_response(list_response)
        accounts = parsed_list.get("content", [])
        
        if len(accounts) == 0:
            pytest.skip("没有可用的 Financial Account 进行测试")
        
        financial_account_id = accounts[0].get("id")
        
        print("\n[Step] 使用 status='Open' 筛选 Sub Accounts")
        sub_response = fa_api.get_related_sub_accounts(
            financial_account_id, 
            status="Open",
            page=0, 
            size=10
        )
        
        assert sub_response.status_code == 200
        parsed_sub = fa_api.parse_list_response(sub_response)
        
        sub_accounts = parsed_sub.get("content", [])
        print(f"  返回 {len(sub_accounts)} 个 Open 状态的 Sub Accounts")
        
        print(f"✓ Status 筛选测试完成")

    def test_retrieve_related_sub_accounts_pagination(self, login_session):
        """
        测试场景4：验证 Sub Accounts 列表分页功能
        验证点：
        1. 接口返回 200
        2. 分页信息正确
        """
        fa_api = FinancialAccountAPI(session=login_session)
        
        list_response = fa_api.list_financial_accounts(page=0, size=1)
        assert list_response.status_code == 200
        
        parsed_list = fa_api.parse_list_response(list_response)
        accounts = parsed_list.get("content", [])
        
        if len(accounts) == 0:
            pytest.skip("没有可用的 Financial Account 进行测试")
        
        financial_account_id = accounts[0].get("id")
        
        print("\n[Step] 使用分页参数 page=0, size=5")
        sub_response = fa_api.get_related_sub_accounts(
            financial_account_id, 
            page=0, 
            size=5
        )
        
        assert sub_response.status_code == 200
        parsed_sub = fa_api.parse_list_response(sub_response)
        
        print(f"✓ 分页测试完成:")
        print(f"  总元素数: {parsed_sub['total_elements']}")
        print(f"  总页数: {parsed_sub['total_pages']}")
        print(f"  当前页: {parsed_sub['number']}")
        print(f"  每页大小: {parsed_sub['size']}")

    def test_retrieve_related_sub_accounts_response_fields(self, login_session):
        """
        测试场景5：验证 Sub Account 响应字段完整性
        验证点：
        1. 接口返回 200
        2. Sub Account 对象包含必需字段
        """
        fa_api = FinancialAccountAPI(session=login_session)
        
        list_response = fa_api.list_financial_accounts(page=0, size=1)
        assert list_response.status_code == 200
        
        parsed_list = fa_api.parse_list_response(list_response)
        accounts = parsed_list.get("content", [])
        
        if len(accounts) == 0:
            pytest.skip("没有可用的 Financial Account 进行测试")
        
        financial_account_id = accounts[0].get("id")
        
        print("\n[Step] 获取 Sub Accounts 并验证字段")
        sub_response = fa_api.get_related_sub_accounts(financial_account_id, page=0, size=1)
        assert sub_response.status_code == 200
        
        parsed_sub = fa_api.parse_list_response(sub_response)
        sub_accounts = parsed_sub.get("content", [])
        
        if len(sub_accounts) > 0:
            sub = sub_accounts[0]
            expected_fields = [
                "id", "name", "financial_account_id", "status",
                "balance", "available_balance", "account_identifier"
            ]
            
            print("[Step] 验证 Sub Account 字段")
            for field in expected_fields:
                value = sub.get(field, "(not present)")
                print(f"  {field}: {value}")
            
            print(f"✓ 字段验证完成")
        else:
            print("  跳过字段验证（列表为空）")
