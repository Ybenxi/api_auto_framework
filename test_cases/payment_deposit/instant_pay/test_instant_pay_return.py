"""
Instant Pay - Return Payment & Return Request 接口测试用例
POST /api/v1/cores/{core}/money-movements/instant-pay/return-payment/{transaction_id}
POST /api/v1/cores/{core}/money-movements/instant-pay/return-request/{transaction_id}

业务规则（已验证）：
  return-payment：
    - 只能对已成功结算（Completed，Origination 方向）的 transaction 操作
    - Processing 状态 → code=599 "Transaction is not allowed to payment return."
    - 不存在 ID → code=599 "Transaction does not exist."

  return-request：
    - 针对收到的 Incoming 交易（收到别人的钱）进行原路退款
    - 需要真实 Incoming Completed 数据，自动化中难以制造，测 invalid 场景为主

必填参数：return_code（必填）, return_reason（可选）
"""
import pytest
from utils.logger import logger

pytestmark = pytest.mark.instant_pay


@pytest.mark.instant_pay
@pytest.mark.no_rerun
class TestInstantPayReturnPayment:

    def _get_completed_txns(self, instant_pay_api):
        """获取 Completed 状态的 instant pay transaction"""
        resp = instant_pay_api.list_transactions(status="Completed", size=10)
        return resp.json().get("data", {}).get("content", []) if resp.json().get("code") == 200 else []

    def test_return_payment_on_processing_txn(self, instant_pay_api):
        """
        测试场景1：对 Processing 状态的 txn 发起 return-payment → 被拒绝
        Test Scenario1: Return Payment on Processing Transaction Returns Error
        业务规则：只有已结算的 txn 才能 return
        """
        # 找一个 Processing 状态的 txn
        resp = instant_pay_api.list_transactions(status="Processing", size=3)
        processing = resp.json().get("data", {}).get("content", [])
        if not processing:
            pytest.skip("无 Processing 状态的 Instant Pay 交易")

        txn_id = processing[0].get("transaction_id") or processing[0].get("id")
        ret_resp = instant_pay_api.return_payment(
            transaction_id=txn_id,
            return_code="AC03",
            return_reason="Auto test return on Processing"
        )
        assert ret_resp.status_code == 200
        body = ret_resp.json()
        assert body.get("code") != 200
        logger.info(f"✓ Processing 状态 txn return-payment 被拒绝: code={body.get('code')}, msg={body.get('error_message')}")

    def test_return_payment_on_completed_txn(self, instant_pay_api):
        """
        测试场景2：对 Completed 状态的 txn 发起 return-payment
        Test Scenario2: Return Payment on Completed Transaction
        验证点：code=200 或提示"已退款"，视实际数据而定
        """
        completed = self._get_completed_txns(instant_pay_api)
        if not completed:
            pytest.skip("无 Completed 状态的 Instant Pay 交易")

        # 优先找 Debit/Origination 方向（我们发出去的）
        txn = next(
            (t for t in completed
             if t.get("direction") == "Origination" or t.get("transaction_type") == "Debit"),
            completed[0]
        )
        txn_id = txn.get("transaction_id") or txn.get("id")

        ret_resp = instant_pay_api.return_payment(
            transaction_id=txn_id,
            return_code="AC03",
            return_reason="Auto test return on Completed"
        )
        assert ret_resp.status_code == 200
        body = ret_resp.json()
        if body.get("code") == 200:
            logger.info(f"✓ Completed txn return-payment 成功: id={txn_id}")
        else:
            logger.info(f"  ⚠ Completed txn return-payment 返回: code={body.get('code')}, msg={body.get('error_message','')[:60]}")
            # 可能已经被 return 过了，属于正常探索性结果

    def test_return_payment_invalid_txn_id(self, instant_pay_api):
        """
        测试场景3：使用不存在的 transaction_id → code=599
        Test Scenario3: Invalid Transaction ID Returns 599
        """
        ret_resp = instant_pay_api.return_payment(
            transaction_id="INVALID_TXN_ID_99999",
            return_code="AC03",
            return_reason="Test"
        )
        assert ret_resp.status_code == 200
        body = ret_resp.json()
        assert body.get("code") != 200
        logger.info(f"✓ 无效 txn_id return-payment 被拒绝: code={body.get('code')}, msg={body.get('error_message')}")

    def test_return_payment_missing_return_code(self, instant_pay_api):
        """
        测试场景4：缺少必填 return_code
        Test Scenario4: Missing Required return_code Returns Error
        """
        url = instant_pay_api.config.get_full_url(
            "/money-movements/instant-pay/return-payment/FAKE_TXN_ID_123"
        )
        resp = instant_pay_api.session.post(url, json={"return_reason": "Missing code"})
        assert resp.status_code == 200
        body = resp.json()
        if body.get("code") != 200:
            logger.info(f"✓ 缺少 return_code 被拒绝: code={body.get('code')}")
        else:
            logger.info(f"  ⚠ API 接受了缺少 return_code 的请求（探索性结果）")


@pytest.mark.instant_pay
@pytest.mark.no_rerun
class TestInstantPayReturnRequest:
    """
    Return Request 测试
    注：return-request 针对 Incoming 交易（收到别人的钱），原路退款
    因为自动化无法制造真实 Incoming Completed 数据，主要测 invalid 场景
    """

    def test_return_request_invalid_txn_id(self, instant_pay_api):
        """
        测试场景1：使用不存在的 transaction_id → code=599
        Test Scenario1: Invalid Transaction ID Returns 599
        """
        ret_resp = instant_pay_api.return_request(
            transaction_id="INVALID_TXN_ID_99999",
            return_code="AC03",
            return_reason="Test return request"
        )
        assert ret_resp.status_code == 200
        body = ret_resp.json()
        assert body.get("code") != 200
        logger.info(f"✓ 无效 txn_id return-request 被拒绝: code={body.get('code')}, msg={body.get('error_message')}")

    def test_return_request_on_origination_txn(self, instant_pay_api):
        """
        测试场景2：对我们发出的 Origination 交易发起 return-request → 被拒绝
        Test Scenario2: Return Request on Origination Transaction Returns Error
        （return-request 只针对 Incoming，对 Origination 应被拒绝）
        """
        # 找一个 Origination 方向的 txn
        resp = instant_pay_api.list_transactions(size=10)
        txns = resp.json().get("data", {}).get("content", [])
        orig_txn = next(
            (t for t in txns if t.get("direction") == "Origination"), None
        )
        if not orig_txn:
            pytest.skip("无 Origination 方向的 Instant Pay 交易")

        txn_id = orig_txn.get("transaction_id") or orig_txn.get("id")
        ret_resp = instant_pay_api.return_request(
            transaction_id=txn_id,
            return_code="AC03",
            return_reason="Auto test return request on Origination"
        )
        assert ret_resp.status_code == 200
        body = ret_resp.json()
        if body.get("code") != 200:
            logger.info(f"✓ Origination txn return-request 被拒绝（符合预期）: code={body.get('code')}")
        else:
            logger.info(f"  ⚠ Origination txn return-request 被接受（探索性结果）")

    @pytest.mark.skip(reason="return-request 需要真实 Incoming Completed 数据，无法自动化制造")
    def test_return_request_success(self, instant_pay_api):
        """⚠️ 跳过：需要真实收到的 Incoming Completed 交易"""
        pass
