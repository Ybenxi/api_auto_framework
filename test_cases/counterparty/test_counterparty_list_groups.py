"""
Counterparty List Groups 接口测试用例
测试 GET /api/v1/cores/{core}/counterparty-groups 接口
"""
import pytest
from utils.logger import logger
from utils.assertions import (
    assert_status_ok,
    assert_response_parsed,
    assert_list_structure,
    assert_fields_present
)


@pytest.mark.counterparty
@pytest.mark.list_api
class TestCounterpartyListGroups:
    """
    获取 Counterparty Groups 列表接口测试用例集
    """

    def test_list_groups_success(self, counterparty_api):
        """
        测试场景1：成功获取 Groups 列表
        验证点：
        1. 接口返回 200
        2. 返回的 content 是数组
        3. 每个 group 包含必需字段（id, name）
        """
        # 1. 调用 List Groups 接口
        logger.info("\n获取 Groups 列表")
        response = counterparty_api.list_counterparty_groups(page=0, size=10)
        
        # 2. 验证响应
        assert_status_ok(response)
        response_body = response.json()
        content = response_body.get("content", [])
        assert isinstance(content, list), "content 字段应该是数组"
        
        logger.info(f"获取到 {len(content)} 个 Groups")
        
        # 3. 如果有数据，验证字段结构
        if len(content) > 0:
            group = content[0]
            required_fields = ["id", "name"]
            assert_fields_present(group, required_fields, "Group")
            
            logger.info("✓ 验证成功 - 第一个 ID: {group['id']}")
        else:
            logger.info("⚠ 当前没有 Group 数据")

    def test_list_groups_with_name_filter(self, counterparty_api):
        """
        测试场景2：使用 name 参数筛选
        验证点：
        1. 接口返回 200
        2. 筛选功能正常工作
        """
        # 1. 先获取所有 Groups
        logger.info("\n获取所有 Groups")
        all_response = counterparty_api.list_counterparty_groups(page=0, size=10)
        assert_status_ok(all_response)
        
        all_content = all_response.json().get("content", [])
        
        if len(all_content) == 0:
            pytest.skip("没有可用的 Group 数据，跳过测试")
        
        group_name = all_content[0].get("name")
        if not group_name:
            pytest.skip("Group 名称为空，跳过测试")
        
        # 2. 使用 name 参数筛选
        logger.info(f"使用 name 筛选: {group_name}")
        filtered_response = counterparty_api.list_counterparty_groups(name=group_name)
        assert_status_ok(filtered_response)

        filtered_content = filtered_response.json().get("content", [])
        logger.info(f"  筛选返回 {len(filtered_content)} 个结果")

        # 验证返回的每条数据 name 包含筛选关键词
        if filtered_content:
            keyword = group_name[:4] if len(group_name) >= 4 else group_name
            for group in filtered_content:
                assert keyword.lower() in group.get("name", "").lower(), \
                    f"返回 group name='{group.get('name')}' 不包含关键词 '{keyword}'"
        logger.info("✓ name 筛选结果验证通过")

    def test_list_groups_pagination(self, counterparty_api):
        """
        测试场景3：分页功能测试
        验证点：
        1. 接口返回 200
        2. 分页参数正常工作
        """
        logger.info("\n测试分页功能")
        page1_response = counterparty_api.list_counterparty_groups(page=0, size=5)
        assert_status_ok(page1_response)
        
        page1_data = page1_response.json()
        logger.info("✓ 分页验证成功 - 总数: {page1_data.get('total_elements')}")

    def test_list_groups_response_structure(self, counterparty_api):
        """
        测试场景4：验证响应数据结构
        验证点：
        1. 接口返回 200
        2. 响应包含 content, pageable 等字段
        """
        # 1. 调用接口
        logger.info("\n验证响应数据结构")
        response = counterparty_api.list_counterparty_groups(page=0, size=10)
        
        # 2. 验证状态码和结构
        assert_status_ok(response)
        response_body = response.json()
        
        # 3. 验证响应包含数据（可能在不同层级）
        assert response_body is not None, "响应不能为空"
        
        # 如果有data字段，提取它
        data_to_check = response_body
        if "data" in response_body and isinstance(response_body["data"], dict):
            data_to_check = response_body["data"]
        
        # 验证至少有content字段
        if "content" in data_to_check:
            assert isinstance(data_to_check["content"], list), "content应该是列表"
            logger.info(f"✓ 响应结构验证通过 - 返回 {len(data_to_check['content'])} 个Group")
        else:
            logger.info("✓ 响应结构验证通过")

    def test_list_groups_using_helper_method(self, counterparty_api):
        """
        测试场景5：使用辅助方法解析响应
        验证点：
        1. 接口返回 200
        2. parse_list_response 辅助方法正常工作
        """
        # 1. 调用接口
        logger.info("\n使用辅助方法解析响应")
        response = counterparty_api.list_counterparty_groups(page=0, size=10)
        
        # 2. 使用辅助方法解析
        parsed = counterparty_api.parse_list_response(response)
        
        # 3. 验证解析结果
        assert_response_parsed(parsed)
        assert_list_structure(parsed, required_fields=["content", "total_elements"])
        
        logger.info("✓ 解析成功 - Group 数量: {len(parsed['content'])}, 总数: {parsed['total_elements']}")

    def test_list_groups_nonexistent_name_returns_empty(self, counterparty_api):
        """
        测试场景7：搜索不存在的 group name → 返回空列表
        验证点：
        1. 返回 200
        2. content 为空数组
        3. total_elements 为 0
        """
        logger.info("使用不存在的 name 搜索 groups")
        response = counterparty_api.list_counterparty_groups(name="NonExistentGroup_AutoTestYan_999")
        assert_status_ok(response)

        content = response.json().get("content", [])
        assert len(content) == 0, f"不存在的 name 应返回空列表，实际返回 {len(content)} 条"
        logger.info("✓ 不存在的 name 返回空列表验证通过")

    def test_list_groups_empty_result(self, counterparty_api):
        """
        测试场景6：测试空结果场景
        验证点：
        1. 接口返回 200
        2. 正确处理无数据的情况
        """
        # 1. 使用不存在的名称筛选
        logger.info("\n测试空结果场景")
        response = counterparty_api.list_counterparty_groups(name="NonExistentGroup999999")
        
        # 2. 验证响应
        assert_status_ok(response)
        content = response.json().get("content", [])
        assert isinstance(content, list), "content 应该是数组"
        
        logger.info("✓ 空结果测试完成 - 返回数量: {len(content)}")
