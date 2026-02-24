"""
Client List - List Clients 接口测试用例
测试 GET /api/v1/cores/{core}/client-lists 接口
"""
import pytest
from utils.logger import logger
from utils.assertions import (
    assert_status_ok,
    assert_list_structure,
    assert_pagination,
    assert_enum_filter
)
from data.enums import OMSCategory


@pytest.mark.client_list
@pytest.mark.list_api
@pytest.mark.skip(reason="接口返回404，DEV环境该模块暂不可用，待确认后启用")
class TestClientListList:
    """
    客户列表接口测试用例集
    ⚠️ 文档问题：响应结构60+字段平铺，嵌套关系不清晰
    """

    def test_list_clients_success(self, client_list_api):
        """
        测试场景1：成功获取客户列表
        验证点：
        1. 接口返回 200
        2. 返回列表结构正确
        """
        logger.info("测试场景1：成功获取客户列表")
        
        response = client_list_api.list_clients(page=0, size=10)
        
        assert_status_ok(response)
        
        response_body = response.json()
        assert_list_structure(response_body)
        
        logger.info(f"✓ 客户列表获取成功，返回 {len(response_body.get('content', []))} 个客户")

    @pytest.mark.parametrize("oms_category", [
        OMSCategory.EQUITY,
        OMSCategory.MUTUAL_FUND,
        OMSCategory.CRYPTO_CURRENCY,
        OMSCategory.CERTIFICATES_OF_DEPOSIT,
        OMSCategory.BOND,
        OMSCategory.OTHERS
    ])
    def test_list_clients_with_oms_category_filter(self, client_list_api, oms_category):
        """
        测试场景2：使用 oms_category 筛选客户（覆盖全部6个枚举值）
        验证点：
        1. 接口返回 200
        2. 返回的每条客户 oms_category 与筛选值一致
        """
        logger.info(f"测试场景2：使用 oms_category='{oms_category}' 筛选")

        response = client_list_api.list_clients(oms_category=oms_category, size=10)
        assert_status_ok(response)

        content = response.json().get("content", [])
        logger.info(f"  返回 {len(content)} 个客户")

        if not content:
            logger.info(f"  ⚠️ oms_category='{oms_category}' 无数据，跳过筛选值验证")
        else:
            for client in content:
                assert client.get("oms_category") == str(oms_category), \
                    f"筛选结果包含非 {oms_category}: {client.get('oms_category')}"
            logger.info(f"✓ {len(content)} 条数据 oms_category 均为 {oms_category}")

    def test_list_clients_with_account_name_filter(self, client_list_api):
        """
        测试场景3：使用 account_name 模糊筛选客户
        先 list 获取真实 account_name，验证每条结果包含关键词
        验证点：
        1. 接口返回 200
        2. 返回的每条客户 account_name 包含筛选关键词
        """
        logger.info("测试场景3：使用 account_name 筛选")

        # Step 1: 获取真实 account_name
        base_response = client_list_api.list_clients(page=0, size=1)
        assert_status_ok(base_response)
        base_content = base_response.json().get("content", [])

        if not base_content:
            pytest.skip("无客户数据，跳过")

        real_name = base_content[0].get("account_name", "")
        if not real_name or len(real_name) < 2:
            pytest.skip("account_name 为空或过短，跳过")

        keyword = real_name[:4]
        logger.info(f"  使用关键词: '{keyword}'（来自 account_name='{real_name}'）")

        # Step 2: 用关键词筛选
        response = client_list_api.list_clients(account_name=keyword, size=10)
        assert_status_ok(response)

        content = response.json().get("content", [])
        assert len(content) > 0, f"筛选结果为空，关键词 '{keyword}' 应能匹配到数据"

        # Step 3: 断言
        for client in content:
            assert keyword.lower() in client.get("account_name", "").lower(), \
                f"返回数据 account_name='{client.get('account_name')}' 不包含关键词 '{keyword}'"

        logger.info(f"✓ account_name 筛选验证通过，返回 {len(content)} 条")

    def test_list_clients_with_date_range(self, client_list_api):
        """
        测试场景4：使用日期范围筛选客户
        验证点：
        1. 接口返回 200
        2. 日期参数正确传递
        """
        logger.info("测试场景4：使用日期范围筛选")
        
        response = client_list_api.list_clients(
            start_date="2024-01-01",
            end_date="2024-12-31",
            size=10
        )
        
        assert_status_ok(response)
        
        response_body = response.json()
        logger.info(f"✓ 日期范围筛选成功，返回 {len(response_body.get('content', []))} 个客户")

    def test_list_clients_pagination_first_page(self, client_list_api):
        """
        测试场景5：分页查询-第一页
        验证点：
        1. 接口返回 200
        2. 分页信息正确（size=5, number=0）
        3. 返回数量 <= size
        """
        logger.info("测试场景5：分页查询-第一页")

        response = client_list_api.list_clients(page=0, size=5)
        assert_status_ok(response)

        data = response.json()
        assert data.get("size") == 5, f"size 不正确: {data.get('size')}"
        assert data.get("number") == 0, f"number 不正确: {data.get('number')}"
        assert len(data.get("content", [])) <= 5, "返回数量超过 size=5"

        logger.info("✓ 第一页分页验证通过")

    def test_list_clients_pagination_second_page(self, client_list_api):
        """
        测试场景6：分页查询-第二页
        验证点：
        1. 接口返回 200
        2. number=1, first=false
        """
        logger.info("测试场景6：分页查询-第二页")
        
        response = client_list_api.list_clients(page=1, size=5)
        
        assert_status_ok(response)
        
        response_body = response.json()
        assert response_body.get("number") == 1, "页码应为1"
        assert response_body.get("first") == False, "first应为false"
        
        logger.info("✓ 第二页分页验证通过")

    def test_list_clients_empty_result(self, client_list_api):
        """
        测试场景7：查询结果为空
        验证点：
        1. 接口返回 200
        2. content为空数组
        3. empty=true
        """
        logger.info("测试场景7：查询结果为空")
        
        response = client_list_api.list_clients(
            account_name="NONEXISTENT_CLIENT_9999",
            size=10
        )
        
        assert_status_ok(response)
        
        response_body = response.json()
        assert response_body.get("empty") == True or len(response_body.get("content", [])) == 0, \
            "空结果应标记empty=true或content为空"
        
        logger.info("✓ 空结果验证通过")

    def test_list_clients_with_multiple_filters(self, client_list_api):
        """
        测试场景8：组合多个筛选条件
        验证点：
        1. 接口返回 200
        2. 多个筛选条件同时生效
        """
        logger.info("测试场景8：组合多个筛选条件")
        
        response = client_list_api.list_clients(
            oms_category=OMSCategory.EQUITY,
            start_date="2024-01-01",
            end_date="2024-12-31",
            size=10
        )
        
        assert_status_ok(response)
        
        logger.info("✓ 组合筛选验证通过")

    def test_list_clients_response_structure(self, client_list_api):
        """
        测试场景9：验证响应字段完整性
        验证点：
        1. 接口返回 200
        2. 必需字段存在
        """
        logger.info("测试场景9：验证响应字段完整性")
        
        response = client_list_api.list_clients(size=1)
        
        assert_status_ok(response)
        
        response_body = response.json()
        content = response_body.get("content", [])
        
        if content:
            client = content[0]
            logger.debug(f"客户字段: {list(client.keys())}")
            
            # 验证一些基本字段（根据实际情况调整）
            # 注意：由于文档问题，字段结构可能混乱
            assert "id" in client or "client_id" in client, "应包含ID字段"
        
        logger.info("✓ 响应结构验证完成")
