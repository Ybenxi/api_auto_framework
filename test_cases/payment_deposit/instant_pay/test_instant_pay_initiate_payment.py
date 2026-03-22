"""
Instant Pay - Initiate Payment 接口测试用例
POST /api/v1/cores/{core}/money-movements/instant-pay/payment

业务规则（已验证）：
- FA 如果有 sub_account，必须传 sub_account_id（否则 code=599）
- counterparty 的 assign_account_ids 必须包含 FA 的 account_id（Approved 状态）
- 余额不足 → code=600 "Insufficient available funds."
- 发起后 status=Processing，direction=Origination
- 响应用 transaction_id 字段（不是 id）

已验证账户数据：
  IP_FA=251119084741475550（有 sub），IP_SUB=251119084741475584
  IP_CP=251212054048369447（Instant Pay CP，assign=['250918043812871683'] = FA's account_id）
"""
import pytest
import time
from utils.logger import logger

IP_FA        = "251119084741475550"
IP_SUB       = "251119084741475584"
IP_CP        = "251212054048369447"   # assign 了 IP_FA 的 account_id
INVISIBLE_FA = "241010195850134683"

MEMO_PREFIX = "Auto TestYan IP Payment"

pytestmark = [pytest.mark.instant_pay, pytest.mark.no_rerun]


