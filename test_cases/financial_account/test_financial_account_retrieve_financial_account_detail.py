"""
Financial Account Detail 接口测试用例
测试 GET /api/v1/cores/{core}/financial-accounts/:financial_account_id 接口
对应文档标题: Retrieve Financial Account Detail
"""
import pytest
from api.financial_account_api import FinancialAccountAPI
from utils.logger import logger


@pytest.mark.financial_account
@pytest.mark.detail_api
class TestFinancialAccountRetrieveFinancialAccountDetail:
    """
    Financial Account 详情查询接口测试用例集
    """

    def test_retrieve_financial_account_detail_success(self, login_session):
        """
        测试场景1：成功获取 Financial Account 详情
        验证点：
        1. 先获取列表，取第一个 Financial Account ID
        2. 调用详情接口返回 200
        3. 返回的 id 与请求的 id 一致
        4. 必需字段均存在
        """
        fa_api = FinancialAccountAPI(session=login_session)

        logger.info("获取 Financial Accounts 列表")
        list_response = fa_api.list_financial_accounts(page=0, size=1)
        assert list_response.status_code == 200, \
            f"List 接口返回状态码错误: {list_response.status_code}"

        parsed_list = fa_api.parse_list_response(list_response)
        accounts = parsed_list.get("content", [])

        if not accounts:
            pytest.skip("没有可用的 Financial Account 进行详情查询测试")

        financial_account_id = accounts[0].get("id")
        logger.info(f"  使用 Financial Account ID: {financial_account_id}")

        logger.info("调用 Retrieve Financial Account Detail 接口")
        detail_response = fa_api.get_financial_account_detail(financial_account_id)

        logger.info("验证 HTTP 状态码为 200")
        assert detail_response.status_code == 200, \
            f"Detail 接口返回状态码错误: {detail_response.status_code}, Response: {detail_response.text}"

        parsed_detail = fa_api.parse_detail_response(detail_response)
        assert not parsed_detail.get("error"), f"Detail 响应解析失败: {parsed_detail.get('message')}"

        # 验证 ID 一致性
        logger.info("验证返回的 id 与请求的 id 一致")
        assert parsed_detail.get("id") == financial_account_id, \
            f"ID 不一致: 请求 {financial_account_id}, 返回 {parsed_detail.get('id')}"

        # 验证必需字段（assert，不是 logger）
        logger.info("验证必需字段存在")
        required_fields = ["id", "name", "account_number", "status", "source", "balance"]
        for field in required_fields:
            assert field in parsed_detail, f"Financial Account 详情缺少必需字段: '{field}'"
            logger.info(f"  ✓ {field}: {parsed_detail.get(field)}")

        logger.info("✓ Financial Account 详情获取成功")

    def test_retrieve_financial_account_detail_id_consistency(self, login_session):
        """
        测试场景2：验证详情数据与列表数据一致性
        验证点：
        1. 详情接口返回的关键字段值与列表接口一致
        """
        fa_api = FinancialAccountAPI(session=login_session)

        logger.info("获取 Financial Accounts 列表")
        list_response = fa_api.list_financial_accounts(page=0, size=1)
        assert list_response.status_code == 200

        parsed_list = fa_api.parse_list_response(list_response)
        accounts = parsed_list.get("content", [])

        if not accounts:
            pytest.skip("没有可用的 Financial Account 进行测试")

        fa_from_list = accounts[0]
        financial_account_id = fa_from_list.get("id")

        logger.info("调用详情接口")
        detail_response = fa_api.get_financial_account_detail(financial_account_id)
        assert detail_response.status_code == 200

        fa_from_detail = fa_api.parse_detail_response(detail_response)
        assert not fa_from_detail.get("error")

        # 验证关键字段一致
        fields_to_compare = ["id", "name", "account_number", "status", "source", "record_type"]
        logger.info("验证列表与详情关键字段一致")
        for field in fields_to_compare:
            list_val = fa_from_list.get(field)
            detail_val = fa_from_detail.get(field)
            assert list_val == detail_val, \
                f"字段 '{field}' 列表={list_val} 与详情={detail_val} 不一致"
            logger.info(f"  ✓ {field}: {detail_val}")

        logger.info("✓ 列表与详情数据一致性验证通过")

    def test_retrieve_financial_account_detail_with_invalid_id(self, login_session):
        """
        测试场景3：使用无效 ID 获取详情
        验证点：
        1. 服务器返回 200 OK（统一错误处理设计）
        2. 响应体包含错误信息（code != 200）
        """
        fa_api = FinancialAccountAPI(session=login_session)

        logger.info("使用无效 ID 调用详情接口")
        detail_response = fa_api.get_financial_account_detail("invalid_financial_account_id_12345")

        assert detail_response.status_code == 200, \
            f"服务器应该返回 200，实际返回 {detail_response.status_code}"

        response_body = detail_response.json()
        assert "error" in detail_response.text.lower() or response_body.get("code") != 200, \
            "无效 ID 应该返回错误信息"

        logger.info(f"✓ 无效 ID 正确返回错误，code={response_body.get('code')}")

    def test_retrieve_financial_account_detail_with_invisible_id(self, login_session):
        """
        测试场景5：使用不在当前用户 visible 范围内的 FA ID 获取详情
        验证点：
        1. 使用越权 FA ID：241010195850134683（ACTC Yhan FA，属于 Yingying）
        2. 服务器返回 200 OK
        3. code=506, error_message 包含 "visibility permission deny"
        4. data 为 null
        """
        fa_api = FinancialAccountAPI(session=login_session)

        invisible_fa_id = "241010195850134683"  # ACTC Yhan FA，不属于当前用户
        logger.info(f"使用越权 FA ID: {invisible_fa_id}")

        detail_response = fa_api.get_financial_account_detail(invisible_fa_id)
        assert detail_response.status_code == 200, \
            f"服务器应该返回 200，实际: {detail_response.status_code}"

        response_body = detail_response.json()
        logger.info(f"  响应: {response_body}")

        assert response_body.get("code") == 506, \
            f"越权 FA ID 应该返回 code=506，实际: {response_body.get('code')}"
        assert "visibility permission deny" in response_body.get("error_message", "").lower(), \
            f"error_message 应包含 'visibility permission deny'，实际: {response_body.get('error_message')}"
        assert response_body.get("data") is None, "visibility 拒绝时 data 应为 null"

        logger.info(f"✓ 越权 FA ID 校验通过: code=506")
        """
        测试场景4：验证详情响应的完整数据结构
        验证点：
        1. 接口返回 200
        2. 包含完整的 Financial Account 信息字段
        """
        fa_api = FinancialAccountAPI(session=login_session)

        logger.info("获取 Financial Accounts 列表")
        list_response = fa_api.list_financial_accounts(page=0, size=1)
        assert list_response.status_code == 200

        parsed_list = fa_api.parse_list_response(list_response)
        accounts = parsed_list.get("content", [])

        if not accounts:
            pytest.skip("没有可用的 Financial Account 进行测试")

        financial_account_id = accounts[0].get("id")

        logger.info("调用详情接口")
        detail_response = fa_api.get_financial_account_detail(financial_account_id)
        assert detail_response.status_code == 200

        parsed_detail = fa_api.parse_detail_response(detail_response)
        assert not parsed_detail.get("error")

        # 验证完整字段集合
        detail_fields = [
            "id", "name", "account_number", "status", "source",
            "balance", "available_balance", "pending_deposits",
            "pending_withdrawals", "record_type", "sub_type", "created_date"
        ]

        logger.info("验证详情响应字段")
        for field in detail_fields:
            assert field in parsed_detail, f"详情响应缺少字段: '{field}'"
            logger.info(f"  ✓ {field}: {parsed_detail.get(field)}")

        logger.info("✓ 详情响应结构验证完成")
