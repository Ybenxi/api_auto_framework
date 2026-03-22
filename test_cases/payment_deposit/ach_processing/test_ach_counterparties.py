"""
ACH Processing - Counterparties 接口测试用例
GET  /money-movements/ach/counterparties  List ACH Counterparties
POST /money-movements/ach/counterparties  Create ACH Counterparty

Create 必填字段：name, type, bank_account_type, bank_routing_number,
                  bank_name, bank_account_owner_name, bank_account_number
"""
import pytest
import time
from utils.logger import logger

MEMO_PREFIX = "Auto TestYan ACH CP"

pytestmark = pytest.mark.ach_processing


def _name(suffix=""):
    return f"{MEMO_PREFIX} {suffix} {int(time.time())}"


@pytest.mark.ach_processing
class TestListAchCounterparties:

    def _get_content(self, response):
        body = response.json()
        data = body.get("data", body) or {}
        return data.get("content", []) if isinstance(data, dict) else body.get("content", [])

    def test_list_success(self, ach_processing_api):
        """
        测试场景1：成功获取 ACH Counterparty 列表
        Test Scenario1: Successfully List ACH Counterparties
        """
        resp = ach_processing_api.list_counterparties(size=10)
        assert resp.status_code == 200
        body = resp.json()
        assert body.get("code") == 200
        data = body.get("data", {})
        total = data.get("total_elements", 0)
        assert isinstance(data.get("content", []), list)
        logger.info(f"✓ ACH CP 列表: total={total}")

    def test_filter_by_name(self, ach_processing_api):
        """
        测试场景2：按 name 模糊筛选
        Test Scenario2: Filter by Name
        """
        base = self._get_content(ach_processing_api.list_counterparties(size=1))
        if not base:
            pytest.skip("无 CP 数据")
        keyword = (base[0].get("name") or "")[:6]
        if not keyword:
            pytest.skip("name 为空")
        resp = ach_processing_api.list_counterparties(name=keyword, size=10)
        assert resp.status_code == 200
        assert resp.json().get("code") == 200
        filtered = self._get_content(resp)
        if filtered:
            for cp in filtered:
                assert keyword.lower() in (cp.get("name") or "").lower()
        logger.info(f"✓ name 筛选: keyword='{keyword}', 返回 {len(filtered)} 条")

    def test_pagination(self, ach_processing_api):
        """
        测试场景3：分页验证
        Test Scenario3: Pagination
        """
        resp = ach_processing_api.list_counterparties(page=0, size=2)
        assert resp.status_code == 200
        assert resp.json().get("code") == 200
        data = resp.json().get("data", {})
        assert len(data.get("content", [])) <= 2
        logger.info("✓ 分页验证通过")

    def test_nonexistent_name(self, ach_processing_api):
        """
        测试场景4：不存在的 name 返回空列表
        Test Scenario4: Non-existent Name Returns Empty
        """
        resp = ach_processing_api.list_counterparties(name="XYZXYZ_NOT_EXISTS_99999")
        assert resp.status_code == 200
        assert resp.json().get("code") == 200
        assert len(self._get_content(resp)) == 0
        logger.info("✓ 不存在 name 返回空列表")


@pytest.mark.ach_processing
class TestCreateAchCounterparty:

    def test_create_success_minimal(self, ach_processing_api):
        """
        测试场景1：传必填字段创建成功
        Test Scenario1: Create with Required Fields Only
        """
        resp = ach_processing_api.create_counterparty(
            name=_name("Minimal"),
            type="Person",
            bank_account_type="Savings",
            bank_routing_number="091918457",
            bank_name="Test Bank ACH",
            bank_account_owner_name="Auto TestYan Owner",
            bank_account_number="111111111",
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body.get("code") == 200, \
            f"code 应为 200，实际: {body.get('code')}, err={body.get('error_message')}"
        data = body.get("data", body)
        assert data.get("id")
        logger.info(f"✓ ACH CP 最小字段创建成功: id={data.get('id')}")

    def test_create_with_assign_account(self, ach_processing_api, login_session):
        """
        测试场景2：创建时指定 assign_account_ids
        Test Scenario2: Create with assign_account_ids
        """
        from api.account_api import AccountAPI
        accs = AccountAPI(session=login_session).list_accounts(
            page=0, size=1
        ).json().get("data", {}).get("content", [])
        if not accs:
            pytest.skip("无 account 数据")
        acc_id = accs[0]["id"]
        resp = ach_processing_api.create_counterparty(
            name=_name("WithAcc"),
            type="Company",
            bank_account_type="Checking",
            bank_routing_number="091918457",
            bank_name="Test Bank ACH",
            bank_account_owner_name="Auto TestYan Owner",
            bank_account_number="222222222",
            assign_account_ids=[acc_id]
        )
        assert resp.status_code == 200
        assert resp.json().get("code") == 200
        data = resp.json().get("data", resp.json())
        assigns = data.get("assign_account_ids", [])
        if assigns:
            logger.info(f"  assign status: {[a.get('status') for a in assigns]}")
        logger.info(f"✓ 含 assign_account 创建成功: id={data.get('id')}")

    @pytest.mark.parametrize("cp_type", ["Employee", "Company", "Person", "Vendor"])
    def test_create_type_enum(self, ach_processing_api, cp_type):
        """
        测试场景3：type 枚举全覆盖
        Test Scenario3: type Enum Coverage
        """
        resp = ach_processing_api.create_counterparty(
            name=_name(cp_type),
            type=cp_type,
            bank_account_type="Savings",
            bank_routing_number="091918457",
            bank_name="Test Bank ACH",
            bank_account_owner_name="Auto TestYan Owner",
            bank_account_number="333333333",
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body.get("code") == 200, \
            f"type='{cp_type}' 应被接受, err={body.get('error_message')}"
        assert (body.get("data", body)).get("type") == cp_type
        logger.info(f"  ✓ type='{cp_type}' 创建成功")

    @pytest.mark.parametrize("bank_type", ["Savings", "Checking"])
    def test_create_bank_account_type_enum(self, ach_processing_api, bank_type):
        """
        测试场景4：bank_account_type 枚举全覆盖
        Test Scenario4: bank_account_type Enum
        """
        resp = ach_processing_api.create_counterparty(
            name=_name(f"Bank{bank_type}"),
            type="Person",
            bank_account_type=bank_type,
            bank_routing_number="091918457",
            bank_name="Test Bank ACH",
            bank_account_owner_name="Auto TestYan Owner",
            bank_account_number="444444444",
        )
        assert resp.status_code == 200
        assert resp.json().get("code") == 200
        logger.info(f"  ✓ bank_account_type='{bank_type}' 创建成功")

    def test_create_missing_name(self, ach_processing_api):
        """
        测试场景5：缺少必填 name
        Test Scenario5: Missing name Returns Error
        """
        url = ach_processing_api.config.get_full_url("/money-movements/ach/counterparties")
        resp = ach_processing_api.session.post(url, json={
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

    def test_create_missing_routing_number(self, ach_processing_api):
        """
        测试场景6：缺少必填 bank_routing_number
        Test Scenario6: Missing bank_routing_number Returns Error
        """
        url = ach_processing_api.config.get_full_url("/money-movements/ach/counterparties")
        resp = ach_processing_api.session.post(url, json={
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
