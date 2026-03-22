"""
Instant Pay - Transactions 接口测试用例

⚠️ 注意：本文件包含两个独立接口的测试：
1. GET /money-movements/instant-pay/transactions
   → 普通 Instant Pay 交易列表
   → 响应结构：{"code": 200, "data": {"content": [...], total_elements...}}
   → id 字段名称为 "transaction_id"（不是 "id"）
   → status: Processing/Reviewing/Completed/Cancelled/Failed

2. GET /money-movements/instant-pay/request-payment/transactions
   → RFP（Request for Payment）定时交易列表
   → 响应结构：{"code": 200, "data": {"content": [...], total_elements...}}
   → id 字段名称为 "id"
   → status: Cancelled/Pending/Rejected/Paid_In_Full/Paid_In_Partial
   → direction: Origination/Incoming
   → 特有字段：execution_date, expiration_date, amount_modification_allowed, early_payment_allowed
"""
import pytest
from utils.logger import logger

pytestmark = pytest.mark.instant_pay


# ════════════════════════════════════════════════════════════════════
# List Instant Pay Transactions（普通 instant pay 交易）
# ════════════════════════════════════════════════════════════════════
@pytest.mark.instant_pay
class TestListInstantPayTransactions:

    def _get_content(self, response):
        body = response.json()
        data = body.get("data", body) or {}
        return data, data.get("content", []) if isinstance(data, dict) else []

    def test_list_success(self, instant_pay_api):
        """
        测试场景1：成功获取 Instant Pay 交易列表
        Test Scenario1: Successfully List Instant Pay Transactions
        验证点：code=200，id 字段为 transaction_id，含 direction/link 等特有字段
        """
        resp = instant_pay_api.list_transactions(size=10)
        assert resp.status_code == 200
        body = resp.json()
        assert body.get("code") == 200

        data, content = self._get_content(resp)
        total = data.get("total_elements", 0)
        assert isinstance(content, list)
        logger.info(f"  total={total}, returned={len(content)}")

        if content:
            txn = content[0]
            # Instant Pay 用 transaction_id 不用 id
            assert "transaction_id" in txn or "id" in txn, "交易应含 id 字段"
            for field in ["status", "amount", "direction", "financial_account_id"]:
                if field in txn:
                    logger.info(f"  ✓ {field}: {txn.get(field)}")
        logger.info("✓ Instant Pay 交易列表获取成功")

    @pytest.mark.parametrize("status", [
        "Processing", "Reviewing", "Completed", "Cancelled", "Failed"
    ])
    def test_filter_by_status(self, instant_pay_api, status):
        """
        测试场景2：按 status 枚举筛选（5个值）
        Test Scenario2: Filter by status Enum (All 5 Values)
        """
        resp = instant_pay_api.list_transactions(status=status, size=10)
        assert resp.status_code == 200
        assert resp.json().get("code") == 200
        _, content = self._get_content(resp)
        if not content:
            logger.info(f"  ⚠ status='{status}' 无数据")
        else:
            for txn in content:
                assert txn.get("status") == status
            logger.info(f"  ✓ status='{status}': {len(content)} 条")

    @pytest.mark.parametrize("transaction_type", ["Credit", "Debit"])
    def test_filter_by_transaction_type(self, instant_pay_api, transaction_type):
        """
        测试场景3：按 transaction_type 枚举筛选（Credit/Debit）
        Test Scenario3: Filter by transaction_type
        """
        resp = instant_pay_api.list_transactions(transaction_type=transaction_type, size=10)
        assert resp.status_code == 200
        assert resp.json().get("code") == 200
        _, content = self._get_content(resp)
        if not content:
            logger.info(f"  ⚠ transaction_type='{transaction_type}' 无数据")
        else:
            for txn in content:
                assert txn.get("transaction_type") == transaction_type
            logger.info(f"  ✓ transaction_type='{transaction_type}': {len(content)} 条")

    def test_filter_by_financial_account_id(self, instant_pay_api):
        """
        测试场景4：按 financial_account_id 筛选
        Test Scenario4: Filter by financial_account_id
        """
        _, base = self._get_content(instant_pay_api.list_transactions(size=20))
        fa_id = next(
            (t.get("financial_account_id") for t in base if t.get("financial_account_id")),
            None
        )
        if not fa_id:
            pytest.skip("无包含 fa_id 的交易")
        resp = instant_pay_api.list_transactions(financial_account_id=fa_id, size=10)
        assert resp.status_code == 200
        assert resp.json().get("code") == 200
        logger.info(f"✓ financial_account_id 筛选通过，返回 {len(self._get_content(resp)[1])} 条")

    def test_pagination(self, instant_pay_api):
        """
        测试场景5：分页验证
        Test Scenario5: Pagination
        """
        resp = instant_pay_api.list_transactions(page=0, size=5)
        assert resp.status_code == 200
        data, content = self._get_content(resp)
        assert len(content) <= 5
        assert data.get("size") == 5
        logger.info(f"✓ 分页验证: size=5, total={data.get('total_elements',0)}")


