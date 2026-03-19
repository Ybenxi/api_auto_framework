"""
Trading Order - List Securities 接口测试用例
测试 GET /api/v1/cores/{core}/trading-orders/securities 接口

文档定义的 issue_type 枚举（只有4个，不包含 Bond）：
  Common Stock / ETF / Mutual Funds / Crypto Currency

symbol 和 issue_type 均支持数组传参（多值）。

响应结构说明：
  {"code": 200, "data": {"content": [...], "totalElements": N, "size": N, ...}}
"""
import pytest
from utils.logger import logger
from utils.assertions import assert_status_ok


# 文档定义的4个 issue_type 枚举值（不包含 Bond 等非文档值）
VALID_ISSUE_TYPES = ["Common Stock", "ETF", "Mutual Funds", "Crypto Currency"]


def _get_data_and_content(response):
    body = response.json()
    data = body.get("data", body) or {}
    return data, data.get("content", [])


@pytest.mark.trading_order
@pytest.mark.list_api
class TestTradingOrderListSecurities:
    """
    可交易证券列表接口测试用例集
    """

    def test_list_securities_success(self, trading_order_api):
        """
        测试场景1：成功获取证券列表
        验证点：
        1. HTTP 200，业务 code=200
        2. 返回 data.content 数组
        3. 每条证券含必要字段
        """
        response = trading_order_api.list_securities(page=0, size=10)
        assert_status_ok(response)

        body = response.json()
        assert body.get("code") == 200, f"业务 code 应为 200，实际: {body.get('code')}"

        data, content = _get_data_and_content(response)
        assert isinstance(content, list), "data.content 应为数组"

        if content:
            first = content[0]
            for field in ["id", "name", "symbol", "issue_type"]:
                assert field in first, f"证券对象缺少必需字段: '{field}'"
                logger.info(f"  ✓ {field}: {first.get(field)}")

        logger.info(f"✓ 证券列表获取成功，返回 {len(content)} 个，totalElements={data.get('totalElements', 0)}")

    @pytest.mark.parametrize("issue_type", VALID_ISSUE_TYPES)
    def test_list_securities_with_issue_type_filter(self, trading_order_api, issue_type):
        """
        测试场景2：使用 issue_type 单值筛选（覆盖文档定义的4个枚举值）
        验证点：
        1. HTTP 200
        2. 返回的每条证券 issue_type 与筛选值一致
        """
        response = trading_order_api.list_securities(issue_type=issue_type, size=10)
        assert_status_ok(response)

        _, securities = _get_data_and_content(response)
        logger.info(f"  issue_type='{issue_type}' 返回 {len(securities)} 个证券")

        if securities:
            for sec in securities:
                assert sec.get("issue_type") == issue_type, \
                    f"返回证券 issue_type='{sec.get('issue_type')}' 与筛选值 '{issue_type}' 不一致"
            logger.info(f"✓ issue_type='{issue_type}' 筛选验证通过")
        else:
            logger.info(f"  ⚠ issue_type='{issue_type}' 无数据，仅验证接口可调通")

    def test_list_securities_with_multiple_issue_types(self, trading_order_api):
        """
        测试场景3：使用 issue_type 数组传参（同时筛选多个类型）
        验证点：
        1. HTTP 200
        2. 返回的证券 issue_type 均在传入的数组中
        """
        issue_types = ["Common Stock", "ETF"]
        response = trading_order_api.list_securities(issue_type=issue_types, size=20)
        assert_status_ok(response)

        _, securities = _get_data_and_content(response)
        logger.info(f"  多 issue_type 筛选返回 {len(securities)} 个证券")

        if securities:
            for sec in securities:
                assert sec.get("issue_type") in issue_types, \
                    f"返回证券 issue_type='{sec.get('issue_type')}' 不在传入列表 {issue_types} 中"
            logger.info(f"✓ 多 issue_type 数组筛选验证通过")

    def test_list_securities_with_symbol_filter_single(self, trading_order_api):
        """
        测试场景4：使用 symbol 单值筛选
        先 list 获取真实 symbol，再用它筛选，验证每条结果 symbol 匹配
        验证点：
        1. HTTP 200
        2. 返回的每条证券 symbol 与筛选值一致（精确匹配）
        """
        base_response = trading_order_api.list_securities(page=0, size=10)
        assert_status_ok(base_response)
        _, base_securities = _get_data_and_content(base_response)

        if not base_securities:
            pytest.skip("无证券数据，跳过 symbol 筛选测试")

        real_symbol = base_securities[0].get("symbol", "")
        if not real_symbol:
            pytest.skip("symbol 字段为空，跳过")

        logger.info(f"  使用真实 symbol: {real_symbol}")
        response = trading_order_api.list_securities(symbol=real_symbol, size=20)
        assert_status_ok(response)

        _, securities = _get_data_and_content(response)
        assert len(securities) > 0, f"symbol='{real_symbol}' 筛选结果为空"

        for sec in securities:
            assert sec.get("symbol") == real_symbol, \
                f"返回证券 symbol='{sec.get('symbol')}' 与筛选值 '{real_symbol}' 不一致"
        logger.info(f"✓ symbol 单值筛选验证通过，返回 {len(securities)} 条")

    def test_list_securities_with_symbol_filter_multiple(self, trading_order_api):
        """
        测试场景5：使用 symbol 数组传参（同时筛选多个 symbol）
        先 list 取前2个真实 symbol，用数组方式传参
        验证点：
        1. HTTP 200
        2. 返回的每条证券 symbol 均在传入的数组中
        """
        base_response = trading_order_api.list_securities(page=0, size=20)
        assert_status_ok(base_response)
        _, base_securities = _get_data_and_content(base_response)

        symbols_to_filter = list({s.get("symbol") for s in base_securities if s.get("symbol")})[:2]
        if len(symbols_to_filter) < 2:
            pytest.skip("证券数据不足2条有 symbol，跳过数组传参测试")

        logger.info(f"  使用 symbol 数组: {symbols_to_filter}")
        response = trading_order_api.list_securities(symbol=symbols_to_filter, size=20)
        assert_status_ok(response)

        _, securities = _get_data_and_content(response)
        assert len(securities) > 0, f"symbol 数组筛选结果为空"

        for sec in securities:
            assert sec.get("symbol") in symbols_to_filter, \
                f"返回证券 symbol='{sec.get('symbol')}' 不在传入数组 {symbols_to_filter} 中"
        logger.info(f"✓ symbol 数组传参筛选验证通过，返回 {len(securities)} 条")

    def test_list_securities_with_cusip_filter(self, trading_order_api):
        """
        测试场景6：使用 cusip 筛选证券
        先 list 获取真实 cusip，再用它筛选，验证返回数据匹配
        验证点：
        1. HTTP 200
        2. 返回的每条证券 cusip 与筛选值一致
        """
        base_response = trading_order_api.list_securities(page=0, size=20)
        assert_status_ok(base_response)
        _, base_securities = _get_data_and_content(base_response)

        real_cusip = next((s.get("cusip") for s in base_securities if s.get("cusip")), None)
        if not real_cusip:
            pytest.skip("无包含 cusip 的证券数据，跳过")

        logger.info(f"  使用真实 cusip: {real_cusip}")
        response = trading_order_api.list_securities(cusip=real_cusip, size=10)
        assert_status_ok(response)

        _, securities = _get_data_and_content(response)
        assert len(securities) > 0, f"cusip='{real_cusip}' 筛选结果为空"

        for sec in securities:
            assert sec.get("cusip") == real_cusip, \
                f"返回证券 cusip='{sec.get('cusip')}' 与筛选值 '{real_cusip}' 不一致"
        logger.info(f"✓ cusip 筛选验证通过，返回 {len(securities)} 条")

    def test_list_securities_with_invalid_issue_type(self, trading_order_api):
        """
        测试场景7：使用文档未定义的 issue_type 值（如 Bond）
        验证点：
        1. HTTP 200
        2. 返回空列表 或 business code != 200（API 不接受非文档枚举值）
        """
        response = trading_order_api.list_securities(issue_type="Bond", size=10)
        assert_status_ok(response)

        body = response.json()
        _, securities = _get_data_and_content(response)
        logger.info(f"  非文档 issue_type='Bond' 响应: code={body.get('code')}, 返回 {len(securities)} 条")

        if body.get("code") != 200:
            logger.info(f"✓ API 拒绝了非文档 issue_type: code={body.get('code')}")
        else:
            assert len(securities) == 0, f"非文档 issue_type 应返回空列表，实际 {len(securities)} 条"
            logger.info("✓ 非文档 issue_type 返回空列表")

    def test_list_securities_pagination(self, trading_order_api):
        """
        测试场景8：验证分页功能
        验证点：
        1. HTTP 200，data.size == 5，data.number == 0
        2. 返回数量 <= 5
        """
        response = trading_order_api.list_securities(page=0, size=5)
        assert_status_ok(response)

        data, content = _get_data_and_content(response)
        assert data.get("size") == 5, f"size 不正确: 期望 5，实际 {data.get('size')}"
        assert data.get("number") == 0, f"number 不正确: 期望 0，实际 {data.get('number')}"
        assert len(content) <= 5, f"返回数量超过 size=5，实际 {len(content)}"
        logger.info(f"✓ 分页验证通过: size={data.get('size')}, total={data.get('totalElements', 0)}")
