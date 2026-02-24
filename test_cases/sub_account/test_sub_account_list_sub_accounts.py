"""
Sub Account List 接口测试用例
测试 GET /api/v1/cores/{core}/sub-accounts 接口
对应文档标题: List Sub Accounts
"""
import pytest
from api.sub_account_api import SubAccountAPI
from utils.logger import logger


@pytest.mark.sub_account
@pytest.mark.list_api
class TestSubAccountListSubAccounts:
    """
    Sub Account 列表查询接口测试用例集
    """

    def test_list_sub_accounts_success(self, login_session):
        """
        测试场景1：成功获取 Sub Accounts 列表
        验证点：
        1. 接口返回 200
        2. 返回数据结构正确（包含 content、pageable 等字段）
        3. content 是数组类型
        """
        sa_api = SubAccountAPI(session=login_session)

        logger.info("调用 List Sub Accounts 接口")
        list_response = sa_api.list_sub_accounts(page=0, size=10)

        logger.info("验证 HTTP 状态码为 200")
        assert list_response.status_code == 200, \
            f"List Sub Accounts 接口返回状态码错误: {list_response.status_code}, Response: {list_response.text}"

        logger.info("解析响应并验证数据结构")
        parsed_list = sa_api.parse_list_response(list_response)
        assert not parsed_list.get("error"), f"List 响应解析失败: {parsed_list.get('message')}"

        logger.info("验证返回数据结构")
        assert "content" in parsed_list, "响应中缺少 content 字段"
        assert isinstance(parsed_list["content"], list), "content 字段不是数组类型"

        sub_accounts = parsed_list["content"]
        logger.info(f"  总元素数: {parsed_list['total_elements']}")
        logger.info(f"  总页数: {parsed_list['total_pages']}")
        logger.info(f"  当前页: {parsed_list['number']}")
        logger.info(f"  每页大小: {parsed_list['size']}")
        logger.info(f"  返回 {len(sub_accounts)} 个 Sub Accounts")

        if sub_accounts:
            logger.info(f"  第一个 Sub Account: {sub_accounts[0].get('name')} ({sub_accounts[0].get('status')})")

        logger.info("✓ 测试通过")

    @pytest.mark.parametrize("status", ["Open", "Closed", "Pending"])
    def test_list_sub_accounts_with_status_filter(self, login_session, status):
        """
        测试场景2：使用 status 筛选 Sub Accounts（覆盖全部枚举值）
        验证点：
        1. 接口返回 200
        2. 返回的每条 Sub Account 的 status 均与筛选值一致
        """
        sa_api = SubAccountAPI(session=login_session)

        logger.info(f"使用 status='{status}' 筛选 Sub Accounts")
        list_response = sa_api.list_sub_accounts(status=status, size=10)

        logger.info("验证 HTTP 状态码为 200")
        assert list_response.status_code == 200, \
            f"接口返回状态码错误: {list_response.status_code}"

        parsed_list = sa_api.parse_list_response(list_response)
        assert not parsed_list.get("error"), f"响应解析失败: {parsed_list.get('message')}"

        sub_accounts = parsed_list["content"]
        logger.info(f"  返回 {len(sub_accounts)} 个 Sub Accounts")

        if not sub_accounts:
            logger.info(f"  ⚠️ status='{status}' 无数据，跳过筛选值验证")
        else:
            logger.info(f"验证每条数据的 status 均为 {status}")
            for sa in sub_accounts:
                assert sa.get("status") == status, \
                    f"筛选结果包含非 {status} 状态: status={sa.get('status')}, id={sa.get('id')}"
            logger.info(f"✓ {len(sub_accounts)} 条数据均为 {status} 状态")

    def test_list_sub_accounts_with_name_filter(self, login_session):
        """
        测试场景3：使用 name 模糊筛选 Sub Accounts
        先 list 获取真实 name 取前4字符作为关键词，验证每条结果包含该关键词
        验证点：
        1. 接口返回 200
        2. 返回的每条 Sub Account 的 name 包含搜索关键词
        """
        sa_api = SubAccountAPI(session=login_session)

        # Step 1: 获取真实 name
        logger.info("先获取列表，取第一条数据的 name 作为关键词")
        base_response = sa_api.list_sub_accounts(page=0, size=1)
        assert base_response.status_code == 200
        base = sa_api.parse_list_response(base_response)

        if not base["content"]:
            pytest.skip("无 Sub Account 数据，跳过")

        real_name = base["content"][0].get("name", "")
        if not real_name or len(real_name) < 2:
            pytest.skip("name 字段为空或过短，跳过")

        keyword = real_name[:4]
        logger.info(f"  使用关键词: '{keyword}'（来自 name='{real_name}'）")

        # Step 2: 用关键词筛选
        logger.info(f"使用 name='{keyword}' 模糊筛选")
        list_response = sa_api.list_sub_accounts(name=keyword, size=10)

        assert list_response.status_code == 200, \
            f"接口返回状态码错误: {list_response.status_code}"

        parsed_list = sa_api.parse_list_response(list_response)
        assert not parsed_list.get("error"), f"响应解析失败: {parsed_list.get('message')}"

        sub_accounts = parsed_list["content"]
        assert len(sub_accounts) > 0, f"筛选结果为空，关键词 '{keyword}' 应能匹配到数据"

        # Step 3: 断言每条数据 name 包含关键词
        logger.info("验证每条数据的 name 包含关键词")
        for sa in sub_accounts:
            assert keyword.lower() in sa.get("name", "").lower(), \
                f"返回数据 name='{sa.get('name')}' 不包含关键词 '{keyword}'"

        logger.info(f"✓ name 模糊筛选验证通过，返回 {len(sub_accounts)} 条")

    def test_list_sub_accounts_with_financial_account_id_filter(self, login_session):
        """
        测试场景4：使用 financial_account_id 筛选 Sub Accounts
        先 list 获取真实 financial_account_id，验证每条结果 financial_account_id 匹配
        验证点：
        1. 接口返回 200
        2. 返回的每条 Sub Account 的 financial_account_id 与筛选值一致
        """
        sa_api = SubAccountAPI(session=login_session)

        # Step 1: 获取真实 financial_account_id
        logger.info("先获取列表，取第一条数据的 financial_account_id")
        base_response = sa_api.list_sub_accounts(page=0, size=1)
        assert base_response.status_code == 200
        base = sa_api.parse_list_response(base_response)

        if not base["content"]:
            pytest.skip("无 Sub Account 数据，跳过")

        real_fa_id = base["content"][0].get("financial_account_id")
        if not real_fa_id:
            pytest.skip("financial_account_id 字段为空，跳过")

        logger.info(f"  使用真实 financial_account_id: {real_fa_id}")

        # Step 2: 用真实值筛选
        logger.info(f"使用 financial_account_id='{real_fa_id}' 筛选")
        list_response = sa_api.list_sub_accounts(financial_account_id=real_fa_id, size=10)

        assert list_response.status_code == 200, \
            f"接口返回状态码错误: {list_response.status_code}"

        parsed_list = sa_api.parse_list_response(list_response)
        assert not parsed_list.get("error"), f"响应解析失败: {parsed_list.get('message')}"

        sub_accounts = parsed_list["content"]
        assert len(sub_accounts) > 0, f"筛选结果为空，financial_account_id={real_fa_id} 应有数据"

        # Step 3: 断言每条数据 financial_account_id 匹配
        logger.info("验证每条数据的 financial_account_id 与筛选值一致")
        for sa in sub_accounts:
            assert sa.get("financial_account_id") == real_fa_id, \
                f"返回了不匹配的 financial_account_id: {sa.get('financial_account_id')}"

        logger.info(f"✓ financial_account_id 筛选验证通过，返回 {len(sub_accounts)} 条")

    def test_list_sub_accounts_pagination(self, login_session):
        """
        测试场景5：验证分页功能
        验证点：
        1. 接口返回 200
        2. 分页信息正确（page=0, size=5）
        3. 返回数量 <= size
        """
        sa_api = SubAccountAPI(session=login_session)

        logger.info("使用分页参数 page=0, size=5")
        list_response = sa_api.list_sub_accounts(page=0, size=5)

        logger.info("验证 HTTP 状态码为 200")
        assert list_response.status_code == 200, \
            f"接口返回状态码错误: {list_response.status_code}"

        parsed_list = sa_api.parse_list_response(list_response)
        assert not parsed_list.get("error"), f"响应解析失败: {parsed_list.get('message')}"

        logger.info("验证分页信息")
        assert parsed_list["size"] == 5, \
            f"分页大小不正确: 期望 5, 实际 {parsed_list['size']}"
        assert parsed_list["number"] == 0, \
            f"页码不正确: 期望 0, 实际 {parsed_list['number']}"
        assert len(parsed_list["content"]) <= 5, \
            f"返回数量 {len(parsed_list['content'])} 超过 size=5"

        logger.info("✓ 分页测试通过:")
        logger.info(f"  总元素数: {parsed_list['total_elements']}")
        logger.info(f"  总页数: {parsed_list['total_pages']}")
        logger.info(f"  当前页: {parsed_list['number']}")
        logger.info(f"  每页大小: {parsed_list['size']}")
        logger.info(f"  实际返回: {len(parsed_list['content'])} 条")

    def test_list_sub_accounts_response_fields(self, login_session):
        """
        测试场景6：验证响应字段完整性
        验证点：
        1. 接口返回 200
        2. Sub Account 对象必须包含所有必需字段
        """
        sa_api = SubAccountAPI(session=login_session)

        logger.info("调用 List Sub Accounts 接口")
        list_response = sa_api.list_sub_accounts(page=0, size=1)

        assert list_response.status_code == 200, \
            f"接口返回状态码错误: {list_response.status_code}"

        parsed_list = sa_api.parse_list_response(list_response)
        assert not parsed_list.get("error"), f"响应解析失败: {parsed_list.get('message')}"

        sub_accounts = parsed_list["content"]

        if not sub_accounts:
            pytest.skip("无数据，跳过字段验证")

        sa = sub_accounts[0]
        required_fields = ["id", "name", "financial_account_id", "status", "balance"]

        logger.info("验证 Sub Account 必需字段")
        for field in required_fields:
            assert field in sa, f"Sub Account 对象缺少必需字段: '{field}'"
            logger.info(f"  ✓ {field}: {sa.get(field)}")

        logger.info("✓ 字段完整性验证通过")

    def test_list_sub_accounts_empty_result(self, login_session):
        """
        测试场景7：空结果验证
        验证点：
        1. 使用不存在的筛选条件时，接口返回 200
        2. 返回的 content 是空列表
        3. total_elements 为 0
        """
        sa_api = SubAccountAPI(session=login_session)

        logger.info("使用不存在的名称查询")
        response = sa_api.list_sub_accounts(name="NONEXISTENT_SUB_ACCOUNT_999999")

        assert response.status_code == 200, f"接口返回状态码错误: {response.status_code}"

        parsed = sa_api.parse_list_response(response)
        assert not parsed.get("error"), f"响应解析失败: {parsed.get('message')}"

        assert len(parsed["content"]) == 0, \
            f"期望返回空列表，但实际有 {len(parsed['content'])} 条数据"
        assert parsed.get("total_elements") == 0, \
            f"total_elements 应该为 0，实际为 {parsed.get('total_elements')}"

        logger.info("✓ 空结果验证通过")
