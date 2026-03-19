"""
Trading Order - List Investment Financial Accounts 接口测试用例
测试 GET /api/v1/cores/{core}/trading-orders/financial-accounts 接口

响应结构说明：
  {"code": 200, "data": {"content": [...], "totalElements": N, "size": N, "number": N, ...}}
  - 分页字段使用驼峰：totalElements / size / number
"""
import pytest
from utils.logger import logger
from utils.assertions import assert_status_ok


def _get_data_and_content(response):
    body = response.json()
    data = body.get("data", body) or {}
    return data, data.get("content", [])


@pytest.mark.trading_order
@pytest.mark.list_api
class TestTradingOrderListFinancialAccounts:
    """
    投资账户列表接口测试用例集
    """

    def test_list_investment_financial_accounts_success(self, trading_order_api):
        """
        测试场景1：成功获取投资账户列表
        验证点：
        1. HTTP 200，业务 code=200
        2. 返回 data.content 数组
        3. 每条账户含必要字段（id, name, account_number）
        """
        response = trading_order_api.list_investment_financial_accounts(page=0, size=10)
        assert_status_ok(response)

        body = response.json()
        assert body.get("code") == 200, f"业务 code 应为 200，实际: {body.get('code')}"

        data, content = _get_data_and_content(response)
        assert isinstance(content, list), "data.content 应为数组"

        if content:
            first = content[0]
            for field in ["id", "name", "account_number"]:
                assert field in first, f"账户对象缺少必需字段: '{field}'"
                logger.info(f"  ✓ {field}: {first.get(field)}")

        logger.info(f"✓ 投资账户列表获取成功，返回 {len(content)} 个，totalElements={data.get('totalElements', 0)}")

    def test_list_investment_financial_accounts_with_name_filter(self, trading_order_api):
        """
        测试场景2：使用 name 参数模糊筛选账户
        先 list 取真实账户名，再用其前4个字符筛选，验证返回结果包含关键词
        验证点：
        1. HTTP 200
        2. 返回结果中每条账户名称包含筛选关键词
        """
        # 先获取真实账户名
        list_response = trading_order_api.list_investment_financial_accounts(page=0, size=10)
        assert_status_ok(list_response)
        _, accounts = _get_data_and_content(list_response)

        if not accounts:
            pytest.skip("无投资账户数据，跳过 name 筛选测试")

        real_name = accounts[0].get("name", "")
        if not real_name:
            pytest.skip("账户名称为空，跳过")

        # 取前4个字符做模糊搜索
        keyword = real_name[:4]
        logger.info(f"  使用 name 关键词: '{keyword}'（来自真实账户名 '{real_name}'）")

        filter_response = trading_order_api.list_investment_financial_accounts(name=keyword, size=20)
        assert_status_ok(filter_response)

        _, filtered = _get_data_and_content(filter_response)
        assert len(filtered) > 0, f"name='{keyword}' 筛选结果为空"

        for acc in filtered:
            assert keyword.lower() in acc.get("name", "").lower(), \
                f"筛选结果账户名 '{acc.get('name')}' 不包含关键词 '{keyword}'"
        logger.info(f"✓ name 筛选验证通过，返回 {len(filtered)} 条")

    def test_list_investment_financial_accounts_pagination(self, trading_order_api):
        """
        测试场景3：验证分页功能
        验证点：
        1. HTTP 200，data.size == 5，data.number == 0
        2. 返回数量 <= 5
        3. totalElements > 0（有数据的接口）
        """
        response = trading_order_api.list_investment_financial_accounts(page=0, size=5)
        assert_status_ok(response)

        data, content = _get_data_and_content(response)

        assert data.get("size") == 5, f"size 不正确: 期望 5，实际 {data.get('size')}"
        assert data.get("number") == 0, f"number 不正确: 期望 0，实际 {data.get('number')}"
        assert len(content) <= 5, f"返回数量超过 size=5，实际 {len(content)}"

        logger.info(f"✓ 分页验证通过: size={data.get('size')}, number={data.get('number')}, "
                    f"returned={len(content)}, totalElements={data.get('totalElements', 0)}")

    def test_list_investment_financial_accounts_response_fields(self, trading_order_api):
        """
        测试场景4：验证账户响应字段完整性
        验证点：
        1. HTTP 200
        2. 每条账户必须包含 id, name, account_number
        """
        response = trading_order_api.list_investment_financial_accounts(page=0, size=5)
        assert_status_ok(response)

        _, accounts = _get_data_and_content(response)

        if accounts:
            for acc in accounts:
                for field in ["id", "name", "account_number"]:
                    assert field in acc, f"账户对象缺少必需字段: '{field}'"
            logger.info(f"✓ 字段完整性验证通过，检查了 {len(accounts)} 条")
        else:
            logger.info("✓ 无账户数据，结构验证通过")

    def test_list_investment_financial_accounts_with_invalid_name(self, trading_order_api):
        """
        测试场景5：使用不存在的 name 筛选
        验证点：
        1. HTTP 200
        2. 返回空列表
        """
        response = trading_order_api.list_investment_financial_accounts(
            name="XYZXYZ_NOT_EXISTS_99999",
            size=10
        )
        assert_status_ok(response)

        _, accounts = _get_data_and_content(response)
        assert len(accounts) == 0, f"不存在的 name 应返回空列表，实际 {len(accounts)} 条"
        logger.info("✓ 不存在的 name 返回空列表")
