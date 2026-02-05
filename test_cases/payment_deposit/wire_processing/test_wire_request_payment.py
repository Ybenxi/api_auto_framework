"""
Wire Processing - Request Payment 接口测试用例
测试 POST /api/v1/cores/{core}/money-movements/wire/request-payment 接口
"""
import pytest
from utils.logger import logger


@pytest.mark.wire_processing
@pytest.mark.create_api
@pytest.mark.no_rerun
@pytest.mark.skip(reason="真实收款请求，会发起拉款")
class TestWireRequestPayment:
    """
    电汇收款请求测试（破坏性操作，全部skip）
    """

    def test_request_wire_payment_success(self, wire_processing_api):
        """测试场景1：成功发起收款请求"""
        logger.info("测试场景1：成功发起电汇收款请求")
        
        response = wire_processing_api.request_wire_payment(
            amount="50.00",
            financial_account_id="test_fa_id",
            counterparty_id="test_cp_id",
            memo="Request Payment"
        )
        assert response.status_code == 200
        logger.info("✓ 收款请求发起成功")

    def test_request_payment_description_unclear(self, wire_processing_api):
        """测试场景2：功能描述不清验证"""
        logger.info("测试场景2：功能描述验证")
        
        logger.warning("⚠️ 文档问题：功能描述不清")
        logger.warning("说'initiate instant pay pull'")
        logger.warning("与Instant Pay模块关系不明")
        logger.warning("pull vs push含义未说明")
        
        logger.info("✓ 描述不清问题已记录")

    def test_memo_length_shorter(self, wire_processing_api):
        """测试场景3：memo长度限制更短"""
        logger.info("测试场景3：memo长度限制验证")
        
        logger.warning("⚠️ 文档问题：memo长度不一致")
        logger.warning("Wire Payment: 最多210字符")
        logger.warning("Request Payment: 最多140字符")
        logger.warning("为什么Request Payment的memo更短？")
        
        logger.info("✓ memo长度问题已记录")
