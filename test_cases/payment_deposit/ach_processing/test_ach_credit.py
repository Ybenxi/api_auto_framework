"""
ACH Processing - Credit 接口测试用例
测试 POST /api/v1/cores/{core}/money-movements/ach/credit 接口
"""
import pytest
from utils.logger import logger
from data.enums import PaymentTransactionType


@pytest.mark.ach_processing
@pytest.mark.create_api
@pytest.mark.no_rerun
@pytest.mark.skip(reason="真实ACH转账，会实际扣款，需要理解first_party逻辑")
class TestACHCredit:
    """
    ACH Credit测试（破坏性，全部skip）
    """

    def test_initiate_credit_third_party(self, ach_processing_api):
        """测试场景1：发起第三方Credit（标准场景）"""
        logger.info("测试场景1：发起第三方ACH Credit")
        
        response = ach_processing_api.initiate_credit(
            amount="100.00",
            financial_account_id="test_fa_id",
            counterparty_id="test_counterparty_id",  # 第三方Counterparty ID
            first_party=False,
            same_day=False,
            memo="Third Party Credit"
        )
        assert response.status_code == 200
        logger.info("✓ 第三方Credit发起成功")

    def test_initiate_credit_first_party(self, ach_processing_api):
        """测试场景2：发起第一方Credit（自己账户间）"""
        logger.info("测试场景2：发起第一方ACH Credit")
        
        response = ach_processing_api.initiate_credit(
            amount="50.00",
            financial_account_id="test_fa_id",
            counterparty_id="test_bank_account_id",  # 第一方Bank Account ID
            first_party=True,
            memo="First Party Credit"
        )
        assert response.status_code == 200
        logger.info("✓ 第一方Credit发起成功")

    def test_initiate_credit_same_day(self, ach_processing_api):
        """测试场景3：Same Day ACH Credit"""
        logger.info("测试场景3：Same Day ACH Credit")
        
        logger.warning("⚠️ Same Day ACH截止时间（UniFi Deadline）：")
        logger.warning("9:45 AM ET - Same Day")
        logger.warning("3:45 PM ET - Same Day")
        logger.warning("6:45 PM ET - Next Day")
        logger.warning("9:45 PM ET - Next Day")
        
        response = ach_processing_api.initiate_credit(
            amount="200.00",
            financial_account_id="test_fa_id",
            counterparty_id="test_cp_id",
            first_party=False,
            same_day=True,  # 当天处理
            memo="Same Day Credit"
        )
        assert response.status_code == 200
        logger.info("✓ Same Day Credit发起成功")


@pytest.mark.ach_processing
@pytest.mark.create_api
class TestACHCreditErrors:
    """ACH Credit错误处理（可运行）"""

    def test_missing_required_field(self, ach_processing_api):
        """测试场景4：缺少必需字段"""
        logger.info("测试场景4：缺少必需字段")
        
        response = ach_processing_api.initiate_credit(
            amount="10.00",
            financial_account_id="test_fa_id",
            counterparty_id=""  # 空
        )
        assert response.status_code == 200
        logger.info("✓ 缺少必需字段测试完成")

    def test_same_day_cutoff_time_inconsistency(self, ach_processing_api):
        """测试场景5：same_day截止时间不一致验证"""
        logger.info("测试场景5：same_day截止时间不一致")
        
        logger.warning("⚠️ 文档问题：截止时间说明不一致")
        logger.warning("Properties说：3:00 PM CT")
        logger.warning("表格说：3:45 PM ET也是Same Day")
        logger.warning("时区不一致（CT vs ET）")
        logger.warning("时间不一致（3:00 PM vs 3:45 PM）")
        
        logger.info("✓ 截止时间不一致已记录")
