"""
Wire Processing - 国内电汇 & Cancel 接口测试用例
POST /api/v1/cores/{core}/money-movements/wire/payment         Initiate Wire Transaction
PATCH /api/v1/cores/{core}/money-movements/wire/:id/cancel    Cancel Wire Transaction

业务规则（已验证）：
- FA 如果有 sub_account，必须携带 sub_account_id（否则 code=599）
- counterparty 必须是 Wire 类型（International_Wire 类型会报 code=599）
- FA 对应的 account_id 必须在 counterparty 的 assign_account_ids 中
- 发起后状态为 Processing（非实时，不是 Completed）
- cancel 只能 cancel wire/international wire 类型，其他类型 code=599

已验证账户数据：
  WIRE_FA=251119084741475550（有 sub），WIRE_SUB=251119084741475584
  WIRE_CP=251212054048128208（Wire 类型，assign=['250918043812871683']）
  INTL_CP=251212054048302253（International_Wire 类型，用于错误场景测试）
"""
import pytest
import time
from utils.logger import logger

WIRE_FA      = "251119084741475550"
WIRE_SUB     = "251119084741475584"
WIRE_CP      = "251212054048128208"   # Wire 类型 CP，assign 了 WIRE_FA 的 account_id
INTL_CP      = "251212054048302253"   # International_Wire 类型，用于类型错误测试
INVISIBLE_FA = "241010195850134683"

MEMO_PREFIX = "Auto TestYan Wire Payment"

pytestmark = [pytest.mark.wire_processing, pytest.mark.no_rerun]


