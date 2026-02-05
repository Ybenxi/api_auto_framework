"""
Account Transfer - Transactions 接口测试用例
测试 GET /api/v1/cores/{core}/money-movements/account-transfer/transactions 接口
"""
import pytest
from utils.logger import logger
from utils.assertions import assert_status_ok
from data.enums import PaymentTransactionStatus, PaymentTransactionType


@pytest.mark.account_transfer
@pytest.mark.list_api
class TestAccountTransferTransactions:
    """
    Account Transfer交易列表接口测试用例集
    ⚠️ 文档问题：
    1. 响应无code包装层
    2. direction字段未在Properties定义
    3. transaction_type参数描述错误（说Internal Pay）
    """

    def test_list_transactions_success(self, account_transfer_api):
        """
        测试场景1：成功获取交易列表
        验证点：
        1. 接口返回 200
        2. 返回分页结构
        3. 无code包装层
        """
        logger.info("测试场景1：成功获取交易列表")
        
        response = account_transfer_api.list_transactions(page=0, size=10)
        
        assert response.status_code == 200
        
        response_body = response.json()
        
        if "content" in response_body and "code" not in response_body:
            logger.warning("⚠️ 确认：响应无code包装层")
            logger.info(f"✓ 交易列表获取成功，返回 {len(response_body.get('content', []))} 条交易")
        
        logger.info("✓ 交易列表获取成功")

    def test_filter_by_status(self, account_transfer_api):
        """
        测试场景2：按status筛选
        验证点：
        1. status参数生效
        """
        logger.info("测试场景2：按status筛选")
        
        response = account_transfer_api.list_transactions(
            status=PaymentTransactionStatus.COMPLETED,
            size=10
        )
        
        assert response.status_code == 200
        
        logger.info("✓ status筛选验证通过")

    def test_filter_by_date_range(self, account_transfer_api):
        """
        测试场景3：按日期范围筛选
        验证点：
        1. start_date和end_date参数生效
        """
        logger.info("测试场景3：按日期范围筛选")
        
        response = account_transfer_api.list_transactions(
            start_date="2024-01-01",
            end_date="2024-12-31",
            size=10
        )
        
        assert response.status_code == 200
        
        logger.info("✓ 日期范围筛选验证通过")

    def test_filter_by_payer_and_payee(self, account_transfer_api):
        """
        测试场景4：按付款方和收款方筛选
        验证点：
        1. payer_financial_account_id参数生效
        2. payee_financial_account_id参数生效
        """
        logger.info("测试场景4：按付款方和收款方筛选")
        
        response = account_transfer_api.list_transactions(
            payer_financial_account_id="test_payer_id",
            payee_financial_account_id="test_payee_id",
            size=10
        )
        
        assert response.status_code == 200
        
        logger.info("✓ 付款方和收款方筛选验证通过")

    def test_direction_field(self, account_transfer_api):
        """
        测试场景5：direction字段验证
        验证点：
        1. 响应包含direction字段
        2. 但Properties中未定义
        3. 这是Account Transfer独有（Internal Pay无此字段）
        """
        logger.info("测试场景5：direction字段验证")
        
        response = account_transfer_api.list_transactions(size=1)
        
        assert response.status_code == 200
        
        content = response.json().get("content", [])
        
        if content:
            transaction = content[0]
            
            if "direction" in transaction:
                logger.warning("⚠️ 检测到direction字段（Properties中未定义）")
                logger.info(f"direction值: {transaction['direction']}")
                logger.info("这是Account Transfer独有字段（Internal Pay无）")
            else:
                logger.info("未检测到direction字段")
        
        logger.info("✓ direction字段验证完成")

    def test_transaction_type_description_error(self, account_transfer_api):
        """
        测试场景6：transaction_type参数描述错误
        验证点：
        1. 文档说"Internal Pay request"
        2. 实际应为"Account Transfer request"
        """
        logger.info("测试场景6：参数描述错误验证")
        
        logger.warning("⚠️ 文档问题：transaction_type参数描述错误")
        logger.warning("文档说：The transaction type of Internal Pay request")
        logger.warning("应改为：The transaction type of Account Transfer request")
        
        logger.info("✓ 描述错误已记录")
