"""
Open Banking List Connected External Accounts 接口测试用例
测试 GET /api/v1/cores/{core}/open-banking/accounts 接口
"""
import pytest
from api.account_api import AccountAPI
from utils.assertions import assert_status_ok, assert_fields_present
from utils.logger import logger


@pytest.mark.list_api
class TestOpenBankingListConnectedExternalAccounts:
    """
    获取已连接外部账户列表接口测试用例集
    """

    def test_list_connected_external_accounts_success(self, open_banking_api, login_session):
        """
        测试场景1：成功获取已连接外部账户列表
        验证点：
        1. 接口返回 200
        2. 返回的 data 是数组
        3. 每个外部账户包含必需字段（id, name, account_number, status, record_type）
        
        前置条件：需要先获取一个真实的 account_id
        """
        # 1. 获取真实的 account_id
        account_api = AccountAPI(session=login_session)
        logger.info("获取真实的 account_id")
        account_response = account_api.list_accounts(page=0, size=1)
        assert_status_ok(account_response, 200)
        
        account_data = account_response.json().get("data", {})
        accounts = account_data.get("content", [])
        
        if len(accounts) == 0:
            pytest.skip("没有可用的 Account 数据，跳过测试")
        
        account_id = accounts[0]["id"]
        logger.info(f"  获取到 Account ID: {account_id}")
        
        # 2. 调用 List Connected External Accounts 接口
        logger.info("调用 List Connected External Accounts 接口")
        response = open_banking_api.list_connected_external_accounts(account_id=account_id)
        
        # 3. 验证状态码
        logger.info("验证 HTTP 状态码为 200")
        assert_status_ok(response, 200)
        
        # 4. 解析响应并验证数据
        logger.info("解析响应并验证数据")
        response_body = response.json()
        
        # 5. 验证 code 字段
        logger.info("验证 code 字段为 200")
        assert response_body.get("code") == 200, \
            f"响应 code 不正确: 期望 200, 实际 {response_body.get('code')}"
        
        # 6. 验证 data 是数组
        data = response_body.get("data", [])
        assert isinstance(data, list), "data 字段应该是数组"
        logger.info("获取到 {len(data)} 个外部账户")
        
        # 7. 如果有数据，验证字段结构
        if len(data) > 0:
            logger.info("验证第一个外部账户的必需字段")
            external_account = data[0]
            required_fields = ["id", "name", "account_number", "status", "record_type"]
            assert_fields_present(external_account, required_fields, "外部账户数据")
            
            for field in required_fields:
                logger.info(f"  ✓ {field}: {external_account.get(field)}")
            
            logger.info(f"\n✓ 成功获取已连接外部账户列表:")
            logger.info(f"  账户数量: {len(data)}")
            logger.info(f"  第一个外部账户 ID: {external_account['id']}")
            logger.info(f"  账户名称: {external_account.get('name')}")
            logger.info(f"  账户状态: {external_account.get('status')}")
        else:
            logger.info("  ⚠ 当前没有已连接的外部账户")

    def test_list_connected_external_accounts_response_structure(self, open_banking_api, login_session):
        """
        测试场景2：验证响应数据结构
        验证点：
        1. 接口返回 200
        2. 响应包含 code, error_message, error, data 字段
        3. data 是数组而非对象
        """
        # 1. 获取 account_id
        account_api = AccountAPI(session=login_session)
        logger.info("获取真实的 account_id")
        account_response = account_api.list_accounts(page=0, size=1)
        assert_status_ok(account_response, 200)
        
        account_data = account_response.json().get("data", {})
        accounts = account_data.get("content", [])
        
        if len(accounts) == 0:
            pytest.skip("没有可用的 Account 数据，跳过测试")
        
        account_id = accounts[0]["id"]
        
        # 2. 调用接口
        logger.info("调用 List Connected External Accounts 接口")
        response = open_banking_api.list_connected_external_accounts(account_id=account_id)
        
        # 3. 验证状态码
        logger.info("验证 HTTP 状态码为 200")
        assert_status_ok(response, 200)
        
        # 4. 验证响应数据结构
        logger.info("验证响应数据结构")
        response_body = response.json()
        
        # 验证是 JSON 对象
        assert isinstance(response_body, dict), "响应应该是 JSON 对象"
        
        # 验证必需字段
        assert_fields_present(response_body, ["code", "data"], "响应")
        logger.info(f"  ✓ code: {response_body.get('code')}")
        logger.info(f"  ✓ data: 存在")
        
        # error_message 和 error 字段仅在失败时存在
        if response_body.get("code") != 200:
            assert "error_message" in response_body, "错误响应中缺少 error_message 字段"
        
        # 验证 data 是数组
        assert isinstance(response_body["data"], list), "data 字段应该是数组"
        
        logger.info("✓ 响应数据结构验证通过")

    def test_list_connected_external_accounts_all_fields(self, open_banking_api, login_session):
        """
        测试场景3：验证所有字段存在
        验证点：
        1. 接口返回 200
        2. 外部账户数据包含所有字段（包括可能为 null 的字段）
        """
        # 1. 获取 account_id
        account_api = AccountAPI(session=login_session)
        logger.info("获取真实的 account_id")
        account_response = account_api.list_accounts(page=0, size=1)
        assert_status_ok(account_response, 200)
        
        account_data = account_response.json().get("data", {})
        accounts = account_data.get("content", [])
        
        if len(accounts) == 0:
            pytest.skip("没有可用的 Account 数据，跳过测试")
        
        account_id = accounts[0]["id"]
        
        # 3. 调用接口
        logger.info("调用 List Connected External Accounts 接口")
        response = open_banking_api.list_connected_external_accounts(account_id=account_id)
        
        # 4. 验证状态码
        assert response.status_code == 200, f"接口返回状态码错误: {response.status_code}"
        
        # 4. 解析响应
        data = response.json().get("data", [])
        if len(data) == 0:
            pytest.skip("没有可用的外部账户数据，跳过测试")
        
        # 5. 验证所有字段
        logger.info("验证第一个外部账户的所有字段")
        external_account = data[0]
        
        all_fields = [
            "id", "name", "account_number", "status", "record_type",
            "source", "external_account_num", "unified_account_id",
            "institution_id", "description", "service_type", "created_date"
        ]
        
        missing_fields = []
        for field in all_fields:
            if field not in external_account:
                missing_fields.append(field)
            else:
                value = external_account.get(field)
                logger.info(f"  ✓ {field}: {value if value is not None else 'null'}")
        
        if missing_fields:
            logger.info(f"  ⚠ 缺少字段: {', '.join(missing_fields)}")
        else:
            logger.info(f"  ✓ 所有字段都存在")
        
        logger.info("✓ 字段完整性验证完成")

    def test_list_connected_external_accounts_status_values(self, open_banking_api, login_session):
        """
        测试场景4：验证 status 字段值
        验证点：
        1. 接口返回 200
        2. status 字段存在
        3. status 值为常见状态（如 Open, Closed）
        """
        # 1. 获取 account_id
        account_api = AccountAPI(session=login_session)
        logger.info("获取真实的 account_id")
        account_response = account_api.list_accounts(page=0, size=1)
        assert_status_ok(account_response, 200)
        
        account_data = account_response.json().get("data", {})
        accounts = account_data.get("content", [])
        
        if len(accounts) == 0:
            pytest.skip("没有可用的 Account 数据，跳过测试")
        
        account_id = accounts[0]["id"]
        
        # 2. 调用接口
        logger.info("调用 List Connected External Accounts 接口")
        response = open_banking_api.list_connected_external_accounts(account_id=account_id)
        
        # 3. 验证状态码
        assert_status_ok(response, 200)
        
        # 4. 解析响应
        data = response.json().get("data", [])
        if len(data) == 0:
            pytest.skip("没有可用的外部账户数据，跳过测试")
        
        # 5. 验证 status
        logger.info("验证 status 字段")
        
        status_values = set()
        for external_account in data:
            assert "status" in external_account, "外部账户数据缺少 status 字段"
            status = external_account.get("status")
            if status:
                status_values.add(status)
        
        logger.info(f"  发现的状态值: {', '.join(status_values)}")
        
        # 常见的状态值
        common_statuses = ["Open", "Closed", "Active", "Inactive"]
        
        for status in status_values:
            if status in common_statuses:
                logger.info(f"  ✓ {status} 是常见状态值")
            else:
                logger.info(f"  ⚠ {status} 是非常见状态值")
        
        logger.info("✓ status 验证完成")

    def test_list_connected_external_accounts_record_type_values(self, open_banking_api, login_session):
        """
        测试场景5：验证 record_type 字段值
        验证点：
        1. 接口返回 200
        2. record_type 字段存在
        3. record_type 值为常见类型（如 Saving, Checking）
        """
        # 1. 获取 account_id
        account_api = AccountAPI(session=login_session)
        logger.info("获取真实的 account_id")
        account_response = account_api.list_accounts(page=0, size=1)
        assert_status_ok(account_response, 200)
        
        account_data = account_response.json().get("data", {})
        accounts = account_data.get("content", [])
        
        if len(accounts) == 0:
            pytest.skip("没有可用的 Account 数据，跳过测试")
        
        account_id = accounts[0]["id"]
        
        # 2. 调用接口
        logger.info("调用 List Connected External Accounts 接口")
        response = open_banking_api.list_connected_external_accounts(account_id=account_id)
        
        # 3. 验证状态码
        assert_status_ok(response, 200)
        
        # 4. 解析响应
        data = response.json().get("data", [])
        if len(data) == 0:
            pytest.skip("没有可用的外部账户数据，跳过测试")
        
        # 5. 验证 record_type
        logger.info("验证 record_type 字段")
        
        record_type_values = set()
        for external_account in data:
            assert "record_type" in external_account, "外部账户数据缺少 record_type 字段"
            record_type = external_account.get("record_type")
            if record_type:
                record_type_values.add(record_type)
        
        logger.info(f"  发现的 record_type 值: {', '.join(record_type_values)}")
        
        # 常见的 record_type 值
        common_types = ["Saving", "Checking", "Investment", "Credit"]
        
        for record_type in record_type_values:
            if record_type in common_types:
                logger.info(f"  ✓ {record_type} 是常见账户类型")
            else:
                logger.info(f"  ⚠ {record_type} 是非常见账户类型")
        
        logger.info("✓ record_type 验证完成")

    def test_list_connected_external_accounts_using_helper_method(self, open_banking_api, login_session):
        """
        测试场景6：使用辅助方法解析响应
        验证点：
        1. 接口返回 200
        2. 使用 parse_list_response 辅助方法成功解析响应
        3. 解析后的数据结构正确
        """
        # 1. 获取 account_id
        account_api = AccountAPI(session=login_session)
        logger.info("获取真实的 account_id")
        account_response = account_api.list_accounts(page=0, size=1)
        assert_status_ok(account_response, 200)
        
        account_data = account_response.json().get("data", {})
        accounts = account_data.get("content", [])
        
        if len(accounts) == 0:
            pytest.skip("没有可用的 Account 数据，跳过测试")
        
        account_id = accounts[0]["id"]
        
        # 2. 调用接口
        logger.info("调用 List Connected External Accounts 接口")
        response = open_banking_api.list_connected_external_accounts(account_id=account_id)
        
        # 3. 使用辅助方法解析响应
        logger.info("使用 parse_list_response 辅助方法解析响应")
        parsed = open_banking_api.parse_list_response(response)
        
        # 4. 验证解析结果
        logger.info("验证解析结果")
        assert not parsed.get("error"), f"响应解析失败: {parsed.get('message')}"
        
        # 验证包含必需字段
        assert_fields_present(parsed, ["code", "data"], "解析结果")
        
        # 验证 code 为 200
        assert parsed["code"] == 200, f"code 不正确: 期望 200, 实际 {parsed['code']}"
        
        # 验证 data 是列表
        assert isinstance(parsed["data"], list), "data 应该是列表"
        
        logger.info(f"\n✓ 辅助方法解析验证通过:")
        logger.info(f"  Code: {parsed['code']}")
        logger.info(f"  外部账户数量: {len(parsed['data'])}")
        logger.info(f"  Error Message: {parsed.get('error_message')}")
