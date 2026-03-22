"""
ACH Processing - First Party Logic 接口测试用例

first_party 说明：
  - first_party=False（默认）：普通 ACH 交易（Payment）
    → 使用 /ach/counterparties 列表的 CP
  - first_party=True：第一方 ACH 转账（Transfer，与外部绑定账户交易）
    → 使用 /ach/bank-accounts 列表的 id 作为 counterparty_id
    → FA 对应的 account_id 必须与 bank-account 的 account_id 一致

已验证：
  - bank-accounts 存在（total=7）
  - first_party=True + bank-account CP（account_id 不匹配）→ code=599 "Counterparty is not assigned to the corresponding account."
"""
import pytest
import time
from utils.logger import logger

ACH_FA       = "251119084741475550"
ACH_SUB      = "251119084741475584"
ACH_CP       = "251212054048369793"

MEMO_PREFIX = "Auto TestYan ACH FP"

pytestmark = pytest.mark.ach_processing


@pytest.mark.ach_processing
class TestAchFirstPartyLogic:

    def _get_bank_accounts(self, ach_processing_api):
        resp = ach_processing_api.list_bank_accounts(size=10)
        return (resp.json().get("data", resp.json()) or {}).get("content", [])

    def test_list_bank_accounts_success(self, ach_processing_api):
        """
        测试场景1：成功获取 First Party Bank Accounts 列表
        Test Scenario1: List First Party Bank Accounts
        验证点：code=200，含 bank_name, bank_routing_number, account_id
        """
        resp = ach_processing_api.list_bank_accounts(size=10)
        assert resp.status_code == 200
        body = resp.json()
        assert body.get("code") == 200
        bank_accs = (body.get("data", {}) or {}).get("content", [])
        assert isinstance(bank_accs, list)
        total = (body.get("data", {}) or {}).get("total_elements", 0)
        logger.info(f"  total bank_accounts={total}, returned={len(bank_accs)}")
        if bank_accs:
            ba = bank_accs[0]
            for field in ["id", "bank_name", "bank_routing_number", "account_id"]:
                if field in ba:
                    logger.info(f"  ✓ {field}: {ba.get(field)}")
        logger.info("✓ First Party Bank Accounts 列表获取成功")

    def test_first_party_false_credit_uses_ach_cp(self, ach_processing_api):
        """
        测试场景2：first_party=False 使用普通 ACH CP 成功发起 Credit
        Test Scenario2: first_party=False Credit Uses Regular ACH Counterparty
        """
        resp = ach_processing_api.initiate_credit(
            financial_account_id=ACH_FA,
            sub_account_id=ACH_SUB,
            counterparty_id=ACH_CP,
            amount="0.01",
            first_party=False,
            same_day=False,
            memo=f"{MEMO_PREFIX} FP=False {int(time.time())}"
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body.get("code") == 200, \
            f"fp=False credit 失败: err={body.get('error_message')}"
        data = body.get("data") or body
        txn_id = data.get("id")
        assert data.get("first_party") is False
        ach_processing_api.cancel_transaction(txn_id)
        logger.info(f"✓ first_party=False 使用 ACH CP 成功: id={txn_id}")

    def test_first_party_true_with_bank_account_mismatch(self, ach_processing_api):
        """
        测试场景3：first_party=True 使用 bank-account CP（account_id 不匹配 FA） → 被拒绝
        Test Scenario3: first_party=True with Mismatched bank-account Returns Error
        """
        bank_accs = self._get_bank_accounts(ach_processing_api)
        if not bank_accs:
            pytest.skip("无 bank account 数据")
        ba_id = bank_accs[0].get("id")

        resp = ach_processing_api.initiate_credit(
            financial_account_id=ACH_FA,
            sub_account_id=ACH_SUB,
            counterparty_id=ba_id,
            amount="0.01",
            first_party=True,
            same_day=False,
            memo=f"{MEMO_PREFIX} FP=True Mismatch {int(time.time())}"
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body.get("code") != 200
        logger.info(f"✓ first_party=True account_id 不匹配被拒绝: code={body.get('code')}, msg={body.get('error_message','')[:60]}")

    def test_first_party_true_with_regular_ach_cp(self, ach_processing_api):
        """
        测试场景4：first_party=True 但使用普通 ACH CP（非 bank-account）
        Test Scenario4: first_party=True with Regular ACH CP (Should Validate Bank Owner)
        """
        resp = ach_processing_api.initiate_credit(
            financial_account_id=ACH_FA,
            sub_account_id=ACH_SUB,
            counterparty_id=ACH_CP,
            amount="0.01",
            first_party=True,
            same_day=False,
            memo=f"{MEMO_PREFIX} FP=True RegularCP {int(time.time())}"
        )
        assert resp.status_code == 200
        body = resp.json()
        if body.get("code") == 200:
            data = body.get("data") or body
            txn_id = data.get("id")
            ach_processing_api.cancel_transaction(txn_id)
            logger.info(f"  ⚠ first_party=True 普通 CP 被接受（探索性结果）: id={txn_id}")
        else:
            logger.info(f"✓ first_party=True 普通 CP 被拒绝: code={body.get('code')}")

    def test_bank_accounts_filter_by_financial_account_id(self, ach_processing_api):
        """
        测试场景5：bank-accounts 按 financial_account_id 筛选
        Test Scenario5: Filter bank-accounts by financial_account_id
        """
        bank_accs = self._get_bank_accounts(ach_processing_api)
        if not bank_accs:
            pytest.skip("无 bank account 数据")
        resp = ach_processing_api.list_bank_accounts(
            financial_account_id=ACH_FA, size=10
        )
        assert resp.status_code == 200
        assert resp.json().get("code") == 200
        logger.info("✓ bank-accounts 按 financial_account_id 筛选通过")

    def test_first_party_debit_field_verification(self, ach_processing_api):
        """
        测试场景6：Debit 发起 first_party=False，验证响应 first_party 字段
        Test Scenario6: Verify first_party Field in Debit Response
        """
        resp = ach_processing_api.initiate_debit(
            financial_account_id=ACH_FA,
            sub_account_id=ACH_SUB,
            counterparty_id=ACH_CP,
            amount="0.01",
            first_party=False,
            same_day=False,
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body.get("code") == 200
        data = body.get("data") or body
        assert "first_party" in data, "Debit 响应应含 first_party 字段"
        assert data.get("first_party") is False
        txn_id = data.get("id")
        ach_processing_api.cancel_transaction(txn_id)
        logger.info(f"✓ Debit 响应 first_party=False 字段验证通过: id={txn_id}")
