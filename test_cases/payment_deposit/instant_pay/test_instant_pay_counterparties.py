"""
Instant Pay - Counterparties 接口测试用例
测试对手方列表和创建接口
"""
import pytest
from utils.logger import logger
from data.enums import CounterpartyType, BankAccountType


@pytest.mark.instant_pay
@pytest.mark.list_api
class TestInstantPayCounterparties:
    """Instant Pay对手方测试"""

    def test_list_counterparties_success(self, instant_pay_api):
        """测试场景1：成功获取对手方列表"""
        logger.info("测试场景1：成功获取对手方列表")
        
        response = instant_pay_api.list_counterparties(page=0, size=10)
        assert response.status_code == 200
        logger.info("✓ 对手方列表获取成功")


@pytest.mark.instant_pay
@pytest.mark.create_api
@pytest.mark.skip(reason="需要真实数据创建对手方")
class TestInstantPayCounterpartiesCreate:
    """对手方创建测试（skip）"""

    def test_create_counterparty_success(self, instant_pay_api):
        """测试场景2：成功创建Instant Pay对手方"""
        logger.info("测试场景2：成功创建对手方")
        
        import time
        response = instant_pay_api.create_counterparty(
            name=f"Auto TestYan Instant CP {int(time.time())}",
            type=CounterpartyType.PERSON,
            bank_account_type=BankAccountType.CHECKING,
            bank_routing_number="091918457",
            bank_name="Test Bank",
            bank_account_owner_name="Auto TestYan",
            bank_account_number="111111111"
        )
        assert response.status_code == 200
        logger.info("✓ 对手方创建成功")
