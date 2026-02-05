"""
Trading Order - Submit Order 接口测试用例
测试 POST /api/v1/cores/{core}/trading-orders/{order_id}/submit 接口
"""
import pytest
from utils.logger import logger
from utils.assertions import assert_status_ok


@pytest.mark.trading_order
@pytest.mark.update_api
class TestTradingOrderSubmit:
    """
    提交草稿订单接口测试用例集
    ⚠️ 注意：只能提交status=New的草稿订单
    """

    @pytest.mark.skip(reason="需要真实的草稿订单ID，待完善数据准备")
    def test_submit_draft_order_success(self, trading_order_api):
        """
        测试场景1：成功提交草稿订单
        验证点：
        1. 接口返回 200
        2. 订单状态从 New 变为 Pending/In_Progress
        """
        logger.info("测试场景1：成功提交草稿订单")
        
        # 步骤1：先创建一个草稿订单
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
        
        assert draft_order.get("status") == "New", "草稿订单初始状态应为New"
        
        # 步骤2：提交草稿订单
        submit_response = trading_order_api.submit_order(order_id)
        assert_status_ok(submit_response)
        
        submit_body = submit_response.json()
        submitted_order = submit_body.get("data", submit_body)
        
        # 验证状态变化
        assert submitted_order.get("status") in ["Pending", "In_Progress"], \
            "提交后订单状态应变为Pending或In_Progress"
        
        logger.info(f"✓ 订单提交成功，状态: {draft_order['status']} → {submitted_order['status']}")

    def test_submit_invalid_order_id(self, trading_order_api):
        """
        测试场景2：提交不存在的订单ID
        验证点：
        1. 接口返回错误
        2. code为404或其他错误码
        """
        logger.info("测试场景2：提交不存在的订单ID")
        
        invalid_order_id = "INVALID_ORDER_ID_999"
        
        response = trading_order_api.submit_order(invalid_order_id)
        
        assert response.status_code == 200, "HTTP状态码应为200"
        response_body = response.json()
        assert response_body.get("code") != 200, "业务code应不为200"
        
        logger.info(f"✓ 正确拒绝无效的订单ID: {response_body.get('error_message', 'Unknown error')}")

    @pytest.mark.skip(reason="需要真实的已提交订单ID")
    def test_submit_already_submitted_order(self, trading_order_api):
        """
        测试场景3：提交已经提交过的订单
        验证点：
        1. 接口返回错误
        2. 提示订单状态不允许重复提交
        """
        logger.info("测试场景3：重复提交订单")
        
        # 需要一个已经提交的订单ID
        already_submitted_order_id = "test_submitted_order_id"
        
        response = trading_order_api.submit_order(already_submitted_order_id)
        
        assert response.status_code == 200
        response_body = response.json()
        assert response_body.get("code") != 200
        
        logger.info(f"✓ 正确拒绝重复提交: {response_body.get('error_message', 'Unknown error')}")

    @pytest.mark.skip(reason="需要真实的Cancelled订单ID")
    def test_submit_cancelled_order(self, trading_order_api):
        """
        测试场景4：提交已取消的订单
        验证点：
        1. 接口返回错误
        2. 提示订单已取消
        """
        logger.info("测试场景4：提交已取消的订单")
        
        # 需要一个已取消的订单ID
        cancelled_order_id = "test_cancelled_order_id"
        
        response = trading_order_api.submit_order(cancelled_order_id)
        
        assert response.status_code == 200
        response_body = response.json()
        assert response_body.get("code") != 200
        
        logger.info(f"✓ 正确拒绝已取消订单的提交: {response_body.get('error_message', 'Unknown error')}")
