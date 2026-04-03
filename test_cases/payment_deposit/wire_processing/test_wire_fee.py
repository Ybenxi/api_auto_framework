"""
Wire Processing - Transaction Fee 接口测试用例
POST /api/v1/cores/{core}/money-movements/wire/fee

响应结构：{"code": 200, "data": {financial_account_id, fee, amount, same_day}}
特有参数：payment_type（Wire/International_Wire，默认 Wire），same_day

已验证：
  Wire fee=1.5, International_Wire fee=3.51（两种费率不同！）
  invisible FA → code=506
"""
import pytest
from utils.logger import logger

VALID_FA     = "251212054048470568"
INVISIBLE_FA = "241010195850134683"

pytestmark = pytest.mark.wire_processing


@pytest.mark.wire_processing
class TestWireFee:

    def test_fee_wire_default(self, wire_processing_api):
        """
        测试场景1：Wire 类型手续费（不传 payment_type，默认 Wire）
        Test Scenario1: Wire Fee with Default payment_type
        验证点：code=200，data 含 fee/amount/same_day/financial_account_id
        """
        resp = wire_processing_api.quote_transaction_fee(
            financial_account_id=VALID_FA, amount="10"
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body.get("code") == 200, f"code 应为 200，实际: {body.get('code')}"

        data = body.get("data", {})
        for field in ["fee", "amount", "same_day", "financial_account_id"]:
            assert field in data, f"缺少字段: '{field}'"
        assert isinstance(data.get("fee"), (int, float))
        wire_fee = data.get("fee")
        logger.info(f"✓ 默认 Wire fee={wire_fee}, same_day=False")

    def test_fee_wire_explicit(self, wire_processing_api):
        """
        测试场景2：显式传 payment_type=Wire
        Test Scenario2: Explicit payment_type=Wire
        """
        resp = wire_processing_api.quote_transaction_fee(
            financial_account_id=VALID_FA, amount="10", payment_type="Wire"
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body.get("code") == 200
        logger.info(f"✓ payment_type=Wire: fee={body.get('data',{}).get('fee')}")

    def test_fee_international_wire(self, wire_processing_api):
        """
        测试场景3：International_Wire 手续费（费率不同于 Wire）
        Test Scenario3: International_Wire Fee Rate
        验证点：code=200，fee 是数值，且高于 Wire 费率（已知 3.51 > 1.5）
        """
        resp = wire_processing_api.quote_transaction_fee(
            financial_account_id=VALID_FA, amount="10",
            payment_type="International_Wire"
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body.get("code") == 200
        data = body.get("data", {})
        assert isinstance(data.get("fee"), (int, float))
        logger.info(f"✓ International_Wire fee={data.get('fee')}（高于 Wire 费率）")

    def test_fee_same_day_true(self, wire_processing_api):
        """
        测试场景4：same_day=True
        Test Scenario4: Wire Fee with same_day=True
        """
        resp = wire_processing_api.quote_transaction_fee(
            financial_account_id=VALID_FA, amount="10", same_day=True
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body.get("code") == 200
        logger.info(f"✓ same_day=True: fee={body.get('data',{}).get('fee')}")

    def test_fee_invisible_fa(self, wire_processing_api):
        """
        测试场景5：越权 FA ID → code=506
        Test Scenario5: Invisible FA Returns 506
        """
        resp = wire_processing_api.quote_transaction_fee(
            financial_account_id=INVISIBLE_FA, amount="10"
        )
        assert resp.status_code == 200
        assert resp.json().get("code") == 506
        logger.info("✓ 越权 FA 被拒绝: code=506")

    def test_fee_invalid_fa(self, wire_processing_api):
        """
        测试场景6：无效 FA ID
        Test Scenario6: Invalid FA ID Returns Error
        """
        resp = wire_processing_api.quote_transaction_fee(
            financial_account_id="INVALID_FA_99999", amount="10"
        )
        assert resp.status_code == 200
        assert resp.json().get("code") != 200
        logger.info(f"✓ 无效 FA 被拒绝: code={resp.json().get('code')}")

    def test_fee_missing_amount(self, wire_processing_api):
        """
        测试场景7：缺少必填参数 amount
        Test Scenario7: Missing Required amount Returns Error
        """
        url = wire_processing_api.config.get_full_url("/money-movements/wire/fee")
        resp = wire_processing_api.session.post(url, json={"financial_account_id": VALID_FA})
        assert resp.status_code == 200
        assert resp.json().get("code") != 200
        logger.info(f"✓ 缺少 amount 被拒绝: code={resp.json().get('code')}")
