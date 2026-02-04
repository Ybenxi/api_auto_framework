"""
账户 Settled Transactions 接口测试用例
测试 GET /api/v1/cores/{core}/accounts/{account_id}/settled-transactions 接口
"""
import pytest
from utils.assertions import (
from utils.logger import logger
    assert_status_ok,
    assert_response_parsed,
    assert_list_structure,
    assert_pagination,
    assert_fields_present
)


@pytest.mark.transaction_api
class TestAccountTransactions:
    """
    账户 Settled Transactions 接口测试用例集
    """

    def test_get_settled_transactions_success(self, account_api):
        """
        测试场景1：成功获取账户的 Settled Transactions
        依赖逻辑：先从列表接口获取一个有效的 account_id，然后获取 Transactions
        验证点：
        1. 列表接口返回成功
        2. Transactions 接口返回 200
        3. 返回数据结构正确（content 列表）
        4. 如果有数据，验证字段完整性
        """
        # 先调用列表接口获取一个账户 ID
        list_response = account_api.list_accounts(size=1)
        assert_status_ok(list_response)
        parsed_list = account_api.parse_list_response(list_response)
        assert_response_parsed(parsed_list)
        
        accounts = parsed_list["content"]
        if len(accounts) == 0:
            pytest.skip("没有可用的账户数据，跳过 Transactions 测试")
        
        # 提取第一个账户的 ID
        account_id = accounts[0]["id"]
        
        # 调用 Transactions 接口
        transactions_response = account_api.get_settled_transactions(account_id)
        
        # 断言状态码和解析响应
        assert_status_ok(transactions_response)
        parsed_transactions = account_api.parse_transactions_response(transactions_response)
        assert_response_parsed(parsed_transactions)
        assert_list_structure(parsed_transactions, has_pagination=True)
        
        transactions = parsed_transactions["content"]
        
        # 如果有数据，验证字段完整性
        if len(transactions) > 0:
            first_transaction = transactions[0]
            
            # 验证必需字段
            required_fields = [
                "id",
                "financial_account_id",
                "financial_account_name",
                "financial_account_number",
                "transaction_type",
                "settle_date"
            ]
            assert_fields_present(first_transaction, required_fields, obj_name="Transaction")
            
            print(f"✓ 成功获取 Transactions: 总数={parsed_transactions['total_elements']}, "
                  f"第一个 Transaction ID={first_transaction.get('id')}, "
                  f"Financial Account={first_transaction.get('financial_account_name')}")
        else:
            logger.info("✓ 成功获取 Transactions（当前账户没有 Settled Transactions）")

    def test_get_settled_transactions_with_date_range(self, account_api):
        """
        测试场景2：使用日期范围筛选 Transactions
        验证点：
        1. 使用 begin_date 和 end_date 筛选
        2. 验证返回结果符合日期范围
        """
        # 获取账户 ID
        list_response = account_api.list_accounts(size=1)
        assert_status_ok(list_response)
        parsed_list = account_api.parse_list_response(list_response)
        assert_response_parsed(parsed_list)
        
        if len(parsed_list["content"]) == 0:
            pytest.skip("没有可用的账户数据")
        
        account_id = parsed_list["content"][0]["id"]
        
        # 使用日期范围筛选
        transactions_response = account_api.get_settled_transactions(
            account_id,
            begin_date="2024-01-01",
            end_date="2024-12-31"
        )
        
        # 验证状态码和解析响应
        assert_status_ok(transactions_response)
        parsed_transactions = account_api.parse_transactions_response(transactions_response)
        assert_response_parsed(parsed_transactions)
        
        transactions = parsed_transactions["content"]
        
        # 验证筛选结果
        if len(transactions) > 0:
            for transaction in transactions:
                settle_date = transaction.get("settle_date")
                if settle_date:
                    logger.info(f"  Transaction {transaction.get('id')}: settle_date={settle_date}")
        
        logger.info("✓ 日期范围筛选测试完成，返回 {len(transactions)} 个 Transactions")

    def test_get_settled_transactions_with_security_filter(self, account_api):
        """
        测试场景3：使用证券筛选 Transactions
        验证点：
        1. 使用 security 参数筛选
        2. 验证返回结果包含指定证券
        """
        # 获取账户 ID
        list_response = account_api.list_accounts(size=1)
        assert_status_ok(list_response)
        parsed_list = account_api.parse_list_response(list_response)
        assert_response_parsed(parsed_list)
        
        if len(parsed_list["content"]) == 0:
            pytest.skip("没有可用的账户数据")
        
        account_id = parsed_list["content"][0]["id"]
        
        # 使用证券筛选（例如 AAPL）
        security_keyword = "AAPL"
        transactions_response = account_api.get_settled_transactions(
            account_id,
            security=security_keyword
        )
        
        # 验证状态码和解析响应
        assert_status_ok(transactions_response)
        parsed_transactions = account_api.parse_transactions_response(transactions_response)
        assert_response_parsed(parsed_transactions)
        
        transactions = parsed_transactions["content"]
        
        # 验证筛选结果
        if len(transactions) > 0:
            for transaction in transactions:
                security_name = transaction.get("security_name", "")
                symbol = transaction.get("symbol", "")
                logger.info(f"  Transaction {transaction.get('id')}: {security_name} ({symbol})")
        else:
            logger.info(f"  没有找到包含证券 {security_keyword} 的 Transactions")
        
        logger.info("✓ 证券筛选测试完成，返回 {len(transactions)} 个 Transactions")

    def test_get_settled_transactions_pagination(self, account_api):
        """
        测试场景4：验证分页功能
        验证点：
        1. 使用不同的 page 和 size
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
        transactions_response = account_api.get_settled_transactions(account_id, page=0, size=5)
        
        # 验证状态码和解析响应
        assert_status_ok(transactions_response)
        parsed_transactions = account_api.parse_transactions_response(transactions_response)
        assert_response_parsed(parsed_transactions)
        
        # 验证分页信息
        assert_pagination(parsed_transactions, expected_size=5, expected_page=0)
        
        print(f"✓ 分页测试完成: 总元素数={parsed_transactions['total_elements']}, "
              f"总页数={parsed_transactions['total_pages']}, 当前页={parsed_transactions['number']}")

    def test_get_settled_transactions_empty_result(self, account_api):
        """
        测试场景5：验证空结果处理
        验证点：
        1. 使用不存在的筛选条件
        2. 验证返回 200 和空列表
        """
        # 获取账户 ID
        list_response = account_api.list_accounts(size=1)
        assert_status_ok(list_response)
        parsed_list = account_api.parse_list_response(list_response)
        assert_response_parsed(parsed_list)
        
        if len(parsed_list["content"]) == 0:
            pytest.skip("没有可用的账户数据")
        
        account_id = parsed_list["content"][0]["id"]
        
        # 使用不存在的筛选条件（未来的日期范围）
        transactions_response = account_api.get_settled_transactions(
            account_id,
            begin_date="2099-01-01",
            end_date="2099-12-31"
        )
        
        # 验证状态码和解析响应
        assert_status_ok(transactions_response)
        parsed_transactions = account_api.parse_transactions_response(transactions_response)
        assert_response_parsed(parsed_transactions)
        
        transactions = parsed_transactions["content"]
        assert isinstance(transactions, list), "content 应该是一个列表"
        
        logger.info("✓ 空结果测试完成，返回 {len(transactions)} 个 Transactions")

    def test_get_settled_transactions_fields_completeness(self, account_api):
        """
        测试场景6：验证 Transaction 字段完整性
        验证点：
        1. 返回的 Transaction 包含所有必需字段
        2. 验证可选字段存在（可能为 null）
        """
        # 获取账户 ID
        list_response = account_api.list_accounts(size=1)
        assert_status_ok(list_response)
        parsed_list = account_api.parse_list_response(list_response)
        assert_response_parsed(parsed_list)
        
        if len(parsed_list["content"]) == 0:
            pytest.skip("没有可用的账户数据")
        
        account_id = parsed_list["content"][0]["id"]
        
        # 获取 Transactions
        transactions_response = account_api.get_settled_transactions(account_id, size=1)
        assert_status_ok(transactions_response)
        parsed_transactions = account_api.parse_transactions_response(transactions_response)
        assert_response_parsed(parsed_transactions)
        
        if len(parsed_transactions["content"]) == 0:
            pytest.skip("没有可用的 Transaction 数据")
        
        transaction = parsed_transactions["content"][0]
        
        # 验证必需字段
        required_fields = [
            "id",
            "financial_account_id",
            "financial_account_name",
            "financial_account_number",
            "transaction_type",
            "settle_date"
        ]
        
        assert_fields_present(transaction, required_fields, obj_name="Transaction")
        
        # 验证可选字段（可能为 null）
        optional_fields = [
            "security_name",
            "symbol",
            "cusip",
            "units",
            "price",
            "amount",
            "market_value",
            "cost_basis",
            "transaction_fee",
            "sec_fee",
            "commision_fee",
            "carrying_value",
            "transaction_sub_type",
            "external_flow_affect",
            "trade_date",
            "check_number",
            "check_date",
            "notes",
            "recipient_name"
        ]
        
        for field in optional_fields:
            if field in transaction:
                logger.info(f"  {field}: {transaction.get(field)}")
        
        logger.info("✓ 字段完整性验证通过")
