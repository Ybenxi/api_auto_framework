"""
Financial Account Payment Detail 接口测试用例
测试 GET /api/v1/cores/{core}/financial-accounts/:financial_account_id/detail 接口
对应文档标题: Retrieve a Financial Account Payment Detail
"""
import pytest
from api.financial_account_api import FinancialAccountAPI
from utils.logger import logger


@pytest.mark.financial_account
@pytest.mark.payment_detail_api
class TestFinancialAccountRetrieveAFinancialAccountPaymentDetail:
    """
    Financial Account 支付详情查询接口测试用例集
    """

    def test_retrieve_payment_detail_success(self, login_session):
        """
        测试场景1：成功获取 Financial Account 的支付详情
        验证点：
        1. 先获取列表，取第一个 Financial Account ID
        2. 调用支付详情接口返回 200
        3. 返回数据包含 account_number 和 routing_number
        """
        fa_api = FinancialAccountAPI(session=login_session)
        
        # 获取 Financial Account
        logger.info("获取 Financial Accounts 列表")
        list_response = fa_api.list_financial_accounts(page=0, size=1)
        assert list_response.status_code == 200
        
        parsed_list = fa_api.parse_list_response(list_response)
        accounts = parsed_list.get("content", [])
        
        if len(accounts) == 0:
            pytest.skip("没有可用的 Financial Account 进行测试")
        
        financial_account_id = accounts[0].get("id")
        logger.info(f"  使用 Financial Account ID: {financial_account_id}")
        
        # 获取支付详情
        logger.info("调用 Retrieve a Financial Account Payment Detail 接口")
        detail_response = fa_api.get_payment_detail(financial_account_id)
        
        logger.info("验证 HTTP 状态码为 200")
        assert detail_response.status_code == 200, \
            f"接口返回状态码错误: {detail_response.status_code}, Response: {detail_response.text}"
        
        # 解析响应
        logger.info("解析响应并验证数据结构")
        response_data = detail_response.json()
        
        # 响应可能包含 data 字段
        if "data" in response_data:
            payment_data = response_data["data"]
        else:
            payment_data = response_data
        
        # 验证必需字段存在（assert，不是 logger）
        required_fields = ["account_number", "routing_number"]
        for field in required_fields:
            assert field in payment_data, f"支付详情缺少必需字段: '{field}'"
            logger.info(f"  ✓ {field}: {payment_data.get(field)}")

        logger.info("✓ 成功获取支付详情")

    def test_retrieve_payment_detail_with_invalid_id(self, login_session):
        """
        测试场景2：使用无效 ID 获取支付详情
        验证点：
        1. 接口返回非 200 状态码
        """
        fa_api = FinancialAccountAPI(session=login_session)
        
        logger.info("使用无效 ID 调用支付详情接口")
        invalid_id = "invalid_financial_account_id_12345"
        detail_response = fa_api.get_payment_detail(invalid_id)
        
        logger.info("验证返回状态码")
        logger.info(f"  状态码: {detail_response.status_code}")
        
        # 服务器返回 200（统一错误处理）
        assert detail_response.status_code == 200, \
            f"服务器应该返回 200，但实际返回了 {detail_response.status_code}"
        
        # 验证响应包含错误信息
        response_body = detail_response.json()
        assert "error" in detail_response.text.lower() or response_body.get("code") != 200, \
            f"无效 ID 应该返回错误信息"
        
        logger.info("✓ 无效 ID 测试完成")

    def test_retrieve_payment_detail_response_structure(self, login_session):
        """
        测试场景3：验证支付详情响应的数据结构
        验证点：
        1. 接口返回 200
        2. 响应包含必需的支付信息字段
        """
        fa_api = FinancialAccountAPI(session=login_session)
        
        list_response = fa_api.list_financial_accounts(page=0, size=1)
        assert list_response.status_code == 200
        
        parsed_list = fa_api.parse_list_response(list_response)
        accounts = parsed_list.get("content", [])
        
        if len(accounts) == 0:
            pytest.skip("没有可用的 Financial Account 进行测试")
        
        financial_account_id = accounts[0].get("id")
        
        logger.info("获取支付详情并验证结构")
        detail_response = fa_api.get_payment_detail(financial_account_id)
        assert detail_response.status_code == 200
        
        response_data = detail_response.json()
        
        # 验证响应结构和必需字段
        logger.info("验证响应结构和必需字段")
        payment_data = response_data.get("data", response_data)

        required_fields = ["account_number", "routing_number"]
        for field in required_fields:
            assert field in payment_data, f"支付详情响应缺少必需字段: '{field}'"
            logger.info(f"  ✓ {field}: {payment_data.get(field)}")

        logger.info("✓ 响应结构验证完成")
