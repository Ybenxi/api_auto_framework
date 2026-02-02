"""
账户管理接口测试用例
覆盖多种测试场景，包括基础查询、筛选、分页、枚举类型等
"""
import pytest
from api.account_api import AccountAPI
from data.enums import BusinessEntityType, AccountStatus


class TestAccountList:
    """
    账户列表接口测试用例集
    """

    def test_list_accounts_basic(self, login_session):
        """
        测试场景1：基础列表查询 - 验证接口可用性
        验证点：
        1. HTTP 状态码为 200
        2. 响应中包含 content 字段
        3. content 是一个列表
        4. 响应结构完整（包含分页信息）
        """
        # 1. 初始化 API 对象
        account_api = AccountAPI(session=login_session)
        
        # 2. 调用接口
        print("\n[Step] 调用账户列表接口（无筛选条件）")
        response = account_api.list_accounts()
        
        # 3. 断言 HTTP 状态码
        print("[Step] 验证 HTTP 状态码为 200")
        assert response.status_code == 200, f"接口返回状态码错误: {response.status_code}"
        
        # 4. 解析响应
        print("[Step] 解析响应数据")
        parsed = account_api.parse_list_response(response)
        assert not parsed.get("error"), f"响应解析失败: {parsed.get('message')}"
        
        # 5. 验证数据结构
        print("[Step] 验证响应数据结构")
        assert "content" in parsed, "响应中缺少 content 字段"
        assert isinstance(parsed["content"], list), "content 字段不是列表类型"
        assert "total_elements" in parsed, "响应中缺少 total_elements 字段"
        
        # 打印统计信息
        print(f"✓ 成功获取到 {len(parsed['content'])} 个账户，总计 {parsed['total_elements']} 个")

    @pytest.mark.parametrize("search_name", ["Example", "Test", "Account"])
    def test_list_accounts_filter_by_name(self, login_session, search_name):
        """
        测试场景2：名称筛选查询 - 验证筛选逻辑
        验证点：
        1. 接口返回成功
        2. 返回的所有账户名称都包含搜索关键词（不区分大小写）
        """
        # 1. 初始化 API 对象
        account_api = AccountAPI(session=login_session)
        
        # 2. 调用接口并传入筛选参数
        print(f"\n[Step] 调用接口并筛选名称包含 '{search_name}' 的账户")
        response = account_api.list_accounts(name=search_name)
        
        # 3. 断言状态码
        print("[Step] 验证 HTTP 状态码为 200")
        assert response.status_code == 200, f"接口返回状态码错误: {response.status_code}"
        
        # 4. 解析响应
        print("[Step] 解析响应并验证筛选结果")
        parsed = account_api.parse_list_response(response)
        assert not parsed.get("error"), f"响应解析失败: {parsed.get('message')}"
        
        accounts = parsed["content"]
        
        # 如果返回了数据，验证筛选逻辑
        if len(accounts) > 0:
            for account in accounts:
                account_name = account.get("account_name", "")
                assert search_name.lower() in account_name.lower(), \
                    f"账户名称 '{account_name}' 不包含搜索关键词 '{search_name}'"
            print(f"✓ 筛选成功，找到 {len(accounts)} 个包含 '{search_name}' 的账户")
        else:
            print(f"⚠ 未找到包含 '{search_name}' 的账户（可能是正常情况）")

    def test_list_accounts_filter_by_entity_type(self, login_session):
        """
        测试场景3：枚举类型筛选 - 使用 BusinessEntityType 枚举
        验证点：
        1. 枚举类可以正常传递给 API
        2. 返回的所有账户的 business_entity_type 都是 LLC
        """
        # 1. 初始化 API 对象
        account_api = AccountAPI(session=login_session)
        
        # 2. 使用枚举类型调用接口
        print(f"\n[Step] 使用枚举类型 BusinessEntityType.LLC 筛选账户")
        response = account_api.list_accounts(business_entity_type=BusinessEntityType.LLC)
        
        # 3. 断言状态码
        print("[Step] 验证 HTTP 状态码为 200")
        assert response.status_code == 200, f"接口返回状态码错误: {response.status_code}"
        
        # 4. 解析响应并验证
        print("[Step] 验证返回的账户类型都是 LLC")
        parsed = account_api.parse_list_response(response)
        assert not parsed.get("error"), f"响应解析失败: {parsed.get('message')}"
        
        accounts = parsed["content"]
        
        if len(accounts) > 0:
            for account in accounts:
                entity_type = account.get("business_entity_type")
                # 注意：API 可能返回 null，这里只验证非 null 的情况
                if entity_type is not None:
                    assert entity_type == BusinessEntityType.LLC.value, \
                        f"账户 {account.get('account_number')} 的类型是 '{entity_type}'，不是 'LLC'"
            print(f"✓ 筛选成功，找到 {len(accounts)} 个 LLC 类型的账户")
        else:
            print("⚠ 未找到 LLC 类型的账户（可能是正常情况）")

    def test_list_accounts_multiple_filters(self, login_session):
        """
        测试场景4：多条件组合筛选
        验证点：
        1. 可以同时传递多个筛选参数
        2. 接口正常返回结果
        """
        # 1. 初始化 API 对象
        account_api = AccountAPI(session=login_session)
        
        # 2. 使用多个筛选条件
        print("\n[Step] 使用多个筛选条件查询账户")
        response = account_api.list_accounts(
            status=AccountStatus.ACTIVE,
            business_entity_type=BusinessEntityType.LLC,
            name="Example"
        )
        
        # 3. 断言状态码
        print("[Step] 验证 HTTP 状态码为 200")
        assert response.status_code == 200, f"接口返回状态码错误: {response.status_code}"
        
        # 4. 解析响应
        print("[Step] 解析响应数据")
        parsed = account_api.parse_list_response(response)
        assert not parsed.get("error"), f"响应解析失败: {parsed.get('message')}"
        
        print(f"✓ 组合筛选成功，找到 {len(parsed['content'])} 个符合条件的账户")

    @pytest.mark.parametrize("page_size", [5, 10, 20])
    def test_list_accounts_pagination(self, login_session, page_size):
        """
        测试场景5：分页功能验证
        验证点：
        1. 可以指定每页大小
        2. 返回的数据量不超过指定大小
        3. 分页信息正确
        """
        # 1. 初始化 API 对象
        account_api = AccountAPI(session=login_session)
        
        # 2. 使用分页参数
        print(f"\n[Step] 请求第 1 页，每页 {page_size} 条数据")
        response = account_api.list_accounts(page=0, size=page_size)
        
        # 3. 断言状态码
        print("[Step] 验证 HTTP 状态码为 200")
        assert response.status_code == 200, f"接口返回状态码错误: {response.status_code}"
        
        # 4. 验证分页信息
        print("[Step] 验证分页参数生效")
        parsed = account_api.parse_list_response(response)
        assert not parsed.get("error"), f"响应解析失败: {parsed.get('message')}"
        
        # 验证返回的数据量不超过指定大小
        assert len(parsed["content"]) <= page_size, \
            f"返回的数据量 {len(parsed['content'])} 超过了指定的每页大小 {page_size}"
        
        # 验证分页信息
        assert parsed["size"] == page_size, f"分页信息中的 size 不正确"
        
        print(f"✓ 分页验证成功，请求 {page_size} 条，实际返回 {len(parsed['content'])} 条")

    @pytest.mark.parametrize("account_status", [
        AccountStatus.ACTIVE,
        AccountStatus.INACTIVE,
        AccountStatus.PENDING
    ])
    def test_list_accounts_filter_by_status(self, login_session, account_status):
        """
        测试场景6：状态筛选 - 使用枚举类型
        验证点：
        1. 枚举类型可以正常使用
        2. 接口正常返回
        """
        # 1. 初始化 API 对象
        account_api = AccountAPI(session=login_session)
        
        # 2. 使用状态枚举筛选
        print(f"\n[Step] 筛选状态为 {account_status.value} 的账户")
        response = account_api.list_accounts(status=account_status)
        
        # 3. 断言状态码
        print("[Step] 验证 HTTP 状态码为 200")
        assert response.status_code == 200, f"接口返回状态码错误: {response.status_code}"
        
        # 4. 解析响应
        print("[Step] 解析响应数据")
        parsed = account_api.parse_list_response(response)
        assert not parsed.get("error"), f"响应解析失败: {parsed.get('message')}"
        
        accounts = parsed["content"]
        
        if len(accounts) > 0:
            for account in accounts:
                actual_status = account.get("account_status")
                if actual_status is not None:
                    assert actual_status == account_status.value, \
                        f"账户状态不匹配，期望 {account_status.value}，实际 {actual_status}"
            print(f"✓ 找到 {len(accounts)} 个状态为 {account_status.value} 的账户")
        else:
            print(f"⚠ 未找到状态为 {account_status.value} 的账户")

    def test_list_accounts_empty_result(self, login_session):
        """
        测试场景7：空结果验证
        验证点：
        1. 使用不存在的筛选条件时，接口返回 200
        2. 返回的 content 是空列表
        3. total_elements 为 0
        """
        # 1. 初始化 API 对象
        account_api = AccountAPI(session=login_session)
        
        # 2. 使用不太可能存在的筛选条件
        print("\n[Step] 使用不存在的账户编号查询")
        response = account_api.list_accounts(account_number="NONEXISTENT-999999")
        
        # 3. 断言状态码
        print("[Step] 验证 HTTP 状态码为 200")
        assert response.status_code == 200, f"接口返回状态码错误: {response.status_code}"
        
        # 4. 验证空结果
        print("[Step] 验证返回空列表")
        parsed = account_api.parse_list_response(response)
        assert not parsed.get("error"), f"响应解析失败: {parsed.get('message')}"
        
        assert len(parsed["content"]) == 0, "期望返回空列表，但实际有数据"
        assert parsed.get("empty", False) == True, "empty 字段应该为 True"
        
        print("✓ 空结果验证成功，接口正确返回空列表")

    def test_account_response_fields(self, login_session):
        """
        测试场景8：响应字段完整性验证
        验证点：
        1. 返回的账户对象包含必需字段
        2. 字段类型正确
        """
        # 1. 初始化 API 对象
        account_api = AccountAPI(session=login_session)
        
        # 2. 获取账户列表
        print("\n[Step] 获取账户列表")
        response = account_api.list_accounts(size=1)
        
        # 3. 断言状态码
        print("[Step] 验证 HTTP 状态码为 200")
        assert response.status_code == 200, f"接口返回状态码错误: {response.status_code}"
        
        # 4. 验证字段完整性
        print("[Step] 验证账户对象字段完整性")
        parsed = account_api.parse_list_response(response)
        assert not parsed.get("error"), f"响应解析失败: {parsed.get('message')}"
        
        accounts = parsed["content"]
        
        if len(accounts) > 0:
            account = accounts[0]
            
            # 必需字段列表
            required_fields = [
                "id", "account_name", "account_number", "account_status",
                "record_type", "create_time"
            ]
            
            for field in required_fields:
                assert field in account, f"账户对象缺少必需字段: {field}"
            
            print(f"✓ 字段完整性验证通过，账户对象包含所有必需字段")
            print(f"  示例账户: {account.get('account_number')} - {account.get('account_name')}")
        else:
            pytest.skip("没有账户数据可供验证")
