"""
Trading Order - Order Detail 接口测试用例
测试 GET /api/v1/cores/{core}/trading-orders/:id 接口
"""
import pytest
from utils.logger import logger
from utils.assertions import assert_status_ok, assert_fields_present


@pytest.mark.trading_order
@pytest.mark.detail_api
class TestTradingOrderDetail:
    """
    订单详情接口测试用例集
    """

    def test_get_order_detail_success(self, trading_order_api):
        """
        测试场景1：成功获取订单详情
        验证点：1. code=200 2. 返回订单完整信息
        """
        logger.info("测试场景1：获取订单详情")
        
        list_response = trading_order_api.list_orders(size=1)
        assert_status_ok(list_response)
        
        orders = list_response.json().get("content", [])
        if len(orders) == 0:
            pytest.skip("没有可用订单")
        
        order_id = orders[0]["id"]
        logger.info(f"使用订单ID: {order_id}")
        
        response = trading_order_api.get_order_detail(order_id)
        
        assert_status_ok(response)
        
        response_body = response.json()
        assert response_body.get("code") == 200
        
        order_data = response_body.get("data", {})
        required_fields = ["id", "symbol", "order_action", "status"]
        assert_fields_present(order_data, required_fields, "订单详情")
        
        logger.info("✓ 订单详情获取成功")

    def test_get_order_detail_invalid_id(self, trading_order_api):
        """
        测试场景2：使用无效ID获取详情
        验证点：返回错误或空数据
        """
        logger.info("测试场景2：使用无效ID")
        
        response = trading_order_api.get_order_detail("INVALID_ORDER_ID_999")
        
        assert_status_ok(response)
        
        response_body = response.json()
        assert response_body.get("code") != 200 or response_body.get("data") is None
        
        logger.info("✓ 无效ID错误处理正常")
