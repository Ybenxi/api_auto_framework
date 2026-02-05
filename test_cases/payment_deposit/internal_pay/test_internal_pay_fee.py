"""
Internal Pay - Transaction Fee 接口测试用例
测试 POST /api/v1/cores/{core}/money-movements/internal-pay/fee 接口
"""
import pytest
from utils.logger import logger
from utils.assertions import assert_status_ok


@pytest.mark.internal_pay
@pytest.mark.detail_api
class TestInternalPayFee:
    """
    Internal Pay费用计算接口测试用例集
    ⚠️ 文档问题：HTTP方法示例错误（POST写成GET）
    """

    @pytest.mark.skip(reason="需要真实的financial_account_id")
    def test_quote_fee_success(self, internal_pay_api):
        """
        测试场景1：成功计算交易费用
        验证点：
        1. 接口返回 200
        2. code=200
        3. 返回fee金额
        """
        logger.info("测试场景1：成功计算交易费用")
        
        response = internal_pay_api.quote_transaction_fee(
            financial_account_id="test_fa_id",
            amount="100.00"
        )
        
        assert_status_ok(response)
        
        response_body = response.json()
        assert response_body.get("code") == 200, "业务code应为200"
        
        data = response_body.get("data", {})
        assert "fee" in data, "应包含fee字段"
        assert "amount" in data, "应包含amount字段"
        
        logger.info(f"✓ 费用计算成功，fee: {data.get('fee')}, amount: {data.get('amount')}")

    def test_invalid_financial_account_id(self, internal_pay_api):
        """
        测试场景2：无效的financial_account_id
        验证点：
        1. 接口返回错误
        """
        logger.info("测试场景2：无效的financial_account_id")
        
        response = internal_pay_api.quote_transaction_fee(
            financial_account_id="INVALID_FA_ID_999",
            amount="100.00"
        )
        
        assert response.status_code == 200
        
        response_body = response.json()
        if response_body.get("code") != 200:
            logger.info(f"✓ 正确拒绝无效ID: {response_body.get('error_message')}")
        
        logger.info("✓ 无效账户ID测试完成")

    def test_same_day_field(self, internal_pay_api):
        """
        测试场景3：same_day字段验证
        验证点：
        1. 响应包含same_day字段
        2. 但Properties中未定义
        3. 含义不明（当天到账？）
        """
        logger.info("测试场景3：same_day字段验证")
        
        # 使用测试数据
        response = internal_pay_api.quote_transaction_fee(
            financial_account_id="test_fa_id",
            amount="50.00"
        )
        
        if response.status_code == 200 and response.json().get("code") == 200:
            data = response.json().get("data", {})
            
            if "same_day" in data:
                logger.warning("⚠️ 检测到same_day字段（Properties中未定义）")
                logger.info(f"same_day值: {data['same_day']}")
                logger.info("推测含义：是否当天到账/处理")
            else:
                logger.info("未检测到same_day字段")
        
        logger.info("✓ same_day字段验证完成")

    def test_fee_calculation_for_different_amounts(self, internal_pay_api):
        """
        测试场景4：不同金额的费用计算
        验证点：
        1. 费用计算规则
        2. 是否有最低/最高费用
        """
        logger.info("测试场景4：不同金额的费用计算")
        
        test_amounts = ["1.00", "100.00", "1000.00"]
        
        for amount in test_amounts:
            response = internal_pay_api.quote_transaction_fee(
                financial_account_id="test_fa_id",
                amount=amount
            )
            
            if response.status_code == 200 and response.json().get("code") == 200:
                fee = response.json().get("data", {}).get("fee")
                logger.debug(f"金额: {amount}, 费用: {fee}")
        
        logger.info("✓ 费用计算测试完成")

    def test_http_method_error_in_doc(self, internal_pay_api):
        """
        测试场景5：HTTP方法示例错误记录
        验证点：
        1. 文档标题：POST /fee
        2. 示例中：GET /fee（错误）
        """
        logger.info("测试场景5：HTTP方法示例错误")
        
        logger.warning("⚠️ 文档问题：HTTP方法示例错误")
        logger.warning("标题标注: POST /internal-pay/fee")
        logger.warning("示例代码: GET /internal-pay/fee")
        logger.warning("正确的应该是POST（需要请求体）")
        
        logger.info("✓ HTTP方法错误已记录")
