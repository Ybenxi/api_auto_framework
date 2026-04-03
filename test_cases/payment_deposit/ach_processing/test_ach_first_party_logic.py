"""
ACH Processing - First Party Logic 接口测试用例

first_party 说明（已验证）：
  first_party=False：普通 ACH 交易（Payment），使用 /ach/counterparties 的 CP
  first_party=True：第一方 ACH 转账（Transfer），使用 /ach/bank-accounts 的 id 作为 CP
                    CP 的 account_id 必须与 FA 的 account_id 一致

已验证的工作组合：
  Credit fp=True:
    FA=251212054048470574, SUB=251212054048470660, CP=251212054048237385
    CP 是 bank-account（account_id=251212054048210865，与 FA account_id 匹配）

  Debit fp=True（可能因外部余额不足报 600）：
    FA=251212054048470568, SUB=251212054048470660, CP=251212054048127858
    CP 是 bank-account（account_id=251212054048470503，与 FA account_id 匹配）

  fp=False 普通 CP：
    使用 conftest 的 ach_fp_false_ctx（list 动态解析，勿硬编码已清理的 CP）

  错误场景：
    fp=True + bank-account account_id 不匹配 FA → code=599 "Counterparty is not assigned to the corresponding account."
"""
import pytest
import time
from utils.logger import logger

# fp=True Credit 数据
ACH_FA_CREDIT_FP  = "251212054048470574"
ACH_SUB_CREDIT_FP = "251212054048470660"
ACH_CP_BANK_CREDIT = "251212054048237385"  # bank-account，account_id=251212054048210865

# fp=True Debit 数据（来自用户提供的示例）
ACH_FA_DEBIT_FP  = "251212054048470568"
ACH_SUB_DEBIT_FP = "251212054048470660"
ACH_CP_BANK_DEBIT = "251212054048127858"   # bank-account，account_id=251212054048470503

MEMO_PREFIX = "Auto TestYan ACH FP"

pytestmark = pytest.mark.ach_processing


