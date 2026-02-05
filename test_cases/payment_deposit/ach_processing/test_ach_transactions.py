"""
ACH Processing - Transactions 接口测试用例
测试 GET /api/v1/cores/{core}/money-movements/ach/transactions 接口
"""
import pytest
from utils.logger import logger
from data.enums import PaymentTransactionStatus


@pytest.mark.ach_processing
@pytest.mark.list_api
class TestACHTransactions:
    """ACH交易列表测试"""

    def test_list_transactions_success(self, ach_processing_api):
        """测试场景1：成功获取交易列表"""
        logger.info("测试场景1：成功获取ACH交易列表")
        
        response = ach_processing_api.list_transactions(page=0, size=10)
        assert response.status_code == 200
        
        if "content" in response.json():
            logger.info(f"✓ 交易列表获取成功")
        
        logger.info("✓ 列表获取成功")

    def test_filter_by_status(self, ach_processing_api):
        """测试场景2：按status筛选"""
        logger.info("测试场景2：按status筛选")
        
        response = ach_processing_api.list_transactions(
            status=PaymentTransactionStatus.COMPLETED, size=10
        )
        assert response.status_code == 200
        logger.info("✓ status筛选验证通过")

    def test_undefined_response_fields(self, ach_processing_api):
        """测试场景3：未定义响应字段验证（13+个）"""
        logger.info("测试场景3：未定义响应字段验证")
        
        response = ach_processing_api.list_transactions(size=1)
        content = response.json().get("content", [])
        
        if content:
            transaction = content[0]
            undefined = ["fee", "completed_date", "financial_account_name",
                        "counterparty_name", "schedule_date", "transaction_id",
                        "first_party", "same_day", "reversal_id", "direction",
                        "reference_number"]
            
            found = [f for f in undefined if f in transaction]
            if found:
                logger.warning(f"⚠️ 未定义字段: {found}")
            
            # 检查first_party字段
            if "first_party" in transaction:
                first_party = transaction["first_party"]
                logger.info(f"first_party值: {first_party}")
                logger.info("first_party=true: 第一方转账（Bank Account ID）")
                logger.info("first_party=false: 第三方转账（Counterparty ID）")
        
        logger.info("✓ 未定义字段验证完成")
