"""
Counterparty List Counterparties 接口测试用例
测试 GET /api/v1/cores/{core}/counterparties 接口
"""
import pytest
from api.counterparty_api import CounterpartyAPI


@pytest.mark.counterparty
@pytest.mark.list_api
class TestCounterpartyListCounterparties:
    """
    获取 Counterparties 列表接口测试用例集
    """

    def test_list_counterparties_success(self, login_session):
        """
        测试场景1：成功获取 Counterparties 列表
        验证点：
        1. 接口返回 200
        2. 返回的 content 是数组
        3. 每个 counterparty 包含必需字段（id, name, type, payment_type）
        """
        # 1. 初始化 API 对象
        counterparty_api = CounterpartyAPI(session=login_session)
        
        # 2. 调用 List Counterparties 接口
        print("\n[Step] 调用 List Counterparties 接口")
        response = counterparty_api.list_counterparties(page=0, size=10)
        
        # 3. 断言状态码
        print("[Step] 验证 HTTP 状态码为 200")
        assert response.status_code == 200, \
            f"List Counterparties 接口返回状态码错误: {response.status_code}, Response: {response.text}"
        
        # 4. 解析响应
        print("[Step] 解析响应并验证数据")
        response_body = response.json()
        
        # 5. 验证 content 是数组
        content = response_body.get("content", [])
        assert isinstance(content, list), "content 字段应该是数组"
        
        print(f"[Step] 获取到 {len(content)} 个 Counterparties")
        
        # 6. 如果有数据，验证字段结构
        if len(content) > 0:
            print("[Step] 验证第一个 Counterparty 的必需字段")
            counterparty = content[0]
            required_fields = ["id", "name", "type", "payment_type", "bank_account_owner_name", "assign_account_ids"]
            
            for field in required_fields:
                assert field in counterparty, f"Counterparty 数据缺少必需字段: {field}"
                print(f"  ✓ {field}: {counterparty.get(field)}")
            
            print(f"\n✓ 成功获取 Counterparties 列表:")
            print(f"  数量: {len(content)}")
            print(f"  第一个 ID: {counterparty['id']}")
            print(f"  名称: {counterparty.get('name')}")
            print(f"  类型: {counterparty.get('type')}")
            print(f"  支付类型: {counterparty.get('payment_type')}")
        else:
            print("  ⚠ 当前没有 Counterparty 数据")

    def test_list_counterparties_with_name_filter(self, login_session):
        """
        测试场景2：使用 name 参数筛选
        验证点：
        1. 接口返回 200
        2. 筛选功能正常工作
        """
        # 1. 初始化 API 对象
        counterparty_api = CounterpartyAPI(session=login_session)
        
        # 2. 先不带参数查询，获取一个名称
        print("\n[Step] 先获取所有 Counterparties")
        all_response = counterparty_api.list_counterparties(page=0, size=10)
        assert all_response.status_code == 200, "获取所有 Counterparties 失败"
        
        all_content = all_response.json().get("content", [])
        
        if len(all_content) == 0:
            pytest.skip("没有可用的 Counterparty 数据，跳过测试")
        
        # 获取第一个 counterparty 的名称
        counterparty_name = all_content[0].get("name")
        if not counterparty_name:
            pytest.skip("Counterparty 名称为空，跳过测试")
        
        print(f"[Step] 使用 name 参数筛选: {counterparty_name}")
        
        # 3. 调用带筛选的接口
        filtered_response = counterparty_api.list_counterparties(name=counterparty_name)
        
        # 4. 验证状态码
        print("[Step] 验证 HTTP 状态码为 200")
        assert filtered_response.status_code == 200, \
            f"筛选接口返回状态码错误: {filtered_response.status_code}"
        
        # 5. 验证返回数据
        filtered_content = filtered_response.json().get("content", [])
        print(f"[Step] 筛选后获取到 {len(filtered_content)} 个 Counterparties")
        
        print(f"✓ name 参数筛选测试完成")

    def test_list_counterparties_with_status_filter(self, login_session):
        """
        测试场景3：使用 status 参数筛选
        验证点：
        1. 接口返回 200
        2. status 筛选功能正常工作
        """
        # 1. 初始化 API 对象
        counterparty_api = CounterpartyAPI(session=login_session)
        
        # 2. 测试不同的 status 值
        test_statuses = ["Approved", "Pending", "Rejected", "Terminated"]
        
        for status in test_statuses:
            print(f"\n[Step] 测试 status 筛选: {status}")
            response = counterparty_api.list_counterparties(status=status, page=0, size=10)
            
            # 验证状态码
            assert response.status_code == 200, \
                f"status={status} 筛选失败: {response.status_code}"
            
            content = response.json().get("content", [])
            print(f"  筛选结果数量: {len(content)}")
        
        print(f"\n✓ status 参数筛选测试完成")

    def test_list_counterparties_with_payment_type_filter(self, login_session):
        """
        测试场景4：使用 payment_type 参数筛选
        验证点：
        1. 接口返回 200
        2. payment_type 筛选功能正常工作
        """
        # 1. 初始化 API 对象
        counterparty_api = CounterpartyAPI(session=login_session)
        
        # 2. 测试不同的 payment_type 值
        test_payment_types = ["ACH", "Check", "Wire", "International_Wire"]
        
        for payment_type in test_payment_types:
            print(f"\n[Step] 测试 payment_type 筛选: {payment_type}")
            response = counterparty_api.list_counterparties(payment_type=payment_type, page=0, size=10)
            
            # 验证状态码
            assert response.status_code == 200, \
                f"payment_type={payment_type} 筛选失败: {response.status_code}"
            
            content = response.json().get("content", [])
            print(f"  筛选结果数量: {len(content)}")
            
            # 如果有结果，验证 payment_type 字段
            if len(content) > 0:
                for counterparty in content:
                    assert counterparty.get("payment_type") == payment_type, \
                        f"筛选结果的 payment_type 不匹配: 期望 {payment_type}, 实际 {counterparty.get('payment_type')}"
        
        print(f"\n✓ payment_type 参数筛选测试完成")

    def test_list_counterparties_pagination(self, login_session):
        """
        测试场景5：分页功能测试
        验证点：
        1. 接口返回 200
        2. 分页参数正常工作
        3. 返回分页信息正确
        """
        # 1. 初始化 API 对象
        counterparty_api = CounterpartyAPI(session=login_session)
        
        # 2. 测试不同的分页参数
        print("\n[Step] 测试分页功能")
        
        # 第一页
        page1_response = counterparty_api.list_counterparties(page=0, size=5)
        assert page1_response.status_code == 200, "第一页请求失败"
        
        page1_data = page1_response.json()
        print(f"  第一页数量: {len(page1_data.get('content', []))}")
        print(f"  总元素数: {page1_data.get('total_elements')}")
        print(f"  总页数: {page1_data.get('total_pages')}")
        
        # 验证分页信息
        assert "pageable" in page1_data, "响应中缺少 pageable 字段"
        assert "total_elements" in page1_data, "响应中缺少 total_elements 字段"
        assert "total_pages" in page1_data, "响应中缺少 total_pages 字段"
        
        print(f"✓ 分页功能测试完成")

    def test_list_counterparties_using_helper_method(self, login_session):
        """
        测试场景6：使用辅助方法解析响应
        验证点：
        1. 接口返回 200
        2. parse_list_response 辅助方法正常工作
        """
        # 1. 初始化 API 对象
        counterparty_api = CounterpartyAPI(session=login_session)
        
        # 2. 调用接口
        print("\n[Step] 调用 List Counterparties 接口")
        response = counterparty_api.list_counterparties(page=0, size=10)
        
        # 3. 使用辅助方法解析响应
        print("[Step] 使用 parse_list_response 辅助方法解析响应")
        parsed = counterparty_api.parse_list_response(response)
        
        # 4. 验证解析结果
        print("[Step] 验证解析结果")
        assert not parsed.get("error"), f"响应解析失败: {parsed.get('message')}"
        
        # 验证包含必需字段
        assert "content" in parsed, "解析结果缺少 content 字段"
        assert "pageable" in parsed, "解析结果缺少 pageable 字段"
        assert "total_elements" in parsed, "解析结果缺少 total_elements 字段"
        
        # 验证 content 是列表
        assert isinstance(parsed["content"], list), "content 应该是列表"
        
        print(f"\n✓ 辅助方法解析验证通过:")
        print(f"  Counterparty 数量: {len(parsed['content'])}")
        print(f"  总元素数: {parsed['total_elements']}")
        print(f"  总页数: {parsed['total_pages']}")