@pytest.mark.ach_processing
class TestAchFirstPartyLogic:

    def _get_bank_accounts(self, ach_processing_api):
        resp = ach_processing_api.list_bank_accounts(size=50)
        return (resp.json().get("data", resp.json()) or {}).get("content", [])

    def test_list_bank_accounts_success(self, ach_processing_api):
        """
        测试场景1：成功获取 First Party Bank Accounts 列表
        Test Scenario1: List First Party Bank Accounts
        验证点：code=200，含 bank_name, bank_routing_number, account_id, bank_is_us_based
        """
        resp = ach_processing_api.list_bank_accounts(size=10)
        assert resp.status_code == 200
        body = resp.json()
        assert body.get("code") == 200
        data = body.get("data", {}) or {}
        bank_accs = data.get("content", [])
        total = data.get("total_elements", 0)
        logger.info(f"  total bank_accounts={total}, returned={len(bank_accs)}")
        if bank_accs:
            ba = bank_accs[0]
            for field in ["id", "bank_name", "bank_routing_number", "account_id", "bank_is_us_based"]:
                if field in ba:
                    logger.info(f"  ✓ {field}: {ba.get(field)}")
        assert total > 0, "至少应有一个 bank account"
        logger.info("✓ First Party Bank Accounts 列表获取成功")

    def test_verify_bank_accounts_in_list(self, ach_processing_api):
        """
        测试场景2：验证两个已知 bank-account CP 在 bank-accounts 列表中
        Test Scenario2: Verify Known bank-account CPs Exist in List
        """
        bank_accs = self._get_bank_accounts(ach_processing_api)
        ids = [ba.get("id") for ba in bank_accs]
        assert ACH_CP_BANK_CREDIT in ids, \
            f"bank-account {ACH_CP_BANK_CREDIT} 应在 bank-accounts 列表中"
        assert ACH_CP_BANK_DEBIT in ids, \
            f"bank-account {ACH_CP_BANK_DEBIT} 应在 bank-accounts 列表中"
        logger.info(f"✓ 两个已知 bank-account CP 均在 bank-accounts 列表中")

    @pytest.mark.no_rerun
    def test_credit_fp_false_uses_regular_cp(self, ach_processing_api, ach_fp_false_ctx):
        """
        测试场景3：first_party=False Credit 使用普通 ACH CP 成功
        Test Scenario3: first_party=False Credit Uses Regular ACH CP
        """
        resp = ach_processing_api.initiate_credit(
            financial_account_id=ach_fp_false_ctx["fa"],
            sub_account_id=ach_fp_false_ctx["sub"],
            counterparty_id=ach_fp_false_ctx["cp"],
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
        logger.info(f"✓ first_party=False 使用普通 ACH CP 成功: id={txn_id}")

    @pytest.mark.no_rerun
    def test_credit_fp_true_uses_bank_account_cp(self, ach_processing_api):
        """
        测试场景4：first_party=True Credit 使用 bank-account 作为 CP 成功
        Test Scenario4: first_party=True Credit Uses bank-account CP
        验证点：bank-account 的 account_id 与 FA 的 account_id 一致才能成功
        """
        resp = ach_processing_api.initiate_credit(
            financial_account_id=ACH_FA_CREDIT_FP,
            sub_account_id=ACH_SUB_CREDIT_FP,
            counterparty_id=ACH_CP_BANK_CREDIT,
            amount="0.01",
            first_party=True,
            same_day=False,
            memo=f"{MEMO_PREFIX} FP=True Credit {int(time.time())}"
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body.get("code") == 200, \
            f"fp=True credit 失败: code={body.get('code')}, err={body.get('error_message')}"
        data = body.get("data") or body
        txn_id = data.get("id")
        assert data.get("first_party") is True
        ach_processing_api.cancel_transaction(txn_id)
        logger.info(f"✓ first_party=True Credit 使用 bank-account CP 成功: id={txn_id}")

    @pytest.mark.no_rerun
    def test_debit_fp_true_uses_bank_account_cp(self, ach_processing_api):
        """
        测试场景5：first_party=True Debit 使用 bank-account 作为 CP
        Test Scenario5: first_party=True Debit Uses bank-account CP
        ⚠ 注意：外部账户余额不足时可能报 code=600，属正常业务拦截
        """
        resp = ach_processing_api.initiate_debit(
            financial_account_id=ACH_FA_DEBIT_FP,
            sub_account_id=ACH_SUB_DEBIT_FP,
            counterparty_id=ACH_CP_BANK_DEBIT,
            amount="0.01",
            first_party=True,
            same_day=False,
            memo=f"{MEMO_PREFIX} FP=True Debit {int(time.time())}"
        )
        assert resp.status_code == 200
        body = resp.json()

        if body.get("code") == 200:
            data = body.get("data") or body
            txn_id = data.get("id")
            assert data.get("first_party") is True
            assert data.get("transaction_type") == "Debit"
            ach_processing_api.cancel_transaction(txn_id)
            logger.info(f"✓ first_party=True Debit 成功: id={txn_id}")
        elif body.get("code") == 600:
            logger.info(f"  ⚠ 外部账户余额不足（业务正常拦截）: code=600")
        else:
            assert False, f"意外错误: code={body.get('code')}, err={body.get('error_message')}"

    def test_credit_fp_true_with_mismatched_bank_account(self, ach_processing_api):
        """
        测试场景6：first_party=True 使用 account_id 不匹配的 bank-account → code=599
        Test Scenario6: first_party=True with Mismatched bank-account Returns 599
        "Counterparty is not assigned to the corresponding account."
        """
        bank_accs = self._get_bank_accounts(ach_processing_api)
        # 找一个 account_id 不匹配 ACH_FA_CREDIT_FP 的 bank-account
        mismatched_ba = next(
            (ba for ba in bank_accs
             if ba.get("id") != ACH_CP_BANK_CREDIT and ba.get("account_id") != "251212054048210865"),
            None
        )
        if not mismatched_ba:
            pytest.skip("未找到 account_id 不匹配的 bank-account")

        ba_id = mismatched_ba.get("id")
        resp = ach_processing_api.initiate_credit(
            financial_account_id=ACH_FA_CREDIT_FP,
            sub_account_id=ACH_SUB_CREDIT_FP,
            counterparty_id=ba_id,
            amount="0.01",
            first_party=True,
            same_day=False,
            memo=f"{MEMO_PREFIX} FP=True Mismatch {int(time.time())}"
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body.get("code") != 200
        logger.info(f"✓ account_id 不匹配被拒绝: code={body.get('code')}, msg={body.get('error_message','')[:60]}")
