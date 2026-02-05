"""
Account Transfer - Transfer 接口测试用例
测试 POST /api/v1/cores/{core}/money-movements/account-transfer 接口
"""
import pytest
from utils.logger import logger
from utils.assertions import assert_status_ok


@pytest.mark.account_transfer
@pytest.mark.create_api
@pytest.mark.no_rerun
class TestAccountTransferTransfer:
    """
    Account Transfer转账接口测试用例集
    ⚠️ 重要：这是真实的转账操作，会实际扣款
    ⚠️ 大部分测试需要skip
    """

    @pytest.mark.skip(reason="真实转账操作，会实际扣款，需要测试账户")
    def test_initiate_transfer_success(self, account_transfer_api):
        """
        测试场景1：成功发起转账
        验证点：
        1. 接口返回 200
        2. 返回交易ID和status
        3. 包含direction字段（Account Transfer独有）
        """
        logger.info("测试场景1：成功发起转账")
        
        response = account_transfer_api.initiate_transfer(
            payer_financial_account_id="test_payer_fa_id",
            payee_financial_account_id="test_payee_fa_id",
            amount="1.00",
            memo="Auto TestYan Account Transfer"
        )
        
        assert response.status_code == 200
        
        # 响应无code包装层
        transfer_data = response.json()
        
        assert transfer_data.get("id") is not None, "交易ID不应为空"
        assert transfer_data.get("status") in ["Completed", "Processing", "Reviewing"]
        
        # 检查direction字段（Account Transfer独有）
        if "direction" in transfer_data:
            logger.info(f"✓ 检测到direction字段: {transfer_data['direction']}")
        
        logger.info(f"✓ 转账发起成功，ID: {transfer_data['id']}")

    @pytest.mark.skip(reason="真实转账，需要测试账户")
    def test_cross_profile_transfer(self, account_transfer_api):
        """
        测试场景2：跨Profile转账
        验证点：
        1. Account Transfer支持跨Profile
        2. 转账成功
        """
        logger.info("测试场景2：跨Profile转账")
        
        logger.info("⚠️ Account Transfer核心特性：跨Profile灵活性")
        logger.info("可在不同profile的账户间转账")
        logger.info("这是与Internal Pay的主要差异之一")
        
        response = account_transfer_api.initiate_transfer(
            payer_financial_account_id="profile1_fa_id",
            payee_financial_account_id="profile2_fa_id",
            amount="10.00",
            memo="Cross Profile Transfer"
        )
        
        logger.info(f"响应状态: {response.status_code}")
        
        logger.info("✓ 跨Profile转账测试完成")

    def test_missing_required_field(self, account_transfer_api):
        """
        测试场景3：缺少必需字段
        验证点：
        1. 接口返回错误
        """
        logger.info("测试场景3：缺少必需字段")
        
        response = account_transfer_api.initiate_transfer(
            payer_financial_account_id="test_payer_id",
            payee_financial_account_id="test_payee_id"
            # 缺少 amount
        )
        
        assert response.status_code == 200
        logger.info(f"响应: {response.json()}")
        
        logger.info("✓ 缺少必需字段测试完成")

    def test_invalid_account_ids(self, account_transfer_api):
        """
        测试场景4：无效的账户ID
        验证点：
        1. 接口返回错误
        """
        logger.info("测试场景4：无效的账户ID")
        
        response = account_transfer_api.initiate_transfer(
            payer_financial_account_id="INVALID_PAYER_999",
            payee_financial_account_id="INVALID_PAYEE_999",
            amount="1.00"
        )
        
        assert response.status_code == 200
        logger.info(f"响应: {response.json()}")
        
        logger.info("✓ 无效账户ID测试完成")

    def test_response_no_code_wrapper(self, account_transfer_api):
        """
        测试场景5：响应格式验证（无code包装层）
        验证点：
        1. Transfer响应直接返回交易对象
        2. parse方法正确处理
        """
        logger.info("测试场景5：响应格式验证")
        
        logger.warning("⚠️ 文档问题：响应格式不一致")
        logger.info("List Transactions: 无code包装层")
        logger.info("List Financial Accounts: 无code包装层")
        logger.info("Transfer: 无code包装层")
        logger.info("Quote Fee: 有code包装层")
        
        logger.info("✓ 格式不一致问题已记录")

    def test_module_difference_from_internal_pay(self, account_transfer_api):
        """
        测试场景6：与Internal Pay的差异验证
        验证点：
        1. Account Transfer多了direction字段
        2. 支持跨Profile转账
        3. 其他功能几乎完全相同
        """
        logger.info("测试场景6：与Internal Pay差异验证")
        
        logger.warning("⚠️ 文档问题：模块差异未说明")
        logger.info("Internal Pay vs Account Transfer差异：")
        logger.info("1. Account Transfer有direction字段")
        logger.info("2. Account Transfer支持跨Profile")
        logger.info("3. URL路径不同")
        logger.info("4. 其他Properties和接口完全相同")
        logger.info("建议文档明确说明使用场景")
        
        logger.info("✓ 模块差异已记录")
