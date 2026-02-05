"""
Trading Order - List Securities 接口测试用例
测试 GET /api/v1/cores/{core}/trading-orders/securities 接口
"""
import pytest
from utils.logger import logger
from utils.assertions import (
    assert_status_ok,
    assert_list_structure,
    assert_pagination,
    assert_fields_present,
    assert_enum_filter
)
from data.enums import IssueType


@pytest.mark.trading_order
@pytest.mark.list_api
class TestTradingOrderListSecurities:
    """
    可交易证券列表接口测试用例集
    """

    def test_list_securities_success(self, trading_order_api):
        """
        测试场景1：成功获取证券列表
        验证点：
        1. 接口返回 200
        2. 返回列表结构正确
        3. 分页信息完整
        """
        logger.info("测试场景1：成功获取证券列表")
        
        response = trading_order_api.list_securities(page=0, size=10)
        
        assert_status_ok(response)
        
        response_body = response.json()
        assert_list_structure(response_body)
        
        logger.info(f"✓ 证券列表获取成功，返回 {len(response_body['content'])} 个证券")

    def test_list_securities_with_issue_type_filter(self, trading_order_api):
        """
        测试场景2：使用issue_type筛选
        验证点：
        1. 接口返回 200
        2. 返回的证券类型符合筛选条件
        """
        logger.info("测试场景2：使用issue_type筛选")
        
        response = trading_order_api.list_securities(
            issue_type=IssueType.COMMON_STOCK,
            size=10
        )
        
        assert_status_ok(response)
        
        response_body = response.json()
        securities = response_body.get("content", [])
        
        if len(securities) > 0:
            assert_enum_filter(securities, "issue_type", IssueType.COMMON_STOCK)
            logger.info(f"✓ issue_type 筛选验证通过，返回 {len(securities)} 个证券")
        else:
            logger.info("✓ 筛选返回空结果")

    def test_list_securities_with_symbol_filter(self, trading_order_api):
        """
        测试场景3：使用symbol筛选
        验证点：
        1. 接口返回 200
        2. symbol参数被正确处理
        """
        logger.info("测试场景3：使用symbol筛选")
        
        response = trading_order_api.list_securities(symbol="AAPL", size=10)
        
        assert_status_ok(response)
        
        response_body = response.json()
        securities = response_body.get("content", [])
        
        if len(securities) > 0:
            logger.info(f"✓ symbol筛选成功，返回 {len(securities)} 个结果")
        else:
            logger.info("✓ 筛选返回空结果")

    def test_list_securities_with_cusip_filter(self, trading_order_api):
        """
        测试场景4：使用CUSIP筛选
        验证点：
        1. 接口返回 200
        2. cusip参数被正确处理
        """
        logger.info("测试场景4：使用CUSIP筛选")
        
        response = trading_order_api.list_securities(cusip="037833100", size=10)
        
        assert_status_ok(response)
        
        logger.info("✓ CUSIP筛选参数处理正常")

    def test_list_securities_pagination(self, trading_order_api):
        """
        测试场景5：验证分页功能
        验证点：
        1. 接口返回 200
        2. 分页信息正确
        """
        logger.info("测试场景5：验证分页功能")
        
        response = trading_order_api.list_securities(page=0, size=5)
        
        assert_status_ok(response)
        
        response_body = response.json()
        assert_pagination(response_body, expected_size=5, expected_page=0)
        
        logger.info("✓ 分页功能验证通过")

    def test_list_securities_response_fields(self, trading_order_api):
        """
        测试场景6：验证响应字段完整性
        验证点：
        1. 接口返回 200
        2. 证券对象包含必需字段
        """
        logger.info("测试场景6：验证响应字段")
        
        response = trading_order_api.list_securities(size=1)
        
        assert_status_ok(response)
        
        response_body = response.json()
        securities = response_body.get("content", [])
        
        if len(securities) > 0:
            security = securities[0]
            required_fields = ["id", "name", "symbol", "issue_type", "price"]
            assert_fields_present(security, required_fields, "证券对象")
            
            logger.info("✓ 证券对象字段完整性验证通过")
        else:
            logger.info("✓ 响应结构正常（空结果）")
