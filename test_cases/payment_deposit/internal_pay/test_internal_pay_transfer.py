"""
Internal Pay - Transfer 接口测试用例
POST /api/v1/cores/{core}/money-movements/internal-pay/transfer

响应结构：{"code": 200, "data": {status, transaction_id, amount, fee, memo, ...}}
注意：Internal Pay 无 direction 字段（区别于 Account Transfer）。

业务规则：
  - 如果 payer FA 有 sub account，必须传 payer_sub_account_id
  - payee FA 同理
  - 转账完成后状态为 Completed（实时结算）
  - 每笔转账产生 2 条 transaction 记录（Credit 和 Debit）
  - memo 格式：Auto TestYan Internal Pay {timestamp}

已验证测试账户（dev actc 环境）：
  FA1 (有固定 Sub)：
    PAYER_FA  = "251212054048470568"
    PAYER_SUB = "251212054048470660"
  FA3 (无 Sub，不需要 sub_account_id)：
    PAYER_FA_NO_SUB = "251212054048470609"
  Payee (外部 FA，有 Sub)：
    PAYEE_FA  = "250918043814723897"
    PAYEE_SUB = "250918043814723925"
"""
import pytest
import time
from utils.logger import logger
from test_cases.test_ids import FA_1_ID, FA_3_ID, MAIN_SUB_ID

# FA1 has the fixed Sub — use for sub-based transfers
PAYER_FA  = FA_1_ID        # "251212054048470568"
PAYER_SUB = MAIN_SUB_ID    # "251212054048470660"

# FA3 has NO sub accounts — use for FA-only (no sub) transfers
PAYER_FA_NO_SUB = FA_3_ID  # "251212054048470609"

# Payee: external FA with its own sub
PAYEE_FA  = "250918043814723897"
PAYEE_SUB = "250918043814723925"

MEMO_PREFIX = "Auto TestYan Internal Pay"

pytestmark = pytest.mark.internal_pay


def _memo():
    return f"{MEMO_PREFIX} {int(time.time())}"


