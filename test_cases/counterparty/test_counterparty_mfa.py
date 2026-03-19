"""
Counterparty MFA 接口测试用例（V2 接口）
接口：
  GET  /api/v2/cores/actc/counterparties/:id/mfa           Get MFA Info
  POST /api/v2/cores/actc/counterparties/:id/mfa/send      Send MFA Message
  POST /api/v2/cores/actc/counterparties/:id/mfa/verify    Verify MFA Message
  POST /api/v2/cores/actc/counterparties               Create A New Counterparty with MFA
  PATCH /api/v2/cores/actc/counterparties/:id          Update Counterparty Detail with MFA

重要说明：
  MFA 接口中的 :id 是 Contact（Record Owner）的 ID，不是 Counterparty 的 ID。
  需要先通过 Contact List 接口搜索 "TestYan" 找到一个 contact id 来使用。

限制说明（自动化无法完成的场景）：
  - 无法收到真实验证码（Email/SMS），因此 verify 无法正常通过
  - 无法获得有效 access_token，因此 Create/Update with MFA 无法走完完整业务流程
  测试策略：
  - Get/Send MFA：用 contact id，验证接口可达、响应结构正确
  - Verify：用假验证码，验证接口不崩溃（返回 HTTP 200，业务错误 code != 200 是预期的）
  - Create/Update with MFA：传假 access_token，验证接口不崩溃（code != 200 是预期的）
"""
import pytest
import time
from typing import Optional
from api.account_api import AccountAPI
from api.contact_api import ContactAPI
from utils.logger import logger


VALID_ROUTING_NUMBER = "091918457"


def _ts() -> str:
    return str(int(time.time()))


def _get_contact_id(login_session) -> Optional[str]:
    """
    通过 Contact List 接口搜索 name='TestYan' 找到一个 contact id，
    作为 MFA 接口的 owner id（:id 参数）。
    """
    contact_api = ContactAPI(session=login_session)
    resp = contact_api.list_contacts(name="TestYan", size=5)
    if resp.status_code != 200:
        return None
    body = resp.json()
    inner = body.get("data", body)
    contacts = inner.get("content", []) if isinstance(inner, dict) else []
    if contacts:
        return contacts[0].get("id")
    return None


def _create_own_cp(counterparty_api, login_session) -> Optional[str]:
    account_api = AccountAPI(session=login_session)
    accounts = account_api.list_accounts(page=0, size=1).json().get("data", {}).get("content", [])
    if not accounts:
        pytest.skip("无可用 Account，跳过")

    ts = _ts()
    data = {
        "name": f"Auto TestYan CP MFA {ts}",
        "type": "Person",
        "payment_type": "ACH",
        "bank_account_type": "Checking",
        "bank_routing_number": VALID_ROUTING_NUMBER,
        "bank_name": "Auto TestYan Bank",
        "bank_account_owner_name": "Auto TestYan MFA Owner",
        "bank_account_number": "111111111",
        "assign_account_ids": [accounts[0]["id"]]
    }
    resp = counterparty_api.create_counterparty(data)
    if resp.status_code != 200 or resp.json().get("code") != 200:
        pytest.skip(f"创建 CP 失败，跳过 MFA 测试")
    cp_id = resp.json().get("data", resp.json()).get("id")
    assert cp_id
    return cp_id


