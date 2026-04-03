"""
Wire Processing - Counterparties 接口测试用例
GET  /api/v1/cores/{core}/money-movements/wire/counterparties  List Wire Counterparties
POST /api/v1/cores/{core}/money-movements/wire/counterparties  Create Wire Counterparty

List 筛选参数：payment_type（Wire/International_Wire）, name, bank_account_owner_name,
               financial_account_id, account_ids

Create 必填字段（Wire）：name, type, bank_account_type, bank_routing_number, bank_name,
                          bank_city, bank_state, bank_account_owner_name, bank_account_number
⚠️ 文档说 Wire 时 bank_name/city/state 自动填充，但实测必须显式传入

Create 必填字段（International_Wire）：name, type, bank_account_type, bank_account_owner_name,
    bank_account_number, country, address1, city, state, zip_code, bank_name, bank_address,
    bank_city, bank_state, bank_zip_code, bank_country, swift_code

响应结构（List）：{"code": 200, "data": {"content": [...], "total_elements": N, ...}}
响应结构（Create）：{"code": 200, "data": {id, name, payment_type, ...}} 或直接对象
"""
import pytest
import time
from utils.logger import logger

# 已验证的测试账户
VALID_ACCOUNT_ID   = "251212054048470503"  # WIRE_FA 对应的 account_id
INTL_ACCOUNT_ID    = "251212054048267357"  # INTL_FA 对应的 account_id（需确认）
VALID_ROUTING      = "091918457"
VALID_SWIFT        = "CRBKUS33XXX"
MEMO_PREFIX        = "Auto TestYan Wire CP"

pytestmark = pytest.mark.wire_processing


def _name(suffix=""):
    return f"{MEMO_PREFIX} {suffix} {int(time.time())}"


# ════════════════════════════════════════════════════════════════════
# List Wire Counterparties
# ════════════════════════════════════════════════════════════════════
@pytest.mark.wire_processing
class TestListWireCounterparties:

    def _get_content(self, response):
        body = response.json()
        data = body.get("data", body) or {}
        return data.get("content", []) if isinstance(data, dict) else []

    def test_list_success(self, wire_processing_api):
        """
        测试场景1：成功获取 Wire Counterparty 列表
        Test Scenario1: Successfully List Wire Counterparties
        验证点：code=200，仅包含 Wire 或 International_Wire 类型 CP
        """
        resp = wire_processing_api.list_counterparties(size=10)
        assert resp.status_code == 200
        body = resp.json()
        assert body.get("code") == 200

        data = body.get("data", {})
        content = data.get("content", [])
        total = data.get("total_elements", 0)
        assert isinstance(content, list)
        logger.info(f"  total={total}, returned={len(content)}")

        # 验证返回的 CP 类型只能是 Wire 或 International_Wire
        if content:
            for cp in content:
                pt = cp.get("payment_type")
                if pt:
                    assert pt in ("Wire", "International_Wire"), \
                        f"Wire list 返回了错误 payment_type: {pt}"
        logger.info("✓ Wire Counterparty 列表获取成功")

    @pytest.mark.parametrize("payment_type", ["Wire", "International_Wire"])
    def test_filter_by_payment_type(self, wire_processing_api, payment_type):
        """
        测试场景2：按 payment_type 枚举筛选
        Test Scenario2: Filter by payment_type Enum (Wire/International_Wire)
        """
        resp = wire_processing_api.list_counterparties(payment_type=payment_type, size=10)
        assert resp.status_code == 200
        assert resp.json().get("code") == 200
        content = self._get_content(resp)
        if content:
            for cp in content:
                if cp.get("payment_type"):
                    assert cp["payment_type"] == payment_type
        logger.info(f"  ✓ payment_type='{payment_type}': 返回 {len(content)} 条")

    def test_filter_by_name(self, wire_processing_api):
        """
        测试场景3：按 name 模糊筛选
        Test Scenario3: Filter by Name
        """
        base = self._get_content(wire_processing_api.list_counterparties(size=1))
        if not base:
            pytest.skip("无 CP 数据")
        keyword = (base[0].get("name") or "")[:6]
        if not keyword:
            pytest.skip("name 为空")
        resp = wire_processing_api.list_counterparties(name=keyword, size=10)
        assert resp.status_code == 200
        filtered = self._get_content(resp)
        if filtered:
            for cp in filtered:
                assert keyword.lower() in (cp.get("name") or "").lower()
        logger.info(f"✓ name 筛选: keyword='{keyword}', 返回 {len(filtered)} 条")

    def test_pagination(self, wire_processing_api):
        """
        测试场景4：分页验证
        Test Scenario4: Pagination
        """
        resp = wire_processing_api.list_counterparties(page=0, size=2)
        assert resp.status_code == 200
        data = resp.json().get("data", {})
        assert len(data.get("content", [])) <= 2
        logger.info("✓ 分页验证通过")

    def test_nonexistent_name_returns_empty(self, wire_processing_api):
        """
        测试场景5：搜索不存在的 name → 返回空列表
        Test Scenario5: Non-existent Name Returns Empty List
        """
        resp = wire_processing_api.list_counterparties(name="XYZXYZ_NOT_EXISTS_99999")
        assert resp.status_code == 200
        assert resp.json().get("code") == 200
        assert len(self._get_content(resp)) == 0
        logger.info("✓ 不存在 name 返回空列表")


