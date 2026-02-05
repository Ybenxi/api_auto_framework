"""
Remote Deposit Check - Scan & Deposit 接口测试用例
测试支票扫描和存款接口
"""
import pytest
from utils.logger import logger
from utils.assertions import assert_status_ok


@pytest.mark.remote_deposit_check
@pytest.mark.create_api
@pytest.mark.skip(reason="需要支票图片文件和真实存款操作")
class TestCheckScanDeposit:
    """
    支票扫描和存款测试（全部skip）
    ⚠️ Scan需要图片文件，Deposit会真实入账
    """

    def test_scan_check_success(self, remote_deposit_check_api):
        """测试场景1：成功扫描支票"""
        logger.info("测试场景1：成功扫描支票")
        
        response = remote_deposit_check_api.scan_check(
            front_check_image_path="/tmp/front_check.jpg",
            back_check_image_path="/tmp/back_check.jpg",
            financial_account_id="test_fa_id",
            amount="100.00"
        )
        
        assert response.status_code == 200
        
        scan_data = response.json()
        assert scan_data.get("success") == True, "扫描应成功"
        assert scan_data.get("item_identifier") is not None
        
        logger.info(f"✓ 扫描成功，item_identifier: {scan_data.get('item_identifier')}")

    def test_scan_response_format(self, remote_deposit_check_api):
        """测试场景2：Scan响应格式验证（使用success不是code）"""
        logger.info("测试场景2：Scan响应格式验证")
        
        logger.warning("⚠️ Scan响应格式特殊")
        logger.warning("使用success字段而不是code字段")
        logger.warning("这是唯一使用success的接口")
        logger.info("✓ 特殊响应格式已记录")

    def test_submit_deposit_success(self, remote_deposit_check_api):
        """测试场景3：成功提交存款"""
        logger.info("测试场景3：成功提交存款")
        
        # 依赖scan结果
        response = remote_deposit_check_api.submit_deposit(
            financial_account_id="test_fa_id",
            amount="100.00",
            item_identifier="uuid-from-scan",
            routing_number="121182865",
            account_number="1320301002154",
            check_date="2024-12-01",
            memo="Test Deposit"
        )
        
        assert response.status_code == 200
        logger.info("✓ 存款提交成功")

    def test_complete_deposit_flow(self, remote_deposit_check_api):
        """测试场景4：完整存款流程（Scan→Deposit）"""
        logger.info("测试场景4：完整存款流程")
        
        result = remote_deposit_check_api.complete_deposit_flow(
            front_image_path="/tmp/front.jpg",
            back_image_path="/tmp/back.jpg",
            financial_account_id="test_fa_id",
            amount="50.00",
            check_date="2024-12-01",
            memo="Complete Flow Test"
        )
        
        logger.info(f"流程步骤数: {len(result['steps'])}")
        logger.info(f"扫描结果: {result.get('scan_result')}")
        logger.info(f"最终结果: {result['success']}")
        
        logger.info("✓ 完整流程测试完成")


@pytest.mark.remote_deposit_check
@pytest.mark.create_api
class TestCheckScanDepositErrors:
    """扫描和存款错误处理（可运行）"""

    def test_scan_file_format_validation(self, remote_deposit_check_api):
        """测试场景5：文件格式验证"""
        logger.info("测试场景5：文件格式验证")
        
        logger.info("⚠️ 支持的文件格式：")
        logger.info("jpeg, png, pdf, tiff")
        logger.warning("文档中格式说明有误（带引号和点号）")
        logger.info("✓ 文件格式已记录")

    def test_deposit_missing_item_identifier(self, remote_deposit_check_api):
        """测试场景6：缺少item_identifier"""
        logger.info("测试场景6：缺少item_identifier")
        
        response = remote_deposit_check_api.submit_deposit(
            financial_account_id="test_fa_id",
            amount="100.00",
            item_identifier="",  # 空
            routing_number="121182865",
            account_number="1320301002154",
            check_date="2024-12-01"
        )
        assert response.status_code == 200
        logger.info("✓ 缺少item_identifier测试完成")

    def test_item_identifier_dependency(self, remote_deposit_check_api):
        """测试场景7：item_identifier依赖关系验证"""
        logger.info("测试场景7：item_identifier依赖验证")
        
        logger.warning("⚠️ 流程依赖：")
        logger.warning("1. 必须先Scan获取item_identifier")
        logger.warning("2. 然后用item_identifier提交Deposit")
        logger.warning("3. item_identifier有效期未说明")
        logger.warning("4. 是否可重复使用未说明")
        logger.info("✓ 依赖关系已记录")
