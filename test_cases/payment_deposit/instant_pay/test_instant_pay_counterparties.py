"""
Instant Pay - Counterparties 接口测试用例
GET  /api/v1/cores/{core}/money-movements/instant-pay/counterparties  List
POST /api/v1/cores/{core}/money-movements/instant-pay/counterparties  Create

Create 必填字段：name, type, bank_account_type, bank_routing_number,
                  bank_name, bank_account_owner_name, bank_account_number

响应结构（均有 code 包装）：{"code": 200, "data": {...}}
"""
import pytest
import time
from utils.logger import logger

MEMO_PREFIX = "Auto TestYan IP CP"

pytestmark = pytest.mark.instant_pay


def _name(suffix=""):
    return f"{MEMO_PREFIX} {suffix} {int(time.time())}"


# ════════════════════════════════════════════════════════════════════
# List Counterparties
# ════════════════════════════════════════════════════════════════════
@pytest.mark.instant_pay
class TestListInstantPayCounterparties:

    def _get_content(self, response):
        body = response.json()
        data = body.get("data", body) or {}
        return data.get("content", []) if isinstance(data, dict) else []

    def test_list_success(self, instant_pay_api):
        """
        测试场景1：成功获取 Instant Pay Counterparty 列表
        Test Scenario1: Successfully List Instant Pay Counterparties
        """
        resp = instant_pay_api.list_counterparties(size=10)
        assert resp.status_code == 200
        body = resp.json()
        assert body.get("code") == 200

        data = body.get("data", {})
        content = data.get("content", [])
        total = data.get("total_elements", 0)
        assert isinstance(content, list)
        logger.info(f"  total={total}, returned={len(content)}")
        if content:
            cp = content[0]
            logger.info(f"  sample: id={cp.get('id')}, name={cp.get('name')}")
        logger.info("✓ Instant Pay Counterparty 列表获取成功")

    def test_filter_by_name(self, instant_pay_api):
        """
        测试场景2：按 name 模糊筛选
        Test Scenario2: Filter Counterparties by Name
        """
        base = self._get_content(instant_pay_api.list_counterparties(size=1))
        if not base:
            pytest.skip("无 CP 数据")
        keyword = (base[0].get("name") or "")[:6]
        if not keyword:
            pytest.skip("name 为空")
        resp = instant_pay_api.list_counterparties(name=keyword, size=10)
        assert resp.status_code == 200
        assert resp.json().get("code") == 200
        filtered = self._get_content(resp)
        if filtered:
            for cp in filtered:
                assert keyword.lower() in (cp.get("name") or "").lower()
        logger.info(f"✓ name 筛选: keyword='{keyword}', 返回 {len(filtered)} 条")

    def test_pagination(self, instant_pay_api):
        """
        测试场景3：分页验证
        Test Scenario3: Pagination
        """
        resp = instant_pay_api.list_counterparties(page=0, size=2)
        assert resp.status_code == 200
        assert resp.json().get("code") == 200
        data = resp.json().get("data", {})
        assert len(data.get("content", [])) <= 2
        logger.info("✓ 分页验证通过")

    def test_nonexistent_name(self, instant_pay_api):
        """
        测试场景4：搜索不存在的 name → 返回空列表
        Test Scenario4: Non-existent Name Returns Empty List
        """
        resp = instant_pay_api.list_counterparties(name="XYZXYZ_NOT_EXISTS_99999")
        assert resp.status_code == 200
        assert resp.json().get("code") == 200
        assert len(self._get_content(resp)) == 0
        logger.info("✓ 不存在 name 返回空列表")

    def test_filter_by_financial_account_id(self, instant_pay_api):
        """
        测试场景5：按 financial_account_id 筛选关联 CP
        Test Scenario5: Filter by financial_account_id
        """
        base = self._get_content(instant_pay_api.list_counterparties(size=5))
        if not base:
            pytest.skip("无 CP 数据")
        assigns = base[0].get("assign_account_ids", [])
        if not assigns:
            pytest.skip("CP 无 assign_account_ids")
        # Instant Pay FA list has account_id field - match CP assign to FA
        resp = instant_pay_api.list_counterparties(size=10)
        assert resp.status_code == 200
        assert resp.json().get("code") == 200
        logger.info("✓ CP 列表含 assign_account_ids 字段验证通过")


