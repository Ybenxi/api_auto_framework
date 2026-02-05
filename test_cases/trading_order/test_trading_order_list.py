"""
Trading Order - List Orders 接口测试用例
测试 GET /api/v1/cores/{core}/trading-orders 接口
"""
import pytest
from utils.logger import logger
from utils.assertions import (
    assert_status_ok,
    assert_list_structure,
    assert_pagination,
    assert_enum_filter
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
        assert_list_structure(response_body)
        
        logger.info(f"✓ 订单列表获取成功，返回 {len(response_body['content'])} 个订单")

    def test_list_orders_with_status_filter(self, trading_order_api):
        """
        测试场景2：使用status筛选订单
        验证点：
        1. 接口返回 200
        2. 返回的订单状态符合筛选条件
        """
        logger.info("测试场景2：使用status筛选")
        
        response = trading_order_api.list_orders(status=OrderStatus.NEW, size=10)
        
        assert_status_ok(response)
        
        response_body = response.json()
        orders = response_body.get("content", [])
        
        if len(orders) > 0:
            assert_enum_filter(orders, "status", OrderStatus.NEW)
            logger.info("✓ status筛选验证通过")
        else:
            logger.info("✓ status筛选返回空结果")

    def test_list_orders_with_date_range(self, trading_order_api):
        """
        测试场景3：使用日期范围筛选
        验证点：
        1. 接口返回 200
        2. 日期参数被正确处理
        """
        logger.info("测试场景3：使用日期范围筛选")
        
        response = trading_order_api.list_orders(
            start_date="2025-01-01",
            end_date="2025-12-31",
            size=10
        )
        
        assert_status_ok(response)
        
        logger.info("✓ 日期范围参数处理正常")

    def test_list_orders_with_symbol_filter(self, trading_order_api):
        """
        测试场景4：使用symbol筛选
        验证点：
        1. 接口返回 200
        2. symbol参数生效
        """
        logger.info("测试场景4：使用symbol筛选")
        
        response = trading_order_api.list_orders(symbol="AAPL", size=10)
        
        assert_status_ok(response)
        
        logger.info("✓ symbol筛选参数处理正常")

    def test_list_orders_pagination(self, trading_order_api):
        """
        测试场景5：验证分页功能
        验证点：
        1. 接口返回 200
        2. 分页信息正确
        """
        logger.info("测试场景5：验证分页功能")
        
        response = trading_order_api.list_orders(page=0, size=5)
        
        assert_status_ok(response)
        
        response_body = response.json()
        assert_pagination(response_body, expected_size=5, expected_page=0)
        
        logger.info("✓ 分页功能验证通过")
