"""
Sub Account Create 接口测试用例
测试 POST /api/v1/cores/{core}/sub-accounts 接口
对应文档标题: Create a Sub Account

业务规则：
- 只有 source == 'Managed' 的 FA 才允许创建 Sub Account
- source 为 null 或非 Managed（如 Unmanaged/Illiquid）的 FA 会返回 code=599
"""
import pytest
import uuid
from typing import Optional
from api.sub_account_api import SubAccountAPI
from api.financial_account_api import FinancialAccountAPI
from utils.logger import logger


EXPECTED_SOURCE_ERROR_MSG = (
    "Only 'Managed' source financial accounts are permitted to create a sub. "
    "Please use an appropriate financial account."
)


def _get_managed_fa_id(fa_api: FinancialAccountAPI) -> Optional[str]:
    """
    获取一个 source == 'Managed' 的 FA ID。
    先用 source 参数精确筛选，若接口不支持该参数则从全量列表里遍历过滤。
    """
    # 优先使用 source 参数筛选（减少遍历开销）
    resp = fa_api.list_financial_accounts(source="Managed", size=20)
    if resp.status_code == 200:
        accounts = fa_api.parse_list_response(resp).get("content", [])
        for acc in accounts:
            if acc.get("source") == "Managed" and acc.get("id"):
                return acc.get("id")

    # 后备：全量遍历取第一个 Managed
    resp = fa_api.list_financial_accounts(size=50)
    if resp.status_code == 200:
        for acc in fa_api.parse_list_response(resp).get("content", []):
            if acc.get("source") == "Managed" and acc.get("id"):
                return acc.get("id")

    return None


def _get_non_managed_fa_id(fa_api: FinancialAccountAPI) -> Optional[str]:
    """
    获取一个 source 不为 'Managed'（如 null / Unmanaged / Illiquid）的 FA ID。
    用于验证业务规则拦截。
    """
    for source in [None, "Unmanaged", "Illiquid"]:
        if source is not None:
            resp = fa_api.list_financial_accounts(source=source, size=10)
        else:
            resp = fa_api.list_financial_accounts(size=50)

        if resp.status_code == 200:
            for acc in fa_api.parse_list_response(resp).get("content", []):
                if acc.get("source") != "Managed" and acc.get("id"):
                    return acc.get("id")

    return None


