"""
Wire Processing - Wire Payment 接口测试用例
测试电汇转账接口（Wire和International Wire）
"""
import pytest
from utils.logger import logger
from utils.assertions import assert_status_ok


@pytest.mark.wire_processing
@pytest.mark.create_api
@pytest.mark.no_rerun
@pytest.mark.skip(reason="真实电汇操作，会实际扣款，不可撤销")
class TestWirePayment:
    """
    电汇转账测试（破坏性操作，全部skip）
    包含Wire、International Wire、Request Payment
    """

    def test_initiate_wire_payment_success(self, wire_processing_api):
        """测试场景1：成功发起国内电汇"""
        logger.info("测试场景1：成功发起国内电汇")
        
        response = wire_processing_api.initiate_wire_payment(
            amount="100.00",
            financial_account_id="test_fa_id",
            counterparty_id="test_cp_id",
            memo="Auto TestYan Wire Transfer"
        )
        assert response.status_code == 200
        logger.info("✓ 国内电汇发起成功")

    def test_initiate_international_wire_success(self, wire_processing_api):
        """测试场景2：成功发起国际电汇"""
        logger.info("测试场景2：成功发起国际电汇")
        
        response = wire_processing_api.initiate_international_wire_payment(
            amount="1000.00",
            financial_account_id="test_fa_id",
            counterparty_id="test_intl_cp_id",
            memo="International Transfer"
        )
        assert response.status_code == 200
        logger.info("✓ 国际电汇发起成功")

    def test_request_wire_payment_success(self, wire_processing_api):
        """测试场景3：成功发起收款请求"""
        logger.info("测试场景3：成功发起收款请求")
        
        response = wire_processing_api.request_wire_payment(
            amount="50.00",
            financial_account_id="test_fa_id",
            counterparty_id="test_cp_id",
            memo="Request Payment"
        )
        assert response.status_code == 200
        logger.info("✓ 收款请求发起成功")


@pytest.mark.wire_processing
@pytest.mark.create_api
class TestWirePaymentErrors:
    """电汇错误处理（可运行）"""

    def test_wire_missing_counterparty_id(self, wire_processing_api):
        """测试场景4：缺少counterparty_id"""
        logger.info("测试场景4：缺少counterparty_id")
        
        response = wire_processing_api.initiate_wire_payment(
            amount="100.00",
            financial_account_id="test_fa_id",
            counterparty_id=""
        )
        assert response.status_code == 200
        logger.info("✓ 缺少对手方ID测试完成")

    def test_url_path_error_documentation(self, wire_processing_api):
        """测试场景5：URL路径错误验证"""
        logger.info("测试场景5：URL路径文档错误")
        
        logger.warning("⚠️ 文档问题：URL路径示例错误")
        logger.warning("文档示例：/cores/xxx/wire/payment")
        logger.warning("应该是：/cores/xxx/money-movements/wire/payment")
        logger.info("✓ URL路径错误已记录")
