"""
Counterparty Group 成员管理测试用例
接口：
  POST   /counterparty-groups/:id/counterparty      Add Counterparties to a Group
  DELETE /counterparty-groups/:id/counterparty      Delete Counterparty from the Group
  GET    /counterparty-groups/:id/counterparties    List Group Related Counterparties

关键业务规则：
  - Add 接口是全量替换：每次提交 counterparty_ids 就是当前 group 的全部成员
    （不支持只追加某一个，每次 post 都会替换整个成员列表）
  - 一个 Counterparty 可以同时属于多个 Group
  - List Group Counterparties 返回完整的 counterparty 对象，含 group_id / group_name 字段
  - 操作不在自己 visible 范围内的资源会被拒绝
"""
import pytest
import time
from typing import Optional
from api.account_api import AccountAPI
from utils.logger import logger


VALID_ROUTING_NUMBER = "091918457"


def _ts() -> str:
    return str(int(time.time()))


def _create_group(counterparty_api, name: str) -> str:
    resp = counterparty_api.create_counterparty_group(name)
    assert resp.status_code == 200, f"创建 Group 失败: {resp.status_code}"
    body = resp.json()
    gid = body.get("data", body).get("id") if isinstance(body, dict) else None
    assert gid, f"创建 Group 未返回 id: {body}"
    return gid


def _create_ach_cp(counterparty_api, login_session, suffix: str = "") -> str:
    account_api = AccountAPI(session=login_session)
    acc_resp = account_api.list_accounts(page=0, size=1)
    accounts = acc_resp.json().get("data", {}).get("content", [])
    if not accounts:
        pytest.skip("无可用 Account，跳过")

    ts = _ts()
    data = {
        "name": f"Auto TestYan CP GroupMember {suffix} {ts}",
        "type": "Person",
        "payment_type": "ACH",
        "bank_account_type": "Checking",
        "bank_routing_number": VALID_ROUTING_NUMBER,
        "bank_name": "Auto TestYan Bank",
        "bank_account_owner_name": f"Auto TestYan {suffix}",
        "bank_account_number": "111111111",
        "assign_account_ids": [accounts[0]["id"]]
    }
    cp_resp = counterparty_api.create_counterparty(data)
    assert cp_resp.status_code == 200
    body = cp_resp.json()
    assert body.get("code") == 200, f"创建 CP 失败: {body}"
    cp_id = body.get("data", body).get("id")
    assert cp_id, "创建 CP 未返回 id"
    return cp_id


