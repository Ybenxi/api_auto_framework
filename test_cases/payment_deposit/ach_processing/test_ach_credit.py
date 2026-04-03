"""
ACH Processing - Credit 接口测试用例
POST /api/v1/cores/{core}/money-movements/ach/credit

ACH Credit = 向外部账户（counterparty）转账（推送资金）

已验证数据：
  first_party=False:
    FA/SUB 见 conftest ACH_FP_FALSE_*；counterparty_id 由 fixture ach_fp_false_ctx 从 list 动态解析
    （避免硬编码 CP 被 cleanup_counterparty「Auto TestYan」清理后失效）
  first_party=True（使用 bank-account 作为 CP）:
    ACH_FA=251212054048470574, ACH_SUB=251212054048470660, ACH_CP_FP=251212054048237385
    （CP 是 bank-account，account_id=251212054048210865，与 FA 的 account_id 一致）
"""
import pytest
import time
from utils.logger import logger

ACH_FA_FP_TRUE = "251212054048470574"
ACH_SUB_FP_TRUE = "251212054048470660"
ACH_CP_FP    = "251212054048237385"    # bank-account CP，用于 first_party=True
INVISIBLE_FA = "241010195850134683"

MEMO_PREFIX = "Auto TestYan ACH Credit"

pytestmark = [pytest.mark.ach_processing, pytest.mark.no_rerun]


