"""
Sub Account Detail 接口测试用例
测试 GET /api/v1/cores/{core}/sub-accounts/:sub_account_id 接口
对应文档标题: Retrieve Sub Account Detail
"""
import pytest
from api.sub_account_api import SubAccountAPI
from utils.logger import logger


@pytest.mark.sub_account
@pytest.mark.detail_api
class TestSubAccountRetrieveSubAccountDetail:
    """
    Sub Account 详情查询接口测试用例集
    """

    def test_retrieve_sub_account_detail_success(self, login_session):
        """
        测试场景1：成功获取 Sub Account 详情
        验证点：
        1. 先获取列表，取第一个 Sub Account ID
        2. 调用详情接口返回 200
        3. 返回的 id 与请求的 id 一致
        4. 必需字段均存在（assert 断言）
        """
        sa_api = SubAccountAPI(session=login_session)

        logger.info("获取 Sub Accounts 列表")
        list_response = sa_api.list_sub_accounts(page=0, size=1)
        assert list_response.status_code == 200, \
            f"List 接口返回状态码错误: {list_response.status_code}"

        parsed_list = sa_api.parse_list_response(list_response)
        sub_accounts = parsed_list.get("content", [])

        if not sub_accounts:
            pytest.skip("没有可用的 Sub Account 进行详情查询测试")

        sub_account_id = sub_accounts[0].get("id")
        logger.info(f"  使用 Sub Account ID: {sub_account_id}")

        logger.info("调用 Retrieve Sub Account Detail 接口")
        detail_response = sa_api.get_sub_account_detail(sub_account_id)

        logger.info("验证 HTTP 状态码为 200")
        assert detail_response.status_code == 200, \
            f"Detail 接口返回状态码错误: {detail_response.status_code}, Response: {detail_response.text}"

        parsed_detail = sa_api.parse_detail_response(detail_response)
        assert not parsed_detail.get("error"), f"Detail 响应解析失败: {parsed_detail.get('message')}"

        # 验证 ID 一致性
        logger.info("验证返回的 id 与请求的 id 一致")
        assert parsed_detail.get("id") == sub_account_id, \
            f"ID 不一致: 请求 {sub_account_id}, 返回 {parsed_detail.get('id')}"

        # 验证必需字段（assert，不是 logger）
        logger.info("验证必需字段存在")
        required_fields = ["id", "name", "financial_account_id", "status", "balance"]
        for field in required_fields:
            assert field in parsed_detail, f"Sub Account 详情缺少必需字段: '{field}'"
            logger.info(f"  ✓ {field}: {parsed_detail.get(field)}")

        logger.info("✓ Sub Account 详情获取成功")

    def test_retrieve_sub_account_detail_id_consistency(self, login_session):
        """
        测试场景2：验证详情数据与列表数据一致性
        验证点：
        1. 详情接口返回的关键字段值与列表接口一致
        """
        sa_api = SubAccountAPI(session=login_session)

        logger.info("获取 Sub Accounts 列表")
        list_response = sa_api.list_sub_accounts(page=0, size=1)
        assert list_response.status_code == 200

        parsed_list = sa_api.parse_list_response(list_response)
        sub_accounts = parsed_list.get("content", [])

        if not sub_accounts:
            pytest.skip("没有可用的 Sub Account 进行测试")

        sa_from_list = sub_accounts[0]
        sub_account_id = sa_from_list.get("id")

        logger.info("调用详情接口")
        detail_response = sa_api.get_sub_account_detail(sub_account_id)
        assert detail_response.status_code == 200

        sa_from_detail = sa_api.parse_detail_response(detail_response)
        assert not sa_from_detail.get("error")

        # 验证关键字段一致
        fields_to_compare = ["id", "name", "financial_account_id", "status"]
        logger.info("验证列表与详情关键字段一致")
        for field in fields_to_compare:
            list_val = sa_from_list.get(field)
            detail_val = sa_from_detail.get(field)
            assert list_val == detail_val, \
                f"字段 '{field}' 列表={list_val} 与详情={detail_val} 不一致"
            logger.info(f"  ✓ {field}: {detail_val}")

        logger.info("✓ 列表与详情数据一致性验证通过")

    def test_retrieve_sub_account_detail_with_invalid_id(self, login_session):
        """
        测试场景3：使用无效 ID 获取详情
        验证点：
        1. 服务器返回 200 OK（统一错误处理设计）
        2. 响应体包含错误信息（code != 200）
        """
        sa_api = SubAccountAPI(session=login_session)

        logger.info("使用无效 ID 调用详情接口")
        detail_response = sa_api.get_sub_account_detail("invalid_sub_account_id_12345")

        assert detail_response.status_code == 200, \
            f"服务器应该返回 200，实际返回 {detail_response.status_code}"

        response_body = detail_response.json()
        assert "error" in detail_response.text.lower() or response_body.get("code") != 200, \
            "无效 ID 应该返回错误信息"

        logger.info(f"✓ 无效 ID 正确返回错误，code={response_body.get('code')}")

    def test_retrieve_sub_account_detail_response_structure(self, login_session):
        """
        测试场景4：验证详情响应的完整数据结构
        验证点：
        1. 接口返回 200
        2. 包含完整的 Sub Account 信息字段
        """
        sa_api = SubAccountAPI(session=login_session)

        logger.info("获取 Sub Accounts 列表")
        list_response = sa_api.list_sub_accounts(page=0, size=1)
        assert list_response.status_code == 200

        parsed_list = sa_api.parse_list_response(list_response)
        sub_accounts = parsed_list.get("content", [])

        if not sub_accounts:
            pytest.skip("没有可用的 Sub Account 进行测试")

        sub_account_id = sub_accounts[0].get("id")

        logger.info("调用详情接口")
        detail_response = sa_api.get_sub_account_detail(sub_account_id)
        assert detail_response.status_code == 200

        parsed_detail = sa_api.parse_detail_response(detail_response)
        assert not parsed_detail.get("error")

        detail_fields = [
            "id", "name", "financial_account_id", "status",
            "balance", "available_balance", "account_identifier",
            "created_date"
        ]

        logger.info("验证详情响应字段")
        for field in detail_fields:
            assert field in parsed_detail, f"详情响应缺少字段: '{field}'"
            logger.info(f"  ✓ {field}: {parsed_detail.get(field)}")

        logger.info("✓ 详情响应结构验证完成")

    def test_retrieve_sub_account_detail_with_invisible_id(self, login_session):
        """
        测试场景5：使用不在当前用户 visible 范围内的 sub_account_id 查询详情
        验证点：
        1. 使用他人的 Sub Account（通过越权 FA ID 关联，实际不在 visible 范围内）
        2. 服务器返回 200 OK（统一错误处理设计）
        3. 响应体 code == 506
        4. error_message 包含 "visibility permission deny"
        5. data 为 null
        """
        sa_api = SubAccountAPI(session=login_session)

        # 使用不在当前用户 visible 范围内的 Sub Account ID
        # 通过越权账户 241010195849720143（yhan account Sanchez）关联的 sub account
        invisible_sa_id = "241010195849720143"  # yhan account（不属于当前用户）
        logger.info(f"使用不在 visible 范围内的 Sub Account ID: {invisible_sa_id}")

        detail_response = sa_api.get_sub_account_detail(invisible_sa_id)

        assert detail_response.status_code == 200, \
            f"服务器应该返回 200（统一错误处理），实际: {detail_response.status_code}"

        response_body = detail_response.json()
        logger.info(f"  响应: {response_body}")

        assert response_body.get("code") == 506, \
            f"越权 Sub Account ID 应该返回 code=506，实际: {response_body.get('code')}"

        error_msg = response_body.get("error_message", "")
        assert "visibility permission deny" in error_msg.lower(), \
            f"error_message 应包含 'visibility permission deny'，实际: {error_msg}"

        assert response_body.get("data") is None, \
            "visibility 拒绝时 data 应为 null"

        logger.info(f"✓ 越权 Sub Account ID 校验通过: code=506, msg={error_msg}")
