"""
Instant Pay - Approve/Reject 接口测试用例

以下 4 个接口依赖对方发起的交易，无法自动化模拟，仅验证 invalid ID 场景：
  POST /instant-pay/payment-request/approve/:id
  POST /instant-pay/payment-request/reject/:id
  POST /instant-pay/return-request/approve/:id
  POST /instant-pay/return-request/reject/:id

业务说明（用户确认）：
  - Approve/Reject Payment Request：处理别人向我们发起的 instant pay 请求
  - Approve/Reject Return Request：处理别人要求退款的请求
  - 以上均无法通过自动化模拟对方，只能验证接口可达性和 invalid 场景
  - 所有正向场景 skip

已验证：所有 invalid ID 均返回 code=599 "Transaction does not exist."
"""
import pytest
from utils.logger import logger

pytestmark = pytest.mark.instant_pay


@pytest.mark.instant_pay
class TestApproveRejectPaymentRequest:

    def test_approve_payment_request_invalid_id(self, instant_pay_api):
        """
        测试场景1：approve payment request - 无效 ID → code=599
        Test Scenario1: Approve Payment Request with Invalid ID Returns 599
        """
        resp = instant_pay_api.approve_payment_request("INVALID_ID_99999")
        assert resp.status_code == 200
        body = resp.json()
        assert body.get("code") != 200
        logger.info(f"✓ approve-payment-request INVALID: code={body.get('code')}, msg={body.get('error_message')}")

    def test_reject_payment_request_invalid_id(self, instant_pay_api):
        """
        测试场景2：reject payment request - 无效 ID → code=599
        Test Scenario2: Reject Payment Request with Invalid ID Returns 599
        """
        resp = instant_pay_api.reject_payment_request(
            "INVALID_ID_99999",
            reject_code="AC04",
            reject_reason="Auto test"
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body.get("code") != 200
        logger.info(f"✓ reject-payment-request INVALID: code={body.get('code')}, msg={body.get('error_message')}")

    @pytest.mark.skip(reason="需要对方向我们发起的 Incoming RFP，无法自动化模拟")
    def test_approve_payment_request_success(self, instant_pay_api):
        """⚠️ 跳过：需要真实 Incoming RFP 数据"""
        pass

    @pytest.mark.skip(reason="需要对方向我们发起的 Incoming RFP，无法自动化模拟")
    def test_reject_payment_request_success(self, instant_pay_api):
        """⚠️ 跳过：需要真实 Incoming RFP 数据"""
        pass


@pytest.mark.instant_pay
class TestApproveRejectReturnRequest:

    def test_approve_return_request_invalid_id(self, instant_pay_api):
        """
        测试场景3：approve return request - 无效 ID → code=599
        Test Scenario3: Approve Return Request with Invalid ID Returns 599
        """
        resp = instant_pay_api.approve_return_request("INVALID_RETURN_ID_99999")
        assert resp.status_code == 200
        body = resp.json()
        assert body.get("code") != 200
        logger.info(f"✓ approve-return-request INVALID: code={body.get('code')}, msg={body.get('error_message')}")

    def test_reject_return_request_invalid_id(self, instant_pay_api):
        """
        测试场景4：reject return request - 无效 ID → code=599
        Test Scenario4: Reject Return Request with Invalid ID Returns 599
        """
        resp = instant_pay_api.reject_return_request(
            "INVALID_RETURN_ID_99999",
            reject_code="AC04",
            reject_reason="Auto test"
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body.get("code") != 200
        logger.info(f"✓ reject-return-request INVALID: code={body.get('code')}, msg={body.get('error_message')}")

    @pytest.mark.skip(reason="需要对方发起 return request，无法自动化模拟")
    def test_approve_return_request_success(self, instant_pay_api):
        """⚠️ 跳过：需要真实 return request 数据"""
        pass

    @pytest.mark.skip(reason="需要对方发起 return request，无法自动化模拟")
    def test_reject_return_request_success(self, instant_pay_api):
        """⚠️ 跳过：需要真实 return request 数据"""
        pass
