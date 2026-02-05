"""
Trading Order - Cancel Order 接口测试用例
测试 POST /api/v1/cores/{core}/trading-orders/{order_id}/cancel 接口
"""
import pytest
from utils.logger import logger
from utils.assertions import assert_status_ok


@pytest.mark.trading_order
@pytest.mark.delete_api
@pytest.mark.no_rerun
class TestTradingOrderCancel:
    """
    取消订单接口测试用例集
    ⚠️ 重要限制：
    - 可以取消 pending 或 overnight 订单
    - 推测：New, Pending, Overnight 状态可取消
    - 已成交（Filled, Posted）不可取消
    
    ⚠️ 破坏性操作：取消订单是不可逆的，大部分测试标记为skip
    """

    @pytest.mark.skip(reason="破坏性操作，需要真实订单，待完善数据准备")
    def test_cancel_draft_order_success(self, trading_order_api):
        """
        测试场景1：取消草稿订单
        验证点：
        1. 接口返回 200
        2. 订单状态变为 Cancelled
        """
        logger.info("测试场景1：取消草稿订单")
        
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
        order_id = draft_body.get("data", draft_body).get("id")
        
        # 步骤2：取消订单
        cancel_response = trading_order_api.cancel_order(order_id)
        assert_status_ok(cancel_response)
        
        cancel_body = cancel_response.json()
        cancelled_order = cancel_body.get("data", cancel_body)
        
        assert cancelled_order.get("status") == "Cancelled", "订单状态应变为Cancelled"
        
        logger.info(f"✓ 订单取消成功，ID: {order_id}")

    @pytest.mark.skip(reason="破坏性操作，需要真实的Pending订单")
    def test_cancel_pending_order_success(self, trading_order_api):
        """
        测试场景2：取消Pending状态的订单
        验证点：
        1. 接口返回 200
        2. 订单状态变为 Cancelled
        """
        logger.info("测试场景2：取消Pending订单")
        
        # 需要一个Pending状态的订单ID
        pending_order_id = "test_pending_order_id"
        
        response = trading_order_api.cancel_order(pending_order_id)
        assert_status_ok(response)
        
        response_body = response.json()
        cancelled_order = response_body.get("data", response_body)
        
        assert cancelled_order.get("status") == "Cancelled"
        
        logger.info(f"✓ Pending订单取消成功")

    def test_cancel_invalid_order_id(self, trading_order_api):
        """
        测试场景3：取消不存在的订单ID
        验证点：
        1. 接口返回错误
        2. code为404或其他错误码
        """
        logger.info("测试场景3：取消不存在的订单ID")
        
        invalid_order_id = "INVALID_ORDER_ID_999"
        
        response = trading_order_api.cancel_order(invalid_order_id)
        
        assert response.status_code == 200, "HTTP状态码应为200"
        response_body = response.json()
        assert response_body.get("code") != 200, "业务code应不为200"
        
        logger.info(f"✓ 正确拒绝无效的订单ID: {response_body.get('error_message', 'Unknown error')}")

    @pytest.mark.skip(reason="需要真实的Filled订单ID")
    def test_cancel_filled_order(self, trading_order_api):
        """
        测试场景4：尝试取消已成交的订单
        验证点：
        1. 接口返回错误
        2. 提示订单已成交，无法取消
        """
        logger.info("测试场景4：尝试取消已成交订单")
        
        # 需要一个已成交的订单ID（status=Filled）
        filled_order_id = "test_filled_order_id"
        
        response = trading_order_api.cancel_order(filled_order_id)
        
        assert response.status_code == 200
        response_body = response.json()
        assert response_body.get("code") != 200
        
        error_message = response_body.get("error_message", "")
        logger.info(f"✓ 正确拒绝取消已成交订单: {error_message}")

    @pytest.mark.skip(reason="需要真实的Posted订单ID")
    def test_cancel_posted_order(self, trading_order_api):
        """
        测试场景5：尝试取消已入账的订单
        验证点：
        1. 接口返回错误
        2. 提示订单已入账，无法取消
        """
        logger.info("测试场景5：尝试取消已入账订单")
        
        # 需要一个已入账的订单ID（status=Posted）
        posted_order_id = "test_posted_order_id"
        
        response = trading_order_api.cancel_order(posted_order_id)
        
        assert response.status_code == 200
        response_body = response.json()
        assert response_body.get("code") != 200
        
        logger.info(f"✓ 正确拒绝取消已入账订单: {response_body.get('error_message', 'Unknown error')}")

    @pytest.mark.skip(reason="需要真实的Cancelled订单ID")
    def test_cancel_already_cancelled_order(self, trading_order_api):
        """
        测试场景6：尝试重复取消订单
        验证点：
        1. 接口返回错误或幂等成功
        2. 订单状态保持 Cancelled
        """
        logger.info("测试场景6：重复取消订单")
        
        # 需要一个已取消的订单ID
        cancelled_order_id = "test_cancelled_order_id"
        
        response = trading_order_api.cancel_order(cancelled_order_id)
        
        assert response.status_code == 200
        response_body = response.json()
        
        # 可能返回错误，也可能幂等成功
        if response_body.get("code") == 200:
            logger.info("✓ 重复取消幂等成功")
        else:
            logger.info(f"✓ 正确拒绝重复取消: {response_body.get('error_message', 'Unknown error')}")
