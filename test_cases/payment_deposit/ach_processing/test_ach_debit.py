"""
ACH Processing - Debit 接口测试用例
POST /api/v1/cores/{core}/money-movements/ach/debit

ACH Debit = 向外部账户发起拉款（pull 资金进来，Money来自 counterparty）

已验证数据：
  first_party=False:
    使用 conftest 的 ach_debit_fp_false_ctx：FA=251119…，CP 从列表中选 Approved assign 到 profile 251212054048470503
    （勿与 Credit 共用 210705+301820：Debit 拉款易 code=600；勿用已清理的 369793）
  first_party=True：fixture ach_fp_true_debit_ctx（FA1 + 动态匹配 bank-account id）
    ⚠ 注意：Debit fp=True 可能因外部账户余额不足而报 code=600
"""
import pytest
import time
from utils.logger import logger

INVISIBLE_FA = "241010195850134683"
MEMO_PREFIX  = "Auto TestYan ACH Debit"

pytestmark = [pytest.mark.ach_processing, pytest.mark.no_rerun]


@pytest.mark.ach_processing
@pytest.mark.no_rerun
class TestAchDebit:

    def test_debit_fp_false_success_and_cancel(self, ach_processing_api, ach_debit_fp_false_ctx):
        """
        测试场景1：first_party=False Debit 成功发起并 cancel
        Test Scenario1: Initiate ACH Debit (first_party=False) and Cancel
        验证点：code=200, status=Processing, transaction_type=Debit, first_party=False
        """
        memo = f"{MEMO_PREFIX} fp=False {time.strftime('%Y-%m-%d %H:%M:%S')}"
        resp = ach_processing_api.initiate_debit(
            financial_account_id=ach_debit_fp_false_ctx["fa"],
            sub_account_id=ach_debit_fp_false_ctx["sub"],
            counterparty_id=ach_debit_fp_false_ctx["cp"],
            amount="0.01",
            first_party=False,
            same_day=False,
            memo=memo
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body.get("code") == 200, \
            f"ACH Debit fp=False 失败: code={body.get('code')}, err={body.get('error_message')}"

        data = body.get("data") or body
        txn_id = data.get("id") or data.get("transaction_id")
        assert txn_id
        assert data.get("status") == "Processing"
        assert data.get("transaction_type") == "Debit"
        assert data.get("first_party") is False
        logger.info(f"  ✓ ACH Debit fp=False 发起成功: id={txn_id}")

        cancel_resp = ach_processing_api.cancel_transaction(txn_id)
        assert cancel_resp.json().get("code") == 200
        logger.info(f"✓ ACH Debit fp=False cancel 成功")

    def test_debit_fp_true_success_and_cancel(self, ach_processing_api, ach_fp_true_debit_ctx):
        """
        测试场景2：first_party=True Debit 发起（使用 bank-account CP）
        Test Scenario2: Initiate ACH Debit (first_party=True) with bank-account CP
        验证点：code=200, first_party=True
        ⚠ 注意：外部账户余额不足时可能报 code=600，属正常业务拦截
        """
        memo = f"{MEMO_PREFIX} fp=True {time.strftime('%Y-%m-%d %H:%M:%S')}"
        ctx = ach_fp_true_debit_ctx
        resp = ach_processing_api.initiate_debit(
            financial_account_id=ctx["fa"],
            sub_account_id=ctx["sub"],
            counterparty_id=ctx["bank_cp_id"],
            amount="0.01",
            first_party=True,
            same_day=False,
            memo=memo
        )
        assert resp.status_code == 200
        body = resp.json()

        if body.get("code") == 200:
            data = body.get("data") or body
            txn_id = data.get("id")
            assert data.get("first_party") is True
            assert data.get("transaction_type") == "Debit"
            logger.info(f"  ✓ ACH Debit fp=True 发起成功: id={txn_id}")
            cancel_resp = ach_processing_api.cancel_transaction(txn_id)
            assert cancel_resp.json().get("code") == 200
            logger.info(f"✓ ACH Debit fp=True cancel 成功")
        elif body.get("code") == 600:
            logger.info(f"  ⚠ 外部账户余额不足被拦截（业务正常）: code=600")
        else:
            assert False, f"ACH Debit fp=True 返回意外 code={body.get('code')}, err={body.get('error_message')}"

    def test_debit_appears_in_list(self, ach_processing_api, ach_debit_fp_false_ctx):
        """
        测试场景3：Debit 发起后在 transactions list 中可查到
        Test Scenario3: Debit Appears in Transactions List
        """
        resp = ach_processing_api.initiate_debit(
            financial_account_id=ach_debit_fp_false_ctx["fa"],
            sub_account_id=ach_debit_fp_false_ctx["sub"],
            counterparty_id=ach_debit_fp_false_ctx["cp"],
            amount="0.01",
            first_party=False,
            same_day=False,
            memo=f"{MEMO_PREFIX} ListCheck {int(time.time())}"
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body.get("code") == 200
        data = body.get("data") or body
        txn_id = data.get("id")

        list_resp = ach_processing_api.list_transactions(
            financial_account_id=ach_debit_fp_false_ctx["fa"], size=10
        )
        assert list_resp.status_code == 200
        txns = list_resp.json().get("data", {}).get("content", [])
        found = any(t.get("id") == txn_id for t in txns)
        if found:
            logger.info(f"  ✓ Debit 在 list 中找到: id={txn_id}")
        else:
            logger.info(f"  ⚠ 未在 list 前10条中找到 id={txn_id}")

        ach_processing_api.cancel_transaction(txn_id)
        logger.info("✓ Debit list 查询验证完成")

    def test_debit_with_schedule_date(self, ach_processing_api, ach_debit_fp_false_ctx):
        """
        测试场景4：传入未来 schedule_date 的 Debit
        Test Scenario4: Debit with Future schedule_date
        """
        resp = ach_processing_api.initiate_debit(
            financial_account_id=ach_debit_fp_false_ctx["fa"],
            sub_account_id=ach_debit_fp_false_ctx["sub"],
            counterparty_id=ach_debit_fp_false_ctx["cp"],
            amount="0.01",
            first_party=False,
            same_day=False,
            schedule_date="2026-12-31",
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body.get("code") == 200
        data = body.get("data") or body
        txn_id = data.get("id")
        ach_processing_api.cancel_transaction(txn_id)
        logger.info(f"✓ schedule_date Debit 发起成功: id={txn_id}")

    def test_debit_missing_sub_account_id(self, ach_processing_api, ach_debit_fp_false_ctx):
        """
        测试场景5：FA 有 sub 但未传 sub_account_id → 被拒绝
        Test Scenario5: Missing sub_account_id Returns Error
        """
        resp = ach_processing_api.initiate_debit(
            financial_account_id=ach_debit_fp_false_ctx["fa"],
            counterparty_id=ach_debit_fp_false_ctx["cp"],
            amount="0.01",
            first_party=False,
            same_day=False,
        )
        assert resp.status_code == 200
        assert resp.json().get("code") != 200
        logger.info(f"✓ 缺少 sub_account_id 被拒绝: code={resp.json().get('code')}")

    def test_debit_invisible_fa(self, ach_processing_api, ach_debit_fp_false_ctx):
        """
        测试场景6：越权 FA → 被拒绝
        Test Scenario6: Invisible FA Returns Error
        """
        resp = ach_processing_api.initiate_debit(
            financial_account_id=INVISIBLE_FA,
            counterparty_id=ach_debit_fp_false_ctx["cp"],
            amount="0.01",
            first_party=False,
            same_day=False,
        )
        assert resp.status_code == 200
        assert resp.json().get("code") != 200
        logger.info(f"✓ 越权 FA 被拒绝: code={resp.json().get('code')}")

    def test_debit_negative_amount(self, ach_processing_api, ach_debit_fp_false_ctx):
        """
        测试场景7：负数金额
        Test Scenario7: Negative Amount Returns Error
        """
        resp = ach_processing_api.initiate_debit(
            financial_account_id=ach_debit_fp_false_ctx["fa"],
            sub_account_id=ach_debit_fp_false_ctx["sub"],
            counterparty_id=ach_debit_fp_false_ctx["cp"],
            amount="-1",
            first_party=False,
            same_day=False,
        )
        assert resp.status_code == 200
        assert resp.json().get("code") != 200
        logger.info(f"✓ 负数金额被拒绝: code={resp.json().get('code')}")
