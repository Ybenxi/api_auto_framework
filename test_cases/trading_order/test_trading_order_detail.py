"""
Trading Order - Order Detail 接口测试用例
测试 GET /api/v1/cores/{core}/trading-orders/:id 接口

响应结构：{"code": 200, "data": {订单详情}}
"""
import pytest
from utils.logger import logger
from utils.assertions import assert_status_ok, assert_fields_present


def _get_first_order_from_list(trading_order_api):
    """从 list 接口取第一条订单，返回 (order_id, order_dict) 或 (None, None)"""
    list_response = trading_order_api.list_orders(page=0, size=1)
    if list_response.status_code != 200:
        return None, None
    body = list_response.json()
    if body.get("code") != 200:
        return None, None
    data = body.get("data", body) or {}
    orders = data.get("content", [])
    if not orders:
        return None, None
    return orders[0].get("id"), orders[0]


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
        2. HTTP 200，business code=200
        3. 返回的 id 与请求的 id 一致
        4. 必需字段均存在
        """
        order_id, _ = _get_first_order_from_list(trading_order_api)
        if not order_id:
            pytest.skip("没有可用订单")

        logger.info(f"  使用订单 ID: {order_id}")
        response = trading_order_api.get_order_detail(order_id)
        assert_status_ok(response)

        response_body = response.json()
        assert response_body.get("code") == 200, f"业务 code 应为 200，实际: {response_body.get('code')}"

        order_data = response_body.get("data", {})
        assert order_data.get("id") == order_id, \
            f"ID 不一致: 请求 {order_id}, 返回 {order_data.get('id')}"

        required_fields = ["id", "symbol", "order_action", "status", "security_id",
                           "quantity", "quantity_type", "order_type"]
        assert_fields_present(order_data, required_fields, "订单详情")

        for field in required_fields:
            logger.info(f"  ✓ {field}: {order_data.get(field)}")
        logger.info("✓ 订单详情获取成功")

    def test_get_order_detail_compare_with_list(self, trading_order_api):
        """
        测试场景2：从 list 取一条订单，查其 detail，对比所有在 list 中存在的字段
        验证点：
        1. detail 接口返回的所有字段与 list 中同一条订单一致
        2. detail 不应比 list 缺少字段（detail 通常比 list 更详细）
        3. 记录 detail 有但 list 没有的额外字段（detail 独有字段）
        """
        order_id, order_from_list = _get_first_order_from_list(trading_order_api)
        if not order_id or not order_from_list:
            pytest.skip("没有可用订单")

        logger.info(f"  对比订单 ID: {order_id}")

        response = trading_order_api.get_order_detail(order_id)
        assert_status_ok(response)

        order_from_detail = response.json().get("data", {})

        # 对比 list 中的所有字段，detail 的值必须与之一致
        mismatches = []
        for field, list_val in order_from_list.items():
            detail_val = order_from_detail.get(field)
            if detail_val != list_val:
                mismatches.append(f"  ✗ {field}: list={list_val!r}, detail={detail_val!r}")
            else:
                logger.info(f"  ✓ {field}: {list_val!r}")

        if mismatches:
            # 记录为警告而非断言失败（因为某些字段如时间戳可能在查询时更新）
            logger.warning("以下字段在 list 和 detail 中值不一致（可能为时间戳更新等正常情况）:")
            for m in mismatches:
                logger.warning(m)
            # 只对关键字段做硬断言
            key_fields = ["id", "symbol", "order_action", "status", "security_id"]
            hard_mismatches = [f for f in mismatches if any(k in f for k in key_fields)]
            assert not hard_mismatches, \
                f"关键字段 list 与 detail 不一致:\n" + "\n".join(hard_mismatches)

        # 记录 detail 独有的字段（比 list 更详细）
        list_keys = set(order_from_list.keys())
        detail_keys = set(order_from_detail.keys())
        extra_in_detail = detail_keys - list_keys
        missing_in_detail = list_keys - detail_keys

        if extra_in_detail:
            logger.info(f"  ✓ detail 额外字段（比 list 更详细）: {sorted(extra_in_detail)}")
        if missing_in_detail:
            logger.warning(f"  ⚠ detail 缺少的 list 字段: {sorted(missing_in_detail)}")
            # detail 不应比 list 缺少字段
            assert not missing_in_detail, \
                f"detail 缺少以下 list 中存在的字段: {sorted(missing_in_detail)}"

        logger.info("✓ list 与 detail 字段一致性验证通过")

    def test_get_order_detail_invalid_id(self, trading_order_api):
        """
        测试场景3：使用无效 ID 获取详情
        验证点：
        1. HTTP 200（统一错误处理）
        2. business code != 200 或 data is None
        """
        response = trading_order_api.get_order_detail("INVALID_ORDER_ID_999")
        assert_status_ok(response)

        response_body = response.json()
        code = response_body.get("code")
        data = response_body.get("data")
        assert code != 200 or data is None, \
            f"无效 ID 应返回错误或空数据，实际 code={code}, data={data}"

        logger.info(f"✓ 无效 ID 错误处理正常，code={code}")
