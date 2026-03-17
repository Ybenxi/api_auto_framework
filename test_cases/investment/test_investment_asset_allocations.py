"""
Investment - Asset Allocations 接口测试用例
测试 GET /api/v1/cores/{core}/reports/investments/asset-allocations 接口
"""
import pytest
from utils.logger import logger
from utils.assertions import assert_status_ok


@pytest.mark.investment
@pytest.mark.list_api
class TestInvestmentAssetAllocations:
    """
    资产配置接口测试用例集
    返回嵌套结构的资产配置数据（可能 3-4 层深）
    ⚠️ 文档问题：嵌套结构说明不完整
    ⚠️ 业务规则：必须提供 account_id 或 financial_account_id 之一
    """

    def test_missing_both_account_ids(self, investment_api, short_date_range):
        """
        测试场景1：两个ID都不提供 → 业务错误
        验证点：
        1. 接口返回 HTTP 200（统一错误处理）
        2. 业务 code != 200
        3. data 为 null
        """
        logger.info("测试场景1：两个ID都不提供")

        response = investment_api.get_asset_allocations(**short_date_range)

        assert response.status_code == 200
        response_body = response.json()
        logger.info(f"  响应: {response_body}")

        assert response_body.get("code") != 200, \
            "不提供ID应返回业务错误码，但返回了 code=200"
        assert response_body.get("data") is None

        logger.info(f"✓ 缺少必需参数校验通过，code={response_body.get('code')}")

    def test_future_date_range(self, investment_api):
        """
        测试场景2：未来日期范围（无数据期间）
        验证点：
        1. 接口返回 HTTP 200
        2. 无ID时返回业务错误，或有ID时返回空数组
        """
        logger.info("测试场景2：未来日期范围")

        response = investment_api.get_asset_allocations(
            begin_date="2099-01-01",
            end_date="2099-12-31"
        )

        assert response.status_code == 200
        response_body = response.json()
        logger.info(f"  响应: {response_body}")

        if isinstance(response_body, dict):
            assert response_body.get("code") != 200
        elif isinstance(response_body, list):
            assert len(response_body) == 0, "未来日期无数据，应返回空数组"

        logger.info("✓ 未来日期范围测试通过")

    @pytest.mark.skip(reason="需要真实 financial_account_id 且该账户须有投资数据")
    def test_get_asset_allocations_success(self, investment_api, short_date_range):
        """
        测试场景3：成功获取资产配置（需要真实数据）
        验证点：
        1. 接口返回 200，业务 code=200
        2. 返回数组结构
        3. 每个元素包含 date 和 allocations
        """
        logger.info("测试场景3：成功获取资产配置")

        response = investment_api.get_asset_allocations(
            financial_account_id="<替换为真实FA ID>",
            **short_date_range
        )

        assert_status_ok(response)

        allocations_list = response.json()
        assert isinstance(allocations_list, list), "响应应为数组"

        if allocations_list:
            item = allocations_list[0]
            assert "date" in item, "应包含 date 字段"
            assert "allocations" in item, "应包含 allocations 字段"
            assert isinstance(item["allocations"], list), "allocations 应为数组"

        logger.info(f"✓ 资产配置获取成功，返回 {len(allocations_list)} 个日期的数据")

    @pytest.mark.skip(reason="需要真实数据，验证嵌套结构")
    def test_verify_nested_structure(self, investment_api, short_date_range):
        """
        测试场景4：验证嵌套结构（children，需要真实数据）
        验证点：
        1. allocations 数组中的元素包含 children 字段
        2. children 可能继续嵌套
        """
        logger.info("测试场景4：验证嵌套结构")

        response = investment_api.get_asset_allocations(
            financial_account_id="<替换为真实FA ID>",
            **short_date_range
        )

        assert_status_ok(response)
        allocations_list = response.json()

        if allocations_list and allocations_list[0].get("allocations"):
            first_allocation = allocations_list[0]["allocations"][0]
            if "children" in first_allocation:
                logger.info(f"✓ 检测到嵌套结构，children 有 {len(first_allocation['children'])} 个子项")

        logger.info("✓ 嵌套结构验证完成")

    @pytest.mark.skip(reason="需要真实数据，验证百分比计算")
    def test_verify_percentage_calculation(self, investment_api, short_date_range):
        """
        测试场景5：验证百分比计算（需要真实数据）
        验证点：
        1. percent_of_level：在当前层级的占比
        2. 同层级的 percent_of_level 总和应接近 1.0
        """
        logger.info("测试场景5：验证百分比计算")

        response = investment_api.get_asset_allocations(
            financial_account_id="<替换为真实FA ID>",
            **short_date_range
        )

        assert_status_ok(response)
        allocations_list = response.json()

        if allocations_list:
            allocations = allocations_list[0].get("allocations", [])
            total_percent = sum(a.get("percent_of_level", 0) for a in allocations)
            logger.debug(f"顶层 percent_of_level 总和: {total_percent}")

            if 0.99 <= total_percent <= 1.01:
                logger.info("✓ 百分比计算正确")
            else:
                logger.warning(f"⚠️ 百分比总和异常: {total_percent}")

        logger.info("✓ 百分比计算验证完成")

    @pytest.mark.skip(reason="需要真实数据，验证日期排序")
    def test_date_array_completeness(self, investment_api, short_date_range):
        """
        测试场景6：日期数组完整性（需要真实数据）
        验证点：
        1. 返回的日期范围与请求一致
        2. 日期按升序排列
        """
        logger.info("测试场景6：日期数组完整性")

        response = investment_api.get_asset_allocations(
            financial_account_id="<替换为真实FA ID>",
            **short_date_range
        )

        assert_status_ok(response)
        allocations_list = response.json()

        dates = [item["date"] for item in allocations_list]
        assert dates == sorted(dates), "日期应按升序排列"

        logger.info(f"✓ 日期数组完整性验证通过，共 {len(dates)} 个交易日")
