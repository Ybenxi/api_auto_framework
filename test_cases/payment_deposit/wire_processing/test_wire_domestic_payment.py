"""
Wire Processing - Wire Payment 接口测试用例
测试 POST /api/v1/cores/{core}/money-movements/wire/payment 接口
"""
import pytest
from utils.logger import logger
from utils.assertions import assert_status_ok


@pytest.mark.wire_processing
@pytest.mark.create_api
@pytest.mark.no_rerun
@pytest.mark.skip(reason="真实国内电汇，会实际扣款，不可撤销")
class TestWirePayment:
    """
    国内电汇测试（破坏性操作，全部skip）
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


@pytest.mark.wire_processing
@pytest.mark.create_api
class TestWirePaymentErrors:
    """国内电汇错误处理（可运行）"""

    def test_wire_missing_counterparty_id(self, wire_processing_api):
        """测试场景2：缺少counterparty_id"""
        logger.info("测试场景2：缺少counterparty_id")
        
        response = wire_processing_api.initiate_wire_payment(
            amount="100.00",
            financial_account_id="test_fa_id",
            counterparty_id=""
        )
        assert response.status_code == 200
        logger.info("✓ 缺少对手方ID测试完成")

    def test_url_path_error_documentation(self, wire_processing_api):
        """测试场景3：URL路径错误验证"""
        logger.info("测试场景3：URL路径文档错误")
        
        logger.warning("⚠️ 文档问题：URL路径示例错误")
        logger.warning("文档示例：/cores/xxx/wire/payment")
        logger.warning("应该是：/cores/xxx/money-movements/wire/payment")
        logger.info("✓ URL路径错误已记录")
