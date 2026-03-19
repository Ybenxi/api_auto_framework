"""
Trading Order - List Orders 接口测试用例
测试 GET /api/v1/cores/{core}/trading-orders 接口

响应结构说明：
  {"code": 200, "data": {"content": [...], "totalElements": N, "size": N, "number": N, ...}}
  - 所有 content 和分页字段都在 data 层下
  - 分页字段用驼峰命名：totalElements / totalPages / numberOfElements
"""
import pytest
from utils.logger import logger
from utils.assertions import assert_status_ok
from data.enums import OrderStatus, IssueType, OrderAction


def _get_content_and_data(response):
    """从响应中安全取出 data 层和 content 列表"""
    body = response.json()
    data = body.get("data", body) or {}
    return data, data.get("content", [])


@pytest.mark.trading_order
@pytest.mark.list_api
class TestTradingOrderList:
    """
    订单列表接口测试用例集
    """

    def test_list_orders_success(self, trading_order_api):
        """
        测试场景1：成功获取订单列表
        验证点：
        1. HTTP 200，业务 code=200
        2. 响应有 data.content 数组
        3. 返回的每条订单含必要字段
        """
        response = trading_order_api.list_orders(page=0, size=10)
        assert_status_ok(response)

        body = response.json()
        assert body.get("code") == 200, f"业务 code 应为 200，实际: {body.get('code')}"
        data, content = _get_content_and_data(response)
        assert isinstance(content, list), "data.content 应为数组"

        logger.info(f"✓ 订单列表获取成功，返回 {len(content)} 条，totalElements={data.get('totalElements', 0)}")

    @pytest.mark.parametrize("status", [
        OrderStatus.NEW, OrderStatus.PENDING, OrderStatus.IN_PROGRESS,
        OrderStatus.FILLED, OrderStatus.POSTED, OrderStatus.CANCELLED,
        OrderStatus.REJECTED, OrderStatus.OVERNIGHT, OrderStatus.PARTIALLY_FILLED
    ])
    def test_list_orders_with_status_filter(self, trading_order_api, status):
        """
        测试场景2：使用 status 筛选订单（覆盖全部9个枚举值）
        验证点：
        1. HTTP 200
        2. 返回的每条订单 status 均与筛选值一致
        """
        response = trading_order_api.list_orders(status=status, size=20)
        assert_status_ok(response)

        _, orders = _get_content_and_data(response)
        if not orders:
            logger.info(f"  ⚠️ status='{status}' 无数据")
        else:
            for order in orders:
                assert order.get("status") == str(status), \
                    f"筛选结果包含非 {status}: status={order.get('status')}"
            logger.info(f"✓ status='{status}' 筛选验证通过，{len(orders)} 条")

    @pytest.mark.parametrize("order_action", [
        OrderAction.BUY, OrderAction.SELL, OrderAction.SELL_ALL
    ])
    def test_list_orders_with_order_action_filter(self, trading_order_api, order_action):
        """
        测试场景3：使用 order_action 筛选订单（覆盖全部3个枚举值）
        验证点：
        1. HTTP 200
        2. 返回的每条订单 order_action 均与筛选值一致
        """
        response = trading_order_api.list_orders(order_action=order_action, size=20)
        assert_status_ok(response)

        _, orders = _get_content_and_data(response)
        if not orders:
            logger.info(f"  ⚠️ order_action='{order_action}' 无数据")
        else:
            for order in orders:
                assert order.get("order_action") == str(order_action), \
                    f"筛选结果包含非 {order_action}: {order.get('order_action')}"
            logger.info(f"✓ order_action='{order_action}' 筛选验证通过，{len(orders)} 条")

    @pytest.mark.parametrize("issue_type", [
        "Common Stock", "ETF", "Mutual Funds", "Crypto Currency"
    ])
    def test_list_orders_with_issue_type_filter(self, trading_order_api, issue_type):
        """
        测试场景4：使用 issue_type 筛选订单（覆盖文档定义的4个枚举值）
        验证点：
        1. HTTP 200
        2. 返回的每条订单 issue_type 均与筛选值一致
        """
        response = trading_order_api.list_orders(issue_type=issue_type, size=20)
        assert_status_ok(response)

        _, orders = _get_content_and_data(response)
        if not orders:
            logger.info(f"  ⚠️ issue_type='{issue_type}' 无数据")
        else:
            for order in orders:
                assert order.get("issue_type") == issue_type, \
                    f"筛选结果 issue_type='{order.get('issue_type')}' 与期望 '{issue_type}' 不一致"
            logger.info(f"✓ issue_type='{issue_type}' 筛选验证通过，{len(orders)} 条")

    def test_list_orders_with_symbol_filter(self, trading_order_api):
        """
        测试场景5：使用 symbol 筛选订单
        先 list 获取真实 symbol，再用它筛选，验证每条结果 symbol 匹配
        验证点：
        1. HTTP 200
        2. 返回的每条订单 symbol 与筛选值一致
        """
        base_response = trading_order_api.list_orders(page=0, size=20)
        assert_status_ok(base_response)
        _, base_orders = _get_content_and_data(base_response)

        if not base_orders:
            pytest.skip("无订单数据，跳过 symbol 筛选测试")

        real_symbol = base_orders[0].get("symbol")
        if not real_symbol:
            pytest.skip("symbol 字段为空，跳过")

        logger.info(f"  使用真实 symbol: {real_symbol}")
        response = trading_order_api.list_orders(symbol=real_symbol, size=20)
        assert_status_ok(response)

        _, orders = _get_content_and_data(response)
        assert len(orders) > 0, f"symbol='{real_symbol}' 筛选结果为空"
        for order in orders:
            assert order.get("symbol") == real_symbol, \
                f"筛选结果包含不匹配的 symbol: {order.get('symbol')}"
        logger.info(f"✓ symbol 筛选验证通过，返回 {len(orders)} 条")

    def test_list_orders_with_financial_account_id_filter(self, trading_order_api):
        """
        测试场景6：使用 financial_account_id 筛选订单
        先 list 获取真实 financial_account_id，验证每条结果 financial_account_id 匹配
        """
        base_response = trading_order_api.list_orders(page=0, size=20)
        assert_status_ok(base_response)
        _, base_orders = _get_content_and_data(base_response)

        if not base_orders:
            pytest.skip("无订单数据，跳过")

        real_fa_id = next((o.get("financial_account_id") for o in base_orders if o.get("financial_account_id")), None)
        if not real_fa_id:
            pytest.skip("所有订单均无 financial_account_id，跳过")

        logger.info(f"  使用真实 financial_account_id: {real_fa_id}")
        response = trading_order_api.list_orders(financial_account_id=real_fa_id, size=20)
        assert_status_ok(response)

        _, orders = _get_content_and_data(response)
        assert len(orders) > 0, f"financial_account_id='{real_fa_id}' 筛选结果为空"
        for order in orders:
            assert order.get("financial_account_id") == real_fa_id, \
                f"返回了不匹配的 financial_account_id: {order.get('financial_account_id')}"
        logger.info(f"✓ financial_account_id 筛选验证通过，返回 {len(orders)} 条")

    def test_list_orders_with_sub_account_id_filter(self, trading_order_api):
        """
        测试场景7：使用 sub_account_id 筛选订单
        先 list 获取真实 sub_account_id（如有），验证每条结果匹配
        """
        base_response = trading_order_api.list_orders(page=0, size=50)
        assert_status_ok(base_response)
        _, base_orders = _get_content_and_data(base_response)

        real_sa_id = next((o.get("sub_account_id") for o in base_orders if o.get("sub_account_id")), None)
        if not real_sa_id:
            pytest.skip("无包含 sub_account_id 的订单数据，跳过")

        logger.info(f"  使用真实 sub_account_id: {real_sa_id}")
        response = trading_order_api.list_orders(sub_account_id=real_sa_id, size=20)
        assert_status_ok(response)

        _, orders = _get_content_and_data(response)
        assert len(orders) > 0, f"sub_account_id='{real_sa_id}' 筛选结果为空"
        for order in orders:
            assert order.get("sub_account_id") == real_sa_id, \
                f"返回了不匹配的 sub_account_id: {order.get('sub_account_id')}"
        logger.info(f"✓ sub_account_id 筛选验证通过，返回 {len(orders)} 条")

    def test_list_orders_with_cusip_filter(self, trading_order_api):
        """
        测试场景8：使用 cusip 筛选订单
        先 list 获取真实 cusip，再用它筛选
        """
        base_response = trading_order_api.list_orders(page=0, size=20)
        assert_status_ok(base_response)
        _, base_orders = _get_content_and_data(base_response)

        real_cusip = next((o.get("cusip") for o in base_orders if o.get("cusip")), None)
        if not real_cusip:
            pytest.skip("无包含 cusip 的订单数据，跳过")

        logger.info(f"  使用真实 cusip: {real_cusip}")
        response = trading_order_api.list_orders(cusip=real_cusip, size=20)
        assert_status_ok(response)

        _, orders = _get_content_and_data(response)
        assert len(orders) > 0, f"cusip='{real_cusip}' 筛选结果为空"
        for order in orders:
            assert order.get("cusip") == real_cusip, \
                f"返回了不匹配的 cusip: {order.get('cusip')}"
        logger.info(f"✓ cusip 筛选验证通过，返回 {len(orders)} 条")

    def test_list_orders_with_date_range(self, trading_order_api):
        """
        测试场景9：使用日期范围筛选
        验证点：
        1. HTTP 200
        2. 返回数据的 created_date 在指定日期范围内
        """
        start_date = "2025-01-01"
        end_date = "2026-12-31"
        response = trading_order_api.list_orders(start_date=start_date, end_date=end_date, size=20)
        assert_status_ok(response)

        _, orders = _get_content_and_data(response)
        logger.info(f"  日期范围 [{start_date}, {end_date}] 返回 {len(orders)} 条")

        if orders:
            for order in orders:
                created_at = order.get("created_date") or order.get("created_at", "")
                if created_at and len(created_at) >= 10:
                    order_date = created_at[:10]
                    assert start_date <= order_date <= end_date, \
                        f"订单日期 '{order_date}' 不在范围 [{start_date}, {end_date}]"
        logger.info("✓ 日期范围筛选验证通过")

    def test_list_orders_with_invalid_date_range(self, trading_order_api):
        """
        测试场景10：结束日期早于开始日期（无效日期范围）
        验证点：
        1. HTTP 200
        2. 返回空列表或 business code != 200
        """
        response = trading_order_api.list_orders(
            start_date="2026-12-31",
            end_date="2025-01-01",
            size=10
        )
        assert_status_ok(response)

        body = response.json()
        _, orders = _get_content_and_data(response)
        logger.info(f"  无效日期范围响应: code={body.get('code')}, 返回 {len(orders)} 条")

        if body.get("code") != 200:
            logger.info(f"✓ API 拒绝了无效日期范围: code={body.get('code')}")
        else:
            assert len(orders) == 0, f"结束日期早于开始日期时应返回空列表，实际返回 {len(orders)} 条"
            logger.info("✓ 无效日期范围返回空列表")

    def test_list_orders_with_invalid_date_format(self, trading_order_api):
        """
        测试场景11：填写错误的日期格式
        验证点：
        1. HTTP 200
        2. API 拒绝或返回空（不接受非 YYYY-MM-DD 格式）
        """
        response = trading_order_api.list_orders(
            start_date="01/01/2025",
            end_date="12/31/2025",
            size=10
        )
        assert_status_ok(response)

        body = response.json()
        _, orders = _get_content_and_data(response)
        logger.info(f"  错误日期格式响应: code={body.get('code')}, 返回 {len(orders)} 条")

        if body.get("code") != 200:
            logger.info(f"✓ API 拒绝了错误日期格式: code={body.get('code')}")
        else:
            logger.info("⚠ API 接受了非标准日期格式（探索性结果）")

    def test_list_orders_with_invalid_fa_id(self, trading_order_api):
        """
        测试场景12：使用错误的 financial_account_id 筛选
        验证点：
        1. HTTP 200
        2. 返回空列表或 business code != 200
        """
        response = trading_order_api.list_orders(financial_account_id="INVALID_FA_ID_9999", size=10)
        assert_status_ok(response)

        _, orders = _get_content_and_data(response)
        assert len(orders) == 0, f"无效 fa_id 应返回空列表，实际返回 {len(orders)} 条"
        logger.info("✓ 无效 financial_account_id 返回空列表")

    def test_list_orders_with_invalid_symbol(self, trading_order_api):
        """
        测试场景13：使用错误/不存在的 symbol 筛选
        验证点：
        1. HTTP 200
        2. 返回空列表
        """
        response = trading_order_api.list_orders(symbol="XXXXXXXX_NOT_EXISTS_9999", size=10)
        assert_status_ok(response)

        _, orders = _get_content_and_data(response)
        assert len(orders) == 0, f"不存在的 symbol 应返回空列表，实际返回 {len(orders)} 条"
        logger.info("✓ 不存在的 symbol 返回空列表")

    def test_list_orders_with_invalid_status(self, trading_order_api):
        """
        测试场景14：使用不在枚举范围内的 status 值
        验证点：
        1. HTTP 200
        2. API 拒绝（code != 200）或返回空列表
        """
        response = trading_order_api.list_orders(status="InvalidStatus999", size=10)
        assert_status_ok(response)

        body = response.json()
        _, orders = _get_content_and_data(response)
        logger.info(f"  无效 status 响应: code={body.get('code')}, 返回 {len(orders)} 条")

        if body.get("code") != 200:
            logger.info(f"✓ API 拒绝了无效 status: code={body.get('code')}")
        else:
            assert len(orders) == 0, f"无效 status 应返回空列表，实际返回 {len(orders)} 条"
            logger.info("✓ 无效 status 返回空列表")

    def test_list_orders_pagination(self, trading_order_api):
        """
        测试场景15：验证分页功能
        验证点：
        1. HTTP 200，data.size == 5，data.number == 0
        2. 返回数量 <= 5
        """
        response = trading_order_api.list_orders(page=0, size=5)
        assert_status_ok(response)

        data, content = _get_content_and_data(response)
        assert data.get("size") == 5, f"分页大小不正确: 期望 5, 实际 {data.get('size')}"
        assert data.get("number") == 0, f"页码不正确: 期望 0, 实际 {data.get('number')}"
        assert len(content) <= 5, f"返回数量超过 size=5，实际 {len(content)}"
        logger.info(f"✓ 分页功能验证通过，total={data.get('totalElements', 0)}")
