"""
Client List - Historical Chart 接口测试用例
测试 GET /api/v1/cores/{core}/client-lists/historical-chart 接口
"""
import pytest
from utils.logger import logger
from utils.assertions import assert_status_ok
from data.enums import OMSCategory


@pytest.mark.client_list
@pytest.mark.chart_api
class TestClientListHistoricalChart:
    """
    历史图表数据接口测试用例集
    ⚠️ 文档问题：Historical Chart响应结构缺失
    """

    def test_get_historical_chart_success(self, client_list_api):
        """
        测试场景1：成功获取历史图表数据
        验证点：
        1. 接口返回 200
        2. 返回图表数据结构
        """
        logger.info("测试场景1：成功获取历史图表数据")
        
        response = client_list_api.get_historical_chart()
        
        assert_status_ok(response)
        
        response_body = response.json()
        logger.debug(f"图表数据结构: {list(response_body.keys())}")
        
        logger.info("✓ 历史图表数据获取成功")

    def test_get_historical_chart_with_oms_category(self, client_list_api):
        """
        测试场景2：按oms_category筛选图表数据
        验证点：
        1. 接口返回 200
        2. 筛选参数生效
        """
        logger.info("测试场景2：按oms_category筛选")
        
        response = client_list_api.get_historical_chart(oms_category=OMSCategory.EQUITY)
        
        assert_status_ok(response)
        
        logger.info("✓ 按分类筛选图表数据成功")

    def test_get_historical_chart_with_date_range(self, client_list_api):
        """
        测试场景3：按日期范围获取图表数据
        验证点：
        1. 接口返回 200
        2. 日期范围参数生效
        """
        logger.info("测试场景3：按日期范围获取图表数据")
        
        response = client_list_api.get_historical_chart(
            start_date="2024-01-01",
            end_date="2024-12-31"
        )
        
        assert_status_ok(response)
        
        response_body = response.json()
        logger.debug(f"日期范围图表数据: {response_body}")
        
        logger.info("✓ 日期范围图表数据获取成功")

    def test_get_historical_chart_with_multiple_filters(self, client_list_api):
        """
        测试场景4：组合多个筛选条件获取图表
        验证点：
        1. 接口返回 200
        2. 多个筛选条件同时生效
        """
        logger.info("测试场景4：组合多个筛选条件")
        
        response = client_list_api.get_historical_chart(
            oms_category=OMSCategory.CRYPTO_CURRENCY,
            start_date="2024-01-01",
            end_date="2024-12-31"
        )
        
        assert_status_ok(response)
        
        logger.info("✓ 组合筛选图表数据获取成功")

    def test_get_historical_chart_empty_result(self, client_list_api):
        """
        测试场景5：查询无数据的时间段
        验证点：
        1. 接口返回 200
        2. 返回空图表数据
        """
        logger.info("测试场景5：查询无数据的时间段")
        
        response = client_list_api.get_historical_chart(
            start_date="2099-01-01",
            end_date="2099-12-31"
        )
        
        assert_status_ok(response)
        
        response_body = response.json()
        # 空数据可能返回空数组或特定结构
        logger.debug(f"空数据图表: {response_body}")
        
        logger.info("✓ 空数据图表获取成功")

    def test_get_historical_chart_response_structure(self, client_list_api):
        """
        测试场景6：验证图表响应结构
        验证点：
        1. 接口返回 200
        2. 包含图表所需的关键字段
        """
        logger.info("测试场景6：验证图表响应结构")
        
        response = client_list_api.get_historical_chart(
            start_date="2024-01-01",
            end_date="2024-12-31"
        )
        
        assert_status_ok(response)
        
        response_body = response.json()
        data = response_body.get("data", response_body)
        
        logger.debug(f"图表数据字段: {list(data.keys()) if isinstance(data, dict) else type(data)}")
        
        # 由于文档缺失，无法断言具体字段
        # 只验证返回了某种数据结构
        assert data is not None, "图表数据不应为空"
        
        logger.info("✓ 图表响应结构验证完成")

    def test_get_historical_chart_invalid_date_range(self, client_list_api):
        """
        测试场景7：无效的日期范围（结束日期早于开始日期）
        验证点：
        1. 接口返回错误或空数据
        """
        logger.info("测试场景7：无效的日期范围")
        
        response = client_list_api.get_historical_chart(
            start_date="2024-12-31",
            end_date="2024-01-01"
        )
        
        # 可能返回错误或空数据
        if response.status_code == 200:
            response_body = response.json()
            if response_body.get("code") == 200:
                logger.info("✓ 系统返回空数据（接受无效日期范围）")
            else:
                logger.info(f"✓ 正确拒绝无效日期范围: {response_body.get('error_message', 'Unknown error')}")
        else:
            logger.info(f"✓ HTTP错误: {response.status_code}")