@pytest.mark.wire_processing
@pytest.mark.no_rerun
class TestWireDomesticPayment:

    def test_initiate_wire_payment_success(self, wire_processing_api):
        """
        测试场景1：成功发起国内 Wire 交易，并立即 cancel
        Test Scenario1: Initiate Wire Payment and Cancel Immediately
        验证点：code=200，status=Processing，可被 cancel
        """
        memo = f"{MEMO_PREFIX} {time.strftime('%Y-%m-%d %H:%M:%S')}"
        resp = wire_processing_api.initiate_wire_payment(
            financial_account_id=WIRE_FA,
            counterparty_id=WIRE_CP,
            amount="0.01",
            sub_account_id=WIRE_SUB,
            schedule_date="2026-12-31",
            memo=memo
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body.get("code") == 200, \
            f"发起 Wire 失败: code={body.get('code')}, err={body.get('error_message')}"

        data = body.get("data") or body
        txn_id = data.get("id")
        status = data.get("status")
        assert txn_id, "交易 id 不应为空"
        assert status == "Processing", f"Wire 交易状态应为 Processing，实际: {status}"
        logger.info(f"  ✓ Wire 发起成功: id={txn_id}, status={status}")

        # 立即 cancel，清理数据
        cancel_resp = wire_processing_api.session.patch(
            wire_processing_api.config.get_full_url(f"/money-movements/wire/{txn_id}/cancel")
        )
        cancel_body = cancel_resp.json()
        assert cancel_body.get("code") == 200
        logger.info(f"✓ Wire 发起后立即 cancel 成功: id={txn_id}")

    def test_wire_response_fields(self, wire_processing_api):
        """
        测试场景2：验证 Wire 响应字段完整性（发起后立即 cancel）
        Test Scenario2: Verify Wire Response Fields Completeness
        """
        memo = f"{MEMO_PREFIX} FieldCheck {int(time.time())}"
        resp = wire_processing_api.initiate_wire_payment(
            financial_account_id=WIRE_FA,
            counterparty_id=WIRE_CP,
            amount="0.01",
            sub_account_id=WIRE_SUB,
            memo=memo
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body.get("code") == 200
        data = body.get("data") or body

        required_fields = [
            "id", "status", "amount", "financial_account_id",
            "counterparty_id", "transaction_type"
        ]
        for field in required_fields:
            assert field in data, f"Wire 响应缺少字段: '{field}'"

        txn_id = data.get("id")
        # 立即 cancel
        wire_processing_api.session.patch(
            wire_processing_api.config.get_full_url(f"/money-movements/wire/{txn_id}/cancel")
        )
        logger.info(f"✓ Wire 响应字段验证通过: {[f for f in required_fields if f in data]}")

    def test_wire_missing_sub_account_id(self, wire_processing_api):
        """
        测试场景3：FA 有 sub_account 但未传 sub_account_id → code=599
        Test Scenario3: FA with Sub but Missing sub_account_id Returns 599
        """
        resp = wire_processing_api.initiate_wire_payment(
            financial_account_id=WIRE_FA,
            counterparty_id=WIRE_CP,
            amount="0.01",
            # 故意不传 sub_account_id
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body.get("code") != 200, \
            f"缺少 sub_account_id 应返回错误，实际 code={body.get('code')}"
        logger.info(f"✓ 缺少 sub_account_id 被拒绝: code={body.get('code')}, msg={body.get('error_message')}")

    def test_wire_with_international_wire_cp(self, wire_processing_api):
        """
        测试场景4：使用 International_Wire 类型 CP 发起国内 Wire → code=599
        Test Scenario4: International_Wire CP Used for Domestic Wire Returns 599
        """
        resp = wire_processing_api.initiate_wire_payment(
            financial_account_id=WIRE_FA,
            counterparty_id=INTL_CP,
            amount="0.01",
            sub_account_id=WIRE_SUB,
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body.get("code") != 200
        logger.info(f"✓ International_Wire CP 被拒绝: code={body.get('code')}, msg={body.get('error_message')}")

    def test_wire_invisible_fa(self, wire_processing_api):
        """
        测试场景5：使用越权 FA ID → 被拒绝
        Test Scenario5: Invisible FA ID Returns Error
        """
        resp = wire_processing_api.initiate_wire_payment(
            financial_account_id=INVISIBLE_FA,
            counterparty_id=WIRE_CP,
            amount="0.01",
        )
        assert resp.status_code == 200
        assert resp.json().get("code") != 200
        logger.info(f"✓ 越权 FA 被拒绝: code={resp.json().get('code')}")

    def test_wire_missing_counterparty_id(self, wire_processing_api):
        """
        测试场景6：缺少必填 counterparty_id
        Test Scenario6: Missing Required counterparty_id
        """
        url = wire_processing_api.config.get_full_url("/money-movements/wire/payment")
        resp = wire_processing_api.session.post(url, json={
            "financial_account_id": WIRE_FA,
            "sub_account_id": WIRE_SUB,
            "amount": "0.01"
        })
        assert resp.status_code == 200
        assert resp.json().get("code") != 200
        logger.info(f"✓ 缺少 counterparty_id 被拒绝: code={resp.json().get('code')}")

    def test_wire_negative_amount(self, wire_processing_api):
        """
        测试场景7：金额为负数
        Test Scenario7: Negative Amount Returns Error
        """
        resp = wire_processing_api.initiate_wire_payment(
            financial_account_id=WIRE_FA,
            counterparty_id=WIRE_CP,
            amount="-10",
            sub_account_id=WIRE_SUB,
        )
        assert resp.status_code == 200
        assert resp.json().get("code") != 200
        logger.info(f"✓ 负数金额被拒绝: code={resp.json().get('code')}")

    # ────── Cancel Wire Transaction ──────

    def test_cancel_wire_invalid_txn_id(self, wire_processing_api):
        """
        测试场景8：使用不存在的 transaction_id cancel
        Test Scenario8: Cancel with Non-existent Transaction ID
        """
        url = wire_processing_api.config.get_full_url(
            "/money-movements/wire/INVALID_TXN_99999/cancel"
        )
        resp = wire_processing_api.session.patch(url)
        assert resp.status_code == 200
        body = resp.json()
        assert body.get("code") != 200
        logger.info(f"✓ 无效 txn_id cancel 被拒绝: code={body.get('code')}")

    def test_cancel_non_wire_txn_returns_error(self, wire_processing_api):
        """
        测试场景9：cancel internal pay 类型 transaction → code=599
        Test Scenario9: Cancel Non-wire Transaction Returns 599
        业务规则：只能 cancel Wire 和 International_Wire 类型的交易
        """
        # 获取一个 internal pay transaction id
        url = wire_processing_api.config.get_full_url("/money-movements/internal-pay/transactions")
        r = wire_processing_api.session.get(url, params={"size": 1})
        ip_txns = r.json().get("data", {}).get("content", [])
        if not ip_txns:
            pytest.skip("无 Internal Pay 交易数据")
        ip_id = ip_txns[0].get("id")

        cancel_url = wire_processing_api.config.get_full_url(
            f"/money-movements/wire/{ip_id}/cancel"
        )
        resp = wire_processing_api.session.patch(cancel_url)
        assert resp.status_code == 200
        body = resp.json()
        assert body.get("code") != 200, \
            f"Non-wire txn 应返回错误，实际 code={body.get('code')}"
        logger.info(f"✓ Non-wire txn cancel 被拒绝: code={body.get('code')}, msg={body.get('error_message')}")
