"""
Instant Pay - Cancel/Approve/Reject 接口测试用例
测试Request Payment的取消、批准、拒绝操作
"""
import pytest
from utils.logger import logger


@pytest.mark.instant_pay
@pytest.mark.update_api
@pytest.mark.no_rerun
@pytest.mark.skip(reason="需要真实的Request Payment ID")
class TestInstantPayCancelApproveReject:
    """
    Cancel/Approve/Reject操作测试（全部skip）
    ⚠️ 文档问题：Cancel vs Reject概念混淆
    """

    def test_cancel_request_payment(self, instant_pay_api):
        """测试场景1：取消收款请求"""
        logger.info("测试场景1：取消收款请求")
        
        response = instant_pay_api.cancel_request_payment(
            rfp_id="test_rfp_id",
            cancel_code="AC03",  # 值未知
            cancel_reason="Test cancel"
        )
        assert response.status_code == 200
        logger.info("✓ 收款请求取消成功")

    def test_approve_payment_request(self, instant_pay_api):
        """测试场景2：批准付款请求"""
        logger.info("测试场景2：批准付款请求")
        
        logger.warning("⚠️ 批准后会实际付款")
        
        response = instant_pay_api.approve_payment_request(
            rfp_id="test_rfp_id",
            memo="Approved"
        )
        assert response.status_code == 200
        logger.info("✓ 付款请求批准成功")

    def test_reject_payment_request(self, instant_pay_api):
        """测试场景3：拒绝付款请求"""
        logger.info("测试场景3：拒绝付款请求")
        
        response = instant_pay_api.reject_payment_request(
            rfp_id="test_rfp_id",
            reject_code="AC04",  # 值未知
            reject_reason="Test reject"
        )
        assert response.status_code == 200
        logger.info("✓ 付款请求拒绝成功")


@pytest.mark.instant_pay
@pytest.mark.update_api
class TestInstantPayCancelApproveRejectErrors:
    """Cancel/Approve/Reject错误处理（可运行）"""

    def test_cancel_code_unknown_values(self, instant_pay_api):
        """测试场景4：cancel_code可能值验证"""
        logger.info("测试场景4：cancel_code可能值验证")
        
        logger.warning("⚠️ 文档问题：cancel_code可能值未知")
        logger.warning("文档说'link is as follows'但没有链接")
        logger.warning("示例只有AC03，不知道完整列表")
        logger.warning("格式未说明（字母+数字？）")
        
        logger.info("✓ cancel_code问题已记录")

    def test_reject_code_unknown_values(self, instant_pay_api):
        """测试场景5：reject_code可能值验证"""
        logger.info("测试场景5：reject_code可能值")
        
        logger.warning("⚠️ 文档问题：reject_code可能值未知")
        logger.warning("外部链接缺失，无法查询code列表")
        logger.warning("示例：AC04")
        
        logger.info("✓ reject_code问题已记录")

    def test_cancel_vs_reject_confusion(self, instant_pay_api):
        """测试场景6：Cancel vs Reject概念混淆"""
        logger.info("测试场景6：Cancel vs Reject概念验证")
        
        logger.warning("⚠️ 文档问题：术语混淆")
        logger.warning("Cancel Request Payment：取消请求付款")
        logger.warning("Reject Payment Request：拒绝付款请求")
        logger.warning("两者区别未说明")
        logger.warning("Cancel是发起方取消，Reject是接收方拒绝？")
        
        logger.info("✓ 术语混淆已记录")
