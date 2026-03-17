"""
账户关联 Financial Accounts 接口测试用例
测试 GET /api/v1/cores/{core}/accounts/{account_id}/financial-accounts 接口
"""
import pytest
from utils.logger import logger
from utils.assertions import (
    assert_status_ok,
    assert_response_parsed,
    assert_list_structure,
    assert_pagination,
    assert_empty_result,
    assert_fields_present
)


class TestAccountFinancialAccounts:
    """
    账户关联 Financial Accounts 接口测试用例集
    """

    def _get_account_id(self, account_api):
        """辅助：获取第一个可用的 account_id"""
        resp = account_api.list_accounts(size=1)
        assert_status_ok(resp)
        parsed = account_api.parse_list_response(resp)
        content = parsed.get("content", [])
        return content[0]["id"] if content else None

    # ──────────────────────────────────────────────
    # 基础成功场景
    # ──────────────────────────────────────────────
    def test_get_financial_accounts_success(self, account_api):
        """
        测试场景1：成功获取账户关联的 Financial Accounts
        验证点：
        1. 接口返回 200
        2. 返回结构符合预期
        3. 如有数据，必需字段存在
        """
        account_id = self._get_account_id(account_api)
        if not account_id:
            pytest.skip("没有可用的账户数据，跳过 Financial Accounts 测试")

        financial_response = account_api.get_financial_accounts(account_id)
        assert_status_ok(financial_response)

        parsed_financial = account_api.parse_financial_accounts_response(financial_response)
        assert_response_parsed(parsed_financial)
        assert_list_structure(parsed_financial, has_pagination=True)

        financial_accounts = parsed_financial["content"]
        if financial_accounts:
            required_fields = ["id", "name", "account_number", "status", "record_type"]
            assert_fields_present(financial_accounts[0], required_fields, obj_name="Financial Account")
            logger.info(f"  示例 FA: {financial_accounts[0].get('id')} - {financial_accounts[0].get('name')}")

        logger.info(f"✓ 成功获取 Financial Accounts: 总数={parsed_financial['total_elements']}")

    # ──────────────────────────────────────────────
    # 非必填字段单独验证
    # ──────────────────────────────────────────────
    def test_get_financial_accounts_filter_by_status(self, account_api):
        """
        测试场景2：使用 status 筛选 Financial Accounts
        先获取真实 status，再用它筛选，验证每条数据 status 匹配
        验证点：
        1. 接口返回 200
        2. 每条 status 与筛选值一致
        """
        account_id = self._get_account_id(account_api)
        if not account_id:
            pytest.skip("没有可用的账户数据")

        # 先获取真实 status
        base_resp = account_api.get_financial_accounts(account_id, size=1)
        assert_status_ok(base_resp)
        base_parsed = account_api.parse_financial_accounts_response(base_resp)
        fa_list = base_parsed.get("content", [])

        if not fa_list:
            pytest.skip("该账户无 Financial Accounts，跳过 status 筛选测试")

        real_status = fa_list[0].get("status")
        if not real_status:
            pytest.skip("status 字段为空，跳过")

        logger.info(f"  使用真实 status: '{real_status}'")

        financial_response = account_api.get_financial_accounts(account_id, status=real_status, size=10)
        assert_status_ok(financial_response)

        parsed_financial = account_api.parse_financial_accounts_response(financial_response)
        fa_list = parsed_financial.get("content", [])

        if fa_list:
            for fa in fa_list:
                assert fa.get("status") == real_status, \
                    f"返回了 status={fa.get('status')} 不匹配筛选值 '{real_status}'"

        logger.info(f"✓ status='{real_status}' 筛选验证通过，返回 {len(fa_list)} 条")

    def test_get_financial_accounts_filter_by_name(self, account_api):
        """
        测试场景3：使用 name 模糊筛选 Financial Accounts
        先获取真实 name，取前4字符作为关键词，验证返回数据均包含该关键词
        验证点：
        1. 接口返回 200
        2. 每条数据 name 包含关键词（不区分大小写）
        """
        account_id = self._get_account_id(account_api)
        if not account_id:
            pytest.skip("没有可用的账户数据")

        base_resp = account_api.get_financial_accounts(account_id, size=1)
        assert_status_ok(base_resp)
        base_parsed = account_api.parse_financial_accounts_response(base_resp)
        fa_list = base_parsed.get("content", [])

        if not fa_list:
            pytest.skip("该账户无 Financial Accounts，跳过 name 筛选测试")

        real_name = fa_list[0].get("name", "")
        if not real_name or len(real_name) < 2:
            pytest.skip("FA name 为空或过短，跳过")

        keyword = real_name[:4]
        logger.info(f"  使用关键词: '{keyword}'（来自 name='{real_name}'）")

        financial_response = account_api.get_financial_accounts(account_id, name=keyword, size=10)
        assert_status_ok(financial_response)

        parsed_financial = account_api.parse_financial_accounts_response(financial_response)
        fa_list = parsed_financial.get("content", [])

        if fa_list:
            for fa in fa_list:
                assert keyword.lower() in (fa.get("name") or "").lower(), \
                    f"name='{fa.get('name')}' 不包含关键词 '{keyword}'"

        logger.info(f"✓ name 模糊筛选验证通过，返回 {len(fa_list)} 条")

    def test_get_financial_accounts_filter_by_account_number(self, account_api):
        """
        测试场景4：使用 account_number 筛选
        先获取真实 account_number，再用它精确筛选，验证结果匹配
        验证点：
        1. 接口返回 200
        2. 返回的数据 account_number 与筛选值一致
        """
        account_id = self._get_account_id(account_api)
        if not account_id:
            pytest.skip("没有可用的账户数据")

        base_resp = account_api.get_financial_accounts(account_id, size=1)
        assert_status_ok(base_resp)
        base_parsed = account_api.parse_financial_accounts_response(base_resp)
        fa_list = base_parsed.get("content", [])

        if not fa_list:
            pytest.skip("该账户无 Financial Accounts，跳过 account_number 筛选测试")

        real_acc_num = fa_list[0].get("account_number")
        if not real_acc_num:
            pytest.skip("account_number 字段为空，跳过")

        logger.info(f"  使用真实 account_number: '{real_acc_num}'")

        financial_response = account_api.get_financial_accounts(account_id, account_number=real_acc_num, size=10)
        assert_status_ok(financial_response)

        parsed_financial = account_api.parse_financial_accounts_response(financial_response)
        fa_list = parsed_financial.get("content", [])

        if fa_list:
            for fa in fa_list:
                assert fa.get("account_number") == real_acc_num, \
                    f"account_number='{fa.get('account_number')}' 与筛选值 '{real_acc_num}' 不一致"

        logger.info(f"✓ account_number 筛选验证通过，返回 {len(fa_list)} 条")

    # ──────────────────────────────────────────────
    # 组合筛选
    # ──────────────────────────────────────────────
    def test_get_financial_accounts_filter_status_and_name_combined(self, account_api):
        """
        测试场景5：status + name 组合筛选
        先获取真实数据，构造组合条件，验证返回数据均满足两个条件
        验证点：
        1. 接口返回 200
        2. 每条数据 status 匹配且 name 包含关键词
        """
        account_id = self._get_account_id(account_api)
        if not account_id:
            pytest.skip("没有可用的账户数据")

        base_resp = account_api.get_financial_accounts(account_id, size=1)
        assert_status_ok(base_resp)
        base_parsed = account_api.parse_financial_accounts_response(base_resp)
        fa_list = base_parsed.get("content", [])

        if not fa_list:
            pytest.skip("该账户无 Financial Accounts，跳过组合筛选测试")

        real_status = fa_list[0].get("status")
        real_name = fa_list[0].get("name", "")

        if not real_status or not real_name or len(real_name) < 2:
            pytest.skip("status 或 name 为空，跳过组合筛选测试")

        keyword = real_name[:4]
        logger.info(f"  组合筛选: status='{real_status}' + name='{keyword}'")

        financial_response = account_api.get_financial_accounts(
            account_id, status=real_status, name=keyword, size=10
        )
        assert_status_ok(financial_response)

        parsed_financial = account_api.parse_financial_accounts_response(financial_response)
        fa_list = parsed_financial.get("content", [])

        if fa_list:
            for fa in fa_list:
                assert fa.get("status") == real_status, \
                    f"status='{fa.get('status')}' 与筛选值 '{real_status}' 不一致"
                assert keyword.lower() in (fa.get("name") or "").lower(), \
                    f"name='{fa.get('name')}' 不包含关键词 '{keyword}'"

        logger.info(f"✓ status + name 组合筛选验证通过，返回 {len(fa_list)} 条")

    # ──────────────────────────────────────────────
    # 空结果 & 分页
    # ──────────────────────────────────────────────
    def test_get_financial_accounts_empty_result(self, account_api):
        """
        测试场景6：使用不存在的筛选条件 → 返回空列表
        验证点：
        1. 接口返回 200
        2. content 为空列表
        """
        account_id = self._get_account_id(account_api)
        if not account_id:
            pytest.skip("没有可用的账户数据")

        financial_response = account_api.get_financial_accounts(
            account_id, account_number="NONEXISTENT-FA-999999"
        )
        assert_status_ok(financial_response)

        parsed_financial = account_api.parse_financial_accounts_response(financial_response)
        assert_response_parsed(parsed_financial)
        assert_empty_result(parsed_financial)

        logger.info("✓ 空结果验证通过")

    def test_get_financial_accounts_pagination(self, account_api):
        """
        测试场景7：验证分页功能
        验证点：
        1. page=0, size=5 分页信息正确
        2. 返回数量 <= size
        """
        account_id = self._get_account_id(account_api)
        if not account_id:
            pytest.skip("没有可用的账户数据")

        financial_response = account_api.get_financial_accounts(account_id, page=0, size=5)
        assert_status_ok(financial_response)

        parsed_financial = account_api.parse_financial_accounts_response(financial_response)
        assert_response_parsed(parsed_financial)
        assert_pagination(parsed_financial, expected_size=5, expected_page=0)

        logger.info(f"✓ 分页验证通过: 总数={parsed_financial['total_elements']}, "
                    f"返回 {len(parsed_financial['content'])} 条")

    # ──────────────────────────────────────────────
    # 越权验证
    # ──────────────────────────────────────────────
    def test_get_financial_accounts_with_invisible_account_id(self, account_api):
        """
        测试场景8：使用不在当前用户 visible 范围内的 account_id
        验证点：
        1. 使用他人账户 241010195849720143（yhan account Sanchez）
        2. 服务器返回 200 OK
        3. 返回空列表 或 code=506（按 visible 范围过滤）
        """
        invisible_account_id = "241010195849720143"  # yhan account Sanchez
        logger.info(f"使用不在 visible 范围内的 account_id: {invisible_account_id}")

        financial_response = account_api.get_financial_accounts(invisible_account_id)
        assert financial_response.status_code == 200, \
            f"服务器应该返回 200，实际: {financial_response.status_code}"

        response_body = financial_response.json()
        logger.info(f"  响应: {response_body}")

        if isinstance(response_body, dict) and response_body.get("code") == 506:
            logger.info(f"  返回 code=506 visibility permission deny")
        else:
            parsed_financial = account_api.parse_financial_accounts_response(financial_response)
            fa_list = parsed_financial.get("content", [])
            assert len(fa_list) == 0, \
                f"越权 account_id 应返回空列表，实际返回 {len(fa_list)} 条"
            logger.info("  越权 account_id 返回空 Financial Accounts 列表")

        logger.info("✓ 越权 account_id Financial Accounts 查询验证通过")