@pytest.mark.sub_account
@pytest.mark.create_api
class TestSubAccountCreateASubAccount:
    """
    Sub Account 创建接口测试用例集
    """

    def test_create_sub_account_success(self, login_session, db_cleanup):
        """
        测试场景1：使用 source='Managed' 的 FA 成功创建 Sub Account
        验证点：
        1. 先筛选出 source == 'Managed' 的 Financial Account
        2. 创建 Sub Account 返回 HTTP 200，业务 code == 200
        3. 返回数据包含新创建的 Sub Account 信息（Echo 验证）
        """
        sa_api = SubAccountAPI(session=login_session)
        fa_api = FinancialAccountAPI(session=login_session)

        logger.info("获取 source='Managed' 的 Financial Account ID")
        managed_fa_id = _get_managed_fa_id(fa_api)

        if not managed_fa_id:
            pytest.skip("未找到 source='Managed' 的 Financial Account，跳过正向测试")

        logger.info(f"  使用 Managed FA ID: {managed_fa_id}")

        unique_name = f"Auto TestYan Sub Account {uuid.uuid4().hex[:8]}"
        sub_account_data = {
            "financial_account_id": managed_fa_id,
            "name": unique_name,
            "description": "Auto-generated test sub account"
        }

        logger.info(f"创建 Sub Account: {unique_name}")
        create_response = sa_api.create_sub_account(sub_account_data)

        assert create_response.status_code in [200, 201], \
            f"Create Sub Account 接口返回状态码错误: {create_response.status_code}, Response: {create_response.text}"

        response_data = create_response.json()
        assert response_data.get("code") == 200, \
            f"业务 code 应为 200，实际: {response_data.get('code')}, msg: {response_data.get('error_message')}"

        created_sub_account = response_data.get("data") or response_data

        assert created_sub_account.get("id") is not None, "创建的 Sub Account ID 为 None"

        # Echo 验证
        assert created_sub_account.get("name") == unique_name, \
            f"name 不一致: 发送 '{unique_name}', 返回 '{created_sub_account.get('name')}'"
        assert created_sub_account.get("financial_account_id") == managed_fa_id, \
            f"financial_account_id 不一致"

        # 必需字段验证
        for field in ["id", "name", "financial_account_id", "status"]:
            assert field in created_sub_account, f"创建响应缺少必需字段: '{field}'"

        if db_cleanup:
            db_cleanup.track("sub_account", created_sub_account.get("id"))

        logger.info(f"✓ Sub Account 创建成功: ID={created_sub_account.get('id')}, Name={unique_name}")

    def test_create_sub_account_with_non_managed_fa_returns_599(self, login_session):
        """
        测试场景2（反向）：使用 source 非 'Managed' 的 FA 创建 Sub Account → 业务规则拦截
        业务规则：只有 source='Managed' 的 FA 才允许挂载 Sub Account
        验证点：
        1. 准备一个 source != 'Managed'（null 或 Unmanaged/Illiquid）的合法 FA ID
        2. 发起 POST 请求
        3. HTTP 状态码 200（统一错误处理）
        4. code == 599
        5. error_message 严格等于业务规则说明
        6. data 为 null
        """
        sa_api = SubAccountAPI(session=login_session)
        fa_api = FinancialAccountAPI(session=login_session)

        logger.info("获取 source != 'Managed' 的 Financial Account ID（用于反向测试）")
        non_managed_fa_id = _get_non_managed_fa_id(fa_api)

        if not non_managed_fa_id:
            pytest.skip("未找到 source 非 'Managed' 的 Financial Account，跳过反向测试")

        # 记录该 FA 的 source 供日志输出
        detail_resp = fa_api.get_financial_account_detail(non_managed_fa_id)
        fa_source = None
        if detail_resp.status_code == 200:
            detail_body = detail_resp.json()
            fa_detail = detail_body.get("data") or detail_body
            fa_source = fa_detail.get("source")

        logger.info(f"  使用 non-Managed FA ID: {non_managed_fa_id}（source={fa_source}）")

        sub_account_data = {
            "financial_account_id": non_managed_fa_id,
            "name": f"Auto TestYan Sub Account NonManaged {uuid.uuid4().hex[:8]}"
        }

        create_response = sa_api.create_sub_account(sub_account_data)

        assert create_response.status_code == 200, \
            f"服务器应返回 200（统一错误处理），实际: {create_response.status_code}"

        response_body = create_response.json()
        logger.info(f"  响应: {response_body}")

        assert response_body.get("code") == 599, \
            f"source 非 Managed 的 FA 应返回 code=599，实际: {response_body.get('code')}"

        actual_msg = response_body.get("error_message", "")
        assert actual_msg == EXPECTED_SOURCE_ERROR_MSG, \
            f"error_message 不匹配:\n  期望: '{EXPECTED_SOURCE_ERROR_MSG}'\n  实际: '{actual_msg}'"

        assert response_body.get("data") is None, \
            "业务规则拦截时 data 应为 null"

        logger.info(f"✓ 业务规则拦截验证通过: code=599, error_message 完全匹配")

    def test_create_sub_account_missing_financial_account_id(self, login_session):
        """
        测试场景3：缺少 financial_account_id 时创建失败
        验证点：
        1. 不提供 financial_account_id
        2. 服务器返回 200 OK + 业务错误码 code != 200
        3. data 为 null
        """
        sa_api = SubAccountAPI(session=login_session)

        logger.info("尝试创建缺少 financial_account_id 的 Sub Account")
        sub_account_data = {
            "name": "Auto TestYan Sub Account Without FA ID"
            # 缺少 financial_account_id
        }

        create_response = sa_api.create_sub_account(sub_account_data)

        assert create_response.status_code == 200, \
            f"服务器应返回 200，实际: {create_response.status_code}"

        response_body = create_response.json()
        logger.info(f"  响应: {response_body}")

        assert response_body.get("code") != 200, \
            f"缺少 financial_account_id 应返回业务错误码，但返回了 code=200"
        assert response_body.get("data") is None, \
            "缺少必需字段时 data 应为 null"

        logger.info(f"✓ 缺少 financial_account_id 校验通过，code={response_body.get('code')}")

    def test_create_sub_account_with_invalid_financial_account_id(self, login_session):
        """
        测试场景4：使用格式无效的 Financial Account ID 创建
        验证点：
        1. 提供无效格式的 financial_account_id
        2. 服务器返回 200 OK + 业务错误码 code != 200
        3. data 为 null
        """
        sa_api = SubAccountAPI(session=login_session)

        logger.info("尝试使用无效 Financial Account ID 创建 Sub Account")
        sub_account_data = {
            "financial_account_id": "invalid_fa_id_12345",
            "name": "Auto TestYan Sub Account Invalid FA ID"
        }

        create_response = sa_api.create_sub_account(sub_account_data)

        assert create_response.status_code == 200
        response_body = create_response.json()
        logger.info(f"  响应: {response_body}")

        assert response_body.get("code") != 200, \
            f"无效 FA ID 应返回业务错误码，但返回了 code=200"
        assert response_body.get("data") is None

        logger.info(f"✓ 无效 FA ID 校验通过，code={response_body.get('code')}")

    def test_create_sub_account_missing_name(self, login_session):
        """
        测试场景5：缺少 name 字段时创建失败
        验证点：
        1. 使用 source='Managed' 的 FA，但不传 name
        2. 服务器返回 200 OK（统一错误处理）
        3. 业务错误码 code != 200
        4. data 为 null
        """
        sa_api = SubAccountAPI(session=login_session)
        fa_api = FinancialAccountAPI(session=login_session)

        logger.info("获取 source='Managed' 的 Financial Account ID")
        managed_fa_id = _get_managed_fa_id(fa_api)

        if not managed_fa_id:
            pytest.skip("未找到 source='Managed' 的 Financial Account")

        # 只传 financial_account_id，不传 name
        sub_account_data = {
            "financial_account_id": managed_fa_id
            # 缺少 name
        }

        logger.info("尝试创建缺少 name 的 Sub Account")
        create_response = sa_api.create_sub_account(sub_account_data)

        assert create_response.status_code == 200, \
            f"服务器应返回 200（统一错误处理），实际: {create_response.status_code}"

        response_body = create_response.json()
        logger.info(f"  响应: {response_body}")

        assert response_body.get("code") != 200, \
            f"缺少必需字段 name 应返回业务错误码，但返回了 code=200"
        assert response_body.get("data") is None

        logger.info(f"✓ 缺少 name 校验通过，code={response_body.get('code')}")

    def test_create_sub_account_response_structure(self, login_session, db_cleanup):
        """
        测试场景6：验证创建响应的数据结构完整性
        验证点：
        1. 使用 source='Managed' 的 FA
        2. 创建成功后验证所有必需字段
        3. Echo 验证（发送值 == 返回值）
        """
        sa_api = SubAccountAPI(session=login_session)
        fa_api = FinancialAccountAPI(session=login_session)

        managed_fa_id = _get_managed_fa_id(fa_api)
        if not managed_fa_id:
            pytest.skip("未找到 source='Managed' 的 Financial Account")

        unique_name = f"Auto TestYan Sub Account {uuid.uuid4().hex[:8]}"
        sub_account_data = {
            "financial_account_id": managed_fa_id,
            "name": unique_name
        }

        logger.info(f"创建 Sub Account 并验证响应结构: {unique_name}")
        create_response = sa_api.create_sub_account(sub_account_data)

        assert create_response.status_code in [200, 201]
        response_data = create_response.json()
        assert response_data.get("code") == 200, \
            f"业务 code 应为 200，实际: {response_data.get('code')}, msg: {response_data.get('error_message')}"

        created = response_data.get("data") or response_data

        expected_fields = ["id", "name", "financial_account_id", "status"]
        for field in expected_fields:
            assert field in created, f"创建响应缺少必需字段: '{field}'"
            logger.info(f"  ✓ {field}: {created.get(field)}")

        # Echo 验证
        assert created.get("name") == unique_name
        assert created.get("financial_account_id") == managed_fa_id

        if db_cleanup:
            db_cleanup.track("sub_account", created.get("id"))

        logger.info("✓ 响应结构验证完成")

    def test_create_sub_account_then_verify_in_list(self, login_session, db_cleanup):
        """
        测试场景7：创建 Sub Account 后立即在列表中查询，验证数据一致性
        验证点：
        1. 使用 source='Managed' 的 FA 创建成功
        2. 立即调用 List 接口，使用 name 筛选
        3. 验证列表中包含刚创建的 Sub Account
        4. 验证字段值一致
        """
        sa_api = SubAccountAPI(session=login_session)
        fa_api = FinancialAccountAPI(session=login_session)

        managed_fa_id = _get_managed_fa_id(fa_api)
        if not managed_fa_id:
            pytest.skip("未找到 source='Managed' 的 Financial Account")

        unique_name = f"Auto TestYan Sub Account Verify {uuid.uuid4().hex[:8]}"
        sub_account_data = {
            "financial_account_id": managed_fa_id,
            "name": unique_name
        }

        logger.info(f"创建 Sub Account: {unique_name}")
        create_response = sa_api.create_sub_account(sub_account_data)

        assert create_response.status_code in [200, 201]
        response_body = create_response.json()
        assert response_body.get("code") == 200, \
            f"业务 code 应为 200，实际: {response_body.get('code')}"

        created = response_body.get("data") or response_body
        created_id = created.get("id")
        assert created_id is not None

        if db_cleanup:
            db_cleanup.track("sub_account", created_id)

        # 立即查询列表
        logger.info("立即在列表中查询刚创建的 Sub Account")
        list_response = sa_api.list_sub_accounts(name=unique_name)
        assert list_response.status_code == 200

        parsed_list = sa_api.parse_list_response(list_response)
        assert not parsed_list.get("error")

        sub_accounts = parsed_list["content"]
        found = any(
            sa.get("id") == created_id and
            sa.get("name") == unique_name and
            sa.get("financial_account_id") == managed_fa_id
            for sa in sub_accounts
        )

        assert found, f"列表中未找到刚创建的 Sub Account (ID: {created_id})"
        logger.info(f"✓ 创建后立即查询验证通过，ID={created_id}, Name={unique_name}")

    def test_create_sub_account_with_initial_balance_zero(self, login_session, db_cleanup):
        """
        测试场景8：显式传入 initial_balance=0（默认值验证）
        验证点：
        1. 使用 source='Managed' 的 FA
        2. 传入 initial_balance=0
        3. 创建成功，查询详情验证 balance == 0
        """
        sa_api = SubAccountAPI(session=login_session)
        fa_api = FinancialAccountAPI(session=login_session)

        managed_fa_id = _get_managed_fa_id(fa_api)
        if not managed_fa_id:
            pytest.skip("未找到 source='Managed' 的 Financial Account")

        unique_name = f"Auto TestYan Sub Account InitBal0 {uuid.uuid4().hex[:8]}"
        sub_account_data = {
            "financial_account_id": managed_fa_id,
            "name": unique_name,
            "initial_balance": 0
        }

        logger.info(f"创建 Sub Account（initial_balance=0）: {unique_name}")
        create_response = sa_api.create_sub_account(sub_account_data)

        assert create_response.status_code in [200, 201]
        response_body = create_response.json()
        assert response_body.get("code") == 200, \
            f"业务 code 应为 200，实际: {response_body.get('code')}"

        created = response_body.get("data") or response_body
        sa_id = created.get("id")
        assert sa_id is not None

        if db_cleanup:
            db_cleanup.track("sub_account", sa_id)

        # 查详情验证 balance
        detail_resp = sa_api.get_sub_account_detail(sa_id)
        assert detail_resp.status_code == 200

        detail = sa_api.parse_detail_response(detail_resp)
        assert not detail.get("error")

        balance = float(detail.get("balance", -1))
        assert balance == 0.0, f"initial_balance=0 时，balance 应为 0，实际: {balance}"

        logger.info(f"✓ initial_balance=0 验证通过，balance={balance}")

    def test_create_sub_account_initial_balance_exceeds_available(self, login_session):
        """
        测试场景9：initial_balance 超过可用余额时报错
        验证点：
        1. 使用 source='Managed' 的 FA
        2. 传入极大的 initial_balance（999999999.99）
        3. code=599，error_message 包含余额相关说明
        """
        sa_api = SubAccountAPI(session=login_session)
        fa_api = FinancialAccountAPI(session=login_session)

        managed_fa_id = _get_managed_fa_id(fa_api)
        if not managed_fa_id:
            pytest.skip("未找到 source='Managed' 的 Financial Account")

        unique_name = f"Auto TestYan Sub Account OverBalance {uuid.uuid4().hex[:8]}"
        sub_account_data = {
            "financial_account_id": managed_fa_id,
            "name": unique_name,
            "initial_balance": 999999999.99
        }

        logger.info("尝试创建 initial_balance 超过可用余额的 Sub Account")
        create_response = sa_api.create_sub_account(sub_account_data)

        assert create_response.status_code == 200
        response_body = create_response.json()
        logger.info(f"  响应: {response_body}")

        assert response_body.get("code") != 200, \
            "极大 initial_balance 不应该创建成功，但返回了 code=200"
        assert response_body.get("data") is None

        error_msg = response_body.get("error_message", "")
        code = response_body.get("code")
        logger.info(f"  code={code}, error_message={error_msg}")

        if code == 599:
            assert "initial balance" in error_msg.lower() or "allocatable" in error_msg.lower(), \
                f"code=599 时，error_message 应包含余额相关说明，实际: {error_msg}"
            logger.info("✓ 超出可用余额时正确返回 code=599")
        else:
            logger.warning(f"⚠️ 返回了 code={code}（FA 可能无 suspense sub account），error: {error_msg}")
            logger.info("✓ initial_balance 超出范围校验通过")

    def test_create_sub_account_with_invisible_fa_id(self, login_session):
        """
        测试场景10：使用不在当前用户 visible 范围内的 FA ID
        验证点：
        1. 使用他人的 FA ID：241010195850134683（ACTC Yhan FA）
        2. HTTP 200，code=506，error_message 包含 'visibility permission deny'
        3. data 为 null
        """
        sa_api = SubAccountAPI(session=login_session)

        invisible_fa_id = "241010195850134683"  # ACTC Yhan FA，属于 Yingying

        sub_account_data = {
            "financial_account_id": invisible_fa_id,
            "name": f"Auto TestYan Sub Account Invisible {uuid.uuid4().hex[:8]}"
        }

        logger.info(f"使用越权 FA ID: {invisible_fa_id}")
        create_response = sa_api.create_sub_account(sub_account_data)

        assert create_response.status_code == 200
        response_body = create_response.json()
        logger.info(f"  响应: {response_body}")

        assert response_body.get("code") == 506, \
            f"越权 FA ID 应返回 code=506，实际: {response_body.get('code')}"
        assert "visibility permission deny" in response_body.get("error_message", "").lower()
        assert response_body.get("data") is None

        logger.info(f"✓ 越权 FA ID 校验通过: code=506")
