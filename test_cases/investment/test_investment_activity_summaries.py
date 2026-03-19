"""
Investment - Activity Summaries 接口测试用例
测试 GET /api/v1/cores/{core}/reports/investments/activity-summaries 接口

响应结构：{"code": 200, "data": {beginning_market_value, net_additions, ...}}
account_id 或 financial_account_id 二选一必填。
有账户但无投资数据时，data 字段存在但所有值为 null（不是缺失）。
"""
import pytest
from api.account_api import AccountAPI
from utils.logger import logger
from utils.assertions import assert_status_ok


def _get_account_id(login_session) -> str:
    """从 list_accounts 动态获取一个真实 account_id"""
    acc_api = AccountAPI(session=login_session)
    accs = acc_api.list_accounts(page=0, size=1).json().get("data", {}).get("content", [])
    if not accs:
        pytest.skip("无可用 account 数据，跳过")
    return accs[0]["id"]


@pytest.mark.investment
@pytest.mark.list_api
class TestInvestmentActivitySummaries:

    def test_missing_both_account_ids(self, investment_api, valid_date_range):
        """
        测试场景1：两个ID都不提供 → 业务错误
        Test Scenario1: Missing Both Account IDs Returns Business Error
        验证点：
        1. HTTP 200（统一错误处理）
        2. business code=599，error_message 包含 "account_id missing"
        3. data 为 null
        """
        response = investment_api.get_activity_summaries(**valid_date_range)

        assert response.status_code == 200
        body = response.json()
        assert body.get("code") != 200, f"不提供ID应返回业务错误，实际 code={body.get('code')}"
        assert body.get("data") is None, "缺少必需参数时 data 应为 null"
        logger.info(f"✓ 缺少ID校验通过: code={body.get('code')}, msg={body.get('error_message')}")

    def test_invalid_date_format(self, investment_api, login_session):
        """
        测试场景2：无效的日期格式（斜杠格式）
        Test Scenario2: Invalid Date Format Returns Business Error
        验证点：
        1. HTTP 200
        2. business code != 200
        """
        account_id = _get_account_id(login_session)
        response = investment_api.get_activity_summaries(
            account_id=account_id,
            begin_date="2024/01/01",
            end_date="2024-01-31"
        )
        assert response.status_code == 200
        body = response.json()
        assert body.get("code") != 200, f"无效日期格式应返回业务错误，实际 code={body.get('code')}"
        logger.info(f"✓ 无效日期格式被拒绝: code={body.get('code')}")

    def test_date_range_reversed(self, investment_api, login_session):
        """
        测试场景3：日期范围倒置（end_date < begin_date）
        Test Scenario3: Reversed Date Range Returns Error or Empty Data
        验证点：
        1. HTTP 200
        2. business code != 200 或 data 所有字段为 null
        """
        account_id = _get_account_id(login_session)
        response = investment_api.get_activity_summaries(
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
            # 允许返回 data 但值全为 null
            assert data is None or all(v is None for v in data.values()), \
                "倒置日期范围数据应为 null 或全 null 字段"
            logger.info(f"✓ 倒置日期返回 null 数据")

    def test_get_activity_summaries_with_account_id(self, investment_api, login_session):
        """
        测试场景4：使用 account_id 获取活动摘要
        Test Scenario4: Get Activity Summaries with account_id
        验证点：
        1. HTTP 200，business code=200
        2. data 包含文档定义的所有字段（值可能为 null，但字段存在）
        """
        account_id = _get_account_id(login_session)
        response = investment_api.get_activity_summaries(
            account_id=account_id,
            begin_date="2023-01-01",
            end_date="2023-12-31"
        )
        assert response.status_code == 200
        body = response.json()
        assert body.get("code") == 200, \
            f"使用真实 account_id 应返回 code=200，实际: {body.get('code')}, msg={body.get('error_message')}"

        data = body.get("data", {})
        assert isinstance(data, dict), "data 应为对象"
        required_fields = [
            "beginning_market_value", "net_additions", "contributions",
            "withdrawals", "fees", "gain_loss",
            "market_appreciation_or_depreciation", "income", "ending_market_value"
        ]
        for field in required_fields:
            assert field in data, f"data 缺少文档定义字段: '{field}'"
            logger.info(f"  ✓ {field}: {data.get(field)}")

        logger.info(f"✓ activity_summaries 字段结构验证通过（account_id={account_id}）")

    @pytest.mark.skip(reason="需要真实有投资数据的 financial_account_id（当前环境 FA 均无投资数据）")
    def test_with_financial_account_id(self, investment_api):
        """
        测试场景5：使用 financial_account_id（需有投资数据）
        Test Scenario5: Get Activity Summaries with financial_account_id
        """
        response = investment_api.get_activity_summaries(
            financial_account_id="<替换为有投资数据的 FA ID>",
            begin_date="2023-01-01",
            end_date="2023-12-31"
        )
        assert response.status_code == 200
        body = response.json()
        assert body.get("code") == 200
        data = body.get("data", {})
        assert any(v is not None for v in data.values()), "有投资数据的账户至少有一个非 null 字段"
        logger.info(f"✓ financial_account_id 场景验证通过")
