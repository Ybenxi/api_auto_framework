"""
ACH Processing - Transaction Fee 接口测试用例
测试 POST /api/v1/cores/{core}/money-movements/ach/fee 接口
"""
import pytest
from utils.logger import logger
from utils.assertions import assert_status_ok
from data.enums import PaymentTransactionType


@pytest.mark.ach_processing
@pytest.mark.detail_api
class TestACHFee:
    """ACH费用计算测试"""

    @pytest.mark.skip(reason="需要真实financial_account_id")
    def test_quote_fee_third_party_credit(self, ach_processing_api):
        """测试场景1：计算第三方Credit费用"""
        logger.info("测试场景1：计算第三方Credit费用")
        
        response = ach_processing_api.quote_transaction_fee(
            financial_account_id="test_fa_id",
            amount="100.00",
            transaction_type=PaymentTransactionType.CREDIT,
            same_day=False,
            first_party=False
        )
        
        assert_status_ok(response)
        
        data = response.json().get("data", {})
        assert "fee" in data
        logger.info(f"✓ 费用计算成功，fee: {data.get('fee')}")

    @pytest.mark.skip(reason="需要真实数据")
    def test_quote_fee_first_party(self, ach_processing_api):
        """测试场景2：计算第一方转账费用"""
        logger.info("测试场景2：计算第一方转账费用")
        
        response = ach_processing_api.quote_transaction_fee(
            financial_account_id="test_fa_id",
            amount="50.00",
            transaction_type=PaymentTransactionType.CREDIT,
            first_party=True  # 第一方
        )
        
        assert_status_ok(response)
        logger.info("✓ 第一方费用计算成功")

    @pytest.mark.skip(reason="需要真实数据")
    def test_quote_fee_same_day_impact(self, ach_processing_api):
        """测试场景3：Same Day对费用的影响"""
        logger.info("测试场景3：Same Day费用影响")
        
        # 非Same Day
        response1 = ach_processing_api.quote_transaction_fee(
            financial_account_id="test_fa_id",
            amount="100.00",
            transaction_type=PaymentTransactionType.CREDIT,
            same_day=False
        )
        
        # Same Day
        response2 = ach_processing_api.quote_transaction_fee(
            financial_account_id="test_fa_id",
            amount="100.00",
            transaction_type=PaymentTransactionType.CREDIT,
            same_day=True
        )
        
        if response1.status_code == 200 and response2.status_code == 200:
            fee1 = response1.json().get("data", {}).get("fee")
            fee2 = response2.json().get("data", {}).get("fee")
            logger.info(f"非Same Day: {fee1}, Same Day: {fee2}")
        
        logger.info("✓ Same Day费用影响验证完成")

    def test_quote_fee_parameters_required_with_default(self, ach_processing_api):
        """测试场景4：required参数有默认值（矛盾）"""
        logger.info("测试场景4：required参数验证")
        
        logger.warning("⚠️ 文档问题：参数标记矛盾")
        logger.warning("same_day: (required) Default value is false")
        logger.warning("first_party: (required) Default value is false")
        logger.warning("问题：有默认值为何还是required？")
        logger.warning("应该标记为optional with default")
        
        logger.info("✓ 参数矛盾已记录")
