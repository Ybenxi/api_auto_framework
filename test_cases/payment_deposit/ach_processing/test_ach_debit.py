"""
ACH Processing - Debit 接口测试用例
测试 POST /api/v1/cores/{core}/money-movements/ach/debit 接口
"""
import pytest
from utils.logger import logger


@pytest.mark.ach_processing
@pytest.mark.create_api
@pytest.mark.no_rerun
@pytest.mark.skip(reason="真实ACH收款，会从对方拉款，需要理解first_party逻辑")
class TestACHDebit:
    """
    ACH Debit测试（破坏性，全部skip）
    """

    def test_initiate_debit_third_party(self, ach_processing_api):
        """测试场景1：发起第三方Debit（收款）"""
        logger.info("测试场景1：发起第三方ACH Debit")
        
        response = ach_processing_api.initiate_debit(
            amount="75.00",
            financial_account_id="test_fa_id",
            counterparty_id="test_counterparty_id",
            first_party=False,
            memo="Third Party Debit"
        )
        assert response.status_code == 200
        logger.info("✓ 第三方Debit发起成功")

    def test_initiate_debit_first_party(self, ach_processing_api):
        """测试场景2：发起第一方Debit"""
        logger.info("测试场景2：发起第一方ACH Debit")
        
        response = ach_processing_api.initiate_debit(
            amount="30.00",
            financial_account_id="test_fa_id",
            counterparty_id="test_bank_account_id",  # 第一方Bank Account ID
            first_party=True,
            memo="First Party Debit"
        )
        assert response.status_code == 200
        logger.info("✓ 第一方Debit发起成功")

    def test_initiate_debit_same_day(self, ach_processing_api):
        """测试场景3：Same Day ACH Debit"""
        logger.info("测试场景3：Same Day ACH Debit")
        
        response = ach_processing_api.initiate_debit(
            amount="100.00",
            financial_account_id="test_fa_id",
            counterparty_id="test_cp_id",
            first_party=False,
            same_day=True,
            memo="Same Day Debit"
        )
        assert response.status_code == 200
        logger.info("✓ Same Day Debit发起成功")
