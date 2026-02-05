"""
Instant Pay - Initiate Request Payment 接口测试用例
测试 POST /api/v1/cores/{core}/money-movements/instant-pay/request-payment 接口
"""
import pytest
from utils.logger import logger


@pytest.mark.instant_pay
@pytest.mark.create_api
@pytest.mark.no_rerun
@pytest.mark.skip(reason="真实收款请求，需要对手方配合")
class TestInstantPayRequestPayment:
    """
    Instant Pay收款请求测试（全部skip）
    """

    def test_initiate_request_payment_success(self, instant_pay_api):
        """测试场景1：成功发起收款请求"""
        logger.info("测试场景1：成功发起Instant Pay收款请求")
        
        response = instant_pay_api.initiate_request_payment(
            amount="50.00",
            financial_account_id="test_fa_id",
            counterparty_id="test_cp_id",
            execution_date="2025-04-22",
            expiration_date="2025-04-30"
        )
        assert response.status_code == 200
        logger.info("✓ 收款请求发起成功")

    def test_request_payment_with_modification_allowed(self, instant_pay_api):
        """测试场景2：允许修改金额的收款请求"""
        logger.info("测试场景2：允许修改金额的收款请求")
        
        logger.warning("⚠️ amount_modification_allowed逻辑未详细说明")
        logger.warning("问题：付款方如何修改金额？")
        logger.warning("问题：修改范围有限制吗？")
        
        response = instant_pay_api.initiate_request_payment(
            amount="100.00",
            financial_account_id="test_fa_id",
            counterparty_id="test_cp_id",
            amount_modification_allowed=True
        )
        assert response.status_code == 200
        logger.info("✓ 允许修改金额测试完成")

    def test_request_payment_early_payment_allowed(self, instant_pay_api):
        """测试场景3：允许提前支付的收款请求"""
        logger.info("测试场景3：允许提前支付")
        
        logger.warning("⚠️ early_payment_allowed定义不明")
        logger.warning("问题：early相对于什么日期？execution_date？")
        logger.warning("问题：提前多久算early？")
        
        response = instant_pay_api.initiate_request_payment(
            amount="80.00",
            financial_account_id="test_fa_id",
            counterparty_id="test_cp_id",
            early_payment_allowed=True
        )
        assert response.status_code == 200
        logger.info("✓ 允许提前支付测试完成")

    def test_execution_and_expiration_dates(self, instant_pay_api):
        """测试场景4：执行日期和过期日期"""
        logger.info("测试场景4：执行和过期日期验证")
        
        logger.info("execution_date默认：当天")
        logger.info("expiration_date默认：1年后")
        logger.warning("过期后如何处理？自动取消？未说明")
        
        logger.info("✓ 日期默认值已记录")
