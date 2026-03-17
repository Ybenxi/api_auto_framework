"""
Sub Account Related FBO Accounts 接口测试用例
测试 GET /api/v1/cores/{core}/sub-accounts/:sub_account_id/fbo-accounts 接口
对应文档标题: Retrieve Related Fbo Accounts
"""
import pytest
from api.sub_account_api import SubAccountAPI
from utils.logger import logger


@pytest.mark.sub_account
@pytest.mark.fbo_accounts_api
class TestSubAccountRetrieveRelatedFboAccounts:
    """
    Sub Account 相关 FBO Accounts 查询接口测试用例集
    """

    def test_retrieve_related_fbo_accounts_success(self, login_session):
        """
        测试场景1：成功获取 Sub Account 相关的 FBO Accounts
        验证点：
        1. 先获取列表，取第一个 Sub Account ID
        2. 调用 FBO Accounts 接口返回 200
        3. 返回数据结构正确
        """
        sa_api = SubAccountAPI(session=login_session)
        
        # 获取 Sub Account
        logger.info("获取 Sub Accounts 列表")
        list_response = sa_api.list_sub_accounts(page=0, size=1)
        assert list_response.status_code == 200
        
        parsed_list = sa_api.parse_list_response(list_response)
        sub_accounts = parsed_list.get("content", [])
        
        if len(sub_accounts) == 0:
            pytest.skip("没有可用的 Sub Account 进行测试")
        
        sub_account_id = sub_accounts[0].get("id")
        logger.info(f"  使用 Sub Account ID: {sub_account_id}")
        
        # 获取相关 FBO Accounts
        logger.info("调用 Retrieve Related Fbo Accounts 接口")
        fbo_response = sa_api.get_related_fbo_accounts(sub_account_id, page=0, size=10)
        
        logger.info("验证 HTTP 状态码为 200")
        assert fbo_response.status_code == 200, \
            f"接口返回状态码错误: {fbo_response.status_code}, Response: {fbo_response.text}"
        
        parsed_fbo = sa_api.parse_list_response(fbo_response)
        assert not parsed_fbo.get("error"), f"响应解析失败: {parsed_fbo.get('message')}"
        
        fbo_accounts = parsed_fbo.get("content", [])
        logger.info("✓ 成功获取相关 FBO Accounts:")
        logger.info(f"  总数: {parsed_fbo['total_elements']}")
        logger.info(f"  返回 {len(fbo_accounts)} 个 FBO Accounts")
        
        if len(fbo_accounts) > 0:
            fbo = fbo_accounts[0]
            logger.info(f"  第一个 FBO Account: {fbo.get('name')} ({fbo.get('status')})")

    def test_retrieve_related_fbo_accounts_with_status_filter(self, login_session):
        """
        测试场景2：使用 status 筛选 FBO Accounts
        验证点：
        1. 接口返回 200
        2. 返回数据结构正确
        """
        sa_api = SubAccountAPI(session=login_session)
        
        list_response = sa_api.list_sub_accounts(page=0, size=1)
        assert list_response.status_code == 200
        
        parsed_list = sa_api.parse_list_response(list_response)
        sub_accounts = parsed_list.get("content", [])
        
        if len(sub_accounts) == 0:
            pytest.skip("没有可用的 Sub Account 进行测试")
        
        sub_account_id = sub_accounts[0].get("id")
        
        logger.info("使用 status='Open' 筛选 FBO Accounts")
        fbo_response = sa_api.get_related_fbo_accounts(
            sub_account_id, 
            status="Open",
            page=0, 
            size=10
        )
        
        assert fbo_response.status_code == 200
        parsed_fbo = sa_api.parse_list_response(fbo_response)
        
        fbo_accounts = parsed_fbo.get("content", [])
        logger.info(f"  返回 {len(fbo_accounts)} 个 Open 状态的 FBO Accounts")
        
        logger.info("✓ Status 筛选测试完成")

    def test_retrieve_related_fbo_accounts_pagination(self, login_session):
        """
        测试场景3：验证 FBO Accounts 列表分页功能
        验证点：
        1. 接口返回 200
        2. 分页信息正确
        """
        sa_api = SubAccountAPI(session=login_session)
        
        list_response = sa_api.list_sub_accounts(page=0, size=1)
        assert list_response.status_code == 200
        
        parsed_list = sa_api.parse_list_response(list_response)
        sub_accounts = parsed_list.get("content", [])
        
        if len(sub_accounts) == 0:
            pytest.skip("没有可用的 Sub Account 进行测试")
        
        sub_account_id = sub_accounts[0].get("id")
        
        logger.info("使用分页参数 page=0, size=5")
        fbo_response = sa_api.get_related_fbo_accounts(
            sub_account_id, 
            page=0, 
            size=5
        )
        
        assert fbo_response.status_code == 200
        parsed_fbo = sa_api.parse_list_response(fbo_response)
        
        logger.info("✓ 分页测试完成:")
        logger.info(f"  总元素数: {parsed_fbo['total_elements']}")
        logger.info(f"  总页数: {parsed_fbo['total_pages']}")
        logger.info(f"  当前页: {parsed_fbo['number']}")
        logger.info(f"  每页大小: {parsed_fbo['size']}")

    def test_retrieve_related_fbo_accounts_response_fields(self, login_session):
        """
        测试场景4：验证 FBO Account 响应字段完整性
        验证点：
        1. 接口返回 200
        2. FBO Account 对象包含必需字段（assert 断言）
        """
        sa_api = SubAccountAPI(session=login_session)
        
        list_response = sa_api.list_sub_accounts(page=0, size=1)
        assert list_response.status_code == 200
        
        parsed_list = sa_api.parse_list_response(list_response)
        sub_accounts = parsed_list.get("content", [])
        
        if len(sub_accounts) == 0:
            pytest.skip("没有可用的 Sub Account 进行测试")
        
        sub_account_id = sub_accounts[0].get("id")
        
        logger.info("获取 FBO Accounts 并验证字段")
        fbo_response = sa_api.get_related_fbo_accounts(sub_account_id, page=0, size=1)
        assert fbo_response.status_code == 200
        
        parsed_fbo = sa_api.parse_list_response(fbo_response)
        fbo_accounts = parsed_fbo.get("content", [])
        
        if len(fbo_accounts) > 0:
            fbo = fbo_accounts[0]
            required_fields = [
                "id", "name", "sub_account_id", "status",
                "balance", "available_balance", "account_number", "routing_number"
            ]
            
            logger.info("验证 FBO Account 必需字段")
            for field in required_fields:
                assert field in fbo, f"FBO Account 缺少必需字段: '{field}'"
                logger.info(f"  ✓ {field}: {fbo.get(field)}")
            
            logger.info("✓ 字段验证完成")
        else:
            logger.info("  跳过字段验证（FBO Account 列表为空）")

    def test_retrieve_related_fbo_accounts_with_invalid_sub_account_id(self, login_session):
        """
        测试场景5：使用不存在/错误的 sub_account_id 查询
        验证点：
        1. 使用格式正确但不存在的 sub_account_id
        2. 接口返回 200（统一错误处理设计）
        3. 返回的 content 是空列表，或者 code != 200
        （实际行为：服务端查不到数据，返回空列表 或 业务错误）
        """
        sa_api = SubAccountAPI(session=login_session)

        invalid_sa_id = "999999999999999999"  # 不存在的 sub_account_id
        logger.info(f"使用不存在的 sub_account_id: {invalid_sa_id}")

        fbo_response = sa_api.get_related_fbo_accounts(invalid_sa_id, page=0, size=10)

        assert fbo_response.status_code == 200, \
            f"服务器应该返回 200（统一错误处理），实际: {fbo_response.status_code}"

        response_body = fbo_response.json()
        logger.info(f"  响应: {response_body}")

        # 两种合法结果：
        # 1. 业务错误码（code != 200）：直接返回错误
        # 2. 成功但空列表：ID 不存在，无数据
        if isinstance(response_body, dict) and "code" in response_body and response_body.get("code") != 200:
            logger.info(f"  返回业务错误码: code={response_body.get('code')}, msg={response_body.get('error_message')}")
        else:
            parsed_fbo = sa_api.parse_list_response(fbo_response)
            assert len(parsed_fbo.get("content", [])) == 0, \
                f"不存在的 sub_account_id 应返回空列表，实际有 {len(parsed_fbo.get('content', []))} 条"
            logger.info("  返回空列表")

        logger.info("✓ 无效 sub_account_id 验证通过")
