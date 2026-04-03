"""
ACH Processing - Transaction Fee 接口测试用例
POST /api/v1/cores/{core}/money-movements/ach/fee

ACH fee 有 5 个必填参数（比其他 payment 模块多 first_party 和 transaction_type）
已验证费率：
  Credit  fp=False: 3.5
  Debit   fp=False: 0.1
  Credit  fp=True:  3.51
  Debit   fp=True:  3.51
"""
import pytest
from utils.logger import logger

VALID_FA     = "251212054048470568"
INVISIBLE_FA = "241010195850134683"

pytestmark = pytest.mark.ach_processing


@pytest.mark.ach_processing
class TestAchFee:

    def test_fee_credit_not_first_party(self, ach_processing_api):
        """
        测试场景1：Credit 交易，first_party=False 手续费
        Test Scenario1: Credit Fee with first_party=False
        """
        resp = ach_processing_api.quote_transaction_fee(
            financial_account_id=VALID_FA, amount="10",
            same_day=False, first_party=False, transaction_type="Credit"
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body.get("code") == 200
        data = body.get("data", {})
        for field in ["fee", "amount", "same_day", "first_party", "transaction_type", "financial_account_id"]:
            assert field in data, f"缺少字段: '{field}'"
        assert isinstance(data.get("fee"), (int, float))
        credit_fp_false_fee = data.get("fee")
        logger.info(f"✓ Credit fp=False: fee={credit_fp_false_fee}")

    def test_fee_debit_not_first_party(self, ach_processing_api):
        """
        测试场景2：Debit 交易，first_party=False 手续费（费率低于 Credit）
        Test Scenario2: Debit Fee with first_party=False
        """
        resp = ach_processing_api.quote_transaction_fee(
            financial_account_id=VALID_FA, amount="10",
            same_day=False, first_party=False, transaction_type="Debit"
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body.get("code") == 200
        debit_fee = body.get("data", {}).get("fee")
        assert isinstance(debit_fee, (int, float))
        logger.info(f"✓ Debit fp=False: fee={debit_fee}（低于 Credit 费率）")

    def test_fee_credit_first_party(self, ach_processing_api):
        """
        测试场景3：Credit 交易，first_party=True（费率与 fp=False 不同）
        Test Scenario3: Credit Fee with first_party=True
        """
        resp = ach_processing_api.quote_transaction_fee(
            financial_account_id=VALID_FA, amount="10",
            same_day=False, first_party=True, transaction_type="Credit"
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body.get("code") == 200
        data = body.get("data", {})
        assert data.get("first_party") is True
        logger.info(f"✓ Credit fp=True: fee={data.get('fee')}")

    def test_fee_debit_first_party(self, ach_processing_api):
        """
        测试场景4：Debit 交易，first_party=True
        Test Scenario4: Debit Fee with first_party=True
        """
        resp = ach_processing_api.quote_transaction_fee(
            financial_account_id=VALID_FA, amount="10",
            same_day=False, first_party=True, transaction_type="Debit"
        )
        assert resp.status_code == 200
        assert resp.json().get("code") == 200
        logger.info(f"✓ Debit fp=True: fee={resp.json().get('data',{}).get('fee')}")

    def test_fee_same_day_true(self, ach_processing_api):
        """
        测试场景5：same_day=True（当天到账，可能影响手续费）
        Test Scenario5: same_day=True May Affect Fee
        """
        resp = ach_processing_api.quote_transaction_fee(
            financial_account_id=VALID_FA, amount="10",
            same_day=True, first_party=False, transaction_type="Credit"
        )
        assert resp.status_code == 200
        assert resp.json().get("code") == 200
        logger.info(f"✓ same_day=True: fee={resp.json().get('data',{}).get('fee')}")

    def test_fee_invisible_fa(self, ach_processing_api):
        """
        测试场景6：越权 FA ID → code=506
        Test Scenario6: Invisible FA Returns 506
        """
        resp = ach_processing_api.quote_transaction_fee(
            financial_account_id=INVISIBLE_FA, amount="10",
            same_day=False, first_party=False, transaction_type="Credit"
        )
        assert resp.status_code == 200
        assert resp.json().get("code") == 506
        logger.info("✓ 越权 FA 被拒绝: code=506")

    def test_fee_invalid_transaction_type(self, ach_processing_api):
        """
        测试场景7：transaction_type 枚举值错误
        Test Scenario7: Invalid transaction_type Returns Error
        """
        url = ach_processing_api.config.get_full_url("/money-movements/ach/fee")
        resp = ach_processing_api.session.post(url, json={
            "financial_account_id": VALID_FA, "amount": "10",
            "same_day": False, "first_party": False, "transaction_type": "INVALID_TYPE"
        })
        assert resp.status_code == 200
        assert resp.json().get("code") != 200
        logger.info(f"✓ 无效 transaction_type 被拒绝: code={resp.json().get('code')}")

    def test_fee_missing_transaction_type(self, ach_processing_api):
        """
        测试场景8：缺少必填 transaction_type（ACH fee 特有必填参数）
        Test Scenario8: Missing Required transaction_type Returns Error
        """
        url = ach_processing_api.config.get_full_url("/money-movements/ach/fee")
        resp = ach_processing_api.session.post(url, json={
            "financial_account_id": VALID_FA, "amount": "10",
            "same_day": False, "first_party": False
            # 缺少 transaction_type
        })
        assert resp.status_code == 200
        assert resp.json().get("code") != 200
        logger.info(f"✓ 缺少 transaction_type 被拒绝: code={resp.json().get('code')}")
