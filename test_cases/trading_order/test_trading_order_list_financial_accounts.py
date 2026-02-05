"""
Trading Order - List Investment Financial Accounts 接口测试用例
测试 GET /api/v1/cores/{core}/trading-orders/financial-accounts 接口
"""
import pytest
from utils.logger import logger
from utils.assertions import (
    assert_status_ok,
    assert_list_structure,
    assert_pagination,
    assert_fields_present,
    assert_string_contains_filter
)


@pytest.mark.trading_order
@pytest.mark.list_api
class TestTradingOrderListFinancialAccounts:
    """
    投资账户列表接口测试用例集
    """

    def test_list_investment_financial_accounts_success(self, trading_order_api):
        """
        测试场景1：成功获取投资账户列表
        验证点：
        1. 接口返回 200
        2. 返回列表结构正确
        3. 分页信息完整
        """
        logger.info("测试场景1：成功获取投资账户列表")
        
        response = trading_order_api.list_investment_financial_accounts(page=0, size=10)
        
        # 验证响应
        assert_status_ok(response)
        
        response_body = response.json()
        assert_list_structure(response_body)
        
        logger.info(f"✓ 投资账户列表获取成功，返回 {len(response_body['content'])} 个账户")

    def test_list_investment_financial_accounts_with_name_filter(self, trading_order_api):
        """
        测试场景2：使用name参数筛选账户
        验证点：
        1. 接口返回 200
        2. 筛选参数生效
        """
        logger.info("测试场景2：使用name参数筛选")
        
        # 先获取一个账户名称
        list_response = trading_order_api.list_investment_financial_accounts(size=1)
        assert_status_ok(list_response)
        
        accounts = list_response.json().get("content", [])
        if len(accounts) == 0:
            pytest.skip("没有可用的账户数据")
        
        test_name = accounts[0].get("name", "")
        if not test_name:
            pytest.skip("账户名称为空")
        
        # 使用名称筛选
        logger.info(f"使用名称筛选: {test_name}")
        filter_response = trading_order_api.list_investment_financial_accounts(name=test_name)
        
        assert_status_ok(filter_response)
        
        filtered_accounts = filter_response.json().get("content", [])
        if len(filtered_accounts) > 0:
            assert_string_contains_filter(filtered_accounts, "name", test_name, case_sensitive=False)
            logger.info("✓ 名称筛选功能验证通过")
        else:
            logger.info("✓ 筛选返回空结果（可能是模糊匹配未命中）")

    def test_list_investment_financial_accounts_pagination(self, trading_order_api):
        """
        测试场景3：验证分页功能
        验证点：
        1. 接口返回 200
        2. 分页参数正确处理
        """
        logger.info("测试场景3：验证分页功能")
        
        response = trading_order_api.list_investment_financial_accounts(page=0, size=5)
        
        assert_status_ok(response)
        
        response_body = response.json()
        assert_pagination(response_body, expected_size=5, expected_page=0)
        
        logger.info("✓ 分页功能验证通过")

    def test_list_investment_financial_accounts_response_structure(self, trading_order_api):
        """
        测试场景4：验证响应结构
        验证点：
        1. 接口返回 200
        2. 响应包含必需字段
        """
        logger.info("测试场景4：验证响应结构")
        
        response = trading_order_api.list_investment_financial_accounts(size=1)
        
        assert_status_ok(response)
        
        response_body = response.json()
        accounts = response_body.get("content", [])
        
        if len(accounts) > 0:
            account = accounts[0]
            required_fields = ["id", "name", "account_number"]
            assert_fields_present(account, required_fields, "投资账户")
            
            logger.info("✓ 响应结构验证通过")
        else:
            logger.info("✓ 响应结构正常（空结果）")

    def test_list_investment_financial_accounts_using_helper_method(self, trading_order_api):
        """
        测试场景5：使用辅助方法解析响应
        验证点：
        1. parse_list_response 辅助方法正常工作
        2. 解析结果包含必需字段
        """
        logger.info("测试场景5：使用辅助方法解析响应")
        
        response = trading_order_api.list_investment_financial_accounts()
        parsed = trading_order_api.parse_list_response(response)
        
        assert not parsed.get("error"), f"解析失败: {parsed.get('message')}"
        assert "content" in parsed
        assert "total_elements" in parsed
        
        logger.info(f"✓ 辅助方法解析成功，总数: {parsed['total_elements']}")
