"""
Trading Order - Initiate Order 接口测试用例
测试 POST /api/v1/cores/{core}/trading-orders 接口
"""
import pytest
from utils.logger import logger
from utils.assertions import assert_status_ok


@pytest.mark.trading_order
@pytest.mark.create_api
class TestTradingOrderInitiate:
    """
    直接发起订单接口测试用例集
    ⚠️ 注意：Initiate vs Draft
    - Draft: 创建草稿，status=New，需要手动Submit
    - Initiate: 直接提交到市场，status=In_Progress
    """

    @pytest.mark.skip(reason="需要真实的financial_account_id和security_id，待完善数据准备")
    def test_initiate_market_order_success(self, trading_order_api):
        """
        测试场景1：直接发起市价单
        验证点：
        1. 接口返回 200
        2. 订单状态为 In_Progress（区别于Draft的New）
        3. 返回订单ID
        """
        logger.info("测试场景1：直接发起市价单")
        
        order_data = {
            "financial_account_id": "test_fa_id",
            "order_action": "Buy",
            "security_id": "test_security_id",
            "quantity_type": "Shares",
            "quantity": 10,
            "order_type": "Market_Order"
        }
        
        response = trading_order_api.initiate_order(order_data)
        assert_status_ok(response)
        
        response_body = response.json()
        order_data = response_body.get("data", response_body)
        
        assert order_data.get("id") is not None, "订单ID不应为空"
        assert order_data.get("status") == "In_Progress", "Initiate订单应为In_Progress状态"
        
        logger.info(f"✓ 订单直接发起成功，ID: {order_data['id']}, Status: {order_data['status']}")

    @pytest.mark.skip(reason="需要真实数据")
    def test_initiate_limit_order_success(self, trading_order_api):
        """
        测试场景2：直接发起限价单
        验证点：
        1. 接口返回 200
        2. limit_price正确保存
        """
        logger.info("测试场景2：直接发起限价单")
        
        order_data = {
            "financial_account_id": "test_fa_id",
            "order_action": "Buy",
            "security_id": "test_security_id",
            "quantity_type": "Shares",
            "quantity": 10,
            "order_type": "Limit_Order",
            "limit_price": 100.50
        }
        
        response = trading_order_api.initiate_order(order_data)
        assert_status_ok(response)
        
        response_body = response.json()
        order_data_resp = response_body.get("data", response_body)
        
        assert order_data_resp.get("order_type") == "Limit_Order"
        assert order_data_resp.get("limit_price") == 100.50
        
        logger.info("✓ 限价单发起成功")

    @pytest.mark.skip(reason="需要真实数据")
    def test_initiate_stop_limit_order_success(self, trading_order_api):
        """
        测试场景3：直接发起止损限价单
        验证点：
        1. 接口返回 200
        2. stop_price和limit_price都正确保存
        """
        logger.info("测试场景3：直接发起止损限价单")
        
        order_data = {
            "financial_account_id": "test_fa_id",
            "order_action": "Sell",
            "security_id": "test_security_id",
            "quantity_type": "Shares",
            "quantity": 5,
            "order_type": "Stop_Limit",
            "stop_price": 95.00,
            "limit_price": 90.00
        }
        
        response = trading_order_api.initiate_order(order_data)
        assert_status_ok(response)
        
        response_body = response.json()
        order_data_resp = response_body.get("data", response_body)
        
        assert order_data_resp.get("order_type") == "Stop_Limit"
        assert order_data_resp.get("stop_price") == 95.00
        assert order_data_resp.get("limit_price") == 90.00
        
        logger.info("✓ 止损限价单发起成功")

    def test_initiate_order_missing_required_field(self, trading_order_api):
        """
        测试场景4：缺少必需字段
        验证点：
        1. 接口返回错误
        2. code不为200
        """
        logger.info("测试场景4：缺少必需字段")
        
        order_data = {
            "financial_account_id": "test_fa_id",
            "order_action": "Buy"
            # 缺少 security_id, quantity_type, quantity, order_type
        }
        
        response = trading_order_api.initiate_order(order_data)
        
        assert response.status_code == 200, "HTTP状态码应为200"
        response_body = response.json()
        assert response_body.get("code") != 200, "业务code应不为200"
        
        logger.info(f"✓ 正确拒绝缺少必需字段的请求: {response_body.get('error_message', 'Unknown error')}")

    def test_initiate_order_invalid_order_type(self, trading_order_api):
        """
        测试场景5：无效的order_type
        验证点：
        1. 接口返回错误
        """
        logger.info("测试场景5：无效的order_type")
        
        order_data = {
            "financial_account_id": "test_fa_id",
            "order_action": "Buy",
            "security_id": "test_security_id",
            "quantity_type": "Shares",
            "quantity": 10,
            "order_type": "Invalid_Order_Type"
        }
        
        response = trading_order_api.initiate_order(order_data)
        
        assert response.status_code == 200
        response_body = response.json()
        assert response_body.get("code") != 200
        
        logger.info(f"✓ 正确拒绝无效的order_type: {response_body.get('error_message', 'Unknown error')}")

    def test_initiate_limit_order_without_limit_price(self, trading_order_api):
        """
        测试场景6：限价单缺少limit_price
        验证点：
        1. 接口返回错误
        2. 提示缺少limit_price
        """
        logger.info("测试场景6：限价单缺少limit_price")
        
        order_data = {
            "financial_account_id": "test_fa_id",
            "order_action": "Buy",
            "security_id": "test_security_id",
            "quantity_type": "Shares",
            "quantity": 10,
            "order_type": "Limit_Order"
            # 缺少 limit_price
        }
        
        response = trading_order_api.initiate_order(order_data)
        
        assert response.status_code == 200
        response_body = response.json()
        assert response_body.get("code") != 200
        
        logger.info(f"✓ 正确拒绝缺少limit_price的限价单: {response_body.get('error_message', 'Unknown error')}")
