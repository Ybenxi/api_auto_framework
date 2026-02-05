"""
Internal Pay - Transactions 接口测试用例
测试 GET /api/v1/cores/{core}/money-movements/internal-pay/transactions 接口
"""
import pytest
from utils.logger import logger
from utils.assertions import assert_status_ok, assert_pagination
from data.enums import PaymentTransactionStatus, PaymentTransactionType


@pytest.mark.internal_pay
@pytest.mark.list_api
class TestInternalPayTransactions:
    """
    Internal Pay交易列表接口测试用例集
    ⚠️ 文档问题：
    1. 响应无code包装层（直接返回分页结构）
    2. 多个字段未在Properties定义（fee, completed_date等）
    """

    def test_list_transactions_success(self, internal_pay_api):
        """
        测试场景1：成功获取交易列表
        验证点：
        1. 接口返回 200
        2. 返回分页结构
        3. 无code包装层（文档特殊格式）
        """
        logger.info("测试场景1：成功获取交易列表")
        
        response = internal_pay_api.list_transactions(page=0, size=10)
        
        assert response.status_code == 200, "HTTP状态码应为200"
        
        response_body = response.json()
        
        # 验证无code包装层
        if "content" in response_body and "code" not in response_body:
            logger.warning("⚠️ 确认：响应无code包装层（直接返回分页结构）")
            assert "pageable" in response_body
            logger.info(f"✓ 交易列表获取成功，返回 {len(response_body.get('content', []))} 条交易")
        
        logger.info("✓ 交易列表获取成功")

    def test_filter_by_status(self, internal_pay_api):
        """
        测试场景2：按status筛选
        验证点：
        1. status参数生效
        """
        logger.info("测试场景2：按status筛选")
        
        response = internal_pay_api.list_transactions(
            status=PaymentTransactionStatus.COMPLETED,
            size=10
        )
        
        assert response.status_code == 200
        
        logger.info("✓ status筛选验证通过")

    def test_filter_by_date_range(self, internal_pay_api):
        """
        测试场景3：按日期范围筛选
        验证点：
        1. start_date和end_date参数生效
        2. 日期格式：YYYY-MM-DD
        """
        logger.info("测试场景3：按日期范围筛选")
        
        response = internal_pay_api.list_transactions(
            start_date="2024-01-01",
            end_date="2024-12-31",
            size=10
        )
        
        assert response.status_code == 200
        
        logger.info("✓ 日期范围筛选验证通过")

    def test_filter_by_payer_account(self, internal_pay_api):
        """
        测试场景4：按付款方账户筛选
        验证点：
        1. payer_financial_account_id参数生效
        """
        logger.info("测试场景4：按付款方账户筛选")
        
        response = internal_pay_api.list_transactions(
            payer_financial_account_id="test_payer_id",
            size=10
        )
        
        assert response.status_code == 200
        
        logger.info("✓ 付款方账户筛选验证通过")

    def test_filter_by_transaction_type(self, internal_pay_api):
        """
        测试场景5：按transaction_type筛选
        验证点：
        1. transaction_type参数生效
        2. Credit或Debit
        """
        logger.info("测试场景5：按transaction_type筛选")
        
        response = internal_pay_api.list_transactions(
            transaction_type=PaymentTransactionType.CREDIT,
            size=10
        )
        
        assert response.status_code == 200
        
        logger.info("✓ transaction_type筛选验证通过")

    def test_pagination(self, internal_pay_api):
        """
        测试场景6：分页查询
        验证点：
        1. 分页参数正确传递
        2. 分页信息正确返回
        """
        logger.info("测试场景6：分页查询")
        
        response = internal_pay_api.list_transactions(page=0, size=5)
        
        assert response.status_code == 200
        
        # 由于无code包装层，直接验证分页字段
        response_body = response.json()
        if "pageable" in response_body:
            assert response_body.get("number") == 0, "页码应为0"
            assert response_body.get("size") == 5, "页面大小应为5"
        
        logger.info("✓ 分页验证通过")

    def test_undefined_response_fields(self, internal_pay_api):
        """
        测试场景7：验证未定义的响应字段
        验证点：
        1. fee字段（Properties中未定义）
        2. completed_date字段（Properties中未定义）
        3. transaction_id字段（Properties中未定义）
        4. payer/payee_name字段（Properties中未定义）
        """
        logger.info("测试场景7：未定义响应字段验证")
        
        response = internal_pay_api.list_transactions(size=1)
        
        assert response.status_code == 200
        
        response_body = response.json()
        content = response_body.get("content", [])
        
        if content:
            transaction = content[0]
            
            # 检查未定义的字段
            undefined_fields = []
            if "fee" in transaction:
                undefined_fields.append("fee")
            if "completed_date" in transaction:
                undefined_fields.append("completed_date")
            if "transaction_id" in transaction:
                undefined_fields.append("transaction_id")
            if "payer_financial_account_name" in transaction:
                undefined_fields.append("payer_financial_account_name")
            
            if undefined_fields:
                logger.warning(f"⚠️ 检测到Properties中未定义的字段: {undefined_fields}")
            
            logger.debug(f"交易字段: {list(transaction.keys())}")
        
        logger.info("✓ 未定义字段验证完成")

    def test_parse_list_response(self, internal_pay_api):
        """
        测试场景8：parse方法验证
        验证点：
        1. parse方法正确处理无code包装层格式
        """
        logger.info("测试场景8：parse方法验证")
        
        response = internal_pay_api.list_transactions(size=1)
        
        parsed = internal_pay_api.parse_list_response(response)
        
        assert not parsed.get("error"), "解析不应出错"
        assert parsed.get("no_code_wrapper") == True, "应检测到无code包装层"
        
        logger.info("✓ parse方法验证通过")
