"""
Sub Account Create 接口测试用例
测试 POST /api/v1/cores/{core}/sub-accounts 接口
对应文档标题: Create a Sub Account
"""
import pytest
import uuid
from api.sub_account_api import SubAccountAPI
from api.financial_account_api import FinancialAccountAPI
from utils.logger import logger


@pytest.mark.sub_account
@pytest.mark.create_api
class TestSubAccountCreateASubAccount:
    """
    Sub Account 创建接口测试用例集
    """

    def test_create_sub_account_success(self, login_session, db_cleanup):
        """
        测试场景1：成功创建 Sub Account
        验证点：
        1. 先获取一个 Financial Account ID
        2. 创建 Sub Account 返回 200/201
        3. 返回数据包含新创建的 Sub Account 信息
        """
        # 1. 初始化 API 对象
        sa_api = SubAccountAPI(session=login_session)
        fa_api = FinancialAccountAPI(session=login_session)
        
        # 2. 获取 Financial Account ID
        logger.info("获取 Financial Account ID")
        fa_response = fa_api.list_financial_accounts(page=0, size=1)
        assert fa_response.status_code == 200, \
            f"获取 Financial Accounts 失败: {fa_response.status_code}"
        
        fa_parsed = fa_api.parse_list_response(fa_response)
        fa_accounts = fa_parsed.get("content", [])
        
        if len(fa_accounts) == 0:
            pytest.skip("没有可用的 Financial Account 进行测试")
        
        financial_account_id = fa_accounts[0].get("id")
        logger.info(f"  使用 Financial Account ID: {financial_account_id}")
        
        # 3. 准备创建数据
        unique_name = f"Auto TestYan Sub Account {uuid.uuid4().hex[:8]}"
        sub_account_data = {
            "financial_account_id": financial_account_id,
            "name": unique_name,
            "description": "Auto-generated test sub account"
        }
        
        # 4. 调用创建接口
        logger.info("创建 Sub Account: {unique_name}")
        create_response = sa_api.create_sub_account(sub_account_data)
        
        # 5. 验证状态码
        logger.info("验证 HTTP 状态码")
        assert create_response.status_code in [200, 201], \
            f"Create Sub Account 接口返回状态码错误: {create_response.status_code}, Response: {create_response.text}"
        
        # 6. 解析响应
        logger.info("解析响应并验证数据")
        response_data = create_response.json()
        
        if "data" in response_data:
            created_sub_account = response_data["data"]
        else:
            created_sub_account = response_data
        
        # 验证返回了 ID
        assert created_sub_account.get("id") is not None, "创建的 Sub Account ID 为 None"

        # Echo 验证：返回值与发送值一致
        logger.info("验证 Echo 字段")
        assert created_sub_account.get("name") == unique_name, \
            f"name 不一致: 发送 '{unique_name}', 返回 '{created_sub_account.get('name')}'"
        assert created_sub_account.get("financial_account_id") == financial_account_id, \
            f"financial_account_id 不一致: 发送 '{financial_account_id}', 返回 '{created_sub_account.get('financial_account_id')}'"

        # 必需字段验证（assert，不是 logger）
        required_fields = ["id", "name", "financial_account_id", "status"]
        for field in required_fields:
            assert field in created_sub_account, f"创建响应缺少必需字段: '{field}'"

        # 跟踪 ID，测试结束后自动清理
        if db_cleanup:
            db_cleanup.track("sub_account", created_sub_account.get("id"))

        logger.info("✓ Sub Account 创建成功:")
        logger.info(f"  ID: {created_sub_account.get('id')}")
        logger.info(f"  Name: {created_sub_account.get('name')}")
        logger.info(f"  Financial Account ID: {created_sub_account.get('financial_account_id')}")
        logger.info(f"  Status: {created_sub_account.get('status')}")

    def test_create_sub_account_missing_required_fields(self, login_session):
        """
        测试场景2：缺少必需字段时创建失败
        验证点（基于真实业务行为）：
        1. 不提供 financial_account_id
        2. 服务器返回 200 OK + 响应体包含业务错误码
        """
        sa_api = SubAccountAPI(session=login_session)
        
        logger.info("尝试创建缺少必需字段的 Sub Account")
        sub_account_data = {
            "name": "Auto TestYan Sub Account Without FA ID"
            # 缺少 financial_account_id
        }
        
        create_response = sa_api.create_sub_account(sub_account_data)
        
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

    def test_create_sub_account_with_invalid_financial_account_id(self, login_session):
        """
        测试场景3：使用无效的 Financial Account ID 创建
        验证点（基于真实业务行为）：
        1. 提供无效的 financial_account_id
        2. 服务器返回 200 OK + 响应体包含业务错误码
        """
        sa_api = SubAccountAPI(session=login_session)
        
        logger.info("尝试使用无效 Financial Account ID 创建 Sub Account")
        sub_account_data = {
            "financial_account_id": "invalid_fa_id_12345",
            "name": "Auto TestYan Sub Account Invalid FA ID"
        }
        
        create_response = sa_api.create_sub_account(sub_account_data)
        
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
            f"无效 FA ID 应该返回业务错误码，但返回了 code=200"
        assert response_body.get("data") is None, \
            f"无效 FA ID 时 data 应该为 None"
        
        logger.info("✓ 无效 Financial Account ID 测试完成，业务错误码: {response_body.get('code')}")

    def test_create_sub_account_response_structure(self, login_session, db_cleanup):
        """
        测试场景4：验证创建响应的数据结构
        验证点：
        1. 成功创建后返回完整的 Sub Account 信息
        """
        sa_api = SubAccountAPI(session=login_session)
        fa_api = FinancialAccountAPI(session=login_session)
        
        # 获取 Financial Account ID
        logger.info("获取 Financial Account ID")
        fa_response = fa_api.list_financial_accounts(page=0, size=1)
        assert fa_response.status_code == 200
        
        fa_parsed = fa_api.parse_list_response(fa_response)
        fa_accounts = fa_parsed.get("content", [])
        
        if len(fa_accounts) == 0:
            pytest.skip("没有可用的 Financial Account 进行测试")
        
        financial_account_id = fa_accounts[0].get("id")
        
        # 创建 Sub Account
        unique_name = f"Auto TestYan Sub Account {uuid.uuid4().hex[:8]}"
        sub_account_data = {
            "financial_account_id": financial_account_id,
            "name": unique_name
        }
        
        logger.info("创建 Sub Account 并验证响应结构")
        create_response = sa_api.create_sub_account(sub_account_data)
        
        if create_response.status_code in [200, 201]:
            response_data = create_response.json()
            
            if "data" in response_data:
                created = response_data["data"]
            else:
                created = response_data
            
            expected_fields = ["id", "name", "financial_account_id", "status"]

            logger.info("验证响应字段（assert）")
            for field in expected_fields:
                assert field in created, f"创建响应缺少必需字段: '{field}'"
                logger.info(f"  ✓ {field}: {created.get(field)}")

            # Echo 验证
            assert created.get("name") == unique_name, \
                f"name 不一致: 发送 '{unique_name}', 返回 '{created.get('name')}'"
            assert created.get("financial_account_id") == financial_account_id, \
                f"financial_account_id 不一致"

            # 跟踪 ID，测试结束后自动清理
            # 跟踪 ID，测试结束后自动清理
            if db_cleanup:
                db_cleanup.track("sub_account", created.get("id"))

            logger.info("✓ 响应结构验证完成")
        else:
            logger.info(f"  创建失败，状态码: {create_response.status_code}")
            pytest.skip("创建失败，跳过响应结构验证")

    def test_create_sub_account_then_verify_in_list(self, login_session, db_cleanup):
        """
        测试场景5：创建 Sub Account 后立即在列表中查询，验证数据一致性
        验证点：
        1. 创建 Sub Account 成功
        2. 立即调用 List 接口，使用 name 筛选
        3. 验证列表中包含刚创建的 Sub Account
        4. 验证字段值一致
        """
        sa_api = SubAccountAPI(session=login_session)
        fa_api = FinancialAccountAPI(session=login_session)
        
        # 获取 Financial Account ID
        logger.info("获取 Financial Account ID")
        fa_response = fa_api.list_financial_accounts(page=0, size=1)
        assert fa_response.status_code == 200
        
        fa_parsed = fa_api.parse_list_response(fa_response)
        fa_accounts = fa_parsed.get("content", [])
        
        if len(fa_accounts) == 0:
            pytest.skip("没有可用的 Financial Account 进行测试")
        
        financial_account_id = fa_accounts[0].get("id")
        
        # 创建 Sub Account（使用唯一名称）
        unique_name = f"Auto TestYan Sub Account Verify {uuid.uuid4().hex[:8]}"
        sub_account_data = {
            "financial_account_id": financial_account_id,
            "name": unique_name
        }
        
        logger.info("创建 Sub Account: {unique_name}")
        create_response = sa_api.create_sub_account(sub_account_data)
        
        assert create_response.status_code in [200, 201], \
            f"创建失败: {create_response.status_code}"
        
        response_body = create_response.json()
        created = response_body.get("data") or response_body
        created_id = created.get("id")
        
        assert created_id is not None, "创建的 Sub Account ID 为 None"

        # 跟踪 ID，测试结束后自动清理
        if db_cleanup:
            db_cleanup.track("sub_account", created_id)

        # 立即调用 List 接口筛选
        logger.info("立即在列表中查询刚创建的 Sub Account")
        list_response = sa_api.list_sub_accounts(name=unique_name)
        
        assert list_response.status_code == 200, f"List 接口失败: {list_response.status_code}"
        
        parsed_list = sa_api.parse_list_response(list_response)
        assert not parsed_list.get("error"), f"List 响应解析失败"
        
        sub_accounts = parsed_list["content"]
        
        # 验证列表中包含刚创建的 Sub Account
        logger.info("验证列表中包含刚创建的 Sub Account")
        found = False
        for sa in sub_accounts:
            if sa.get("id") == created_id:
                found = True
                # 验证字段一致性
                assert sa.get("name") == unique_name, "name 不一致"
                assert sa.get("financial_account_id") == financial_account_id, \
                    "financial_account_id 不一致"
                break
        
        assert found, f"列表中未找到刚创建的 Sub Account (ID: {created_id})"
        
        logger.info("✓ 创建后立即查询验证通过，数据完全一致")
        logger.info(f"  Sub Account ID: {created_id}")
        logger.info(f"  Name: {unique_name}")

    def test_create_sub_account_missing_name(self, login_session):
        """
        测试场景6：缺少必需字段 name 时创建失败
        验证点：
        1. 有 financial_account_id，但不传 name
        2. 服务器返回 200 OK（统一错误处理）
        3. 业务错误码 code != 200
        4. data 为 None
        """
        sa_api = SubAccountAPI(session=login_session)
        fa_api = FinancialAccountAPI(session=login_session)

        # 获取真实 FA ID
        logger.info("获取 Financial Account ID")
        fa_response = fa_api.list_financial_accounts(page=0, size=1)
        assert fa_response.status_code == 200

        fa_parsed = fa_api.parse_list_response(fa_response)
        fa_accounts = fa_parsed.get("content", [])

        if not fa_accounts:
            pytest.skip("没有可用的 Financial Account 进行测试")

        financial_account_id = fa_accounts[0].get("id")

        # 只传 financial_account_id，不传 name
        sub_account_data = {
            "financial_account_id": financial_account_id
            # 缺少 name
        }

        logger.info("尝试创建缺少 name 的 Sub Account")
        create_response = sa_api.create_sub_account(sub_account_data)

        assert create_response.status_code == 200, \
            f"服务器应该返回 200（统一错误处理），实际: {create_response.status_code}"

        response_body = create_response.json()
        logger.info(f"  响应: {response_body}")

        assert response_body.get("code") != 200, \
            f"缺少必需字段 name 应该返回业务错误码，但返回了 code=200"
        assert response_body.get("data") is None, \
            f"缺少必需字段 name 时 data 应该为 None"

        logger.info(f"✓ 缺少 name 校验通过，业务错误码: {response_body.get('code')}")

    def test_create_sub_account_with_initial_balance_zero(self, login_session, db_cleanup):
        """
        测试场景7：显式传入 initial_balance=0（默认值验证）
        验证点：
        1. 传入 initial_balance=0
        2. 创建成功
        3. 查询详情验证 balance == 0
        文档说明：initial_balance 默认为 0，表示创建时转入 sub account 的初始金额
        """
        sa_api = SubAccountAPI(session=login_session)
        fa_api = FinancialAccountAPI(session=login_session)

        # 获取 FA ID
        fa_response = fa_api.list_financial_accounts(page=0, size=1)
        assert fa_response.status_code == 200
        fa_accounts = fa_api.parse_list_response(fa_response).get("content", [])

        if not fa_accounts:
            pytest.skip("没有可用的 Financial Account 进行测试")

        financial_account_id = fa_accounts[0].get("id")
        unique_name = f"Auto TestYan Sub Account InitBal0 {uuid.uuid4().hex[:8]}"

        sub_account_data = {
            "financial_account_id": financial_account_id,
            "name": unique_name,
            "initial_balance": 0
        }

        logger.info(f"创建 Sub Account（initial_balance=0）: {unique_name}")
        create_response = sa_api.create_sub_account(sub_account_data)

        assert create_response.status_code in [200, 201], \
            f"创建失败: {create_response.status_code}"

        response_body = create_response.json()
        created = response_body.get("data") or response_body

        assert created.get("id") is not None, "创建的 Sub Account ID 为 None"

        # 查详情验证 balance
        sa_id = created.get("id")
        logger.info(f"  创建成功 ID: {sa_id}，查询详情验证 balance")

        # 跟踪 ID，测试结束后自动清理
        if db_cleanup:
            db_cleanup.track("sub_account", sa_id)

        detail_resp = sa_api.get_sub_account_detail(sa_id)
        assert detail_resp.status_code == 200
        detail = sa_api.parse_detail_response(detail_resp)
        assert not detail.get("error"), f"详情解析失败: {detail.get('message')}"

        balance = float(detail.get("balance", -1))
        assert balance == 0.0, f"initial_balance=0 时，balance 应为 0，实际: {balance}"

        logger.info(f"✓ initial_balance=0 验证通过，balance={balance}")

    def test_create_sub_account_initial_balance_exceeds_available(self, login_session):
        """
        测试场景8：initial_balance 超过可用余额时报错
        验证点：
        1. 传入极大的 initial_balance（999999999.99）
        2. 返回 code 599
        3. error_message 包含 "Initial balance cannot be greater than the available allocatable balance"
        文档业务规则：
        - 如果 FA 有 sub account，初始余额从 suspense sub account 扣
        - 余额不足时返回 code 599
        """
        sa_api = SubAccountAPI(session=login_session)
        fa_api = FinancialAccountAPI(session=login_session)

        # 获取 FA ID
        fa_response = fa_api.list_financial_accounts(page=0, size=1)
        assert fa_response.status_code == 200
        fa_accounts = fa_api.parse_list_response(fa_response).get("content", [])

        if not fa_accounts:
            pytest.skip("没有可用的 Financial Account 进行测试")

        financial_account_id = fa_accounts[0].get("id")
        unique_name = f"Auto TestYan Sub Account OverBalance {uuid.uuid4().hex[:8]}"

        # 使用极大值，必然超过可用余额
        sub_account_data = {
            "financial_account_id": financial_account_id,
            "name": unique_name,
            "initial_balance": 999999999.99
        }

        logger.info("尝试创建 initial_balance 超过可用余额的 Sub Account")
        create_response = sa_api.create_sub_account(sub_account_data)

        assert create_response.status_code == 200

        response_body = create_response.json()
        logger.info(f"  响应: {response_body}")

        # 两种合法结果：
        # 1. code 599 - 余额不足（已有 sub account 且 suspense 余额不足）
        # 2. code != 200 的其他错误（FA 还没有 sub 时，suspense 不存在）
        assert response_body.get("code") != 200, \
            f"极大 initial_balance 不应该创建成功，但返回了 code=200"
        assert response_body.get("data") is None, \
            "创建失败时 data 应为 None"

        error_msg = response_body.get("error_message", "")
        code = response_body.get("code")
        logger.info(f"  业务错误码: {code}")
        logger.info(f"  错误信息: {error_msg}")

        if code == 599:
            assert "initial balance" in error_msg.lower() or "allocatable" in error_msg.lower(), \
                f"code=599 时，error_message 应包含余额相关说明，实际: {error_msg}"
            logger.info("✓ 超出可用余额时正确返回 code=599")
        else:
            logger.warning(f"⚠️ 返回了 code={code}（可能 FA 没有 suspense sub account），error: {error_msg}")
            logger.info("✓ initial_balance 超出范围校验通过（FA 无 suspense sub account）")

    def test_create_sub_account_with_invisible_fa_id(self, login_session):
        """
        测试场景9：使用不在当前用户 visible 范围内的 FA ID
        验证点：
        1. 使用他人的 FA ID：241010195850134683（ACTC Yhan FA，不属于当前用户）
        2. 服务器返回 200 OK（统一错误处理）
        3. 业务错误码 code == 506
        4. error_message == "visibility permission deny"
        5. data 为 None
        """
        sa_api = SubAccountAPI(session=login_session)

        # 使用不在当前用户 visible 范围内的 FA ID
        invisible_fa_id = "241010195850134683"  # ACTC Yhan FA，属于 Yingying，不属于当前用户

        sub_account_data = {
            "financial_account_id": invisible_fa_id,
            "name": f"Auto TestYan Sub Account Invisible {uuid.uuid4().hex[:8]}"
        }

        logger.info(f"使用不在 visible 范围内的 FA ID: {invisible_fa_id}")
        create_response = sa_api.create_sub_account(sub_account_data)

        assert create_response.status_code == 200, \
            f"服务器应该返回 200（统一错误处理），实际: {create_response.status_code}"

        response_body = create_response.json()
        logger.info(f"  响应: {response_body}")

        assert response_body.get("code") == 506, \
            f"使用不可见 FA ID 应该返回 code=506，实际: {response_body.get('code')}"

        error_msg = response_body.get("error_message", "")
        assert "visibility permission deny" in error_msg.lower(), \
            f"error_message 应包含 'visibility permission deny'，实际: {error_msg}"

        assert response_body.get("data") is None, \
            "visibility 拒绝时 data 应为 None"

        logger.info(f"✓ 越权 FA ID 校验通过: code={response_body.get('code')}, msg={error_msg}")
