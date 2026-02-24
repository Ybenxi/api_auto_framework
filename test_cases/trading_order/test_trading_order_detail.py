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
        验证点：
        1. 先 list 获取真实订单 ID
        2. code=200
        3. 返回的 id 与请求的 id 一致
        4. 必需字段均存在
        """
        logger.info("测试场景1：获取订单详情")

        # Trading Order list 响应有 data 包装层
        list_response = trading_order_api.list_orders(size=1)
        assert_status_ok(list_response)

        list_body = list_response.json()
        content_data = list_body.get("data", list_body)
        orders = content_data.get("content", [])

        if not orders:
            pytest.skip("没有可用订单")

        order_id = orders[0]["id"]
        logger.info(f"  使用订单 ID: {order_id}")

        response = trading_order_api.get_order_detail(order_id)
        assert_status_ok(response)

        response_body = response.json()
        assert response_body.get("code") == 200, \
            f"业务 code 不为 200: {response_body.get('code')}"

        order_data = response_body.get("data", {})

        # 验证 ID 一致性
        logger.info("验证返回的 id 与请求的 id 一致")
        assert order_data.get("id") == order_id, \
            f"ID 不一致: 请求 {order_id}, 返回 {order_data.get('id')}"

        # 验证必需字段
        required_fields = ["id", "symbol", "order_action", "status"]
        assert_fields_present(order_data, required_fields, "订单详情")

        logger.info(f"  ✓ id: {order_data.get('id')}")
        logger.info(f"  ✓ symbol: {order_data.get('symbol')}")
        logger.info(f"  ✓ order_action: {order_data.get('order_action')}")
        logger.info(f"  ✓ status: {order_data.get('status')}")
        logger.info("✓ 订单详情获取成功")

    def test_get_order_detail_id_consistency_with_list(self, trading_order_api):
        """
        测试场景2：验证详情数据与列表数据一致性
        验证点：
        1. 详情接口返回的关键字段值与列表接口一致
        """
        logger.info("测试场景2：详情与列表数据一致性")

        list_response = trading_order_api.list_orders(size=1)
        assert_status_ok(list_response)

        list_body = list_response.json()
        content_data = list_body.get("data", list_body)
        orders = content_data.get("content", [])

        if not orders:
            pytest.skip("没有可用订单")

        order_from_list = orders[0]
        order_id = order_from_list["id"]

        response = trading_order_api.get_order_detail(order_id)
        assert_status_ok(response)

        order_from_detail = response.json().get("data", {})

        # 验证关键字段一致
        fields_to_compare = ["id", "symbol", "order_action", "status"]
        logger.info("验证列表与详情关键字段一致")
        for field in fields_to_compare:
            list_val = order_from_list.get(field)
            detail_val = order_from_detail.get(field)
            assert list_val == detail_val, \
                f"字段 '{field}' 列表={list_val} 与详情={detail_val} 不一致"
            logger.info(f"  ✓ {field}: {detail_val}")

        logger.info("✓ 列表与详情数据一致性验证通过")

    def test_get_order_detail_invalid_id(self, trading_order_api):
        """
        测试场景3：使用无效ID获取详情
        验证点：
        1. 返回 200（统一错误处理）
        2. code != 200 或 data is None
        """
        logger.info("测试场景3：使用无效ID")

        response = trading_order_api.get_order_detail("INVALID_ORDER_ID_999")
        assert_status_ok(response)

        response_body = response.json()
        assert response_body.get("code") != 200 or response_body.get("data") is None, \
            "无效 ID 应该返回错误或空数据"

        logger.info(f"✓ 无效 ID 错误处理正常，code={response_body.get('code')}")
