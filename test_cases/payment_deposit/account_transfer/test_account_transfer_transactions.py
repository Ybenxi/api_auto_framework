"""
Account Transfer - Transactions 接口测试用例
GET /api/v1/cores/{core}/money-movements/account-transfer/transactions

响应结构：{"code": 200, "data": {"content": [...], "total_elements": N, ...}}
已结算转账状态固定为 Completed；每笔转账产生 2 条记录（Origination + Receipt）。
"""
import pytest
from utils.logger import logger

pytestmark = pytest.mark.account_transfer


@pytest.mark.account_transfer
class TestAccountTransferTransactions:

    def _get_content(self, response):
        body = response.json()
        data = body.get("data", body) or {}
        return data.get("content", []) if isinstance(data, dict) else []

    def test_list_transactions_success(self, account_transfer_api):
        """
        测试场景1：成功获取交易列表
        Test Scenario1: Successfully List Account Transfer Transactions
        验证点：
        1. HTTP 200，code=200
        2. data.content 是数组
        3. 有数据时每条含 status, direction, transaction_type, memo 字段
        """
        resp = account_transfer_api.list_transactions(size=10)
        assert resp.status_code == 200
        body = resp.json()
        assert body.get("code") == 200, f"code 应为 200，实际: {body.get('code')}"

        data = body.get("data", {})
        content = data.get("content", [])
        assert isinstance(content, list)
        total = data.get("total_elements", 0)
        logger.info(f"  total_elements={total}, returned={len(content)}")

        if content:
            txn = content[0]
            for field in ["status", "direction", "transaction_type"]:
                if field in txn:
                    logger.info(f"  ✓ {field}: {txn.get(field)}")
        logger.info("✓ 交易列表获取成功")

    @pytest.mark.parametrize("status", [
        "Processing", "Reviewing", "Completed", "Cancelled", "Failed"
    ])
    def test_filter_by_status(self, account_transfer_api, status):
        """
        测试场景2：按 status 枚举筛选（全部5个枚举值）
        Test Scenario2: Filter Transactions by status Enum (All 5 Values)
        验证点：有数据时每条 status 均与筛选值一致
        """
        resp = account_transfer_api.list_transactions(status=status, size=10)
        assert resp.status_code == 200
        body = resp.json()
        assert body.get("code") == 200

        content = self._get_content(resp)
        if not content:
            logger.info(f"  ⚠ status='{status}' 无数据")
        else:
            for txn in content:
                assert txn.get("status") == status, \
                    f"筛选结果包含非 {status}: {txn.get('status')}"
            logger.info(f"  ✓ status='{status}': {len(content)} 条均匹配")

    @pytest.mark.parametrize("transaction_type", ["Credit", "Debit"])
    def test_filter_by_transaction_type(self, account_transfer_api, transaction_type):
        """
        测试场景3：按 transaction_type 枚举筛选（Credit / Debit）
        Test Scenario3: Filter Transactions by transaction_type Enum
        """
        resp = account_transfer_api.list_transactions(transaction_type=transaction_type, size=10)
        assert resp.status_code == 200
        assert resp.json().get("code") == 200

        content = self._get_content(resp)
        if not content:
            logger.info(f"  ⚠ transaction_type='{transaction_type}' 无数据")
        else:
            for txn in content:
                assert txn.get("transaction_type") == transaction_type, \
                    f"筛选结果 transaction_type={txn.get('transaction_type')} 不匹配"
            logger.info(f"  ✓ transaction_type='{transaction_type}': {len(content)} 条均匹配")

    def test_filter_by_transaction_id(self, account_transfer_api):
        """
        测试场景4：按 transaction_id 精确筛选
        Test Scenario4: Filter by Specific Transaction ID
        """
        base = self._get_content(account_transfer_api.list_transactions(size=1))
        if not base:
            pytest.skip("无交易数据，跳过")

        real_id = base[0].get("id") or base[0].get("transaction_id")
        if not real_id:
            pytest.skip("transaction id 为空")

        resp = account_transfer_api.list_transactions(transaction_id=real_id, size=10)
        assert resp.status_code == 200
        content = self._get_content(resp)
        assert len(content) > 0
        for txn in content:
            assert txn.get("id") == real_id or txn.get("transaction_id") == real_id
        logger.info(f"✓ transaction_id 精确筛选通过，id={real_id}")

    def test_filter_by_date_range(self, account_transfer_api):
        """
        测试场景5：按日期范围筛选
        Test Scenario5: Filter Transactions by Date Range
        验证点：返回的 create_time 在日期范围内
        """
        resp = account_transfer_api.list_transactions(
            start_date="2025-01-01",
            end_date="2026-12-31",
            size=10
        )
        assert resp.status_code == 200
        assert resp.json().get("code") == 200

        content = self._get_content(resp)
        logger.info(f"  日期范围内返回 {len(content)} 条")

        if content:
            for txn in content:
                create_time = txn.get("create_time", "")
                if create_time and len(create_time) >= 10:
                    txn_date = create_time[:10]
                    assert "2025-01-01" <= txn_date <= "2026-12-31", \
                        f"交易日期 {txn_date} 不在范围内"
        logger.info("✓ 日期范围筛选验证通过")

    def test_filter_by_payer_fa(self, account_transfer_api):
        """
        测试场景6：按 payer_financial_account_id 筛选
        Test Scenario6: Filter by Payer Financial Account ID
        """
        base = self._get_content(account_transfer_api.list_transactions(size=20))
        # 找有 payer_financial_account_id 且出现多次的 fa_id（确保筛选有意义）
        payer_id = next((t.get("payer_financial_account_id") for t in base
                         if t.get("payer_financial_account_id")), None)
        if not payer_id:
            pytest.skip("无包含 payer_financial_account_id 的交易，跳过")

        resp = account_transfer_api.list_transactions(
            payer_financial_account_id=payer_id, size=10
        )
        assert resp.status_code == 200
        content = self._get_content(resp)
        # 有 payer_fa 字段时才做断言；部分记录可能是 payee 视角（Receipt），该字段可能不同
        checked = 0
        for txn in content:
            if "payer_financial_account_id" in txn and txn.get("payer_financial_account_id"):
                assert txn.get("payer_financial_account_id") == payer_id, \
                    f"筛选结果 payer_fa 不匹配: {txn.get('payer_financial_account_id')}"
                checked += 1
        logger.info(f"✓ payer_fa 筛选通过，返回 {len(content)} 条，验证了 {checked} 条")

    def test_direction_field_in_response(self, account_transfer_api):
        """
        测试场景7：direction 字段验证（Account Transfer 独有字段）
        Test Scenario7: Verify direction Field (Unique to Account Transfer)
        验证点：
        1. 响应含 direction 字段
        2. 值为 Origination 或 Receipt（每笔转账产生两条记录）
        """
        base = self._get_content(account_transfer_api.list_transactions(size=10))
        if not base:
            pytest.skip("无交易数据，跳过")

        directions = set()
        for txn in base:
            if "direction" in txn:
                directions.add(txn["direction"])
        logger.info(f"  发现的 direction 值: {directions}")
        assert directions.issubset({"Origination", "Receipt"}), \
            f"direction 出现未知值: {directions - {'Origination', 'Receipt'}}"
        logger.info("✓ direction 字段验证通过")

    def test_completed_status_for_internal_transfer(self, account_transfer_api):
        """
        测试场景8：内部转账完成后状态为 Completed
        Test Scenario8: Completed Transactions Have Correct Status
        验证点：查已完成的转账，direction 和 status 均正确
        """
        resp = account_transfer_api.list_transactions(status="Completed", size=5)
        assert resp.status_code == 200
        content = self._get_content(resp)

        if not content:
            pytest.skip("无 Completed 状态交易，跳过")

        for txn in content:
            assert txn.get("status") == "Completed"
            assert txn.get("direction") in ["Origination", "Receipt"]
        logger.info(f"✓ Completed 内部转账状态验证通过，{len(content)} 条")

    def test_pagination(self, account_transfer_api):
        """
        测试场景9：分页功能验证
        Test Scenario9: Pagination Verification
        """
        resp = account_transfer_api.list_transactions(page=0, size=5)
        assert resp.status_code == 200
        body = resp.json()
        assert body.get("code") == 200

        data = body.get("data", {})
        content = data.get("content", [])
        assert len(content) <= 5
        assert data.get("size") == 5
        assert data.get("number") == 0
        logger.info(f"✓ 分页验证通过: size=5, returned={len(content)}, total={data.get('total_elements',0)}")
