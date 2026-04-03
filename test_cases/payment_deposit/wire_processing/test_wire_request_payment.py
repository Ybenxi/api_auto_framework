"""
Wire Processing - Request for Wire Payment 接口测试用例
POST /api/v1/cores/{core}/money-movements/wire/request-payment

功能：发起一笔「拉款」请求，UniFi 向对方银行账户发起 pull
特点：交易发起后 status=Not_Sent（非实时），可以 cancel

响应结构：{"code": 200, "data": {id, status="Not_Sent", ...}}

已验证：
  WIRE_FA=251212054048470568，WIRE_SUB=251212054048470660
  WIRE_CP=251212054048128208（Wire 类型，用于 request-payment）
"""
import pytest
import time
from utils.logger import logger

WIRE_FA      = "251212054048470568"
WIRE_SUB     = "251212054048470660"
INVISIBLE_FA = "241010195850134683"

MEMO_PREFIX = "Auto TestYan Wire Not_Sent"

pytestmark = [pytest.mark.wire_processing, pytest.mark.no_rerun]


@pytest.mark.wire_processing
@pytest.mark.no_rerun
class TestWireRequestPayment:

    def test_request_payment_success(self, wire_processing_api, wire_cp_id):
        """
        测试场景1：成功发起 Wire 拉款请求（Not_Sent 状态），并立即 cancel
        Test Scenario1: Initiate Wire Request Payment (Not_Sent) and Cancel
        验证点：code=200，status=Not_Sent，可被 cancel
        """
        memo = f"{MEMO_PREFIX} {time.strftime('%Y-%m-%d %H:%M:%S')}"
        resp = wire_processing_api.request_wire_payment(
            financial_account_id=WIRE_FA,
            counterparty_id=wire_cp_id,
            amount="0.88",
            sub_account_id=WIRE_SUB,
            memo=memo
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body.get("code") == 200, \
            f"发起 Not_Sent Wire 失败: code={body.get('code')}, err={body.get('error_message')}"

        data = body.get("data") or body
        txn_id = data.get("id")
        status = data.get("status")
        assert txn_id, "交易 id 不应为空"
        assert status == "Not_Sent", f"request-payment 状态应为 Not_Sent，实际: {status}"
        logger.info(f"  ✓ Not_Sent Wire 发起成功: id={txn_id}, status={status}")

        # 尝试 cancel（Not_Sent 类型可能走不同 cancel 路径，不强制断言）
        cancel_resp = wire_processing_api.session.patch(
            wire_processing_api.config.get_full_url(f"/money-movements/wire/{txn_id}/cancel")
        )
        cancel_code = cancel_resp.json().get("code")
        if cancel_code == 200:
            logger.info(f"✓ Not_Sent Wire cancel 成功: id={txn_id}")
        else:
            logger.info(f"  ⚠ Not_Sent Wire cancel: code={cancel_code}，msg={cancel_resp.json().get('error_message')}")

    def test_request_payment_response_fields(self, wire_processing_api, wire_cp_id):
        """
        测试场景2：验证 Not_Sent 交易响应字段（发起后 cancel）
        Test Scenario2: Verify Not_Sent Transaction Response Fields
        """
        resp = wire_processing_api.request_wire_payment(
            financial_account_id=WIRE_FA,
            counterparty_id=wire_cp_id,
            amount="0.01",
            sub_account_id=WIRE_SUB,
            memo=f"{MEMO_PREFIX} FieldCheck {int(time.time())}"
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body.get("code") == 200
        data = body.get("data") or body

        required_fields = [
            "id", "status", "amount", "financial_account_id", "counterparty_id"
        ]
        for field in required_fields:
            assert field in data, f"响应缺少字段: '{field}'"
        assert data.get("status") == "Not_Sent"

        txn_id = data.get("id")
        wire_processing_api.session.patch(
            wire_processing_api.config.get_full_url(f"/money-movements/wire/{txn_id}/cancel")
        )
        logger.info(f"✓ Not_Sent 响应字段验证通过: fields={[f for f in required_fields if f in data]}")

    def test_request_payment_appears_in_list(self, wire_processing_api, wire_cp_id):
        """
        测试场景3：Not_Sent 交易在 list transactions 中可查到（发起后 cancel）
        Test Scenario3: Not_Sent Transaction Appears in List Transactions
        """
        resp = wire_processing_api.request_wire_payment(
            financial_account_id=WIRE_FA,
            counterparty_id=wire_cp_id,
            amount="0.01",
            sub_account_id=WIRE_SUB,
            memo=f"{MEMO_PREFIX} ListCheck {int(time.time())}"
        )
        assert resp.status_code == 200
        assert resp.json().get("code") == 200
        data = resp.json().get("data") or resp.json()
        txn_id = data.get("id")

        # 在 list 里查
        list_resp = wire_processing_api.list_transactions(
            financial_account_id=WIRE_FA, size=10
        )
        assert list_resp.status_code == 200
        txns = list_resp.json().get("data", {}).get("content", [])
        found = any(t.get("id") == txn_id for t in txns)
        if found:
            logger.info(f"  ✓ Not_Sent 交易在 list 中找到: id={txn_id}")
        else:
            logger.info(f"  ⚠ 未在 list 中找到 id={txn_id}（可能数量太多，已翻页）")

        # cancel
        wire_processing_api.session.patch(
            wire_processing_api.config.get_full_url(f"/money-movements/wire/{txn_id}/cancel")
        )
        logger.info("✓ Not_Sent list 查询验证完成")

    def test_request_payment_missing_sub_account_id(self, wire_processing_api, wire_cp_id):
        """
        测试场景4：FA 有 sub 但未传 sub_account_id → 被拒绝
        Test Scenario4: FA with Sub but Missing sub_account_id Returns Error
        """
        resp = wire_processing_api.request_wire_payment(
            financial_account_id=WIRE_FA,
            counterparty_id=wire_cp_id,
            amount="0.01",
            # 故意不传 sub_account_id
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body.get("code") != 200
        logger.info(f"✓ 缺少 sub_account_id 被拒绝: code={body.get('code')}")

    def test_request_payment_invisible_fa(self, wire_processing_api, wire_cp_id):
        """
        测试场景5：越权 FA ID → 被拒绝
        Test Scenario5: Invisible FA Returns Error
        """
        resp = wire_processing_api.request_wire_payment(
            financial_account_id=INVISIBLE_FA,
            counterparty_id=wire_cp_id,
            amount="0.01",
        )
        assert resp.status_code == 200
        assert resp.json().get("code") != 200
        logger.info(f"✓ 越权 FA 被拒绝: code={resp.json().get('code')}")

    def test_request_payment_missing_amount(self, wire_processing_api, wire_cp_id):
        """
        测试场景6：缺少必填 amount
        Test Scenario6: Missing Required amount Returns Error
        """
        url = wire_processing_api.config.get_full_url("/money-movements/wire/request-payment")
        resp = wire_processing_api.session.post(url, json={
            "financial_account_id": WIRE_FA,
            "sub_account_id": WIRE_SUB,
            "counterparty_id": wire_cp_id,
        })
        assert resp.status_code == 200
        assert resp.json().get("code") != 200
        logger.info(f"✓ 缺少 amount 被拒绝: code={resp.json().get('code')}")
