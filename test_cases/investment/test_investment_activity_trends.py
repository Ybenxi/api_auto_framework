"""
Investment - Activity Trends 接口测试用例
测试 GET /api/v1/cores/{core}/reports/investments/activity-trends 接口

响应结构：{"code": 200, "data": [{date, market_value, net_addition, bmv_and_net_addition}, ...]}
account_id 或 financial_account_id 二选一必填。
"""
import pytest
from api.account_api import AccountAPI
from utils.logger import logger


def _get_account_id(login_session) -> str:
    acc_api = AccountAPI(session=login_session)
    accs = acc_api.list_accounts(page=0, size=1).json().get("data", {}).get("content", [])
    if not accs:
        pytest.skip("无可用 account 数据，跳过")
    return accs[0]["id"]


@pytest.mark.investment
@pytest.mark.list_api
class TestInvestmentActivityTrends:

    def test_missing_both_account_ids(self, investment_api, valid_date_range):
        """
        测试场景1：两个ID都不提供 → 业务错误
        Test Scenario1: Missing Both Account IDs Returns Business Error
        """
        response = investment_api.get_activity_trends(**valid_date_range)

        assert response.status_code == 200
        body = response.json()
        assert body.get("code") != 200, f"不提供ID应返回业务错误，实际 code={body.get('code')}"
        assert body.get("data") is None
        logger.info(f"✓ 缺少ID校验通过: code={body.get('code')}")

    def test_invalid_date_formats(self, investment_api, login_session):
        """
        测试场景2：多种无效日期格式
        Test Scenario2: Multiple Invalid Date Formats Return Business Error
        """
        account_id = _get_account_id(login_session)
        invalid_cases = [
            ("01/01/2024", "2024-01-31", "MM/DD/YYYY"),
            ("2024-13-01", "2024-12-31", "无效月份13"),
        ]
        for begin_date, end_date, desc in invalid_cases:
            r = investment_api.get_activity_trends(
                account_id=account_id, begin_date=begin_date, end_date=end_date
            )
            body = r.json()
            assert body.get("code") != 200, f"[{desc}] 无效日期应返回错误"
            logger.info(f"  ✓ [{desc}] code={body.get('code')}")
        logger.info("✓ 无效日期格式验证通过")

    def test_future_date_range_returns_empty(self, investment_api, login_session):
        """
        测试场景3：未来日期范围（无交易数据）
        Test Scenario3: Future Date Range Returns Empty Data Array
        验证点：
        1. HTTP 200，business code=200
        2. data 为空数组（无历史数据）
        """
        account_id = _get_account_id(login_session)
        response = investment_api.get_activity_trends(
            account_id=account_id,
            begin_date="2099-01-01",
            end_date="2099-12-31"
        )
        assert response.status_code == 200
        body = response.json()
        code = body.get("code")
        data = body.get("data")
        if code == 200:
            assert data == [] or data is None, f"未来日期应返回空数组，实际: {data}"
            logger.info("✓ 未来日期返回空数组")
        else:
            logger.info(f"✓ 未来日期被拒绝: code={code}")

    def test_get_activity_trends_with_account_id(self, investment_api, login_session):
        """
        测试场景4：使用 account_id 获取趋势数据，验证响应结构
        Test Scenario4: Get Activity Trends with account_id and Verify Structure
        验证点：
        1. HTTP 200，business code=200
        2. data 是数组（可为空，取决于账户投资数据）
        3. 若有数据，每条包含 date/market_value/net_addition/bmv_and_net_addition
        """
        account_id = _get_account_id(login_session)
        response = investment_api.get_activity_trends(
            account_id=account_id,
            begin_date="2023-01-01",
            end_date="2023-01-05"
        )
        assert response.status_code == 200
        body = response.json()
        assert body.get("code") == 200, \
            f"使用真实 account_id 应返回 code=200，实际: {body.get('code')}"

        data = body.get("data", [])
        assert isinstance(data, list), "data 应为数组"
        logger.info(f"  返回 {len(data)} 条趋势记录")

        if data:
            required = ["date", "market_value", "net_addition", "bmv_and_net_addition"]
            for field in required:
                assert field in data[0], f"趋势记录缺少字段: '{field}'"
            logger.info(f"  ✓ 字段结构正确: {list(data[0].keys())}")
            dates = [item["date"] for item in data]
            assert dates == sorted(dates), "日期应按升序排列"
            logger.info("  ✓ 日期按升序排列")
        logger.info("✓ activity_trends 验证通过")

    def test_date_range_reversed(self, investment_api, login_session):
        """
        测试场景5：日期范围倒置
        Test Scenario5: Reversed Date Range Returns Error or Empty
        """
        account_id = _get_account_id(login_session)
        response = investment_api.get_activity_trends(
            account_id=account_id,
            begin_date="2024-01-31",
            end_date="2024-01-01"
        )
        assert response.status_code == 200
        body = response.json()
        code = body.get("code")
        data = body.get("data")
        if code != 200:
            logger.info(f"✓ 倒置日期被拒绝: code={code}")
        else:
            assert data == [] or data is None
            logger.info("✓ 倒置日期返回空数组")
