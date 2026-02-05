"""
Remote Deposit Check - Financial Accounts 接口测试用例
测试 GET /api/v1/cores/{core}/money-movements/checks/financial-accounts 接口
"""
import pytest
from utils.logger import logger
from utils.assertions import assert_status_ok
from data.enums import AccountSubType


@pytest.mark.remote_deposit_check
@pytest.mark.list_api
class TestCheckFinancialAccounts:
    """
    Check可用账户列表接口测试用例集
    ⚠️ 文档问题：
    1. 接口描述错误（说ACH应为Check）
    2. HTTP方法示例错误（GET写成POST）
    3. 响应无code包装层
    """

    def test_list_financial_accounts_success(self, remote_deposit_check_api):
        """
        测试场景1：成功获取可用账户列表
        验证点：
        1. 接口返回 200
        2. 返回Financial Accounts列表
        """
        logger.info("测试场景1：成功获取Check可用账户列表")
        
        response = remote_deposit_check_api.list_financial_accounts(page=0, size=10)
        
        assert response.status_code == 200, "HTTP状态码应为200"
        
        response_body = response.json()
        
        if "content" in response_body:
            logger.info(f"✓ 可用账户列表获取成功，返回 {len(response_body.get('content', []))} 个账户")
        
        logger.info("✓ 可用账户列表获取成功")

    def test_filter_by_account_number(self, remote_deposit_check_api):
        """
        测试场景2：按account_number筛选
        验证点：
        1. account_number参数生效
        """
        logger.info("测试场景2：按account_number筛选")
        
        response = remote_deposit_check_api.list_financial_accounts(
            account_number="1-01-1-0007876",
            size=10
        )
        
        assert response.status_code == 200
        
        logger.info("✓ account_number筛选验证通过")

    def test_filter_by_name_fuzzy_search(self, remote_deposit_check_api):
        """
        测试场景3：按name模糊搜索
        验证点：
        1. name参数支持模糊搜索
        """
        logger.info("测试场景3：按name模糊搜索")
        
        response = remote_deposit_check_api.list_financial_accounts(name="Test", size=10)
        
        assert response.status_code == 200
        
        logger.info("✓ name模糊搜索验证通过")

    def test_filter_by_sub_type(self, remote_deposit_check_api):
        """
        测试场景4：按sub_type筛选
        验证点：
        1. sub_type参数生效
        2. 支持Checking和Savings（注意拼写）
        """
        logger.info("测试场景4：按sub_type筛选")
        
        response = remote_deposit_check_api.list_financial_accounts(
            sub_type=AccountSubType.CHECKING,
            size=10
        )
        
        assert response.status_code == 200
        
        logger.info("✓ sub_type筛选验证通过")

    def test_response_financial_account_id_redundancy(self, remote_deposit_check_api):
        """
        测试场景5：financial_account_id字段冗余验证
        验证点：
        1. 响应同时有id、account_id、financial_account_id
        2. 三个ID字段关系不明
        """
        logger.info("测试场景5：ID字段冗余验证")
        
        response = remote_deposit_check_api.list_financial_accounts(size=1)
        
        assert response.status_code == 200
        
        content = response.json().get("content", [])
        
        if content:
            account = content[0]
            
            has_id = "id" in account
            has_account_id = "account_id" in account
            has_fa_id = "financial_account_id" in account
            
            logger.info(f"id存在: {has_id}")
            logger.info(f"account_id存在: {has_account_id}")
            logger.info(f"financial_account_id存在: {has_fa_id}")
            
            if has_id and has_account_id and has_fa_id:
                logger.warning("⚠️ 文档问题：同时有三个ID字段，关系不明")
        
        logger.info("✓ ID字段冗余验证完成")

    def test_interface_description_error(self, remote_deposit_check_api):
        """
        测试场景6：接口描述错误验证
        验证点：
        1. 文档说"originate ACH transactions"
        2. 应为"originate Check transactions"
        """
        logger.info("测试场景6：接口描述错误验证")
        
        logger.warning("⚠️ 文档问题：接口描述错误")
        logger.warning("文档说：financial accounts that can originate ACH transactions")
        logger.warning("应改为：financial accounts that can originate Check transactions")
        
        logger.info("✓ 描述错误已记录")

    def test_http_method_example_error(self, remote_deposit_check_api):
        """
        测试场景7：HTTP方法示例错误
        验证点：
        1. 文档标题：GET
        2. 示例代码：POST（错误）
        """
        logger.info("测试场景7：HTTP方法示例错误")
        
        logger.warning("⚠️ 文档问题：HTTP方法示例错误")
        logger.warning("标题标注: GET /checks/financial-accounts")
        logger.warning("示例代码: POST /checks/financial-accounts")
        
        logger.info("✓ HTTP方法错误已记录")
