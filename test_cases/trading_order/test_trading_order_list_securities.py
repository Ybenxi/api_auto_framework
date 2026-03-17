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

    @pytest.mark.parametrize("issue_type", list(IssueType))
    def test_list_securities_with_issue_type_filter(self, trading_order_api, issue_type):
        """
        测试场景2：使用 issue_type 筛选（覆盖全部枚举值）
        验证点：
        1. 接口返回 200
        2. 返回的每条证券 issue_type 与筛选值一致
        """
        logger.info(f"测试场景2：使用 issue_type='{issue_type.value}' 筛选")

        response = trading_order_api.list_securities(
            issue_type=issue_type,
            size=10
        )

        assert_status_ok(response)

        response_body = response.json()
        securities = response_body.get("content", [])
        logger.info(f"  返回 {len(securities)} 个证券")

        if securities:
            for sec in securities:
                assert sec.get("issue_type") == issue_type.value, \
                    f"返回证券 issue_type='{sec.get('issue_type')}' 与筛选值 '{issue_type.value}' 不一致"
            logger.info(f"✓ issue_type='{issue_type.value}' 筛选验证通过")

    def test_list_securities_with_symbol_filter(self, trading_order_api):
        """
        测试场景3：使用 symbol 筛选
        先 list 获取真实 symbol，再用它筛选，验证每条返回数据的 symbol 匹配
        验证点：
        1. 接口返回 200
        2. 返回的每条数据 symbol 包含关键词
        """
        logger.info("测试场景3：使用 symbol 筛选")

        # 先获取真实 symbol
        base_response = trading_order_api.list_securities(size=1)
        assert_status_ok(base_response)
        base_securities = base_response.json().get("content", [])

        if not base_securities:
            pytest.skip("无证券数据，跳过")

        real_symbol = base_securities[0].get("symbol", "")
        if not real_symbol:
            logger.info("  symbol 字段为空，使用 AAPL 作为关键词")
            real_symbol = "AAPL"

        response = trading_order_api.list_securities(symbol=real_symbol, size=10)
        assert_status_ok(response)

        securities = response.json().get("content", [])
        logger.info(f"  symbol='{real_symbol}' 筛选返回 {len(securities)} 个")

        if securities:
            for sec in securities:
                sec_symbol = sec.get("symbol", "") or ""
                assert real_symbol.upper() in sec_symbol.upper() or sec_symbol.upper() in real_symbol.upper(), \
                    f"返回证券 symbol='{sec_symbol}' 不包含关键词 '{real_symbol}'"
            logger.info(f"✓ symbol 筛选验证通过")

    def test_list_securities_with_cusip_filter(self, trading_order_api):
        """
        测试场景4：使用 CUSIP 筛选
        先 list 获取真实 cusip，再用它筛选，验证返回数据匹配
        验证点：
        1. 接口返回 200
        2. 返回的每条数据 cusip 与筛选值一致
        """
        logger.info("测试场景4：使用 CUSIP 筛选")

        # 先获取真实 cusip
        base_response = trading_order_api.list_securities(size=1)
        assert_status_ok(base_response)
        base_securities = base_response.json().get("content", [])

        real_cusip = None
        if base_securities:
            real_cusip = base_securities[0].get("cusip")

        if not real_cusip:
            # 使用苹果公司的已知 cusip 测试
            real_cusip = "037833100"
            logger.info(f"  无法获取真实 cusip，使用 AAPL CUSIP: {real_cusip}")

        response = trading_order_api.list_securities(cusip=real_cusip, size=10)
        assert_status_ok(response)

        securities = response.json().get("content", [])
        logger.info(f"  cusip='{real_cusip}' 筛选返回 {len(securities)} 个")

        if securities:
            for sec in securities:
                assert sec.get("cusip") == real_cusip, \
                    f"返回证券 cusip='{sec.get('cusip')}' 与筛选值 '{real_cusip}' 不一致"
            logger.info(f"✓ CUSIP 筛选验证通过")
        else:
            logger.info(f"  cusip='{real_cusip}' 在当前环境无数据，验证接口接受参数正常")

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
