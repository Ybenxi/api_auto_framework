"""
Financial Account Related Sub Accounts 接口测试用例
测试 GET /api/v1/cores/{core}/financial-accounts/:financial_account_id/sub-accounts 接口
对应文档标题: Retrieve Related Sub Accounts
"""
import pytest
from api.financial_account_api import FinancialAccountAPI
from utils.logger import logger


def _get_fa_id_with_sub_accounts(fa_api: FinancialAccountAPI, page_size: int = 20):
    """
    遍历 FA 列表，找到第一个有 Sub Account 数据的 FA ID。
    返回 (fa_id, first_sub_account) 或 (None, None)。
    """
    list_resp = fa_api.list_financial_accounts(page=0, size=page_size)
    if list_resp.status_code != 200:
        return None, None

    accounts = fa_api.parse_list_response(list_resp).get("content", [])
    for acc in accounts:
        fa_id = acc.get("id")
        if not fa_id:
            continue
        resp = fa_api.get_related_sub_accounts(fa_id, page=0, size=1)
        if resp.status_code != 200:
            continue
        subs = fa_api.parse_list_response(resp).get("content", [])
        if subs:
            logger.info(f"  找到有 Sub Account 数据的 FA: {fa_id}")
            return fa_id, subs[0]

    return None, None


