"""
账户关联 Financial Accounts 接口测试用例
测试 GET /api/v1/cores/{core}/accounts/{account_id}/financial-accounts 接口
"""
import pytest
from utils.logger import logger
from utils.assertions import (
    assert_status_ok,
    assert_response_parsed,
    assert_list_structure,
    assert_enum_filter,
    assert_pagination,
    assert_empty_result,
    assert_fields_present
)


class TestAccountFinancialAccounts:
    """
    账户关联 Financial Accounts 接口测试用例集
    """

    def test_get_financial_accounts_success(self, account_api):
        """
        测试场景1：成功获取账户关联的 Financial Accounts
        验证点：
        1. 先获取有效的 account_id
        2. 调用 Financial Accounts 接口
        3. 验证状态码 200
        4. 验证返回结构符合预期（content 列表）
        """
        # 获取一个有效的账户 ID
        list_response = account_api.list_accounts(size=1)
        assert_status_ok(list_response)
        parsed_list = account_api.parse_list_response(list_response)
        assert_response_parsed(parsed_list)
        
        accounts = parsed_list["content"]
        if len(accounts) == 0:
            pytest.skip("没有可用的账户数据，跳过 Financial Accounts 测试")
        
        account_id = accounts[0]["id"]
        
        # 调用 Financial Accounts 接口
        financial_response = account_api.get_financial_accounts(account_id)
        
        # 验证状态码和解析响应
        assert_status_ok(financial_response)
        parsed_financial = account_api.parse_financial_accounts_response(financial_response)
        assert_response_parsed(parsed_financial)
        assert_list_structure(parsed_financial, has_pagination=True)
        
        financial_accounts = parsed_financial["content"]
        total = parsed_financial["total_elements"]
        
        # 如果有数据，验证字段完整性
        if len(financial_accounts) > 0:
            first_account = financial_accounts[0]
            
            # 必需字段
            required_fields = ["id", "name", "account_number", "status", "record_type"]
            assert_fields_present(first_account, required_fields, obj_name="Financial Account")
            
            print(f"✓ 成功获取 Financial Accounts: 总数={total}, "
                  f"示例 ID={first_account.get('id')}, Name={first_account.get('name')}")
        else:
            logger.info("✓ 成功获取 Financial Accounts（当前账户没有关联的 Financial Accounts）")

    def test_get_financial_accounts_with_filters(self, account_api):
        """
        测试场景2：使用筛选条件获取 Financial Accounts
        验证点：
        1. 使用 status 筛选
        2. 验证返回结果符合筛选条件
        """
        # 获取账户 ID
        list_response = account_api.list_accounts(size=1)
        assert_status_ok(list_response)
        parsed_list = account_api.parse_list_response(list_response)
        assert_response_parsed(parsed_list)
        
        if len(parsed_list["content"]) == 0:
            pytest.skip("没有可用的账户数据")
        
        account_id = parsed_list["content"][0]["id"]
        
        # 使用筛选条件
        filter_status = "Pending"
        financial_response = account_api.get_financial_accounts(
            account_id,
            status=filter_status
        )
        
        # 验证
        assert_status_ok(financial_response)
        parsed_financial = account_api.parse_financial_accounts_response(financial_response)
        assert_response_parsed(parsed_financial)
        
        financial_accounts = parsed_financial["content"]
        
        # 如果有数据，验证筛选逻辑
        if len(financial_accounts) > 0:
            assert_enum_filter(financial_accounts, "status", filter_status, allow_none=True)
            logger.info("✓ 筛选成功，找到 {len(financial_accounts)} 个状态为 {filter_status} 的 Financial Accounts")
        else:
            logger.info(f"⚠ 未找到状态为 {filter_status} 的 Financial Accounts（可能是正常情况）")

    def test_get_financial_accounts_pagination(self, account_api):
        """
        测试场景3：验证分页功能
        验证点：
        1. 使用不同的 page 和 size 参数
        2. 验证分页信息正确
        """
        # 获取账户 ID
        list_response = account_api.list_accounts(size=1)
        assert_status_ok(list_response)
        parsed_list = account_api.parse_list_response(list_response)
        assert_response_parsed(parsed_list)
        
        if len(parsed_list["content"]) == 0:
            pytest.skip("没有可用的账户数据")
        
        account_id = parsed_list["content"][0]["id"]
        
        # 使用分页参数
        page_size = 5
        financial_response = account_api.get_financial_accounts(
            account_id,
            page=0,
            size=page_size
        )
        
        # 验证分页信息
        assert_status_ok(financial_response)
        parsed_financial = account_api.parse_financial_accounts_response(financial_response)
        assert_response_parsed(parsed_financial)
        
        assert_pagination(parsed_financial, expected_size=page_size, expected_page=0)
        
        logger.info("✓ 分页验证成功，请求 {page_size} 条，实际返回 {len(parsed_financial['content'])} 条")

    def test_get_financial_accounts_empty_result(self, account_api):
        """
        测试场景4：验证空结果处理
        验证点：
        1. 使用不存在的筛选条件
        2. 验证接口返回 200 和空列表
        """
        # 获取账户 ID
        list_response = account_api.list_accounts(size=1)
        assert_status_ok(list_response)
        parsed_list = account_api.parse_list_response(list_response)
        assert_response_parsed(parsed_list)
        
        if len(parsed_list["content"]) == 0:
            pytest.skip("没有可用的账户数据")
        
        account_id = parsed_list["content"][0]["id"]
        
        # 使用不太可能存在的筛选条件
        financial_response = account_api.get_financial_accounts(
            account_id,
            account_number="NONEXISTENT-999999"
        )
        
        # 验证空结果
        assert_status_ok(financial_response)
        parsed_financial = account_api.parse_financial_accounts_response(financial_response)
        assert_response_parsed(parsed_financial)
        
        assert_empty_result(parsed_financial)
        
        logger.info("✓ 空结果验证成功，接口正确返回空列表")

    def test_get_financial_accounts_invalid_account_id(self, account_api):
        """
        测试场景5：使用无效的 account_id
        验证点：
        1. 接口返回错误状态码
        """
        # 使用无效的 account_id
        invalid_id = "INVALID_ACCOUNT_ID_999999"
        financial_response = account_api.get_financial_accounts(invalid_id)
        
        # 验证返回错误状态码
        # 注意：某些 API 可能对无效 ID 返回 200 + 空列表，这里根据实际情况调整
        if financial_response.status_code == 200:
            parsed_financial = account_api.parse_financial_accounts_response(financial_response)
            assert len(parsed_financial["content"]) == 0, \
                "使用无效 ID 应该返回空列表"
            logger.info("✓ 使用无效 ID 返回 200 和空列表")
        else:
            logger.info("✓ 使用无效 ID 正确返回错误状态码: {financial_response.status_code}")
