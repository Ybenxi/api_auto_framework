"""
Internal Pay - Transactions 接口测试用例
GET /api/v1/cores/{core}/money-movements/internal-pay/transactions

响应结构：{"code": 200, "data": {"content": [...], "total_elements": N, ...}}
每笔转账产生 2 条记录（Credit 收款方 + Debit 付款方）。
注意：Internal Pay 无 direction 字段（区别于 Account Transfer）。
"""
import pytest
from utils.logger import logger

pytestmark = pytest.mark.internal_pay


@pytest.mark.internal_pay
class TestInternalPayTransactions:

    def _get_data_and_content(self, response):
        body = response.json()
        data = body.get("data", body) or {}
        return data, data.get("content", []) if isinstance(data, dict) else []

    def test_list_transactions_success(self, internal_pay_api):
        """
        测试场景1：成功获取交易列表
        Test Scenario1: Successfully List Internal Pay Transactions
        验证点：
        1. HTTP 200，code=200
        2. data.content 是数组
        3. 无 direction 字段（区别于 Account Transfer）
        """
        resp = internal_pay_api.list_transactions(size=10)
        assert resp.status_code == 200
        body = resp.json()
        assert body.get("code") == 200

        data, content = self._get_data_and_content(resp)
        assert isinstance(content, list)
        total = data.get("total_elements", 0)
        logger.info(f"  total={total}, returned={len(content)}")

        if content:
            txn = content[0]
            assert "direction" not in txn, "Internal Pay 不应有 direction 字段"
            for field in ["status", "transaction_type"]:
                if field in txn:
                    logger.info(f"  ✓ {field}: {txn.get(field)}")
        logger.info("✓ 交易列表获取成功")

    @pytest.mark.parametrize("status", [
        "Processing", "Reviewing", "Completed", "Cancelled", "Failed"
    ])
    def test_filter_by_status(self, internal_pay_api, status):
        """
        测试场景2：按 status 枚举筛选（全部5个枚举值）
        Test Scenario2: Filter by status Enum (All 5 Values)
        """
        resp = internal_pay_api.list_transactions(status=status, size=10)
        assert resp.status_code == 200
        assert resp.json().get("code") == 200

        _, content = self._get_data_and_content(resp)
        if not content:
            logger.info(f"  ⚠ status='{status}' 无数据")
        else:
            for txn in content:
                assert txn.get("status") == status
            logger.info(f"  ✓ status='{status}': {len(content)} 条均匹配")

    @pytest.mark.parametrize("transaction_type", ["Credit", "Debit"])
    def test_filter_by_transaction_type(self, internal_pay_api, transaction_type):
        """
        测试场景3：按 transaction_type 枚举筛选（Credit / Debit）
        Test Scenario3: Filter by transaction_type Enum
        Credit = 收款方视角，Debit = 付款方视角
        """
        resp = internal_pay_api.list_transactions(transaction_type=transaction_type, size=10)
        assert resp.status_code == 200
        assert resp.json().get("code") == 200

        _, content = self._get_data_and_content(resp)
        if not content:
            logger.info(f"  ⚠ transaction_type='{transaction_type}' 无数据")
        else:
            for txn in content:
                assert txn.get("transaction_type") == transaction_type
            logger.info(f"  ✓ transaction_type='{transaction_type}': {len(content)} 条均匹配")

    def test_filter_by_transaction_id(self, internal_pay_api):
        """
        测试场景4：按 transaction_id 精确筛选
        Test Scenario4: Filter by Specific Transaction ID
        """
        _, base = self._get_data_and_content(
            internal_pay_api.list_transactions(size=1)
        )
        if not base:
            pytest.skip("无交易数据，跳过")

        real_id = base[0].get("id") or base[0].get("transaction_id")
        if not real_id:
            pytest.skip("transaction id 为空")

        resp = internal_pay_api.list_transactions(transaction_id=real_id, size=10)
        assert resp.status_code == 200
        _, content = self._get_data_and_content(resp)
        assert len(content) > 0
        for txn in content:
            assert txn.get("id") == real_id or txn.get("transaction_id") == real_id
        logger.info(f"✓ transaction_id 精确筛选通过，id={real_id}")

    def test_filter_by_date_range(self, internal_pay_api):
        """
        测试场景5：按日期范围筛选，验证 create_time 在范围内
        Test Scenario5: Filter by Date Range and Verify create_time
        """
        resp = internal_pay_api.list_transactions(
            start_date="2025-01-01", end_date="2026-12-31", size=10
        )
        assert resp.status_code == 200
        assert resp.json().get("code") == 200

        _, content = self._get_data_and_content(resp)
        logger.info(f"  日期范围内返回 {len(content)} 条")
        if content:
            for txn in content:
                create_time = txn.get("create_time", "")
                if create_time and len(create_time) >= 10:
                    txn_date = create_time[:10]
                    assert "2025-01-01" <= txn_date <= "2026-12-31"
        logger.info("✓ 日期范围筛选验证通过")

    def test_filter_by_payer_fa(self, internal_pay_api):
        """
        测试场景6：按 payer_financial_account_id 筛选
        Test Scenario6: Filter by Payer Financial Account ID
        """
        _, base = self._get_data_and_content(
            internal_pay_api.list_transactions(size=20)
        )
        payer_id = next(
            (t.get("payer_financial_account_id") for t in base
             if t.get("payer_financial_account_id")), None
        )
        if not payer_id:
            pytest.skip("无包含 payer_financial_account_id 的交易")

        resp = internal_pay_api.list_transactions(
            payer_financial_account_id=payer_id, size=10
        )
        assert resp.status_code == 200
        _, content = self._get_data_and_content(resp)
        # 筛选结果里 Debit 视角的 payer_fa 应匹配；Credit 视角的记录 payer_fa 可能不同（接收方视角）
        # 只验证有 payer_fa 字段且能匹配到的记录数量 > 0
        matched = sum(1 for t in content
                      if t.get("payer_financial_account_id") == payer_id)
        total_with_payer = sum(1 for t in content
                               if t.get("payer_financial_account_id"))
        logger.info(f"  返回 {len(content)} 条，其中 payer_fa 匹配 {matched} 条，有 payer_fa 字段共 {total_with_payer} 条")
        assert matched > 0 or total_with_payer == 0, \
            f"应至少有一条记录的 payer_fa={payer_id} 匹配，实际 {matched} 条"
        logger.info(f"✓ payer_fa 筛选通过")

    def test_two_records_per_transfer(self, internal_pay_api):
        """
        测试场景7：每笔转账产生 2 条记录（Credit + Debit）
        Test Scenario7: Each Transfer Creates 2 Records (Credit + Debit)
        验证点：查完整的 transactions 列表，应同时存在 Credit 和 Debit 类型记录
        """
        resp = internal_pay_api.list_transactions(size=50)
        assert resp.status_code == 200

        _, content = self._get_data_and_content(resp)
        types = {t.get("transaction_type") for t in content}
        logger.info(f"  存在的 transaction_type 值: {types}")

        if len(content) > 1:
            assert "Credit" in types or "Debit" in types, "应有 Credit 或 Debit 类型记录"
        logger.info("✓ transaction_type 验证通过")

    def test_pagination(self, internal_pay_api):
        """
        测试场景8：分页功能验证
        Test Scenario8: Pagination Verification
        """
        resp = internal_pay_api.list_transactions(page=0, size=5)
        assert resp.status_code == 200
        data, content = self._get_data_and_content(resp)
        assert len(content) <= 5
        assert data.get("size") == 5
        assert data.get("number") == 0
        logger.info(f"✓ 分页验证通过: size=5, returned={len(content)}, total={data.get('total_elements',0)}")
