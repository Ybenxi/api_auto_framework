"""
Counterparty List Counterparties 接口测试用例
测试 GET /api/v1/cores/{core}/counterparties 接口
"""
import pytest
from utils.assertions import (
    assert_status_ok,
    assert_response_parsed,
    assert_list_structure,
    assert_fields_present
)


@pytest.mark.counterparty
@pytest.mark.list_api
class TestCounterpartyListCounterparties:
    """
    获取 Counterparties 列表接口测试用例集
    """

    def test_list_counterparties_success(self, counterparty_api):
        """
        测试场景1：成功获取 Counterparties 列表
        验证点：
        1. 接口返回 200
        2. 返回的 content 是数组
        3. 每个 counterparty 包含必需字段（id, name, type, payment_type）
        """
        # 1. 调用 List Counterparties 接口
        print("\n获取 Counterparties 列表")
        response = counterparty_api.list_counterparties(page=0, size=10)
        
        # 2. 验证响应
        assert_status_ok(response)
        response_body = response.json()
        content = response_body.get("content", [])
        assert isinstance(content, list), "content 字段应该是数组"
        
        print(f"获取到 {len(content)} 个 Counterparties")
        
        # 3. 如果有数据，验证字段结构
        if len(content) > 0:
            counterparty = content[0]
            required_fields = ["id", "name", "type", "payment_type", "bank_account_owner_name", "assign_account_ids"]
            assert_fields_present(counterparty, required_fields, "Counterparty")
            
            print(f"✓ 验证成功 - 第一个 ID: {counterparty['id']}")
        else:
            print("⚠ 当前没有 Counterparty 数据")

    def test_list_counterparties_with_name_filter(self, counterparty_api):
        """
        测试场景2：使用 name 参数筛选
        验证点：
        1. 接口返回 200
        2. 筛选功能正常工作
        """
        # 1. 先获取所有 Counterparties
        print("\n获取所有 Counterparties")
        all_response = counterparty_api.list_counterparties(page=0, size=10)
        assert_status_ok(all_response)
        
        all_content = all_response.json().get("content", [])
        
        if len(all_content) == 0:
            pytest.skip("没有可用的 Counterparty 数据，跳过测试")
        
        counterparty_name = all_content[0].get("name")
        if not counterparty_name:
            pytest.skip("Counterparty 名称为空，跳过测试")
        
        # 2. 使用 name 参数筛选
        print(f"使用 name 筛选: {counterparty_name}")
        filtered_response = counterparty_api.list_counterparties(name=counterparty_name)
        assert_status_ok(filtered_response)
        
        filtered_content = filtered_response.json().get("content", [])
        print(f"✓ 筛选完成 - 获取到 {len(filtered_content)} 个结果")

    def test_list_counterparties_with_status_filter(self, counterparty_api):
        """
        测试场景3：使用 status 参数筛选
        验证点：
        1. 接口返回 200
        2. status 筛选功能正常工作
        """
        test_statuses = ["Approved", "Pending", "Rejected", "Terminated"]
        
        print("\n测试 status 筛选")
        for status in test_statuses:
            response = counterparty_api.list_counterparties(status=status, page=0, size=10)
            assert_status_ok(response)
            
            content = response.json().get("content", [])
            print(f"  {status}: {len(content)} 个结果")
        
        print("✓ status 筛选测试完成")

    def test_list_counterparties_with_payment_type_filter(self, counterparty_api):
        """
        测试场景4：使用 payment_type 参数筛选
        验证点：
        1. 接口返回 200
        2. payment_type 筛选功能正常工作
        """
        test_payment_types = ["ACH", "Check", "Wire", "International_Wire"]
        
        print("\n测试 payment_type 筛选")
        for payment_type in test_payment_types:
            response = counterparty_api.list_counterparties(payment_type=payment_type, page=0, size=10)
            assert_status_ok(response)
            
            content = response.json().get("content", [])
            print(f"  {payment_type}: {len(content)} 个结果")
            
            # 如果有结果，验证 payment_type 字段
            if len(content) > 0:
                for counterparty in content:
                    assert counterparty.get("payment_type") == payment_type, \
                        f"筛选结果的 payment_type 不匹配: 期望 {payment_type}, 实际 {counterparty.get('payment_type')}"
        
        print("✓ payment_type 筛选测试完成")

    def test_list_counterparties_pagination(self, counterparty_api):
        """
        测试场景5：分页功能测试
        验证点：
        1. 接口返回 200
        2. 分页参数正常工作
        3. 返回分页信息正确
        """
        print("\n测试分页功能")
        page1_response = counterparty_api.list_counterparties(page=0, size=5)
        assert_status_ok(page1_response)
        
        page1_data = page1_response.json()
        
        # 验证分页信息字段
        required_fields = ["pageable", "total_elements", "total_pages"]
        assert_fields_present(page1_data, required_fields, "分页信息")
        
        print(f"✓ 分页验证成功 - 总数: {page1_data.get('total_elements')}")

    def test_list_counterparties_using_helper_method(self, counterparty_api):
        """
        测试场景6：使用辅助方法解析响应
        验证点：
        1. 接口返回 200
        2. parse_list_response 辅助方法正常工作
        """
        # 1. 调用接口
        print("\n使用辅助方法解析响应")
        response = counterparty_api.list_counterparties(page=0, size=10)
        
        # 2. 使用辅助方法解析
        parsed = counterparty_api.parse_list_response(response)
        
        # 3. 验证解析结果
        assert_response_parsed(parsed)
        assert_list_structure(parsed, required_fields=["content", "pageable", "total_elements"])
        
        print(f"✓ 解析成功 - Counterparty 数量: {len(parsed['content'])}, 总数: {parsed['total_elements']}")
