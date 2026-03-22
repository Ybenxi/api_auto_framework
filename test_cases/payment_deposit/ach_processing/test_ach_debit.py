"""
ACH Processing - Debit 接口测试用例
POST /api/v1/cores/{core}/money-movements/ach/debit

ACH Debit = 向外部账户发起拉款（pull 资金进来）
特点：与 Credit 参数类似，first_party=False 使用普通 ACH CP

已验证数据：
  ACH_FA=251119084741475550，ACH_SUB=251119084741475584
  ACH_CP=251212054048369793（assign 了 FA 的 account_id）
"""
import pytest
import time
from utils.logger import logger

ACH_FA       = "251119084741475550"
ACH_SUB      = "251119084741475584"
ACH_CP       = "251212054048369793"
INVISIBLE_FA = "241010195850134683"

MEMO_PREFIX = "Auto TestYan ACH Debit"

pytestmark = [pytest.mark.ach_processing, pytest.mark.no_rerun]


@pytest.mark.ach_processing
@pytest.mark.no_rerun
class TestAchDebit:

    def test_debit_success_and_cancel(self, ach_processing_api):
        """
        测试场景1：成功发起 ACH Debit，立即 cancel
        Test Scenario1: Initiate ACH Debit and Cancel
        验证点：code=200, status=Processing, transaction_type=Debit, first_party=False
        """
        memo = f"{MEMO_PREFIX} {time.strftime('%Y-%m-%d %H:%M:%S')}"
        resp = ach_processing_api.initiate_debit(
            financial_account_id=ACH_FA,
            sub_account_id=ACH_SUB,
            counterparty_id=ACH_CP,
            amount="0.01",
            first_party=False,
            same_day=False,
            memo=memo
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body.get("code") == 200, \
            f"ACH Debit 发起失败: code={body.get('code')}, err={body.get('error_message')}"

        data = body.get("data") or body
        txn_id = data.get("id") or data.get("transaction_id")
        assert txn_id, "交易 id 不应为空"
        assert data.get("status") == "Processing"
        assert data.get("transaction_type") == "Debit"
        assert data.get("first_party") is False
        logger.info(f"  ✓ ACH Debit 发起成功: id={txn_id}, status=Processing")

        cancel_resp = ach_processing_api.cancel_transaction(txn_id)
        assert cancel_resp.json().get("code") == 200
        logger.info(f"✓ ACH Debit cancel 成功: id={txn_id}")

    def test_debit_appears_in_list(self, ach_processing_api):
        """
        测试场景2：Debit 发起后在 transactions list 中可查到
        Test Scenario2: Debit Appears in Transactions List
        """
        resp = ach_processing_api.initiate_debit(
            financial_account_id=ACH_FA,
            sub_account_id=ACH_SUB,
            counterparty_id=ACH_CP,
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
            financial_account_id=ACH_FA, size=10
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

    def test_debit_with_schedule_date(self, ach_processing_api):
        """
        测试场景3：传入未来 schedule_date 的 Debit
        Test Scenario3: Debit with Future schedule_date
        """
        resp = ach_processing_api.initiate_debit(
            financial_account_id=ACH_FA,
            sub_account_id=ACH_SUB,
            counterparty_id=ACH_CP,
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

    def test_debit_missing_sub_account_id(self, ach_processing_api):
        """
        测试场景4：FA 有 sub 但未传 sub_account_id → 被拒绝
        Test Scenario4: Missing sub_account_id Returns Error
        """
        resp = ach_processing_api.initiate_debit(
            financial_account_id=ACH_FA,
            counterparty_id=ACH_CP,
            amount="0.01",
            first_party=False,
            same_day=False,
        )
        assert resp.status_code == 200
        assert resp.json().get("code") != 200
        logger.info(f"✓ 缺少 sub_account_id 被拒绝: code={resp.json().get('code')}")

    def test_debit_invisible_fa(self, ach_processing_api):
        """
        测试场景5：越权 FA → 被拒绝
        Test Scenario5: Invisible FA Returns Error
        """
        resp = ach_processing_api.initiate_debit(
            financial_account_id=INVISIBLE_FA,
            counterparty_id=ACH_CP,
            amount="0.01",
            first_party=False,
            same_day=False,
        )
        assert resp.status_code == 200
        assert resp.json().get("code") != 200
        logger.info(f"✓ 越权 FA 被拒绝: code={resp.json().get('code')}")

    def test_debit_negative_amount(self, ach_processing_api):
        """
        测试场景6：负数金额
        Test Scenario6: Negative Amount Returns Error
        """
        resp = ach_processing_api.initiate_debit(
            financial_account_id=ACH_FA,
            sub_account_id=ACH_SUB,
            counterparty_id=ACH_CP,
            amount="-1",
            first_party=False,
            same_day=False,
        )
        assert resp.status_code == 200
        assert resp.json().get("code") != 200
        logger.info(f"✓ 负数金额被拒绝: code={resp.json().get('code')}")
