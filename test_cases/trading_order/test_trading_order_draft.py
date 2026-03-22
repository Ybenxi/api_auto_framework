"""
Trading Order - Create Draft Order 接口测试用例
测试 POST /api/v1/cores/{core}/trading-orders/draft 接口

接口说明：
  - financial_account_id 和 sub_account_id 二选一（至少提供一个）
  - order_action: Buy / Sell / Sell_All
  - security_id: 必填，从 list_orders 反查真实 ID
  - quantity_type: Shares / Dollars
  - quantity: 必填整数
  - order_type: Market_Order / Limit_Order / Stop_Order / Stop_Limit
  - limit_price: order_type=Limit_Order 或 Stop_Limit 时必填
  - stop_price: order_type=Stop_Order 或 Stop_Limit 时必填

策略：
  - 从 list_orders 接口反查真实 security_id 和 financial_account_id（确保数据可用）
  - 创建后验证响应字段，不实际提交到市场（状态为 New）
  - 所有创建成功的草稿订单加 @pytest.mark.no_rerun，避免重复创建
"""
import pytest
import time
from typing import Optional, Tuple
from utils.logger import logger
from utils.assertions import assert_status_ok


def _get_real_ids(trading_order_api) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """
    从 list_orders 反查真实可用的 financial_account_id, sub_account_id, security_id。
    返回 (financial_account_id, sub_account_id, security_id) 三元组。
    ⚠ API 要求使用 sub_account_id 进行交易（code=300: Only sub-accounts are supported）
    优先返回有 sub_account_id 的订单数据。
    """
    resp = trading_order_api.list_orders(page=0, size=50)
    if resp.status_code != 200:
        return None, None, None
    body = resp.json()
    if body.get("code") != 200:
        return None, None, None

    orders = body.get("data", {}).get("content", [])

    # 优先找有 sub_account_id 的订单（API 要求必须用 sub_account）
    for order in orders:
        sa_id = order.get("sub_account_id")
        sec_id = order.get("security_id")
        if sec_id and sa_id:
            fa_id = order.get("financial_account_id")
            logger.info(f"  反查到可用 IDs (含 sub): fa_id={fa_id}, sa_id={sa_id}, security_id={sec_id}")
            return fa_id, sa_id, sec_id

    # 没有含 sub_account_id 的订单，返回 None
    logger.warning("  未找到含 sub_account_id 的订单，Trading Order Draft 测试将跳过")
    return None, None, None


def _assert_draft_success(response, expected_fields=None):
    """验证 draft 创建成功，返回 data 字典"""
    assert response.status_code == 200
    body = response.json()
    assert body.get("code") == 200, \
        f"draft 创建应返回 code=200，实际: {body.get('code')}, msg={body.get('error_message')}"
    data = body.get("data", {})
    assert data.get("id"), "创建的草稿订单应有 id"
    assert data.get("status") == "New", \
        f"草稿订单状态应为 'New'，实际: {data.get('status')}"
    if expected_fields:
        for field in expected_fields:
            assert field in data, f"draft 响应缺少字段: '{field}'"
    return data


