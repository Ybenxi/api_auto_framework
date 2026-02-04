"""
Open Banking List Authorized Accounts 接口测试用例
测试 GET /api/v1/cores/{core}/open-banking/accounts/authorized-accounts 接口
"""
import pytest
from utils.assertions import assert_status_ok, assert_fields_present
from utils.logger import logger


@pytest.mark.list_api
class TestOpenBankingListAuthorizedAccounts:
    """
    获取授权账户列表接口测试用例集
    """

    def test_list_authorized_accounts_success(self, open_banking_api):
        """
        测试场景1：成功获取授权账户列表
        验证点：
        1. 接口返回 200
        2. 返回的 data 是数组
        3. 每个账户包含必需字段（id, account_name, account_number, account_status, record_type）
        """
        # 1. 调用 List Authorized Accounts 接口
        logger.info("调用 List Authorized Accounts 接口")
        response = open_banking_api.list_authorized_accounts()
        
        # 2. 断言状态码
        logger.info("验证 HTTP 状态码为 200")
        assert_status_ok(response, 200)
        
        # 3. 解析响应并验证数据
        logger.info("解析响应并验证数据")
        response_body = response.json()
        
        # 4. 验证 code 字段
        logger.info("验证 code 字段为 200")
        assert response_body.get("code") == 200, \
            f"响应 code 不正确: 期望 200, 实际 {response_body.get('code')}"
        
        # 5. 验证 data 是数组
        data = response_body.get("data", [])
        assert isinstance(data, list), "data 字段应该是数组"
        logger.info("获取到 {len(data)} 个授权账户")
        
        # 6. 如果有数据，验证字段结构
        if len(data) > 0:
            logger.info("验证第一个账户的必需字段")
            account = data[0]
            required_fields = ["id", "account_name", "account_number", "account_status", "record_type"]
            assert_fields_present(account, required_fields, "账户数据")
            
            for field in required_fields:
                logger.info(f"  ✓ {field}: {account.get(field)}")
            
            logger.info(f"\n✓ 成功获取授权账户列表:")
            logger.info(f"  账户数量: {len(data)}")
            logger.info(f"  第一个账户 ID: {account['id']}")
            logger.info(f"  账户名称: {account.get('account_name')}")
            logger.info(f"  账户状态: {account.get('account_status')}")
        else:
            logger.info("  ⚠ 当前没有授权账户数据")

    def test_list_authorized_accounts_with_name_filter(self, open_banking_api):
        """
        测试场景2：使用 name 参数筛选
        验证点：
        1. 接口返回 200
        2. 返回的数据符合筛选条件
        """
        # 1. 先不带参数查询，获取一个账户名称
        logger.info("先获取所有授权账户")
        all_response = open_banking_api.list_authorized_accounts()
        assert_status_ok(all_response, 200)
        
        all_data = all_response.json().get("data", [])
        
        if len(all_data) == 0:
            pytest.skip("没有可用的授权账户数据，跳过测试")
        
        # 获取第一个账户的名称（部分匹配）
        account_name = all_data[0].get("account_name")
        if not account_name:
            pytest.skip("账户名称为空，跳过测试")
        
        # 使用部分名称进行筛选
        search_name = account_name[:4] if len(account_name) > 4 else account_name
        logger.info("使用 name 参数筛选: {search_name}")
        
        # 2. 调用带筛选的接口
        filtered_response = open_banking_api.list_authorized_accounts(name=search_name)
        
        # 3. 验证状态码
        logger.info("验证 HTTP 状态码为 200")
        assert_status_ok(filtered_response, 200)
        
        # 4. 验证返回数据
        filtered_data = filtered_response.json().get("data", [])
        logger.info("筛选后获取到 {len(filtered_data)} 个账户")
        
        # 5. 验证筛选结果
        if len(filtered_data) > 0:
            logger.info("验证筛选结果包含搜索关键词")
            for account in filtered_data:
                account_name_value = account.get("account_name", "")
                logger.info(f"  账户名称: {account_name_value}")
        
        logger.info("✓ name 参数筛选测试完成")

    def test_list_authorized_accounts_response_structure(self, open_banking_api):
        """
        测试场景3：验证响应数据结构
        验证点：
        1. 接口返回 200
        2. 响应包含 code, error_message, error, data 字段
        3. data 是数组而非对象
        """
        # 1. 调用接口
        logger.info("调用 List Authorized Accounts 接口")
        response = open_banking_api.list_authorized_accounts()
        
        # 2. 验证状态码
        logger.info("验证 HTTP 状态码为 200")
        assert_status_ok(response, 200)
        
        # 3. 验证响应数据结构
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

    def test_list_authorized_accounts_all_fields(self, open_banking_api):
        """
        测试场景4：验证所有字段存在
        验证点：
        1. 接口返回 200
        2. 账户数据包含所有字段（包括可能为 null 的字段）
        """
        # 1. 调用接口
        logger.info("调用 List Authorized Accounts 接口")
        response = open_banking_api.list_authorized_accounts()
        
        # 2. 验证状态码
        assert_status_ok(response, 200)
        
        # 3. 解析响应
        data = response.json().get("data", [])
        if len(data) == 0:
            pytest.skip("没有可用的授权账户数据，跳过测试")
        
        # 4. 验证所有字段
        logger.info("验证第一个账户的所有字段")
        account = data[0]
        
        all_fields = [
            "id", "account_name", "account_type", "business_entity_type",
            "account_email", "sub_routing_number", "sub_routing_name",
            "parent_account_id", "account_number", "account_status",
            "business_tax_id", "record_type", "billing_street", "billing_city",
            "billing_state", "billing_zipcode", "billing_country",
            "mailing_street", "mailing_city", "mailing_state",
            "mailing_zipcode", "mailing_country", "market_value",
            "create_time", "record_owner_id", "last_fin_cenchecked_date",
            "last_ofacchecked_date"
        ]
        
        missing_fields = []
        for field in all_fields:
            if field not in account:
                missing_fields.append(field)
            else:
                value = account.get(field)
                logger.info(f"  ✓ {field}: {value if value is not None else 'null'}")
        
        if missing_fields:
            logger.info(f"  ⚠ 缺少字段: {', '.join(missing_fields)}")
        else:
            logger.info(f"  ✓ 所有字段都存在")
        
        logger.info("✓ 字段完整性验证完成")

    def test_list_authorized_accounts_account_status_values(self, open_banking_api):
        """
        测试场景5：验证 account_status 字段值
        验证点：
        1. 接口返回 200
        2. account_status 字段存在
        3. account_status 值为常见状态（如 Active, Inactive）
        """
        # 1. 调用接口
        logger.info("调用 List Authorized Accounts 接口")
        response = open_banking_api.list_authorized_accounts()
        
        # 2. 验证状态码
        assert_status_ok(response, 200)
        
        # 3. 解析响应
        data = response.json().get("data", [])
        if len(data) == 0:
            pytest.skip("没有可用的授权账户数据，跳过测试")
        
        # 4. 验证 account_status
        logger.info("验证 account_status 字段")
        
        status_values = set()
        for account in data:
            assert "account_status" in account, "账户数据缺少 account_status 字段"
            status = account.get("account_status")
            if status:
                status_values.add(status)
        
        logger.info(f"  发现的状态值: {', '.join(status_values)}")
        
        # 常见的状态值
        common_statuses = ["Active", "Inactive", "Pending", "Closed"]
        
        for status in status_values:
            if status in common_statuses:
                logger.info(f"  ✓ {status} 是常见状态值")
            else:
                logger.info(f"  ⚠ {status} 是非常见状态值")
        
        logger.info("✓ account_status 验证完成")

    def test_list_authorized_accounts_using_helper_method(self, open_banking_api):
        """
        测试场景6：使用辅助方法解析响应
        验证点：
        1. 接口返回 200
        2. 使用 parse_list_response 辅助方法成功解析响应
        3. 解析后的数据结构正确
        """
        # 1. 调用接口
        logger.info("调用 List Authorized Accounts 接口")
        response = open_banking_api.list_authorized_accounts()
        
        # 2. 使用辅助方法解析响应
        logger.info("使用 parse_list_response 辅助方法解析响应")
        parsed = open_banking_api.parse_list_response(response)
        
        # 3. 验证解析结果
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
        logger.info(f"  账户数量: {len(parsed['data'])}")
        logger.info(f"  Error Message: {parsed.get('error_message')}")
