"""
账户关联 Financial Accounts 接口测试用例
测试 GET /api/v1/cores/{core}/accounts/{account_id}/financial-accounts 接口
"""
import pytest
from api.account_api import AccountAPI


class TestAccountFinancialAccounts:
    """
    账户关联 Financial Accounts 接口测试用例集
    """

    def test_get_financial_accounts_success(self, login_session):
        """
        测试场景1：成功获取账户关联的 Financial Accounts
        验证点：
        1. 先获取有效的 account_id
        2. 调用 Financial Accounts 接口
        3. 验证状态码 200
        4. 验证返回结构符合预期（content 列表）
        """
        # 1. 初始化 API 对象
        account_api = AccountAPI(session=login_session)
        
        # 2. 获取一个有效的账户 ID
        print("\n[Step] 获取账户列表，提取账户 ID")
        list_response = account_api.list_accounts(size=1)
        assert list_response.status_code == 200, f"列表接口返回状态码错误: {list_response.status_code}"
        
        parsed_list = account_api.parse_list_response(list_response)
        assert not parsed_list.get("error"), f"列表响应解析失败: {parsed_list.get('message')}"
        
        accounts = parsed_list["content"]
        if len(accounts) == 0:
            pytest.skip("没有可用的账户数据，跳过 Financial Accounts 测试")
        
        account_id = accounts[0]["id"]
        account_number = accounts[0].get("account_number")
        print(f"  账户 ID: {account_id}, 账户编号: {account_number}")
        
        # 3. 调用 Financial Accounts 接口
        print(f"[Step] 调用 Financial Accounts 接口")
        financial_response = account_api.get_financial_accounts(account_id)
        
        # 4. 验证状态码
        print("[Step] 验证 HTTP 状态码为 200")
        assert financial_response.status_code == 200, \
            f"Financial Accounts 接口返回状态码错误: {financial_response.status_code}, 响应: {financial_response.text}"
        
        # 5. 解析响应
        print("[Step] 解析响应并验证数据结构")
        parsed_financial = account_api.parse_financial_accounts_response(financial_response)
        assert not parsed_financial.get("error"), f"响应解析失败: {parsed_financial.get('message')}"
        
        # 6. 验证数据结构
        assert "content" in parsed_financial, "响应中缺少 content 字段"
        assert isinstance(parsed_financial["content"], list), "content 字段不是列表类型"
        assert "total_elements" in parsed_financial, "响应中缺少 total_elements 字段"
        
        financial_accounts = parsed_financial["content"]
        total = parsed_financial["total_elements"]
        
        print(f"✓ 成功获取 Financial Accounts，共 {total} 个，当前页 {len(financial_accounts)} 个")
        
        # 7. 如果有数据，验证字段完整性
        if len(financial_accounts) > 0:
            print("[Step] 验证 Financial Account 对象字段")
            first_account = financial_accounts[0]
            
            # 必需字段
            required_fields = ["id", "name", "account_number", "status", "record_type"]
            for field in required_fields:
                assert field in first_account, f"Financial Account 对象缺少必需字段: {field}"
            
            print(f"  示例 Financial Account:")
            print(f"    ID: {first_account.get('id')}")
            print(f"    Name: {first_account.get('name')}")
            print(f"    Account Number: {first_account.get('account_number')}")
            print(f"    Status: {first_account.get('status')}")
            print(f"    Sub Type: {first_account.get('sub_type')}")

    def test_get_financial_accounts_with_filters(self, login_session):
        """
        测试场景2：使用筛选条件获取 Financial Accounts
        验证点：
        1. 使用 status 筛选
        2. 验证返回结果符合筛选条件
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
        
        # 3. 使用筛选条件
        filter_status = "Pending"
        print(f"[Step] 使用筛选条件 status={filter_status}")
        financial_response = account_api.get_financial_accounts(
            account_id,
            status=filter_status
        )
        
        # 4. 验证
        print("[Step] 验证响应")
        assert financial_response.status_code == 200, \
            f"接口返回状态码错误: {financial_response.status_code}"
        
        parsed_financial = account_api.parse_financial_accounts_response(financial_response)
        assert not parsed_financial.get("error"), f"响应解析失败: {parsed_financial.get('message')}"
        
        financial_accounts = parsed_financial["content"]
        
        # 如果有数据，验证筛选逻辑
        if len(financial_accounts) > 0:
            for account in financial_accounts:
                actual_status = account.get("status")
                if actual_status is not None:
                    assert actual_status == filter_status, \
                        f"Financial Account 状态不匹配，期望 {filter_status}，实际 {actual_status}"
            print(f"✓ 筛选成功，找到 {len(financial_accounts)} 个状态为 {filter_status} 的 Financial Accounts")
        else:
            print(f"⚠ 未找到状态为 {filter_status} 的 Financial Accounts（可能是正常情况）")

    def test_get_financial_accounts_pagination(self, login_session):
        """
        测试场景3：验证分页功能
        验证点：
        1. 使用不同的 page 和 size 参数
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
        page_size = 5
        print(f"[Step] 请求第 1 页，每页 {page_size} 条数据")
        financial_response = account_api.get_financial_accounts(
            account_id,
            page=0,
            size=page_size
        )
        
        # 4. 验证分页信息
        print("[Step] 验证分页参数生效")
        assert financial_response.status_code == 200, \
            f"接口返回状态码错误: {financial_response.status_code}"
        
        parsed_financial = account_api.parse_financial_accounts_response(financial_response)
        assert not parsed_financial.get("error"), f"响应解析失败: {parsed_financial.get('message')}"
        
        # 验证返回的数据量不超过指定大小
        assert len(parsed_financial["content"]) <= page_size, \
            f"返回的数据量 {len(parsed_financial['content'])} 超过了指定的每页大小 {page_size}"
        
        # 验证分页信息
        assert parsed_financial["size"] == page_size, f"分页信息中的 size 不正确"
        
        print(f"✓ 分页验证成功，请求 {page_size} 条，实际返回 {len(parsed_financial['content'])} 条")

    def test_get_financial_accounts_empty_result(self, login_session):
        """
        测试场景4：验证空结果处理
        验证点：
        1. 使用不存在的筛选条件
        2. 验证接口返回 200 和空列表
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
        
        # 3. 使用不太可能存在的筛选条件
        print("[Step] 使用不存在的 account_number 查询")
        financial_response = account_api.get_financial_accounts(
            account_id,
            account_number="NONEXISTENT-999999"
        )
        
        # 4. 验证空结果
        print("[Step] 验证返回空列表")
        assert financial_response.status_code == 200, \
            f"接口返回状态码错误: {financial_response.status_code}"
        
        parsed_financial = account_api.parse_financial_accounts_response(financial_response)
        assert not parsed_financial.get("error"), f"响应解析失败: {parsed_financial.get('message')}"
        
        # 验证返回空列表
        assert len(parsed_financial["content"]) == 0, "期望返回空列表，但实际有数据"
        
        print("✓ 空结果验证成功，接口正确返回空列表")

    def test_get_financial_accounts_invalid_account_id(self, login_session):
        """
        测试场景5：使用无效的 account_id
        验证点：
        1. 接口返回错误状态码
        """
        # 1. 初始化 API 对象
        account_api = AccountAPI(session=login_session)
        
        # 2. 使用无效的 account_id
        invalid_id = "INVALID_ACCOUNT_ID_999999"
        print(f"\n[Step] 使用无效的账户 ID: {invalid_id}")
        financial_response = account_api.get_financial_accounts(invalid_id)
        
        # 3. 验证返回错误状态码
        print("[Step] 验证返回非 200 状态码")
        # 注意：某些 API 可能对无效 ID 返回 200 + 空列表，这里根据实际情况调整
        # 如果 API 返回 404，则断言非 200；如果返回 200 + 空列表，则验证空列表
        if financial_response.status_code == 200:
            parsed_financial = account_api.parse_financial_accounts_response(financial_response)
            assert len(parsed_financial["content"]) == 0, \
                "使用无效 ID 应该返回空列表"
            print(f"✓ 使用无效 ID 返回 200 和空列表")
        else:
            print(f"✓ 使用无效 ID 正确返回错误状态码: {financial_response.status_code}")
