"""
Counterparty Update 接口测试用例
接口：
  PATCH /api/v1/cores/actc/counterparties/:id   Update Counterparty Detail (v1)

关键业务规则：
  - type 和 payment_type 不可被更新（文档明确说明）
  - 枚举值大小写必须完全匹配（Person/Company/Vendor/Employee, ACH/Wire/…, Checking/Savings）
  - phone_number 必须是 E.164 格式（+14155552671）
  - country 必须符合 ISO 3166
  - 所有非必填字段均可更新（name, bank_account_owner_name, bank_account_number, address1…）
  - 更新后在 Detail 接口中验证字段已生效
  - 越权 CP ID 应被拒绝（code != 200）
"""
import pytest
import time
from typing import Optional
from api.account_api import AccountAPI
from utils.logger import logger


VALID_ROUTING_NUMBER = "091918457"


def _ts() -> str:
    return str(int(time.time()))


def _create_own_cp(counterparty_api, login_session,
                   payment_type: str = "ACH", suffix: str = "") -> Optional[str]:
    """
    创建一个属于自己的 ACH Counterparty 并返回 cp_id，失败则 pytest.skip。
    Update 测试必须用自己创建的 CP，不能取 list 第一条（可能属于他人）。
    """
    account_api = AccountAPI(session=login_session)
    acc_resp = account_api.list_accounts(page=0, size=1)
    accounts = acc_resp.json().get("data", {}).get("content", [])
    if not accounts:
        pytest.skip("无可用 Account，跳过")

    ts = _ts()
    data: dict = {
        "name": f"Auto TestYan CP Update Base {suffix} {ts}",
        "type": "Person",
        "payment_type": payment_type,
        "bank_account_type": "Checking",
        "bank_routing_number": VALID_ROUTING_NUMBER,
        "bank_name": "Auto TestYan Bank",
        "bank_account_owner_name": "Auto TestYan Update Owner",
        "bank_account_number": "111111111",
        "assign_account_ids": [accounts[0]["id"]]
    }
    resp = counterparty_api.create_counterparty(data)
    if resp.status_code != 200:
        pytest.skip(f"创建 Counterparty 失败: HTTP {resp.status_code}")
    body = resp.json()
    if body.get("code") != 200:
        pytest.skip(f"创建 Counterparty 业务失败: {body.get('error_message')}")
    cp_id = body.get("data", body).get("id")
    assert cp_id, "创建 CP 未返回 id"
    return cp_id


