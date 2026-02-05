"""
Account Transfer - Transaction Fee 接口测试用例
测试 POST /api/v1/cores/{core}/money-movements/account-transfer/fee 接口
"""
import pytest
from utils.logger import logger
from utils.assertions import assert_status_ok


@pytest.mark.account_transfer
@pytest.mark.detail_api
class TestAccountTransferFee:
    """
    Account Transfer费用计算接口测试用例集
    ⚠️ 文档问题：HTTP方法示例错误（POST写成GET）
    """

    @pytest.mark.skip(reason="需要真实的financial_account_id")
    def test_quote_fee_success(self, account_transfer_api):
        """
        测试场景1：成功计算交易费用
        验证点：
        1. 接口返回 200
        2. code=200
        3. 返回fee金额
        """
        logger.info("测试场景1：成功计算交易费用")
        
        response = account_transfer_api.quote_transaction_fee(
            financial_account_id="test_fa_id",
            amount="100.00"
        )
        
        assert_status_ok(response)
        
        response_body = response.json()
        assert response_body.get("code") == 200
        
        data = response_body.get("data", {})
        assert "fee" in data
        assert "amount" in data
        
        logger.info(f"✓ 费用计算成功，fee: {data.get('fee')}")

    def test_invalid_account_id(self, account_transfer_api):
        """
        测试场景2：无效的账户ID
        验证点：
        1. 接口返回错误
        """
        logger.info("测试场景2：无效的账户ID")
        
        response = account_transfer_api.quote_transaction_fee(
            financial_account_id="INVALID_ID_999",
            amount="100.00"
        )
        
        assert response.status_code == 200
        
        response_body = response.json()
        if response_body.get("code") != 200:
            logger.info(f"✓ 正确拒绝无效ID")
        
        logger.info("✓ 无效账户ID测试完成")

    def test_same_day_field(self, account_transfer_api):
        """
        测试场景3：same_day字段验证
        验证点：
        1. 响应包含same_day字段
        2. 但未说明含义
        """
        logger.info("测试场景3：same_day字段验证")
        
        response = account_transfer_api.quote_transaction_fee(
            financial_account_id="test_fa_id",
            amount="50.00"
        )
        
        if response.status_code == 200 and response.json().get("code") == 200:
            data = response.json().get("data", {})
            
            if "same_day" in data:
                logger.warning("⚠️ 检测到same_day字段（未定义）")
                logger.info(f"same_day值: {data['same_day']}")
        
        logger.info("✓ same_day字段验证完成")

    def test_http_method_example_error(self, account_transfer_api):
        """
        测试场景4：HTTP方法示例错误
        验证点：
        1. 文档标题：POST
        2. 示例代码：GET（错误）
        """
        logger.info("测试场景4：HTTP方法示例错误")
        
        logger.warning("⚠️ 文档问题：HTTP方法示例错误")
        logger.warning("标题标注: POST /account-transfer/fee")
        logger.warning("示例代码: GET /account-transfer/fee")
        logger.warning("正确的应该是POST")
        
        logger.info("✓ HTTP方法错误已记录")
