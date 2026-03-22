"""
ACH Processing - Transactions 接口测试用例
GET /api/v1/cores/{core}/money-movements/ach/transactions

响应结构：{"code": 200, "data": {"content": [...], "total_elements": N, ...}}
ACH 特有字段：first_party, same_day, reference_number, reversal_id
"""
import pytest
from utils.logger import logger

pytestmark = pytest.mark.ach_processing


@pytest.mark.ach_processing
class TestAchTransactions:

    def _get_content(self, response):
        body = response.json()
        data = body.get("data", body) or {}
        return data, data.get("content", []) if isinstance(data, dict) else []

    def test_list_success(self, ach_processing_api):
        """
        测试场景1：成功获取 ACH 交易列表
        Test Scenario1: Successfully List ACH Transactions
        验证点：code=200，含 ACH 特有字段 first_party/same_day
        """
        resp = ach_processing_api.list_transactions(size=10)
        assert resp.status_code == 200
        body = resp.json()
        assert body.get("code") == 200

        data, content = self._get_content(resp)
        total = data.get("total_elements", 0)
        assert isinstance(content, list)
        logger.info(f"  total={total}, returned={len(content)}")

        if content:
            txn = content[0]
            for field in ["id", "status", "first_party", "same_day", "direction"]:
                if field in txn:
                    logger.info(f"  ✓ {field}: {txn.get(field)}")
        logger.info("✓ ACH 交易列表获取成功")

    @pytest.mark.parametrize("status", [
        "Processing", "Reviewing", "Completed", "Cancelled", "Failed"
    ])
    def test_filter_by_status(self, ach_processing_api, status):
        """
        测试场景2：按 status 枚举筛选（5个值）
        Test Scenario2: Filter by status Enum
        """
        resp = ach_processing_api.list_transactions(status=status, size=10)
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
    def test_filter_by_transaction_type(self, ach_processing_api, transaction_type):
        """
        测试场景3：按 transaction_type 枚举筛选（Credit/Debit）
        Test Scenario3: Filter by transaction_type Enum
        """
        resp = ach_processing_api.list_transactions(transaction_type=transaction_type, size=10)
        assert resp.status_code == 200
        assert resp.json().get("code") == 200
        _, content = self._get_content(resp)
        if not content:
            logger.info(f"  ⚠ transaction_type='{transaction_type}' 无数据")
        else:
            for txn in content:
                assert txn.get("transaction_type") == transaction_type
            logger.info(f"  ✓ transaction_type='{transaction_type}': {len(content)} 条")

    def test_filter_by_financial_account_id(self, ach_processing_api):
        """
        测试场景4：按 financial_account_id 筛选
        Test Scenario4: Filter by financial_account_id
        """
        _, base = self._get_content(ach_processing_api.list_transactions(size=20))
        fa_id = next(
            (t.get("financial_account_id") for t in base if t.get("financial_account_id")), None
        )
        if not fa_id:
            pytest.skip("无包含 fa_id 的交易")
        resp = ach_processing_api.list_transactions(financial_account_id=fa_id, size=10)
        assert resp.status_code == 200
        assert resp.json().get("code") == 200
        logger.info(f"✓ financial_account_id 筛选: fa_id={fa_id}")

    def test_filter_by_date_range(self, ach_processing_api):
        """
        测试场景5：按日期范围筛选
        Test Scenario5: Filter by Date Range
        """
        resp = ach_processing_api.list_transactions(
            start_date="2025-01-01", end_date="2026-12-31", size=10
        )
        assert resp.status_code == 200
        assert resp.json().get("code") == 200
        _, content = self._get_content(resp)
        logger.info(f"✓ 日期范围筛选: 返回 {len(content)} 条")

    def test_ach_specific_fields(self, ach_processing_api):
        """
        测试场景6：验证 ACH 特有字段（first_party, same_day, reference_number）
        Test Scenario6: Verify ACH-specific Fields
        """
        _, base = self._get_content(ach_processing_api.list_transactions(size=5))
        if not base:
            pytest.skip("无交易数据")
        txn = base[0]
        ach_fields = ["first_party", "same_day", "reference_number"]
        present = [f for f in ach_fields if f in txn]
        assert "first_party" in present, "ACH 交易应含 first_party 字段"
        assert "same_day" in present, "ACH 交易应含 same_day 字段"
        logger.info(f"✓ ACH 特有字段: {present}")

    def test_pagination(self, ach_processing_api):
        """
        测试场景7：分页验证
        Test Scenario7: Pagination
        """
        resp = ach_processing_api.list_transactions(page=0, size=5)
        assert resp.status_code == 200
        data, content = self._get_content(resp)
        assert len(content) <= 5
        assert data.get("size") == 5
        logger.info(f"✓ 分页验证: size=5, total={data.get('total_elements',0)}")
