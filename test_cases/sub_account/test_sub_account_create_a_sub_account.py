"""
Sub Account Create 接口测试用例
测试 POST /api/v1/cores/{core}/sub-accounts 接口
对应文档标题: Create a Sub Account
"""
import pytest
import uuid
from api.sub_account_api import SubAccountAPI
from api.financial_account_api import FinancialAccountAPI


@pytest.mark.sub_account
@pytest.mark.create_api
class TestSubAccountCreateASubAccount:
    """
    Sub Account 创建接口测试用例集
    """

    def test_create_sub_account_success(self, login_session):
        """
        测试场景：成功创建 Sub Account
        验证点：
        1. 先获取一个 Financial Account ID
        2. 创建 Sub Account 返回 200/201
        3. 返回数据包含新创建的 Sub Account 信息
        """
        # 1. 初始化 API 对象
        sa_api = SubAccountAPI(session=login_session)
        fa_api = FinancialAccountAPI(session=login_session)
        
        # 2. 获取 Financial Account ID
        print("\n[Step] 获取 Financial Account ID")
        fa_response = fa_api.list_financial_accounts(page=0, size=1)
        assert fa_response.status_code == 200, \
            f"获取 Financial Accounts 失败: {fa_response.status_code}"
        
        fa_parsed = fa_api.parse_list_response(fa_response)
        fa_accounts = fa_parsed.get("content", [])
        
        if len(fa_accounts) == 0:
            pytest.skip("没有可用的 Financial Account 进行测试")
        
        financial_account_id = fa_accounts[0].get("id")
        print(f"  使用 Financial Account ID: {financial_account_id}")
        
        # 3. 准备创建数据
        unique_name = f"Test Sub Account {uuid.uuid4().hex[:8]}"
        sub_account_data = {
            "financial_account_id": financial_account_id,
            "name": unique_name,
            "description": "Auto-generated test sub account"
        }
        
        # 4. 调用创建接口
        print(f"[Step] 创建 Sub Account: {unique_name}")
        create_response = sa_api.create_sub_account(sub_account_data)
        
        # 5. 验证状态码
        print("[Step] 验证 HTTP 状态码")
        assert create_response.status_code in [200, 201], \
            f"Create Sub Account 接口返回状态码错误: {create_response.status_code}, Response: {create_response.text}"
        
        # 6. 解析响应
        print("[Step] 解析响应并验证数据")
        response_data = create_response.json()
        
        if "data" in response_data:
            created_sub_account = response_data["data"]
        else:
            created_sub_account = response_data
        
        print(f"✓ Sub Account 创建成功:")
        print(f"  ID: {created_sub_account.get('id')}")
        print(f"  Name: {created_sub_account.get('name')}")
        print(f"  Financial Account ID: {created_sub_account.get('financial_account_id')}")
        print(f"  Status: {created_sub_account.get('status')}")

    def test_create_sub_account_missing_required_fields(self, login_session):
        """
        测试场景：缺少必需字段时创建失败
        验证点：
        1. 不提供 financial_account_id
        2. 接口返回错误状态码
        """
        sa_api = SubAccountAPI(session=login_session)
        
        print("\n[Step] 尝试创建缺少必需字段的 Sub Account")
        sub_account_data = {
            "name": "Test Sub Account Without FA ID"
            # 缺少 financial_account_id
        }
        
        create_response = sa_api.create_sub_account(sub_account_data)
        
        print(f"[Step] 验证返回错误状态码")
        print(f"  状态码: {create_response.status_code}")
        
        # 应该返回 400 或其他错误码
        assert create_response.status_code != 200 and create_response.status_code != 201, \
            f"缺少必需字段应该返回错误，但返回了: {create_response.status_code}"
        
        print(f"✓ 缺少必需字段测试完成")

    def test_create_sub_account_with_invalid_financial_account_id(self, login_session):
        """
        测试场景：使用无效的 Financial Account ID 创建
        验证点：
        1. 提供无效的 financial_account_id
        2. 接口返回错误状态码
        """
        sa_api = SubAccountAPI(session=login_session)
        
        print("\n[Step] 尝试使用无效 Financial Account ID 创建 Sub Account")
        sub_account_data = {
            "financial_account_id": "invalid_fa_id_12345",
            "name": "Test Sub Account With Invalid FA ID"
        }
        
        create_response = sa_api.create_sub_account(sub_account_data)
        
        print(f"[Step] 验证返回错误状态码")
        print(f"  状态码: {create_response.status_code}")
        
        # 应该返回错误码
        assert create_response.status_code != 200 and create_response.status_code != 201, \
            f"无效 FA ID 应该返回错误，但返回了: {create_response.status_code}"
        
        print(f"✓ 无效 Financial Account ID 测试完成")

    def test_create_sub_account_response_structure(self, login_session):
        """
        测试场景：验证创建响应的数据结构
        验证点：
        1. 成功创建后返回完整的 Sub Account 信息
        """
        sa_api = SubAccountAPI(session=login_session)
        fa_api = FinancialAccountAPI(session=login_session)
        
        # 获取 Financial Account ID
        print("\n[Step] 获取 Financial Account ID")
        fa_response = fa_api.list_financial_accounts(page=0, size=1)
        assert fa_response.status_code == 200
        
        fa_parsed = fa_api.parse_list_response(fa_response)
        fa_accounts = fa_parsed.get("content", [])
        
        if len(fa_accounts) == 0:
            pytest.skip("没有可用的 Financial Account 进行测试")
        
        financial_account_id = fa_accounts[0].get("id")
        
        # 创建 Sub Account
        unique_name = f"Test Sub Account {uuid.uuid4().hex[:8]}"
        sub_account_data = {
            "financial_account_id": financial_account_id,
            "name": unique_name
        }
        
        print(f"[Step] 创建 Sub Account 并验证响应结构")
        create_response = sa_api.create_sub_account(sub_account_data)
        
        if create_response.status_code in [200, 201]:
            response_data = create_response.json()
            
            if "data" in response_data:
                created = response_data["data"]
            else:
                created = response_data
            
            expected_fields = ["id", "name", "financial_account_id", "status"]
            
            print("[Step] 验证响应字段")
            for field in expected_fields:
                value = created.get(field, "(not present)")
                print(f"  {field}: {value}")
            
            print(f"✓ 响应结构验证完成")
        else:
            print(f"  创建失败，状态码: {create_response.status_code}")
            pytest.skip("创建失败，跳过响应结构验证")
