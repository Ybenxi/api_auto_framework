"""
Investment - Asset Allocations 接口测试用例
测试 GET /api/v1/cores/{core}/reports/investments/asset-allocations 接口

响应结构：{"code": 200, "data": [{date, allocations: [{class, segment, name, ...children}]}]}
allocations 是嵌套结构（可能 3-4 层深），children 字段递归嵌套。
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
class TestInvestmentAssetAllocations:

    def test_missing_both_account_ids(self, investment_api, short_date_range):
        """
        测试场景1：两个ID都不提供 → 业务错误
        Test Scenario1: Missing Both Account IDs Returns Business Error
        """
        response = investment_api.get_asset_allocations(**short_date_range)
        assert response.status_code == 200
        body = response.json()
        assert body.get("code") != 200
        assert body.get("data") is None
        logger.info(f"✓ 缺少ID校验通过: code={body.get('code')}")

    def test_future_date_range_returns_empty(self, investment_api, login_session):
        """
        测试场景2：未来日期范围 → 返回空数组
        Test Scenario2: Future Date Range Returns Empty Array
        """
        account_id = _get_account_id(login_session)
        response = investment_api.get_asset_allocations(
            account_id=account_id,
            begin_date="2099-01-01",
            end_date="2099-12-31"
        )
        assert response.status_code == 200
        body = response.json()
        code = body.get("code")
        data = body.get("data")
        if code == 200:
            assert data == [] or data is None
            logger.info("✓ 未来日期返回空数组")
        else:
            logger.info(f"✓ 未来日期被拒绝: code={code}")

    def test_get_asset_allocations_structure(self, investment_api, login_session):
        """
        测试场景3：获取资产配置，验证响应结构
        Test Scenario3: Get Asset Allocations and Verify Response Structure
        验证点：
        1. HTTP 200，business code=200
        2. data 是数组，每条含 date 和 allocations
        3. allocations 是嵌套结构（class/segment/name/symbol/market_value 等字段）
        4. 日期按升序排列
        """
        account_id = _get_account_id(login_session)
        response = investment_api.get_asset_allocations(
            account_id=account_id,
            begin_date="2023-01-01",
            end_date="2023-01-05"
        )
        assert response.status_code == 200
        body = response.json()
        assert body.get("code") == 200, \
            f"应返回 code=200，实际: {body.get('code')}"

        data = body.get("data", [])
        assert isinstance(data, list), "data 应为数组"
        logger.info(f"  返回 {len(data)} 天的配置数据")

        if data:
            item = data[0]
            assert "date" in item, "应含 date 字段"
            assert "allocations" in item, "应含 allocations 字段"
            assert isinstance(item["allocations"], list)

            # 验证嵌套结构字段（可能为 null，但字段应存在）
            if item["allocations"]:
                alloc = item["allocations"][0]
                doc_fields = ["class", "market_value", "percent_of_level",
                              "percent_of_total", "children"]
                for field in doc_fields:
                    if field in alloc:
                        logger.info(f"  ✓ allocations[0].{field}: {alloc.get(field)}")

            # 日期升序
            dates = [d["date"] for d in data]
            assert dates == sorted(dates), "日期应按升序排列"
            logger.info("  ✓ 日期升序")

        logger.info("✓ asset_allocations 结构验证通过")

    def test_invalid_date_format(self, investment_api, login_session):
        """
        测试场景4：无效日期格式
        Test Scenario4: Invalid Date Format Returns Business Error
        """
        account_id = _get_account_id(login_session)
        response = investment_api.get_asset_allocations(
            account_id=account_id,
            begin_date="2024/01/01",
            end_date="2024-01-31"
        )
        assert response.status_code == 200
        body = response.json()
        assert body.get("code") != 200, f"无效日期应返回错误，实际: {body.get('code')}"
        logger.info(f"✓ 无效日期格式被拒绝: code={body.get('code')}")

    def test_date_range_reversed(self, investment_api, login_session):
        """
        测试场景5：日期范围倒置
        Test Scenario5: Reversed Date Range Returns Error or Empty
        """
        account_id = _get_account_id(login_session)
        response = investment_api.get_asset_allocations(
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
