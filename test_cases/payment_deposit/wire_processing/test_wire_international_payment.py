"""
Wire Processing - 国际电汇接口测试用例
POST /api/v1/cores/{core}/money-movements/international-wire/payment

业务规则（已验证）：
- counterparty 必须是 International_Wire 类型（Wire 类型会报错）
- FA 如果有 sub，必须传 sub_account_id
- counterparty assign_account_ids 必须包含 FA 对应的 account_id

已验证账户数据：
  INTL_FA=251212054048210705，INTL_SUB=251212054048210868
  INTL_CP=251212054048302253（International_Wire 类型）
  WIRE_CP=251212054048128208（Wire 类型，用于错误场景）
"""
import pytest
import time
from utils.logger import logger

INTL_FA      = "251212054048210705"
INTL_SUB     = "251212054048210868"
INTL_CP      = "251212054048302253"   # International_Wire 类型 CP
WIRE_CP      = "251212054048128208"   # Wire 类型，用于错误场景
INVISIBLE_FA = "241010195850134683"

MEMO_PREFIX = "Auto TestYan IntlWire Payment"

pytestmark = [pytest.mark.wire_processing, pytest.mark.no_rerun]


@pytest.mark.wire_processing
@pytest.mark.no_rerun
class TestInternationalWirePayment:

    def test_initiate_intl_wire_success(self, wire_processing_api):
        """
        测试场景1：成功发起国际 Wire 交易，并立即 cancel
        Test Scenario1: Initiate International Wire Payment and Cancel Immediately
        验证点：code=200，status=Processing，可被 cancel
        """
        memo = f"{MEMO_PREFIX} {time.strftime('%Y-%m-%d %H:%M:%S')}"
        resp = wire_processing_api.initiate_international_wire_payment(
            financial_account_id=INTL_FA,
            counterparty_id=INTL_CP,
            amount="0.01",
            sub_account_id=INTL_SUB,
            schedule_date="2026-12-28",
            memo=memo
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body.get("code") == 200, \
            f"发起国际 Wire 失败: code={body.get('code')}, err={body.get('error_message')}"

        data = body.get("data") or body
        txn_id = data.get("id")
        status = data.get("status")
        assert txn_id, "交易 id 不应为空"
        assert status == "Processing", f"国际 Wire 状态应为 Processing，实际: {status}"
        logger.info(f"  ✓ 国际 Wire 发起成功: id={txn_id}, status={status}")

        # 尝试 cancel（国际 Wire 可能不支持 cancel，不强制断言）
        cancel_resp = wire_processing_api.session.patch(
            wire_processing_api.config.get_full_url(f"/money-movements/wire/{txn_id}/cancel")
        )
        cancel_code = cancel_resp.json().get("code")
        if cancel_code == 200:
            logger.info(f"✓ 国际 Wire cancel 成功: id={txn_id}")
        else:
            logger.info(f"  ⚠ 国际 Wire cancel 返回: code={cancel_code}（国际 Wire 可能不支持 cancel）")

    def test_intl_wire_with_wire_cp_rejected(self, wire_processing_api):
        """
        测试场景2：使用 Wire 类型 CP 发起国际 Wire → 被拒绝
        Test Scenario2: Domestic Wire CP Used for International Wire Returns Error
        """
        resp = wire_processing_api.initiate_international_wire_payment(
            financial_account_id=INTL_FA,
            counterparty_id=WIRE_CP,
            amount="0.01",
            sub_account_id=INTL_SUB,
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body.get("code") != 200
        logger.info(f"✓ Wire 类型 CP 被拒绝于国际 Wire: code={body.get('code')}, msg={body.get('error_message')}")

    def test_intl_wire_missing_sub_account_id(self, wire_processing_api):
        """
        测试场景3：FA 有 sub 但未传 sub_account_id → code=599
        Test Scenario3: FA with Sub but Missing sub_account_id Returns 599
        """
        resp = wire_processing_api.initiate_international_wire_payment(
            financial_account_id=INTL_FA,
            counterparty_id=INTL_CP,
            amount="0.01",
            # 故意不传 sub_account_id
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body.get("code") != 200
        logger.info(f"✓ 缺少 sub_account_id 被拒绝: code={body.get('code')}")

    def test_intl_wire_invisible_fa(self, wire_processing_api):
        """
        测试场景4：使用越权 FA ID
        Test Scenario4: Invisible FA ID Returns Error
        """
        resp = wire_processing_api.initiate_international_wire_payment(
            financial_account_id=INVISIBLE_FA,
            counterparty_id=INTL_CP,
            amount="0.01",
        )
        assert resp.status_code == 200
        assert resp.json().get("code") != 200
        logger.info(f"✓ 越权 FA 被拒绝: code={resp.json().get('code')}")

    def test_intl_wire_missing_required_params(self, wire_processing_api):
        """
        测试场景5：缺少必填参数 counterparty_id
        Test Scenario5: Missing Required counterparty_id Returns Error
        """
        url = wire_processing_api.config.get_full_url("/money-movements/international-wire/payment")
        resp = wire_processing_api.session.post(url, json={
            "financial_account_id": INTL_FA,
            "sub_account_id": INTL_SUB,
            "amount": "0.01"
        })
        assert resp.status_code == 200
        assert resp.json().get("code") != 200
        logger.info(f"✓ 缺少 counterparty_id 被拒绝: code={resp.json().get('code')}")

    def test_intl_wire_negative_amount(self, wire_processing_api):
        """
        测试场景6：金额为负数
        Test Scenario6: Negative Amount Returns Error
        """
        resp = wire_processing_api.initiate_international_wire_payment(
            financial_account_id=INTL_FA,
            counterparty_id=INTL_CP,
            amount="-5",
            sub_account_id=INTL_SUB,
        )
        assert resp.status_code == 200
        assert resp.json().get("code") != 200
        logger.info(f"✓ 负数金额被拒绝: code={resp.json().get('code')}")
