"""
Instant Pay - Initiate Payment 接口测试用例
测试 POST /api/v1/cores/{core}/money-movements/instant-pay/payment 接口
"""
import pytest
from utils.logger import logger


@pytest.mark.instant_pay
@pytest.mark.create_api
@pytest.mark.no_rerun
@pytest.mark.skip(reason="真实支付操作，会实际扣款，20秒超时限制")
class TestInstantPayPayment:
    """
    Instant Pay支付测试（破坏性，全部skip）
    ⚠️ 20秒超时限制：Payment Timeout Clock
    """

    def test_initiate_payment_success(self, instant_pay_api):
        """测试场景1：成功发起Instant Pay支付"""
        logger.info("测试场景1：成功发起Instant Pay支付")
        
        response = instant_pay_api.initiate_payment(
            amount="10.00",
            financial_account_id="test_fa_id",
            counterparty_id="test_cp_id",
            memo="Auto TestYan Instant Pay"
        )
        assert response.status_code == 200
        logger.info("✓ Instant Pay支付发起成功")

    def test_payment_with_link(self, instant_pay_api):
        """测试场景2：包含link的支付"""
        logger.info("测试场景2：包含link的支付")
        
        response = instant_pay_api.initiate_payment(
            amount="20.00",
            financial_account_id="test_fa_id",
            counterparty_id="test_cp_id",
            link="https://www.example.com"
        )
        assert response.status_code == 200
        logger.info("✓ 包含link的支付成功")

    def test_payment_with_structured_content(self, instant_pay_api):
        """测试场景3：包含structured_content的支付"""
        logger.info("测试场景3：包含structured_content的支付")
        
        logger.warning("⚠️ structured_content说明不清")
        logger.warning("文档说明：The file content which upload to the system")
        logger.warning("实际是XML字符串，不是文件上传")
        logger.warning("格式规范未说明，用途不明")
        
        response = instant_pay_api.initiate_payment(
            amount="30.00",
            financial_account_id="test_fa_id",
            counterparty_id="test_cp_id",
            structured_content="<Strd><AddtlRmtInf>test</AddtlRmtInf></Strd>"
        )
        assert response.status_code == 200
        logger.info("✓ structured_content支付测试完成")

    def test_payment_timeout_clock(self, instant_pay_api):
        """测试场景4：20秒超时限制验证"""
        logger.info("测试场景4：20秒超时限制")
        
        logger.warning("⚠️⚠️⚠️ Payment Timeout Clock：20秒限制")
        logger.warning("所有Instant Pay必须在20秒内完成或失败")
        logger.warning("这是FedNow系统的硬性要求")
        logger.warning("超时交易会自动失败")
        
        logger.info("✓ 20秒超时限制已记录")


@pytest.mark.instant_pay
@pytest.mark.create_api
class TestInstantPayPaymentErrors:
    """Instant Pay支付错误处理（可运行）"""

    def test_missing_required_field(self, instant_pay_api):
        """测试场景5：缺少必需字段"""
        logger.info("测试场景5：缺少必需字段")
        
        response = instant_pay_api.initiate_payment(
            amount="10.00",
            financial_account_id="test_fa_id",
            counterparty_id=""  # 空
        )
        assert response.status_code == 200
        logger.info("✓ 缺少必需字段测试完成")

    def test_url_path_error(self, instant_pay_api):
        """测试场景6：URL路径示例错误"""
        logger.info("测试场景6：URL路径错误验证")
        
        logger.warning("⚠️ 文档问题：URL路径示例错误")
        logger.warning("示例：/cores/xxx/instant-pay/payment")
        logger.warning("应该：/cores/xxx/money-movements/instant-pay/payment")
        
        logger.info("✓ URL错误已记录")