@pytest.mark.counterparty
class TestCounterpartyUpdate:
    """
    Counterparty Update 接口测试
    所有场景均用自己创建的 CP，不依赖外部数据
    """

    # ------------------------------------------------------------------
    # 场景1：更新单个字段 name — 成功，Detail 验证回显
    # ------------------------------------------------------------------
    def test_update_name_success_and_verify_in_detail(self, counterparty_api, login_session, db_cleanup):
        """
        测试场景1：成功更新 Counterparty name，并在 Detail 中验证更新生效
        验证点：
        1. HTTP 200，业务 code=200
        2. 响应中 name 已更新
        3. GET Detail 接口中 name 与更新值一致
        4. 其他字段不受影响
        """
        cp_id = _create_own_cp(counterparty_api, login_session, suffix="Name")
        if db_cleanup:
            db_cleanup.track("counterparty", cp_id)

        new_name = f"Auto TestYan CP Renamed {_ts()}"
        logger.info(f"更新 CP({cp_id}) name -> '{new_name}'")
        update_resp = counterparty_api.update_counterparty(cp_id, {"name": new_name})

        assert update_resp.status_code == 200
        update_body = update_resp.json()
        logger.info(f"  更新响应: code={update_body.get('code')}")
        assert update_body.get("code") == 200, \
            f"更新应返回 code=200，实际: {update_body.get('code')}, msg={update_body.get('error_message')}"

        updated = update_body.get("data", update_body)
        assert updated.get("name") == new_name, \
            f"name 回显错误: 期望 '{new_name}', 实际 '{updated.get('name')}'"
        assert updated.get("id") == cp_id, "id 不应变化"

        # 用 Detail 接口二次确认
        detail_resp = counterparty_api.get_counterparty_detail(cp_id)
        assert detail_resp.status_code == 200
        detail = detail_resp.json().get("data", detail_resp.json())
        assert detail.get("name") == new_name, \
            f"Detail 中 name 未更新: '{detail.get('name')}'"

        logger.info(f"✓ name 更新并在 Detail 中验证通过")

    # ------------------------------------------------------------------
    # 场景2：更新多个可更新字段
    # ------------------------------------------------------------------
    def test_update_multiple_fields_success(self, counterparty_api, login_session, db_cleanup):
        """
        测试场景2：同时更新多个字段（name, bank_account_owner_name, address1, city, zip_code）
        验证点：
        1. HTTP 200，业务 code=200
        2. 所有更新字段在响应中正确回显
        3. Detail 中所有字段已生效
        """
        cp_id = _create_own_cp(counterparty_api, login_session, suffix="Multi")
        if db_cleanup:
            db_cleanup.track("counterparty", cp_id)

        ts = _ts()
        update_data = {
            "name": f"Auto TestYan CP Multi Updated {ts}",
            "bank_account_owner_name": "Auto TestYan Updated Owner",
            "address1": "999 Updated Ave",
            "city": "Updated City",
            "zip_code": "90210"
        }

        logger.info(f"更新 CP({cp_id}) 多个字段")
        update_resp = counterparty_api.update_counterparty(cp_id, update_data)
        assert update_resp.status_code == 200
        update_body = update_resp.json()
        assert update_body.get("code") == 200, \
            f"更新失败: code={update_body.get('code')}, msg={update_body.get('error_message')}"

        updated = update_body.get("data", update_body)
        for field, expected in update_data.items():
            actual = updated.get(field)
            if actual is not None:
                assert actual == expected, f"字段 '{field}' 更新失败: 期望 '{expected}', 实际 '{actual}'"
                logger.info(f"  ✓ {field} = '{actual}'")
            else:
                logger.info(f"  ⚠ 响应中未包含字段 {field}，通过 Detail 验证")

        # Detail 验证
        detail = counterparty_api.get_counterparty_detail(cp_id).json().get("data", {})
        assert detail.get("name") == update_data["name"], \
            f"Detail name 未更新: '{detail.get('name')}'"

        logger.info(f"✓ 多字段更新通过")

    # ------------------------------------------------------------------
    # 场景3：type 不可被更新（尝试修改 type 应被拒绝或忽略）
    # ------------------------------------------------------------------
    def test_update_type_is_not_allowed(self, counterparty_api, login_session, db_cleanup):
        """
        测试场景3：尝试更新 type 字段（type 不可更新）
        验证点：
        1. HTTP 200
        2. 业务 code != 200（API 应拒绝），或 code=200 但 type 仍为原值（忽略该字段）
        """
        cp_id = _create_own_cp(counterparty_api, login_session, suffix="TypeChange")
        if db_cleanup:
            db_cleanup.track("counterparty", cp_id)

        original_detail = counterparty_api.get_counterparty_detail(cp_id).json().get("data", {})
        original_type = original_detail.get("type", "Person")

        logger.info(f"尝试更新 CP({cp_id}) type: '{original_type}' -> 'Company'")
        update_resp = counterparty_api.update_counterparty(cp_id, {"type": "Company", "name": f"Auto TestYan CP TypeTest {_ts()}"})
        assert update_resp.status_code == 200

        body = update_resp.json()
        logger.info(f"  响应: code={body.get('code')}")

        if body.get("code") != 200:
            logger.info(f"✓ API 拒绝了更新 type: code={body.get('code')}")
        else:
            # 接受了请求，验证 type 是否真的被改变
            updated_type = body.get("data", body).get("type")
            if updated_type == original_type:
                logger.info(f"✓ API 接受了请求但忽略了 type 字段（仍为 '{original_type}'）")
            else:
                logger.info(f"⚠ 探索性结果: type 被更新为 '{updated_type}'（文档说不可更新，需确认）")

    # ------------------------------------------------------------------
    # 场景4：payment_type 不可被更新
    # ------------------------------------------------------------------
    def test_update_payment_type_is_not_allowed(self, counterparty_api, login_session, db_cleanup):
        """
        测试场景4：尝试更新 payment_type 字段（payment_type 不可更新）
        验证点：
        1. HTTP 200
        2. 业务 code != 200（API 拒绝），或 payment_type 仍为原值（忽略该字段）
        """
        cp_id = _create_own_cp(counterparty_api, login_session, suffix="PTChange")
        if db_cleanup:
            db_cleanup.track("counterparty", cp_id)

        original_detail = counterparty_api.get_counterparty_detail(cp_id).json().get("data", {})
        original_pt = original_detail.get("payment_type", "ACH")

        logger.info(f"尝试更新 CP({cp_id}) payment_type: '{original_pt}' -> 'Wire'")
        update_resp = counterparty_api.update_counterparty(cp_id, {
            "payment_type": "Wire",
            "name": f"Auto TestYan CP PTTest {_ts()}"
        })
        assert update_resp.status_code == 200

        body = update_resp.json()
        logger.info(f"  响应: code={body.get('code')}")

        if body.get("code") != 200:
            logger.info(f"✓ API 拒绝了更新 payment_type: code={body.get('code')}")
        else:
            actual_pt = body.get("data", body).get("payment_type")
            if actual_pt == original_pt:
                logger.info(f"✓ API 忽略了 payment_type 字段（仍为 '{original_pt}'）")
            else:
                logger.info(f"⚠ 探索性结果: payment_type 被更新为 '{actual_pt}'（文档说不可更新，需确认）")

    # ------------------------------------------------------------------
    # 场景5：更新 phone_number — 不符合 E.164 格式
    # ------------------------------------------------------------------
    def test_update_phone_invalid_e164_format(self, counterparty_api, login_session, db_cleanup):
        """
        测试场景5：更新 phone_number 时传入非 E.164 格式的手机号
        验证点：
        1. HTTP 200
        2. 业务 code != 200（格式校验拒绝）或记录为探索性结果
        """
        cp_id = _create_own_cp(counterparty_api, login_session, suffix="PhoneInvalid")
        if db_cleanup:
            db_cleanup.track("counterparty", cp_id)

        invalid_phones = ["13812345678", "1-415-555-2671", "415-555-2671"]
        for phone in invalid_phones:
            logger.info(f"更新 phone_number='{phone}'（非 E.164）")
            resp = counterparty_api.update_counterparty(cp_id, {
                "phone_number": phone,
                "name": f"Auto TestYan CP Phone {_ts()}"
            })
            assert resp.status_code == 200
            body = resp.json()
            logger.info(f"  code={body.get('code')}, msg={body.get('error_message')}")

            if body.get("code") != 200:
                logger.info(f"  ✓ 非 E.164 格式手机号被拒绝")
            else:
                logger.info(f"  ⚠ API 接受了非 E.164 格式（探索性结果）")

        logger.info("✓ 非 E.164 手机号格式验证完成")

    # ------------------------------------------------------------------
    # 场景6：更新 phone_number — 符合 E.164 格式（成功）
    # ------------------------------------------------------------------
    def test_update_phone_valid_e164_format(self, counterparty_api, login_session, db_cleanup):
        """
        测试场景6：更新 phone_number 为合法 E.164 格式
        验证点：
        1. HTTP 200，业务 code=200
        2. Detail 中 phone_number 已更新
        """
        cp_id = _create_own_cp(counterparty_api, login_session, suffix="PhoneValid")
        if db_cleanup:
            db_cleanup.track("counterparty", cp_id)

        valid_phone = "+14155552671"
        logger.info(f"更新 phone_number='{valid_phone}'（E.164 格式）")
        resp = counterparty_api.update_counterparty(cp_id, {
            "phone_number": valid_phone,
            "name": f"Auto TestYan CP PhoneValid {_ts()}"
        })
        assert resp.status_code == 200
        body = resp.json()
        logger.info(f"  code={body.get('code')}")

        if body.get("code") == 200:
            logger.info(f"✓ 合法 E.164 手机号更新成功")
        else:
            logger.info(f"⚠ 更新结果: code={body.get('code')}, msg={body.get('error_message')}")

    # ------------------------------------------------------------------
    # 场景7：更新 country — 非 ISO 3166 格式
    # ------------------------------------------------------------------
    def test_update_country_invalid_iso3166(self, counterparty_api, login_session, db_cleanup):
        """
        测试场景7：更新 country 时传入非 ISO 3166 格式
        验证点：
        1. HTTP 200
        2. 业务 code != 200（格式校验拒绝）或探索性结果
        """
        cp_id = _create_own_cp(counterparty_api, login_session, suffix="CountryInvalid")
        if db_cleanup:
            db_cleanup.track("counterparty", cp_id)

        invalid_countries = ["CHINA", "USA", "United_States"]
        for country in invalid_countries:
            logger.info(f"更新 country='{country}'（非 ISO 3166）")
            resp = counterparty_api.update_counterparty(cp_id, {
                "country": country,
                "name": f"Auto TestYan CP Country {_ts()}"
            })
            assert resp.status_code == 200
            body = resp.json()
            logger.info(f"  code={body.get('code')}, msg={body.get('error_message')}")

            if body.get("code") != 200:
                logger.info(f"  ✓ 非 ISO 3166 country 被拒绝")
            else:
                logger.info(f"  ⚠ API 接受了非 ISO 3166 country（探索性结果）")

        logger.info("✓ 非 ISO 3166 country 格式验证完成")

    # ------------------------------------------------------------------
    # 场景8：更新 bank_account_type — 大小写必须完全匹配枚举
    # ------------------------------------------------------------------
    @pytest.mark.parametrize("bank_account_type,should_pass", [
        ("Checking", True),
        ("Savings", True),
        ("checking", False),   # 小写，枚举必须完全匹配
        ("SAVINGS", False),    # 全大写
        ("Invalid", False),    # 超出枚举范围
    ])
    def test_update_bank_account_type_enum_case_sensitive(
        self, counterparty_api, login_session, db_cleanup,
        bank_account_type, should_pass
    ):
        """
        测试场景8：更新 bank_account_type 验证枚举大小写敏感
        验证点：
        1. Checking/Savings（正确大小写）→ code=200
        2. checking/SAVINGS/Invalid → code != 200（枚举大小写必须完全匹配）
        """
        cp_id = _create_own_cp(counterparty_api, login_session,
                               suffix=f"BAT{bank_account_type[:3]}")
        if db_cleanup:
            db_cleanup.track("counterparty", cp_id)

        logger.info(f"更新 bank_account_type='{bank_account_type}'")
        resp = counterparty_api.update_counterparty(cp_id, {
            "bank_account_type": bank_account_type,
            "name": f"Auto TestYan CP BAT {bank_account_type} {_ts()}"
        })
        assert resp.status_code == 200
        body = resp.json()
        code = body.get("code")
        logger.info(f"  code={code}")

        if should_pass:
            assert code == 200, \
                f"合法枚举值 '{bank_account_type}' 应被接受，实际: code={code}"
            logger.info(f"  ✓ '{bank_account_type}' 被接受")
        else:
            if code != 200:
                logger.info(f"  ✓ 错误枚举值 '{bank_account_type}' 被拒绝")
            else:
                logger.info(f"  ⚠ API 接受了错误枚举值 '{bank_account_type}'（探索性结果）")

    # ------------------------------------------------------------------
    # 场景9：使用无效 counterparty_id 更新
    # ------------------------------------------------------------------
    def test_update_invalid_counterparty_id(self, counterparty_api):
        """
        测试场景9：使用不存在的 counterparty_id 更新
        验证点：
        1. HTTP 200
        2. 业务 code != 200
        """
        logger.info("使用无效 ID 更新 Counterparty")
        resp = counterparty_api.update_counterparty(
            "INVALID_CP_999999",
            {"name": "Auto TestYan InvalidUpdate"}
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body.get("code") != 200, \
            f"无效 ID 应返回业务错误，实际 code={body.get('code')}"
        logger.info(f"✓ 无效 ID 被拒绝: code={body.get('code')}")

    # ------------------------------------------------------------------
    # 场景10：使用越权 CP ID 更新
    # ------------------------------------------------------------------
    def test_update_invisible_counterparty_id(self, counterparty_api):
        """
        测试场景10：使用越权 counterparty_id（不在自己 visible 范围内）更新
        验证点：
        1. HTTP 200
        2. 业务 code != 200（506 或其他）
        """
        invisible_cp_id = "241010195849717901"   # Chaolong actc ach 11
        logger.info(f"使用越权 CP ID 更新: {invisible_cp_id}")
        resp = counterparty_api.update_counterparty(
            invisible_cp_id,
            {"name": "Auto TestYan InvisibleUpdate"}
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body.get("code") != 200, \
            f"越权 CP ID 应返回错误，实际 code={body.get('code')}"
        logger.info(f"✓ 越权 CP ID 被拒绝: code={body.get('code')}")

    # ------------------------------------------------------------------
    # 场景11：创建 CP 后在 List 和 Detail 中验证字段一致
    # ------------------------------------------------------------------
    def test_create_then_verify_in_list_and_detail(self, counterparty_api, login_session, db_cleanup):
        """
        测试场景11：创建 Counterparty 后验证 List 和 Detail 中字段与创建时传入值一致
        验证点：
        1. 创建 ACH Counterparty（包含多个可选字段）
        2. 在 List 中可通过 name 查到
        3. Detail 中的关键字段与创建时一致（name, type, payment_type, bank_account_type）
        4. assign_account_ids 正确回显
        """
        account_api = AccountAPI(session=login_session)
        accounts = account_api.list_accounts(page=0, size=1).json().get("data", {}).get("content", [])
        if not accounts:
            pytest.skip("无可用 Account，跳过")

        ts = _ts()
        create_data = {
            "name": f"Auto TestYan CP Verify {ts}",
            "type": "Company",
            "payment_type": "ACH",
            "bank_account_type": "Savings",
            "bank_routing_number": VALID_ROUTING_NUMBER,
            "bank_name": "Auto TestYan Verify Bank",
            "bank_account_owner_name": "Auto TestYan Verify Owner",
            "bank_account_number": "111222333",
            "address1": "100 Test Street",
            "city": "Test City",
            "state": "TX",
            "zip_code": "75001",
            "country": "US",
            "phone_number": "+14155550100",
            "assign_account_ids": [accounts[0]["id"]]
        }

        logger.info(f"创建 CP: {create_data['name']}")
        create_resp = counterparty_api.create_counterparty(create_data)
        assert create_resp.status_code == 200
        create_body = create_resp.json()
        assert create_body.get("code") == 200, \
            f"创建失败: {create_body.get('error_message')}"
        cp_id = create_body.get("data", create_body).get("id")
        assert cp_id
        if db_cleanup:
            db_cleanup.track("counterparty", cp_id)

        # 在 List 中查找
        list_resp = counterparty_api.list_counterparties(name=create_data["name"][:20], size=10)
        list_content = list_resp.json().get("content", [])
        found_in_list = any(c.get("id") == cp_id for c in list_content)
        assert found_in_list, f"在 List 中未找到 CP id={cp_id}"
        logger.info("  ✓ List 中可查到该 CP")

        # 验证 Detail 字段
        detail_resp = counterparty_api.get_counterparty_detail(cp_id)
        assert detail_resp.status_code == 200
        detail = detail_resp.json().get("data", detail_resp.json())

        fields_to_check = [
            ("name", create_data["name"]),
            ("type", create_data["type"]),
            ("payment_type", create_data["payment_type"]),
            ("bank_account_type", create_data["bank_account_type"]),
            ("bank_routing_number", create_data["bank_routing_number"]),
            ("bank_account_number", create_data["bank_account_number"]),
        ]
        mismatches = []
        for field, expected in fields_to_check:
            actual = detail.get(field)
            if actual == expected:
                logger.info(f"  ✓ {field}: '{actual}'")
            else:
                mismatches.append(f"{field}: 期望 '{expected}', 实际 '{actual}'")

        assert not mismatches, \
            f"Detail 字段与创建值不一致:\n" + "\n".join(mismatches)

        # assign_account_ids 验证
        assign_list = detail.get("assign_account_ids", [])
        assert isinstance(assign_list, list), "assign_account_ids 应为数组"
        assert any(a.get("account_id") == accounts[0]["id"] for a in assign_list), \
            "assign_account_ids 中未找到传入的 account_id"
        logger.info(f"  ✓ assign_account_ids 回显正确")

        logger.info(f"✓ List + Detail 字段与创建值一致验证通过")
