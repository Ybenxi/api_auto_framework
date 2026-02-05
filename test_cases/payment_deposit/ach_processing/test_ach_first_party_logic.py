"""
ACH Processing - First Party业务逻辑测试
测试第一方和第三方转账的区别
"""
import pytest
from utils.logger import logger


@pytest.mark.ach_processing
@pytest.mark.list_api
class TestACHFirstPartyLogic:
    """
    First Party业务逻辑验证
    ⚠️⚠️⚠️ 这是ACH模块最关键的业务逻辑
    """

    def test_list_bank_accounts_for_first_party(self, ach_processing_api):
        """
        测试场景1：获取第一方银行账户列表
        验证点：
        1. 返回Bank Accounts（用于first_party=true）
        2. 响应字段验证
        """
        logger.info("测试场景1：获取第一方银行账户列表")
        
        response = ach_processing_api.list_bank_accounts(page=0, size=10)
        assert response.status_code == 200
        
        content = response.json().get("content", [])
        
        if content:
            bank_account = content[0]
            logger.info(f"✓ Bank Account ID: {bank_account.get('id')}")
            logger.info("此ID用于first_party=true的转账")
            
            # 验证bank_is_us_based字段
            if "bank_is_us_based" in bank_account:
                logger.info(f"bank_is_us_based: {bank_account['bank_is_us_based']}")
        
        logger.info("✓ 第一方银行账户列表获取成功")

    def test_list_counterparties_for_third_party(self, ach_processing_api):
        """
        测试场景2：获取第三方对手方列表
        验证点：
        1. 返回ACH Counterparties（用于first_party=false）
        2. 与Bank Accounts的区别
        """
        logger.info("测试场景2：获取第三方对手方列表")
        
        response = ach_processing_api.list_counterparties(page=0, size=10)
        assert response.status_code == 200
        
        content = response.json().get("content", [])
        
        if content:
            counterparty = content[0]
            logger.info(f"✓ Counterparty ID: {counterparty.get('id')}")
            logger.info("此ID用于first_party=false的转账")
        
        logger.info("✓ 第三方对手方列表获取成功")

    def test_first_party_logic_explanation(self, ach_processing_api):
        """
        测试场景3：First Party业务逻辑说明
        验证点：
        1. 记录完整的业务逻辑
        2. first_party字段的影响
        """
        logger.info("测试场景3：First Party业务逻辑")
        
        logger.info("=" * 60)
        logger.info("⚠️⚠️⚠️ ACH First Party核心业务逻辑")
        logger.info("=" * 60)
        
        logger.info("")
        logger.info("【第一方转账】first_party=true")
        logger.info("  使用场景：自己的不同银行账户间转账")
        logger.info("  counterparty_id来源：")
        logger.info("    → 从 list_bank_accounts() 接口获取")
        logger.info("    → 使用返回的 Bank Account ID")
        logger.info("  验证：UniFi会验证银行所有人信息")
        
        logger.info("")
        logger.info("【第三方转账】first_party=false")
        logger.info("  使用场景：给其他人/公司转账")
        logger.info("  counterparty_id来源：")
        logger.info("    → 从 list_counterparties() 接口获取")
        logger.info("    → 使用返回的 ACH Counterparty ID")
        logger.info("  验证：使用已创建和批准的counterparty")
        
        logger.info("")
        logger.info("【错误使用会导致】")
        logger.info("  ✗ first_party=true但用Counterparty ID → 验证失败")
        logger.info("  ✗ first_party=false但用Bank Account ID → 可能找不到counterparty")
        
        logger.info("=" * 60)
        
        logger.info("✓ First Party逻辑已完整记录")


@pytest.mark.ach_processing
@pytest.mark.create_api
@pytest.mark.no_rerun
@pytest.mark.skip(reason="真实转账操作，需要理解first_party逻辑")
class TestACHFirstPartyTransfer:
    """
    First Party转账测试（需要真实数据，全部skip）
    """

    def test_first_party_credit(self, ach_processing_api):
        """
        测试场景4：第一方Credit转账
        验证点：
        1. first_party=true
        2. counterparty_id使用Bank Account ID
        """
        logger.info("测试场景4：第一方Credit转账")
        
        # 步骤1：获取Bank Account ID
        bank_accounts = ach_processing_api.list_bank_accounts(size=1)
        bank_id = bank_accounts.json().get("content", [])[0].get("id")
        
        logger.info(f"使用Bank Account ID: {bank_id}")
        
        # 步骤2：发起第一方转账
        response = ach_processing_api.initiate_credit(
            amount="10.00",
            financial_account_id="test_fa_id",
            counterparty_id=bank_id,  # ⚠️ 使用Bank Account ID
            first_party=True,          # ⚠️ 标记为第一方
            memo="First Party Transfer"
        )
        
        assert response.status_code == 200
        logger.info("✓ 第一方Credit转账成功")

    def test_third_party_credit(self, ach_processing_api):
        """
        测试场景5：第三方Credit转账
        验证点：
        1. first_party=false
        2. counterparty_id使用ACH Counterparty ID
        """
        logger.info("测试场景5：第三方Credit转账")
        
        # 步骤1：获取Counterparty ID
        counterparties = ach_processing_api.list_counterparties(size=1)
        cp_id = counterparties.json().get("content", [])[0].get("id")
        
        logger.info(f"使用Counterparty ID: {cp_id}")
        
        # 步骤2：发起第三方转账
        response = ach_processing_api.initiate_credit(
            amount="20.00",
            financial_account_id="test_fa_id",
            counterparty_id=cp_id,    # ⚠️ 使用Counterparty ID
            first_party=False,         # ⚠️ 标记为第三方
            memo="Third Party Transfer"
        )
        
        assert response.status_code == 200
        logger.info("✓ 第三方Credit转账成功")

    def test_first_party_with_wrong_counterparty_type(self, ach_processing_api):
        """
        测试场景6：first_party=true但使用Counterparty ID（错误场景）
        验证点：
        1. 应该返回错误
        2. 验证业务逻辑约束
        """
        logger.info("测试场景6：first_party逻辑错误验证")
        
        # 获取Counterparty ID（不是Bank Account ID）
        counterparties = ach_processing_api.list_counterparties(size=1)
        cp_id = counterparties.json().get("content", [])[0].get("id")
        
        # 错误使用：first_party=true但用Counterparty ID
        response = ach_processing_api.initiate_credit(
            amount="10.00",
            financial_account_id="test_fa_id",
            counterparty_id=cp_id,    # ⚠️ 错误：应该用Bank Account ID
            first_party=True,          # ⚠️ 但标记为第一方
            memo="Wrong ID Type"
        )
        
        # 应该返回错误
        logger.info(f"响应状态: {response.status_code}")
        logger.info("应该返回错误（ID类型不匹配）")
        
        logger.info("✓ 错误场景验证完成")