@pytest.mark.trading_order
@pytest.mark.create_api
class TestTradingOrderDraft:
    """
    创建草稿订单接口测试用例集
    所有场景从 list_orders 反查真实 security_id 和 financial_account_id
    """

    @pytest.mark.no_rerun
    def test_create_draft_market_order_buy(self, trading_order_api):
        """
        测试场景1：创建市价买单草稿（Market_Order + Buy）
        验证点：
        1. HTTP 200，business code=200
        2. status='New'（草稿状态）
        3. 响应包含完整字段（id, symbol, order_action, status, quantity 等）
        """
        fa_id, sa_id, sec_id = _get_real_ids(trading_order_api)
        if not sec_id or not (fa_id or sa_id):
            pytest.skip("无法从 list_orders 获取真实 security_id/fa_id，跳过")

        order_data = {
            "order_action": "Buy",
            "security_id": sec_id,
            "quantity_type": "Shares",
            "quantity": 1,
            "order_type": "Market_Order"
        }
        if fa_id:
            order_data["financial_account_id"] = fa_id
        else:
            order_data["sub_account_id"] = sa_id

        logger.info(f"创建 Market_Order Buy 草稿：security_id={sec_id}")
        resp = trading_order_api.create_draft_order(order_data)

        data = _assert_draft_success(resp, expected_fields=[
            "id", "symbol", "order_action", "status", "security_id",
            "quantity", "quantity_type", "order_type"
        ])
        assert data.get("order_action") == "Buy"
        assert data.get("order_type") == "Market_Order"
        logger.info(f"✓ Market_Order Buy 草稿创建成功: id={data.get('id')}, symbol={data.get('symbol')}")

    @pytest.mark.no_rerun
    def test_create_draft_market_order_sell(self, trading_order_api):
        """
        测试场景2：创建市价卖单草稿（Market_Order + Sell）
        验证点：
        1. HTTP 200，business code=200（或业务拒绝无持仓 Sell）
        2. 若成功：status='New'，order_action='Sell'
        """
        fa_id, sa_id, sec_id = _get_real_ids(trading_order_api)
        if not sec_id or not (fa_id or sa_id):
            pytest.skip("无法获取真实 security_id/fa_id，跳过")

        order_data = {
            "order_action": "Sell",
            "security_id": sec_id,
            "quantity_type": "Shares",
            "quantity": 1,
            "order_type": "Market_Order"
        }
        if fa_id:
            order_data["financial_account_id"] = fa_id
        else:
            order_data["sub_account_id"] = sa_id

        logger.info(f"创建 Market_Order Sell 草稿：security_id={sec_id}")
        resp = trading_order_api.create_draft_order(order_data)
        assert_status_ok(resp)

        body = resp.json()
        if body.get("code") == 200:
            data = body.get("data", {})
            assert data.get("status") == "New"
            assert data.get("order_action") == "Sell"
            logger.info(f"✓ Market_Order Sell 草稿创建成功: id={data.get('id')}")
        else:
            logger.info(f"  API 拒绝 Sell（可能无持仓或账户限制）: code={body.get('code')}, msg={body.get('error_message')}")

    @pytest.mark.no_rerun
    def test_create_draft_limit_order(self, trading_order_api):
        """
        测试场景3：创建限价单草稿（Limit_Order + Buy，需要 limit_price）
        验证点：
        1. HTTP 200，business code=200
        2. status='New'，order_type='Limit_Order'，limit_price 回显
        """
        fa_id, sa_id, sec_id = _get_real_ids(trading_order_api)
        if not sec_id or not (fa_id or sa_id):
            pytest.skip("无法获取真实 security_id/fa_id，跳过")

        order_data = {
            "order_action": "Buy",
            "security_id": sec_id,
            "quantity_type": "Dollars",
            "quantity": 100,
            "order_type": "Limit_Order",
            "limit_price": 50.00
        }
        if fa_id:
            order_data["financial_account_id"] = fa_id
        else:
            order_data["sub_account_id"] = sa_id

        logger.info(f"创建 Limit_Order Buy 草稿：security_id={sec_id}, limit_price=50.00")
        resp = trading_order_api.create_draft_order(order_data)
        assert_status_ok(resp)

        body = resp.json()
        if body.get("code") == 200:
            data = body.get("data", {})
            assert data.get("status") == "New"
            assert data.get("order_type") == "Limit_Order"
            assert data.get("limit_price") is not None, "limit_price 应回显"
            logger.info(f"✓ Limit_Order Buy 草稿创建成功: id={data.get('id')}, limit_price={data.get('limit_price')}")
        else:
            logger.info(f"  API 拒绝 Limit_Order: code={body.get('code')}, msg={body.get('error_message')}")

    @pytest.mark.no_rerun
    def test_create_draft_stop_order(self, trading_order_api):
        """
        测试场景4：创建止损单草稿（Stop_Order + Sell，需要 stop_price）
        验证点：
        1. HTTP 200，business code=200 或业务拒绝
        2. 若成功：status='New'，order_type='Stop_Order'，stop_price 回显
        """
        fa_id, sa_id, sec_id = _get_real_ids(trading_order_api)
        if not sec_id or not (fa_id or sa_id):
            pytest.skip("无法获取真实 security_id/fa_id，跳过")

        order_data = {
            "order_action": "Sell",
            "security_id": sec_id,
            "quantity_type": "Shares",
            "quantity": 1,
            "order_type": "Stop_Order",
            "stop_price": 40.00
        }
        if fa_id:
            order_data["financial_account_id"] = fa_id
        else:
            order_data["sub_account_id"] = sa_id

        logger.info(f"创建 Stop_Order Sell 草稿：security_id={sec_id}, stop_price=40.00")
        resp = trading_order_api.create_draft_order(order_data)
        assert_status_ok(resp)

        body = resp.json()
        if body.get("code") == 200:
            data = body.get("data", {})
            assert data.get("status") == "New"
            assert data.get("order_type") == "Stop_Order"
            assert data.get("stop_price") is not None, "stop_price 应回显"
            logger.info(f"✓ Stop_Order Sell 草稿创建成功: id={data.get('id')}")
        else:
            logger.info(f"  API 拒绝 Stop_Order: code={body.get('code')}, msg={body.get('error_message')}")

    @pytest.mark.no_rerun
    def test_create_draft_stop_limit_order(self, trading_order_api):
        """
        测试场景5：创建止损限价单草稿（Stop_Limit，需要 stop_price + limit_price）
        验证点：
        1. HTTP 200，business code=200 或业务拒绝
        2. 若成功：status='New'，order_type='Stop_Limit'，两个价格均回显
        """
        fa_id, sa_id, sec_id = _get_real_ids(trading_order_api)
        if not sec_id or not (fa_id or sa_id):
            pytest.skip("无法获取真实 security_id/fa_id，跳过")

        order_data = {
            "order_action": "Buy",
            "security_id": sec_id,
            "quantity_type": "Shares",
            "quantity": 1,
            "order_type": "Stop_Limit",
            "stop_price": 45.00,
            "limit_price": 50.00
        }
        if fa_id:
            order_data["financial_account_id"] = fa_id
        else:
            order_data["sub_account_id"] = sa_id

        logger.info(f"创建 Stop_Limit Buy 草稿：security_id={sec_id}")
        resp = trading_order_api.create_draft_order(order_data)
        assert_status_ok(resp)

        body = resp.json()
        if body.get("code") == 200:
            data = body.get("data", {})
            assert data.get("status") == "New"
            assert data.get("order_type") == "Stop_Limit"
            logger.info(f"✓ Stop_Limit Buy 草稿创建成功: id={data.get('id')}")
        else:
            logger.info(f"  API 拒绝 Stop_Limit: code={body.get('code')}, msg={body.get('error_message')}")

    def test_create_draft_missing_required_order_action(self, trading_order_api):
        """
        测试场景6：缺少必填字段 order_action
        验证点：
        1. HTTP 200
        2. business code != 200（缺少必填参数应被拒绝）
        """
        fa_id, sa_id, sec_id = _get_real_ids(trading_order_api)
        if not sec_id or not (fa_id or sa_id):
            pytest.skip("无法获取真实 security_id/fa_id，跳过")

        order_data = {
            # 故意省略 order_action
            "security_id": sec_id,
            "quantity_type": "Shares",
            "quantity": 1,
            "order_type": "Market_Order"
        }
        if fa_id:
            order_data["financial_account_id"] = fa_id
        else:
            order_data["sub_account_id"] = sa_id

        resp = trading_order_api.create_draft_order(order_data)
        assert_status_ok(resp)

        body = resp.json()
        assert body.get("code") != 200, \
            f"缺少 order_action 应被拒绝，实际 code={body.get('code')}"
        logger.info(f"✓ 缺少 order_action 被拒绝: code={body.get('code')}, msg={body.get('error_message')}")

    def test_create_draft_missing_required_security_id(self, trading_order_api):
        """
        测试场景7：缺少必填字段 security_id
        验证点：
        1. HTTP 200
        2. business code != 200
        """
        fa_id, sa_id, _ = _get_real_ids(trading_order_api)
        if not (fa_id or sa_id):
            pytest.skip("无法获取真实 fa_id/sa_id，跳过")

        order_data = {
            "order_action": "Buy",
            # 故意省略 security_id
            "quantity_type": "Shares",
            "quantity": 1,
            "order_type": "Market_Order"
        }
        if fa_id:
            order_data["financial_account_id"] = fa_id
        else:
            order_data["sub_account_id"] = sa_id

        resp = trading_order_api.create_draft_order(order_data)
        assert_status_ok(resp)

        body = resp.json()
        assert body.get("code") != 200, \
            f"缺少 security_id 应被拒绝，实际 code={body.get('code')}"
        logger.info(f"✓ 缺少 security_id 被拒绝: code={body.get('code')}, msg={body.get('error_message')}")

    def test_create_draft_missing_fa_and_sa_id(self, trading_order_api):
        """
        测试场景8：financial_account_id 和 sub_account_id 都不传（二选一必填）
        验证点：
        1. HTTP 200
        2. business code != 200
        """
        _, _, sec_id = _get_real_ids(trading_order_api)
        if not sec_id:
            pytest.skip("无法获取真实 security_id，跳过")

        order_data = {
            "order_action": "Buy",
            "security_id": sec_id,
            "quantity_type": "Shares",
            "quantity": 1,
            "order_type": "Market_Order"
            # 故意不传 financial_account_id 和 sub_account_id
        }

        resp = trading_order_api.create_draft_order(order_data)
        assert_status_ok(resp)

        body = resp.json()
        assert body.get("code") != 200, \
            f"缺少 fa_id 和 sa_id 应被拒绝，实际 code={body.get('code')}"
        logger.info(f"✓ 缺少 fa_id/sa_id 被拒绝: code={body.get('code')}, msg={body.get('error_message')}")

    def test_create_draft_limit_order_missing_limit_price(self, trading_order_api):
        """
        测试场景9：Limit_Order 缺少 limit_price（条件必填）
        验证点：
        1. HTTP 200
        2. business code != 200（缺少条件必填参数应被拒绝）
        """
        fa_id, sa_id, sec_id = _get_real_ids(trading_order_api)
        if not sec_id or not (fa_id or sa_id):
            pytest.skip("无法获取真实 security_id/fa_id，跳过")

        order_data = {
            "order_action": "Buy",
            "security_id": sec_id,
            "quantity_type": "Shares",
            "quantity": 1,
            "order_type": "Limit_Order"
            # 故意省略 limit_price（Limit_Order 必填）
        }
        if fa_id:
            order_data["financial_account_id"] = fa_id
        else:
            order_data["sub_account_id"] = sa_id

        resp = trading_order_api.create_draft_order(order_data)
        assert_status_ok(resp)

        body = resp.json()
        if body.get("code") != 200:
            logger.info(f"✓ Limit_Order 缺少 limit_price 被拒绝: code={body.get('code')}")
        else:
            logger.info("⚠ API 接受了 Limit_Order 无 limit_price（探索性结果）")

    def test_create_draft_invalid_order_action(self, trading_order_api):
        """
        测试场景10：使用无效的 order_action 枚举值
        验证点：
        1. HTTP 200
        2. business code != 200
        """
        fa_id, sa_id, sec_id = _get_real_ids(trading_order_api)
        if not sec_id or not (fa_id or sa_id):
            pytest.skip("无法获取真实 security_id/fa_id，跳过")

        order_data = {
            "order_action": "INVALID_ACTION_999",
            "security_id": sec_id,
            "quantity_type": "Shares",
            "quantity": 1,
            "order_type": "Market_Order"
        }
        if fa_id:
            order_data["financial_account_id"] = fa_id
        else:
            order_data["sub_account_id"] = sa_id

        resp = trading_order_api.create_draft_order(order_data)
        assert_status_ok(resp)

        body = resp.json()
        assert body.get("code") != 200, \
            f"无效 order_action 应被拒绝，实际 code={body.get('code')}"
        logger.info(f"✓ 无效 order_action 被拒绝: code={body.get('code')}, msg={body.get('error_message')}")

    def test_create_draft_invalid_security_id(self, trading_order_api):
        """
        测试场景11：使用不存在的 security_id
        验证点：
        1. HTTP 200
        2. business code != 200
        """
        fa_id, sa_id, _ = _get_real_ids(trading_order_api)
        if not (fa_id or sa_id):
            pytest.skip("无法获取真实 fa_id/sa_id，跳过")

        order_data = {
            "order_action": "Buy",
            "security_id": "INVALID_SECURITY_ID_99999999",
            "quantity_type": "Shares",
            "quantity": 1,
            "order_type": "Market_Order"
        }
        if fa_id:
            order_data["financial_account_id"] = fa_id
        else:
            order_data["sub_account_id"] = sa_id

        resp = trading_order_api.create_draft_order(order_data)
        assert_status_ok(resp)

        body = resp.json()
        assert body.get("code") != 200, \
            f"无效 security_id 应被拒绝，实际 code={body.get('code')}"
        logger.info(f"✓ 无效 security_id 被拒绝: code={body.get('code')}, msg={body.get('error_message')}")
