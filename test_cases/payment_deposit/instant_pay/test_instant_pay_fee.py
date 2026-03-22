"""
Instant Pay - Transaction Fee 接口测试用例
POST /api/v1/cores/{core}/money-movements/instant-pay/fee

响应结构：{"code": 200, "data": {financial_account_id, fee, amount, same_day}}
已验证：FA=251212054048210705 fee=3.51, invisible FA → code=506
"""
import pytest
from utils.logger import logger

VALID_FA     = "251119084741475550"
INVISIBLE_FA = "241010195850134683"

pytestmark = pytest.mark.instant_pay


@pytest.mark.instant_pay
class TestInstantPayFee:

    def test_fee_success(self, instant_pay_api):
        """
        测试场景1：使用有效 FA 计算 Instant Pay 手续费
        Test Scenario1: Calculate Instant Pay Fee with Valid FA
        """
        resp = instant_pay_api.quote_transaction_fee(
            financial_account_id=VALID_FA, amount="10"
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body.get("code") == 200, f"code 应为 200，实际: {body.get('code')}"

        data = body.get("data", {})
        for field in ["fee", "amount", "same_day", "financial_account_id"]:
            assert field in data, f"缺少字段: '{field}'"
        assert isinstance(data.get("fee"), (int, float))
        assert isinstance(data.get("same_day"), bool)
        logger.info(f"✓ fee={data.get('fee')}, same_day=False")

    def test_fee_same_day_true(self, instant_pay_api):
        """
        测试场景2：same_day=True
        Test Scenario2: Fee with same_day=True
        """
        resp = instant_pay_api.quote_transaction_fee(
            financial_account_id=VALID_FA, amount="10", same_day=True
        )
        assert resp.status_code == 200
        assert resp.json().get("code") == 200
        logger.info(f"✓ same_day=True: fee={resp.json().get('data',{}).get('fee')}")

    def test_fee_various_amounts(self, instant_pay_api):
        """
        测试场景3：不同金额手续费计算
        Test Scenario3: Fee for Various Amounts
        """
        for amount in ["1", "100", "1000", "0.01"]:
            resp = instant_pay_api.quote_transaction_fee(
                financial_account_id=VALID_FA, amount=amount
            )
            assert resp.status_code == 200
            assert resp.json().get("code") == 200, f"amount={amount} failed"
            logger.info(f"  amount={amount}: fee={resp.json().get('data',{}).get('fee')}")
        logger.info("✓ 多金额手续费验证通过")

    def test_fee_invisible_fa(self, instant_pay_api):
        """
        测试场景4：越权 FA ID → code=506
        Test Scenario4: Invisible FA Returns 506
        """
        resp = instant_pay_api.quote_transaction_fee(
            financial_account_id=INVISIBLE_FA, amount="10"
        )
        assert resp.status_code == 200
        assert resp.json().get("code") == 506
        logger.info("✓ 越权 FA 被拒绝: code=506")

    def test_fee_invalid_fa(self, instant_pay_api):
        """
        测试场景5：无效 FA ID
        Test Scenario5: Invalid FA ID Returns Error
        """
        resp = instant_pay_api.quote_transaction_fee(
            financial_account_id="INVALID_FA_99999", amount="10"
        )
        assert resp.status_code == 200
        assert resp.json().get("code") != 200
        logger.info(f"✓ 无效 FA 被拒绝: code={resp.json().get('code')}")

    def test_fee_negative_amount(self, instant_pay_api):
        """
        测试场景6：负数金额
        Test Scenario6: Negative Amount Returns Error
        """
        resp = instant_pay_api.quote_transaction_fee(
            financial_account_id=VALID_FA, amount="-10"
        )
        assert resp.status_code == 200
        assert resp.json().get("code") != 200
        logger.info(f"✓ 负数金额被拒绝: code={resp.json().get('code')}")

    def test_fee_missing_amount(self, instant_pay_api):
        """
        测试场景7：缺少必填参数 amount
        Test Scenario7: Missing Required amount Returns Error
        """
        url = instant_pay_api.config.get_full_url("/money-movements/instant-pay/fee")
        resp = instant_pay_api.session.post(url, json={"financial_account_id": VALID_FA})
        assert resp.status_code == 200
        assert resp.json().get("code") != 200
        logger.info(f"✓ 缺少 amount 被拒绝: code={resp.json().get('code')}")
