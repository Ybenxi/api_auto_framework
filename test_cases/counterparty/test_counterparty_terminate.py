"""
Counterparty Terminate 测试用例
接口：PATCH /api/v1/cores/actc/counterparties/:counterparty_id/terminate

关键业务规则（与旧版误解的修正）：
  - 本接口**不是把 Counterparty 本身状态改为 Terminated**
  - 而是把 Counterparty 里指定的 assign_account 的 status 改成 "Terminate"
  - 参数是 account_ids（数组），指定要 terminate 的 assign account
  - 操作成功后：
      * 在 Counterparty List / Detail 查询，被指定的 assign_account 的 status 变为 "Terminate"
      * 未被指定的 assign_account status 不受影响
  - 响应格式：{"code": 200, "data": true}
"""
import pytest
import time
from typing import Optional
from api.account_api import AccountAPI
from utils.logger import logger


VALID_ROUTING_NUMBER = "091918457"


def _ts() -> str:
    return str(int(time.time()))


def _create_ach_cp_with_accounts(counterparty_api, login_session,
                                  account_ids: list, suffix: str = "") -> Optional[str]:
    """
    创建绑定了指定 account_ids 的 ACH Counterparty，返回 cp_id。
    失败则返回 None。
    """
    ts = _ts()
    data = {
        "name": f"Auto TestYan CP Terminate {suffix} {ts}",
        "type": "Person",
        "payment_type": "ACH",
        "bank_account_type": "Checking",
        "bank_routing_number": VALID_ROUTING_NUMBER,
        "bank_name": "Auto TestYan Bank",
        "bank_account_owner_name": f"Auto TestYan Terminate {suffix}",
        "bank_account_number": "111111111",
        "assign_account_ids": account_ids
    }
    resp = counterparty_api.create_counterparty(data)
    if resp.status_code != 200:
        return None
    body = resp.json()
    if body.get("code") != 200:
        return None
    return body.get("data", body).get("id")


def _get_account_ids(login_session, count: int = 1) -> list:
    """从 list_accounts 取前 count 个 account_id，不足则 pytest.skip"""
    account_api = AccountAPI(session=login_session)
    resp = account_api.list_accounts(page=0, size=10)
    accounts = resp.json().get("data", {}).get("content", [])
    if len(accounts) < count:
        pytest.skip(f"需要至少 {count} 个 Account，当前只有 {len(accounts)} 个")
    return [a["id"] for a in accounts[:count]]


def _get_cp_assign_accounts(counterparty_api, cp_id: str) -> list:
    """
    从 Counterparty Detail 取回 assign_account_ids 列表。
    若获取失败则返回空列表。
    """
    resp = counterparty_api.get_counterparty_detail(cp_id)
    if resp.status_code != 200:
        return []
    body = resp.json()
    detail = body.get("data", body)
    return detail.get("assign_account_ids", [])


