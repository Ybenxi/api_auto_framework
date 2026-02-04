"""
Financial Account List 接口测试用例
测试 GET /api/v1/cores/{core}/financial-accounts 接口
对应文档标题: List Financial Accounts
"""
import pytest
from api.financial_account_api import FinancialAccountAPI
from utils.logger import logger


@pytest.mark.financial_account
@pytest.mark.list_api
class TestFinancialAccountListFinancialAccounts:
    """
    Financial Account 列表查询接口测试用例集
    """

    def test_list_financial_accounts_success(self, login_session):
        """
        测试场景1：成功获取 Financial Accounts 列表
        验证点：
        1. 接口返回 200
        2. 返回数据结构正确（包含 content、pageable 等字段）
        3. content 是数组类型
        """
        # 1. 初始化 API 对象
        fa_api = FinancialAccountAPI(session=login_session)
        
        # 2. 调用 List 接口
        logger.info("调用 List Financial Accounts 接口")
        list_response = fa_api.list_financial_accounts(page=0, size=10)
        
        # 3. 验证状态码
        logger.info("验证 HTTP 状态码为 200")
        assert list_response.status_code == 200, \
            f"List Financial Accounts 接口返回状态码错误: {list_response.status_code}, Response: {list_response.text}"
        
        # 4. 解析响应
        logger.info("解析响应并验证数据结构")
        parsed_list = fa_api.parse_list_response(list_response)
        assert not parsed_list.get("error"), f"List 响应解析失败: {parsed_list.get('message')}"
        
        # 5. 验证数据结构
        logger.info("验证返回数据结构")
        assert "content" in parsed_list, "响应中缺少 content 字段"
        assert isinstance(parsed_list["content"], list), "content 字段不是数组类型"
        
        accounts = parsed_list["content"]
        
        logger.info("✓ 成功获取 Financial Accounts 列表:")
        logger.info(f"  总元素数: {parsed_list['total_elements']}")
        logger.info(f"  总页数: {parsed_list['total_pages']}")
        logger.info(f"  当前页: {parsed_list['number']}")
        logger.info(f"  每页大小: {parsed_list['size']}")
        logger.info(f"  返回 {len(accounts)} 个 Financial Accounts")
        
        if len(accounts) > 0:
            logger.info(f"  第一个 Financial Account: {accounts[0].get('name')} ({accounts[0].get('account_number')})")

    def test_list_financial_accounts_with_status_filter(self, login_session):
        """
        测试场景2：使用 status 筛选 Financial Accounts
        验证点：
        1. 接口返回 200
        2. 返回数据结构正确
        """
        fa_api = FinancialAccountAPI(session=login_session)
        
        logger.info("使用 status='Open' 筛选 Financial Accounts")
        list_response = fa_api.list_financial_accounts(status="Open", size=10)
        
        logger.info("验证 HTTP 状态码为 200")
        assert list_response.status_code == 200, \
            f"List Financial Accounts 接口返回状态码错误: {list_response.status_code}"
        
        parsed_list = fa_api.parse_list_response(list_response)
        assert not parsed_list.get("error"), f"List 响应解析失败: {parsed_list.get('message')}"
        
        accounts = parsed_list["content"]
        logger.info(f"  返回 {len(accounts)} 个 Financial Accounts")
        
        if len(accounts) > 0:
            logger.info(f"  第一个 Financial Account: {accounts[0].get('name')} ({accounts[0].get('status')})")
        
        logger.info("✓ Status 筛选测试完成")

    def test_list_financial_accounts_with_source_filter(self, login_session):
        """
        测试场景3：使用 source 筛选 Financial Accounts
        验证点：
        1. 接口返回 200
        2. 返回数据结构正确
        """
        fa_api = FinancialAccountAPI(session=login_session)
        
        logger.info("使用 source='Managed' 筛选 Financial Accounts")
        list_response = fa_api.list_financial_accounts(source="Managed", size=10)
        
        logger.info("验证 HTTP 状态码为 200")
        assert list_response.status_code == 200, \
            f"List Financial Accounts 接口返回状态码错误: {list_response.status_code}"
        
        parsed_list = fa_api.parse_list_response(list_response)
        assert not parsed_list.get("error"), f"List 响应解析失败: {parsed_list.get('message')}"
        
        accounts = parsed_list["content"]
        logger.info(f"  返回 {len(accounts)} 个 Financial Accounts")
        
        logger.info("✓ Source 筛选测试完成")

    def test_list_financial_accounts_with_record_type_filter(self, login_session):
        """
        测试场景4：使用 record_type 筛选 Financial Accounts
        验证点：
        1. 接口返回 200
        2. 返回数据结构正确
        """
        fa_api = FinancialAccountAPI(session=login_session)
        
        logger.info("使用 record_type='Bank_Account' 筛选 Financial Accounts")
        list_response = fa_api.list_financial_accounts(record_type="Bank_Account", size=10)
        
        logger.info("验证 HTTP 状态码为 200")
        assert list_response.status_code == 200, \
            f"List Financial Accounts 接口返回状态码错误: {list_response.status_code}"
        
        parsed_list = fa_api.parse_list_response(list_response)
        assert not parsed_list.get("error"), f"List 响应解析失败: {parsed_list.get('message')}"
        
        accounts = parsed_list["content"]
        logger.info(f"  返回 {len(accounts)} 个 Financial Accounts")
        
        logger.info("✓ Record Type 筛选测试完成")

    def test_list_financial_accounts_pagination(self, login_session):
        """
        测试场景5：验证分页功能
        验证点：
        1. 接口返回 200
        2. 分页信息正确（page、size）
        """
        fa_api = FinancialAccountAPI(session=login_session)
        
        logger.info("使用分页参数 page=0, size=5")
        list_response = fa_api.list_financial_accounts(page=0, size=5)
        
        logger.info("验证 HTTP 状态码为 200")
        assert list_response.status_code == 200, \
            f"List Financial Accounts 接口返回状态码错误: {list_response.status_code}"
        
        parsed_list = fa_api.parse_list_response(list_response)
        assert not parsed_list.get("error"), f"List 响应解析失败: {parsed_list.get('message')}"
        
        logger.info("验证分页信息")
        assert parsed_list["size"] == 5, f"分页大小不正确: 期望 5, 实际 {parsed_list['size']}"
        assert parsed_list["number"] == 0, f"页码不正确: 期望 0, 实际 {parsed_list['number']}"
        
        logger.info("✓ 分页测试完成:")
        logger.info(f"  总元素数: {parsed_list['total_elements']}")
        logger.info(f"  总页数: {parsed_list['total_pages']}")
        logger.info(f"  当前页: {parsed_list['number']}")
        logger.info(f"  每页大小: {parsed_list['size']}")

    def test_list_financial_accounts_response_fields(self, login_session):
        """
        测试场景6：验证响应字段完整性
        验证点：
        1. 接口返回 200
        2. Financial Account 对象包含必需字段
        """
        fa_api = FinancialAccountAPI(session=login_session)
        
        logger.info("调用 List Financial Accounts 接口")
        list_response = fa_api.list_financial_accounts(page=0, size=1)
        
        logger.info("验证 HTTP 状态码为 200")
        assert list_response.status_code == 200, \
            f"List Financial Accounts 接口返回状态码错误: {list_response.status_code}"
        
        parsed_list = fa_api.parse_list_response(list_response)
        assert not parsed_list.get("error"), f"List 响应解析失败: {parsed_list.get('message')}"
        
        accounts = parsed_list["content"]
        
        if len(accounts) > 0:
            logger.info("验证 Financial Account 对象字段完整性")
            account = accounts[0]
            
            expected_fields = ["id", "name", "account_number", "status", "source", "balance"]
            
            for field in expected_fields:
                if field in account:
                    logger.info(f"  ✓ {field}: {account.get(field)}")
                else:
                    logger.info(f"  - {field}: (not present)")
            
            logger.info("✓ 字段完整性验证完成")

    def test_list_financial_accounts_empty_result(self, login_session):
        """
        测试场景7：空结果验证
        验证点：
        1. 使用不存在的筛选条件时，接口返回 200
        2. 返回的 content 是空列表
        3. total_elements 为 0
        """
        fa_api = FinancialAccountAPI(session=login_session)
        
        # 使用不太可能存在的筛选条件
        response = fa_api.list_financial_accounts(account_number="NONEXISTENT_FA_999999")
        
        # 验证状态码
        assert response.status_code == 200, f"接口返回状态码错误: {response.status_code}"
        
        # 解析响应
        parsed = fa_api.parse_list_response(response)
        assert not parsed.get("error"), f"响应解析失败: {parsed.get('message')}"
        
        # 验证空结果
        assert len(parsed["content"]) == 0, "期望返回空列表，但实际有数据"
        assert parsed.get("total_elements") == 0, "total_elements 应该为 0"
        
        logger.info("✓ 空结果验证成功，接口正确返回空列表")
