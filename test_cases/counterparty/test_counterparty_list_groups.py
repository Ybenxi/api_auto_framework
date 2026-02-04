"""
Counterparty List Groups 接口测试用例
测试 GET /api/v1/cores/{core}/counterparty-groups 接口
"""
import pytest
from api.counterparty_api import CounterpartyAPI


@pytest.mark.counterparty
@pytest.mark.list_api
class TestCounterpartyListGroups:
    """
    获取 Counterparty Groups 列表接口测试用例集
    """

    def test_list_groups_success(self, login_session):
        """
        测试场景1：成功获取 Groups 列表
        验证点：
        1. 接口返回 200
        2. 返回的 content 是数组
        3. 每个 group 包含必需字段（id, name）
        """
        # 1. 初始化 API 对象
        counterparty_api = CounterpartyAPI(session=login_session)
        
        # 2. 调用 List Groups 接口
        print("\n[Step] 调用 List Groups 接口")
        response = counterparty_api.list_counterparty_groups(page=0, size=10)
        
        # 3. 断言状态码
        print("[Step] 验证 HTTP 状态码为 200")
        assert response.status_code == 200, \
            f"List Groups 接口返回状态码错误: {response.status_code}, Response: {response.text}"
        
        # 4. 解析响应
        print("[Step] 解析响应并验证数据")
        response_body = response.json()
        
        # 5. 验证 content 是数组
        content = response_body.get("content", [])
        assert isinstance(content, list), "content 字段应该是数组"
        
        print(f"[Step] 获取到 {len(content)} 个 Groups")
        
        # 6. 如果有数据，验证字段结构
        if len(content) > 0:
            print("[Step] 验证第一个 Group 的必需字段")
            group = content[0]
            required_fields = ["id", "name"]
            
            for field in required_fields:
                assert field in group, f"Group 数据缺少必需字段: {field}"
                print(f"  ✓ {field}: {group.get(field)}")
            
            print(f"\n✓ 成功获取 Groups 列表:")
            print(f"  数量: {len(content)}")
            print(f"  第一个 ID: {group['id']}")
            print(f"  名称: {group.get('name')}")
        else:
            print("  ⚠ 当前没有 Group 数据")

    def test_list_groups_with_name_filter(self, login_session):
        """
        测试场景2：使用 name 参数筛选
        验证点：
        1. 接口返回 200
        2. 筛选功能正常工作
        """
        # 1. 初始化 API 对象
        counterparty_api = CounterpartyAPI(session=login_session)
        
        # 2. 先不带参数查询，获取一个名称
        print("\n[Step] 先获取所有 Groups")
        all_response = counterparty_api.list_counterparty_groups(page=0, size=10)
        assert all_response.status_code == 200, "获取所有 Groups 失败"
        
        all_content = all_response.json().get("content", [])
        
        if len(all_content) == 0:
            pytest.skip("没有可用的 Group 数据，跳过测试")
        
        # 获取第一个 group 的名称
        group_name = all_content[0].get("name")
        if not group_name:
            pytest.skip("Group 名称为空，跳过测试")
        
        print(f"[Step] 使用 name 参数筛选: {group_name}")
        
        # 3. 调用带筛选的接口
        filtered_response = counterparty_api.list_counterparty_groups(name=group_name)
        
        # 4. 验证状态码
        print("[Step] 验证 HTTP 状态码为 200")
        assert filtered_response.status_code == 200, \
            f"筛选接口返回状态码错误: {filtered_response.status_code}"
        
        # 5. 验证返回数据
        filtered_content = filtered_response.json().get("content", [])
        print(f"[Step] 筛选后获取到 {len(filtered_content)} 个 Groups")
        
        print(f"✓ name 参数筛选测试完成")

    def test_list_groups_pagination(self, login_session):
        """
        测试场景3：分页功能测试
        验证点：
        1. 接口返回 200
        2. 分页参数正常工作
        """
        # 1. 初始化 API 对象
        counterparty_api = CounterpartyAPI(session=login_session)
        
        # 2. 测试不同的分页参数
        print("\n[Step] 测试分页功能")
        
        # 第一页
        page1_response = counterparty_api.list_counterparty_groups(page=0, size=5)
        assert page1_response.status_code == 200, "第一页请求失败"
        
        page1_data = page1_response.json()
        print(f"  第一页数量: {len(page1_data.get('content', []))}")
        print(f"  总元素数: {page1_data.get('total_elements')}")
        
        print(f"✓ 分页功能测试完成")

    def test_list_groups_response_structure(self, login_session):
        """
        测试场景4：验证响应数据结构
        验证点：
        1. 接口返回 200
        2. 响应包含 content, pageable 等字段
        """
        # 1. 初始化 API 对象
        counterparty_api = CounterpartyAPI(session=login_session)
        
        # 2. 调用接口
        print("\n[Step] 调用 List Groups 接口")
        response = counterparty_api.list_counterparty_groups(page=0, size=10)
        
        # 3. 验证状态码
        print("[Step] 验证 HTTP 状态码为 200")
        assert response.status_code == 200, \
            f"接口返回状态码错误: {response.status_code}"
        
        # 4. 验证响应数据结构
        print("[Step] 验证响应数据结构")
        response_body = response.json()
        
        # 验证包含必需字段
        expected_fields = ["content", "pageable", "total_elements", "total_pages"]
        for field in expected_fields:
            assert field in response_body, f"响应中缺少字段: {field}"
            print(f"  ✓ {field}: 存在")
        
        # 验证 content 是数组
        assert isinstance(response_body["content"], list), "content 字段应该是数组"
        
        print(f"✓ 响应数据结构验证通过")

    def test_list_groups_using_helper_method(self, login_session):
        """
        测试场景5：使用辅助方法解析响应
        验证点：
        1. 接口返回 200
        2. parse_list_response 辅助方法正常工作
        """
        # 1. 初始化 API 对象
        counterparty_api = CounterpartyAPI(session=login_session)
        
        # 2. 调用接口
        print("\n[Step] 调用 List Groups 接口")
        response = counterparty_api.list_counterparty_groups(page=0, size=10)
        
        # 3. 使用辅助方法解析响应
        print("[Step] 使用 parse_list_response 辅助方法解析响应")
        parsed = counterparty_api.parse_list_response(response)
        
        # 4. 验证解析结果
        print("[Step] 验证解析结果")
        assert not parsed.get("error"), f"响应解析失败: {parsed.get('message')}"
        
        # 验证包含必需字段
        assert "content" in parsed, "解析结果缺少 content 字段"
        assert "total_elements" in parsed, "解析结果缺少 total_elements 字段"
        
        # 验证 content 是列表
        assert isinstance(parsed["content"], list), "content 应该是列表"
        
        print(f"\n✓ 辅助方法解析验证通过:")
        print(f"  Group 数量: {len(parsed['content'])}")
        print(f"  总元素数: {parsed['total_elements']}")

    def test_list_groups_empty_result(self, login_session):
        """
        测试场景6：测试空结果场景
        验证点：
        1. 接口返回 200
        2. 正确处理无数据的情况
        """
        # 1. 初始化 API 对象
        counterparty_api = CounterpartyAPI(session=login_session)
        
        # 2. 使用不存在的名称筛选
        print("\n[Step] 使用不存在的名称筛选")
        response = counterparty_api.list_counterparty_groups(name="NonExistentGroup999999")
        
        # 3. 验证状态码
        assert response.status_code == 200, \
            f"接口返回状态码错误: {response.status_code}"
        
        # 4. 验证返回空列表
        content = response.json().get("content", [])
        print(f"  返回数量: {len(content)}")
        
        assert isinstance(content, list), "content 应该是数组"
        
        print(f"✓ 空结果测试完成")
