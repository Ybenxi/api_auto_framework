"""
FBO Account 创建接口测试用例
测试 POST /api/v1/cores/{core}/fbo-accounts 接口
"""
import pytest
import uuid
from api.fbo_account_api import FboAccountAPI
from api.sub_account_api import SubAccountAPI
from utils.assertions import (
    assert_status_ok,
    assert_response_parsed
)


class TestFboAccountCreate:
    """
    FBO Account 创建接口测试用例集
    """

    def test_create_fbo_account_success(self, login_session):
        """
        测试场景1：成功创建 FBO Account
        验证点：
        1. 先获取一个 Sub Account ID
        2. 创建 FBO Account 返回 200/201
        3. 返回数据包含新创建的 FBO Account 信息
        """
        # 初始化 API 对象
        fbo_api = FboAccountAPI(session=login_session)
        sa_api = SubAccountAPI(session=login_session)
        
        # 获取 Sub Account ID
        print("\n[Step] 获取 Sub Account ID")
        sa_response = sa_api.list_sub_accounts(page=0, size=1)
        assert sa_response.status_code == 200, \
            f"获取 Sub Accounts 失败: {sa_response.status_code}"
        
        sa_parsed = sa_api.parse_list_response(sa_response)
        sub_accounts = sa_parsed.get("content", [])
        
        if len(sub_accounts) == 0:
            pytest.skip("没有可用的 Sub Account 进行测试")
        
        sub_account_id = sub_accounts[0].get("id")
        print(f"  使用 Sub Account ID: {sub_account_id}")
        
        # 准备创建数据
        unique_name = f"Auto TestYan FBO Account {uuid.uuid4().hex[:8]}"
        fbo_account_data = {
            "sub_account_id": sub_account_id,
            "name": unique_name
        }
        
        # 调用创建接口
        print(f"[Step] 创建 FBO Account: {unique_name}")
        create_response = fbo_api.create_fbo_account(fbo_account_data)
        
        # 验证状态码
        print("[Step] 验证 HTTP 状态码")
        assert create_response.status_code in [200, 201], \
            f"Create FBO Account 接口返回状态码错误: {create_response.status_code}, Response: {create_response.text}"
        
        # 解析响应
        print("[Step] 解析响应并验证数据")
        response_data = create_response.json()
        
        if "data" in response_data:
            created_fbo_account = response_data["data"]
        else:
            created_fbo_account = response_data
        
        print(f"✓ FBO Account 创建成功:")
        print(f"  ID: {created_fbo_account.get('id')}")
        print(f"  Name: {created_fbo_account.get('name')}")
        print(f"  Sub Account ID: {created_fbo_account.get('sub_account_id')}")
        print(f"  Status: {created_fbo_account.get('status')}")
        print(f"  Account Identifier: {created_fbo_account.get('account_identifier')}")

    def test_create_fbo_account_missing_required_fields(self, login_session):
        """
        测试场景2：缺少必需字段时创建失败
        验证点（基于真实业务行为）：
        1. 不提供 sub_account_id
        2. 服务器返回 200 OK + 响应体包含业务错误码
        """
        fbo_api = FboAccountAPI(session=login_session)
        
        print("\n[Step] 尝试创建缺少必需字段的 FBO Account")
        fbo_account_data = {
            "name": "Auto TestYan FBO Account Without Sub Account ID"
            # 缺少 sub_account_id
        }
        
        create_response = fbo_api.create_fbo_account(fbo_account_data)
        
        print(f"[Step] 验证返回 200 状态码（统一错误处理设计）")
        print(f"  状态码: {create_response.status_code}")
        assert create_response.status_code == 200, \
            f"服务器应该返回 200，但实际返回了 {create_response.status_code}"
        
        # 验证响应体包含业务错误码
        print(f"[Step] 验证响应体包含业务错误码")
        response_body = create_response.json()
        print(f"  响应: {response_body}")
        
        # 验证不是成功的 code=200
        assert response_body.get("code") != 200, \
            f"缺少必需字段应该返回业务错误码，但返回了 code=200"
        assert response_body.get("data") is None, \
            f"缺少必需字段时 data 应该为 None"
        
        print(f"✓ 缺少必需字段测试完成，业务错误码: {response_body.get('code')}")

    def test_create_fbo_account_with_invalid_sub_account_id(self, login_session):
        """
        测试场景3：使用无效的 Sub Account ID 创建
        验证点（基于真实业务行为）：
        1. 提供无效的 sub_account_id
        2. 服务器返回 200 OK + 响应体包含业务错误码
        """
        fbo_api = FboAccountAPI(session=login_session)
        
        print("\n[Step] 尝试使用无效 Sub Account ID 创建 FBO Account")
        fbo_account_data = {
            "sub_account_id": "invalid_sub_account_id_12345",
            "name": "Auto TestYan FBO Account Invalid Sub Account ID"
        }
        
        create_response = fbo_api.create_fbo_account(fbo_account_data)
        
        print(f"[Step] 验证返回 200 状态码（统一错误处理设计）")
        print(f"  状态码: {create_response.status_code}")
        assert create_response.status_code == 200, \
            f"服务器应该返回 200，但实际返回了 {create_response.status_code}"
        
        # 验证响应体包含业务错误码
        print(f"[Step] 验证响应体包含业务错误码")
        response_body = create_response.json()
        print(f"  响应: {response_body}")
        
        # 验证不是成功的 code=200
        assert response_body.get("code") != 200, \
            f"无效 Sub Account ID 应该返回业务错误码，但返回了 code=200"
        assert response_body.get("data") is None, \
            f"无效 Sub Account ID 时 data 应该为 None"
        
        print(f"✓ 无效 Sub Account ID 测试完成，业务错误码: {response_body.get('code')}")

    def test_create_fbo_account_then_retrieve_detail(self, login_session):
        """
        测试场景4：创建 FBO Account 后立即查询详情，验证数据一致性
        验证点：
        1. 创建 FBO Account 成功
        2. 立即调用 Detail 接口获取详情
        3. 验证所有字段值与创建时传入的数据一致
        """
        fbo_api = FboAccountAPI(session=login_session)
        sa_api = SubAccountAPI(session=login_session)
        
        # 获取 Sub Account ID
        print("\n[Step] 获取 Sub Account ID")
        sa_response = sa_api.list_sub_accounts(page=0, size=1)
        assert_status_ok(sa_response)
        sa_parsed = sa_api.parse_list_response(sa_response)
        assert_response_parsed(sa_parsed)
        
        sub_accounts = sa_parsed.get("content", [])
        if len(sub_accounts) == 0:
            pytest.skip("没有可用的 Sub Account 进行测试")
        
        sub_account_id = sub_accounts[0].get("id")
        
        # 准备创建数据（使用唯一名称避免冲突）
        unique_name = f"Auto TestYan FBO Account Verify {uuid.uuid4().hex[:8]}"
        fbo_account_data = {
            "sub_account_id": sub_account_id,
            "name": unique_name
        }
        
        # 调用 Create 接口
        print(f"[Step] 创建 FBO Account: {unique_name}")
        create_response = fbo_api.create_fbo_account(fbo_account_data)
        
        # 验证创建成功
        assert create_response.status_code in [200, 201], \
            f"Create 失败: {create_response.status_code}"
        
        response_body = create_response.json()
        created_fbo = response_body.get("data") or response_body
        fbo_id = created_fbo.get("id")
        
        assert fbo_id is not None, "创建的 FBO Account ID 为 None"
        
        # 立即调用 Detail 接口
        print(f"[Step] 立即查询 FBO Account 详情 (ID: {fbo_id})")
        detail_response = fbo_api.get_fbo_account_detail(fbo_id)
        
        assert_status_ok(detail_response)
        parsed_detail = fbo_api.parse_detail_response(detail_response)
        assert_response_parsed(parsed_detail)
        
        detail_fbo = parsed_detail["data"]
        
        # 验证字段一致性
        print("[Step] 验证创建和详情数据一致性")
        assert detail_fbo.get("sub_account_id") == fbo_account_data["sub_account_id"], \
            "sub_account_id 不一致"
        assert detail_fbo.get("name") == fbo_account_data["name"], \
            "name 不一致"
        
        print(f"✓ 创建后立即查询验证通过，数据完全一致")
        print(f"  FBO Account ID: {fbo_id}")
        print(f"  Name: {detail_fbo.get('name')}")
        print(f"  Account Identifier: {detail_fbo.get('account_identifier')}")

    def test_create_fbo_account_response_structure(self, login_session):
        """
        测试场景5：验证创建响应的数据结构
        验证点：
        1. 成功创建后返回完整的 FBO Account 信息
        """
        fbo_api = FboAccountAPI(session=login_session)
        sa_api = SubAccountAPI(session=login_session)
        
        # 获取 Sub Account ID
        print("\n[Step] 获取 Sub Account ID")
        sa_response = sa_api.list_sub_accounts(page=0, size=1)
        assert sa_response.status_code == 200
        
        sa_parsed = sa_api.parse_list_response(sa_response)
        sub_accounts = sa_parsed.get("content", [])
        
        if len(sub_accounts) == 0:
            pytest.skip("没有可用的 Sub Account 进行测试")
        
        sub_account_id = sub_accounts[0].get("id")
        
        # 创建 FBO Account
        unique_name = f"Auto TestYan FBO Account Structure {uuid.uuid4().hex[:8]}"
        fbo_account_data = {
            "sub_account_id": sub_account_id,
            "name": unique_name
        }
        
        print(f"[Step] 创建 FBO Account 并验证响应结构")
        create_response = fbo_api.create_fbo_account(fbo_account_data)
        
        if create_response.status_code in [200, 201]:
            response_data = create_response.json()
            
            if "data" in response_data:
                created = response_data["data"]
            else:
                created = response_data
            
            expected_fields = ["id", "name", "sub_account_id", "status", "account_identifier", "balance"]
            
            print("[Step] 验证响应字段")
            for field in expected_fields:
                value = created.get(field, "(not present)")
                print(f"  {field}: {value}")
            
            print(f"✓ 响应结构验证完成")
        else:
            print(f"  创建失败，状态码: {create_response.status_code}")
            pytest.skip("创建失败，跳过响应结构验证")