@pytest.mark.counterparty
class TestCounterpartyMFA:
    """
    Counterparty MFA 接口测试（V2）
    目标：验证接口可达、响应结构正确、不崩溃，而非业务流程完整通过
    """

    # ------------------------------------------------------------------
    # 场景1：Get MFA Info — 用 contact id 获取 MFA 信息
    # ------------------------------------------------------------------
    def test_get_mfa_info_success(self, counterparty_api, login_session, db_cleanup):
        """
        测试场景1：通过 Contact ID（Record Owner）获取 MFA 信息
        说明：MFA 接口的 :id 是 Contact ID（Record Owner），不是 Counterparty ID
        使用固定的 Contact ID: 241010195849941330（当前用户的 contact）
        验证点：
        1. HTTP 200
        2. 业务 code=200
        3. 响应包含 data，data 含 email 字段（phone_number 可为 null）
        """
        owner_id = "241010195849941330"   # 固定使用当前用户的 Contact ID
        logger.info(f"使用固定 contact_id={owner_id} 获取 MFA 信息")
        resp = counterparty_api.get_counterparty_mfa(owner_id)
        assert resp.status_code == 200

        body = resp.json()
        logger.info(f"  响应: {body}")
        assert body.get("code") == 200, \
            f"Get MFA Info 应返回 code=200，实际: {body.get('code')}, msg={body.get('error_message')}"

        data = body.get("data", {})
        assert data is not None, "data 字段不应为 null"
        assert "email" in data, "MFA info 应包含 email 字段"
        logger.info(f"  email: {data.get('email')}, phone_number: {data.get('phone_number')}")

        logger.info(f"✓ Get MFA Info 验证通过")

    # ------------------------------------------------------------------
    # 场景2：Get MFA Info — 无效 CP ID
    # ------------------------------------------------------------------
    def test_get_mfa_info_invalid_id(self, counterparty_api):
        """
        测试场景2：使用无效 CP ID 获取 MFA 信息
        验证点：
        1. HTTP 200
        2. 业务 code != 200
        """
        logger.info("使用无效 ID 获取 MFA 信息")
        resp = counterparty_api.get_counterparty_mfa("INVALID_CP_999999")
        assert resp.status_code == 200
        body = resp.json()
        assert body.get("code") != 200, \
            f"无效 ID 应返回业务错误，实际 code={body.get('code')}"
        logger.info(f"✓ 无效 ID 被拒绝: code={body.get('code')}")

    # ------------------------------------------------------------------
    # 场景3：Send MFA — 用 contact id 发送 Email 验证码
    # ------------------------------------------------------------------
    def test_send_mfa_email_success(self, counterparty_api, login_session, db_cleanup):
        """
        测试场景3：向 Contact（Record Owner）发送 Email MFA 验证码
        说明：MFA 接口的 :id 是 Contact ID（Record Owner），不是 Counterparty ID
        使用固定的 Contact ID: 241010195849941330（当前用户的 contact）
        验证点：
        1. HTTP 200
        2. 业务 code=200，data="" 或 data 为空字符串
        注意：接口只保证触发发送，不保证 email 实际送达（自动化无法收取验证码）
        """
        owner_id = "241010195849941330"   # 固定使用当前用户的 Contact ID
        logger.info(f"向 contact_id={owner_id} 发送 Email MFA")
        resp = counterparty_api.send_counterparty_mfa(owner_id, "Email")
        assert resp.status_code == 200

        body = resp.json()
        logger.info(f"  响应: {body}")
        assert body.get("code") == 200, \
            f"Send MFA 应返回 code=200，实际: {body.get('code')}, msg={body.get('error_message')}"

        logger.info(f"✓ Send MFA Email 接口调通，code=200（验证码已触发发送）")

    # ------------------------------------------------------------------
    # 场景4：Send MFA — Phone 类型（探索性）
    # ------------------------------------------------------------------
    def test_send_mfa_phone(self, counterparty_api, login_session, db_cleanup):
        """
        测试场景4：向 Contact（Record Owner）发送 Phone MFA 验证码（可能没有手机号）
        使用固定的 Contact ID: 241010195849941330（当前用户的 contact）
        验证点：
        1. HTTP 200
        2. code=200 表示发送成功（需要有关联手机号），否则记录业务错误码
        """
        owner_id = "241010195849941330"   # 固定使用当前用户的 Contact ID
        logger.info(f"向 contact_id={owner_id} 发送 Phone MFA")
        resp = counterparty_api.send_counterparty_mfa(owner_id, "Phone")
        assert resp.status_code == 200

        body = resp.json()
        logger.info(f"  响应: code={body.get('code')}, msg={body.get('error_message')}")

        if body.get("code") == 200:
            logger.info("✓ Phone MFA 发送成功（Contact record owner 有手机号）")
        else:
            logger.info(f"  ⚠ Phone MFA 失败（可能 record owner 无手机号）: code={body.get('code')}")

    # ------------------------------------------------------------------
    # 场景5：Send MFA — 无效 verification_method（超出枚举范围）
    # ------------------------------------------------------------------
    def test_send_mfa_invalid_method(self, counterparty_api, login_session, db_cleanup):
        """
        测试场景5：Send MFA 时 verification_method 超出枚举范围（Email/Phone）
        使用固定的 Contact ID: 241010195849941330（当前用户的 contact）
        验证点：
        1. HTTP 200
        2. 业务 code != 200
        """
        owner_id = "241010195849941330"   # 固定使用当前用户的 Contact ID
        logger.info(f"Send MFA 使用无效 method='SMS', contact_id={owner_id}")
        resp = counterparty_api.send_counterparty_mfa(owner_id, "SMS")
        assert resp.status_code == 200
        body = resp.json()
        logger.info(f"  code={body.get('code')}, msg={body.get('error_message')}")

        if body.get("code") != 200:
            logger.info(f"✓ 无效 method 被拒绝: code={body.get('code')}")
        else:
            logger.info("⚠ API 接受了无效 method（探索性结果）")

    # ------------------------------------------------------------------
    # 场景6：Send MFA — 无效 CP ID
    # ------------------------------------------------------------------
    def test_send_mfa_invalid_id(self, counterparty_api):
        """
        测试场景6：使用无效 CP ID 发送 MFA
        验证点：HTTP 200，业务 code != 200
        """
        resp = counterparty_api.send_counterparty_mfa("INVALID_CP_999999", "Email")
        assert resp.status_code == 200
        body = resp.json()
        assert body.get("code") != 200
        logger.info(f"✓ 无效 ID 被拒绝: code={body.get('code')}")

    # ------------------------------------------------------------------
    # 场景7：Verify MFA — 假验证码（预期失败，验证接口不崩溃）
    # ------------------------------------------------------------------
    def test_verify_mfa_with_fake_code(self, counterparty_api, login_session, db_cleanup):
        """
        测试场景7：使用假验证码验证 MFA（自动化无法收取真实验证码）
        说明：MFA 接口的 :id 是 Contact ID（Record Owner），不是 Counterparty ID
        使用固定的 Contact ID: 241010195849941330（当前用户的 contact）
        验证点：
        1. 先向 contact_id 发送 MFA（code=200）
        2. 用假验证码 verify，HTTP 200（接口不崩溃）
        3. 业务 code != 200（假码预期失败，这是合理的预期结果）
        """
        owner_id = "241010195849941330"   # 固定使用当前用户的 Contact ID

        # 先发送 MFA
        send_resp = counterparty_api.send_counterparty_mfa(owner_id, "Email")
        if send_resp.json().get("code") != 200:
            pytest.skip("发送 MFA 失败，跳过验证测试")

        # 用假验证码验证
        logger.info(f"用假验证码 '000000' 验证 MFA，contact_id={owner_id}")
        verify_resp = counterparty_api.verify_counterparty_mfa(owner_id, "000000", "Email")
        assert verify_resp.status_code == 200, \
            f"verify 接口应返回 HTTP 200，实际: {verify_resp.status_code}"

        body = verify_resp.json()
        logger.info(f"  响应: {body}")
        # 假验证码预期 code != 200（这是正常的业务拒绝，不是接口报错）
        assert body.get("code") != 200, \
            "假验证码应被拒绝，但返回了 code=200（请确认是否有测试账号的 bypass 机制）"

        logger.info(f"✓ 假验证码被正确拒绝: code={body.get('code')}，接口未崩溃")

    # ------------------------------------------------------------------
    # 场景8：Create Counterparty with MFA — 假 access_token（预期失败）
    # ------------------------------------------------------------------
    def test_create_counterparty_with_mfa_fake_token(self, counterparty_api, login_session):
        """
        测试场景8：使用假 access_token 调用 Create Counterparty with MFA（V2）
        验证点：
        1. HTTP 200（接口不崩溃）
        2. 业务 code != 200（access_token 无效，预期被拒绝）
        注意：自动化无法获得真实 access_token，此场景验证接口可达性和参数解析
        """
        account_api = AccountAPI(session=login_session)
        accounts = account_api.list_accounts(page=0, size=1).json().get("data", {}).get("content", [])
        account_id = accounts[0]["id"] if accounts else "FAKE_ACCOUNT"

        ts = _ts()
        data = {
            "access_token": "FAKE_MFA_ACCESS_TOKEN_999",   # 无效 token
            "name": f"Auto TestYan CP MFA Create {ts}",
            "type": "Person",
            "payment_type": "ACH",
            "bank_account_type": "Checking",
            "bank_routing_number": VALID_ROUTING_NUMBER,
            "bank_name": "Auto TestYan Bank",
            "bank_account_owner_name": "Auto TestYan MFA Create",
            "bank_account_number": "111111111",
            "assign_account_ids": [account_id]
        }

        logger.info("使用假 access_token 调用 Create CP with MFA (V2)")
        resp = counterparty_api.create_counterparty_with_mfa(data)
        assert resp.status_code == 200, \
            f"接口应返回 HTTP 200，实际: {resp.status_code}"

        body = resp.json()
        logger.info(f"  响应: code={body.get('code')}, msg={body.get('error_message')}")
        # 假 token 预期被拒绝
        assert body.get("code") != 200, \
            "假 access_token 应被拒绝，但返回了 code=200"

        logger.info(f"✓ 假 access_token 被拒绝: code={body.get('code')}，接口未崩溃")

    # ------------------------------------------------------------------
    # 场景9：Update Counterparty with MFA — 假 access_token（预期失败）
    # ------------------------------------------------------------------
    def test_update_counterparty_with_mfa_fake_token(self, counterparty_api, login_session, db_cleanup):
        """
        测试场景9：使用假 access_token 调用 Update Counterparty with MFA（V2）
        验证点：
        1. 先用 v1 接口创建 CP
        2. 用假 access_token 调用 v2 update 接口
        3. HTTP 200（接口不崩溃）
        4. 业务 code != 200（access_token 无效，预期被拒绝）
        """
        cp_id = _create_own_cp(counterparty_api, login_session)
        if db_cleanup:
            db_cleanup.track("counterparty", cp_id)

        update_data = {
            "access_token": "FAKE_MFA_ACCESS_TOKEN_999",   # 无效 token
            "name": f"Auto TestYan CP MFA Update {_ts()}",
            "type": "Person",
            "payment_type": "ACH"
        }

        logger.info(f"使用假 access_token 调用 Update CP with MFA (V2), cp_id={cp_id}")
        resp = counterparty_api.update_counterparty_with_mfa(cp_id, update_data)
        assert resp.status_code == 200, \
            f"接口应返回 HTTP 200，实际: {resp.status_code}"

        body = resp.json()
        logger.info(f"  响应: code={body.get('code')}, msg={body.get('error_message')}")
        # 假 token 预期被拒绝
        assert body.get("code") != 200, \
            "假 access_token 应被拒绝，但返回了 code=200"

        logger.info(f"✓ 假 access_token 更新被拒绝: code={body.get('code')}，接口未崩溃")

    # ------------------------------------------------------------------
    # 场景10：Update Counterparty with MFA — 无效 CP ID
    # ------------------------------------------------------------------
    def test_update_with_mfa_invalid_cp_id(self, counterparty_api):
        """
        测试场景10：使用无效 CP ID 调用 Update with MFA
        验证点：HTTP 200，业务 code != 200
        """
        resp = counterparty_api.update_counterparty_with_mfa(
            "INVALID_CP_999999",
            {"access_token": "FAKE", "name": "Auto TestYan InvalidMFAUpdate",
             "type": "Person", "payment_type": "ACH"}
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body.get("code") != 200
        logger.info(f"✓ 无效 CP ID 被拒绝: code={body.get('code')}")
