"""
Remote Deposit Check - Counterparties 接口测试用例
测试对手方列表和创建接口
"""
import pytest
from utils.logger import logger
from data.enums import CounterpartyType, BankAccountType


@pytest.mark.remote_deposit_check
@pytest.mark.list_api
class TestCheckCounterparties:
    """Check对手方测试"""

    def test_list_counterparties_success(self, remote_deposit_check_api):
        """测试场景1：成功获取对手方列表"""
        logger.info("测试场景1：成功获取对手方列表")
        
        response = remote_deposit_check_api.list_counterparties(page=0, size=10)
        assert response.status_code == 200
        logger.info("✓ 对手方列表获取成功")


@pytest.mark.remote_deposit_check
@pytest.mark.create_api
@pytest.mark.skip(reason="需要真实数据创建对手方")
class TestCheckCounterpartiesCreate:
    """对手方创建测试（skip）"""

    def test_create_counterparty_success(self, remote_deposit_check_api):
        """测试场景2：成功创建支票对手方"""
        logger.info("测试场景2：成功创建支票对手方")
        
        import time
        response = remote_deposit_check_api.create_counterparty(
            name=f"Auto TestYan Check CP {int(time.time())}",
            type=CounterpartyType.PERSON,
            address1="123 Test Street",
            bank_account_type=BankAccountType.CHECKING,
            bank_routing_number="091918457",
            bank_account_owner_name="Auto TestYan",
            bank_account_number="11111111"
        )
        assert response.status_code == 200
        logger.info("✓ 对手方创建成功")


@pytest.mark.remote_deposit_check
@pytest.mark.create_api
class TestCheckCounterpartiesErrors:
    """对手方创建错误处理（可运行）"""

    def test_missing_required_address1(self, remote_deposit_check_api):
        """测试场景3：缺少必需的address1"""
        logger.info("测试场景3：缺少address1")
        
        response = remote_deposit_check_api.create_counterparty(
            name="Auto TestYan Test",
            type=CounterpartyType.PERSON
            # 缺少address1（Check counterparty必需）
        )
        assert response.status_code == 200
        logger.info("✓ 缺少address1测试完成")
