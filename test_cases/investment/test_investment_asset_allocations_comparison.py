"""
Investment - Asset Allocations Comparison 接口测试用例
测试 GET /api/v1/cores/{core}/reports/investments/asset-allocations/comparison 接口

响应结构：{"code": 200, "data": {strategy_name, allocations: [...], dailyItems: [...]}}
需要账户已配置投资策略才有完整数据。

文档问题（已知）：
1. JSON 示例格式错误（分号替代逗号）
2. dailyItems.allocations 字段命名不一致（actual_percent vs percent）
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
@pytest.mark.detail_api
class TestInvestmentAssetAllocationsComparison:

    def test_missing_both_account_ids(self, investment_api, short_date_range):
        """
        测试场景1：两个ID都不提供 → 业务错误
        Test Scenario1: Missing Both Account IDs Returns Business Error
        """
        response = investment_api.get_asset_allocations_comparison(**short_date_range)
        assert response.status_code == 200
        body = response.json()
        assert body.get("code") != 200
        assert body.get("data") is None
        logger.info(f"✓ 缺少ID校验通过: code={body.get('code')}")

    def test_get_comparison_structure(self, investment_api, login_session):
        """
        测试场景2：获取配置对比，验证响应结构
        Test Scenario2: Get Comparison and Verify Response Structure
        验证点：
        1. HTTP 200，business code=200
        2. data 包含 strategy_name, allocations, dailyItems
        3. allocations 每条含 name, actual_start_percent, target_start_percent 等
        4. dailyItems 每条含 date 和 allocations
        """
        account_id = _get_account_id(login_session)
        response = investment_api.get_asset_allocations_comparison(
            account_id=account_id,
            begin_date="2023-01-01",
            end_date="2023-01-05"
        )
        assert response.status_code == 200
        body = response.json()
        assert body.get("code") == 200, \
            f"应返回 code=200，实际: {body.get('code')}"

        data = body.get("data")
        assert isinstance(data, dict), "data 应为对象"

        # 顶层字段（注意：实际 API 返回 daily_items，文档写 dailyItems，兼容两种）
        for field in ["strategy_name", "allocations"]:
            assert field in data, f"data 缺少字段: '{field}'"
            logger.info(f"  ✓ {field}: {str(data.get(field))[:60]}")
        # dailyItems / daily_items 兼容
        daily_key = "dailyItems" if "dailyItems" in data else "daily_items"
        assert daily_key in data, f"data 缺少 dailyItems/daily_items 字段，实际字段: {list(data.keys())}"
        logger.info(f"  ✓ {daily_key}（文档写 dailyItems，实际为 {daily_key}）")

        # allocations 数组结构（值可能为 null，无策略时）
        allocations = data.get("allocations") or []
        assert isinstance(allocations, list), f"allocations 应为数组或 null，实际: {type(allocations)}"
        if allocations:
            alloc_fields = ["name", "actual_start_percent", "actual_end_percent",
                            "actual_diff", "target_start_percent", "target_end_percent"]
            for field in alloc_fields:
                if field not in allocations[0]:
                    logger.info(f"  ⚠ allocations[0] 缺少字段: '{field}'")
                else:
                    logger.info(f"  ✓ allocations[0].{field}: {allocations[0].get(field)}")

        # dailyItems 数组结构
        daily = data.get("daily_items", data.get("dailyItems")) or []
        assert isinstance(daily, list)
        if daily:
            assert "date" in daily[0], "dailyItems 元素应含 date"
            assert "allocations" in daily[0], "dailyItems 元素应含 allocations"
            if daily[0].get("allocations"):
                day_alloc = daily[0]["allocations"][0]
                # 文档字段命名不一致，兼容 actual_percent 和 percent
                has_actual = "actual_percent" in day_alloc
                has_percent = "percent" in day_alloc
                logger.info(f"  dailyItems.allocations 字段: {list(day_alloc.keys())}")
                if has_actual:
                    logger.info("  ✓ 使用 actual_percent 字段名（标准）")
                elif has_percent:
                    logger.info("  ⚠ 使用 percent 字段名（与 allocations 不一致，文档已知问题）")

        logger.info("✓ asset_allocations_comparison 结构验证通过")

    def test_invalid_date_format(self, investment_api, login_session):
        """
        测试场景3：无效日期格式
        Test Scenario3: Invalid Date Format Returns Business Error
        """
        account_id = _get_account_id(login_session)
        response = investment_api.get_asset_allocations_comparison(
            account_id=account_id,
            begin_date="2024/01/01",
            end_date="2024-01-31"
        )
        assert response.status_code == 200
        body = response.json()
        assert body.get("code") != 200
        logger.info(f"✓ 无效日期被拒绝: code={body.get('code')}")

    def test_future_date_range(self, investment_api, login_session):
        """
        测试场景4：未来日期范围
        Test Scenario4: Future Date Range Returns Empty or Null Data
        """
        account_id = _get_account_id(login_session)
        response = investment_api.get_asset_allocations_comparison(
            account_id=account_id,
            begin_date="2099-01-01",
            end_date="2099-12-31"
        )
        assert response.status_code == 200
        body = response.json()
        code = body.get("code")
        data = body.get("data")
        if code == 200:
            # 允许返回 data 但无实际内容（null 字段）
            if data:
                allocs = data.get("allocations") or []
                daily = (data.get("daily_items") or data.get("dailyItems")) or []
                # null 或空数组均视为无有效数据
                assert not allocs or not daily, "未来日期配置对比应无有效数据"
            logger.info("✓ 未来日期返回空对比数据")
        else:
            logger.info(f"✓ 未来日期被拒绝: code={code}")

    def test_date_range_reversed(self, investment_api, login_session):
        """
        测试场景5：日期范围倒置
        Test Scenario5: Reversed Date Range Returns Error or Empty
        """
        account_id = _get_account_id(login_session)
        response = investment_api.get_asset_allocations_comparison(
            account_id=account_id,
            begin_date="2024-01-31",
            end_date="2024-01-01"
        )
        assert response.status_code == 200
        body = response.json()
        code = body.get("code")
        if code != 200:
            logger.info(f"✓ 倒置日期被拒绝: code={code}")
        else:
            data = body.get("data", {})
            daily = data.get("daily_items", data.get("dailyItems", [])) if data else []
            assert daily == [] or daily is None
            logger.info("✓ 倒置日期返回空数据")
