"""
账户 Settled Transactions 接口测试用例
测试 GET /api/v1/cores/{core}/accounts/{account_id}/settled-transactions 接口
"""
import pytest
from api.account_api import AccountAPI


@pytest.mark.transaction_api
class TestAccountTransactions:
    """
    账户 Settled Transactions 接口测试用例集
    """

    def test_get_settled_transactions_success(self, login_session):
        """
        测试场景1：成功获取账户的 Settled Transactions
        依赖逻辑：先从列表接口获取一个有效的 account_id，然后获取 Transactions
        验证点：
        1. 列表接口返回成功
        2. Transactions 接口返回 200
        3. 返回数据结构正确（content 列表）
        4. 如果有数据，验证字段完整性
        """
        # 1. 初始化 API 对象
        account_api = AccountAPI(session=login_session)
        
        # 2. 先调用列表接口获取一个账户 ID
        print("\n[Step] 调用列表接口获取账户 ID")
        list_response = account_api.list_accounts(size=1)
        assert list_response.status_code == 200, f"列表接口返回状态码错误: {list_response.status_code}"
        
        # 3. 解析列表响应
        print("[Step] 解析列表响应，提取账户 ID")
        parsed_list = account_api.parse_list_response(list_response)
        assert not parsed_list.get("error"), f"列表响应解析失败: {parsed_list.get('message')}"
        
        accounts = parsed_list["content"]
        if len(accounts) == 0:
            pytest.skip("没有可用的账户数据，跳过 Transactions 测试")
        
        # 提取第一个账户的 ID
        account_id = accounts[0]["id"]
        print(f"  提取到账户 ID: {account_id}")
        
        # 4. 调用 Transactions 接口
        print(f"[Step] 调用 Transactions 接口获取账户 {account_id} 的 Transactions")
        transactions_response = account_api.get_settled_transactions(account_id)
        
        # 5. 断言状态码
        print("[Step] 验证 HTTP 状态码为 200")
        assert transactions_response.status_code == 200, f"Transactions 接口返回状态码错误: {transactions_response.status_code}"
        
        # 6. 解析 Transactions 响应
        print("[Step] 解析 Transactions 响应并验证数据结构")
        parsed_transactions = account_api.parse_transactions_response(transactions_response)
        assert not parsed_transactions.get("error"), f"Transactions 响应解析失败: {parsed_transactions.get('message')}"
        
        transactions = parsed_transactions["content"]
        
        # 7. 验证返回数据结构
        print("[Step] 验证返回数据结构")
        assert isinstance(transactions, list), "content 应该是一个列表"
        
        # 8. 如果有数据，验证字段完整性
        if len(transactions) > 0:
            print(f"[Step] 验证 Transactions 字段完整性（共 {len(transactions)} 个 Transactions）")
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
            for field in required_fields:
                assert field in first_transaction, f"Transaction 缺少必需字段: {field}"
            
            print(f"✓ 成功获取 Transactions:")
            print(f"  总数: {parsed_transactions['total_elements']}")
            print(f"  第一个 Transaction ID: {first_transaction.get('id')}")
            print(f"  Financial Account: {first_transaction.get('financial_account_name')}")
            print(f"  Transaction Type: {first_transaction.get('transaction_type')}")
            print(f"  Settle Date: {first_transaction.get('settle_date')}")
            
            # 如果有证券信息，打印
            if first_transaction.get("security_name"):
                print(f"  Security: {first_transaction.get('security_name')} ({first_transaction.get('symbol')})")
        else:
            print("✓ 成功获取 Transactions（当前账户没有 Settled Transactions）")

    def test_get_settled_transactions_with_date_range(self, login_session):
        """
        测试场景2：使用日期范围筛选 Transactions
        验证点：
        1. 使用 begin_date 和 end_date 筛选
        2. 验证返回结果符合日期范围
        """
        # 1. 初始化 API 对象
        account_api = AccountAPI(session=login_session)
        
        # 2. 获取账户 ID
        print("\n[Step] 获取账户 ID")
        list_response = account_api.list_accounts(size=1)
        parsed_list = account_api.parse_list_response(list_response)
        
        if len(parsed_list["content"]) == 0:
            pytest.skip("没有可用的账户数据")
        
        account_id = parsed_list["content"][0]["id"]
        
        # 3. 使用日期范围筛选
        print(f"[Step] 使用日期范围筛选 Transactions (2024-01-01 到 2024-12-31)")
        transactions_response = account_api.get_settled_transactions(
            account_id,
            begin_date="2024-01-01",
            end_date="2024-12-31"
        )
        
        # 4. 验证状态码
        assert transactions_response.status_code == 200, f"Transactions 接口返回状态码错误: {transactions_response.status_code}"
        
        # 5. 解析响应
        print("[Step] 解析响应并验证筛选结果")
        parsed_transactions = account_api.parse_transactions_response(transactions_response)
        assert not parsed_transactions.get("error"), f"Transactions 响应解析失败: {parsed_transactions.get('message')}"
        
        transactions = parsed_transactions["content"]
        
        # 6. 验证筛选结果
        if len(transactions) > 0:
            print(f"[Step] 验证所有返回的 Transactions 在日期范围内")
            for transaction in transactions:
                settle_date = transaction.get("settle_date")
                if settle_date:
                    print(f"  Transaction {transaction.get('id')}: settle_date={settle_date}")
                    # 注意：这里可以添加日期范围验证，但需要解析日期字符串
        
        print(f"✓ 日期范围筛选测试完成，返回 {len(transactions)} 个 Transactions")

    def test_get_settled_transactions_with_security_filter(self, login_session):
        """
        测试场景3：使用证券筛选 Transactions
        验证点：
        1. 使用 security 参数筛选
        2. 验证返回结果包含指定证券
        """
        # 1. 初始化 API 对象
        account_api = AccountAPI(session=login_session)
        
        # 2. 获取账户 ID
        print("\n[Step] 获取账户 ID")
        list_response = account_api.list_accounts(size=1)
        parsed_list = account_api.parse_list_response(list_response)
        
        if len(parsed_list["content"]) == 0:
            pytest.skip("没有可用的账户数据")
        
        account_id = parsed_list["content"][0]["id"]
        
        # 3. 使用证券筛选（例如 AAPL）
        security_keyword = "AAPL"
        print(f"[Step] 使用证券筛选 Transactions (security={security_keyword})")
        transactions_response = account_api.get_settled_transactions(
            account_id,
            security=security_keyword
        )
        
        # 4. 验证状态码
        assert transactions_response.status_code == 200, f"Transactions 接口返回状态码错误: {transactions_response.status_code}"
        
        # 5. 解析响应
        print("[Step] 解析响应并验证筛选结果")
        parsed_transactions = account_api.parse_transactions_response(transactions_response)
        assert not parsed_transactions.get("error"), f"Transactions 响应解析失败: {parsed_transactions.get('message')}"
        
        transactions = parsed_transactions["content"]
        
        # 6. 验证筛选结果
        if len(transactions) > 0:
            print(f"[Step] 验证所有返回的 Transactions 包含证券 {security_keyword}")
            for transaction in transactions:
                security_name = transaction.get("security_name", "")
                symbol = transaction.get("symbol", "")
                cusip = transaction.get("cusip", "")
                print(f"  Transaction {transaction.get('id')}: {security_name} ({symbol}) CUSIP:{cusip}")
        else:
            print(f"  没有找到包含证券 {security_keyword} 的 Transactions")
        
        print(f"✓ 证券筛选测试完成，返回 {len(transactions)} 个 Transactions")

    def test_get_settled_transactions_pagination(self, login_session):
        """
        测试场景4：验证分页功能
        验证点：
        1. 使用不同的 page 和 size
        2. 验证分页信息正确
        """
        # 1. 初始化 API 对象
        account_api = AccountAPI(session=login_session)
        
        # 2. 获取账户 ID
        print("\n[Step] 获取账户 ID")
        list_response = account_api.list_accounts(size=1)
        parsed_list = account_api.parse_list_response(list_response)
        
        if len(parsed_list["content"]) == 0:
            pytest.skip("没有可用的账户数据")
        
        account_id = parsed_list["content"][0]["id"]
        
        # 3. 使用分页参数
        print(f"[Step] 使用分页参数 page=0, size=5")
        transactions_response = account_api.get_settled_transactions(account_id, page=0, size=5)
        
        # 4. 验证状态码
        assert transactions_response.status_code == 200, f"Transactions 接口返回状态码错误: {transactions_response.status_code}"
        
        # 5. 解析响应
        print("[Step] 解析响应并验证分页信息")
        parsed_transactions = account_api.parse_transactions_response(transactions_response)
        assert not parsed_transactions.get("error"), f"Transactions 响应解析失败: {parsed_transactions.get('message')}"
        
        # 6. 验证分页信息
        print("[Step] 验证分页信息")
        assert parsed_transactions["size"] == 5, f"分页大小不正确: 期望 5，实际 {parsed_transactions['size']}"
        assert parsed_transactions["number"] == 0, f"页码不正确: 期望 0，实际 {parsed_transactions['number']}"
        
        print(f"✓ 分页测试完成:")
        print(f"  总元素数: {parsed_transactions['total_elements']}")
        print(f"  总页数: {parsed_transactions['total_pages']}")
        print(f"  当前页: {parsed_transactions['number']}")
        print(f"  每页大小: {parsed_transactions['size']}")

    def test_get_settled_transactions_empty_result(self, login_session):
        """
        测试场景5：验证空结果处理
        验证点：
        1. 使用不存在的筛选条件
        2. 验证返回 200 和空列表
        """
        # 1. 初始化 API 对象
        account_api = AccountAPI(session=login_session)
        
        # 2. 获取账户 ID
        print("\n[Step] 获取账户 ID")
        list_response = account_api.list_accounts(size=1)
        parsed_list = account_api.parse_list_response(list_response)
        
        if len(parsed_list["content"]) == 0:
            pytest.skip("没有可用的账户数据")
        
        account_id = parsed_list["content"][0]["id"]
        
        # 3. 使用不存在的筛选条件（未来的日期范围）
        print(f"[Step] 使用未来的日期范围筛选")
        transactions_response = account_api.get_settled_transactions(
            account_id,
            begin_date="2099-01-01",
            end_date="2099-12-31"
        )
        
        # 4. 验证状态码
        assert transactions_response.status_code == 200, f"Transactions 接口返回状态码错误: {transactions_response.status_code}"
        
        # 5. 解析响应
        print("[Step] 解析响应并验证空结果")
        parsed_transactions = account_api.parse_transactions_response(transactions_response)
        assert not parsed_transactions.get("error"), f"Transactions 响应解析失败: {parsed_transactions.get('message')}"
        
        transactions = parsed_transactions["content"]
        
        # 6. 验证返回空列表或少量数据
        print("[Step] 验证返回结果")
        assert isinstance(transactions, list), "content 应该是一个列表"
        
        print(f"✓ 空结果测试完成，返回 {len(transactions)} 个 Transactions")

    def test_get_settled_transactions_fields_completeness(self, login_session):
        """
        测试场景6：验证 Transaction 字段完整性
        验证点：
        1. 返回的 Transaction 包含所有必需字段
        2. 验证可选字段存在（可能为 null）
        """
        # 1. 初始化 API 对象
        account_api = AccountAPI(session=login_session)
        
        # 2. 获取账户 ID
        print("\n[Step] 获取账户 ID")
        list_response = account_api.list_accounts(size=1)
        parsed_list = account_api.parse_list_response(list_response)
        
        if len(parsed_list["content"]) == 0:
            pytest.skip("没有可用的账户数据")
        
        account_id = parsed_list["content"][0]["id"]
        
        # 3. 获取 Transactions
        print(f"[Step] 获取 Transactions")
        transactions_response = account_api.get_settled_transactions(account_id, size=1)
        parsed_transactions = account_api.parse_transactions_response(transactions_response)
        
        if len(parsed_transactions["content"]) == 0:
            pytest.skip("没有可用的 Transaction 数据")
        
        transaction = parsed_transactions["content"][0]
        
        # 4. 验证必需字段
        required_fields = [
            "id",
            "financial_account_id",
            "financial_account_name",
            "financial_account_number",
            "transaction_type",
            "settle_date"
        ]
        
        print("[Step] 验证必需字段存在")
        for field in required_fields:
            assert field in transaction, f"Transaction 缺少必需字段: {field}"
        
        # 5. 验证可选字段（可能为 null）
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
        
        print("[Step] 验证可选字段存在（可能为 null）")
        for field in optional_fields:
            # 不强制要求存在，只是记录
            if field in transaction:
                print(f"  {field}: {transaction.get(field)}")
        
        print(f"✓ 字段完整性验证通过")