@pytest.mark.financial_account
@pytest.mark.sub_accounts_api
class TestFinancialAccountRetrieveRelatedSubAccounts:
    """
    Financial Account 相关 Sub Accounts 查询接口测试用例集
    """

    def test_retrieve_related_sub_accounts_success(self, login_session):
        """
        测试场景1：成功获取 Financial Account 相关的 Sub Accounts
        验证点：
        1. 遍历 FA 列表，找到有 Sub Account 数据的 FA
        2. 接口返回 200，total_elements > 0
        3. 返回的所有 Sub Account financial_account_id 均与请求一致
        4. 必需字段存在
        """
        fa_api = FinancialAccountAPI(session=login_session)

        fa_id, first_sub = _get_fa_id_with_sub_accounts(fa_api)
        if not fa_id:
            pytest.skip("未找到有 Sub Account 数据的 Financial Account")

        logger.info(f"使用有数据的 Financial Account ID: {fa_id}")

        sub_response = fa_api.get_related_sub_accounts(fa_id, page=0, size=10)
        assert sub_response.status_code == 200

        parsed_sub = fa_api.parse_list_response(sub_response)
        assert not parsed_sub.get("error")

        sub_accounts = parsed_sub.get("content", [])
        assert len(sub_accounts) > 0, f"FA {fa_id} 应有 Sub Account 数据，但返回空列表"
        logger.info(f"  总数: {parsed_sub['total_elements']}, 返回 {len(sub_accounts)} 个")

        # financial_account_id 一致性验证
        for sa in sub_accounts:
            assert sa.get("financial_account_id") == fa_id, \
                f"Sub Account financial_account_id={sa.get('financial_account_id')} 与请求 {fa_id} 不一致"
        logger.info("  ✓ 所有 Sub Accounts financial_account_id 均一致")

        # 必需字段验证
        sa0 = sub_accounts[0]
        required_fields = ["id", "name", "financial_account_id", "status", "balance"]
        for field in required_fields:
            assert field in sa0, f"Sub Account 缺少必需字段: '{field}'"

        logger.info("✓ Related Sub Accounts 获取成功")

    def test_retrieve_related_sub_accounts_with_name_filter(self, login_session):
        """
        测试场景2：使用 name 模糊筛选 Sub Accounts
        从有数据的 FA 中取真实 name，用前4字符做关键词，验证每条结果包含关键词
        验证点：
        1. 接口返回 200
        2. 返回的每条 Sub Account name 包含筛选关键词
        """
        fa_api = FinancialAccountAPI(session=login_session)

        fa_id, first_sub = _get_fa_id_with_sub_accounts(fa_api)
        if not fa_id or not first_sub:
            pytest.skip("未找到有 Sub Account 数据的 Financial Account")

        real_name = first_sub.get("name", "")
        if not real_name or len(real_name) < 2:
            pytest.skip("name 字段为空或过短，跳过")

        keyword = real_name[:4]
        logger.info(f"使用关键词: '{keyword}'（来自 name='{real_name}'，FA: {fa_id}）")

        sub_response = fa_api.get_related_sub_accounts(fa_id, name=keyword, page=0, size=10)
        assert sub_response.status_code == 200

        parsed_sub = fa_api.parse_list_response(sub_response)
        sub_accounts = parsed_sub.get("content", [])
        assert len(sub_accounts) > 0, f"筛选结果为空，关键词 '{keyword}' 应能匹配"

        for sa in sub_accounts:
            assert keyword.lower() in sa.get("name", "").lower(), \
                f"Sub Account name='{sa.get('name')}' 不包含关键词 '{keyword}'"

        logger.info(f"✓ name 筛选验证通过，返回 {len(sub_accounts)} 条")

    @pytest.mark.parametrize("status", ["Open", "Closed", "Pending"])
    def test_retrieve_related_sub_accounts_with_status_filter(self, login_session, status):
        """
        测试场景3：使用 status 筛选（覆盖全部枚举值）
        使用有数据的 FA，验证每条返回数据的 status 与筛选值一致
        验证点：
        1. 接口返回 200
        2. 返回的每条 Sub Account status 均与筛选值一致
        """
        fa_api = FinancialAccountAPI(session=login_session)

        fa_id, _ = _get_fa_id_with_sub_accounts(fa_api)
        if not fa_id:
            pytest.skip("未找到有 Sub Account 数据的 Financial Account")

        logger.info(f"使用 status='{status}' 筛选 Sub Accounts（FA: {fa_id}）")
        sub_response = fa_api.get_related_sub_accounts(fa_id, status=status, page=0, size=10)

        assert sub_response.status_code == 200
        sub_accounts = fa_api.parse_list_response(sub_response).get("content", [])
        logger.info(f"  返回 {len(sub_accounts)} 条")

        if not sub_accounts:
            logger.info(f"  ⚠️ status='{status}' 无数据，跳过筛选值验证")
        else:
            for sa in sub_accounts:
                assert sa.get("status") == status, \
                    f"筛选结果包含非 {status} 状态: {sa.get('status')}"
            logger.info(f"✓ {len(sub_accounts)} 条数据均为 {status} 状态")

    def test_retrieve_related_sub_accounts_pagination(self, login_session):
        """
        测试场景4：验证 Sub Accounts 列表分页功能
        验证点：
        1. 使用有数据的 FA，确保分页元数据有意义
        2. 分页信息正确（size=5, number=0）
        3. 返回数量 <= size，total_elements > 0
        """
        fa_api = FinancialAccountAPI(session=login_session)

        fa_id, _ = _get_fa_id_with_sub_accounts(fa_api)
        if not fa_id:
            pytest.skip("未找到有 Sub Account 数据的 Financial Account")

        logger.info(f"使用分页参数 page=0, size=5（FA: {fa_id}）")
        sub_response = fa_api.get_related_sub_accounts(fa_id, page=0, size=5)

        assert sub_response.status_code == 200
        parsed_sub = fa_api.parse_list_response(sub_response)

        assert parsed_sub["size"] == 5, f"size 不正确: {parsed_sub['size']}"
        assert parsed_sub["number"] == 0, f"number 不正确: {parsed_sub['number']}"
        assert len(parsed_sub.get("content", [])) <= 5, "返回数量超过 size=5"
        assert parsed_sub["total_elements"] > 0, \
            f"有数据的 FA 分页 total_elements 应 > 0，实际: {parsed_sub['total_elements']}"

        logger.info(f"✓ 分页测试通过: total={parsed_sub['total_elements']}, "
                    f"size={parsed_sub['size']}, page={parsed_sub['number']}, "
                    f"返回={len(parsed_sub.get('content', []))} 个")

    def test_retrieve_related_sub_accounts_response_fields(self, login_session):
        """
        测试场景5：验证 Sub Account 响应字段完整性
        验证点：
        1. 使用有数据的 FA
        2. Sub Account 对象包含必需字段（assert 断言）
        """
        fa_api = FinancialAccountAPI(session=login_session)

        fa_id, first_sub = _get_fa_id_with_sub_accounts(fa_api)
        if not fa_id or not first_sub:
            pytest.skip("未找到有 Sub Account 数据的 Financial Account")

        required_fields = [
            "id", "name", "financial_account_id", "status",
            "balance", "available_balance", "account_identifier"
        ]

        logger.info("验证 Sub Account 字段")
        for field in required_fields:
            assert field in first_sub, f"Sub Account 缺少必需字段: '{field}'"
            logger.info(f"  ✓ {field}: {first_sub.get(field)}")

        logger.info("✓ 字段完整性验证通过")

    def test_retrieve_related_sub_accounts_with_invisible_fa_id(self, login_session):
        """
        测试场景6：使用越权 FA ID 查询 Sub Accounts → 返回空或拒绝
        验证点：
        1. 使用越权 FA ID：241010195850134683（ACTC Yhan FA）
        2. 服务器返回 200
        3. 返回空列表 或 code=506
        """
        fa_api = FinancialAccountAPI(session=login_session)

        invisible_fa_id = "241010195850134683"  # ACTC Yhan FA
        logger.info(f"使用越权 FA ID 查询 Sub Accounts: {invisible_fa_id}")

        sub_response = fa_api.get_related_sub_accounts(invisible_fa_id, page=0, size=10)
        assert sub_response.status_code == 200

        response_body = sub_response.json()
        if isinstance(response_body, dict) and response_body.get("code") == 506:
            logger.info("  返回 code=506 visibility permission deny")
        else:
            parsed_sub = fa_api.parse_list_response(sub_response)
            assert len(parsed_sub.get("content", [])) == 0, \
                f"越权 FA ID 应返回空列表，实际返回 {len(parsed_sub.get('content', []))} 条"
            logger.info("  越权 FA ID 返回空 Sub Accounts 列表")

        logger.info("✓ 越权 FA ID Sub Accounts 查询验证通过")