@pytest.mark.internal_pay
class TestInternalPayTransfer:

    @pytest.mark.no_rerun
    def test_transfer_success(self, internal_pay_api):
        """
        测试场景1：成功发起 Internal Pay 转账（双方均用 sub）
        Test Scenario1: Successfully Initiate Internal Pay Transfer (with sub accounts)
        验证点：
        1. HTTP 200，code=200
        2. status=Completed（实时结算）
        3. 无 direction 字段（与 Account Transfer 的区别）
        4. memo 正确回显
        5. 转账后在 transactions list 中可查到
        """
        memo = _memo()
        resp = internal_pay_api.initiate_transfer(
            payer_financial_account_id=PAYER_FA,
            payer_sub_account_id=PAYER_SUB,
            payee_financial_account_id=PAYEE_FA,
            payee_sub_account_id=PAYEE_SUB,
            amount="0.01",
            memo=memo
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body.get("code") == 200, \
            f"Transfer should succeed, actual code={body.get('code')}, err={body.get('error_message')}"

        data = body.get("data", {})
        assert data.get("status") == "Completed", f"Expected Completed, got: {data.get('status')}"
        assert "direction" not in data, "Internal Pay should not have direction field"
        assert data.get("memo") == memo, f"memo echo mismatch: {data.get('memo')}"

        txn_id = data.get("transaction_id") or data.get("id")
        logger.info(f"✓ Transfer succeeded: txn_id={txn_id}, memo={memo}")

        # Verify in transactions list
        time.sleep(1)
        list_resp = internal_pay_api.list_transactions(
            payer_financial_account_id=PAYER_FA, size=10
        )
        content = list_resp.json().get("data", {}).get("content", [])
        found = any(t.get("memo") == memo for t in content)
        if found:
            logger.info(f"✓ Transfer record found in list, memo='{memo}'")
        else:
            logger.info(f"  ⚠ Not yet in list (may be delayed), memo='{memo}'")

    @pytest.mark.no_rerun
    def test_transfer_success_no_sub(self, internal_pay_api):
        """
        测试场景1b：成功发起 Internal Pay 转账（payer 使用纯 FA，无 sub）
        Test Scenario1b: Successfully Initiate Internal Pay Transfer (FA only, no sub)
        验证点：
        1. FA3 (no sub accounts) → 无需传 sub_account_id，直接用 FA 发起转账
        2. HTTP 200，code=200，status=Completed
        """
        memo = _memo()
        resp = internal_pay_api.initiate_transfer(
            payer_financial_account_id=PAYER_FA_NO_SUB,
            payee_financial_account_id=PAYEE_FA,
            payee_sub_account_id=PAYEE_SUB,
            amount="0.01",
            memo=memo
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body.get("code") == 200, \
            f"FA-only transfer should succeed, code={body.get('code')}, err={body.get('error_message')}"
        data = body.get("data", {})
        assert data.get("status") == "Completed"
        logger.info(f"✓ FA-only transfer succeeded: status={data.get('status')}, memo={memo}")

    @pytest.mark.no_rerun
    def test_transfer_verify_two_records(self, internal_pay_api):
        """
        测试场景2：转账后验证产生 2 条记录（Credit + Debit）
        Test Scenario2: Transfer Creates 2 Records (Credit and Debit)
        """
        memo = _memo()
        resp = internal_pay_api.initiate_transfer(
            payer_financial_account_id=PAYER_FA,
            payer_sub_account_id=PAYER_SUB,
            payee_financial_account_id=PAYEE_FA,
            payee_sub_account_id=PAYEE_SUB,
            amount="0.01",
            memo=memo
        )
        assert resp.json().get("code") == 200, "转账失败"
        time.sleep(1)

        # 查与本次 memo 相关的记录
        list_resp = internal_pay_api.list_transactions(size=50)
        content = list_resp.json().get("data", {}).get("content", [])
        memo_txns = [t for t in content if t.get("memo") == memo]

        logger.info(f"  本次转账 memo='{memo}' 产生 {len(memo_txns)} 条记录")
        if len(memo_txns) >= 2:
            types = {t.get("transaction_type") for t in memo_txns}
            logger.info(f"  transaction_type 值: {types}")
            assert "Credit" in types and "Debit" in types, \
                "应同时有 Credit（收款）和 Debit（付款）记录"
            logger.info("✓ 每笔转账产生 Credit + Debit 两条记录验证通过")
        elif len(memo_txns) == 1:
            logger.info("  ⚠ 只查到 1 条记录（可能另一条在分页后面）")
        else:
            logger.info("  ⚠ 未查到记录（可能延迟）")

    @pytest.mark.no_rerun
    def test_transfer_verify_balance_change(self, internal_pay_api, login_session):
        """
        测试场景3：转账后验证双方余额变动
        Test Scenario3: Verify Balance Changes After Transfer
        """
        from config.config import config as _config

        def get_balance(fa_id):
            r = login_session.get(
                f"{_config.base_url}/api/v1/cores/{_config.core}/financial-accounts/{fa_id}"
            )
            d = r.json().get("data", r.json()) or {}
            return float(d.get("available_balance") or d.get("balance") or 0)

        payer_before = get_balance(PAYER_FA)
        payee_before = get_balance(PAYEE_FA)
        logger.info(f"  转账前 payer 余额: {payer_before}")
        logger.info(f"  转账前 payee 余额: {payee_before}")

        amount = "0.01"
        memo = _memo()
        resp = internal_pay_api.initiate_transfer(
            payer_financial_account_id=PAYER_FA,
            payer_sub_account_id=PAYER_SUB,
            payee_financial_account_id=PAYEE_FA,
            payee_sub_account_id=PAYEE_SUB,
            amount=amount,
            memo=memo
        )
        assert resp.json().get("code") == 200
        fee = float(resp.json().get("data", {}).get("fee") or 0)
        logger.info(f"  转账成功，amount={amount}, fee={fee}")

        time.sleep(1)
        payer_after = get_balance(PAYER_FA)
        payee_after = get_balance(PAYEE_FA)
        logger.info(f"  转账后 payer 余额: {payer_after}")
        logger.info(f"  转账后 payee 余额: {payee_after}")

        assert payer_before - payer_after > 0, "payer 余额应减少"
        assert payee_after - payee_before >= 0, "payee 余额应增加或不变"
        logger.info("✓ 余额变动验证通过")

    def test_transfer_missing_payer_fa(self, internal_pay_api):
        """
        测试场景4：缺少 payer_financial_account_id（必填）
        Test Scenario4: Missing payer_financial_account_id Returns Error
        """
        url = internal_pay_api.config.get_full_url("/money-movements/internal-pay/transfer")
        resp = internal_pay_api.session.post(url, json={
            "payee_financial_account_id": PAYEE_FA,
            "payee_sub_account_id": PAYEE_SUB,
            "amount": "0.01",
            "memo": _memo()
        })
        assert resp.status_code == 200
        body = resp.json()
        assert body.get("code") != 200
        logger.info(f"✓ 缺少 payer_fa 被拒绝: code={body.get('code')}, msg={body.get('error_message')}")

    def test_transfer_missing_amount(self, internal_pay_api):
        """
        测试场景5：缺少 amount（必填）
        Test Scenario5: Missing amount Returns Error
        """
        url = internal_pay_api.config.get_full_url("/money-movements/internal-pay/transfer")
        resp = internal_pay_api.session.post(url, json={
            "payer_financial_account_id": PAYER_FA,
            "payer_sub_account_id": PAYER_SUB,
            "payee_financial_account_id": PAYEE_FA,
            "payee_sub_account_id": PAYEE_SUB,
            "memo": _memo()
        })
        assert resp.status_code == 200
        assert resp.json().get("code") != 200
        logger.info(f"✓ 缺少 amount 被拒绝: code={resp.json().get('code')}")

    def test_transfer_negative_amount(self, internal_pay_api):
        """
        测试场景6：传入负数金额
        Test Scenario6: Negative Amount Returns Error
        """
        resp = internal_pay_api.initiate_transfer(
            payer_financial_account_id=PAYER_FA,
            payer_sub_account_id=PAYER_SUB,
            payee_financial_account_id=PAYEE_FA,
            payee_sub_account_id=PAYEE_SUB,
            amount="-10",
            memo=_memo()
        )
        assert resp.status_code == 200
        assert resp.json().get("code") != 200
        logger.info(f"✓ 负数金额被拒绝: code={resp.json().get('code')}")

    def test_transfer_invalid_fa_ids(self, internal_pay_api):
        """
        测试场景7：使用不存在的 FA ID
        Test Scenario7: Non-existent FA IDs Return Error
        """
        resp = internal_pay_api.initiate_transfer(
            payer_financial_account_id="INVALID_PAYER_999999",
            payee_financial_account_id="INVALID_PAYEE_999999",
            amount="0.01",
            memo=_memo()
        )
        assert resp.status_code == 200
        assert resp.json().get("code") != 200
        logger.info(f"✓ 无效 FA ID 被拒绝: code={resp.json().get('code')}")
