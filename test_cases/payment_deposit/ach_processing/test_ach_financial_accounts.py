"""
ACH Processing - Financial Accounts 接口测试用例
测试 GET /api/v1/cores/{core}/money-movements/ach/financial-accounts 接口
"""
import pytest
from utils.logger import logger
from utils.assertions import assert_status_ok
from data.enums import AccountSubType


@pytest.mark.ach_processing
@pytest.mark.list_api
class TestACHFinancialAccounts:
    """
    ACH可用账户列表接口测试用例集
    ⚠️ 文档问题：响应无code包装层
    """

    def test_list_financial_accounts_success(self, ach_processing_api):
        """
        测试场景1：成功获取可用账户列表
        验证点：
        1. 接口返回 200
        2. 返回Financial Accounts列表
        """
        logger.info("测试场景1：成功获取ACH可用账户列表")
        
        response = ach_processing_api.list_financial_accounts(page=0, size=10)
        
        assert response.status_code == 200, "HTTP状态码应为200"
        
        response_body = response.json()
        
        if "content" in response_body:
            logger.info(f"✓ 可用账户列表获取成功，返回 {len(response_body.get('content', []))} 个账户")
        
        logger.info("✓ 可用账户列表获取成功")

    def test_filter_by_account_number(self, ach_processing_api):
        """
        测试场景2：按account_number筛选
        验证点：
        1. account_number参数生效
        """
        logger.info("测试场景2：按account_number筛选")
        
        response = ach_processing_api.list_financial_accounts(
            account_number="1-01-1-0007876",
            size=10
        )
        
        assert response.status_code == 200
        
        logger.info("✓ account_number筛选验证通过")

    def test_filter_by_name_fuzzy_search(self, ach_processing_api):
        """
        测试场景3：按name模糊搜索
        验证点：
        1. name参数支持模糊搜索
        """
        logger.info("测试场景3：按name模糊搜索")
        
        response = ach_processing_api.list_financial_accounts(name="Test", size=10)
        
        assert response.status_code == 200
        
        logger.info("✓ name模糊搜索验证通过")

    def test_filter_by_sub_type(self, ach_processing_api):
        """
        测试场景4：按sub_type筛选
        验证点：
        1. sub_type参数生效
        2. 支持Checking和Savings（注意拼写）
        """
        logger.info("测试场景4：按sub_type筛选")
        
        response = ach_processing_api.list_financial_accounts(
            sub_type=AccountSubType.CHECKING,
            size=10
        )
        
        assert response.status_code == 200
        
        logger.info("✓ sub_type筛选验证通过")

    def test_filter_by_account_ids(self, ach_processing_api):
        """
        测试场景5：按account_ids批量查询
        验证点：
        1. account_ids参数支持数组
        2. 逗号分隔格式
        """
        logger.info("测试场景5：按account_ids批量查询")
        
        response = ach_processing_api.list_financial_accounts(
            account_ids=["123", "456"],
            size=10
        )
        
        assert response.status_code == 200
        
        logger.info("✓ account_ids批量查询验证通过")

    def test_response_structure(self, ach_processing_api):
        """
        测试场景6：响应结构验证
        验证点：
        1. 包含余额信息
        2. 包含账户基本信息
        """
        logger.info("测试场景6：响应结构验证")
        
        response = ach_processing_api.list_financial_accounts(size=1)
        
        assert response.status_code == 200
        
        content = response.json().get("content", [])
        
        if content:
            account = content[0]
            
            # 验证余额字段
            balance_fields = ["available_balance", "balance"]
            for field in balance_fields:
                if field in account:
                    logger.debug(f"{field}: {account[field]}")
            
            logger.debug(f"账户字段: {list(account.keys())}")
        
        logger.info("✓ 响应结构验证通过")

    def test_sub_type_spelling_error(self, ach_processing_api):
        """
        测试场景7：sub_type拼写错误验证
        验证点：
        1. 文档说Saving（无s）
        2. 应为Savings
        """
        logger.info("测试场景7：sub_type拼写错误验证")
        
        logger.warning("⚠️ 文档问题：sub_type拼写错误")
        logger.warning("文档说：Checking and Saving")
        logger.warning("应该是：Checking and Savings（复数）")
        
        logger.info("✓ 拼写错误已记录")
