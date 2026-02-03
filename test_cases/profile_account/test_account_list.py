"""
账户管理接口测试用例
覆盖多种测试场景，包括基础查询、筛选、分页、枚举类型等
"""
import pytest
from data.enums import BusinessEntityType, AccountStatus
from utils.assertions import (
    assert_status_ok,
    assert_response_parsed,
    assert_list_structure,
    assert_enum_filter,
    assert_string_contains_filter,
    assert_pagination,
    assert_empty_result,
    assert_fields_present
)


class TestAccountList:
    """
    账户列表接口测试用例集
    """

    def test_list_accounts_basic(self, account_api):
        """
        测试场景1：基础列表查询 - 验证接口可用性
        验证点：
        1. HTTP 状态码为 200
        2. 响应中包含 content 字段
        3. content 是一个列表
        4. 响应结构完整（包含分页信息）
        """
        # 调用接口
        response = account_api.list_accounts()
        
        # 断言 HTTP 状态码
        assert_status_ok(response)
        
        # 解析响应并验证
        parsed = account_api.parse_list_response(response)
        assert_response_parsed(parsed)
        assert_list_structure(parsed, has_pagination=True)
        
        # 打印统计信息
        print(f"✓ 成功获取到 {len(parsed['content'])} 个账户，总计 {parsed['total_elements']} 个")

    @pytest.mark.parametrize("search_name", ["Example", "Test", "Account"])
    def test_list_accounts_filter_by_name(self, account_api, search_name):
        """
        测试场景2：名称筛选查询 - 验证筛选逻辑
        验证点：
        1. 接口返回成功
        2. 返回的所有账户名称都包含搜索关键词（不区分大小写）
        """
        # 调用接口并传入筛选参数
        response = account_api.list_accounts(name=search_name)
        
        # 断言状态码和解析响应
        assert_status_ok(response)
        parsed = account_api.parse_list_response(response)
        assert_response_parsed(parsed)
        
        accounts = parsed["content"]
        
        # 如果返回了数据，验证筛选逻辑
        if len(accounts) > 0:
            assert_string_contains_filter(accounts, "account_name", search_name, case_sensitive=False)
            print(f"✓ 筛选成功，找到 {len(accounts)} 个包含 '{search_name}' 的账户")
        else:
            print(f"⚠ 未找到包含 '{search_name}' 的账户（可能是正常情况）")

    def test_list_accounts_filter_by_entity_type(self, account_api):
        """
        测试场景3：枚举类型筛选 - 使用 BusinessEntityType 枚举
        验证点：
        1. 枚举类可以正常传递给 API
        2. 返回的所有账户的 business_entity_type 都是 LLC
        """
        # 使用枚举类型调用接口
        response = account_api.list_accounts(business_entity_type=BusinessEntityType.LLC)
        
        # 断言状态码和解析响应
        assert_status_ok(response)
        parsed = account_api.parse_list_response(response)
        assert_response_parsed(parsed)
        
        accounts = parsed["content"]
        
        if len(accounts) > 0:
            # 验证所有账户的 business_entity_type 都是 LLC（允许 None，跳过验证）
            assert_enum_filter(accounts, "business_entity_type", BusinessEntityType.LLC, allow_none=True)
            print(f"✓ 筛选成功，找到 {len(accounts)} 个 LLC 类型的账户")
        else:
            print("⚠ 未找到 LLC 类型的账户（可能是正常情况）")

    def test_list_accounts_multiple_filters(self, account_api):
        """
        测试场景4：多条件组合筛选
        验证点：
        1. 可以同时传递多个筛选参数
        2. 接口正常返回结果
        """
        # 使用多个筛选条件
        response = account_api.list_accounts(
            status=AccountStatus.ACTIVE,
            business_entity_type=BusinessEntityType.LLC,
            name="Example"
        )
        
        # 断言状态码和解析响应
        assert_status_ok(response)
        parsed = account_api.parse_list_response(response)
        assert_response_parsed(parsed)
        
        print(f"✓ 组合筛选成功，找到 {len(parsed['content'])} 个符合条件的账户")

    @pytest.mark.parametrize("page_size", [5, 10, 20])
    def test_list_accounts_pagination(self, account_api, page_size):
        """
        测试场景5：分页功能验证
        验证点：
        1. 可以指定每页大小
        2. 返回的数据量不超过指定大小
        3. 分页信息正确
        """
        # 使用分页参数
        response = account_api.list_accounts(page=0, size=page_size)
        
        # 断言状态码和解析响应
        assert_status_ok(response)
        parsed = account_api.parse_list_response(response)
        assert_response_parsed(parsed)
        
        # 验证分页信息
        assert_pagination(parsed, expected_size=page_size, expected_page=0)
        
        print(f"✓ 分页验证成功，请求 {page_size} 条，实际返回 {len(parsed['content'])} 条")

    @pytest.mark.parametrize("account_status", [
        AccountStatus.ACTIVE,
        AccountStatus.INACTIVE,
        AccountStatus.PENDING
    ])
    def test_list_accounts_filter_by_status(self, account_api, account_status):
        """
        测试场景6：状态筛选 - 使用枚举类型
        验证点：
        1. 枚举类型可以正常使用
        2. 接口正常返回
        """
        # 使用状态枚举筛选
        response = account_api.list_accounts(status=account_status)
        
        # 断言状态码和解析响应
        assert_status_ok(response)
        parsed = account_api.parse_list_response(response)
        assert_response_parsed(parsed)
        
        accounts = parsed["content"]
        
        if len(accounts) > 0:
            # 验证所有账户的状态都匹配（允许 None，跳过验证）
            assert_enum_filter(accounts, "account_status", account_status, allow_none=True)
            print(f"✓ 找到 {len(accounts)} 个状态为 {account_status.value} 的账户")
        else:
            print(f"⚠ 未找到状态为 {account_status.value} 的账户")

    def test_list_accounts_empty_result(self, account_api):
        """
        测试场景7：空结果验证
        验证点：
        1. 使用不存在的筛选条件时，接口返回 200
        2. 返回的 content 是空列表
        3. total_elements 为 0
        """
        # 使用不太可能存在的筛选条件
        response = account_api.list_accounts(account_number="NONEXISTENT-999999")
        
        # 断言状态码和解析响应
        assert_status_ok(response)
        parsed = account_api.parse_list_response(response)
        assert_response_parsed(parsed)
        
        # 验证空结果
        assert_empty_result(parsed)
        
        print("✓ 空结果验证成功，接口正确返回空列表")

    def test_account_response_fields(self, account_api):
        """
        测试场景8：响应字段完整性验证
        验证点：
        1. 返回的账户对象包含必需字段
        2. 字段类型正确
        """
        # 获取账户列表
        response = account_api.list_accounts(size=1)
        
        # 断言状态码和解析响应
        assert_status_ok(response)
        parsed = account_api.parse_list_response(response)
        assert_response_parsed(parsed)
        
        accounts = parsed["content"]
        
        if len(accounts) > 0:
            account = accounts[0]
            
            # 必需字段列表
            required_fields = [
                "id", "account_name", "account_number", "account_status",
                "record_type", "create_time"
            ]
            
            # 验证字段完整性
            assert_fields_present(account, required_fields, obj_name="账户对象")
            
            print(f"✓ 字段完整性验证通过，账户对象包含所有必需字段")
            print(f"  示例账户: {account.get('account_number')} - {account.get('account_name')}")
        else:
            pytest.skip("没有账户数据可供验证")

    def test_list_accounts_sorting_by_name(self, account_api):
        """
        测试场景9：排序功能验证 - 按账户名称排序
        验证点：
        1. 使用 sort 参数进行排序
        2. 验证返回的列表按指定字段排序
        """
        # 调用接口，按 account_name 升序排序
        response = account_api.list_accounts(size=20, **{"sort": "account_name,asc"})
        
        # 断言状态码和解析响应
        assert_status_ok(response)
        parsed = account_api.parse_list_response(response)
        assert_response_parsed(parsed)
        
        accounts = parsed["content"]
        
        if len(accounts) >= 2:
            # 验证排序逻辑（账户名称应该按字母顺序升序）
            for i in range(len(accounts) - 1):
                current_name = accounts[i].get("account_name", "").lower()
                next_name = accounts[i + 1].get("account_name", "").lower()
                assert current_name <= next_name, \
                    f"排序不正确: {current_name} 应该在 {next_name} 之前"
            
            print(f"✓ 排序验证成功（升序），共 {len(accounts)} 个账户")
            print(f"  第一个: {accounts[0].get('account_name')}")
            print(f"  最后一个: {accounts[-1].get('account_name')}")
        else:
            print(f"⚠ 账户数量不足，无法验证排序（当前 {len(accounts)} 个）")
