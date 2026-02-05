"""
Trading Order - Create Draft Order 接口测试用例
测试 POST /api/v1/cores/{core}/trading-orders/draft 接口
"""
import pytest
from utils.logger import logger
from utils.assertions import assert_status_ok


@pytest.mark.trading_order
@pytest.mark.create_api
@pytest.mark.skip(reason="需要真实的financial_account_id和security_id，待完善数据准备")
class TestTradingOrderDraft:
    """
    创建草稿订单接口测试用例集
    """

    def test_create_draft_order_market(self, trading_order_api):
        """
        测试场景1：创建市价单草稿
        """
        logger.info("测试场景1：创建市价单草稿")
        
        order_data = {
            "financial_account_id": "test_fa_id",
            "order_action": "Buy",
            "security_id": "test_security_id",
            "quantity_type": "Shares",
            "quantity": 10,
            "order_type": "Market_Order"
        }
        
        response = trading_order_api.create_draft_order(order_data)
        assert_status_ok(response)
        
        logger.info("✓ 草稿订单创建成功")
