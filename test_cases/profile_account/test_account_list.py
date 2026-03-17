"""
账户列表接口测试用例
测试 GET /api/v1/cores/{core}/accounts 接口
"""
import pytest
from data.enums import BusinessEntityType, AccountStatus
from utils.logger import logger
from utils.assertions import (
    assert_status_ok,
    assert_response_parsed,
    assert_list_structure,
    assert_enum_filter,
    assert_string_contains_filter,
    assert_pagination,
    assert_empty_result,
    assert_fields_present
)


class TestAccountList:
    """
    账户列表接口测试用例集
    """

    def test_list_accounts_basic(self, account_api):
        """
        测试场景1：基础列表查询 - 验证接口可用性
        验证点：
        1. HTTP 状态码为 200
        2. 响应中包含 content 字段
        3. content 是一个列表
        4. 响应结构完整（包含分页信息）
        """
        response = account_api.list_accounts()
        assert_status_ok(response)

        parsed = account_api.parse_list_response(response)
        assert_response_parsed(parsed)
        assert_list_structure(parsed, has_pagination=True)

        logger.info(f"✓ 基础查询成功，返回 {len(parsed['content'])} 个账户，总计 {parsed['total_elements']} 个")

    # ──────────────────────────────────────────────
    # business_entity_type 全枚举覆盖
    # ──────────────────────────────────────────────
    @pytest.mark.parametrize("entity_type", list(BusinessEntityType))
    def test_list_accounts_filter_by_entity_type_all_values(self, account_api, entity_type):
        """
        测试场景2：business_entity_type 全枚举筛选（覆盖全部13个枚举值）
        验证点：
        1. 接口返回 200
        2. 如有数据，每条 business_entity_type 与筛选值一致
        """
        response = account_api.list_accounts(business_entity_type=entity_type, size=10)
        assert_status_ok(response)

        parsed = account_api.parse_list_response(response)
        assert_response_parsed(parsed)

        accounts = parsed["content"]
        logger.info(f"  business_entity_type='{entity_type.value}' 返回 {len(accounts)} 条")

        if accounts:
            assert_enum_filter(accounts, "business_entity_type", entity_type, allow_none=True)
            logger.info(f"✓ business_entity_type='{entity_type.value}' 筛选验证通过")

    # ──────────────────────────────────────────────
    # status 全枚举覆盖（5个值）
    # ──────────────────────────────────────────────
    @pytest.mark.parametrize("account_status", list(AccountStatus))
    def test_list_accounts_filter_by_status_all_values(self, account_api, account_status):
        """
        测试场景3：status 全枚举筛选（覆盖 Active/Declined/Terminated/Pending/Hold 全部5个值）
        验证点：
        1. 接口返回 200
        2. 如有数据，每条 account_status 与筛选值一致
        """
        response = account_api.list_accounts(status=account_status, size=10)
        assert_status_ok(response)

        parsed = account_api.parse_list_response(response)
        assert_response_parsed(parsed)

        accounts = parsed["content"]
        logger.info(f"  status='{account_status.value}' 返回 {len(accounts)} 条")

        if accounts:
            for acc in accounts:
                assert acc.get("account_status") == account_status.value, \
                    f"筛选结果包含非 {account_status.value} 状态: account_status={acc.get('account_status')}, id={acc.get('id')}"
            logger.info(f"✓ status='{account_status.value}' 筛选验证通过")

    # ──────────────────────────────────────────────
    # name 筛选
    # ──────────────────────────────────────────────
    def test_list_accounts_filter_by_name_real_value(self, account_api):
        """
        测试场景4：使用真实 name 关键词模糊搜索
        先 list 获取真实账户名，取前4字符作关键词，验证返回数据均包含该关键词
        验证点：
        1. 接口返回 200
        2. 返回的所有账户名包含搜索关键词（不区分大小写）
        """
        base_response = account_api.list_accounts(size=1)
        assert_status_ok(base_response)
        base_parsed = account_api.parse_list_response(base_response)

        if not base_parsed["content"]:
            pytest.skip("无账户数据，跳过 name 筛选测试")

        real_name = base_parsed["content"][0].get("account_name", "")
        if not real_name or len(real_name) < 2:
            pytest.skip("account_name 为空或过短，跳过")

        keyword = real_name[:4]
        logger.info(f"  使用关键词: '{keyword}'（来自 account_name='{real_name}'）")

        response = account_api.list_accounts(name=keyword, size=10)
        assert_status_ok(response)

        parsed = account_api.parse_list_response(response)
        assert_response_parsed(parsed)

        accounts = parsed["content"]
        assert len(accounts) > 0, f"关键词 '{keyword}' 应能匹配到数据"

        for acc in accounts:
            assert keyword.lower() in (acc.get("account_name") or "").lower(), \
                f"返回账户名 '{acc.get('account_name')}' 不包含关键词 '{keyword}'"

        logger.info(f"✓ name 模糊筛选验证通过，返回 {len(accounts)} 条")

    def test_list_accounts_filter_by_name_nonexistent(self, account_api):
        """
        测试场景5：使用不存在的 name 搜索 → 返回空列表
        验证点：
        1. 接口返回 200
        2. content 是空列表
        3. total_elements 为 0
        """
        response = account_api.list_accounts(name="NONEXISTENT_NAME_XYZXYZ_999")
        assert_status_ok(response)

        parsed = account_api.parse_list_response(response)
        assert_response_parsed(parsed)
        assert_empty_result(parsed)

        logger.info("✓ 不存在 name 返回空列表验证通过")

    # ──────────────────────────────────────────────
    # 其他字段错误值搜索
    # ──────────────────────────────────────────────
    def test_list_accounts_filter_by_nonexistent_email(self, account_api):
        """
        测试场景6：使用不存在的 email 搜索 → 返回空列表
        验证点：
        1. 接口返回 200
        2. 返回空列表
        """
        response = account_api.list_accounts(email="nonexistent_auto_test@nowhere99.com")
        assert_status_ok(response)

        parsed = account_api.parse_list_response(response)
        assert_response_parsed(parsed)
        assert_empty_result(parsed)

        logger.info("✓ 不存在 email 返回空列表验证通过")

    def test_list_accounts_filter_by_nonexistent_tax_id(self, account_api):
        """
        测试场景7：使用不存在的 tax_id 搜索 → 返回空列表
        验证点：
        1. 接口返回 200
        2. 返回空列表
        """
        response = account_api.list_accounts(tax_id="000-00-9999")
        assert_status_ok(response)

        parsed = account_api.parse_list_response(response)
        assert_response_parsed(parsed)
        assert_empty_result(parsed)

        logger.info("✓ 不存在 tax_id 返回空列表验证通过")

    def test_list_accounts_filter_by_nonexistent_account_number(self, account_api):
        """
        测试场景8：使用不存在的 account_number 搜索 → 返回空列表
        验证点：
        1. 接口返回 200
        2. 返回空列表
        """
        response = account_api.list_accounts(account_number="NONEXISTENT-ACCT-999999")
        assert_status_ok(response)

        parsed = account_api.parse_list_response(response)
        assert_response_parsed(parsed)
        assert_empty_result(parsed)

        logger.info("✓ 不存在 account_number 返回空列表验证通过")

    # ──────────────────────────────────────────────
    # 分页和字段完整性
    # ──────────────────────────────────────────────
    def test_list_accounts_pagination(self, account_api):
        """
        测试场景9：分页功能验证
        验证点：
        1. page=0, size=5 分页信息正确
        2. 返回数量 <= size
        """
        response = account_api.list_accounts(page=0, size=5)
        assert_status_ok(response)

        parsed = account_api.parse_list_response(response)
        assert_response_parsed(parsed)
        assert_pagination(parsed, expected_size=5, expected_page=0)

        logger.info(f"✓ 分页验证通过: 请求5条，实际返回 {len(parsed['content'])} 条")

    def test_list_accounts_response_fields(self, account_api):
        """
        测试场景10：响应字段完整性验证
        验证点：
        1. 返回的账户对象包含必需字段
        """
        response = account_api.list_accounts(size=1)
        assert_status_ok(response)

        parsed = account_api.parse_list_response(response)
        assert_response_parsed(parsed)

        if not parsed["content"]:
            pytest.skip("没有账户数据可供验证")

        account = parsed["content"][0]
        required_fields = ["id", "account_name", "account_number", "account_status", "record_type", "create_time"]
        assert_fields_present(account, required_fields, obj_name="账户对象")

        logger.info(f"✓ 字段完整性验证通过")
        logger.info(f"  示例账户: {account.get('account_number')} - {account.get('account_name')}")

    # ──────────────────────────────────────────────
    # 多条件组合
    # ──────────────────────────────────────────────
    def test_list_accounts_multiple_filters(self, account_api):
        """
        测试场景11：多条件组合筛选
        验证点：
        1. status=Active + business_entity_type=LLC 同时传递
        2. 接口正常返回
        3. 如有数据，字段均匹配
        """
        response = account_api.list_accounts(
            status=AccountStatus.ACTIVE,
            business_entity_type=BusinessEntityType.LLC,
            size=10
        )
        assert_status_ok(response)

        parsed = account_api.parse_list_response(response)
        assert_response_parsed(parsed)

        accounts = parsed["content"]
        logger.info(f"  Active + LLC 组合筛选返回 {len(accounts)} 条")

        if accounts:
            for acc in accounts:
                if acc.get("account_status"):
                    assert acc.get("account_status") == "Active", \
                        f"status 不匹配: {acc.get('account_status')}"
                if acc.get("business_entity_type"):
                    assert acc.get("business_entity_type") == "LLC", \
                        f"business_entity_type 不匹配: {acc.get('business_entity_type')}"

        logger.info("✓ 多条件组合筛选验证通过")
