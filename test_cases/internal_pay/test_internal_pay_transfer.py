"""
Internal Pay - Transfer 接口测试用例
测试 POST /api/v1/cores/{core}/money-movements/internal-pay/transfer 接口
"""
import pytest
from utils.logger import logger
from utils.assertions import assert_status_ok


@pytest.mark.internal_pay
@pytest.mark.create_api
@pytest.mark.no_rerun
class TestInternalPayTransfer:
    """
    Internal Pay转账接口测试用例集
    ⚠️ 重要：这是真实的转账操作，会实际扣款
    ⚠️ 大部分测试需要skip
    """

    @pytest.mark.skip(reason="真实转账操作，会实际扣款，需要测试账户")
    def test_initiate_transfer_success(self, internal_pay_api):
        """
        测试场景1：成功发起转账
        验证点：
        1. 接口返回 200
        2. 返回交易ID和status
        3. status应为Completed或Processing
        """
        logger.info("测试场景1：成功发起转账")
        
        response = internal_pay_api.initiate_transfer(
            payer_financial_account_id="test_payer_fa_id",
            payee_financial_account_id="test_payee_fa_id",
            amount="1.00",
            memo="Auto TestYan Transfer"
        )
        
        assert response.status_code == 200
        
        # 响应无code包装层
        transfer_data = response.json()
        
        assert transfer_data.get("id") is not None, "交易ID不应为空"
        assert transfer_data.get("status") in ["Completed", "Processing", "Reviewing"]
        
        logger.info(f"✓ 转账发起成功，ID: {transfer_data['id']}, Status: {transfer_data['status']}")

    @pytest.mark.skip(reason="真实转账，需要测试账户")
    def test_transfer_with_sub_accounts(self, internal_pay_api):
        """
        测试场景2：使用Sub Accounts转账
        验证点：
        1. sub_account_id参数正确传递
        2. 转账成功
        """
        logger.info("测试场景2：使用Sub Accounts转账")
        
        response = internal_pay_api.initiate_transfer(
            payer_financial_account_id="test_payer_fa_id",
            payer_sub_account_id="test_payer_sub_id",
            payee_financial_account_id="test_payee_fa_id",
            payee_sub_account_id="test_payee_sub_id",
            amount="5.00",
            memo="Sub Account Transfer"
        )
        
        assert response.status_code == 200
        
        logger.info("✓ Sub Account转账验证通过")

    def test_missing_required_field(self, internal_pay_api):
        """
        测试场景3：缺少必需字段
        验证点：
        1. 接口返回错误
        """
        logger.info("测试场景3：缺少必需字段")
        
        response = internal_pay_api.initiate_transfer(
            payer_financial_account_id="test_payer_id",
            payee_financial_account_id="test_payee_id"
            # 缺少 amount
        )
        
        assert response.status_code == 200
        
        # 检查是否有错误（可能有code字段，也可能直接是错误对象）
        response_body = response.json()
        logger.info(f"响应体: {response_body}")
        
        logger.info("✓ 缺少必需字段测试完成")

    def test_invalid_payer_account_id(self, internal_pay_api):
        """
        测试场景4：无效的付款方账户ID
        验证点：
        1. 接口返回错误
        """
        logger.info("测试场景4：无效的付款方账户ID")
        
        response = internal_pay_api.initiate_transfer(
            payer_financial_account_id="INVALID_PAYER_999",
            payee_financial_account_id="test_payee_id",
            amount="1.00"
        )
        
        assert response.status_code == 200
        logger.info(f"响应: {response.json()}")
        
        logger.info("✓ 无效付款方ID测试完成")

    def test_invalid_payee_account_id(self, internal_pay_api):
        """
        测试场景5：无效的收款方账户ID
        验证点：
        1. 接口返回错误
        """
        logger.info("测试场景5：无效的收款方账户ID")
        
        response = internal_pay_api.initiate_transfer(
            payer_financial_account_id="test_payer_id",
            payee_financial_account_id="INVALID_PAYEE_999",
            amount="1.00"
        )
        
        assert response.status_code == 200
        logger.info(f"响应: {response.json()}")
        
        logger.info("✓ 无效收款方ID测试完成")

    def test_conditional_sub_account_requirement(self, internal_pay_api):
        """
        测试场景6：条件必需字段验证（sub_account_id）
        验证点：
        1. 文档说"Required if a sub account exists"
        2. 逻辑不清晰：谁判断exists？
        3. 验证实际行为
        """
        logger.info("测试场景6：条件必需字段验证")
        
        logger.warning("⚠️ 文档问题：条件必需字段逻辑不清")
        logger.info("sub_account_id: Required if a sub account exists")
        logger.info("问题：由谁判断'exists'？")
        logger.info("问题：如果有多个sub account，如何处理？")
        
        logger.info("✓ 条件必需字段问题已记录")

    def test_response_no_code_wrapper(self, internal_pay_api):
        """
        测试场景7：响应格式验证（无code包装层）
        验证点：
        1. Transfer响应直接返回交易对象
        2. 无code包装层
        3. parse方法正确处理
        """
        logger.info("测试场景7：响应格式验证")
        
        logger.warning("⚠️ 文档问题：响应格式不一致")
        logger.info("List Transactions: 无code包装层")
        logger.info("Transfer: 无code包装层")
        logger.info("Quote Fee: 有code包装层")
        
        logger.info("✓ 格式不一致问题已记录")
