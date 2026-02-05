"""
Remote Deposit Check - Transaction Fee 接口测试用例
测试 POST /api/v1/cores/{core}/money-movements/checks/fee 接口
"""
import pytest
from utils.logger import logger
from utils.assertions import assert_status_ok


@pytest.mark.remote_deposit_check
@pytest.mark.detail_api
class TestCheckFee:
    """Check费用计算测试"""

    @pytest.mark.skip(reason="需要真实financial_account_id")
    def test_quote_check_fee_success(self, remote_deposit_check_api):
        """测试场景1：成功计算Check费用"""
        logger.info("测试场景1：成功计算Check费用")
        
        response = remote_deposit_check_api.quote_transaction_fee(
            financial_account_id="test_fa_id",
            amount="100.00"
        )
        
        assert_status_ok(response)
        data = response.json().get("data", {})
        assert "fee" in data
        logger.info(f"✓ 费用计算成功，fee: {data.get('fee')}")

    def test_http_method_error(self, remote_deposit_check_api):
        """测试场景2：HTTP方法示例错误"""
        logger.info("测试场景2：HTTP方法示例错误")
        
        logger.warning("⚠️ 文档问题：HTTP方法示例错误")
        logger.warning("标题：POST /checks/fee")
        logger.warning("示例：GET /checks/fee")
        logger.info("✓ HTTP方法错误已记录")