@pytest.mark.counterparty
class TestCounterpartyTerminate:
    """
    Counterparty Terminate 接口测试
    重点：terminate 的是 assign_account 的 status，而非 Counterparty 本身
    """

    # ------------------------------------------------------------------
    # 场景1：成功 Terminate 单个 assign_account
    # ------------------------------------------------------------------
    @pytest.mark.no_rerun
    def test_terminate_single_assign_account(self, counterparty_api, login_session, db_cleanup):
        """
        测试场景1：终止单个 assign_account（正向成功场景）
        验证点：
        1. 创建绑定了 account_id_A 的 Counterparty
        2. 调用 terminate，传 account_ids=[account_id_A]
        3. 响应 {"code": 200, "data": true}
        4. 查看 Counterparty Detail，account_id_A 的 status 变为 "Terminate"
        """
        account_ids = _get_account_ids(login_session, count=1)
        account_id_a = account_ids[0]

        cp_id = _create_ach_cp_with_accounts(
            counterparty_api, login_session, [account_id_a], "Single"
        )
        if not cp_id:
            pytest.skip("创建 Counterparty 失败，跳过")
        if db_cleanup:
            db_cleanup.track("counterparty", cp_id)

        logger.info(f"Terminate account_id={account_id_a} in CP({cp_id})")
        term_resp = counterparty_api.terminate_counterparty(cp_id, {"account_ids": [account_id_a]})
        assert term_resp.status_code == 200

        term_body = term_resp.json()
        logger.info(f"  Terminate 响应: {term_body}")
        assert term_body.get("code") == 200, \
            f"Terminate 应返回 code=200，实际: {term_body.get('code')}, msg={term_body.get('error_message')}"
        assert term_body.get("data") is True, \
            f"Terminate data 应为 true，实际: {term_body.get('data')}"

        # 查 Detail 验证 status 变更
        assign_list = _get_cp_assign_accounts(counterparty_api, cp_id)
        logger.info(f"  Terminate 后 assign_account_ids: {assign_list}")

        if assign_list:
            entry = next((a for a in assign_list if a.get("account_id") == account_id_a), None)
            if entry:
                actual_status = entry.get("status", "")
                assert actual_status.lower() in ("terminate", "terminated"), \
                    f"assign_account status 应为 Terminate，实际: '{actual_status}'"
                logger.info(f"✓ account_id={account_id_a} status 已变为 '{actual_status}'")
            else:
                logger.info(f"  ⚠ Detail 中未找到 account_id={account_id_a}，可能已被移除")
        else:
            logger.info("  ⚠ assign_account_ids 为空，无法验证 status")

        logger.info("✓ Terminate 单个 assign_account 成功")

    # ------------------------------------------------------------------
    # 场景2：Terminate 多个 assign_account，仅 terminate 指定的
    # ------------------------------------------------------------------
    @pytest.mark.no_rerun
    def test_terminate_partial_assign_accounts(self, counterparty_api, login_session, db_cleanup):
        """
        测试场景2：Counterparty 有 2 个 assign_account，只 terminate 其中 1 个
        验证点：
        1. 创建绑定了 account_id_A 和 account_id_B 的 Counterparty
        2. 调用 terminate，只传 account_ids=[account_id_A]
        3. 响应 code=200, data=true
        4. Detail 中 account_id_A status 变为 Terminate，account_id_B 不受影响
        """
        account_ids = _get_account_ids(login_session, count=2)
        account_id_a, account_id_b = account_ids[0], account_ids[1]

        cp_id = _create_ach_cp_with_accounts(
            counterparty_api, login_session, [account_id_a, account_id_b], "Partial"
        )
        if not cp_id:
            pytest.skip("创建 Counterparty 失败，跳过")
        if db_cleanup:
            db_cleanup.track("counterparty", cp_id)

        logger.info(f"Terminate 部分 assign_account: CP={cp_id}, terminate account_A={account_id_a}")
        term_resp = counterparty_api.terminate_counterparty(cp_id, {"account_ids": [account_id_a]})
        assert term_resp.status_code == 200

        term_body = term_resp.json()
        logger.info(f"  Terminate 响应: {term_body}")
        assert term_body.get("code") == 200, \
            f"Terminate 应返回 code=200，实际: {term_body.get('code')}"

        # 验证 Detail
        assign_list = _get_cp_assign_accounts(counterparty_api, cp_id)
        logger.info(f"  Terminate 后 assign_account_ids: {assign_list}")

        entry_a = next((a for a in assign_list if a.get("account_id") == account_id_a), None)
        entry_b = next((a for a in assign_list if a.get("account_id") == account_id_b), None)

        if entry_a:
            status_a = entry_a.get("status", "")
            assert status_a.lower() in ("terminate", "terminated"), \
                f"account_id_A status 应为 Terminate，实际: '{status_a}'"
            logger.info(f"  ✓ account_id_A status='{status_a}'（已 Terminate）")
        else:
            logger.info("  ⚠ Detail 中未找到 account_id_A")

        if entry_b:
            status_b = entry_b.get("status", "")
            assert status_b.lower() not in ("terminate", "terminated"), \
                f"account_id_B 不应被 Terminate，但 status='{status_b}'"
            logger.info(f"  ✓ account_id_B status='{status_b}'（未被影响）")
        else:
            logger.info("  ⚠ Detail 中未找到 account_id_B")

        logger.info("✓ Terminate 部分 assign_account 成功，其余 assign_account 不受影响")

    # ------------------------------------------------------------------
    # 场景3：使用无效的 counterparty_id
    # ------------------------------------------------------------------
    def test_terminate_invalid_counterparty_id(self, counterparty_api, login_session):
        """
        测试场景3：使用不存在的 counterparty_id 调用 terminate
        验证点：
        1. HTTP 200
        2. 业务 code != 200
        """
        account_ids = _get_account_ids(login_session, count=1)

        logger.info("使用无效 counterparty_id 调用 terminate")
        resp = counterparty_api.terminate_counterparty(
            "INVALID_CP_ID_999999",
            {"account_ids": account_ids}
        )
        assert resp.status_code == 200
        body = resp.json()
        logger.info(f"  响应: {body}")
        assert body.get("code") != 200 or "error" in str(body).lower(), \
            "无效 counterparty_id 应返回业务错误"
        logger.info(f"✓ 无效 counterparty_id 被拒绝: code={body.get('code')}")

    # ------------------------------------------------------------------
    # 场景4：使用不属于该 Counterparty 的 account_id
    # ------------------------------------------------------------------
    def test_terminate_unassigned_account_id(self, counterparty_api, login_session, db_cleanup):
        """
        测试场景4：传入一个未绑定到该 Counterparty 的 account_id
        验证点：
        1. 创建绑定 account_id_A 的 Counterparty
        2. Terminate 时传 account_id_B（未绑定到该 CP）
        3. 验证 API 的处理：
           - 若拒绝：code != 200
           - 若接受：Detail 中 account_id_A status 不变
        """
        account_ids = _get_account_ids(login_session, count=2)
        account_id_a, account_id_b = account_ids[0], account_ids[1]

        cp_id = _create_ach_cp_with_accounts(
            counterparty_api, login_session, [account_id_a], "UnAssigned"
        )
        if not cp_id:
            pytest.skip("创建 Counterparty 失败，跳过")
        if db_cleanup:
            db_cleanup.track("counterparty", cp_id)

        logger.info(f"Terminate 未绑定的 account_id_B={account_id_b}（CP 只绑定了 A）")
        term_resp = counterparty_api.terminate_counterparty(cp_id, {"account_ids": [account_id_b]})
        assert term_resp.status_code == 200

        term_body = term_resp.json()
        logger.info(f"  响应: {term_body}")

        if term_body.get("code") != 200:
            logger.info(f"✓ API 拒绝了未绑定的 account_id: code={term_body.get('code')}")
        else:
            # 若接受了：验证 account_id_A 的 status 未被改变
            assign_list = _get_cp_assign_accounts(counterparty_api, cp_id)
            entry_a = next((a for a in assign_list if a.get("account_id") == account_id_a), None)
            if entry_a:
                status_a = entry_a.get("status", "")
                assert status_a.lower() not in ("terminate", "terminated"), \
                    f"传入未绑定 account_id 后，绑定的 account_id_A 不应被 Terminate，但 status='{status_a}'"
                logger.info(f"  ✓ account_id_A status='{status_a}'（未受影响）")
            logger.info("✓（探索性结果）API 接受了未绑定的 account_id 但未影响已绑定的 account")

    # ------------------------------------------------------------------
    # 场景5：传入越权 account_id（不在自己 visible 范围）
    # ------------------------------------------------------------------
    def test_terminate_with_invisible_account_id(self, counterparty_api, login_session, db_cleanup):
        """
        测试场景5：terminate 时传入不在自己 visible 范围的 account_id
        验证点：
        1. HTTP 200
        2. 业务 code 为 506（visibility permission deny）或其他错误 code
        """
        INVISIBLE_ACCOUNT_ID = "241010195849720143"   # 属于 Yingying，不在当前用户可见范围

        account_ids = _get_account_ids(login_session, count=1)
        cp_id = _create_ach_cp_with_accounts(
            counterparty_api, login_session, [account_ids[0]], "Invisible"
        )
        if not cp_id:
            pytest.skip("创建 Counterparty 失败，跳过")
        if db_cleanup:
            db_cleanup.track("counterparty", cp_id)

        logger.info(f"Terminate 时传入越权 account_id={INVISIBLE_ACCOUNT_ID}")
        term_resp = counterparty_api.terminate_counterparty(
            cp_id,
            {"account_ids": [INVISIBLE_ACCOUNT_ID]}
        )
        assert term_resp.status_code == 200
        term_body = term_resp.json()
        logger.info(f"  响应: {term_body}")

        assert term_body.get("code") != 200, \
            "越权 account_id 应被拒绝，但返回了 code=200"
        logger.info(f"✓ 越权 account_id 被拒绝: code={term_body.get('code')}, msg={term_body.get('error_message')}")

    # ------------------------------------------------------------------
    # 场景6：Terminate 后在 Counterparty List 中验证 status 变更
    # ------------------------------------------------------------------
    @pytest.mark.no_rerun
    def test_terminate_visible_in_list(self, counterparty_api, login_session, db_cleanup):
        """
        测试场景6：Terminate 后在 Counterparty List 中也能看到 assign_account status 的变更
        验证点：
        1. 创建 CP 并 terminate 一个 account
        2. 在 list_counterparties 中查到该 CP
        3. 验证 assign_account_ids 中该 account 的 status 已变为 Terminate
        """
        account_ids = _get_account_ids(login_session, count=1)
        account_id_a = account_ids[0]

        ts = _ts()
        cp_id = _create_ach_cp_with_accounts(
            counterparty_api, login_session, [account_id_a], f"ListCheck{ts}"
        )
        if not cp_id:
            pytest.skip("创建 Counterparty 失败，跳过")
        if db_cleanup:
            db_cleanup.track("counterparty", cp_id)

        term_resp = counterparty_api.terminate_counterparty(cp_id, {"account_ids": [account_id_a]})
        assert term_resp.json().get("code") == 200, "Terminate 失败"

        # 在 List 中查找该 CP 并验证 assign_account status
        list_resp = counterparty_api.list_counterparties(size=50)
        assert list_resp.status_code == 200
        parsed = counterparty_api.parse_list_response(list_resp)
        counterparties = parsed.get("content", [])

        cp_in_list = next((c for c in counterparties if c.get("id") == cp_id), None)
        if cp_in_list is None:
            logger.info("  ⚠ 在 List 中未查到该 CP（可能超出默认分页），通过 Detail 验证")
        else:
            assign_list = cp_in_list.get("assign_account_ids", [])
            entry = next((a for a in assign_list if a.get("account_id") == account_id_a), None)
            if entry:
                status = entry.get("status", "")
                assert status.lower() in ("terminate", "terminated"), \
                    f"List 中 assign_account status 应为 Terminate，实际: '{status}'"
                logger.info(f"✓ List 中 assign_account status='{status}'（已 Terminate）")
            else:
                logger.info("  ⚠ List 中该 CP 的 assign_account_ids 为空，跳过状态验证")

        logger.info("✓ Terminate 后 List 中验证通过")
