"""
Wire Processing - International Wire Payment 接口测试用例
测试 POST /api/v1/cores/{core}/money-movements/international-wire/payment 接口
"""
import pytest
from utils.logger import logger


@pytest.mark.wire_processing
@pytest.mark.create_api
@pytest.mark.no_rerun
@pytest.mark.skip(reason="真实国际电汇，会实际扣款，不可撤销")
class TestInternationalWirePayment:
    """
    国际电汇测试（破坏性操作，全部skip）
    """

    def test_initiate_international_wire_success(self, wire_processing_api):
        """测试场景1：成功发起国际电汇"""
        logger.info("测试场景1：成功发起国际电汇")
        
        response = wire_processing_api.initiate_international_wire_payment(
            amount="1000.00",
            financial_account_id="test_fa_id",
            counterparty_id="test_intl_cp_id",
            memo="International Transfer"
        )
        assert response.status_code == 200
        logger.info("✓ 国际电汇发起成功")

    def test_international_wire_vs_wire_duplicate(self, wire_processing_api):
        """测试场景2：International Wire vs Wire重复验证"""
        logger.info("测试场景2：接口重复验证")
        
        logger.warning("⚠️ 文档问题：接口完全重复")
        logger.warning("Wire Payment和International Wire Payment:")
        logger.warning("- 请求参数完全相同")
        logger.warning("- 响应结构完全相同")
        logger.warning("- 只有URL路径不同")
        logger.warning("为什么不是一个接口用payment_type参数区分？")
        
        logger.info("✓ 接口重复问题已记录")
