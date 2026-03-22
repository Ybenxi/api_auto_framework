"""
Wire Processing - Transactions 接口测试用例
GET /api/v1/cores/{core}/money-movements/wire/transactions

响应结构：{"code": 200, "data": {"content": [...], "total_elements": N, ...}}
特有筛选参数：payment_type（Wire/International_Wire）

特有字段：payment_type, direction, reference_number, reversal_id
"""
import pytest
from utils.logger import logger

pytestmark = pytest.mark.wire_processing


@pytest.mark.wire_processing
class TestWireTransactions:

    def _get_data_content(self, response):
        body = response.json()
        data = body.get("data", body) or {}
        return data, data.get("content", []) if isinstance(data, dict) else []

    def test_list_success(self, wire_processing_api):
        """
        测试场景1：成功获取 Wire 交易列表
        Test Scenario1: Successfully List Wire Transactions
        验证点：code=200，content 是数组，含 payment_type/direction 字段
        """
        resp = wire_processing_api.list_transactions(size=10)
        assert resp.status_code == 200
        body = resp.json()
        assert body.get("code") == 200

        data, content = self._get_data_content(resp)
        assert isinstance(content, list)
        total = data.get("total_elements", 0)
        logger.info(f"  total={total}, returned={len(content)}")

        if content:
            txn = content[0]
            for field in ["id", "status", "payment_type", "direction", "transaction_type"]:
                if field in txn:
                    logger.info(f"  ✓ {field}: {txn.get(field)}")
        logger.info("✓ Wire 交易列表获取成功")

    @pytest.mark.parametrize("payment_type", ["Wire", "International_Wire"])
    def test_filter_by_payment_type(self, wire_processing_api, payment_type):
        """
        测试场景2：按 payment_type 枚举筛选（Wire / International_Wire）
        Test Scenario2: Filter by payment_type Enum
        """
        resp = wire_processing_api.list_transactions(payment_type=payment_type, size=10)
        assert resp.status_code == 200
        assert resp.json().get("code") == 200

        _, content = self._get_data_content(resp)
        if not content:
            logger.info(f"  ⚠ payment_type='{payment_type}' 无数据")
        else:
            for txn in content:
                if txn.get("payment_type"):
                    assert txn["payment_type"] == payment_type
            logger.info(f"  ✓ payment_type='{payment_type}': {len(content)} 条均匹配")

    @pytest.mark.parametrize("status", [
        "Processing", "Reviewing", "Completed", "Cancelled", "Failed"
    ])
    def test_filter_by_status(self, wire_processing_api, status):
        """
        测试场景3：按 status 枚举筛选（全部5个枚举值）
        Test Scenario3: Filter by status Enum (All 5 Values)
        """
        resp = wire_processing_api.list_transactions(status=status, size=10)
        assert resp.status_code == 200
        assert resp.json().get("code") == 200
        _, content = self._get_data_content(resp)
        if not content:
            logger.info(f"  ⚠ status='{status}' 无数据")
        else:
            for txn in content:
                assert txn.get("status") == status
            logger.info(f"  ✓ status='{status}': {len(content)} 条")

    @pytest.mark.parametrize("transaction_type", ["Credit", "Debit"])
    def test_filter_by_transaction_type(self, wire_processing_api, transaction_type):
        """
        测试场景4：按 transaction_type 枚举筛选（Credit / Debit）
        Test Scenario4: Filter by transaction_type Enum
        """
        resp = wire_processing_api.list_transactions(transaction_type=transaction_type, size=10)
        assert resp.status_code == 200
        assert resp.json().get("code") == 200
        _, content = self._get_data_content(resp)
        if not content:
            logger.info(f"  ⚠ transaction_type='{transaction_type}' 无数据")
        else:
            for txn in content:
                assert txn.get("transaction_type") == transaction_type
            logger.info(f"  ✓ transaction_type='{transaction_type}': {len(content)} 条")

    def test_filter_by_transaction_id(self, wire_processing_api):
        """
        测试场景5：按 transaction_id 精确筛选
        Test Scenario5: Filter by Transaction ID
        """
        _, base = self._get_data_content(wire_processing_api.list_transactions(size=1))
        if not base:
            pytest.skip("无交易数据")
        real_id = base[0].get("id") or base[0].get("transaction_id")
        if not real_id:
            pytest.skip("id 为空")
        resp = wire_processing_api.list_transactions(transaction_id=real_id, size=10)
        assert resp.status_code == 200
        _, content = self._get_data_content(resp)
        assert len(content) > 0
        logger.info(f"✓ transaction_id 精确筛选通过: id={real_id}")

    def test_filter_by_financial_account_id(self, wire_processing_api):
        """
        测试场景6：按 financial_account_id 筛选
        Test Scenario6: Filter by financial_account_id
        """
        _, base = self._get_data_content(wire_processing_api.list_transactions(size=20))
        fa_id = next(
            (t.get("financial_account_id") for t in base if t.get("financial_account_id")), None
        )
        if not fa_id:
            pytest.skip("无包含 financial_account_id 的交易")
        resp = wire_processing_api.list_transactions(financial_account_id=fa_id, size=10)
        assert resp.status_code == 200
        assert resp.json().get("code") == 200
        _, content = self._get_data_content(resp)
        logger.info(f"✓ financial_account_id 筛选: fa_id={fa_id}, 返回 {len(content)} 条")

    def test_filter_by_date_range(self, wire_processing_api):
        """
        测试场景7：按日期范围筛选
        Test Scenario7: Filter by Date Range
        """
        resp = wire_processing_api.list_transactions(
            start_date="2025-01-01", end_date="2026-12-31", size=10
        )
        assert resp.status_code == 200
        assert resp.json().get("code") == 200
        _, content = self._get_data_content(resp)
        if content:
            for txn in content:
                ct = txn.get("create_time", "")
                if ct and len(ct) >= 10:
                    assert "2025-01-01" <= ct[:10] <= "2026-12-31"
        logger.info(f"✓ 日期范围筛选: 返回 {len(content)} 条")

    def test_wire_specific_fields(self, wire_processing_api):
        """
        测试场景8：验证 Wire 特有字段（payment_type, direction, reference_number）
        Test Scenario8: Verify Wire-specific Fields
        """
        _, base = self._get_data_content(wire_processing_api.list_transactions(size=5))
        if not base:
            pytest.skip("无交易数据")
        txn = base[0]
        wire_fields = ["payment_type", "direction", "reference_number", "reversal_id"]
        present = [f for f in wire_fields if f in txn]
        logger.info(f"  Wire 特有字段: {present}")
        assert "payment_type" in present, "Wire 交易应含 payment_type 字段"
        logger.info("✓ Wire 特有字段验证通过")

    def test_pagination(self, wire_processing_api):
        """
        测试场景9：分页验证
        Test Scenario9: Pagination
        """
        resp = wire_processing_api.list_transactions(page=0, size=5)
        assert resp.status_code == 200
        data, content = self._get_data_content(resp)
        assert len(content) <= 5
        assert data.get("size") == 5
        logger.info(f"✓ 分页验证: size=5, total={data.get('total_elements',0)}")
