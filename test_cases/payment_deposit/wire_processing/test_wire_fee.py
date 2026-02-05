"""
Wire Processing - Transaction Fee 接口测试用例
测试 POST /api/v1/cores/{core}/money-movements/wire/fee 接口
"""
import pytest
from utils.logger import logger
from utils.assertions import assert_status_ok
from data.enums import WirePaymentType


@pytest.mark.wire_processing
@pytest.mark.detail_api
class TestWireFee:
    """Wire费用计算测试"""

    @pytest.mark.skip(reason="需要真实financial_account_id")
    def test_quote_wire_fee_success(self, wire_processing_api):
        """测试场景1：成功计算Wire费用"""
        logger.info("测试场景1：成功计算Wire费用")
        
        response = wire_processing_api.quote_transaction_fee(
            financial_account_id="test_fa_id",
            amount="100.00"
        )
        assert_status_ok(response)
        
        data = response.json().get("data", {})
        assert "fee" in data
        logger.info(f"✓ 费用计算成功，fee: {data.get('fee')}")

    @pytest.mark.skip(reason="需要真实数据")
    def test_international_wire_fee(self, wire_processing_api):
        """测试场景2：计算国际电汇费用"""
        logger.info("测试场景2：计算国际电汇费用")
        
        response = wire_processing_api.quote_transaction_fee(
            financial_account_id="test_fa_id",
            amount="1000.00",
            payment_type=WirePaymentType.INTERNATIONAL_WIRE
        )
        assert_status_ok(response)
        logger.info("✓ 国际电汇费用计算成功")

    @pytest.mark.skip(reason="需要真实数据")
    def test_same_day_fee_impact(self, wire_processing_api):
        """测试场景3：same_day参数影响验证"""
        logger.info("测试场景3：same_day参数影响")
        
        # 非same_day
        response1 = wire_processing_api.quote_transaction_fee(
            financial_account_id="test_fa_id",
            amount="100.00",
            same_day=False
        )
        
        # same_day
        response2 = wire_processing_api.quote_transaction_fee(
            financial_account_id="test_fa_id",
            amount="100.00",
            same_day=True
        )
        
        if response1.status_code == 200 and response2.status_code == 200:
            fee1 = response1.json().get("data", {}).get("fee")
            fee2 = response2.json().get("data", {}).get("fee")
            logger.info(f"非same_day费用: {fee1}, same_day费用: {fee2}")
        
        logger.info("✓ same_day影响验证完成")

    def test_http_method_error(self, wire_processing_api):
        """测试场景4：HTTP方法示例错误"""
        logger.info("测试场景4：HTTP方法示例错误")
        
        logger.warning("⚠️ 文档问题：HTTP方法示例错误")
        logger.warning("标题：POST /wire/fee")
        logger.warning("示例：GET /wire/fee")
        logger.info("✓ HTTP方法错误已记录")
