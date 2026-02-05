"""
ACH Processing - Counterparties 接口测试用例
测试对手方列表和创建接口
"""
import pytest
from utils.logger import logger
from data.enums import CounterpartyType, BankAccountType


@pytest.mark.ach_processing
@pytest.mark.list_api
class TestACHCounterparties:
    """ACH对手方测试"""

    def test_list_counterparties_success(self, ach_processing_api):
        """测试场景1：成功获取对手方列表（第三方）"""
        logger.info("测试场景1：成功获取ACH对手方列表")
        
        response = ach_processing_api.list_counterparties(page=0, size=10)
        assert response.status_code == 200
        logger.info("✓ 第三方对手方列表获取成功")


@pytest.mark.ach_processing
@pytest.mark.create_api
@pytest.mark.skip(reason="需要真实数据创建对手方")
class TestACHCounterpartiesCreate:
    """对手方创建测试（skip）"""

    def test_create_counterparty_success(self, ach_processing_api):
        """测试场景2：成功创建ACH对手方"""
        logger.info("测试场景2：成功创建ACH对手方（第三方）")
        
        import time
        response = ach_processing_api.create_counterparty(
            name=f"Auto TestYan ACH CP {int(time.time())}",
            type=CounterpartyType.PERSON,
            bank_account_type=BankAccountType.CHECKING,
            bank_routing_number="091918457",
            bank_name="Test Bank",
            bank_account_owner_name="Auto TestYan",
            bank_account_number="111111111"
        )
        assert response.status_code == 200
        
        cp_id = response.json().get("id")
        logger.info(f"✓ 对手方创建成功，ID: {cp_id}")
        logger.info("此ID用于first_party=false的转账")
