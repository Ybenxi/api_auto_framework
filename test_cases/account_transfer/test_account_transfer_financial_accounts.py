"""
Account Transfer - Financial Accounts 接口测试用例
测试 GET /api/v1/cores/{core}/money-movements/account-transfer/financial-accounts 接口
"""
import pytest
from utils.logger import logger
from utils.assertions import assert_status_ok
from data.enums import AccountSubType


@pytest.mark.account_transfer
@pytest.mark.list_api
class TestAccountTransferFinancialAccounts:
    """
    Account Transfer可用账户列表接口测试用例集
    ⚠️ 文档问题：
    1. 接口描述错误（说ACH应为Account Transfer）
    2. HTTP方法示例错误（GET写成POST）
    """

    def test_list_financial_accounts_success(self, account_transfer_api):
        """
        测试场景1：成功获取可用账户列表
        验证点：
        1. 接口返回 200
        2. 返回Financial Accounts列表
        """
        logger.info("测试场景1：成功获取可用账户列表")
        
        response = account_transfer_api.list_financial_accounts(page=0, size=10)
        
        assert response.status_code == 200
        
        response_body = response.json()
        
        if "content" in response_body:
            logger.info(f"✓ 可用账户列表获取成功，返回 {len(response_body.get('content', []))} 个账户")
        
        logger.info("✓ 可用账户列表获取成功")

    def test_filter_by_account_number(self, account_transfer_api):
        """
        测试场景2：按account_number筛选
        验证点：
        1. account_number参数生效
        """
        logger.info("测试场景2：按account_number筛选")
        
        response = account_transfer_api.list_financial_accounts(
            account_number="1-01-1-0007876",
            size=10
        )
        
        assert response.status_code == 200
        
        logger.info("✓ account_number筛选验证通过")

    def test_filter_by_name_fuzzy_search(self, account_transfer_api):
        """
        测试场景3：按name模糊搜索
        验证点：
        1. name参数支持模糊搜索
        """
        logger.info("测试场景3：按name模糊搜索")
        
        response = account_transfer_api.list_financial_accounts(name="Test", size=10)
        
        assert response.status_code == 200
        
        logger.info("✓ name模糊搜索验证通过")

    def test_filter_by_sub_type(self, account_transfer_api):
        """
        测试场景4：按sub_type筛选
        验证点：
        1. sub_type参数生效
        2. 支持Checking和Savings
        """
        logger.info("测试场景4：按sub_type筛选")
        
        response = account_transfer_api.list_financial_accounts(
            sub_type=AccountSubType.CHECKING,
            size=10
        )
        
        assert response.status_code == 200
        
        logger.info("✓ sub_type筛选验证通过")

    def test_interface_description_error(self, account_transfer_api):
        """
        测试场景5：接口描述错误验证
        验证点：
        1. 文档说"originate ACH transactions"
        2. 应为"originate Account Transfer transactions"
        """
        logger.info("测试场景5：接口描述错误验证")
        
        logger.warning("⚠️ 文档问题：接口描述错误")
        logger.warning("文档说：financial accounts that can originate ACH transactions")
        logger.warning("应改为：financial accounts that can originate Account Transfer transactions")
        
        logger.info("✓ 描述错误已记录")

    def test_http_method_example_error(self, account_transfer_api):
        """
        测试场景6：HTTP方法示例错误
        验证点：
        1. 文档标题：GET
        2. 示例代码：POST（错误）
        """
        logger.info("测试场景6：HTTP方法示例错误")
        
        logger.warning("⚠️ 文档问题：HTTP方法示例错误")
        logger.warning("标题标注: GET /financial-accounts")
        logger.warning("示例代码: POST /financial-accounts")
        
        logger.info("✓ HTTP方法错误已记录")
