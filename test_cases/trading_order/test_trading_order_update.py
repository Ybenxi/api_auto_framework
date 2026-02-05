"""
Trading Order - Update Order 接口测试用例
测试 PATCH /api/v1/cores/{core}/trading-orders/{order_id} 接口
"""
import pytest
from utils.logger import logger
from utils.assertions import assert_status_ok


@pytest.mark.trading_order
@pytest.mark.update_api
class TestTradingOrderUpdate:
    """
    更新订单接口测试用例集
    ⚠️ 重要限制：Only draft orders can be updated
    - 只能更新 status=New 的草稿订单
    - 已提交的订单无法更新
    """

    @pytest.mark.skip(reason="需要真实的草稿订单ID，待完善数据准备")
    def test_update_draft_order_quantity(self, trading_order_api):
        """
        测试场景1：更新草稿订单的数量
        验证点：
        1. 接口返回 200
        2. 数量更新成功
        3. 其他字段保持不变
        """
        logger.info("测试场景1：更新草稿订单数量")
        
        # 步骤1：创建草稿订单
        draft_data = {
            "financial_account_id": "test_fa_id",
            "order_action": "Buy",
            "security_id": "test_security_id",
            "quantity_type": "Shares",
            "quantity": 10,
            "order_type": "Market_Order"
        }
        
        draft_response = trading_order_api.create_draft_order(draft_data)
        assert_status_ok(draft_response)
        
        draft_body = draft_response.json()
        draft_order = draft_body.get("data", draft_body)
        order_id = draft_order.get("id")
        
        # 步骤2：更新数量
        update_data = {
            "quantity": 20
        }
        
        update_response = trading_order_api.update_order(order_id, update_data)
        assert_status_ok(update_response)
        
        update_body = update_response.json()
        updated_order = update_body.get("data", update_body)
        
        assert updated_order.get("quantity") == 20, "数量应更新为20"
        assert updated_order.get("order_action") == "Buy", "order_action应保持不变"
        
        logger.info(f"✓ 订单数量更新成功: 10 → 20")

    @pytest.mark.skip(reason="需要真实数据")
    def test_update_draft_order_limit_price(self, trading_order_api):
        """
        测试场景2：更新限价单的限价
        验证点：
        1. 接口返回 200
        2. limit_price更新成功
        """
        logger.info("测试场景2：更新限价单的限价")
        
        # 步骤1：创建限价单草稿
        draft_data = {
            "financial_account_id": "test_fa_id",
            "order_action": "Buy",
            "security_id": "test_security_id",
            "quantity_type": "Shares",
            "quantity": 10,
            "order_type": "Limit_Order",
            "limit_price": 100.00
        }
        
        draft_response = trading_order_api.create_draft_order(draft_data)
        assert_status_ok(draft_response)
        
        draft_body = draft_response.json()
        order_id = draft_body.get("data", draft_body).get("id")
        
        # 步骤2：更新限价
        update_data = {
            "limit_price": 105.50
        }
        
        update_response = trading_order_api.update_order(order_id, update_data)
        assert_status_ok(update_response)
        
        update_body = update_response.json()
        updated_order = update_body.get("data", update_body)
        
        assert updated_order.get("limit_price") == 105.50, "限价应更新为105.50"
        
        logger.info(f"✓ 限价更新成功: 100.00 → 105.50")

    @pytest.mark.skip(reason="需要真实数据")
    def test_update_draft_order_multiple_fields(self, trading_order_api):
        """
        测试场景3：同时更新多个字段
        验证点：
        1. 接口返回 200
        2. 所有字段都正确更新
        """
        logger.info("测试场景3：同时更新多个字段")
        
        # 步骤1：创建草稿
        draft_data = {
            "financial_account_id": "test_fa_id",
            "order_action": "Buy",
            "security_id": "test_security_id",
            "quantity_type": "Shares",
            "quantity": 10,
            "order_type": "Market_Order"
        }
        
        draft_response = trading_order_api.create_draft_order(draft_data)
        assert_status_ok(draft_response)
        
        order_id = draft_response.json().get("data", draft_response.json()).get("id")
        
        # 步骤2：更新多个字段
        update_data = {
            "quantity": 15,
            "order_type": "Limit_Order",
            "limit_price": 110.00
        }
        
        update_response = trading_order_api.update_order(order_id, update_data)
        assert_status_ok(update_response)
        
        updated_order = update_response.json().get("data", update_response.json())
        
        assert updated_order.get("quantity") == 15
        assert updated_order.get("order_type") == "Limit_Order"
        assert updated_order.get("limit_price") == 110.00
        
        logger.info("✓ 多个字段同时更新成功")

    def test_update_invalid_order_id(self, trading_order_api):
        """
        测试场景4：更新不存在的订单ID
        验证点：
        1. 接口返回错误
        2. code为404或其他错误码
        """
        logger.info("测试场景4：更新不存在的订单ID")
        
        invalid_order_id = "INVALID_ORDER_ID_999"
        update_data = {
            "quantity": 20
        }
        
        response = trading_order_api.update_order(invalid_order_id, update_data)
        
        assert response.status_code == 200, "HTTP状态码应为200"
        response_body = response.json()
        assert response_body.get("code") != 200, "业务code应不为200"
        
        logger.info(f"✓ 正确拒绝无效的订单ID: {response_body.get('error_message', 'Unknown error')}")

    @pytest.mark.skip(reason="需要真实的已提交订单ID")
    def test_update_submitted_order(self, trading_order_api):
        """
        测试场景5：尝试更新已提交的订单
        验证点：
        1. 接口返回错误
        2. 提示 "Only draft orders can be updated"
        """
        logger.info("测试场景5：尝试更新已提交的订单")
        
        # 需要一个已提交的订单ID（status != New）
        submitted_order_id = "test_submitted_order_id"
        update_data = {
            "quantity": 30
        }
        
        response = trading_order_api.update_order(submitted_order_id, update_data)
        
        assert response.status_code == 200
        response_body = response.json()
        assert response_body.get("code") != 200
        
        error_message = response_body.get("error_message", "")
        logger.info(f"✓ 正确拒绝更新已提交订单: {error_message}")

    def test_update_order_invalid_field_value(self, trading_order_api):
        """
        测试场景6：更新为无效的字段值
        验证点：
        1. 接口返回错误
        2. 提示字段值无效
        """
        logger.info("测试场景6：更新为无效的字段值")
        
        fake_order_id = "fake_order_id"
        update_data = {
            "order_type": "Invalid_Order_Type"
        }
        
        response = trading_order_api.update_order(fake_order_id, update_data)
        
        assert response.status_code == 200
        response_body = response.json()
        assert response_body.get("code") != 200
        
        logger.info(f"✓ 正确拒绝无效字段值: {response_body.get('error_message', 'Unknown error')}")
