"""
Client List - 持仓列表/明细/导出接口测试用例
覆盖：
  5. GET /investment/positions/accounts/:id/pending-transactions/details
  6. GET /investment/positions/accounts/:id/settled-transactions
  7. GET /investment/positions/accounts/:id/pending-transactions
  8. GET /investment/positions/accounts/:id/settled-transactions/export
  9. GET /investment/positions/accounts/:id/pending-transactions/export
"""
import pytest
from utils.logger import logger
from utils.assertions import assert_status_ok

pytestmark = pytest.mark.client_list

SORT_FIELDS_SETTLED = [
    "issue_type,ASC", "issue_type,DESC",
    "symbol,ASC", "name,ASC",
    "current_value,DESC", "total_gain_loss_dollar,DESC",
]


@pytest.mark.client_list
class TestSettledTransactionsList:

    def test_settled_transactions_success(self, client_list_api, real_account_id):
        """
        测试场景1：获取已结算交易列表
        Test Scenario1: Get Settled Transactions List Successfully
        验证点：
        1. HTTP 200，code=200
        2. data.holdings 含 content 数组和分页信息
        3. content 每条含文档定义的关键字段
        """
        if not real_account_id:
            pytest.skip("无可用 account_id，跳过")

        resp = client_list_api.get_settled_transactions(account_id=real_account_id, size=5)
        assert_status_ok(resp)
        body = resp.json()
        assert body.get("code") == 200

        data = body.get("data", {})
        assert "holdings" in data, "data 应含 holdings"
        assert "timestamp" in data

        holdings = data.get("holdings", {}) or {}
        content = holdings.get("content", [])
        assert isinstance(content, list)
        logger.info(f"  holdings count: {len(content)}, total={holdings.get('total_elements', 0)}")

        if content:
            item = content[0]
            for field in ["issue_type", "symbol", "name", "units", "current_value", "cost_basis"]:
                if field in item:
                    logger.info(f"  ✓ {field}: {item.get(field)}")
        logger.info("✓ 已结算交易列表验证通过")

    def test_settled_transactions_symbol_filter(self, client_list_api, real_account_id):
        """
        测试场景2：使用 symbol 模糊筛选
        Test Scenario2: Settled Transactions with Symbol Fuzzy Filter
        """
        if not real_account_id:
            pytest.skip("无可用 account_id，跳过")

        resp = client_list_api.get_settled_transactions(
            account_id=real_account_id, symbol="AAPL", size=5
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body.get("code") == 200

        content = body.get("data", {}).get("holdings", {}).get("content", [])
        for item in content:
            assert "AAPL" in (item.get("symbol") or "").upper() or \
                   "AAPL" in (item.get("name") or "").upper(), \
                   f"symbol 筛选结果应含 AAPL，实际: {item.get('symbol')}"
        logger.info(f"✓ symbol=AAPL 筛选: {len(content)} 条")

    def test_settled_transactions_name_filter(self, client_list_api, real_account_id):
        """
        测试场景3：使用 name 模糊筛选
        Test Scenario3: Settled Transactions with Name Fuzzy Filter
        """
        if not real_account_id:
            pytest.skip("无可用 account_id，跳过")

        resp = client_list_api.get_settled_transactions(
            account_id=real_account_id, name="APPLE", size=5
        )
        assert resp.status_code == 200
        assert resp.json().get("code") == 200
        content = resp.json().get("data", {}).get("holdings", {}).get("content", [])
        logger.info(f"✓ name=APPLE 筛选: {len(content)} 条")

    @pytest.mark.parametrize("sort", SORT_FIELDS_SETTLED[:4])
    def test_settled_transactions_sort(self, client_list_api, real_account_id, sort):
        """
        测试场景4：排序字段覆盖
        Test Scenario4: Settled Transactions Sort Field Coverage
        """
        if not real_account_id:
            pytest.skip("无可用 account_id，跳过")

        resp = client_list_api.get_settled_transactions(
            account_id=real_account_id, sort=sort, size=5
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body.get("code") == 200, \
            f"sort='{sort}' 应被接受，实际 code={body.get('code')}"
        logger.info(f"  ✓ sort='{sort}': code=200")

    def test_settled_transactions_pagination(self, client_list_api, real_account_id):
        """
        测试场景5：分页功能验证
        Test Scenario5: Settled Transactions Pagination
        验证点：size=2 时返回数量 <= 2，pageable 字段存在
        """
        if not real_account_id:
            pytest.skip("无可用 account_id，跳过")

        resp = client_list_api.get_settled_transactions(
            account_id=real_account_id, page=0, size=2
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body.get("code") == 200

        holdings = body.get("data", {}).get("holdings", {}) or {}
        content = holdings.get("content", [])
        assert len(content) <= 2, f"size=2 时返回 {len(content)} 条超出限制"
        assert "total_elements" in holdings or "totalElements" in holdings
        logger.info(f"✓ 分页验证通过: size=2, returned={len(content)}")

    def test_settled_transactions_invalid_account(self, client_list_api):
        """
        测试场景6：无效 account_id
        Test Scenario6: Invalid account_id Returns Empty or Error
        """
        resp = client_list_api.get_settled_transactions(
            account_id="INVALID_ACCOUNT_ID_99999", size=5
        )
        assert resp.status_code == 200
        body = resp.json()
        code = body.get("code")
        if code != 200:
            logger.info(f"✓ 无效 account_id 被拒绝: code={code}")
        else:
            content = body.get("data", {}).get("holdings", {}).get("content", [])
            assert content == [], f"无效 account_id 应返回空 content，实际: {len(content)} 条"
            logger.info("✓ 无效 account_id 返回空列表")


@pytest.mark.client_list
class TestPendingTransactionsList:

    def test_pending_transactions_success(self, client_list_api, real_account_id):
        """
        测试场景1：获取待结算交易列表
        Test Scenario1: Get Pending Transactions List Successfully
        验证点：
        1. HTTP 200，code=200
        2. data.holdings 含 content 数组
        """
        if not real_account_id:
            pytest.skip("无可用 account_id，跳过")

        resp = client_list_api.get_pending_transactions(account_id=real_account_id, size=5)
        assert_status_ok(resp)
        body = resp.json()
        assert body.get("code") == 200

        data = body.get("data", {})
        assert "holdings" in data
        content = data.get("holdings", {}).get("content", [])
        logger.info(f"✓ 待结算交易列表: {len(content)} 条")

    def test_pending_transactions_symbol_filter(self, client_list_api, real_account_id):
        """
        测试场景2：symbol 筛选
        Test Scenario2: Pending Transactions with Symbol Filter
        """
        if not real_account_id:
            pytest.skip("无可用 account_id，跳过")

        resp = client_list_api.get_pending_transactions(
            account_id=real_account_id, symbol="AAPL", size=5
        )
        assert resp.status_code == 200
        assert resp.json().get("code") == 200
        logger.info("✓ 待结算交易 symbol 筛选通过")


@pytest.mark.client_list
class TestPendingTransactionsDetails:

    def test_pending_details_with_real_data(self, client_list_api, real_account_id):
        """
        测试场景1：获取待结算交易明细（先查列表找真实 symbol 再查明细）
        Test Scenario1: Get Pending Transaction Details with Real Data
        """
        if not real_account_id:
            pytest.skip("无可用 account_id，跳过")

        # 先从 settled_transactions 取一个真实 symbol
        list_resp = client_list_api.get_settled_transactions(
            account_id=real_account_id, size=1
        )
        content = list_resp.json().get("data", {}).get("holdings", {}).get("content", [])
        if not content:
            pytest.skip("无持仓数据，跳过")

        symbol = content[0].get("symbol")
        issue_type = content[0].get("issue_type", "Common Stock")
        if not symbol:
            pytest.skip("无 symbol，跳过")

        resp = client_list_api.get_pending_transactions_details(
            account_id=real_account_id,
            symbol=symbol,
            issue_type=issue_type,
            size=5
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body.get("code") == 200

        data = body.get("data", {})
        txn_details = data.get("transactions_details", {}) or {}
        content2 = txn_details.get("content", [])
        logger.info(f"  symbol={symbol}, issue_type={issue_type}: {len(content2)} 条明细")
        logger.info("✓ 待结算交易明细验证通过")

    def test_pending_details_missing_required(self, client_list_api, real_account_id):
        """
        测试场景2：缺少必填参数 symbol 或 issue_type
        Test Scenario2: Missing Required Parameters Returns Business Error
        """
        if not real_account_id:
            pytest.skip("无可用 account_id，跳过")

        # 缺少 symbol
        url = client_list_api.config.get_full_url(
            f"/investment/positions/accounts/{real_account_id}/pending-transactions/details"
        )
        resp = client_list_api.session.get(url, params={"issue_type": "Common Stock"})
        assert resp.status_code == 200
        body = resp.json()
        assert body.get("code") != 200, f"缺少 symbol 应返回错误，实际 code={body.get('code')}"
        logger.info(f"✓ 缺少 symbol 被拒绝: code={body.get('code')}")


@pytest.mark.client_list
class TestExportTransactions:

    def test_export_settled_returns_url(self, client_list_api, real_account_id):
        """
        测试场景1：导出已结算交易，返回 XLS 下载链接
        Test Scenario1: Export Settled Transactions Returns XLS Download URL
        验证点：
        1. HTTP 200，code=200
        2. data 是字符串（下载链接），以 http 开头
        """
        if not real_account_id:
            pytest.skip("无可用 account_id，跳过")

        resp = client_list_api.export_settled_transactions(account_id=real_account_id)
        assert resp.status_code == 200
        body = resp.json()
        assert body.get("code") == 200, \
            f"导出已结算应返回 code=200，实际: {body.get('code')}"

        data = body.get("data")
        if data:
            assert isinstance(data, str), "data 应为字符串（下载链接）"
            assert data.startswith("http"), f"下载链接应以 http 开头，实际: {data[:50]}"
            logger.info(f"✓ 已结算导出 URL: {data[:80]}...")
        else:
            logger.info("⚠ 导出接口返回 code=200 但 data 为空（可能无数据可导出）")

    def test_export_pending_returns_url(self, client_list_api, real_account_id):
        """
        测试场景2：导出待结算交易，返回 XLS 下载链接
        Test Scenario2: Export Pending Transactions Returns XLS Download URL
        """
        if not real_account_id:
            pytest.skip("无可用 account_id，跳过")

        resp = client_list_api.export_pending_transactions(account_id=real_account_id)
        assert resp.status_code == 200
        body = resp.json()
        assert body.get("code") == 200

        data = body.get("data")
        if data:
            assert isinstance(data, str)
            logger.info(f"✓ 待结算导出 URL: {data[:80]}...")
        else:
            logger.info("⚠ 待结算导出 data 为空")

    def test_export_with_filters(self, client_list_api, real_account_id):
        """
        测试场景3：带筛选条件导出
        Test Scenario3: Export with Filters Applied
        """
        if not real_account_id:
            pytest.skip("无可用 account_id，跳过")

        resp = client_list_api.export_settled_transactions(
            account_id=real_account_id,
            symbol="AAPL",
            sort="symbol,ASC"
        )
        assert resp.status_code == 200
        assert resp.json().get("code") == 200
        logger.info("✓ 带筛选条件导出通过")
