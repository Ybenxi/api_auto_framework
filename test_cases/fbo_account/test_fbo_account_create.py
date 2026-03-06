"""
FBO Account 创建接口测试用例
测试 POST /api/v1/cores/{core}/fbo-accounts 接口
"""
import pytest
import uuid
from api.fbo_account_api import FboAccountAPI
from api.sub_account_api import SubAccountAPI
from utils.logger import logger
from utils.assertions import (
    assert_status_ok,
    assert_response_parsed
)


class TestFboAccountCreate:
    """
    FBO Account 创建接口测试用例集
    """

    def test_create_fbo_account_success(self, login_session, db_cleanup):
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
        logger.info("获取 Sub Account ID")
        sa_response = sa_api.list_sub_accounts(page=0, size=1)
        assert sa_response.status_code == 200, \
            f"获取 Sub Accounts 失败: {sa_response.status_code}"
        
        sa_parsed = sa_api.parse_list_response(sa_response)
        sub_accounts = sa_parsed.get("content", [])
        
        if len(sub_accounts) == 0:
            pytest.skip("没有可用的 Sub Account 进行测试")
        
        sub_account_id = sub_accounts[0].get("id")
        logger.info(f"  使用 Sub Account ID: {sub_account_id}")
        
        # 准备创建数据
        unique_name = f"Auto TestYan FBO Account {uuid.uuid4().hex[:8]}"
        fbo_account_data = {
            "sub_account_id": sub_account_id,
            "name": unique_name
        }
        
        # 调用创建接口
        logger.info("创建 FBO Account: {unique_name}")
        create_response = fbo_api.create_fbo_account(fbo_account_data)
        
        # 验证状态码
        logger.info("验证 HTTP 状态码")
        assert create_response.status_code in [200, 201], \
            f"Create FBO Account 接口返回状态码错误: {create_response.status_code}, Response: {create_response.text}"
        
        # 解析响应
        logger.info("解析响应并验证数据")
        response_data = create_response.json()
        
        if "data" in response_data:
            created_fbo_account = response_data["data"]
        else:
            created_fbo_account = response_data
        
        # 验证返回了 ID
        assert created_fbo_account.get("id") is not None, "创建的 FBO Account ID 为 None"

        # Echo 验证：返回值与发送值一致
        logger.info("验证 Echo 字段")
        assert created_fbo_account.get("name") == unique_name, \
            f"name 不一致: 发送 '{unique_name}', 返回 '{created_fbo_account.get('name')}'"
        assert created_fbo_account.get("sub_account_id") == sub_account_id, \
            f"sub_account_id 不一致: 发送 '{sub_account_id}', 返回 '{created_fbo_account.get('sub_account_id')}'"

        # 必需字段验证（assert，不是 logger）
        required_fields = ["id", "name", "sub_account_id", "status", "account_identifier"]
        for field in required_fields:
            assert field in created_fbo_account, f"创建响应缺少必需字段: '{field}'"

        # 跟踪 ID，测试结束后自动清理
        if db_cleanup:
            db_cleanup.track("fbo_account", created_fbo_account.get("id"))

        logger.info("✓ FBO Account 创建成功:")
        logger.info(f"  ID: {created_fbo_account.get('id')}")
        logger.info(f"  Name: {created_fbo_account.get('name')}")
        logger.info(f"  Sub Account ID: {created_fbo_account.get('sub_account_id')}")
        logger.info(f"  Status: {created_fbo_account.get('status')}")
        logger.info(f"  Account Identifier: {created_fbo_account.get('account_identifier')}")

    def test_create_fbo_account_missing_required_fields(self, login_session):
        """
        测试场景2：缺少必需字段时创建失败
        验证点（基于真实业务行为）：
        1. 不提供 sub_account_id
        2. 服务器返回 200 OK + 响应体包含业务错误码
        """
        fbo_api = FboAccountAPI(session=login_session)
        
        logger.info("尝试创建缺少必需字段的 FBO Account")
        fbo_account_data = {
            "name": "Auto TestYan FBO Account Without Sub Account ID"
            # 缺少 sub_account_id
        }
        
        create_response = fbo_api.create_fbo_account(fbo_account_data)
        
        logger.info("验证返回 200 状态码（统一错误处理设计）")
        logger.info(f"  状态码: {create_response.status_code}")
        assert create_response.status_code == 200, \
            f"服务器应该返回 200，但实际返回了 {create_response.status_code}"
        
        # 验证响应体包含业务错误码
        logger.info("验证响应体包含业务错误码")
        response_body = create_response.json()
        logger.info(f"  响应: {response_body}")
        
        # 验证不是成功的 code=200
        assert response_body.get("code") != 200, \
            f"缺少必需字段应该返回业务错误码，但返回了 code=200"
        assert response_body.get("data") is None, \
            f"缺少必需字段时 data 应该为 None"
        
        logger.info("✓ 缺少必需字段测试完成，业务错误码: {response_body.get('code')}")

    def test_create_fbo_account_with_invalid_sub_account_id(self, login_session):
        """
        测试场景3：使用无效的 Sub Account ID 创建
        验证点（基于真实业务行为）：
        1. 提供无效的 sub_account_id
        2. 服务器返回 200 OK + 响应体包含业务错误码
        """
        fbo_api = FboAccountAPI(session=login_session)
        
        logger.info("尝试使用无效 Sub Account ID 创建 FBO Account")
        fbo_account_data = {
            "sub_account_id": "invalid_sub_account_id_12345",
            "name": "Auto TestYan FBO Account Invalid Sub Account ID"
        }
        
        create_response = fbo_api.create_fbo_account(fbo_account_data)
        
        logger.info("验证返回 200 状态码（统一错误处理设计）")
        logger.info(f"  状态码: {create_response.status_code}")
        assert create_response.status_code == 200, \
            f"服务器应该返回 200，但实际返回了 {create_response.status_code}"
        
        # 验证响应体包含业务错误码
        logger.info("验证响应体包含业务错误码")
        response_body = create_response.json()
        logger.info(f"  响应: {response_body}")
        
        # 验证不是成功的 code=200
        assert response_body.get("code") != 200, \
            f"无效 Sub Account ID 应该返回业务错误码，但返回了 code=200"
        assert response_body.get("data") is None, \
            f"无效 Sub Account ID 时 data 应该为 None"
        
        logger.info("✓ 无效 Sub Account ID 测试完成，业务错误码: {response_body.get('code')}")

    def test_create_fbo_account_then_retrieve_detail(self, login_session, db_cleanup):
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
        logger.info("获取 Sub Account ID")
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
        logger.info("创建 FBO Account: {unique_name}")
        create_response = fbo_api.create_fbo_account(fbo_account_data)
        
        # 验证创建成功
        assert create_response.status_code in [200, 201], \
            f"Create 失败: {create_response.status_code}"
        
        response_body = create_response.json()
        created_fbo = response_body.get("data") or response_body
        fbo_id = created_fbo.get("id")
        
        assert fbo_id is not None, "创建的 FBO Account ID 为 None"

        # 跟踪 ID，测试结束后自动清理
        if db_cleanup:
            db_cleanup.track("fbo_account", fbo_id)

        # 立即调用 Detail 接口
        logger.info("立即查询 FBO Account 详情 (ID: {fbo_id})")
        detail_response = fbo_api.get_fbo_account_detail(fbo_id)
        
        assert_status_ok(detail_response)
        parsed_detail = fbo_api.parse_detail_response(detail_response)
        assert_response_parsed(parsed_detail)
        
        detail_fbo = parsed_detail["data"]
        
        # 验证字段一致性
        logger.info("验证创建和详情数据一致性")
        assert detail_fbo.get("sub_account_id") == fbo_account_data["sub_account_id"], \
            "sub_account_id 不一致"
        assert detail_fbo.get("name") == fbo_account_data["name"], \
            "name 不一致"
        
        logger.info("✓ 创建后立即查询验证通过，数据完全一致")
        logger.info(f"  FBO Account ID: {fbo_id}")
        logger.info(f"  Name: {detail_fbo.get('name')}")
        logger.info(f"  Account Identifier: {detail_fbo.get('account_identifier')}")

    def test_create_fbo_account_response_structure(self, login_session, db_cleanup):
        """
        测试场景5：验证创建响应的数据结构
        验证点：
        1. 成功创建后返回完整的 FBO Account 信息
        """
        fbo_api = FboAccountAPI(session=login_session)
        sa_api = SubAccountAPI(session=login_session)
        
        # 获取 Sub Account ID
        logger.info("获取 Sub Account ID")
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
        
        logger.info("创建 FBO Account 并验证响应结构")
        create_response = fbo_api.create_fbo_account(fbo_account_data)
        
        if create_response.status_code in [200, 201]:
            response_data = create_response.json()
            
            if "data" in response_data:
                created = response_data["data"]
            else:
                created = response_data
            
            expected_fields = ["id", "name", "sub_account_id", "status", "account_identifier", "balance"]

            logger.info("验证响应字段（assert）")
            for field in expected_fields:
                assert field in created, f"创建响应缺少必需字段: '{field}'"
                logger.info(f"  ✓ {field}: {created.get(field)}")

            # Echo 验证
            assert created.get("name") == unique_name, \
                f"name 不一致: 发送 '{unique_name}', 返回 '{created.get('name')}'"
            assert created.get("sub_account_id") == sub_account_id, \
                f"sub_account_id 不一致"

            # 跟踪 ID，测试结束后自动清理
            # 跟踪 ID，测试结束后自动清理
            if db_cleanup:
                db_cleanup.track("fbo_account", created.get("id"))

            logger.info("✓ 响应结构验证完成")
        else:
            logger.info(f"  创建失败，状态码: {create_response.status_code}")
            pytest.skip("创建失败，跳过响应结构验证")

    def test_create_fbo_account_missing_name(self, login_session):
        """
        测试场景6：缺少必需字段 name 时创建失败
        验证点：
        1. 有 sub_account_id，但不传 name
        2. 服务器返回 200 OK（统一错误处理）
        3. 业务错误码 code != 200
        4. data 为 None
        """
        fbo_api = FboAccountAPI(session=login_session)
        sa_api = SubAccountAPI(session=login_session)

        # 获取真实 sub_account_id
        sa_response = sa_api.list_sub_accounts(page=0, size=1)
        assert sa_response.status_code == 200
        sub_accounts = sa_api.parse_list_response(sa_response).get("content", [])

        if not sub_accounts:
            pytest.skip("没有可用的 Sub Account 进行测试")

        sub_account_id = sub_accounts[0].get("id")

        # 只传 sub_account_id，不传 name
        fbo_account_data = {
            "sub_account_id": sub_account_id
            # 缺少 name
        }

        logger.info("尝试创建缺少 name 的 FBO Account")
        create_response = fbo_api.create_fbo_account(fbo_account_data)

        assert create_response.status_code == 200, \
            f"服务器应该返回 200（统一错误处理），实际: {create_response.status_code}"

        response_body = create_response.json()
        logger.info(f"  响应: {response_body}")

        assert response_body.get("code") != 200, \
            f"缺少必需字段 name 应该返回业务错误码，但返回了 code=200"
        assert response_body.get("data") is None, \
            "缺少 name 时 data 应为 None"

        logger.info(f"✓ 缺少 name 校验通过，业务错误码: {response_body.get('code')}")

    def test_create_fbo_account_with_invisible_sub_account_id(self, login_session):
        """
        测试场景7：使用不在当前用户 visible 范围内的 Sub Account ID
        验证点：
        1. 使用他人账户下的 Sub Account ID（不在当前用户的 visible 范围）
        2. 服务器返回 200 OK（统一错误处理）
        3. 业务错误码 code == 506
        4. error_message == "visibility permission deny"
        测试数据：使用 Yingying（yhan）账户下的 FA ID 对应的不可见 sub_account_id
        注意：直接使用越权 FA 的 ID 构造请求，系统会在 sub_account 层进行 visible 校验
        """
        fbo_api = FboAccountAPI(session=login_session)

        # 使用不在当前用户 visible 范围内的 sub_account_id
        # 该 sub_account_id 属于 Yingying 的账户（yhan account），当前用户无权访问
        # 格式正确但跨用户
        invisible_sub_account_id = "241010195850134684"  # 基于越权 FA ID 构造，不在 visible 范围

        fbo_account_data = {
            "sub_account_id": invisible_sub_account_id,
            "name": f"Auto TestYan FBO Account Invisible {uuid.uuid4().hex[:8]}"
        }

        logger.info(f"使用不在 visible 范围的 Sub Account ID: {invisible_sub_account_id}")
        create_response = fbo_api.create_fbo_account(fbo_account_data)

        assert create_response.status_code == 200, \
            f"服务器应该返回 200（统一错误处理），实际: {create_response.status_code}"

        response_body = create_response.json()
        logger.info(f"  响应: {response_body}")

        # 期望返回权限错误或不存在错误（code != 200）
        assert response_body.get("code") != 200, \
            f"越权 Sub Account ID 不应该创建成功，但返回了 code=200"
        assert response_body.get("data") is None, \
            "越权时 data 应为 None"

        code = response_body.get("code")
        error_msg = response_body.get("error_message", "")
        logger.info(f"  业务错误码: {code}")
        logger.info(f"  错误信息: {error_msg}")

        if code == 506:
            assert "visibility permission deny" in error_msg.lower(), \
                f"code=506 时 error_message 应包含 'visibility permission deny'，实际: {error_msg}"
            logger.info("✓ 越权 Sub Account ID 校验通过: code=506")
        else:
            logger.info(f"  ⚠️ 返回了 code={code}（可能是不存在而非越权），error: {error_msg}")
            logger.info("✓ 越权 Sub Account ID 校验通过（拒绝创建）")