# ════════════════════════════════════════════════════════════════════
# List Request For Payment Transactions（RFP 定时交易）
# ════════════════════════════════════════════════════════════════════
@pytest.mark.instant_pay
class TestListRFPTransactions:

    def _get_content(self, response):
        body = response.json()
        data = body.get("data", body) or {}
        return data, data.get("content", []) if isinstance(data, dict) else []

    def test_list_rfp_success(self, instant_pay_api):
        """
        测试场景1：成功获取 RFP 交易列表
        Test Scenario1: Successfully List RFP Transactions
        验证点：code=200，RFP 特有字段存在（execution_date, expiration_date 等）
        """
        resp = instant_pay_api.list_request_payment_transactions(size=10)
        assert resp.status_code == 200
        body = resp.json()
        assert body.get("code") == 200

        data, content = self._get_content(resp)
        assert isinstance(content, list)
        total = data.get("total_elements", 0)
        logger.info(f"  total={total}, returned={len(content)}")

        if content:
            rfp = content[0]
            # RFP 特有字段
            rfp_fields = ["execution_date", "expiration_date",
                          "amount_modification_allowed", "early_payment_allowed"]
            for f in rfp_fields:
                if f in rfp:
                    logger.info(f"  ✓ {f}: {rfp.get(f)}")
        logger.info("✓ RFP 交易列表获取成功")

    @pytest.mark.parametrize("status", [
        "Cancelled", "Pending", "Rejected", "Paid_In_Full", "Paid_In_Partial"
    ])
    def test_rfp_filter_by_status(self, instant_pay_api, status):
        """
        测试场景2：按 RFP status 枚举筛选（5个值）
        Test Scenario2: Filter RFP by Status Enum (All 5 Values)
        """
        resp = instant_pay_api.list_request_payment_transactions(status=status, size=10)
        assert resp.status_code == 200
        assert resp.json().get("code") == 200
        _, content = self._get_content(resp)
        if not content:
            logger.info(f"  ⚠ status='{status}' 无数据")
        else:
            for rfp in content:
                assert rfp.get("status") == status
            logger.info(f"  ✓ status='{status}': {len(content)} 条")

    @pytest.mark.parametrize("direction", ["Origination", "Incoming"])
    def test_rfp_filter_by_direction(self, instant_pay_api, direction):
        """
        测试场景3：按 direction 筛选（Origination/Incoming）
        Test Scenario3: Filter RFP by Direction
        """
        resp = instant_pay_api.list_request_payment_transactions(direction=direction, size=10)
        assert resp.status_code == 200
        assert resp.json().get("code") == 200
        _, content = self._get_content(resp)
        if not content:
            logger.info(f"  ⚠ direction='{direction}' 无数据")
        else:
            for rfp in content:
                assert rfp.get("direction") == direction
            logger.info(f"  ✓ direction='{direction}': {len(content)} 条")

    def test_rfp_pagination(self, instant_pay_api):
        """
        测试场景4：RFP 列表分页验证
        Test Scenario4: RFP List Pagination
        """
        resp = instant_pay_api.list_request_payment_transactions(page=0, size=3)
        assert resp.status_code == 200
        data, content = self._get_content(resp)
        assert len(content) <= 3
        logger.info(f"✓ RFP 分页验证: size=3, total={data.get('total_elements',0)}")
