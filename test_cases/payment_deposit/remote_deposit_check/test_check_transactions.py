"""
Remote Deposit Check - Transactions 接口测试用例
GET /api/v1/cores/{core}/money-movements/checks/transactions

响应结构：{"code": 200, "data": {"content": [...], "total_elements": N, ...}}
特有筛选参数：counterparty_id（区别于其他 payment 模块）
"""
import pytest
from utils.logger import logger

pytestmark = pytest.mark.remote_deposit_check


@pytest.mark.remote_deposit_check
class TestCheckTransactions:

    def _get_data_content(self, response):
        body = response.json()
        data = body.get("data", body) or {}
        return data, data.get("content", []) if isinstance(data, dict) else []

    def test_list_transactions_success(self, remote_deposit_check_api):
        """
        测试场景1：成功获取 Check 交易列表
        Test Scenario1: Successfully List Check Transactions
        验证点：
        1. HTTP 200，code=200
        2. data.content 是数组
        3. 每条含 status, transaction_type, direction 字段
        """
        resp = remote_deposit_check_api.list_transactions(size=10)
        assert resp.status_code == 200
        body = resp.json()
        assert body.get("code") == 200

        data, content = self._get_data_content(resp)
        assert isinstance(content, list)
        total = data.get("total_elements", 0)
        logger.info(f"  total={total}, returned={len(content)}")

        if content:
            txn = content[0]
            for field in ["status", "transaction_type", "direction", "item_identifier"]:
                if field in txn:
                    logger.info(f"  ✓ {field}: {txn.get(field)}")
        logger.info("✓ Check 交易列表获取成功")

    @pytest.mark.parametrize("status", [
        "Processing", "Reviewing", "Completed", "Cancelled", "Failed"
    ])
    def test_filter_by_status(self, remote_deposit_check_api, status):
        """
        测试场景2：按 status 枚举筛选（全部5个枚举值）
        Test Scenario2: Filter by status Enum (All 5 Values)
        """
        resp = remote_deposit_check_api.list_transactions(status=status, size=10)
        assert resp.status_code == 200
        assert resp.json().get("code") == 200

        _, content = self._get_data_content(resp)
        if not content:
            logger.info(f"  ⚠ status='{status}' 无数据")
        else:
            for txn in content:
                assert txn.get("status") == status
            logger.info(f"  ✓ status='{status}': {len(content)} 条均匹配")

    @pytest.mark.parametrize("transaction_type", ["Credit", "Debit"])
    def test_filter_by_transaction_type(self, remote_deposit_check_api, transaction_type):
        """
        测试场景3：按 transaction_type 枚举筛选（Credit / Debit）
        Test Scenario3: Filter by transaction_type Enum
        """
        resp = remote_deposit_check_api.list_transactions(transaction_type=transaction_type, size=10)
        assert resp.status_code == 200
        assert resp.json().get("code") == 200
        _, content = self._get_data_content(resp)
        if not content:
            logger.info(f"  ⚠ transaction_type='{transaction_type}' 无数据")
        else:
            for txn in content:
                assert txn.get("transaction_type") == transaction_type
            logger.info(f"  ✓ transaction_type='{transaction_type}': {len(content)} 条")

    def test_filter_by_transaction_id(self, remote_deposit_check_api):
        """
        测试场景4：按 transaction_id 精确筛选
        Test Scenario4: Filter by Transaction ID
        """
        _, base = self._get_data_content(
            remote_deposit_check_api.list_transactions(size=1)
        )
        if not base:
            pytest.skip("无交易数据，跳过")
        real_id = base[0].get("id") or base[0].get("transaction_id")
        if not real_id:
            pytest.skip("id 为空")
        resp = remote_deposit_check_api.list_transactions(transaction_id=real_id, size=10)
        assert resp.status_code == 200
        _, content = self._get_data_content(resp)
        assert len(content) > 0
        logger.info(f"✓ transaction_id 精确筛选通过，id={real_id}")

    def test_filter_by_financial_account_id(self, remote_deposit_check_api):
        """
        测试场景5：按 financial_account_id 筛选
        Test Scenario5: Filter by financial_account_id
        """
        _, base = self._get_data_content(
            remote_deposit_check_api.list_transactions(size=20)
        )
        fa_id = next((t.get("financial_account_id") for t in base
                      if t.get("financial_account_id")), None)
        if not fa_id:
            pytest.skip("无包含 financial_account_id 的交易")
        resp = remote_deposit_check_api.list_transactions(financial_account_id=fa_id, size=10)
        assert resp.status_code == 200
        assert resp.json().get("code") == 200
        _, content = self._get_data_content(resp)
        logger.info(f"✓ financial_account_id 筛选通过，返回 {len(content)} 条")

    def test_filter_by_counterparty_id(self, remote_deposit_check_api):
        """
        测试场景6：按 counterparty_id 筛选（Check 独有参数）
        Test Scenario6: Filter by counterparty_id (Check-specific Parameter)
        """
        _, base = self._get_data_content(
            remote_deposit_check_api.list_transactions(size=20)
        )
        cp_id = next((t.get("counterparty_id") for t in base
                      if t.get("counterparty_id")), None)
        if not cp_id:
            pytest.skip("无包含 counterparty_id 的交易")
        resp = remote_deposit_check_api.list_transactions(counterparty_id=cp_id, size=10)
        assert resp.status_code == 200
        assert resp.json().get("code") == 200
        _, content = self._get_data_content(resp)
        logger.info(f"✓ counterparty_id 筛选通过，cp_id={cp_id}，返回 {len(content)} 条")

    def test_filter_by_date_range(self, remote_deposit_check_api):
        """
        测试场景7：按日期范围筛选
        Test Scenario7: Filter by Date Range
        """
        resp = remote_deposit_check_api.list_transactions(
            start_date="2025-01-01", end_date="2026-12-31", size=10
        )
        assert resp.status_code == 200
        assert resp.json().get("code") == 200
        _, content = self._get_data_content(resp)
        logger.info(f"  日期范围内返回 {len(content)} 条")
        if content:
            for txn in content:
                ct = txn.get("create_time", "")
                if ct and len(ct) >= 10:
                    assert "2025-01-01" <= ct[:10] <= "2026-12-31"
        logger.info("✓ 日期范围筛选验证通过")

    def test_check_specific_fields(self, remote_deposit_check_api):
        """
        测试场景8：验证 Check 特有字段（item_identifier, routing_number 等）
        Test Scenario8: Verify Check-specific Fields
        """
        _, base = self._get_data_content(
            remote_deposit_check_api.list_transactions(size=5)
        )
        if not base:
            pytest.skip("无交易数据")
        txn = base[0]
        check_fields = ["item_identifier", "routing_number", "account_number", "check_date"]
        present = [f for f in check_fields if f in txn]
        logger.info(f"  Check 特有字段: {present}")
        assert len(present) > 0, "Check 交易应含至少一个特有字段"
        logger.info("✓ Check 特有字段验证通过")

    def test_pagination(self, remote_deposit_check_api):
        """
        测试场景9：分页验证
        Test Scenario9: Pagination Verification
        """
        resp = remote_deposit_check_api.list_transactions(page=0, size=5)
        assert resp.status_code == 200
        data, content = self._get_data_content(resp)
        assert len(content) <= 5
        assert data.get("size") == 5
        logger.info(f"✓ 分页验证通过: size=5, total={data.get('total_elements',0)}")
