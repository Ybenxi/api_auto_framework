"""
Trading Order - List Orders 接口测试用例
测试 GET /api/v1/cores/{core}/trading-orders 接口
"""
import pytest
from utils.logger import logger
from utils.assertions import (
    assert_status_ok,
    assert_list_structure,
    assert_pagination
)
from data.enums import OrderStatus, IssueType, OrderAction


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
        1. 接口返回 200
        2. 返回列表结构正确
        """
        logger.info("测试场景1：成功获取订单列表")

        response = trading_order_api.list_orders(page=0, size=10)

        assert_status_ok(response)

        response_body = response.json()
        # Trading Order 响应有 data 包装层
        content_data = response_body.get("data", response_body)
        assert "content" in content_data, "响应中缺少 content 字段"
        assert isinstance(content_data["content"], list), "content 不是数组"

        logger.info(f"✓ 订单列表获取成功，返回 {len(content_data['content'])} 个订单")

    @pytest.mark.parametrize("status", [
        OrderStatus.NEW,
        OrderStatus.PENDING,
        OrderStatus.IN_PROGRESS,
        OrderStatus.FILLED,
        OrderStatus.POSTED,
        OrderStatus.CANCELLED,
        OrderStatus.REJECTED,
        OrderStatus.OVERNIGHT,
        OrderStatus.PARTIALLY_FILLED
    ])
    def test_list_orders_with_status_filter(self, trading_order_api, status):
        """
        测试场景2：使用 status 筛选订单（覆盖全部9个枚举值）
        验证点：
        1. 接口返回 200
        2. 返回的每条订单 status 均与筛选值一致
        """
        logger.info(f"测试场景2：使用 status='{status}' 筛选")

        response = trading_order_api.list_orders(status=status, size=10)

        assert_status_ok(response)

        response_body = response.json()
        orders = response_body.get("content", [])

        if not orders:
            logger.info(f"  ⚠️ status='{status}' 无数据，跳过筛选值验证")
        else:
            logger.info(f"验证每条数据的 status 均为 {status}")
            for order in orders:
                assert order.get("status") == str(status), \
                    f"筛选结果包含非 {status} 状态: status={order.get('status')}, id={order.get('id')}"
            logger.info(f"✓ {len(orders)} 条数据均为 {status} 状态")

    @pytest.mark.parametrize("order_action", [
        OrderAction.BUY,
        OrderAction.SELL,
        OrderAction.SELL_ALL
    ])
    def test_list_orders_with_order_action_filter(self, trading_order_api, order_action):
        """
        测试场景3：使用 order_action 筛选订单（覆盖全部3个枚举值）
        验证点：
        1. 接口返回 200
        2. 返回的每条订单 order_action 均与筛选值一致
        """
        logger.info(f"测试场景3：使用 order_action='{order_action}' 筛选")

        response = trading_order_api.list_orders(order_action=order_action, size=10)

        assert_status_ok(response)

        response_body = response.json()
        orders = response_body.get("content", [])

        if not orders:
            logger.info(f"  ⚠️ order_action='{order_action}' 无数据，跳过筛选值验证")
        else:
            logger.info(f"验证每条数据的 order_action 均为 {order_action}")
            for order in orders:
                assert order.get("order_action") == str(order_action), \
                    f"筛选结果包含非 {order_action}: order_action={order.get('order_action')}, id={order.get('id')}"
            logger.info(f"✓ {len(orders)} 条数据均为 {order_action}")

    def test_list_orders_with_symbol_filter(self, trading_order_api):
        """
        测试场景4：使用 symbol 筛选订单
        先 list 获取真实 symbol，验证每条结果包含该 symbol
        验证点：
        1. 接口返回 200
        2. 返回的每条订单 symbol 与筛选值一致
        """
        logger.info("测试场景4：使用 symbol 筛选")

        # Step 1: 获取真实 symbol
        base_response = trading_order_api.list_orders(page=0, size=1)
        assert_status_ok(base_response)
        base_orders = base_response.json().get("content", [])

        if not base_orders:
            pytest.skip("无订单数据，跳过 symbol 筛选测试")

        real_symbol = base_orders[0].get("symbol")
        if not real_symbol:
            pytest.skip("symbol 字段为空，跳过")

        logger.info(f"  使用真实 symbol: {real_symbol}")

        # Step 2: 用真实 symbol 筛选
        response = trading_order_api.list_orders(symbol=real_symbol, size=10)
        assert_status_ok(response)

        orders = response.json().get("content", [])
        assert len(orders) > 0, f"symbol='{real_symbol}' 筛选结果为空"

        # Step 3: 断言每条数据 symbol 匹配
        for order in orders:
            assert order.get("symbol") == real_symbol, \
                f"筛选结果包含不匹配的 symbol: {order.get('symbol')}"

        logger.info(f"✓ symbol 筛选验证通过，返回 {len(orders)} 条")

    def test_list_orders_with_financial_account_id_filter(self, trading_order_api):
        """
        测试场景5：使用 financial_account_id 筛选订单
        先 list 获取真实 financial_account_id，验证每条结果 financial_account_id 匹配
        验证点：
        1. 接口返回 200
        2. 返回的每条订单 financial_account_id 与筛选值一致
        """
        logger.info("测试场景5：使用 financial_account_id 筛选")

        # Step 1: 获取真实 financial_account_id
        base_response = trading_order_api.list_orders(page=0, size=1)
        assert_status_ok(base_response)
        base_orders = base_response.json().get("content", [])

        if not base_orders:
            pytest.skip("无订单数据，跳过")

        real_fa_id = base_orders[0].get("financial_account_id")
        if not real_fa_id:
            pytest.skip("financial_account_id 字段为空，跳过")

        logger.info(f"  使用真实 financial_account_id: {real_fa_id}")

        # Step 2: 筛选
        response = trading_order_api.list_orders(financial_account_id=real_fa_id, size=10)
        assert_status_ok(response)

        orders = response.json().get("content", [])
        assert len(orders) > 0, f"financial_account_id='{real_fa_id}' 筛选结果为空"

        # Step 3: 断言
        for order in orders:
            assert order.get("financial_account_id") == real_fa_id, \
                f"返回了不匹配的 financial_account_id: {order.get('financial_account_id')}"

        logger.info(f"✓ financial_account_id 筛选验证通过，返回 {len(orders)} 条")

    def test_list_orders_with_date_range(self, trading_order_api):
        """
        测试场景6：使用日期范围筛选
        验证点：
        1. 接口返回 200
        2. 返回数据的创建时间在指定日期范围内
        """
        logger.info("测试场景6：使用日期范围筛选")

        start_date = "2025-01-01"
        end_date = "2025-12-31"
        response = trading_order_api.list_orders(
            start_date=start_date,
            end_date=end_date,
            size=10
        )

        assert_status_ok(response)

        response_body = response.json()
        content_data = response_body.get("data", response_body)
        orders = content_data.get("content", [])
        logger.info(f"  日期范围内返回 {len(orders)} 条订单")

        # 验证返回数据的日期在范围内
        if orders:
            for order in orders:
                created_at = order.get("created_at") or order.get("create_date") or order.get("created_date", "")
                if created_at and len(created_at) >= 10:
                    order_date = created_at[:10]
                    assert start_date <= order_date <= end_date, \
                        f"订单日期 '{order_date}' 不在范围 [{start_date}, {end_date}] 内"
            logger.info(f"✓ 日期范围筛选验证通过")
        else:
            logger.info("  无数据返回，跳过日期字段验证")

        logger.info("✓ 日期范围参数处理正常")

    def test_list_orders_pagination(self, trading_order_api):
        """
        测试场景7：验证分页功能
        验证点：
        1. 接口返回 200
        2. 分页信息正确（page=0, size=5）
        3. 返回数量 <= size
        """
        logger.info("测试场景7：验证分页功能")

        response = trading_order_api.list_orders(page=0, size=5)

        assert_status_ok(response)

        response_body = response.json()
        # Trading Order 响应有 data 包装层
        content_data = response_body.get("data", response_body)

        assert content_data.get("size") == 5, \
            f"分页大小不正确: 期望 5, 实际 {content_data.get('size')}"
        assert content_data.get("number") == 0, \
            f"页码不正确: 期望 0, 实际 {content_data.get('number')}"
        assert len(content_data.get("content", [])) <= 5, \
            f"返回数量超过 size=5"

        logger.info("✓ 分页功能验证通过")
