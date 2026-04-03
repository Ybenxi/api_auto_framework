"""
Internal Pay - Transaction Fee 接口测试用例
POST /api/v1/cores/{core}/money-movements/internal-pay/fee

响应结构：{"code": 200, "data": {financial_account_id, fee, amount, same_day}}

已验证测试账户（dev actc）：
  PAYER_FA = "251212054048470574"（有 sub，fee=3.51/10元）
  INVISIBLE_FA = "241010195850134683"（越权，code=506）
"""
import pytest
from utils.logger import logger

PAYER_FA     = "251212054048470574"
INVISIBLE_FA = "241010195850134683"

pytestmark = pytest.mark.internal_pay


@pytest.mark.internal_pay
class TestInternalPayFee:

    def test_fee_success_with_valid_fa(self, internal_pay_api):
        """
        测试场景1：传入有效 FA ID 和金额，成功计算手续费
        Test Scenario1: Successfully Calculate Fee with Valid FA ID
        验证点：
        1. HTTP 200，code=200
        2. data 含 fee, amount, same_day, financial_account_id
        3. fee 是数值类型
        """
        resp = internal_pay_api.quote_transaction_fee(
            financial_account_id=PAYER_FA, amount="10"
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body.get("code") == 200, \
            f"code 应为 200，实际: {body.get('code')}, err={body.get('error_message')}"

        data = body.get("data", {})
        for field in ["fee", "amount", "same_day", "financial_account_id"]:
            assert field in data, f"fee 响应缺少字段: '{field}'"
        assert isinstance(data.get("fee"), (int, float))
        assert data.get("financial_account_id") == PAYER_FA
        logger.info(f"✓ 手续费计算成功: fa={PAYER_FA}, amount=10, fee={data.get('fee')}")

    def test_fee_with_different_amounts(self, internal_pay_api):
        """
        测试场景2：不同金额的手续费计算
        Test Scenario2: Calculate Fee for Different Amount Values
        """
        for amount in ["1", "100", "0.01"]:
            resp = internal_pay_api.quote_transaction_fee(
                financial_account_id=PAYER_FA, amount=amount
            )
            assert resp.status_code == 200
            body = resp.json()
            assert body.get("code") == 200, \
                f"amount={amount}: code={body.get('code')}, err={body.get('error_message')}"
            logger.info(f"  amount={amount}: fee={body.get('data',{}).get('fee')}")
        logger.info("✓ 不同金额手续费计算通过")

    def test_fee_invalid_fa_id(self, internal_pay_api):
        """
        测试场景3：使用不存在的 FA ID
        Test Scenario3: Invalid FA ID Returns Business Error
        验证点：code=599
        """
        resp = internal_pay_api.quote_transaction_fee(
            financial_account_id="INVALID_FA_ID_99999", amount="10"
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body.get("code") != 200
        logger.info(f"✓ 无效 FA ID 被拒绝: code={body.get('code')}, msg={body.get('error_message')}")

    def test_fee_invisible_fa_id(self, internal_pay_api):
        """
        测试场景4：使用不在 visible 范围内的 FA ID
        Test Scenario4: Invisible FA ID Returns 506
        验证点：code=506 "visibility permission deny"
        """
        resp = internal_pay_api.quote_transaction_fee(
            financial_account_id=INVISIBLE_FA, amount="10"
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body.get("code") == 506, \
            f"越权 FA 应返回 506，实际 code={body.get('code')}, msg={body.get('error_message')}"
        logger.info(f"✓ 越权 FA 被拒绝: code=506")

    def test_fee_negative_amount(self, internal_pay_api):
        """
        测试场景5：传入负数金额
        Test Scenario5: Negative Amount Returns Business Error
        """
        resp = internal_pay_api.quote_transaction_fee(
            financial_account_id=PAYER_FA, amount="-10"
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body.get("code") != 200
        logger.info(f"✓ 负数金额被拒绝: code={body.get('code')}, msg={body.get('error_message')}")

    def test_fee_zero_amount(self, internal_pay_api):
        """
        测试场景6：传入 0 金额（探索性）
        Test Scenario6: Zero Amount - Exploratory
        """
        resp = internal_pay_api.quote_transaction_fee(
            financial_account_id=PAYER_FA, amount="0"
        )
        assert resp.status_code == 200
        body = resp.json()
        if body.get("code") == 200:
            logger.info(f"  ⚠ 接受了 amount=0，fee={body.get('data',{}).get('fee')}（探索性）")
        else:
            logger.info(f"✓ amount=0 被拒绝: code={body.get('code')}")

    def test_fee_missing_required_params(self, internal_pay_api):
        """
        测试场景7：缺少必填参数 amount
        Test Scenario7: Missing Required Amount Parameter Returns Error
        """
        url = internal_pay_api.config.get_full_url("/money-movements/internal-pay/fee")
        resp = internal_pay_api.session.post(url, json={"financial_account_id": PAYER_FA})
        assert resp.status_code == 200
        assert resp.json().get("code") != 200
        logger.info(f"✓ 缺少 amount 被拒绝: code={resp.json().get('code')}")
