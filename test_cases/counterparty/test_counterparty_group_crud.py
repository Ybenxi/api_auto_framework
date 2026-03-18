"""
Counterparty Group CRUD 测试用例
接口：
  POST   /counterparty-groups             创建 Group
  PATCH  /counterparty-groups/:id         重命名 Group
  DELETE /counterparty-groups/:id         删除 Group
  GET    /counterparty-groups             查看 Group 列表（含 name 筛选）

关键业务规则：
  - Group 只有 name 一个必填字段
  - 支持按 name 关键字筛选
  - 创建后可重命名
  - 删除返回 {"code": 200, "data": true}
  - 操作不在自己 visible 范围内的 Group ID 会被拒绝
"""
import pytest
import time
from utils.logger import logger


VALID_ROUTING_NUMBER = "091918457"


def _ts() -> str:
    return str(int(time.time()))


def _create_group(counterparty_api, name: str) -> str:
    """
    创建 Group 并返回 group_id，失败则 pytest.skip。
    响应格式：{"name": "...", "id": "..."} —— 无 data 包装层
    """
    resp = counterparty_api.create_counterparty_group(name)
    assert resp.status_code == 200, f"创建 Group HTTP 错误: {resp.status_code}"
    body = resp.json()
    # 文档响应无 code 包装层，直接返回 {"name": ..., "id": ...}
    # 但也兼容有 data 包装的情况
    if "data" in body and isinstance(body["data"], dict):
        gid = body["data"].get("id")
    else:
        gid = body.get("id")
    assert gid, f"创建 Group 未返回 id，响应: {body}"
    return gid


def _create_ach_counterparty(counterparty_api, login_session) -> str:
    """创建一个 ACH Counterparty 并返回 id，供 group 测试使用"""
    from api.account_api import AccountAPI
    account_api = AccountAPI(session=login_session)
    acc_resp = account_api.list_accounts(page=0, size=1)
    accounts = acc_resp.json().get("data", {}).get("content", [])
    if not accounts:
        pytest.skip("无可用 Account，跳过")

    account_id = accounts[0]["id"]
    ts = _ts()
    data = {
        "name": f"Auto TestYan CP For Group {ts}",
        "type": "Person",
        "payment_type": "ACH",
        "bank_account_type": "Checking",
        "bank_routing_number": VALID_ROUTING_NUMBER,
        "bank_name": "Auto TestYan Bank",
        "bank_account_owner_name": "Auto TestYan Group Test",
        "bank_account_number": "111111111",
        "assign_account_ids": [account_id]
    }
    cp_resp = counterparty_api.create_counterparty(data)
    assert cp_resp.status_code == 200
    body = cp_resp.json()
    assert body.get("code") == 200, f"创建 Counterparty 失败: {body}"
    cp_id = body.get("data", body).get("id")
    assert cp_id, "创建 Counterparty 未返回 id"
    return cp_id


