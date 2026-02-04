"""
Counterparty Group Members 接口测试用例
测试 Group 成员管理接口（List, Add, Remove）
"""
import pytest
import time
from utils.logger import logger
from utils.assertions import (
    assert_status_ok,
    assert_list_structure,
    assert_pagination
)


@pytest.mark.counterparty
@pytest.mark.list_api
@pytest.mark.delete_api
class TestCounterpartyGroupMembers:
    """
    Counterparty Group 成员管理接口测试用例集
    """

    @pytest.mark.skip(reason="需要真实 account_id，待完善数据准备逻辑")
    def test_list_group_counterparties_success(self, counterparty_api):
        """
        测试场景1：成功获取 Group 内的 Counterparties 列表
        验证点：
        1. 接口返回 200
        2. 返回列表结构正确
        """
        # 先创建一个 Group
        logger.info("创建测试用的 Group")
        group_name = "Auto TestYan Group Members " + str(int(time.time()))
        create_response = counterparty_api.create_counterparty_group(group_name)
        
        if create_response.status_code != 200:
            pytest.skip(f"创建 Group 失败")
        
        response_body = create_response.json()
        # 提取data字段
        if "data" in response_body and response_body["data"]:
            group_data = response_body["data"]
        else:
            group_data = response_body
        group_id = group_data.get("id")
        logger.info(f"Group 创建成功: {group_id}")
        
        # 查询 Group 内的 Counterparties
        logger.info("查询 Group 内的 Counterparties")
        response = counterparty_api.list_group_counterparties(group_id, page=0, size=10)
        
        # 验证响应
        logger.info("验证响应结构")
        assert_status_ok(response)
        
        response_body = response.json()
        
        # 验证列表结构
        if "content" in response_body:
            assert_list_structure(response_body)
            logger.info(f"✓ Group 成员列表获取成功，返回 {len(response_body['content'])} 个成员")
        else:
            logger.info("✓ Group 成员列表接口调用成功（可能为空）")

    @pytest.mark.skip(reason="需要真实 account_id，待完善数据准备逻辑")
    def test_list_group_counterparties_with_name_filter(self, counterparty_api):
        """
        测试场景2：使用名称筛选 Group 内的 Counterparties
        验证点：
        1. 接口返回 200
        2. 筛选参数生效
        """
        # 创建 Group
        logger.info("创建测试用的 Group")
        group_name = "Auto TestYan Group Filter " + str(int(time.time()))
        create_response = counterparty_api.create_counterparty_group(group_name)
        
        if create_response.status_code != 200:
            pytest.skip(f"创建 Group 失败")
        
        response_body = create_response.json()
        # 提取data字段
        if "data" in response_body and response_body["data"]:
            group_data = response_body["data"]
        else:
            group_data = response_body
        group_id = group_data.get("id")
        
        # 使用名称筛选
        logger.info("使用名称筛选 Counterparties")
        response = counterparty_api.list_group_counterparties(
            group_id,
            name="Auto TestYan",
            size=10
        )
        
        # 验证响应
        logger.info("验证响应")
        assert_status_ok(response)
        
        logger.info("✓ 名称筛选参数处理正常")

    @pytest.mark.skip(reason="需要真实 account_id，待完善数据准备逻辑")
    def test_list_group_counterparties_pagination(self, counterparty_api):
        """
        测试场景3：验证 Group 成员列表分页功能
        验证点：
        1. 接口返回 200
        2. 分页信息正确
        """
        # 创建 Group
        logger.info("创建测试用的 Group")
        group_name = "Auto TestYan Group Pagination " + str(int(time.time()))
        create_response = counterparty_api.create_counterparty_group(group_name)
        
        if create_response.status_code != 200:
            pytest.skip(f"创建 Group 失败")
        
        response_body = create_response.json()
        # 提取data字段
        if "data" in response_body and response_body["data"]:
            group_data = response_body["data"]
        else:
            group_data = response_body
        group_id = group_data.get("id")
        
        # 测试分页
        logger.info("测试分页功能")
        response = counterparty_api.list_group_counterparties(
            group_id,
            page=0,
            size=5
        )
        
        # 验证响应
        logger.info("验证分页响应")
        assert_status_ok(response)
        
        response_body = response.json()
        if "content" in response_body:
            assert_pagination(response_body, expected_size=5, expected_page=0)
            logger.info("✓ 分页功能验证通过")
        else:
            logger.info("✓ 分页参数处理正常")

    def test_list_group_counterparties_invalid_group_id(self, counterparty_api):
        """
        测试场景4：使用无效 group_id 查询成员
        验证点：
        1. 返回 200 状态码（统一错误处理）
        2. 响应包含错误信息或返回空列表
        """
        logger.info("使用无效 Group ID 查询成员")
        invalid_id = "INVALID_GROUP_ID_999999"
        
        response = counterparty_api.list_group_counterparties(invalid_id, size=10)
        
        # 验证错误响应
        logger.info("验证错误响应")
        assert_status_ok(response)
        
        response_body = response.json()
        # 可能返回空列表或错误
        if "content" in response_body:
            assert len(response_body["content"]) == 0, "无效 ID 应该返回空列表"
            logger.info("✓ 无效 ID 返回空列表")
        else:
            logger.info("✓ 无效 ID 错误处理正常")

    @pytest.mark.skip(reason="Add 操作需要真实的 Counterparty ID，避免数据污染")
    def test_add_counterparties_to_group(self, counterparty_api, login_session):
        """
        测试场景5：添加 Counterparties 到 Group
        验证点：
        1. 接口返回 200
        2. Counterparties 成功添加到 Group
        """
        # 1. 创建 Group
        logger.info("创建 Group")
        group_name = "Auto TestYan Group Add Members"
        group_response = counterparty_api.create_counterparty_group(group_name)
        group_data = group_response.json().get("data", group_response.json())
        group_id = group_data.get("id")
        
        # 2. 创建 Counterparty
        logger.info("创建 Counterparty")
        counterparty_data = {
            "account_id": "test_account_id",
            "name": "Auto TestYan Counterparty for Group",
            "payment_type": "ACH",
            "ach_account_number": "1234567890",
            "ach_routing_number": "021000021",
            "ach_account_type": "Checking"
        }
        counterparty_response = counterparty_api.create_counterparty(counterparty_data)
        counterparty_data = counterparty_response.json().get("data", counterparty_response.json())
        counterparty_id = counterparty_data.get("id")
        
        # 3. 添加到 Group
        logger.info("添加 Counterparty 到 Group")
        add_response = counterparty_api.add_counterparties_to_group(
            group_id,
            [counterparty_id]
        )
        
        # 验证响应
        assert_status_ok(add_response)
        
        logger.info("✓ Counterparty 成功添加到 Group")

    def test_add_counterparties_to_group_invalid_group_id(self, counterparty_api):
        """
        测试场景6：使用无效 group_id 添加成员
        验证点：
        1. 返回 200 状态码（统一错误处理）
        2. 响应包含错误信息
        """
        logger.info("使用无效 Group ID 添加成员")
        invalid_group_id = "INVALID_GROUP_ID_999999"
        counterparty_ids = ["fake_id_1", "fake_id_2"]
        
        response = counterparty_api.add_counterparties_to_group(
            invalid_group_id,
            counterparty_ids
        )
        
        # 验证错误响应
        logger.info("验证错误响应")
        assert_status_ok(response)
        
        response_body = response.json()
        assert response_body.get("code") != 200 or "error" in str(response_body).lower(), \
            "无效 Group ID 应该返回错误"
        
        logger.info("✓ 无效 Group ID 错误处理验证通过")

    @pytest.mark.no_rerun  # 破坏性操作，禁止重试
    @pytest.mark.skip(reason="Remove 操作会影响数据，仅手动测试")
    def test_remove_counterparty_from_group(self, counterparty_api, login_session):
        """
        测试场景7：从 Group 中移除 Counterparty
        验证点：
        1. 接口返回 200
        2. Counterparty 成功从 Group 移除
        """
        # 1. 创建 Group
        logger.info("创建 Group")
        group_name = "Auto TestYan Group Remove Test"
        group_response = counterparty_api.create_counterparty_group(group_name)
        group_data = group_response.json().get("data", group_response.json())
        group_id = group_data.get("id")
        
        # 2. 创建并添加 Counterparty
        counterparty_data = {
            "account_id": "test_account_id",
            "name": "Auto TestYan Counterparty to Remove",
            "payment_type": "ACH",
            "ach_account_number": "5555666677",
            "ach_routing_number": "021000021",
            "ach_account_type": "Checking"
        }
        counterparty_response = counterparty_api.create_counterparty(counterparty_data)
        counterparty_data = counterparty_response.json().get("data", counterparty_response.json())
        counterparty_id = counterparty_data.get("id")
        
        # 添加到 Group
        counterparty_api.add_counterparties_to_group(group_id, [counterparty_id])
        
        # 3. 移除
        logger.info("从 Group 移除 Counterparty")
        remove_response = counterparty_api.remove_counterparty_from_group(
            group_id,
            counterparty_id
        )
        
        # 验证响应
        assert_status_ok(remove_response)
        
        logger.info("✓ Counterparty 成功从 Group 移除")

    def test_remove_counterparty_from_group_invalid_ids(self, counterparty_api):
        """
        测试场景8：使用无效 ID 移除成员
        验证点：
        1. 返回 200 状态码（统一错误处理）
        2. 响应包含错误信息
        """
        logger.info("使用无效 ID 移除 Counterparty")
        invalid_group_id = "INVALID_GROUP_ID_999999"
        invalid_counterparty_id = "INVALID_COUNTERPARTY_ID_999999"
        
        response = counterparty_api.remove_counterparty_from_group(
            invalid_group_id,
            invalid_counterparty_id
        )
        
        # 验证错误响应
        logger.info("验证错误响应")
        assert_status_ok(response)
        
        response_body = response.json()
        assert response_body.get("code") != 200 or "error" in str(response_body).lower(), \
            "无效 ID 应该返回错误"
        
        logger.info("✓ 无效 ID 错误处理验证通过")