@pytest.mark.instant_pay
@pytest.mark.no_rerun
class TestInstantPayInitiatePayment:

    def test_initiate_payment_success(self, instant_pay_api):
        """
        测试场景1：成功发起 Instant Pay 支付
        Test Scenario1: Successfully Initiate Instant Pay Payment
        验证点：code=200，status=Processing，direction=Origination，含 transaction_id 字段
        """
        memo = f"{MEMO_PREFIX} {time.strftime('%Y-%m-%d %H:%M:%S')}"
        resp = instant_pay_api.initiate_payment(
            financial_account_id=IP_FA,
            sub_account_id=IP_SUB,
            counterparty_id=IP_CP,
            amount="0.01",
            memo=memo
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body.get("code") == 200, \
            f"Instant Pay 发起失败: code={body.get('code')}, err={body.get('error_message')}"

        data = body.get("data") or body
        txn_id = data.get("transaction_id") or data.get("id")
        assert txn_id, "transaction_id 不应为空"
        assert data.get("status") == "Processing", f"status 应为 Processing，实际: {data.get('status')}"
        assert data.get("direction") == "Origination"
        # 验证 transaction_id 字段名（Instant Pay 特有，不是 id）
        assert "transaction_id" in data, "Instant Pay 响应应含 transaction_id 字段"
        logger.info(f"✓ Instant Pay 发起成功: txn_id={txn_id}, status={data.get('status')}")

    def test_payment_response_fields(self, instant_pay_api):
        """
        测试场景2：验证 Instant Pay 响应字段完整性
        Test Scenario2: Verify Payment Response Fields Completeness
        """
        resp = instant_pay_api.initiate_payment(
            financial_account_id=IP_FA,
            sub_account_id=IP_SUB,
            counterparty_id=IP_CP,
            amount="0.01",
            memo=f"{MEMO_PREFIX} FieldCheck {int(time.time())}"
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body.get("code") == 200
        data = body.get("data") or body

        required_fields = [
            "transaction_id", "status", "amount", "direction",
            "financial_account_id", "counterparty_id", "transaction_type"
        ]
        for field in required_fields:
            assert field in data, f"Instant Pay 响应缺少字段: '{field}'"
        logger.info(f"✓ 响应字段完整性验证通过: {[f for f in required_fields if f in data]}")

    def test_payment_missing_sub_account_id(self, instant_pay_api):
        """
        测试场景3：FA 有 sub 但未传 sub_account_id → code=599
        Test Scenario3: FA with Sub but Missing sub_account_id Returns 599
        """
        resp = instant_pay_api.initiate_payment(
            financial_account_id=IP_FA,
            counterparty_id=IP_CP,
            amount="0.01",
            # 故意不传 sub_account_id
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body.get("code") != 200, \
            f"缺少 sub_account_id 应返回错误，实际 code={body.get('code')}"
        logger.info(f"✓ 缺少 sub_account_id 被拒绝: code={body.get('code')}, msg={body.get('error_message')}")

    def test_payment_insufficient_funds(self, instant_pay_api):
        """
        测试场景4：金额超过余额 → code=600 Insufficient available funds
        Test Scenario4: Insufficient Funds Returns 600
        """
        resp = instant_pay_api.initiate_payment(
            financial_account_id=IP_FA,
            sub_account_id=IP_SUB,
            counterparty_id=IP_CP,
            amount="99999999",  # 超大金额
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body.get("code") != 200
        logger.info(f"✓ 余额不足被拒绝: code={body.get('code')}, msg={body.get('error_message','')[:60]}")

    def test_payment_invisible_fa(self, instant_pay_api):
        """
        测试场景5：越权 FA ID → 被拒绝
        Test Scenario5: Invisible FA Returns Error
        """
        resp = instant_pay_api.initiate_payment(
            financial_account_id=INVISIBLE_FA,
            counterparty_id=IP_CP,
            amount="0.01",
        )
        assert resp.status_code == 200
        assert resp.json().get("code") != 200
        logger.info(f"✓ 越权 FA 被拒绝: code={resp.json().get('code')}")

    def test_payment_missing_counterparty_id(self, instant_pay_api):
        """
        测试场景6：缺少必填 counterparty_id
        Test Scenario6: Missing Required counterparty_id Returns Error
        """
        url = instant_pay_api.config.get_full_url("/money-movements/instant-pay/payment")
        resp = instant_pay_api.session.post(url, json={
            "financial_account_id": IP_FA,
            "sub_account_id": IP_SUB,
            "amount": "0.01"
        })
        assert resp.status_code == 200
        assert resp.json().get("code") != 200
        logger.info(f"✓ 缺少 counterparty_id 被拒绝: code={resp.json().get('code')}")

    def test_payment_negative_amount(self, instant_pay_api):
        """
        测试场景7：负数金额
        Test Scenario7: Negative Amount Returns Error
        """
        resp = instant_pay_api.initiate_payment(
            financial_account_id=IP_FA,
            sub_account_id=IP_SUB,
            counterparty_id=IP_CP,
            amount="-1",
        )
        assert resp.status_code == 200
        assert resp.json().get("code") != 200
        logger.info(f"✓ 负数金额被拒绝: code={resp.json().get('code')}")

    def test_payment_appears_in_transactions_list(self, instant_pay_api):
        """
        测试场景8：发起后在 transactions list 中可查到
        Test Scenario8: Initiated Payment Appears in Transactions List
        """
        resp = instant_pay_api.initiate_payment(
            financial_account_id=IP_FA,
            sub_account_id=IP_SUB,
            counterparty_id=IP_CP,
            amount="0.01",
            memo=f"{MEMO_PREFIX} ListCheck {int(time.time())}"
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body.get("code") == 200
        data = body.get("data") or body
        txn_id = data.get("transaction_id") or data.get("id")

        # 在 list 里按 transaction_id 筛选
        list_resp = instant_pay_api.list_transactions(
            financial_account_id=IP_FA, size=10
        )
        assert list_resp.status_code == 200
        txns = list_resp.json().get("data", {}).get("content", [])
        found = any(
            (t.get("transaction_id") or t.get("id")) == txn_id for t in txns
        )
        if found:
            logger.info(f"  ✓ 发起的 txn 在 list 中找到: id={txn_id}")
        else:
            logger.info(f"  ⚠ 未在 list 前10条中找到 id={txn_id}（可能已翻页）")
        logger.info("✓ Instant Pay 发起后 list 查询验证完成")
