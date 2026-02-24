"""
Financial Account Related Sub Accounts 接口测试用例
测试 GET /api/v1/cores/{core}/financial-accounts/:financial_account_id/sub-accounts 接口
对应文档标题: Retrieve Related Sub Accounts
"""
import pytest
from api.financial_account_api import FinancialAccountAPI
from utils.logger import logger


@pytest.mark.financial_account
@pytest.mark.sub_accounts_api
class TestFinancialAccountRetrieveRelatedSubAccounts:
    """
    Financial Account 相关 Sub Accounts 查询接口测试用例集
    """

    def _get_financial_account_id(self, fa_api):
        """辅助方法：获取第一个可用的 Financial Account ID"""
        list_response = fa_api.list_financial_accounts(page=0, size=1)
        assert list_response.status_code == 200
        parsed_list = fa_api.parse_list_response(list_response)
        accounts = parsed_list.get("content", [])
        if not accounts:
            return None
        return accounts[0].get("id")

    def test_retrieve_related_sub_accounts_success(self, login_session):
        """
        测试场景1：成功获取 Financial Account 相关的 Sub Accounts
        验证点：
        1. 先获取列表，取第一个 Financial Account ID
        2. 调用 Sub Accounts 接口返回 200
        3. 返回的所有 Sub Account financial_account_id 均与请求一致
        4. 必需字段存在
        """
        fa_api = FinancialAccountAPI(session=login_session)

        financial_account_id = self._get_financial_account_id(fa_api)
        if not financial_account_id:
            pytest.skip("没有可用的 Financial Account 进行测试")

        logger.info(f"  使用 Financial Account ID: {financial_account_id}")

        logger.info("调用 Retrieve Related Sub Accounts 接口")
        sub_response = fa_api.get_related_sub_accounts(financial_account_id, page=0, size=10)

        assert sub_response.status_code == 200, \
            f"接口返回状态码错误: {sub_response.status_code}"

        parsed_sub = fa_api.parse_list_response(sub_response)
        assert not parsed_sub.get("error"), f"响应解析失败: {parsed_sub.get('message')}"

        sub_accounts = parsed_sub.get("content", [])
        logger.info(f"  总数: {parsed_sub['total_elements']}, 返回 {len(sub_accounts)} 个")

        if sub_accounts:
            # 验证每条 sub account 的 financial_account_id 与请求一致
            logger.info("验证每条数据的 financial_account_id 与请求一致")
            for sa in sub_accounts:
                assert sa.get("financial_account_id") == financial_account_id, \
                    f"Sub Account financial_account_id={sa.get('financial_account_id')} 与请求 {financial_account_id} 不一致"

            # 验证必需字段
            sa0 = sub_accounts[0]
            required_fields = ["id", "name", "financial_account_id", "status", "balance"]
            for field in required_fields:
                assert field in sa0, f"Sub Account 缺少必需字段: '{field}'"

            logger.info(f"  ✓ 所有 Sub Accounts financial_account_id 均一致")

        logger.info("✓ Related Sub Accounts 获取成功")

    def test_retrieve_related_sub_accounts_with_name_filter(self, login_session):
        """
        测试场景2：使用 name 模糊筛选 Sub Accounts
        先获取真实 name，用前4字符做关键词，验证每条结果包含关键词
        验证点：
        1. 接口返回 200
        2. 返回的每条 Sub Account name 包含筛选关键词
        """
        fa_api = FinancialAccountAPI(session=login_session)

        financial_account_id = self._get_financial_account_id(fa_api)
        if not financial_account_id:
            pytest.skip("没有可用的 Financial Account 进行测试")

        # Step 1: 获取真实 name
        base_response = fa_api.get_related_sub_accounts(financial_account_id, page=0, size=1)
        assert base_response.status_code == 200
        base_parsed = fa_api.parse_list_response(base_response)
        base_subs = base_parsed.get("content", [])

        if not base_subs:
            pytest.skip("该 Financial Account 无 Sub Account 数据，跳过")

        real_name = base_subs[0].get("name", "")
        if not real_name or len(real_name) < 2:
            pytest.skip("name 字段为空或过短，跳过")

        keyword = real_name[:4]
        logger.info(f"  使用关键词: '{keyword}'（来自 name='{real_name}'）")

        # Step 2: 筛选
        sub_response = fa_api.get_related_sub_accounts(
            financial_account_id, name=keyword, page=0, size=10
        )
        assert sub_response.status_code == 200
        parsed_sub = fa_api.parse_list_response(sub_response)
        sub_accounts = parsed_sub.get("content", [])
        assert len(sub_accounts) > 0, f"筛选结果为空，关键词 '{keyword}' 应能匹配"

        # Step 3: 断言每条结果包含关键词
        for sa in sub_accounts:
            assert keyword.lower() in sa.get("name", "").lower(), \
                f"Sub Account name='{sa.get('name')}' 不包含关键词 '{keyword}'"

        logger.info(f"✓ name 筛选验证通过，返回 {len(sub_accounts)} 条")

    @pytest.mark.parametrize("status", ["Open", "Closed", "Pending"])
    def test_retrieve_related_sub_accounts_with_status_filter(self, login_session, status):
        """
        测试场景3：使用 status 筛选（覆盖全部枚举值）
        验证点：
        1. 接口返回 200
        2. 返回的每条 Sub Account status 均与筛选值一致
        """
        fa_api = FinancialAccountAPI(session=login_session)

        financial_account_id = self._get_financial_account_id(fa_api)
        if not financial_account_id:
            pytest.skip("没有可用的 Financial Account 进行测试")

        logger.info(f"使用 status='{status}' 筛选 Sub Accounts")
        sub_response = fa_api.get_related_sub_accounts(
            financial_account_id, status=status, page=0, size=10
        )

        assert sub_response.status_code == 200
        parsed_sub = fa_api.parse_list_response(sub_response)
        sub_accounts = parsed_sub.get("content", [])
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
        1. 接口返回 200
        2. 分页信息正确（size=5, number=0）
        3. 返回数量 <= size
        """
        fa_api = FinancialAccountAPI(session=login_session)

        financial_account_id = self._get_financial_account_id(fa_api)
        if not financial_account_id:
            pytest.skip("没有可用的 Financial Account 进行测试")

        logger.info("使用分页参数 page=0, size=5")
        sub_response = fa_api.get_related_sub_accounts(financial_account_id, page=0, size=5)

        assert sub_response.status_code == 200
        parsed_sub = fa_api.parse_list_response(sub_response)

        assert parsed_sub["size"] == 5, f"size 不正确: {parsed_sub['size']}"
        assert parsed_sub["number"] == 0, f"number 不正确: {parsed_sub['number']}"
        assert len(parsed_sub.get("content", [])) <= 5, "返回数量超过 size=5"

        logger.info("✓ 分页测试通过:")
        logger.info(f"  总元素数: {parsed_sub['total_elements']}")
        logger.info(f"  总页数: {parsed_sub['total_pages']}")
        logger.info(f"  当前页: {parsed_sub['number']}")
        logger.info(f"  每页大小: {parsed_sub['size']}")

    def test_retrieve_related_sub_accounts_response_fields(self, login_session):
        """
        测试场景5：验证 Sub Account 响应字段完整性
        验证点：
        1. 接口返回 200
        2. Sub Account 对象包含必需字段（assert 断言）
        """
        fa_api = FinancialAccountAPI(session=login_session)

        financial_account_id = self._get_financial_account_id(fa_api)
        if not financial_account_id:
            pytest.skip("没有可用的 Financial Account 进行测试")

        sub_response = fa_api.get_related_sub_accounts(financial_account_id, page=0, size=1)
        assert sub_response.status_code == 200

        parsed_sub = fa_api.parse_list_response(sub_response)
        sub_accounts = parsed_sub.get("content", [])

        if not sub_accounts:
            pytest.skip("无 Sub Account 数据，跳过字段验证")

        sub = sub_accounts[0]
        required_fields = [
            "id", "name", "financial_account_id", "status",
            "balance", "available_balance", "account_identifier"
        ]

        logger.info("验证 Sub Account 字段")
        for field in required_fields:
            assert field in sub, f"Sub Account 缺少必需字段: '{field}'"
            logger.info(f"  ✓ {field}: {sub.get(field)}")

        logger.info("✓ 字段完整性验证通过")