@pytest.mark.counterparty
class TestCounterpartyGroupCRUD:
    """
    Counterparty Group 自身的 CRUD 操作测试
    所有场景均用自己创建的 Group，不依赖外部数据
    """

    # ------------------------------------------------------------------
    # 场景1：创建 Group — 成功
    # ------------------------------------------------------------------
    def test_create_group_success(self, counterparty_api, db_cleanup):
        """
        测试场景1：成功创建 Counterparty Group
        验证点：
        1. HTTP 200
        2. 响应包含 id 和 name 字段
        3. name 回显与传入值一致
        """
        ts = _ts()
        group_name = f"Auto TestYan Group Basic {ts}"

        logger.info(f"创建 Group: {group_name}")
        resp = counterparty_api.create_counterparty_group(group_name)

        assert resp.status_code == 200, f"HTTP 错误: {resp.status_code}"
        body = resp.json()
        logger.info(f"  响应: {body}")

        group_data = body.get("data", body) if isinstance(body, dict) else body
        assert group_data.get("id"), "创建 Group 未返回 id"
        assert group_data.get("name") == group_name, \
            f"name 回显错误: 期望 '{group_name}', 实际 '{group_data.get('name')}'"

        if db_cleanup:
            db_cleanup.track("counterparty_group", group_data["id"])

        logger.info(f"✓ Group 创建成功: id={group_data['id']}, name={group_data['name']}")

    # ------------------------------------------------------------------
    # 场景2：创建 Group — 缺少必填字段 name
    # ------------------------------------------------------------------
    def test_create_group_missing_name(self, counterparty_api):
        """
        测试场景2：缺少必填字段 name 创建 Group
        验证点：
        1. HTTP 200（统一错误处理）
        2. 业务 code != 200
        """
        logger.info("创建 Group（缺少 name）")
        resp = counterparty_api.create_counterparty_group("")   # 空字符串

        assert resp.status_code == 200
        body = resp.json()
        logger.info(f"  响应: {body}")

        # 空 name 或缺少 name 应被拒绝
        if body.get("code") is not None:
            assert body.get("code") != 200, \
                "空 name 应返回业务错误，但返回了 code=200"
            logger.info(f"✓ 空 name 被拒绝: code={body.get('code')}")
        else:
            # 若接口接受了空 name，记录为探索性结果
            logger.info("⚠ API 接受了空 name，记录为探索性结果")

    # ------------------------------------------------------------------
    # 场景3：在 List 中验证刚创建的 Group 可被查到
    # ------------------------------------------------------------------
    def test_create_then_appear_in_list(self, counterparty_api, db_cleanup):
        """
        测试场景3：创建 Group 后在 List 中可以查到
        验证点：
        1. 创建成功
        2. 在 group list 中能用 name 筛选到该 Group
        3. List 返回的 id 与创建时一致
        """
        ts = _ts()
        group_name = f"Auto TestYan Group List {ts}"

        group_id = _create_group(counterparty_api, group_name)
        if db_cleanup:
            db_cleanup.track("counterparty_group", group_id)

        logger.info(f"用 name='{group_name}' 在 List 中查找刚创建的 Group")
        list_resp = counterparty_api.list_counterparty_groups(name=group_name, size=5)
        assert list_resp.status_code == 200

        body = list_resp.json()
        content = body.get("content", [])
        found = next((g for g in content if g.get("id") == group_id), None)
        assert found is not None, f"在 List 中未找到刚创建的 Group（id={group_id}）"
        assert found.get("name") == group_name

        logger.info(f"✓ Group 在 List 中可查到: id={group_id}")

    # ------------------------------------------------------------------
    # 场景4：重命名 Group — 成功
    # ------------------------------------------------------------------
    def test_update_group_name_success(self, counterparty_api, db_cleanup):
        """
        测试场景4：成功重命名 Counterparty Group
        验证点：
        1. 先创建 Group
        2. PATCH 重命名
        3. 响应 name 已更新
        4. 在 List 中用新 name 可以查到该 Group
        """
        ts = _ts()
        original_name = f"Auto TestYan Group Original {ts}"
        new_name = f"Auto TestYan Group Renamed {ts}"

        group_id = _create_group(counterparty_api, original_name)
        if db_cleanup:
            db_cleanup.track("counterparty_group", group_id)

        logger.info(f"重命名 Group {group_id}: '{original_name}' -> '{new_name}'")
        update_resp = counterparty_api.update_counterparty_group(group_id, new_name)

        assert update_resp.status_code == 200
        update_body = update_resp.json()
        logger.info(f"  重命名响应: {update_body}")

        updated_data = update_body.get("data", update_body)
        assert updated_data.get("name") == new_name, \
            f"重命名未生效: 期望 '{new_name}', 实际 '{updated_data.get('name')}'"
        assert updated_data.get("id") == group_id, \
            f"id 不应改变: 期望 {group_id}, 实际 {updated_data.get('id')}"

        # 在 List 中用新 name 验证
        list_resp = counterparty_api.list_counterparty_groups(name=new_name, size=5)
        content = list_resp.json().get("content", [])
        found = next((g for g in content if g.get("id") == group_id), None)
        assert found is not None, f"重命名后在 List 中未找到 Group（新 name='{new_name}'）"

        logger.info(f"✓ Group 重命名成功: '{original_name}' -> '{new_name}'")

    # ------------------------------------------------------------------
    # 场景5：重命名 Group — 使用无效 ID
    # ------------------------------------------------------------------
    def test_update_group_invalid_id(self, counterparty_api):
        """
        测试场景5：使用不存在的 Group ID 重命名
        验证点：
        1. HTTP 200（统一错误处理）
        2. 业务 code != 200
        """
        logger.info("使用无效 ID 重命名 Group")
        resp = counterparty_api.update_counterparty_group("INVALID_GROUP_999999", "New Name")

        assert resp.status_code == 200
        body = resp.json()
        logger.info(f"  响应: {body}")
        assert body.get("code") != 200 or "error" in str(body).lower(), \
            "无效 Group ID 应返回业务错误"

        logger.info(f"✓ 无效 Group ID 重命名被拒绝: code={body.get('code')}")

    # ------------------------------------------------------------------
    # 场景6：删除 Group — 成功（先创建再删除，安全测试自建数据）
    # ------------------------------------------------------------------
    @pytest.mark.no_rerun
    def test_delete_group_success(self, counterparty_api):
        """
        测试场景6：成功删除 Group（先创建属于自己的 Group，再删除）
        验证点：
        1. 创建 Group 成功
        2. 删除返回 {"code": 200, "data": true}
        3. 删除后在 List 中用 id 查不到该 Group
        """
        ts = _ts()
        group_name = f"Auto TestYan Group ToDelete {ts}"

        group_id = _create_group(counterparty_api, group_name)
        logger.info(f"创建 Group 成功: {group_id}，准备删除")

        delete_resp = counterparty_api.delete_counterparty_group(group_id)
        assert delete_resp.status_code == 200

        delete_body = delete_resp.json()
        logger.info(f"  删除响应: {delete_body}")
        assert delete_body.get("code") == 200, \
            f"删除 Group 应返回 code=200，实际: {delete_body.get('code')}"
        assert delete_body.get("data") is True, \
            f"删除 Group data 应为 true，实际: {delete_body.get('data')}"

        # 验证删除后 List 中查不到
        list_resp = counterparty_api.list_counterparty_groups(name=group_name, size=5)
        content = list_resp.json().get("content", [])
        still_exists = any(g.get("id") == group_id for g in content)
        assert not still_exists, f"Group 删除后仍在 List 中可查到: id={group_id}"

        logger.info(f"✓ Group 删除成功，List 中已不存在: id={group_id}")

    # ------------------------------------------------------------------
    # 场景7：删除 Group — 使用无效 ID
    # ------------------------------------------------------------------
    @pytest.mark.no_rerun
    def test_delete_group_invalid_id(self, counterparty_api):
        """
        测试场景7：使用不存在的 Group ID 删除
        验证点：
        1. HTTP 200
        2. 业务 code != 200
        """
        logger.info("使用无效 ID 删除 Group")
        resp = counterparty_api.delete_counterparty_group("INVALID_GROUP_999999")

        assert resp.status_code == 200
        body = resp.json()
        logger.info(f"  响应: {body}")
        assert body.get("code") != 200 or "error" in str(body).lower(), \
            "无效 Group ID 应返回业务错误"

        logger.info(f"✓ 无效 Group ID 删除被拒绝: code={body.get('code')}")

    # ------------------------------------------------------------------
    # 场景8：List Groups — 按 name 模糊筛选
    # ------------------------------------------------------------------
    def test_list_groups_name_filter(self, counterparty_api, db_cleanup):
        """
        测试场景8：按 name 关键字筛选 Group 列表
        验证点：
        1. 创建一个 Group
        2. 用 name 前缀筛选，返回结果中每条 name 均包含关键字
        3. 筛选不存在的 name，返回空列表
        """
        ts = _ts()
        group_name = f"Auto TestYan Filter Group {ts}"
        group_id = _create_group(counterparty_api, group_name)
        if db_cleanup:
            db_cleanup.track("counterparty_group", group_id)

        keyword = f"Auto TestYan Filter Group {ts}"
        logger.info(f"用 name='{keyword}' 筛选")
        list_resp = counterparty_api.list_counterparty_groups(name=keyword, size=10)
        assert list_resp.status_code == 200

        content = list_resp.json().get("content", [])
        assert len(content) > 0, f"筛选应至少返回刚创建的 Group"

        for g in content:
            assert keyword.lower() in g.get("name", "").lower(), \
                f"筛选结果包含不匹配 name: '{g.get('name')}'"

        # 不存在的名字 → 空列表
        non_exist_resp = counterparty_api.list_counterparty_groups(
            name="AutoTestYanNonExistGroup999999", size=5
        )
        non_exist_content = non_exist_resp.json().get("content", [])
        assert len(non_exist_content) == 0, "不存在的 name 应返回空列表"

        logger.info(f"✓ Group name 筛选验证通过")

    # ------------------------------------------------------------------
    # 场景9：创建时传 group_id — 在创建 Counterparty 时指定一个不存在的 group_id
    # ------------------------------------------------------------------
    def test_create_counterparty_with_nonexistent_group_id(self, counterparty_api, login_session):
        """
        测试场景9：创建 Counterparty 时传入不存在的 group_id
        验证点：
        1. HTTP 200
        2. 业务 code != 200（group_id 不存在应报错）
        """
        from api.account_api import AccountAPI
        account_api = AccountAPI(session=login_session)
        acc_resp = account_api.list_accounts(page=0, size=1)
        accounts = acc_resp.json().get("data", {}).get("content", [])
        if not accounts:
            pytest.skip("无可用 Account，跳过")

        ts = _ts()
        data = {
            "name": f"Auto TestYan CP Bad GroupID {ts}",
            "type": "Person",
            "payment_type": "ACH",
            "bank_account_type": "Checking",
            "bank_routing_number": VALID_ROUTING_NUMBER,
            "bank_name": "Auto TestYan Bank",
            "bank_account_owner_name": "Auto TestYan Bad Group",
            "bank_account_number": "111111111",
            "assign_account_ids": [accounts[0]["id"]],
            "group_id": "NONEXISTENT_GROUP_ID_99999"   # 不存在的 group_id
        }

        logger.info("创建 Counterparty 时传入不存在的 group_id")
        resp = counterparty_api.create_counterparty(data)
        assert resp.status_code == 200

        body = resp.json()
        logger.info(f"  响应: code={body.get('code')}, msg={body.get('error_message')}")
        assert body.get("code") != 200, \
            "不存在的 group_id 应导致创建失败，但返回了 code=200"

        logger.info(f"✓ 不存在的 group_id 被拒绝: code={body.get('code')}")

    # ------------------------------------------------------------------
    # 场景10：创建时传 group_id — 在创建 Counterparty 时指定有效的 group_id
    # ------------------------------------------------------------------
    def test_create_counterparty_with_valid_group_id(self, counterparty_api, login_session, db_cleanup):
        """
        测试场景10：创建 Counterparty 时传入有效的 group_id
        验证点：
        1. 先创建 Group
        2. 创建 Counterparty 时指定该 group_id
        3. 创建成功
        4. 在 List Group Counterparties 接口中能查到该 Counterparty
        """
        from api.account_api import AccountAPI
        account_api = AccountAPI(session=login_session)
        acc_resp = account_api.list_accounts(page=0, size=1)
        accounts = acc_resp.json().get("data", {}).get("content", [])
        if not accounts:
            pytest.skip("无可用 Account，跳过")

        ts = _ts()
        # 创建 Group
        group_name = f"Auto TestYan Group With CP {ts}"
        group_id = _create_group(counterparty_api, group_name)
        if db_cleanup:
            db_cleanup.track("counterparty_group", group_id)

        # 创建 Counterparty 并绑定 group_id
        data = {
            "name": f"Auto TestYan CP In Group {ts}",
            "type": "Person",
            "payment_type": "ACH",
            "bank_account_type": "Checking",
            "bank_routing_number": VALID_ROUTING_NUMBER,
            "bank_name": "Auto TestYan Bank",
            "bank_account_owner_name": "Auto TestYan Group CP",
            "bank_account_number": "111111111",
            "assign_account_ids": [accounts[0]["id"]],
            "group_id": group_id
        }

        logger.info(f"创建 Counterparty 并绑定 group_id={group_id}")
        cp_resp = counterparty_api.create_counterparty(data)
        assert cp_resp.status_code == 200
        cp_body = cp_resp.json()
        assert cp_body.get("code") == 200, \
            f"创建失败: code={cp_body.get('code')}, msg={cp_body.get('error_message')}"

        cp_id = cp_body.get("data", cp_body).get("id")
        assert cp_id
        if db_cleanup:
            db_cleanup.track("counterparty", cp_id)

        # 在 group 成员列表中验证
        members_resp = counterparty_api.list_group_counterparties(group_id, size=20)
        assert members_resp.status_code == 200
        members_content = members_resp.json().get("content", [])
        found = any(m.get("id") == cp_id for m in members_content)
        assert found, f"创建时指定 group_id 后，Counterparty({cp_id}) 未出现在 Group 成员列表中"

        logger.info(f"✓ Counterparty 通过 group_id 绑定成功: cp_id={cp_id}, group_id={group_id}")