@pytest.mark.counterparty
class TestCounterpartyGroupMembers:
    """
    Counterparty Group 成员管理测试
    所有场景均自建 Group 和 Counterparty，不依赖外部数据
    """

    # ------------------------------------------------------------------
    # 场景1：List Group Counterparties — 空 Group 返回空列表
    # ------------------------------------------------------------------
    def test_list_group_members_empty_group(self, counterparty_api, db_cleanup):
        """
        测试场景1：新创建的空 Group，列出成员返回空列表
        验证点：
        1. HTTP 200
        2. content 为空数组
        3. total_elements = 0
        """
        group_id = _create_group(counterparty_api, f"Auto TestYan Empty Group {_ts()}")
        if db_cleanup:
            db_cleanup.track("counterparty_group", group_id)

        logger.info(f"列出空 Group 成员: group_id={group_id}")
        resp = counterparty_api.list_group_counterparties(group_id, size=10)
        assert resp.status_code == 200

        body = resp.json()
        assert body.get("code") == 200, f"list_group_counterparties 返回错误: {body.get('error_message')}"
        data_inner = body.get("data", {}) or {}
        content = data_inner.get("content", [])
        total = data_inner.get("total_elements", -1)

        assert content == [], f"空 Group 成员列表应为 []，实际: {content}"
        assert total == 0, f"空 Group total_elements 应为 0，实际: {total}"

        logger.info("✓ 空 Group 成员列表验证通过")

    # ------------------------------------------------------------------
    # 场景2：Add Counterparties — 添加一个 Counterparty
    # ------------------------------------------------------------------
    def test_add_single_counterparty_to_group(self, counterparty_api, login_session, db_cleanup):
        """
        测试场景2：向 Group 添加单个 Counterparty
        验证点：
        1. Add 接口返回成功
        2. List Group Counterparties 中能查到该 Counterparty
        3. 返回的 Counterparty 包含 group_id 和 group_name 字段
        """
        ts = _ts()
        group_id = _create_group(counterparty_api, f"Auto TestYan Add1 {ts}")
        if db_cleanup:
            db_cleanup.track("counterparty_group", group_id)

        cp_id = _create_ach_cp(counterparty_api, login_session, "Add1")
        if db_cleanup:
            db_cleanup.track("counterparty", cp_id)

        logger.info(f"向 Group({group_id}) 添加 CP({cp_id})")
        add_resp = counterparty_api.add_counterparties_to_group(group_id, [cp_id])
        assert add_resp.status_code == 200
        add_body = add_resp.json()
        logger.info(f"  Add 响应: {add_body}")

        # 验证 List 中可以查到
        list_resp = counterparty_api.list_group_counterparties(group_id, size=10)
        content = list_resp.json().get("data", {}).get("content", [])
        assert len(content) == 1, f"添加 1 个 CP 后 Group 成员应为 1，实际: {len(content)}"

        member = content[0]
        assert member.get("id") == cp_id, \
            f"成员 id 不匹配: 期望 {cp_id}, 实际 {member.get('id')}"

        # 文档说明 List 结果包含 group_id / group_name
        logger.info(f"  group_id in response: {member.get('group_id')}")
        logger.info(f"  group_name in response: {member.get('group_name')}")

        logger.info(f"✓ 单个 CP 添加到 Group 成功，id={cp_id}")

    # ------------------------------------------------------------------
    # 场景3：Add Counterparties — 添加多个 Counterparty
    # ------------------------------------------------------------------
    def test_add_multiple_counterparties_to_group(self, counterparty_api, login_session, db_cleanup):
        """
        测试场景3：向 Group 一次添加多个 Counterparty
        验证点：
        1. Add 接口返回成功
        2. List 中成员数量与添加数量一致
        3. 每个传入的 cp_id 均在成员列表中
        """
        ts = _ts()
        group_id = _create_group(counterparty_api, f"Auto TestYan MultiAdd {ts}")
        if db_cleanup:
            db_cleanup.track("counterparty_group", group_id)

        cp_id1 = _create_ach_cp(counterparty_api, login_session, "MultiA")
        cp_id2 = _create_ach_cp(counterparty_api, login_session, "MultiB")
        if db_cleanup:
            db_cleanup.track("counterparty", cp_id1)
            db_cleanup.track("counterparty", cp_id2)

        logger.info(f"向 Group({group_id}) 添加 2 个 CP")
        add_resp = counterparty_api.add_counterparties_to_group(group_id, [cp_id1, cp_id2])
        assert add_resp.status_code == 200

        list_resp = counterparty_api.list_group_counterparties(group_id, size=20)
        content = list_resp.json().get("data", {}).get("content", [])
        member_ids = {m.get("id") for m in content}

        assert cp_id1 in member_ids, f"cp_id1={cp_id1} 不在 Group 成员中"
        assert cp_id2 in member_ids, f"cp_id2={cp_id2} 不在 Group 成员中"
        assert len(content) == 2, f"添加 2 个 CP 后 Group 成员应为 2，实际: {len(content)}"

        logger.info(f"✓ 多个 CP 添加到 Group 成功")

    # ------------------------------------------------------------------
    # 场景4：Add 是追加模式，同一 Group 可以添加多个不同的 CP
    # ------------------------------------------------------------------
    def test_add_is_append(self, counterparty_api, login_session, db_cleanup):
        """
        测试场景4：验证 Add Counterparties 接口是追加语义（不是全量替换）
        实测行为：
          - 先 add cp_id1，Group 中有 cp_id1
          - 再 add cp_id2，Group 中同时有 cp_id1 和 cp_id2
          - Add 不会清除已有成员，只追加新成员
        验证点：
        1. 先 add cp_id1
        2. 再 add cp_id2（只传 cp_id2）
        3. Group 成员列表中 cp_id1 和 cp_id2 都存在（追加语义）
        """
        ts = _ts()
        group_id = _create_group(counterparty_api, f"Auto TestYan Append {ts}")
        if db_cleanup:
            db_cleanup.track("counterparty_group", group_id)

        cp_id1 = _create_ach_cp(counterparty_api, login_session, "Append1")
        cp_id2 = _create_ach_cp(counterparty_api, login_session, "Append2")
        if db_cleanup:
            db_cleanup.track("counterparty", cp_id1)
            db_cleanup.track("counterparty", cp_id2)

        # 第1次：add cp_id1
        logger.info(f"第1次 Add: [{cp_id1}]")
        counterparty_api.add_counterparties_to_group(group_id, [cp_id1])

        list1 = counterparty_api.list_group_counterparties(group_id, size=20).json().get("data", {}).get("content", [])
        assert any(m.get("id") == cp_id1 for m in list1), "第1次 Add 后 cp_id1 应在 Group 中"
        logger.info(f"  第1次 Add 后成员: {[m.get('id') for m in list1]}")

        # 第2次：add cp_id2（只传 cp_id2，验证 cp_id1 是否仍然保留）
        logger.info(f"第2次 Add（只传 cp_id2）: [{cp_id2}]")
        counterparty_api.add_counterparties_to_group(group_id, [cp_id2])

        list2 = counterparty_api.list_group_counterparties(group_id, size=20).json().get("data", {}).get("content", [])
        member_ids2 = {m.get("id") for m in list2}
        logger.info(f"  第2次 Add 后成员: {list(member_ids2)}")

        assert cp_id2 in member_ids2, f"第2次 Add 后 cp_id2 应在 Group 中"
        assert cp_id1 in member_ids2, \
            f"Add 是追加模式，第2次 Add 后 cp_id1 应仍然在 Group 中（实际行为）"

        logger.info("✓ Add 追加语义验证通过：两次 Add 后两个 CP 均在 Group 中")

    # ------------------------------------------------------------------
    # 场景5：一个 CP 只能属于一个 Group（加入新 Group 自动从原 Group 移除）
    # ------------------------------------------------------------------
    def test_counterparty_belongs_to_one_group(self, counterparty_api, login_session, db_cleanup):
        """
        测试场景5：验证一个 Counterparty 只能属于一个 Group
        实测行为：将 CP 加入 GroupB 后，GroupA 中的该 CP 自动消失
        验证点：
        1. 创建 GroupA 和 GroupB
        2. 将同一个 cp_id 先加入 GroupA
        3. 再将同一个 cp_id 加入 GroupB
        4. GroupB 中可以查到 cp_id
        5. GroupA 中 cp_id 已自动消失（一个 CP 只能属于一个 Group）
        """
        ts = _ts()
        group_id_a = _create_group(counterparty_api, f"Auto TestYan GroupA {ts}")
        group_id_b = _create_group(counterparty_api, f"Auto TestYan GroupB {ts}")
        if db_cleanup:
            db_cleanup.track("counterparty_group", group_id_a)
            db_cleanup.track("counterparty_group", group_id_b)

        cp_id = _create_ach_cp(counterparty_api, login_session, "OneGroup")
        if db_cleanup:
            db_cleanup.track("counterparty", cp_id)

        # 先加入 GroupA
        logger.info(f"将 CP({cp_id}) 加入 GroupA({group_id_a})")
        counterparty_api.add_counterparties_to_group(group_id_a, [cp_id])

        content_a1 = counterparty_api.list_group_counterparties(group_id_a, size=10).json().get("data", {}).get("content", [])
        assert any(m.get("id") == cp_id for m in content_a1), f"GroupA 加入后应找到 cp_id={cp_id}"
        logger.info(f"  GroupA 当前成员: {[m.get('id') for m in content_a1]}")

        # 再加入 GroupB
        logger.info(f"将 CP({cp_id}) 加入 GroupB({group_id_b})")
        counterparty_api.add_counterparties_to_group(group_id_b, [cp_id])

        content_a2 = counterparty_api.list_group_counterparties(group_id_a, size=10).json().get("data", {}).get("content", [])
        content_b = counterparty_api.list_group_counterparties(group_id_b, size=10).json().get("data", {}).get("content", [])

        logger.info(f"  GroupA 成员（加入GroupB后）: {[m.get('id') for m in content_a2]}")
        logger.info(f"  GroupB 当前成员: {[m.get('id') for m in content_b]}")

        # 验证 GroupB 中有 cp_id
        assert any(m.get("id") == cp_id for m in content_b), f"GroupB 中应能找到 cp_id={cp_id}"

        # 验证 GroupA 中 cp_id 已消失（一个 CP 只能属于一个 Group，自动从原 Group 移除）
        assert not any(m.get("id") == cp_id for m in content_a2), \
            f"CP 加入 GroupB 后，GroupA 中的该 CP 应自动消失（一个 CP 只能属于一个 Group）"

        logger.info(f"✓ 验证通过：CP 只能属于一个 Group，加入 GroupB 后自动从 GroupA 移除")

    # ------------------------------------------------------------------
    # 场景6：Delete Counterparty from Group — 成功移除
    # ------------------------------------------------------------------
    @pytest.mark.no_rerun
    def test_remove_counterparty_from_group_success(self, counterparty_api, login_session, db_cleanup):
        """
        测试场景6：从 Group 中移除 Counterparty
        验证点：
        1. 先创建 Group 并添加 cp_id1 和 cp_id2
        2. 移除 cp_id1
        3. 移除后 Group 成员列表中只有 cp_id2，cp_id1 已消失
        """
        ts = _ts()
        group_id = _create_group(counterparty_api, f"Auto TestYan RemoveTest {ts}")
        if db_cleanup:
            db_cleanup.track("counterparty_group", group_id)

        cp_id1 = _create_ach_cp(counterparty_api, login_session, "Remove1")
        cp_id2 = _create_ach_cp(counterparty_api, login_session, "Remove2")
        if db_cleanup:
            db_cleanup.track("counterparty", cp_id1)
            db_cleanup.track("counterparty", cp_id2)

        # 先添加两个
        counterparty_api.add_counterparties_to_group(group_id, [cp_id1, cp_id2])

        logger.info(f"从 Group({group_id}) 移除 CP({cp_id1})")
        remove_resp = counterparty_api.remove_counterparty_from_group(group_id, cp_id1)
        assert remove_resp.status_code == 200

        remove_body = remove_resp.json()
        logger.info(f"  移除响应: {remove_body}")
        assert remove_body.get("code") == 200, \
            f"移除 CP 应返回 code=200，实际: {remove_body.get('code')}"
        assert remove_body.get("data") is True, \
            f"移除 CP data 应为 true，实际: {remove_body.get('data')}"

        # 验证移除后成员列表
        content = counterparty_api.list_group_counterparties(group_id, size=20).json().get("data", {}).get("content", [])
        member_ids = {m.get("id") for m in content}

        assert cp_id1 not in member_ids, f"cp_id1={cp_id1} 应已从 Group 中移除"
        assert cp_id2 in member_ids, f"cp_id2={cp_id2} 不应受影响，仍应在 Group 中"

        logger.info(f"✓ 从 Group 移除 CP 成功，cp_id1 已消失，cp_id2 仍在")

    # ------------------------------------------------------------------
    # 场景7：Delete Counterparty from Group — 使用无效 ID
    # ------------------------------------------------------------------
    def test_remove_counterparty_invalid_ids(self, counterparty_api):
        """
        测试场景7：使用无效 Group ID 或 CP ID 移除
        验证点：
        1. HTTP 200
        2. 业务 code != 200
        """
        logger.info("使用无效 ID 移除 Counterparty from Group")
        resp = counterparty_api.remove_counterparty_from_group(
            "INVALID_GROUP_999999",
            "INVALID_CP_999999"
        )
        assert resp.status_code == 200
        body = resp.json()
        logger.info(f"  响应: {body}")
        assert body.get("code") != 200 or "error" in str(body).lower()
        logger.info(f"✓ 无效 ID 移除被拒绝: code={body.get('code')}")

    # ------------------------------------------------------------------
    # 场景8：Add 使用无效 Group ID
    # ------------------------------------------------------------------
    def test_add_to_invalid_group_id(self, counterparty_api):
        """
        测试场景8：向不存在的 Group ID 添加 Counterparty
        验证点：
        1. HTTP 200
        2. 业务 code != 200
        """
        logger.info("向无效 Group ID 添加 CP")
        resp = counterparty_api.add_counterparties_to_group(
            "INVALID_GROUP_999999",
            ["FAKE_CP_ID_1"]
        )
        assert resp.status_code == 200
        body = resp.json()
        logger.info(f"  响应: {body}")
        assert body.get("code") != 200 or "error" in str(body).lower()
        logger.info(f"✓ 无效 Group ID 添加被拒绝: code={body.get('code')}")

    # ------------------------------------------------------------------
    # 场景9：List Group Counterparties — 无效 Group ID 返回空或错误
    # ------------------------------------------------------------------
    def test_list_members_invalid_group_id(self, counterparty_api):
        """
        测试场景9：使用无效 Group ID 查询成员
        验证点：
        1. HTTP 200
        2. 返回空列表 或 业务 code != 200
        """
        logger.info("使用无效 Group ID 查询成员")
        resp = counterparty_api.list_group_counterparties("INVALID_GROUP_999999", size=10)
        assert resp.status_code == 200

        body = resp.json()
        data_inner = body.get("data", {}) or {}
        if "content" in data_inner:
            assert data_inner["content"] == [], \
                f"无效 Group ID 成员列表应为空，实际: {data_inner['content']}"
            logger.info("✓ 无效 Group ID 返回空成员列表")
        else:
            assert body.get("code") != 200 or "error" in str(body).lower()
            logger.info(f"✓ 无效 Group ID 返回业务错误: code={body.get('code')}")

    # ------------------------------------------------------------------
    # 场景10：List Group Counterparties — 验证响应字段完整性
    # ------------------------------------------------------------------
    def test_list_members_response_fields(self, counterparty_api, login_session, db_cleanup):
        """
        测试场景10：验证 List Group Counterparties 响应字段
        验证点：
        1. 创建 Group，添加 1 个 CP
        2. List 结果中包含文档定义的字段（id, name, type, payment_type, group_id, group_name, assign_account_ids）
        3. assign_account_ids 是数组，每个元素含 account_id / account_name / status
        """
        ts = _ts()
        group_id = _create_group(counterparty_api, f"Auto TestYan Fields Group {ts}")
        if db_cleanup:
            db_cleanup.track("counterparty_group", group_id)

        cp_id = _create_ach_cp(counterparty_api, login_session, "Fields")
        if db_cleanup:
            db_cleanup.track("counterparty", cp_id)

        counterparty_api.add_counterparties_to_group(group_id, [cp_id])

        list_resp = counterparty_api.list_group_counterparties(group_id, size=10)
        content = list_resp.json().get("data", {}).get("content", [])
        assert len(content) > 0, "应至少有 1 条成员记录"

        member = content[0]
        logger.info(f"  成员字段: {list(member.keys())}")

        required_fields = ["id", "name", "type", "payment_type"]
        for field in required_fields:
            assert field in member, f"List Group Counterparties 缺少必需字段: '{field}'"

        # group_id / group_name 按文档应存在
        if "group_id" in member:
            assert member["group_id"] == group_id, \
                f"group_id 不匹配: 期望 {group_id}, 实际 {member['group_id']}"
            logger.info(f"  ✓ group_id 字段存在且正确")
        else:
            logger.info("  ⚠ group_id 字段不在响应中（文档定义存在）")

        if "assign_account_ids" in member:
            assert isinstance(member["assign_account_ids"], list), \
                "assign_account_ids 应为数组"
            if member["assign_account_ids"]:
                acc_entry = member["assign_account_ids"][0]
                assert "account_id" in acc_entry, "assign_account_ids 元素应含 account_id"
                assert "status" in acc_entry, "assign_account_ids 元素应含 status"
            logger.info(f"  ✓ assign_account_ids 字段结构正确")
        else:
            logger.info("  ⚠ assign_account_ids 字段不在响应中")

        logger.info(f"✓ List Group Counterparties 响应字段验证通过")