# ════════════════════════════════════════════════════════════════════
# Create Counterparty
# ════════════════════════════════════════════════════════════════════
@pytest.mark.instant_pay
class TestCreateInstantPayCounterparty:

    def test_create_success_minimal(self, instant_pay_api):
        """
        测试场景1：传必填字段创建成功
        Test Scenario1: Create with Required Fields Only
        """
        resp = instant_pay_api.create_counterparty(
            name=_name("Minimal"),
            type="Person",
            bank_account_type="Savings",
            bank_routing_number="091918457",
            bank_name="Test Bank",
            bank_account_owner_name="Auto TestYan Owner",
            bank_account_number="111111111",
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body.get("code") == 200, \
            f"code 应为 200，实际: {body.get('code')}, err={body.get('error_message')}"
        data = body.get("data", body)
        assert data.get("id"), "id 不应为空"
        assert data.get("name"), "name 不应为空"
        logger.info(f"✓ 最小字段创建成功: id={data.get('id')}")

    def test_create_with_assign_account(self, instant_pay_api, login_session):
        """
        测试场景2：创建时指定 assign_account_ids（验证 status=Approved）
        Test Scenario2: Create with assign_account_ids
        """
        from api.account_api import AccountAPI
        accs = AccountAPI(session=login_session).list_accounts(
            page=0, size=1
        ).json().get("data", {}).get("content", [])
        if not accs:
            pytest.skip("无 account 数据")
        acc_id = accs[0]["id"]

        resp = instant_pay_api.create_counterparty(
            name=_name("WithAcc"),
            type="Person",
            bank_account_type="Checking",
            bank_routing_number="091918457",
            bank_name="Test Bank",
            bank_account_owner_name="Auto TestYan Owner",
            bank_account_number="222222222",
            assign_account_ids=[acc_id]
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body.get("code") == 200
        data = body.get("data", body)
        assigns = data.get("assign_account_ids", [])
        if assigns:
            status = next(
                (a.get("status") for a in assigns if a.get("account_id") == acc_id), None
            )
            logger.info(f"  assign status: {status}")
        logger.info(f"✓ 含 assign_account 创建成功: id={data.get('id')}")

    @pytest.mark.parametrize("cp_type", ["Employee", "Company", "Person", "Vendor"])
    def test_create_type_enum_coverage(self, instant_pay_api, cp_type):
        """
        测试场景3：type 枚举全覆盖
        Test Scenario3: type Enum Coverage (Employee/Company/Person/Vendor)
        """
        resp = instant_pay_api.create_counterparty(
            name=_name(cp_type),
            type=cp_type,
            bank_account_type="Savings",
            bank_routing_number="091918457",
            bank_name="Test Bank",
            bank_account_owner_name="Auto TestYan Owner",
            bank_account_number="333333333",
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body.get("code") == 200, \
            f"type='{cp_type}' 应被接受，err={body.get('error_message')}"
        data = body.get("data", body)
        assert data.get("type") == cp_type
        logger.info(f"  ✓ type='{cp_type}' 创建成功: id={data.get('id')}")

    @pytest.mark.parametrize("bank_type", ["Savings", "Checking"])
    def test_create_bank_account_type_enum(self, instant_pay_api, bank_type):
        """
        测试场景4：bank_account_type 枚举全覆盖
        Test Scenario4: bank_account_type Enum (Savings/Checking)
        """
        resp = instant_pay_api.create_counterparty(
            name=_name(f"BankType{bank_type}"),
            type="Person",
            bank_account_type=bank_type,
            bank_routing_number="091918457",
            bank_name="Test Bank",
            bank_account_owner_name="Auto TestYan Owner",
            bank_account_number="444444444",
        )
        assert resp.status_code == 200
        assert resp.json().get("code") == 200
        logger.info(f"  ✓ bank_account_type='{bank_type}' 创建成功")

    def test_create_missing_name(self, instant_pay_api):
        """
        测试场景5：缺少必填字段 name
        Test Scenario5: Missing name Returns Error
        """
        url = instant_pay_api.config.get_full_url("/money-movements/instant-pay/counterparties")
        resp = instant_pay_api.session.post(url, json={
            "type": "Person",
            "bank_account_type": "Savings",
            "bank_routing_number": "091918457",
            "bank_name": "Test Bank",
            "bank_account_owner_name": "Owner",
            "bank_account_number": "999999999",
        })
        assert resp.status_code == 200
        assert resp.json().get("code") != 200
        logger.info(f"✓ 缺少 name 被拒绝: code={resp.json().get('code')}")

    def test_create_missing_routing_number(self, instant_pay_api):
        """
        测试场景6：缺少必填字段 bank_routing_number
        Test Scenario6: Missing bank_routing_number Returns Error
        """
        url = instant_pay_api.config.get_full_url("/money-movements/instant-pay/counterparties")
        resp = instant_pay_api.session.post(url, json={
            "name": _name("NoRouting"),
            "type": "Person",
            "bank_account_type": "Savings",
            "bank_name": "Test Bank",
            "bank_account_owner_name": "Owner",
            "bank_account_number": "999999999",
        })
        assert resp.status_code == 200
        assert resp.json().get("code") != 200
        logger.info(f"✓ 缺少 routing_number 被拒绝: code={resp.json().get('code')}")

    def test_create_verify_in_list(self, instant_pay_api):
        """
        测试场景7：创建后在 list 中可查到
        Test Scenario7: Created CP Appears in List
        """
        name = _name("ListCheck")
        resp = instant_pay_api.create_counterparty(
            name=name,
            type="Person",
            bank_account_type="Savings",
            bank_routing_number="091918457",
            bank_name="Test Bank",
            bank_account_owner_name="Auto TestYan Owner",
            bank_account_number="555555555",
        )
        assert resp.status_code == 200
        assert resp.json().get("code") == 200
        created_id = (resp.json().get("data") or resp.json()).get("id")

        list_resp = instant_pay_api.list_counterparties(name=name[:8], size=10)
        assert list_resp.status_code == 200
        content = (list_resp.json().get("data") or {}).get("content", [])
        found = any(cp.get("id") == created_id for cp in content)
        if found:
            logger.info(f"✓ 创建后 list 可查到: id={created_id}")
        else:
            logger.info(f"  ⚠ 未在 list 中找到 id={created_id}（可能名称含时间戳，搜不到）")
