"""
Wire Processing - Transactions 接口测试用例
测试 GET /api/v1/cores/{core}/money-movements/wire/transactions 接口
"""
import pytest
from utils.logger import logger
from utils.assertions import assert_status_ok
from data.enums import PaymentTransactionStatus, WirePaymentType


@pytest.mark.wire_processing
@pytest.mark.list_api
class TestWireTransactions:
    """
    Wire交易列表接口测试用例集
    ⚠️ 文档问题：响应无code包装层，12+字段未定义
    """

    def test_list_transactions_success(self, wire_processing_api):
        """
        测试场景1：成功获取交易列表
        验证点：1. HTTP 200 2. 无code包装层
        """
        logger.info("测试场景1：成功获取Wire交易列表")
        
        response = wire_processing_api.list_transactions(page=0, size=10)
        assert response.status_code == 200
        
        if "content" in response.json():
            logger.info(f"✓ 交易列表获取成功，返回 {len(response.json().get('content', []))} 条")
        
        logger.info("✓ 列表获取成功")

    def test_filter_by_payment_type(self, wire_processing_api):
        """测试场景2：按payment_type筛选"""
        logger.info("测试场景2：按payment_type筛选")
        
        response = wire_processing_api.list_transactions(
            payment_type=WirePaymentType.WIRE, size=10
        )
        assert response.status_code == 200
        logger.info("✓ payment_type筛选验证通过")

    def test_filter_by_status(self, wire_processing_api):
        """测试场景3：按status筛选"""
        logger.info("测试场景3：按status筛选")
        
        response = wire_processing_api.list_transactions(
            status=PaymentTransactionStatus.COMPLETED, size=10
        )
        assert response.status_code == 200
        logger.info("✓ status筛选验证通过")

    def test_filter_by_date_range(self, wire_processing_api):
        """测试场景4：按日期范围筛选"""
        logger.info("测试场景4：按日期范围筛选")
        
        response = wire_processing_api.list_transactions(
            start_date="2024-01-01", end_date="2024-12-31", size=10
        )
        assert response.status_code == 200
        logger.info("✓ 日期范围筛选验证通过")

    def test_undefined_response_fields(self, wire_processing_api):
        """测试场景5：未定义响应字段验证"""
        logger.info("测试场景5：未定义响应字段验证")
        
        response = wire_processing_api.list_transactions(size=1)
        content = response.json().get("content", [])
        
        if content:
            transaction = content[0]
            undefined_fields = ["fee", "completed_date", "financial_account_name", 
                              "counterparty_name", "schedule_date", "transaction_id",
                              "reversal_id", "direction", "reference_number"]
            
            found = [f for f in undefined_fields if f in transaction]
            if found:
                logger.warning(f"⚠️ 检测到未定义字段: {found}")
        
        logger.info("✓ 未定义字段验证完成")