@pytest.mark.ach_processing
@pytest.mark.no_rerun
class TestAchCredit:

    def test_credit_fp_false_success_and_cancel(self, ach_processing_api, ach_fp_false_ctx):
        """
        测试场景1：first_party=False Credit 成功发起并 cancel
        Test Scenario1: Initiate ACH Credit (first_party=False) and Cancel
        验证点：code=200, status=Processing, first_party=False, direction=Origination
        """
        memo = f"{MEMO_PREFIX} fp=False {time.strftime('%Y-%m-%d %H:%M:%S')}"
        resp = ach_processing_api.initiate_credit(
            financial_account_id=ach_fp_false_ctx["fa"],
            sub_account_id=ach_fp_false_ctx["sub"],
            counterparty_id=ach_fp_false_ctx["cp"],
            amount="0.01",
            first_party=False,
            same_day=False,
            memo=memo
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body.get("code") == 200, \
            f"ACH Credit fp=False 失败: code={body.get('code')}, err={body.get('error_message')}"

        data = body.get("data") or body
        txn_id = data.get("id") or data.get("transaction_id")
        assert txn_id
        assert data.get("status") == "Processing"
        assert data.get("direction") == "Origination"
        assert data.get("first_party") is False
        assert data.get("transaction_type") == "Credit"
        logger.info(f"  ✓ Credit fp=False 发起成功: id={txn_id}")

        cancel_resp = ach_processing_api.cancel_transaction(txn_id)
        assert cancel_resp.json().get("code") == 200
        logger.info(f"✓ ACH Credit fp=False cancel 成功")

    def test_credit_fp_true_success_and_cancel(self, ach_processing_api):
        """
        测试场景2：first_party=True Credit 成功发起并 cancel（使用 bank-account 作为 CP）
        Test Scenario2: Initiate ACH Credit (first_party=True) and Cancel
        验证点：code=200, first_party=True，CP 是外部绑定银行账户
        """
        memo = f"{MEMO_PREFIX} fp=True {time.strftime('%Y-%m-%d %H:%M:%S')}"
        resp = ach_processing_api.initiate_credit(
            financial_account_id=ACH_FA_FP_TRUE,
            sub_account_id=ACH_SUB_FP_TRUE,
            counterparty_id=ACH_CP_FP,
            amount="0.01",
            first_party=True,
            same_day=False,
            memo=memo
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body.get("code") == 200, \
            f"ACH Credit fp=True 失败: code={body.get('code')}, err={body.get('error_message')}"

        data = body.get("data") or body
        txn_id = data.get("id") or data.get("transaction_id")
        assert txn_id
        assert data.get("status") == "Processing"
        assert data.get("first_party") is True
        logger.info(f"  ✓ Credit fp=True 发起成功: id={txn_id}")

        cancel_resp = ach_processing_api.cancel_transaction(txn_id)
        assert cancel_resp.json().get("code") == 200
        logger.info(f"✓ ACH Credit fp=True cancel 成功")

    def test_credit_response_fields(self, ach_processing_api, ach_fp_false_ctx):
        """
        测试场景3：验证 ACH Credit 响应字段完整性（含 ACH 特有字段）
        Test Scenario3: Verify ACH Credit Response Fields
        """
        resp = ach_processing_api.initiate_credit(
            financial_account_id=ach_fp_false_ctx["fa"],
            sub_account_id=ach_fp_false_ctx["sub"],
            counterparty_id=ach_fp_false_ctx["cp"],
            amount="0.01",
            first_party=False,
            same_day=False,
            memo=f"{MEMO_PREFIX} FieldCheck {int(time.time())}"
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body.get("code") == 200
        data = body.get("data") or body

        required_fields = [
            "id", "status", "amount", "direction", "first_party",
            "same_day", "financial_account_id", "counterparty_id", "transaction_type"
        ]
        for field in required_fields:
            assert field in data, f"ACH Credit 响应缺少字段: '{field}'"

        txn_id = data.get("id")
        ach_processing_api.cancel_transaction(txn_id)
        logger.info(f"✓ ACH Credit 响应字段验证通过: {required_fields}")

    def test_credit_with_schedule_date(self, ach_processing_api, ach_fp_false_ctx):
        """
        测试场景4：传入未来 schedule_date
        Test Scenario4: Credit with Future schedule_date
        """
        resp = ach_processing_api.initiate_credit(
            financial_account_id=ach_fp_false_ctx["fa"],
            sub_account_id=ach_fp_false_ctx["sub"],
            counterparty_id=ach_fp_false_ctx["cp"],
            amount="0.01",
            first_party=False,
            same_day=False,
            schedule_date="2026-12-31",
            memo=f"{MEMO_PREFIX} ScheduleDate {int(time.time())}"
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body.get("code") == 200
        data = body.get("data") or body
        txn_id = data.get("id")
        ach_processing_api.cancel_transaction(txn_id)
        logger.info(f"✓ schedule_date Credit 发起成功: id={txn_id}")

    def test_credit_missing_sub_account_id(self, ach_processing_api, ach_fp_false_ctx):
        """
        测试场景5：FA 有 sub 但未传 sub_account_id → code=599
        Test Scenario5: Missing sub_account_id Returns Error
        """
        resp = ach_processing_api.initiate_credit(
            financial_account_id=ach_fp_false_ctx["fa"],
            counterparty_id=ach_fp_false_ctx["cp"],
            amount="0.01",
            first_party=False,
            same_day=False,
        )
        assert resp.status_code == 200
        assert resp.json().get("code") != 200
        logger.info(f"✓ 缺少 sub_account_id 被拒绝: code={resp.json().get('code')}")

    def test_credit_invisible_fa(self, ach_processing_api, ach_fp_false_ctx):
        """
        测试场景6：越权 FA → 被拒绝
        Test Scenario6: Invisible FA Returns Error
        """
        resp = ach_processing_api.initiate_credit(
            financial_account_id=INVISIBLE_FA,
            counterparty_id=ach_fp_false_ctx["cp"],
            amount="0.01",
            first_party=False,
            same_day=False,
        )
        assert resp.status_code == 200
        assert resp.json().get("code") != 200
        logger.info(f"✓ 越权 FA 被拒绝: code={resp.json().get('code')}")

    def test_credit_missing_counterparty(self, ach_processing_api, ach_fp_false_ctx):
        """
        测试场景7：缺少必填 counterparty_id
        Test Scenario7: Missing counterparty_id Returns Error
        """
        url = ach_processing_api.config.get_full_url("/money-movements/ach/credit")
        resp = ach_processing_api.session.post(url, json={
            "financial_account_id": ach_fp_false_ctx["fa"],
            "sub_account_id": ach_fp_false_ctx["sub"],
            "amount": "0.01",
            "first_party": False,
            "same_day": False,
        })
        assert resp.status_code == 200
        assert resp.json().get("code") != 200
        logger.info(f"✓ 缺少 counterparty_id 被拒绝: code={resp.json().get('code')}")

    def test_credit_negative_amount(self, ach_processing_api, ach_fp_false_ctx):
        """
        测试场景8：负数金额 → 被拒绝
        Test Scenario8: Negative Amount Returns Error
        """
        resp = ach_processing_api.initiate_credit(
            financial_account_id=ach_fp_false_ctx["fa"],
            sub_account_id=ach_fp_false_ctx["sub"],
            counterparty_id=ach_fp_false_ctx["cp"],
            amount="-1",
            first_party=False,
            same_day=False,
        )
        assert resp.status_code == 200
        assert resp.json().get("code") != 200
        logger.info(f"✓ 负数金额被拒绝: code={resp.json().get('code')}")
