"""
Financial Account List 接口测试用例
测试 GET /api/v1/cores/{core}/financial-accounts 接口
对应文档标题: List Financial Accounts
"""
import pytest
from api.financial_account_api import FinancialAccountAPI
from utils.logger import logger


@pytest.mark.financial_account
@pytest.mark.list_api
class TestFinancialAccountListFinancialAccounts:
    """
    Financial Account 列表查询接口测试用例集
    """

    def test_list_financial_accounts_success(self, login_session):
        """
        测试场景1：成功获取 Financial Accounts 列表
        验证点：
        1. 接口返回 200
        2. 返回数据结构正确（包含 content、pageable 等字段）
        3. content 是数组类型
        """
        fa_api = FinancialAccountAPI(session=login_session)

        logger.info("调用 List Financial Accounts 接口")
        list_response = fa_api.list_financial_accounts(page=0, size=10)

        logger.info("验证 HTTP 状态码为 200")
        assert list_response.status_code == 200, \
            f"List Financial Accounts 接口返回状态码错误: {list_response.status_code}, Response: {list_response.text}"

        logger.info("解析响应并验证数据结构")
        parsed_list = fa_api.parse_list_response(list_response)
        assert not parsed_list.get("error"), f"List 响应解析失败: {parsed_list.get('message')}"

        logger.info("验证返回数据结构")
        assert "content" in parsed_list, "响应中缺少 content 字段"
        assert isinstance(parsed_list["content"], list), "content 字段不是数组类型"

        accounts = parsed_list["content"]
        logger.info(f"  总元素数: {parsed_list['total_elements']}")
        logger.info(f"  总页数: {parsed_list['total_pages']}")
        logger.info(f"  当前页: {parsed_list['number']}")
        logger.info(f"  每页大小: {parsed_list['size']}")
        logger.info(f"  返回 {len(accounts)} 个 Financial Accounts")

        if accounts:
            logger.info(f"  第一个 Financial Account: {accounts[0].get('name')} ({accounts[0].get('account_number')})")

        logger.info("✓ 测试通过")

    def test_list_financial_accounts_with_status_filter(self, login_session):
        """
        测试场景2：使用 status 筛选 Financial Accounts
        验证点：
        1. 接口返回 200
        2. 返回数据结构正确
        3. 返回的每条数据 status 均为 "Open"
        """
        fa_api = FinancialAccountAPI(session=login_session)

        logger.info("使用 status='Open' 筛选 Financial Accounts")
        list_response = fa_api.list_financial_accounts(status="Open", size=10)

        logger.info("验证 HTTP 状态码为 200")
        assert list_response.status_code == 200, \
            f"接口返回状态码错误: {list_response.status_code}"

        parsed_list = fa_api.parse_list_response(list_response)
        assert not parsed_list.get("error"), f"响应解析失败: {parsed_list.get('message')}"

        accounts = parsed_list["content"]
        logger.info(f"  返回 {len(accounts)} 个 Financial Accounts")

        if not accounts:
            pytest.skip("无 Open 状态的数据，无法验证筛选正确性")

        logger.info("验证每条数据的 status 均为 Open")
        for account in accounts:
            assert account.get("status") == "Open", \
                f"筛选结果包含非 Open 状态: status={account.get('status')}, id={account.get('id')}"

        logger.info(f"✓ {len(accounts)} 条数据均为 Open 状态")

    @pytest.mark.parametrize("source", ["Managed", "Illiquid", "Unmanaged"])
    def test_list_financial_accounts_with_source_filter(self, login_session, source):
        """
        测试场景3：使用 source 筛选 Financial Accounts（覆盖全部枚举值）
        验证点：
        1. 接口返回 200
        2. 返回的每条数据 source 均与筛选值一致
        """
        fa_api = FinancialAccountAPI(session=login_session)

        logger.info(f"使用 source='{source}' 筛选 Financial Accounts")
        list_response = fa_api.list_financial_accounts(source=source, size=10)

        logger.info("验证 HTTP 状态码为 200")
        assert list_response.status_code == 200, \
            f"接口返回状态码错误: {list_response.status_code}"

        parsed_list = fa_api.parse_list_response(list_response)
        assert not parsed_list.get("error"), f"响应解析失败: {parsed_list.get('message')}"

        accounts = parsed_list["content"]
        logger.info(f"  返回 {len(accounts)} 个 Financial Accounts")

        if not accounts:
            logger.info(f"  ⚠️ source='{source}' 无数据，跳过筛选值验证")
        else:
            logger.info(f"验证每条数据的 source 均为 {source}")
            for account in accounts:
                assert account.get("source") == source, \
                    f"筛选结果包含非 {source} 来源: source={account.get('source')}, id={account.get('id')}"
            logger.info(f"✓ {len(accounts)} 条数据均为 {source} 来源")

    @pytest.mark.parametrize("record_type", [
        "Bank_Account",
        "Investment_Account",
        "Managed_Solutions",
        "Corporate_Retirement",
        "Trust"
    ])
    def test_list_financial_accounts_with_record_type_filter(self, login_session, record_type):
        """
        测试场景4：使用 record_type 筛选 Financial Accounts（覆盖全部枚举值）
        验证点：
        1. 接口返回 200
        2. 返回的每条数据 record_type 均与筛选值一致
        """
        fa_api = FinancialAccountAPI(session=login_session)

        logger.info(f"使用 record_type='{record_type}' 筛选 Financial Accounts")
        list_response = fa_api.list_financial_accounts(record_type=record_type, size=10)

        logger.info("验证 HTTP 状态码为 200")
        assert list_response.status_code == 200, \
            f"接口返回状态码错误: {list_response.status_code}"

        parsed_list = fa_api.parse_list_response(list_response)
        assert not parsed_list.get("error"), f"响应解析失败: {parsed_list.get('message')}"

        accounts = parsed_list["content"]
        logger.info(f"  返回 {len(accounts)} 个 Financial Accounts")

        if not accounts:
            logger.info(f"  ⚠️ record_type='{record_type}' 无数据，跳过筛选值验证")
        else:
            logger.info(f"验证每条数据的 record_type 均为 {record_type}")
            for account in accounts:
                assert account.get("record_type") == record_type, \
                    f"筛选结果包含非 {record_type} 类型: record_type={account.get('record_type')}, id={account.get('id')}"
            logger.info(f"✓ {len(accounts)} 条数据均为 {record_type} 类型")

    def test_list_financial_accounts_pagination(self, login_session):
        """
        测试场景5：验证分页功能
        验证点：
        1. 接口返回 200
        2. 分页信息正确（page=0, size=5）
        3. 返回数量 <= size
        """
        fa_api = FinancialAccountAPI(session=login_session)

        logger.info("使用分页参数 page=0, size=5")
        list_response = fa_api.list_financial_accounts(page=0, size=5)

        logger.info("验证 HTTP 状态码为 200")
        assert list_response.status_code == 200, \
            f"接口返回状态码错误: {list_response.status_code}"

        parsed_list = fa_api.parse_list_response(list_response)
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

    def test_list_financial_accounts_response_fields(self, login_session):
        """
        测试场景6：验证响应字段完整性
        验证点：
        1. 接口返回 200
        2. Financial Account 对象必须包含所有必需字段
        """
        fa_api = FinancialAccountAPI(session=login_session)

        logger.info("调用 List Financial Accounts 接口")
        list_response = fa_api.list_financial_accounts(page=0, size=1)

        logger.info("验证 HTTP 状态码为 200")
        assert list_response.status_code == 200, \
            f"接口返回状态码错误: {list_response.status_code}"

        parsed_list = fa_api.parse_list_response(list_response)
        assert not parsed_list.get("error"), f"响应解析失败: {parsed_list.get('message')}"

        accounts = parsed_list["content"]

        if not accounts:
            pytest.skip("无数据，跳过字段验证")

        account = accounts[0]
        logger.info("验证 Financial Account 必需字段")

        required_fields = ["id", "name", "account_number", "status", "source"]
        for field in required_fields:
            assert field in account, f"Financial Account 缺少必需字段: '{field}'"
            logger.info(f"  ✓ {field}: {account.get(field)}")

        logger.info("✓ 字段完整性验证通过")

    def test_list_financial_accounts_empty_result(self, login_session):
        """
        测试场景7：空结果验证
        验证点：
        1. 使用不存在的筛选条件时，接口返回 200
        2. 返回的 content 是空列表
        3. total_elements 为 0
        """
        fa_api = FinancialAccountAPI(session=login_session)

        response = fa_api.list_financial_accounts(account_number="NONEXISTENT_FA_999999")

        assert response.status_code == 200, f"接口返回状态码错误: {response.status_code}"

        parsed = fa_api.parse_list_response(response)
        assert not parsed.get("error"), f"响应解析失败: {parsed.get('message')}"

        assert len(parsed["content"]) == 0, \
            f"期望返回空列表，但实际有 {len(parsed['content'])} 条数据"
        assert parsed.get("total_elements") == 0, \
            f"total_elements 应该为 0，实际为 {parsed.get('total_elements')}"

        logger.info("✓ 空结果验证通过，接口正确返回空列表")

    def test_list_financial_accounts_with_account_number_filter(self, login_session):
        """
        测试场景8：使用 account_number 筛选 Financial Accounts
        验证点：
        1. 先 list 获取真实 account_number
        2. 接口返回 200
        3. 返回数据的 account_number 与筛选值完全一致
        """
        fa_api = FinancialAccountAPI(session=login_session)

        # Step 1: 获取真实 account_number
        logger.info("先获取列表，取第一条数据的 account_number")
        base_response = fa_api.list_financial_accounts(page=0, size=1)
        assert base_response.status_code == 200
        base = fa_api.parse_list_response(base_response)

        if not base["content"]:
            pytest.skip("无数据，跳过")

        real_number = base["content"][0].get("account_number")
        if not real_number:
            pytest.skip("account_number 字段为空，跳过")

        logger.info(f"  使用真实 account_number: {real_number}")

        # Step 2: 用真实值筛选
        logger.info(f"使用 account_number='{real_number}' 筛选")
        response = fa_api.list_financial_accounts(account_number=real_number)
        assert response.status_code == 200, f"接口返回状态码错误: {response.status_code}"

        parsed = fa_api.parse_list_response(response)
        assert not parsed.get("error"), f"响应解析失败: {parsed.get('message')}"

        # Step 3: 断言结果
        accounts = parsed["content"]
        assert len(accounts) > 0, f"筛选结果为空，account_number={real_number} 应有数据"

        logger.info("验证每条数据的 account_number 与筛选值一致")
        for account in accounts:
            assert account.get("account_number") == real_number, \
                f"返回了不匹配的 account_number: {account.get('account_number')}"

        logger.info(f"✓ account_number 筛选验证通过，返回 {len(accounts)} 条")

    def test_list_financial_accounts_with_name_filter(self, login_session):
        """
        测试场景9：使用 name 模糊筛选 Financial Accounts
        验证点：
        1. 先 list 获取真实 name，取前4字符为关键词
        2. 接口返回 200
        3. 返回数据的 name 均包含该关键词（模糊匹配）
        """
        fa_api = FinancialAccountAPI(session=login_session)

        # Step 1: 获取真实 name
        logger.info("先获取列表，取第一条数据的 name")
        base_response = fa_api.list_financial_accounts(page=0, size=1)
        assert base_response.status_code == 200
        base = fa_api.parse_list_response(base_response)

        if not base["content"]:
            pytest.skip("无数据，跳过")

        real_name = base["content"][0].get("name", "")
        if not real_name or len(real_name) < 2:
            pytest.skip("name 字段为空或过短，跳过")

        keyword = real_name[:4]
        logger.info(f"  使用关键词: '{keyword}'（来自 name='{real_name}'）")

        # Step 2: 用关键词筛选
        logger.info(f"使用 name='{keyword}' 模糊筛选")
        response = fa_api.list_financial_accounts(name=keyword)
        assert response.status_code == 200, f"接口返回状态码错误: {response.status_code}"

        parsed = fa_api.parse_list_response(response)
        assert not parsed.get("error"), f"响应解析失败: {parsed.get('message')}"

        # Step 3: 断言结果
        accounts = parsed["content"]
        assert len(accounts) > 0, f"筛选结果为空，关键词 '{keyword}' 应能匹配到数据"

        logger.info("验证每条数据的 name 包含关键词")
        for account in accounts:
            assert keyword.lower() in account.get("name", "").lower(), \
                f"返回数据 name='{account.get('name')}' 不包含关键词 '{keyword}'"

        logger.info(f"✓ name 模糊筛选验证通过，返回 {len(accounts)} 条")

    def test_list_financial_accounts_with_account_ids_single(self, login_session):
        """
        测试场景10：使用 account_ids 筛选（单个 account_id，即 Profile Account ID）
        注意：account_ids 传的是 FA 对象里的 account_id（所属 Profile Account），不是 FA 自身的 id
        验证点：
        1. 先 list 获取真实 account_id
        2. 接口返回 200
        3. 返回数据每条的 account_id 均与筛选值一致
        """
        fa_api = FinancialAccountAPI(session=login_session)

        # Step 1: 获取真实 account_id（所属 Profile Account ID）
        logger.info("先获取列表，取第一条数据的 account_id（所属 Profile Account）")
        base_response = fa_api.list_financial_accounts(page=0, size=1)
        assert base_response.status_code == 200
        base = fa_api.parse_list_response(base_response)

        if not base["content"]:
            pytest.skip("无数据，跳过")

        real_account_id = base["content"][0].get("account_id")
        if not real_account_id:
            pytest.skip("account_id 字段为空，跳过")

        logger.info(f"  使用真实 account_id: {real_account_id}")

        # Step 2: 用单个 account_id 筛选
        logger.info(f"使用 account_ids=['{real_account_id}'] 筛选")
        response = fa_api.list_financial_accounts(account_ids=[real_account_id])
        assert response.status_code == 200, f"接口返回状态码错误: {response.status_code}"

        parsed = fa_api.parse_list_response(response)
        assert not parsed.get("error"), f"响应解析失败: {parsed.get('message')}"

        # Step 3: 断言结果
        accounts = parsed["content"]
        assert len(accounts) > 0, f"筛选结果为空，account_id={real_account_id} 应有数据"

        logger.info("验证每条数据的 account_id 与筛选值一致")
        for account in accounts:
            assert account.get("account_id") == real_account_id, \
                f"返回了不匹配的 account_id: {account.get('account_id')}"

        logger.info(f"✓ account_ids 单个筛选验证通过，返回 {len(accounts)} 条")

    def test_list_financial_accounts_with_account_ids_multiple(self, login_session):
        """
        测试场景11：使用 account_ids 筛选（多个 account_id，重复key格式）
        文档说明: Can be submitted as repeated keys: account_ids=456&account_ids=78
        注意：account_ids 传的是 account_id（所属 Profile Account），不是 FA 自身的 id
        验证点：
        1. 先 list 获取多个不同的 account_id
        2. 接口返回 200
        3. 返回数据的 account_id 均在传入的列表中
        """
        fa_api = FinancialAccountAPI(session=login_session)

        # Step 1: 获取前10条数据，收集唯一的 account_id
        logger.info("先获取列表，收集多个不同的 account_id")
        base_response = fa_api.list_financial_accounts(page=0, size=10)
        assert base_response.status_code == 200
        base = fa_api.parse_list_response(base_response)

        if not base["content"]:
            pytest.skip("无数据，跳过")

        # 收集唯一 account_id（去重），最多取2个
        unique_account_ids = list({
            acc["account_id"] for acc in base["content"] if acc.get("account_id")
        })[:2]

        if len(unique_account_ids) < 2:
            pytest.skip(f"唯一 account_id 不足2个（实际{len(unique_account_ids)}个），跳过多值测试")

        logger.info(f"  使用 account_ids: {unique_account_ids}")

        # Step 2: 用多个 account_id 筛选（重复key格式）
        logger.info(f"使用 account_ids={unique_account_ids} 筛选（重复key格式）")
        response = fa_api.list_financial_accounts(account_ids=unique_account_ids)
        assert response.status_code == 200, f"接口返回状态码错误: {response.status_code}"

        parsed = fa_api.parse_list_response(response)
        assert not parsed.get("error"), f"响应解析失败: {parsed.get('message')}"

        # Step 3: 断言结果
        accounts = parsed["content"]
        assert len(accounts) > 0, "筛选结果为空"

        logger.info("验证每条数据的 account_id 均在传入列表中")
        for account in accounts:
            assert account.get("account_id") in unique_account_ids, \
                f"返回了不在筛选列表中的 account_id: {account.get('account_id')}"

        logger.info(f"✓ account_ids 多值筛选验证通过，返回 {len(accounts)} 条")
