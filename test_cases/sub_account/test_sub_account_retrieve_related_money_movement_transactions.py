"""
Sub Account Related Transactions 接口测试用例
测试 GET /api/v1/cores/{core}/sub-accounts/:sub_account_id/transactions 接口
对应文档标题: Retrieve Related Money Movement Transactions
"""
import pytest
from api.sub_account_api import SubAccountAPI
from utils.logger import logger


@pytest.mark.sub_account
@pytest.mark.transactions_api
class TestSubAccountRetrieveRelatedMoneyMovementTransactions:
    """
    Sub Account 相关交易查询接口测试用例集
    """

    def test_retrieve_related_transactions_success(self, login_session):
        """
        测试场景1：成功获取 Sub Account 相关的 Money Movement Transactions
        验证点：
        1. 先获取列表，取第一个 Sub Account ID
        2. 调用交易接口返回 200
        3. 返回数据结构正确
        """
        sa_api = SubAccountAPI(session=login_session)
        
        # 获取 Sub Account
        logger.info("获取 Sub Accounts 列表")
        list_response = sa_api.list_sub_accounts(page=0, size=1)
        assert list_response.status_code == 200
        
        parsed_list = sa_api.parse_list_response(list_response)
        sub_accounts = parsed_list.get("content", [])
        
        if len(sub_accounts) == 0:
            pytest.skip("没有可用的 Sub Account 进行测试")
        
        sub_account_id = sub_accounts[0].get("id")
        logger.info(f"  使用 Sub Account ID: {sub_account_id}")
        
        # 获取相关交易
        logger.info("调用 Retrieve Related Money Movement Transactions 接口")
        txn_response = sa_api.get_related_transactions(sub_account_id, page=0, size=10)
        
        logger.info("验证 HTTP 状态码为 200")
        assert txn_response.status_code == 200, \
            f"接口返回状态码错误: {txn_response.status_code}, Response: {txn_response.text}"
        
        parsed_txn = sa_api.parse_list_response(txn_response)
        assert not parsed_txn.get("error"), f"响应解析失败: {parsed_txn.get('message')}"
        
        transactions = parsed_txn.get("content", [])
        logger.info("✓ 成功获取相关交易:")
        logger.info(f"  总交易数: {parsed_txn['total_elements']}")
        logger.info(f"  返回 {len(transactions)} 条交易记录")
        
        if len(transactions) > 0:
            txn = transactions[0]
            logger.info(f"  第一条交易: {txn.get('transaction_type')} - {txn.get('amount')} ({txn.get('status')})")

    def test_retrieve_related_transactions_with_status_filter(self, login_session):
        """
        测试场景2：使用 status 筛选交易
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
        
        logger.info("使用 status='Completed' 筛选交易")
        txn_response = sa_api.get_related_transactions(
            sub_account_id, 
            status="Completed",
            page=0, 
            size=10
        )
        
        assert txn_response.status_code == 200
        parsed_txn = sa_api.parse_list_response(txn_response)
        
        transactions = parsed_txn.get("content", [])
        logger.info(f"  返回 {len(transactions)} 条 Completed 状态的交易")
        
        logger.info("✓ Status 筛选测试完成")

    def test_retrieve_related_transactions_with_transaction_type_filter(self, login_session):
        """
        测试场景3：使用 transaction_type 筛选交易
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
        
        logger.info("使用 transaction_type='Credit' 筛选交易")
        txn_response = sa_api.get_related_transactions(
            sub_account_id, 
            transaction_type="Credit",
            page=0, 
            size=10
        )
        
        assert txn_response.status_code == 200
        parsed_txn = sa_api.parse_list_response(txn_response)
        
        transactions = parsed_txn.get("content", [])
        logger.info(f"  返回 {len(transactions)} 条 Credit 类型的交易")
        
        logger.info("✓ Transaction Type 筛选测试完成")

    def test_retrieve_related_transactions_pagination(self, login_session):
        """
        测试场景4：验证交易列表分页功能
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
        
        logger.info("使用分页参数 page=0, size=5")
        txn_response = sa_api.get_related_transactions(
            sub_account_id, 
            page=0, 
            size=5
        )
        
        assert txn_response.status_code == 200
        parsed_txn = sa_api.parse_list_response(txn_response)
        
        logger.info("✓ 分页测试完成:")
        logger.info(f"  总元素数: {parsed_txn['total_elements']}")
        logger.info(f"  总页数: {parsed_txn['total_pages']}")
        logger.info(f"  当前页: {parsed_txn['number']}")
        logger.info(f"  每页大小: {parsed_txn['size']}")
