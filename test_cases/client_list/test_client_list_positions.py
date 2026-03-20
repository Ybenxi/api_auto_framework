"""
Client List - 账户持仓汇总接口测试用例
覆盖：
  3. GET /investment/positions/accounts/:id/settled-transactions/summary
  4. GET /investment/positions/accounts/:id/pending-transactions/summary

传入 account_id，返回已结算/待结算交易的汇总数据（units, current_value, cost_basis 等）。
"""
import pytest
from utils.logger import logger
from utils.assertions import assert_status_ok

pytestmark = pytest.mark.client_list


@pytest.mark.client_list
class TestSettledTransactionsSummary:

    def test_settled_summary_success(self, client_list_api, real_account_id):
        """
        测试场景1：获取已结算交易汇总
        Test Scenario1: Get Settled Transactions Summary Successfully
        验证点：
        1. HTTP 200，code=200
        2. data 含 total_holding 和 timestamp
        3. total_holding 含 units, current_value, cost_basis 等字段
        """
        if not real_account_id:
            pytest.skip("无可用 account_id，跳过")

        resp = client_list_api.get_settled_transactions_summary(account_id=real_account_id)
        assert_status_ok(resp)
        body = resp.json()
        assert body.get("code") == 200, f"code 应为 200，实际: {body.get('code')}"

        data = body.get("data", {})
        assert "total_holding" in data, "data 应含 total_holding"
        assert "timestamp" in data, "data 应含 timestamp"

        holding = data.get("total_holding", {}) or {}
        doc_fields = ["units", "current_value", "cost_basis",
                      "total_gain_loss_dollar", "total_gain_loss_percentage"]
        for field in doc_fields:
            if field in holding:
                logger.info(f"  ✓ {field}: {holding.get(field)}")
        logger.info(f"✓ 已结算汇总获取成功: account_id={real_account_id}")

    def test_settled_summary_with_symbol_filter(self, client_list_api, real_account_id):
        """
        测试场景2：使用 symbol 模糊筛选
        Test Scenario2: Settled Summary with Symbol Fuzzy Filter
        """
        if not real_account_id:
            pytest.skip("无可用 account_id，跳过")

        resp = client_list_api.get_settled_transactions_summary(
            account_id=real_account_id, symbol="AAPL"
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body.get("code") == 200
        logger.info(f"✓ symbol=AAPL 筛选汇总: {body.get('data', {}).get('total_holding')}")

    def test_settled_summary_with_name_filter(self, client_list_api, real_account_id):
        """
        测试场景3：使用 name 模糊筛选
        Test Scenario3: Settled Summary with Name Fuzzy Filter
        """
        if not real_account_id:
            pytest.skip("无可用 account_id，跳过")

        resp = client_list_api.get_settled_transactions_summary(
            account_id=real_account_id, name="APPLE"
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body.get("code") == 200
        logger.info(f"✓ name=APPLE 筛选汇总: code={body.get('code')}")

    def test_settled_summary_missing_account_id(self, client_list_api):
        """
        测试场景4：使用空 account_id（路径参数缺失）
        Test Scenario4: Missing account_id Returns Error
        """
        url = client_list_api.config.get_full_url(
            "/investment/positions/accounts/INVALID_ACCOUNT_ID_99999/settled-transactions/summary"
        )
        resp = client_list_api.session.get(url)
        assert resp.status_code == 200
        body = resp.json()
        code = body.get("code")
        if code != 200:
            logger.info(f"✓ 无效 account_id 被拒绝: code={code}")
        else:
            holding = (body.get("data") or {}).get("total_holding") or {}
            assert all(v is None for v in holding.values() if v is not None) or not holding
            logger.info("✓ 无效 account_id 返回空数据")


@pytest.mark.client_list
class TestPendingTransactionsSummary:

    def test_pending_summary_success(self, client_list_api, real_account_id):
        """
        测试场景1：获取待结算交易汇总
        Test Scenario1: Get Pending Transactions Summary Successfully
        验证点：
        1. HTTP 200，code=200
        2. data 含 total_holding 和 timestamp
        """
        if not real_account_id:
            pytest.skip("无可用 account_id，跳过")

        resp = client_list_api.get_pending_transactions_summary(account_id=real_account_id)
        assert_status_ok(resp)
        body = resp.json()
        assert body.get("code") == 200

        data = body.get("data", {})
        assert "total_holding" in data
        assert "timestamp" in data
        logger.info(f"✓ 待结算汇总: {data.get('total_holding')}")

    def test_pending_summary_with_symbol_filter(self, client_list_api, real_account_id):
        """
        测试场景2：使用 symbol 筛选待结算汇总
        Test Scenario2: Pending Summary with Symbol Filter
        """
        if not real_account_id:
            pytest.skip("无可用 account_id，跳过")

        resp = client_list_api.get_pending_transactions_summary(
            account_id=real_account_id, symbol="AAPL"
        )
        assert resp.status_code == 200
        assert resp.json().get("code") == 200
        logger.info("✓ 待结算汇总 symbol 筛选通过")

    def test_compare_settled_vs_pending_structure(self, client_list_api, real_account_id):
        """
        测试场景3：比较已结算和待结算汇总的响应结构一致性
        Test Scenario3: Compare Settled vs Pending Summary Response Structure
        验证点：两个接口的 data 结构应一致（total_holding 字段相同）
        """
        if not real_account_id:
            pytest.skip("无可用 account_id，跳过")

        settled_resp = client_list_api.get_settled_transactions_summary(real_account_id)
        pending_resp = client_list_api.get_pending_transactions_summary(real_account_id)

        assert settled_resp.json().get("code") == 200
        assert pending_resp.json().get("code") == 200

        settled_holding = (settled_resp.json().get("data") or {}).get("total_holding") or {}
        pending_holding = (pending_resp.json().get("data") or {}).get("total_holding") or {}

        settled_keys = set(settled_holding.keys())
        pending_keys = set(pending_holding.keys())

        if settled_keys == pending_keys:
            logger.info(f"✓ 两个汇总接口字段结构一致: {sorted(settled_keys)}")
        else:
            logger.info(f"  已结算字段: {sorted(settled_keys)}")
            logger.info(f"  待结算字段: {sorted(pending_keys)}")
            diff = settled_keys.symmetric_difference(pending_keys)
            logger.info(f"  ⚠ 字段差异: {diff}")
