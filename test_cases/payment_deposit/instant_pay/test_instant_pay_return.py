"""
Instant Pay - Return 接口测试用例
测试退款相关接口
"""
import pytest
from utils.logger import logger


@pytest.mark.instant_pay
@pytest.mark.update_api
@pytest.mark.no_rerun
@pytest.mark.skip(reason="退款操作需要已结算的真实交易")
class TestInstantPayReturn:
    """
    Return相关测试（破坏性，全部skip）
    ⚠️ 文档问题：Return Payment vs Return Request区别不明
    """

    def test_return_payment(self, instant_pay_api):
        """测试场景1：退款支付"""
        logger.info("测试场景1：退款支付")
        
        response = instant_pay_api.return_payment(
            transaction_id="test_txn_id",
            return_code="AC03",
            return_reason="Wrong account"
        )
        assert response.status_code == 200
        logger.info("✓ 退款支付成功")

    def test_return_request(self, instant_pay_api):
        """测试场景2：退款请求"""
        logger.info("测试场景2：退款请求")
        
        logger.warning("⚠️ Return Payment vs Return Request区别未说明")
        
        response = instant_pay_api.return_request(
            transaction_id="test_txn_id",
            return_code="AC03",
            return_reason="Test return"
        )
        assert response.status_code == 200
        logger.info("✓ 退款请求成功")

    def test_approve_return_request(self, instant_pay_api):
        """测试场景3：批准退款请求"""
        logger.info("测试场景3：批准退款请求")
        
        response = instant_pay_api.approve_return_request("test_return_id")
        assert response.status_code == 200
        logger.info("✓ 退款请求批准成功")

    def test_reject_return_request(self, instant_pay_api):
        """测试场景4：拒绝退款请求"""
        logger.info("测试场景4：拒绝退款请求")
        
        response = instant_pay_api.reject_return_request(
            return_request_id="test_return_id",
            reject_code="AC04",
            reject_reason="Test reject"
        )
        assert response.status_code == 200
        logger.info("✓ 退款请求拒绝成功")


@pytest.mark.instant_pay
@pytest.mark.update_api
class TestInstantPayReturnErrors:
    """Return错误处理（可运行）"""

    def test_return_code_unknown_values(self, instant_pay_api):
        """测试场景5：return_code可能值验证"""
        logger.info("测试场景5：return_code可能值")
        
        logger.warning("⚠️ 文档问题：return_code可能值未知")
        logger.warning("外部链接缺失")
        logger.warning("示例：AC03")
        
        logger.info("✓ return_code问题已记录")

    def test_return_reason_example_error(self, instant_pay_api):
        """测试场景6：return_reason示例内容错误"""
        logger.info("测试场景6：return_reason示例错误")
        
        logger.warning("⚠️ 文档问题：示例内容不符合美国场景")
        logger.warning("示例：Wrong IBAN in SCT")
        logger.warning("IBAN是欧洲标准，SCT是欧洲支付")
        logger.warning("但这是美国的FedNow服务")
        logger.warning("示例应该用美国相关的错误描述")
        
        logger.info("✓ 示例错误已记录")

    def test_reject_return_request_url_error(self, instant_pay_api):
        """测试场景7：Reject Return Request URL示例完全错误"""
        logger.info("测试场景7：URL示例完全错误")
        
        logger.warning("⚠️⚠️ 文档问题：URL示例完全错误")
        logger.warning("接口定义：/return-request/reject/:id")
        logger.warning("示例URL：/payment-request/reject/...")
        logger.warning("这是完全不同的接口！")
        
        logger.info("✓ URL严重错误已记录")

    def test_url_naming_inconsistency(self, instant_pay_api):
        """测试场景8：URL命名不一致"""
        logger.info("测试场景8：URL命名不一致")
        
        logger.warning("⚠️ 文档问题：URL命名不一致")
        logger.info("/request-payment/cancel - 使用request-payment")
        logger.info("/payment-request/approve - 使用payment-request")
        logger.info("/payment-request/reject - 使用payment-request")
        logger.info("/return-request/approve - 使用return-request")
        logger.warning("同一功能使用不同格式，容易混淆")
        
        logger.info("✓ URL命名不一致已记录")
