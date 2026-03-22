"""
ACH Processing - Credit 接口测试用例
POST /api/v1/cores/{core}/money-movements/ach/credit

ACH Credit = 向外部账户（counterparty）转账（推送资金）
特点：first_party=False 使用普通 ACH CP，first_party=True 使用 bank-account

已验证数据：
  ACH_FA=251119084741475550，ACH_SUB=251119084741475584
  ACH_CP=251212054048369793（assign=['250918043812871683'] = FA's account_id）
"""
import pytest
import time
from utils.logger import logger

ACH_FA       = "251119084741475550"
ACH_SUB      = "251119084741475584"
ACH_CP       = "251212054048369793"   # ACH CP，assign 了 FA 的 account_id
INVISIBLE_FA = "241010195850134683"

MEMO_PREFIX = "Auto TestYan ACH Credit"

pytestmark = [pytest.mark.ach_processing, pytest.mark.no_rerun]


@pytest.mark.ach_processing
@pytest.mark.no_rerun
class TestAchCredit:

    def test_credit_success_and_cancel(self, ach_processing_api):
        """
        测试场景1：成功发起 ACH Credit，立即 cancel
        Test Scenario1: Initiate ACH Credit and Cancel
        验证点：code=200, status=Processing, first_party=False, direction=Origination
        """
        memo = f"{MEMO_PREFIX} {time.strftime('%Y-%m-%d %H:%M:%S')}"
        resp = ach_processing_api.initiate_credit(
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
            f"ACH Credit 发起失败: code={body.get('code')}, err={body.get('error_message')}"

        data = body.get("data") or body
        txn_id = data.get("id") or data.get("transaction_id")
        assert txn_id, "交易 id 不应为空"
        assert data.get("status") == "Processing"
        assert data.get("direction") == "Origination"
        assert data.get("first_party") is False
        assert data.get("transaction_type") == "Credit"
        logger.info(f"  ✓ ACH Credit 发起成功: id={txn_id}, status=Processing")

        # cancel
        cancel_resp = ach_processing_api.cancel_transaction(txn_id)
        assert cancel_resp.json().get("code") == 200
        logger.info(f"✓ ACH Credit cancel 成功: id={txn_id}")

    def test_credit_response_fields(self, ach_processing_api):
        """
        测试场景2：验证 ACH Credit 响应字段（含 first_party, same_day, reversal_id）
        Test Scenario2: Verify ACH Credit Response Fields
        """
        resp = ach_processing_api.initiate_credit(
            financial_account_id=ACH_FA,
            sub_account_id=ACH_SUB,
            counterparty_id=ACH_CP,
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
        logger.info(f"✓ ACH Credit 响应字段验证通过")

    def test_credit_same_day_false(self, ach_processing_api):
        """
        测试场景3：same_day=False（非当天到账）发起
        Test Scenario3: Credit with same_day=False
        """
        resp = ach_processing_api.initiate_credit(
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
        assert data.get("same_day") is False
        txn_id = data.get("id")
        ach_processing_api.cancel_transaction(txn_id)
        logger.info(f"✓ same_day=False Credit 发起成功: id={txn_id}")

    def test_credit_with_schedule_date(self, ach_processing_api):
        """
        测试场景4：传入未来 schedule_date
        Test Scenario4: Credit with Future schedule_date
        """
        resp = ach_processing_api.initiate_credit(
            financial_account_id=ACH_FA,
            sub_account_id=ACH_SUB,
            counterparty_id=ACH_CP,
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

    def test_credit_missing_sub_account_id(self, ach_processing_api):
        """
        测试场景5：FA 有 sub 但未传 sub_account_id → code=599
        Test Scenario5: FA with Sub but Missing sub_account_id Returns Error
        """
        resp = ach_processing_api.initiate_credit(
            financial_account_id=ACH_FA,
            counterparty_id=ACH_CP,
            amount="0.01",
            first_party=False,
            same_day=False,
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body.get("code") != 200
        logger.info(f"✓ 缺少 sub_account_id 被拒绝: code={body.get('code')}, msg={body.get('error_message')}")

    def test_credit_invisible_fa(self, ach_processing_api):
        """
        测试场景6：越权 FA → 被拒绝
        Test Scenario6: Invisible FA Returns Error
        """
        resp = ach_processing_api.initiate_credit(
            financial_account_id=INVISIBLE_FA,
            counterparty_id=ACH_CP,
            amount="0.01",
            first_party=False,
            same_day=False,
        )
        assert resp.status_code == 200
        assert resp.json().get("code") != 200
        logger.info(f"✓ 越权 FA 被拒绝: code={resp.json().get('code')}")

    def test_credit_missing_counterparty(self, ach_processing_api):
        """
        测试场景7：缺少必填 counterparty_id
        Test Scenario7: Missing counterparty_id Returns Error
        """
        url = ach_processing_api.config.get_full_url("/money-movements/ach/credit")
        resp = ach_processing_api.session.post(url, json={
            "financial_account_id": ACH_FA,
            "sub_account_id": ACH_SUB,
            "amount": "0.01",
            "first_party": False,
            "same_day": False,
        })
        assert resp.status_code == 200
        assert resp.json().get("code") != 200
        logger.info(f"✓ 缺少 counterparty_id 被拒绝: code={resp.json().get('code')}")

    def test_credit_negative_amount(self, ach_processing_api):
        """
        测试场景8：负数金额 → 被拒绝
        Test Scenario8: Negative Amount Returns Error
        """
        resp = ach_processing_api.initiate_credit(
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