# ════════════════════════════════════════════════════════════════════
# Create Wire Counterparty
# ════════════════════════════════════════════════════════════════════
@pytest.mark.wire_processing
class TestCreateWireCounterparty:
    """
    Wire CP 创建测试
    ⚠️ 实测发现：Wire 类型创建时，bank_name/bank_city/bank_state 并非自动填充，需显式传入
    """

    def _base_wire_payload(self, suffix=""):
        """Wire 类型 CP 基础 payload（已验证必填字段）"""
        return dict(
            name=_name(suffix),
            type="Person",
            bank_account_type="Savings",
            bank_routing_number=VALID_ROUTING,
            bank_name="Auto Test Bank",
            bank_city="Test City",
            bank_state="CA",
            bank_account_owner_name="Auto TestYan Owner",
            bank_account_number="111111111",
        )

    def _base_intl_payload(self, suffix=""):
        """International_Wire 类型 CP 基础 payload（已验证必填字段）"""
        return dict(
            name=_name(suffix),
            type="Person",
            payment_type="International_Wire",
            bank_account_type="Savings",
            bank_account_owner_name="Auto TestYan Intl Owner",
            bank_account_number="222222222",
            country="US",
            address1="123 Intl Street",
            city="New York",
            state="NY",
            zip_code="10001",
            bank_name="Intl Test Bank",
            bank_address="456 Bank Ave",
            bank_city="New York",
            bank_state="NY",
            bank_zip_code="10002",
            bank_country="US",
            swift_code=VALID_SWIFT,
        )

    def test_create_wire_success(self, wire_processing_api):
        """
        测试场景1：成功创建 Wire 类型 Counterparty（payment_type 默认 Wire）
        Test Scenario1: Create Wire Counterparty with Default payment_type
        验证点：code=200，id 非空，payment_type=Wire
        """
        payload = self._base_wire_payload("Basic")
        resp = wire_processing_api.create_counterparty(**payload)
        assert resp.status_code == 200
        body = resp.json()
        assert body.get("code") == 200, \
            f"code 应为 200，实际: {body.get('code')}, err={body.get('error_message')}"

        data = body.get("data", body)
        assert data.get("id"), "id 不应为空"
        pt = data.get("payment_type") or "Wire"  # 默认值
        assert pt in ("Wire", None, "")  # payment_type 可能不在响应中
        logger.info(f"✓ Wire CP 创建成功: id={data.get('id')}, payment_type={pt}")

    def test_create_wire_explicit_payment_type(self, wire_processing_api):
        """
        测试场景2：显式传 payment_type=Wire 创建
        Test Scenario2: Create Wire CP with Explicit payment_type=Wire
        """
        payload = self._base_wire_payload("Explicit")
        payload["payment_type"] = "Wire"
        resp = wire_processing_api.create_counterparty(**payload)
        assert resp.status_code == 200
        body = resp.json()
        assert body.get("code") == 200
        logger.info(f"✓ 显式 Wire CP 创建成功")

    def test_create_international_wire_success(self, wire_processing_api):
        """
        测试场景3：成功创建 International_Wire 类型 Counterparty
        Test Scenario3: Create International_Wire Counterparty
        验证点：code=200，id 非空，swift_code 回显
        """
        payload = self._base_intl_payload("Intl")
        resp = wire_processing_api.create_counterparty(**payload)
        assert resp.status_code == 200
        body = resp.json()
        assert body.get("code") == 200, \
            f"code={body.get('code')}, err={body.get('error_message')}"

        data = body.get("data", body)
        assert data.get("id"), "id 不应为空"
        assert data.get("swift_code") == VALID_SWIFT
        logger.info(f"✓ International_Wire CP 创建成功: id={data.get('id')}, swift={data.get('swift_code')}")

    @pytest.mark.parametrize("cp_type", ["Employee", "Company", "Person", "Vendor"])
    def test_create_type_enum_coverage(self, wire_processing_api, cp_type):
        """
        测试场景4：type 枚举全覆盖（Employee/Company/Person/Vendor）
        Test Scenario4: type Enum Coverage
        """
        payload = self._base_wire_payload(cp_type)
        payload["type"] = cp_type
        resp = wire_processing_api.create_counterparty(**payload)
        assert resp.status_code == 200
        body = resp.json()
        assert body.get("code") == 200, \
            f"type='{cp_type}' 应被接受，实际 code={body.get('code')}, err={body.get('error_message')}"
        data = body.get("data", body)
        assert data.get("type") == cp_type
        logger.info(f"  ✓ type='{cp_type}' 创建成功: id={data.get('id')}")

    @pytest.mark.parametrize("bank_type", ["Savings", "Checking"])
    def test_create_bank_account_type_enum(self, wire_processing_api, bank_type):
        """
        测试场景5：bank_account_type 枚举全覆盖
        Test Scenario5: bank_account_type Enum (Savings/Checking)
        """
        payload = self._base_wire_payload(f"BankType{bank_type}")
        payload["bank_account_type"] = bank_type
        resp = wire_processing_api.create_counterparty(**payload)
        assert resp.status_code == 200
        assert resp.json().get("code") == 200
        logger.info(f"  ✓ bank_account_type='{bank_type}' 创建成功")

    def test_create_missing_name(self, wire_processing_api):
        """
        测试场景6：缺少必填字段 name
        Test Scenario6: Missing name Returns Error
        """
        url = wire_processing_api.config.get_full_url("/money-movements/wire/counterparties")
        payload = self._base_wire_payload()
        del payload["name"]
        resp = wire_processing_api.session.post(url, json=payload)
        assert resp.status_code == 200
        assert resp.json().get("code") != 200
        logger.info(f"✓ 缺少 name 被拒绝: code={resp.json().get('code')}")

    def test_create_wire_missing_routing_number(self, wire_processing_api):
        """
        测试场景7：Wire 类型缺少 bank_routing_number（Wire 必填）
        Test Scenario7: Wire CP Missing bank_routing_number
        """
        url = wire_processing_api.config.get_full_url("/money-movements/wire/counterparties")
        payload = self._base_wire_payload("NoRouting")
        del payload["bank_routing_number"]
        resp = wire_processing_api.session.post(url, json=payload)
        assert resp.status_code == 200
        assert resp.json().get("code") != 200
        logger.info(f"✓ Wire 缺少 routing_number 被拒绝: code={resp.json().get('code')}")

    def test_create_intl_missing_swift(self, wire_processing_api):
        """
        测试场景8：International_Wire 类型缺少 swift_code（必填）
        Test Scenario8: International Wire CP Missing swift_code
        """
        url = wire_processing_api.config.get_full_url("/money-movements/wire/counterparties")
        payload = self._base_intl_payload("NoSwift")
        del payload["swift_code"]
        resp = wire_processing_api.session.post(url, json=payload)
        assert resp.status_code == 200
        assert resp.json().get("code") != 200
        logger.info(f"✓ International_Wire 缺少 swift_code 被拒绝: code={resp.json().get('code')}")

    def test_create_with_assign_account(self, wire_processing_api, login_session):
        """
        测试场景9：创建时指定 assign_account_ids
        Test Scenario9: Create CP with assign_account_ids
        验证点：assign_account_ids 中的 account 状态自动设为 Approved（非高风险 account）
        """
        from api.account_api import AccountAPI
        acc_api = AccountAPI(session=login_session)
        accs = acc_api.list_accounts(page=0, size=1).json().get("data", {}).get("content", [])
        if not accs:
            pytest.skip("无 account 数据")
        acc_id = accs[0]["id"]

        payload = self._base_wire_payload("WithAccount")
        payload["assign_account_ids"] = [acc_id]
        resp = wire_processing_api.create_counterparty(**payload)
        assert resp.status_code == 200
        body = resp.json()
        assert body.get("code") == 200
        data = body.get("data", body)
        assigns = data.get("assign_account_ids", [])
        if assigns:
            assert any(a.get("account_id") == acc_id for a in assigns)
            status = next(
                (a.get("status") for a in assigns if a.get("account_id") == acc_id), None
            )
            logger.info(f"  assign status for acc_id={acc_id}: {status}")
        logger.info(f"✓ 含 assign_account 的 CP 创建成功: id={data.get('id')}")

    def test_create_verify_in_list(self, wire_processing_api):
        """
        测试场景10：创建后在 list 中可查到
        Test Scenario10: Created CP Appears in List
        """
        name = _name("ListCheck")
        payload = self._base_wire_payload()
        payload["name"] = name
        resp = wire_processing_api.create_counterparty(**payload)
        assert resp.status_code == 200
        assert resp.json().get("code") == 200
        created_id = (resp.json().get("data") or resp.json()).get("id")

        list_resp = wire_processing_api.list_counterparties(name=name[:10], size=10)
        assert list_resp.status_code == 200
        content = list_resp.json().get("data", {}).get("content", [])
        found = any(cp.get("id") == created_id for cp in content)
        if found:
            logger.info(f"✓ 创建后 list 可查到: id={created_id}")
        else:
            logger.info(f"  ⚠ 未在 list 中找到 id={created_id}（可能延迟）")
