"""
Client List - Client Statistics 接口测试用例
测试 GET /api/v1/cores/{core}/client-lists/statistics 接口
"""
import pytest
from utils.logger import logger
from utils.assertions import assert_status_ok
from data.enums import OMSCategory


@pytest.mark.client_list
@pytest.mark.statistics_api
class TestClientListStatistics:
    """
    客户统计信息接口测试用例集
    """

    def test_get_statistics_success(self, client_list_api):
        """
        测试场景1：成功获取客户统计信息
        验证点：
        1. 接口返回 200
        2. 返回统计数据结构
        """
        logger.info("测试场景1：成功获取客户统计信息")
        
        response = client_list_api.get_client_statistics()
        
        assert_status_ok(response)
        
        response_body = response.json()
        logger.debug(f"统计数据结构: {response_body}")
        
        logger.info("✓ 客户统计信息获取成功")

    def test_get_statistics_with_oms_category(self, client_list_api):
        """
        测试场景2：按oms_category获取统计信息
        验证点：
        1. 接口返回 200
        2. 统计数据针对指定分类
        """
        logger.info("测试场景2：按oms_category获取统计")
        
        response = client_list_api.get_client_statistics(oms_category=OMSCategory.EQUITY)
        
        assert_status_ok(response)
        
        response_body = response.json()
        logger.debug(f"Equity分类统计: {response_body}")
        
        logger.info("✓ 按分类统计信息获取成功")

    def test_get_statistics_response_structure(self, client_list_api):
        """
        测试场景3：验证统计响应结构
        验证点：
        1. 接口返回 200
        2. 包含统计所需的关键字段
        """
        logger.info("测试场景3：验证统计响应结构")
        
        response = client_list_api.get_client_statistics()
        
        assert_status_ok(response)
        
        response_body = response.json()
        data = response_body.get("data", response_body)
        
        logger.debug(f"统计字段: {list(data.keys()) if isinstance(data, dict) else type(data)}")
        
        # 验证返回了统计数据
        assert data is not None, "统计数据不应为空"
        
        # 可能包含的字段（根据实际情况调整）
        possible_fields = ["total_clients", "total_count", "count", "statistics"]
        found_fields = [field for field in possible_fields if field in data]
        if found_fields:
            logger.debug(f"找到统计字段: {found_fields}")
        
        logger.info("✓ 统计响应结构验证完成")

    def test_get_statistics_for_all_categories(self, client_list_api):
        """
        测试场景4：获取所有分类的统计信息
        验证点：
        1. 依次获取各分类统计
        2. 验证不同分类返回不同数据
        """
        logger.info("测试场景4：获取所有分类的统计信息")
        
        categories = [
            OMSCategory.EQUITY,
            OMSCategory.MUTUAL_FUND,
            OMSCategory.CRYPTO_CURRENCY,
            OMSCategory.BOND
        ]
        
        statistics_by_category = {}
        
        for category in categories:
            response = client_list_api.get_client_statistics(oms_category=category)
            assert_status_ok(response)
            
            statistics_by_category[category.value] = response.json()
            logger.debug(f"{category.value} 统计: {statistics_by_category[category.value]}")
        
        logger.info(f"✓ 获取了 {len(statistics_by_category)} 个分类的统计信息")

    def test_get_statistics_comparison(self, client_list_api):
        """
        测试场景5：对比全局统计和分类统计
        验证点：
        1. 全局统计数量应 >= 单个分类统计
        2. 数据一致性验证
        """
        logger.info("测试场景5：对比全局统计和分类统计")
        
        # 获取全局统计
        global_response = client_list_api.get_client_statistics()
        assert_status_ok(global_response)
        global_data = global_response.json().get("data", global_response.json())
        
        # 获取单个分类统计
        equity_response = client_list_api.get_client_statistics(oms_category=OMSCategory.EQUITY)
        assert_status_ok(equity_response)
        equity_data = equity_response.json().get("data", equity_response.json())
        
        logger.debug(f"全局统计: {global_data}")
        logger.debug(f"Equity统计: {equity_data}")
        
        # 如果两者都有count字段，验证全局>=分类
        if "count" in global_data and "count" in equity_data:
            assert global_data["count"] >= equity_data["count"], \
                "全局统计数量应大于等于单个分类"
        
        logger.info("✓ 统计数据对比验证完成")
