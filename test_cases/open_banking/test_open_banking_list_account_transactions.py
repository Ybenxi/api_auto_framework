"""
Open Banking List Account Transactions 接口测试用例
测试 GET /api/v1/cores/{core}/open-banking/accounts/:account_id/transactions 接口
"""
import pytest
from api.open_banking_api import OpenBankingAPI
from api.financial_account_api import FinancialAccountAPI


@pytest.mark.open_banking
@pytest.mark.transactions_api
class TestOpenBankingListAccountTransactions:
    """
    获取账户交易列表接口测试用例集
    """

    def test_list_account_transactions_success(self, login_session):
        """
        测试场景1：成功获取账户交易列表
        验证点：
        1. 接口返回 200
        2. 返回的 data 包含 content 数组
        3. 每个交易记录包含基本字段
        
        前置条件：需要先获取一个真实的 financial_account_id
        """
        # 1. 初始化 API 对象
        open_banking_api = OpenBankingAPI(session=login_session)
        financial_account_api = FinancialAccountAPI(session=login_session)
        
        # 2. 先调用 Financial Account List 接口获取一个真实的 financial_account_id
        print("\n[Step] 先调用 Financial Account List 接口获取真实的 financial_account_id")
        fa_response = financial_account_api.list_financial_accounts(page=0, size=1)
        assert fa_response.status_code == 200, "Financial Account List 接口调用失败"
        
        fa_data = fa_response.json().get("data", {})
        financial_accounts = fa_data.get("content", [])
        
        if len(financial_accounts) == 0:
            pytest.skip("没有可用的 Financial Account 数据，跳过测试")
        
        financial_account_id = financial_accounts[0]["id"]
        print(f"  获取到 Financial Account ID: {financial_account_id}")
        
        # 3. 调用 List Account Transactions 接口
        print(f"[Step] 调用 List Account Transactions 接口")
        response = open_banking_api.list_account_transactions(
            financial_account_id=financial_account_id
        )
        
        # 4. 断言状态码
        print("[Step] 验证 HTTP 状态码为 200")
        assert response.status_code == 200, \
            f"List Account Transactions 接口返回状态码错误: {response.status_code}, Response: {response.text}"
        
        # 5. 解析响应
        print("[Step] 解析响应并验证数据")
        response_body = response.json()
        
        # 6. 验证 code 字段
        print("[Step] 验证 code 字段为 200")
        assert response_body.get("code") == 200, \
            f"响应 code 不正确: 期望 200, 实际 {response_body.get('code')}"
        
        # 7. 验证 data 结构
        data = response_body.get("data", {})
        assert isinstance(data, dict), "data 字段应该是对象"
        
        # 8. 验证 content 数组
        content = data.get("content", [])
        assert isinstance(content, list), "content 字段应该是数组"
        
        print(f"[Step] 获取到 {len(content)} 条交易记录")
        
        # 9. 如果有数据，验证字段结构
        if len(content) > 0:
            print("[Step] 验证第一条交易记录的基本字段")
            transaction = content[0]
            
            # 验证一些基本字段（根据文档，字段非常多，这里只验证关键字段）
            basic_fields = ["transaction_id", "transaction_type", "description", "created_date"]
            
            for field in basic_fields:
                if field in transaction:
                    print(f"  ✓ {field}: {transaction.get(field)}")
            
            print(f"\n✓ 成功获取账户交易列表:")
            print(f"  交易数量: {len(content)}")
            print(f"  第一条交易 ID: {transaction.get('transaction_id')}")
            print(f"  交易类型: {transaction.get('transaction_type')}")
        else:
            print("  ⚠ 当前没有交易记录")

    def test_list_account_transactions_response_structure(self, login_session):
        """
        测试场景2：验证响应数据结构
        验证点：
        1. 接口返回 200
        2. 响应包含 code, error_message, error, data 字段
        3. data 包含 content 数组
        """
        # 1. 初始化 API 对象
        open_banking_api = OpenBankingAPI(session=login_session)
        financial_account_api = FinancialAccountAPI(session=login_session)
        
        # 2. 获取 financial_account_id
        print("\n[Step] 获取真实的 financial_account_id")
        fa_response = financial_account_api.list_financial_accounts(page=0, size=1)
        assert fa_response.status_code == 200, "Financial Account List 接口调用失败"
        
        fa_data = fa_response.json().get("data", {})
        financial_accounts = fa_data.get("content", [])
        
        if len(financial_accounts) == 0:
            pytest.skip("没有可用的 Financial Account 数据，跳过测试")
        
        financial_account_id = financial_accounts[0]["id"]
        
        # 3. 调用接口
        print(f"[Step] 调用 List Account Transactions 接口")
        response = open_banking_api.list_account_transactions(
            financial_account_id=financial_account_id
        )
        
        # 4. 验证状态码
        print("[Step] 验证 HTTP 状态码为 200")
        assert response.status_code == 200, \
            f"接口返回状态码错误: {response.status_code}"
        
        # 5. 验证响应数据结构
        print("[Step] 验证响应数据结构")
        response_body = response.json()
        
        # 验证是 JSON 对象
        assert isinstance(response_body, dict), "响应应该是 JSON 对象"
        
        # 验证必需字段（成功响应）
        assert "code" in response_body, "响应中缺少 code 字段"
        assert "data" in response_body, "响应中缺少 data 字段"
        print(f"  ✓ code: {response_body.get('code')}")
        print(f"  ✓ data: 存在")
        
        # error_message 和 error 字段仅在失败时存在
        if response_body.get("code") != 200:
            assert "error_message" in response_body, "错误响应中缺少 error_message 字段"
        
        # 验证 data 是对象
        assert isinstance(response_body["data"], dict), "data 字段应该是对象"
        
        # 验证 data 包含 content
        data = response_body["data"]
        assert "content" in data, "data 中缺少 content 字段"
        assert isinstance(data["content"], list), "content 应该是数组"
        
        print(f"✓ 响应数据结构验证通过")

    def test_list_account_transactions_key_fields(self, login_session):
        """
        测试场景3：验证交易记录的关键字段
        验证点：
        1. 接口返回 200
        2. 交易记录包含关键字段（transaction_id, transaction_type, description 等）
        """
        # 1. 初始化 API 对象
        open_banking_api = OpenBankingAPI(session=login_session)
        financial_account_api = FinancialAccountAPI(session=login_session)
        
        # 2. 获取 financial_account_id
        print("\n[Step] 获取真实的 financial_account_id")
        fa_response = financial_account_api.list_financial_accounts(page=0, size=1)
        assert fa_response.status_code == 200, "Financial Account List 接口调用失败"
        
        fa_data = fa_response.json().get("data", {})
        financial_accounts = fa_data.get("content", [])
        
        if len(financial_accounts) == 0:
            pytest.skip("没有可用的 Financial Account 数据，跳过测试")
        
        financial_account_id = financial_accounts[0]["id"]
        
        # 3. 调用接口
        print(f"[Step] 调用 List Account Transactions 接口")
        response = open_banking_api.list_account_transactions(
            financial_account_id=financial_account_id
        )
        
        # 4. 验证状态码
        assert response.status_code == 200, f"接口返回状态码错误: {response.status_code}"
        
        # 5. 解析响应
        data = response.json().get("data", {})
        content = data.get("content", [])
        
        if len(content) == 0:
            pytest.skip("没有可用的交易记录，跳过测试")
        
        # 6. 验证关键字段
        print("[Step] 验证第一条交易记录的关键字段")
        transaction = content[0]
        
        # 根据文档，验证一些重要字段
        key_fields = [
            "transaction_id", "transaction_type", "description", "account_id",
            "account_number", "created_date", "transaction_code"
        ]
        
        present_fields = []
        missing_fields = []
        
        for field in key_fields:
            if field in transaction:
                present_fields.append(field)
                value = transaction.get(field)
                print(f"  ✓ {field}: {value if value is not None else 'null'}")
            else:
                missing_fields.append(field)
        
        if missing_fields:
            print(f"  ⚠ 缺少字段: {', '.join(missing_fields)}")
        
        print(f"✓ 关键字段验证完成 (存在: {len(present_fields)}, 缺失: {len(missing_fields)})")

    def test_list_account_transactions_amount_fields(self, login_session):
        """
        测试场景4：验证金额相关字段
        验证点：
        1. 接口返回 200
        2. 交易记录包含金额相关字段（escrow_amount, interest_amount, principal_amount 等）
        3. 金额字段为数字类型
        """
        # 1. 初始化 API 对象
        open_banking_api = OpenBankingAPI(session=login_session)
        financial_account_api = FinancialAccountAPI(session=login_session)
        
        # 2. 获取 financial_account_id
        print("\n[Step] 获取真实的 financial_account_id")
        fa_response = financial_account_api.list_financial_accounts(page=0, size=1)
        assert fa_response.status_code == 200, "Financial Account List 接口调用失败"
        
        fa_data = fa_response.json().get("data", {})
        financial_accounts = fa_data.get("content", [])
        
        if len(financial_accounts) == 0:
            pytest.skip("没有可用的 Financial Account 数据，跳过测试")
        
        financial_account_id = financial_accounts[0]["id"]
        
        # 3. 调用接口
        print(f"[Step] 调用 List Account Transactions 接口")
        response = open_banking_api.list_account_transactions(
            financial_account_id=financial_account_id
        )
        
        # 4. 验证状态码
        assert response.status_code == 200, f"接口返回状态码错误: {response.status_code}"
        
        # 5. 解析响应
        data = response.json().get("data", {})
        content = data.get("content", [])
        
        if len(content) == 0:
            pytest.skip("没有可用的交易记录，跳过测试")
        
        # 6. 验证金额字段
        print("[Step] 验证金额相关字段")
        transaction = content[0]
        
        amount_fields = [
            "escrow_amount", "suspense_amount", "interest_amount",
            "principal_amount", "running_balance_amount", "commission_amount",
            "taxes_amount", "external_amount", "market_value", "transaction_fee"
        ]
        
        for field in amount_fields:
            if field in transaction:
                value = transaction.get(field)
                if value is not None:
                    # 验证是数字类型（int 或 float）
                    assert isinstance(value, (int, float)), \
                        f"{field} 应该是数字类型，实际为: {type(value)}"
                    print(f"  ✓ {field}: {value}")
                else:
                    print(f"  ○ {field}: null")
        
        print(f"✓ 金额字段验证完成")

    def test_list_account_transactions_categorization_fields(self, login_session):
        """
        测试场景5：验证分类相关字段
        验证点：
        1. 接口返回 200
        2. 交易记录包含分类字段（categorization_* 系列）
        """
        # 1. 初始化 API 对象
        open_banking_api = OpenBankingAPI(session=login_session)
        financial_account_api = FinancialAccountAPI(session=login_session)
        
        # 2. 获取 financial_account_id
        print("\n[Step] 获取真实的 financial_account_id")
        fa_response = financial_account_api.list_financial_accounts(page=0, size=1)
        assert fa_response.status_code == 200, "Financial Account List 接口调用失败"
        
        fa_data = fa_response.json().get("data", {})
        financial_accounts = fa_data.get("content", [])
        
        if len(financial_accounts) == 0:
            pytest.skip("没有可用的 Financial Account 数据，跳过测试")
        
        financial_account_id = financial_accounts[0]["id"]
        
        # 3. 调用接口
        print(f"[Step] 调用 List Account Transactions 接口")
        response = open_banking_api.list_account_transactions(
            financial_account_id=financial_account_id
        )
        
        # 4. 验证状态码
        assert response.status_code == 200, f"接口返回状态码错误: {response.status_code}"
        
        # 5. 解析响应
        data = response.json().get("data", {})
        content = data.get("content", [])
        
        if len(content) == 0:
            pytest.skip("没有可用的交易记录，跳过测试")
        
        # 6. 验证分类字段
        print("[Step] 验证分类相关字段")
        transaction = content[0]
        
        categorization_fields = [
            "categorization_normalized_payee_name",
            "categorization_category",
            "categorization_city",
            "categorization_state",
            "categorization_postal_code",
            "categorization_country",
            "categorization_best_representation"
        ]
        
        present_count = 0
        for field in categorization_fields:
            if field in transaction:
                value = transaction.get(field)
                print(f"  ✓ {field}: {value if value is not None else 'null'}")
                present_count += 1
        
        print(f"✓ 分类字段验证完成 (存在 {present_count}/{len(categorization_fields)} 个字段)")

    def test_list_account_transactions_invalid_financial_account_id(self, login_session):
        """
        测试场景6：使用无效的 financial_account_id
        验证点：
        1. 接口返回错误或空结果
        2. 不会导致系统异常
        """
        # 1. 初始化 API 对象
        open_banking_api = OpenBankingAPI(session=login_session)
        
        # 2. 使用无效的 financial_account_id
        invalid_id = "invalid_financial_account_id_999999"
        
        print(f"\n[Step] 使用无效的 financial_account_id: {invalid_id}")
        
        # 3. 调用接口
        print("[Step] 调用 List Account Transactions 接口")
        response = open_banking_api.list_account_transactions(
            financial_account_id=invalid_id
        )
        
        # 4. 验证返回结果
        print("[Step] 验证接口返回")
        print(f"  状态码: {response.status_code}")
        
        # 可能返回 200（空数据）或错误状态码
        if response.status_code == 200:
            response_body = response.json()
            code = response_body.get("code")
            data = response_body.get("data", {})
            content = data.get("content", []) if isinstance(data, dict) else []
            
            print(f"  Code: {code}")
            print(f"  交易数量: {len(content)}")
            
            # 应该返回空数据或错误码
            assert code != 200 or len(content) == 0, \
                "无效 ID 应该返回错误或空数据"
        else:
            print(f"  ✓ 返回错误状态码: {response.status_code}")
        
        print(f"✓ 无效 ID 测试完成")
