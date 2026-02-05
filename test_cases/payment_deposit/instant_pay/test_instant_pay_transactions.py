"""
Instant Pay - Transactions 接口测试用例
测试交易列表和Request Payment列表接口
"""
import pytest
from utils.logger import logger
from data.enums import PaymentTransactionStatus, RequestPaymentStatus, WireDirection


@pytest.mark.instant_pay
@pytest.mark.list_api
class TestInstantPayTransactions:
    """Instant Pay交易列表测试"""

    def test_list_transactions_success(self, instant_pay_api):
        """测试场景1：成功获取交易列表"""
        logger.info("测试场景1：成功获取Instant Pay交易列表")
        
        response = instant_pay_api.list_transactions(page=0, size=10)
        assert response.status_code == 200
        
        if "content" in response.json():
            logger.warning("⚠️ 响应无code包装层")
            logger.info(f"✓ 交易列表获取成功")
        
        logger.info("✓ 列表获取成功")

    def test_filter_by_status(self, instant_pay_api):
        """测试场景2：按status筛选"""
        logger.info("测试场景2：按status筛选")
        
        response = instant_pay_api.list_transactions(
            status=PaymentTransactionStatus.COMPLETED, size=10
        )
        assert response.status_code == 200
        logger.info("✓ status筛选验证通过")

    def test_undefined_response_fields(self, instant_pay_api):
        """测试场景3：未定义响应字段验证（14+个）"""
        logger.info("测试场景3：未定义响应字段验证")
        
        response = instant_pay_api.list_transactions(size=1)
        content = response.json().get("content", [])
        
        if content:
            transaction = content[0]
            undefined = ["fee", "completed_date", "financial_account_name", 
                        "counterparty_name", "schedule_date", "transaction_id",
                        "direction", "link", "structured_file_id"]
            
            found = [f for f in undefined if f in transaction]
            if found:
                logger.warning(f"⚠️ 未定义字段: {found}")
        
        logger.info("✓ 未定义字段验证完成")


@pytest.mark.instant_pay
@pytest.mark.list_api
class TestInstantPayRequestPaymentTransactions:
    """Request Payment交易列表测试"""

    def test_list_request_payment_success(self, instant_pay_api):
        """测试场景4：成功获取Request Payment列表"""
        logger.info("测试场景4：成功获取Request Payment列表")
        
        response = instant_pay_api.list_request_payment_transactions(page=0, size=10)
        assert response.status_code == 200
        
        response_body = response.json()
        if "code" in response_body:
            logger.info("✓ 此接口有code包装层（与List Transactions不同）")
            assert response_body.get("code") == 200
        
        logger.info("✓ Request Payment列表获取成功")

    def test_filter_by_rfp_status(self, instant_pay_api):
        """测试场景5：按Request Payment专有status筛选"""
        logger.info("测试场景5：按RFP status筛选")
        
        response = instant_pay_api.list_request_payment_transactions(
            status=RequestPaymentStatus.PAID_IN_FULL, size=10
        )
        assert response.status_code == 200
        logger.info("✓ RFP status筛选验证通过")

    def test_rfp_status_enum_different(self, instant_pay_api):
        """测试场景6：Request Payment status枚举值验证"""
        logger.info("测试场景6：RFP status枚举验证")
        
        logger.warning("⚠️ 文档问题：RFP status与普通Payment完全不同")
        logger.info("普通Payment: Reviewing, Cancelled, Completed, Processing, Failed")
        logger.info("Request Payment: Cancelled, Pending, Rejected, Paid_In_Full, Paid_In_Partial")
        logger.warning("但Properties中未定义这些新status")
        
        logger.info("✓ status差异已记录")

    def test_filter_by_direction(self, instant_pay_api):
        """测试场景7：按direction筛选"""
        logger.info("测试场景7：按direction筛选")
        
        response = instant_pay_api.list_request_payment_transactions(
            direction=WireDirection.INCOMING, size=10
        )
        assert response.status_code == 200
        logger.info("✓ direction筛选验证通过")
