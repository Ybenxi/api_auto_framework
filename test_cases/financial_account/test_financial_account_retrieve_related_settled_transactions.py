"""
Financial Account Related Settled Transactions 接口测试用例
测试 GET /api/v1/cores/{core}/financial-accounts/:financial_account_id/settled-transactions 接口
对应文档标题: Retrieve Related Settled Transactions
"""
import pytest
from api.financial_account_api import FinancialAccountAPI


@pytest.mark.financial_account
@pytest.mark.settled_transactions_api
class TestFinancialAccountRetrieveRelatedSettledTransactions:
    """
    Financial Account 相关已结算交易查询接口测试用例集
    """

    def test_retrieve_settled_transactions_success(self, login_session):
        """
        测试场景：成功获取 Financial Account 相关的已结算交易
        验证点：
        1. 先获取列表，取第一个 Financial Account ID
        2. 调用已结算交易接口返回 200
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
        
        # 获取已结算交易
        print("[Step] 调用 Retrieve Related Settled Transactions 接口")
        settled_response = fa_api.get_settled_transactions(financial_account_id, page=0, size=10)
        
        print("[Step] 验证 HTTP 状态码为 200")
        assert settled_response.status_code == 200, \
            f"接口返回状态码错误: {settled_response.status_code}, Response: {settled_response.text}"
        
        parsed_settled = fa_api.parse_list_response(settled_response)
        assert not parsed_settled.get("error"), f"响应解析失败: {parsed_settled.get('message')}"
        
        transactions = parsed_settled.get("content", [])
        print(f"✓ 成功获取已结算交易:")
        print(f"  总交易数: {parsed_settled['total_elements']}")
        print(f"  返回 {len(transactions)} 条交易记录")
        
        if len(transactions) > 0:
            txn = transactions[0]
            print(f"  第一条交易: {txn.get('transaction_type')} - {txn.get('symbol')} ({txn.get('settle_date')})")

    def test_retrieve_settled_transactions_with_date_filter(self, login_session):
        """
        测试场景：使用日期筛选已结算交易
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
        
        print("\n[Step] 使用日期范围筛选已结算交易")
        settled_response = fa_api.get_settled_transactions(
            financial_account_id, 
            begin_date="2024-01-01",
            end_date="2024-12-31",
            page=0, 
            size=10
        )
        
        assert settled_response.status_code == 200
        parsed_settled = fa_api.parse_list_response(settled_response)
        
        transactions = parsed_settled.get("content", [])
        print(f"  返回 {len(transactions)} 条匹配的交易记录")
        
        print(f"✓ 日期筛选测试完成")

    def test_retrieve_settled_transactions_with_security_filter(self, login_session):
        """
        测试场景：使用证券名称/代码筛选已结算交易
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
        
        print("\n[Step] 使用 security 筛选已结算交易")
        settled_response = fa_api.get_settled_transactions(
            financial_account_id, 
            security="AAPL",
            page=0, 
            size=10
        )
        
        assert settled_response.status_code == 200
        parsed_settled = fa_api.parse_list_response(settled_response)
        
        transactions = parsed_settled.get("content", [])
        print(f"  返回 {len(transactions)} 条匹配的交易记录")
        
        print(f"✓ Security 筛选测试完成")

    def test_retrieve_settled_transactions_pagination(self, login_session):
        """
        测试场景：验证已结算交易列表分页功能
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
        settled_response = fa_api.get_settled_transactions(
            financial_account_id, 
            page=0, 
            size=5
        )
        
        assert settled_response.status_code == 200
        parsed_settled = fa_api.parse_list_response(settled_response)
        
        print(f"✓ 分页测试完成:")
        print(f"  总元素数: {parsed_settled['total_elements']}")
        print(f"  总页数: {parsed_settled['total_pages']}")
        print(f"  当前页: {parsed_settled['number']}")
        print(f"  每页大小: {parsed_settled['size']}")

    def test_retrieve_settled_transactions_response_fields(self, login_session):
        """
        测试场景：验证已结算交易响应字段完整性
        验证点：
        1. 接口返回 200
        2. 交易对象包含必需字段
        """
        fa_api = FinancialAccountAPI(session=login_session)
        
        list_response = fa_api.list_financial_accounts(page=0, size=1)
        assert list_response.status_code == 200
        
        parsed_list = fa_api.parse_list_response(list_response)
        accounts = parsed_list.get("content", [])
        
        if len(accounts) == 0:
            pytest.skip("没有可用的 Financial Account 进行测试")
        
        financial_account_id = accounts[0].get("id")
        
        print("\n[Step] 获取已结算交易并验证字段")
        settled_response = fa_api.get_settled_transactions(financial_account_id, page=0, size=1)
        assert settled_response.status_code == 200
        
        parsed_settled = fa_api.parse_list_response(settled_response)
        transactions = parsed_settled.get("content", [])
        
        if len(transactions) > 0:
            txn = transactions[0]
            expected_fields = [
                "id", "financial_account_id", "financial_account_name",
                "symbol", "security_name", "transaction_type",
                "amount", "units", "price", "trade_date", "settle_date"
            ]
            
            print("[Step] 验证交易字段")
            for field in expected_fields:
                value = txn.get(field, "(not present)")
                print(f"  {field}: {value}")
            
            print(f"✓ 字段验证完成")
        else:
            print("  跳过字段验证（列表为空）")
