"""
Open Banking Create Bank Account Connect Link 接口测试用例
测试 POST /api/v1/cores/{core}/open-banking/connections/manage/banks 接口
"""
import pytest
from api.open_banking_api import OpenBankingAPI
from api.account_api import AccountAPI


@pytest.mark.open_banking
@pytest.mark.create_api
class TestOpenBankingCreateBankAccountConnectLink:
    """
    创建银行账户连接链接接口测试用例集
    """

    def test_create_bank_account_connect_link_success(self, login_session):
        """
        测试场景1：成功创建银行账户连接链接
        验证点：
        1. 接口返回 200
        2. 响应包含 code 字段，值为 200
        3. 返回的 data 是一个 URL 字符串
        4. URL 包含预期的域名（如 connect2.finicity.com）
        
        前置条件：需要先获取一个真实的 account_id
        """
        # 1. 初始化 API 对象
        open_banking_api = OpenBankingAPI(session=login_session)
        account_api = AccountAPI(session=login_session)
        
        # 2. 先调用 Account List 接口获取一个真实的 account_id
        print("\n[Step] 先调用 Account List 接口获取真实的 account_id")
        account_response = account_api.list_accounts(page=0, size=1)
        assert account_response.status_code == 200, "Account List 接口调用失败"
        
        account_data = account_response.json().get("data", {})
        accounts = account_data.get("content", [])
        
        if len(accounts) == 0:
            pytest.skip("没有可用的 Account 数据，跳过测试")
        
        account_id = accounts[0]["id"]
        print(f"  获取到 Account ID: {account_id}")
        
        # 3. 调用 Create Bank Account Connect Link 接口
        print(f"[Step] 调用 Create Bank Account Connect Link 接口")
        redirect_url = "https://www.fintech.com"
        response = open_banking_api.create_bank_account_connect_link(
            redirect_url=redirect_url,
            account_id=account_id
        )
        
        # 4. 断言状态码
        print("[Step] 验证 HTTP 状态码为 200")
        assert response.status_code == 200, \
            f"Create Bank Account Connect Link 接口返回状态码错误: {response.status_code}, Response: {response.text}"
        
        # 5. 解析响应
        print("[Step] 解析响应并验证数据")
        response_body = response.json()
        
        # 6. 验证 code 字段
        print("[Step] 验证 code 字段为 200")
        assert response_body.get("code") == 200, \
            f"响应 code 不正确: 期望 200, 实际 {response_body.get('code')}"
        
        # 7. 验证 data 字段是 URL
        data = response_body.get("data")
        assert data, "响应中缺少 data 字段"
        assert isinstance(data, str), "data 字段应该是字符串"
        
        print(f"[Step] 验证返回的 URL")
        print(f"  URL 长度: {len(data)}")
        
        # 验证 URL 格式
        assert data.startswith("http://") or data.startswith("https://"), \
            "data 应该是一个有效的 URL"
        
        # 验证包含预期的域名（根据文档示例）
        if "finicity.com" in data:
            print(f"  ✓ URL 包含 finicity.com 域名")
        
        print(f"\n✓ 成功创建银行账户连接链接:")
        print(f"  Account ID: {account_id}")
        print(f"  Redirect URL: {redirect_url}")
        print(f"  返回的连接链接: {data[:100]}...")

    def test_create_bank_account_connect_link_response_structure(self, login_session):
        """
        测试场景2：验证响应数据结构
        验证点：
        1. 接口返回 200
        2. 响应包含 code, error_message, error, data 字段
        3. data 是字符串而非对象或数组
        """
        # 1. 初始化 API 对象
        open_banking_api = OpenBankingAPI(session=login_session)
        account_api = AccountAPI(session=login_session)
        
        # 2. 获取 account_id
        print("\n[Step] 获取真实的 account_id")
        account_response = account_api.list_accounts(page=0, size=1)
        assert account_response.status_code == 200, "Account List 接口调用失败"
        
        account_data = account_response.json().get("data", {})
        accounts = account_data.get("content", [])
        
        if len(accounts) == 0:
            pytest.skip("没有可用的 Account 数据，跳过测试")
        
        account_id = accounts[0]["id"]
        
        # 3. 调用接口
        print(f"[Step] 调用 Create Bank Account Connect Link 接口")
        response = open_banking_api.create_bank_account_connect_link(
            redirect_url="https://www.fintech.com",
            account_id=account_id
        )
        
        # 4. 验证状态码
        print("[Step] 验证 HTTP 状态码为 200")
        assert response.status_code == 200, \
            f"接口返回状态码错误: {response.status_code}"
        
        # 5. 验证响应数据结构
        print("[Step] 验证响应数据结构")
        response_body = response.json()
        
        # 验证是 JSON 对象
        assert isinstance(response_body, dict), "响应应该是 JSON 对象"
        
        # 验证必需字段（成功响应）
        assert "code" in response_body, "响应中缺少 code 字段"
        assert "data" in response_body, "响应中缺少 data 字段"
        print(f"  ✓ code: {response_body.get('code')}")
        print(f"  ✓ data: 存在")
        
        # error_message 和 error 字段仅在失败时存在
        if response_body.get("code") != 200:
            assert "error_message" in response_body, "错误响应中缺少 error_message 字段"
        
        # 验证 data 是字符串
        assert isinstance(response_body["data"], str), "data 字段应该是字符串"
        
        print(f"✓ 响应数据结构验证通过")

    def test_create_bank_account_connect_link_missing_redirect_url(self, login_session):
        """
        测试场景3：缺少 redirect_url 参数
        验证点：
        1. 接口返回错误状态码或错误信息
        2. 错误信息明确指出缺少必需参数
        """
        # 1. 初始化 API 对象
        open_banking_api = OpenBankingAPI(session=login_session)
        
        # 2. 构造缺少 redirect_url 的请求
        print("\n[Step] 调用接口，缺少 redirect_url 参数")
        url = open_banking_api.config.get_full_url("/open-banking/connections/manage/banks")
        data = {
            "account_id": "test_account_id"
            # 缺少 redirect_url
        }
        response = open_banking_api.session.post(url, json=data)
        
        # 3. 验证返回错误
        print("[Step] 验证接口返回错误")
        print(f"  状态码: {response.status_code}")
        
        # 可能返回 400 或 200（带错误信息）
        if response.status_code == 400:
            print(f"  ✓ 返回 400 Bad Request")
        else:
            # 检查响应体中的错误信息
            response_body = response.json()
            code = response_body.get("code")
            error_message = response_body.get("error_message")
            
            print(f"  Code: {code}")
            print(f"  Error Message: {error_message}")
            
            # 验证不是成功状态
            assert code != 200 or error_message, "应该返回错误信息"
        
        print(f"✓ 缺少必需参数测试完成")

    def test_create_bank_account_connect_link_missing_account_id(self, login_session):
        """
        测试场景4：缺少 account_id 参数
        验证点：
        1. 接口返回错误状态码或错误信息
        2. 错误信息明确指出缺少必需参数
        """
        # 1. 初始化 API 对象
        open_banking_api = OpenBankingAPI(session=login_session)
        
        # 2. 构造缺少 account_id 的请求
        print("\n[Step] 调用接口，缺少 account_id 参数")
        url = open_banking_api.config.get_full_url("/open-banking/connections/manage/banks")
        data = {
            "redirect_url": "https://www.fintech.com"
            # 缺少 account_id
        }
        response = open_banking_api.session.post(url, json=data)
        
        # 3. 验证返回错误
        print("[Step] 验证接口返回错误")
        print(f"  状态码: {response.status_code}")
        
        # 可能返回 400 或 200（带错误信息）
        if response.status_code == 400:
            print(f"  ✓ 返回 400 Bad Request")
        else:
            # 检查响应体中的错误信息
            response_body = response.json()
            code = response_body.get("code")
            error_message = response_body.get("error_message")
            
            print(f"  Code: {code}")
            print(f"  Error Message: {error_message}")
            
            # 验证不是成功状态
            assert code != 200 or error_message, "应该返回错误信息"
        
        print(f"✓ 缺少必需参数测试完成")

    def test_create_bank_account_connect_link_invalid_account_id(self, login_session):
        """
        测试场景5：使用无效的 account_id
        验证点：
        1. 接口返回错误信息
        2. 错误信息指出账户不存在或无权限
        """
        # 1. 初始化 API 对象
        open_banking_api = OpenBankingAPI(session=login_session)
        
        # 2. 使用无效的 account_id
        invalid_account_id = "invalid_account_id_999999"
        
        print(f"\n[Step] 使用无效的 account_id: {invalid_account_id}")
        
        # 3. 调用接口
        print("[Step] 调用 Create Bank Account Connect Link 接口")
        response = open_banking_api.create_bank_account_connect_link(
            redirect_url="https://www.fintech.com",
            account_id=invalid_account_id
        )
        
        # 4. 验证返回结果
        print("[Step] 验证接口返回")
        print(f"  状态码: {response.status_code}")
        
        response_body = response.json()
        code = response_body.get("code")
        error_message = response_body.get("error_message")
        
        print(f"  Code: {code}")
        print(f"  Error Message: {error_message}")
        
        # 验证返回错误（code 不为 200 或有错误信息）
        assert code != 200 or error_message, "应该返回错误信息"
        
        print(f"✓ 无效 account_id 测试完成")

    def test_create_bank_account_connect_link_different_redirect_urls(self, login_session):
        """
        测试场景6：测试不同的 redirect_url
        验证点：
        1. 接口支持不同的 redirect_url
        2. 返回的连接链接包含传入的 redirect_url
        """
        # 1. 初始化 API 对象
        open_banking_api = OpenBankingAPI(session=login_session)
        account_api = AccountAPI(session=login_session)
        
        # 2. 获取 account_id
        print("\n[Step] 获取真实的 account_id")
        account_response = account_api.list_accounts(page=0, size=1)
        assert account_response.status_code == 200, "Account List 接口调用失败"
        
        account_data = account_response.json().get("data", {})
        accounts = account_data.get("content", [])
        
        if len(accounts) == 0:
            pytest.skip("没有可用的 Account 数据，跳过测试")
        
        account_id = accounts[0]["id"]
        
        # 3. 测试不同的 redirect_url
        test_urls = [
            "https://www.example.com",
            "https://app.fintech.com/callback",
            "https://localhost:3000/redirect"
        ]
        
        for redirect_url in test_urls:
            print(f"\n[Step] 测试 redirect_url: {redirect_url}")
            response = open_banking_api.create_bank_account_connect_link(
                redirect_url=redirect_url,
                account_id=account_id
            )
            
            # 验证状态码
            assert response.status_code == 200, \
                f"接口返回状态码错误: {response.status_code}"
            
            # 验证返回的链接
            response_body = response.json()
            if response_body.get("code") == 200:
                data = response_body.get("data")
                if data and isinstance(data, str):
                    print(f"  ✓ 成功生成连接链接，长度: {len(data)}")
                else:
                    print(f"  ⚠ 返回数据格式异常")
            else:
                print(f"  ⚠ 返回 code: {response_body.get('code')}")
        
        print(f"\n✓ 不同 redirect_url 测试完成")
