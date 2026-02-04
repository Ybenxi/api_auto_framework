"""
Counterparty Group CRUD 接口测试用例
测试 Group 的创建、更新、删除接口
"""
import pytest
import time
from utils.logger import logger
from utils.assertions import (
    assert_status_ok,
    assert_fields_present
)


@pytest.mark.counterparty
@pytest.mark.create_api
@pytest.mark.update_api
@pytest.mark.delete_api
class TestCounterpartyGroupCRUD:
    """
    Counterparty Group CRUD 接口测试用例集
    """

    def test_create_counterparty_group_success(self, counterparty_api):
        """
        测试场景1：成功创建 Counterparty Group
        验证点：
        1. 接口返回 200
        2. 返回的 Group ID 存在
        3. Group 名称正确
        """
        logger.info("创建 Counterparty Group")
        timestamp = int(time.time())
        group_name = f"Auto TestYan Group Basic {timestamp}"
        
        response = counterparty_api.create_counterparty_group(group_name)
        
        # 验证响应
        logger.info("验证创建响应")
        assert_status_ok(response)
        
        response_body = response.json()
        
        # 提取data字段（如果存在）
        if "data" in response_body and response_body["data"]:
            group_data = response_body["data"]
        else:
            group_data = response_body
        
        # 验证必需字段
        assert_fields_present(group_data, ["id", "name"], "Group")
        
        # 验证名称
        assert group_data.get("name") == group_name, \
            f"Group 名称不匹配: {group_data.get('name')}"
        
        logger.info("✓ Group 创建成功:")
        logger.info(f"  Group ID: {group_data.get('id')}")
        logger.info(f"  Group Name: {group_data.get('name')}")

    def test_create_counterparty_group_with_special_chars(self, counterparty_api):
        """
        测试场景2：创建包含特殊字符的 Group 名称
        验证点：
        1. 接口返回 200
        2. 特殊字符被正确处理
        """
        logger.info("创建包含特殊字符的 Group")
        timestamp = int(time.time())
        group_name = f"Auto TestYan Group-Special_123!@# {timestamp}"
        
        response = counterparty_api.create_counterparty_group(group_name)
        
        # 验证响应
        logger.info("验证响应")
        assert_status_ok(response)
        
        response_body = response.json()
        
        # 提取data字段
        if "data" in response_body and response_body["data"]:
            group_data = response_body["data"]
        else:
            group_data = response_body
        
        # 验证名称
        assert group_data.get("name") == group_name, \
            f"特殊字符未正确保存"
        
        logger.info("✓ 特殊字符处理验证通过")

    def test_create_counterparty_group_duplicate_name(self, counterparty_api):
        """
        测试场景3：创建重名的 Group
        验证点：
        1. 接口能处理重名（允许或拒绝）
        2. 返回适当的响应
        """
        logger.info("创建第一个 Group")
        timestamp = int(time.time())
        group_name = f"Auto TestYan Group Duplicate {timestamp}"
        
        response1 = counterparty_api.create_counterparty_group(group_name)
        assert_status_ok(response1)
        
        # 创建同名 Group
        logger.info("创建同名 Group")
        response2 = counterparty_api.create_counterparty_group(group_name)
        
        # 验证响应（可能允许重名也可能拒绝）
        logger.info("验证重名处理")
        assert response2.status_code in [200, 400, 409], \
            f"状态码应该是 200/400/409，实际: {response2.status_code}"
        
        if response2.status_code == 200:
            logger.info("✓ API 允许重名 Group")
        else:
            logger.info("✓ API 拒绝重名 Group")

    @pytest.mark.skip(reason="需要真实 Group ID，待完善数据准备逻辑")
    def test_update_counterparty_group_name(self, counterparty_api):
        """
        测试场景4：更新 Group 名称
        验证点：
        1. 接口返回 200
        2. 名称更新成功
        """
        # 创建 Group
        logger.info("创建 Group")
        original_name = "Auto TestYan Group Original"
        create_response = counterparty_api.create_counterparty_group(original_name)
        
        if create_response.status_code != 200:
            pytest.skip(f"创建 Group 失败")
        
        group_data = create_response.json()
        group_id = group_data.get("id")
        logger.info(f"Group 创建成功: {group_id}")
        
        # 更新名称
        logger.info("更新 Group 名称")
        new_name = "Auto TestYan Group Updated"
        update_response = counterparty_api.update_counterparty_group(group_id, new_name)
        
        # 验证响应
        logger.info("验证更新响应")
        assert_status_ok(update_response)
        
        response_body = update_response.json()
        updated_data = response_body
        
        assert updated_data.get("name") == new_name, \
            f"名称未更新: {updated_data.get('name')}"
        
        logger.info("✓ Group 名称更新成功:")
        logger.info(f"  原名称: {original_name}")
        logger.info(f"  新名称: {new_name}")

    def test_update_counterparty_group_invalid_id(self, counterparty_api):
        """
        测试场景5：使用无效 ID 更新 Group
        验证点：
        1. 返回 200 状态码（统一错误处理）
        2. 响应包含错误信息
        """
        logger.info("使用无效 ID 更新 Group")
        invalid_id = "INVALID_GROUP_ID_999999"
        new_name = "Updated Name"
        
        response = counterparty_api.update_counterparty_group(invalid_id, new_name)
        
        # 验证错误响应
        logger.info("验证错误响应")
        assert_status_ok(response)
        
        response_body = response.json()
        assert response_body.get("code") != 200 or "error" in str(response_body).lower(), \
            "无效 ID 应该返回错误"
        
        logger.info("✓ 无效 ID 错误处理验证通过")

    @pytest.mark.no_rerun  # 破坏性操作，禁止重试
    @pytest.mark.skip(reason="Delete 是破坏性操作，影响数据，仅手动测试")
    def test_delete_counterparty_group_success(self, counterparty_api):
        """
        测试场景6：成功删除 Group
        验证点：
        1. 接口返回 200
        2. Group 被成功删除
        """
        # 创建 Group
        logger.info("创建要删除的 Group")
        group_name = "Auto TestYan Group to Delete"
        create_response = counterparty_api.create_counterparty_group(group_name)
        
        group_data = create_response.json()
        group_id = group_data.get("id")
        logger.info(f"Group 创建成功: {group_id}")
        
        # 删除 Group
        logger.info("删除 Group")
        delete_response = counterparty_api.delete_counterparty_group(group_id)
        
        # 验证响应
        logger.info("验证删除响应")
        assert_status_ok(delete_response)
        
        logger.info("✓ Group 删除成功")

    def test_delete_counterparty_group_invalid_id(self, counterparty_api):
        """
        测试场景7：使用无效 ID 删除 Group
        验证点：
        1. 返回 200 状态码（统一错误处理）
        2. 响应包含错误信息
        """
        logger.info("使用无效 ID 删除 Group")
        invalid_id = "INVALID_GROUP_ID_999999"
        
        response = counterparty_api.delete_counterparty_group(invalid_id)
        
        # 验证错误响应
        logger.info("验证错误响应")
        assert_status_ok(response)
        
        response_body = response.json()
        assert response_body.get("code") != 200 or "error" in str(response_body).lower(), \
            "无效 ID 应该返回错误"
        
        logger.info("✓ 无效 ID 错误处理验证通过")
