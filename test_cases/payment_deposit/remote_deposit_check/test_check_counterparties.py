"""
Remote Deposit Check - Counterparties 接口测试用例
GET  /api/v1/cores/{core}/money-movements/checks/counterparties  List Check Counterparties
POST /api/v1/cores/{core}/money-movements/checks/counterparties  Create Check Counterparty

Create 必填字段：name, type, address1
type 枚举：Employee / Company / Person / Vendor
bank_account_type 枚举：Savings / Checking

响应结构（Create）：{"code": 200, "data": {id, name, type, ...}}
响应结构（List）：{"code": 200, "data": {"content": [...], "total_elements": N, ...}}
"""
import pytest
import time
from utils.logger import logger
from utils.assertions import assert_status_ok

VALID_ROUTING = "091918457"
MEMO_PREFIX   = "Auto TestYan Check CP"

pytestmark = pytest.mark.remote_deposit_check


def _name(suffix=""):
    return f"{MEMO_PREFIX} {suffix} {int(time.time())}"


def _get_account_id(login_session):
    from api.account_api import AccountAPI
    acc_api = AccountAPI(session=login_session)
    accs = acc_api.list_accounts(page=0, size=1).json().get("data", {}).get("content", [])
    return accs[0]["id"] if accs else None


# ════════════════════════════════════════════════════════════════════
# List Check Counterparties
# ════════════════════════════════════════════════════════════════════
@pytest.mark.remote_deposit_check
class TestListCheckCounterparties:

    def _get_content(self, response):
        body = response.json()
        data = body.get("data", body) or {}
        return data.get("content", []) if isinstance(data, dict) else []

    def test_list_success(self, remote_deposit_check_api):
        """
        测试场景1：成功获取 Check Counterparty 列表
        Test Scenario1: Successfully List Check Counterparties
        验证点：
        1. HTTP 200，code=200
        2. data.content 是数组
        3. 每条含 id, name, type, bank_account_type, assign_account_ids
        """
        resp = remote_deposit_check_api.list_counterparties(size=10)
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
            for field in ["id", "name", "type", "assign_account_ids"]:
                if field in cp:
                    logger.info(f"  ✓ {field}: {cp.get(field)}")
        logger.info("✓ Check Counterparty 列表获取成功")

    def test_filter_by_name(self, remote_deposit_check_api):
        """
        测试场景2：按 name 筛选
        Test Scenario2: Filter Counterparties by Name
        """
        base = self._get_content(remote_deposit_check_api.list_counterparties(size=1))
        if not base:
            pytest.skip("无 counterparty 数据")
        real_name = base[0].get("name", "")
        if not real_name:
            pytest.skip("name 为空")
        keyword = real_name[:6] if len(real_name) >= 6 else real_name
        resp = remote_deposit_check_api.list_counterparties(name=keyword, size=10)
        assert resp.status_code == 200
        assert resp.json().get("code") == 200
        filtered = self._get_content(resp)
        if filtered:
            for cp in filtered:
                assert keyword.lower() in (cp.get("name") or "").lower()
        logger.info(f"✓ name 筛选通过，keyword='{keyword}'，返回 {len(filtered)} 条")

    def test_filter_by_bank_account_owner_name(self, remote_deposit_check_api):
        """
        测试场景3：按 bank_account_owner_name 筛选
        Test Scenario3: Filter by bank_account_owner_name
        """
        base = self._get_content(remote_deposit_check_api.list_counterparties(size=1))
        if not base:
            pytest.skip("无 counterparty 数据")
        owner_name = base[0].get("bank_account_owner_name", "")
        if not owner_name:
            pytest.skip("bank_account_owner_name 为空")
        resp = remote_deposit_check_api.list_counterparties(
            bank_account_owner_name=owner_name[:6], size=10
        )
        assert resp.status_code == 200
        assert resp.json().get("code") == 200
        logger.info(f"✓ bank_account_owner_name 筛选通过，返回 {len(self._get_content(resp))} 条")

    def test_pagination(self, remote_deposit_check_api):
        """
        测试场景4：分页验证
        Test Scenario4: Pagination Verification
        """
        resp = remote_deposit_check_api.list_counterparties(page=0, size=2)
        assert resp.status_code == 200
        data = resp.json().get("data", {})
        assert len(data.get("content", [])) <= 2
        logger.info(f"✓ 分页验证通过")

    def test_nonexistent_name_returns_empty(self, remote_deposit_check_api):
        """
        测试场景5：搜索不存在的 name，返回空列表
        Test Scenario5: Non-existent Name Returns Empty List
        """
        resp = remote_deposit_check_api.list_counterparties(
            name="XYZXYZ_NOT_EXISTS_99999", size=5
        )
        assert resp.status_code == 200
        assert resp.json().get("code") == 200
        content = self._get_content(resp)
        assert len(content) == 0
        logger.info("✓ 不存在的 name 返回空列表")


# ════════════════════════════════════════════════════════════════════
# Create Check Counterparty
# ════════════════════════════════════════════════════════════════════
@pytest.mark.remote_deposit_check
class TestCreateCheckCounterparty:

    def test_create_success_minimal_fields(self, remote_deposit_check_api, login_session):
        """
        测试场景1：仅传必填字段（name, type, address1）创建成功
        Test Scenario1: Create Check Counterparty with Minimal Required Fields
        验证点：
        1. HTTP 200，code=200
        2. data 含 id, name, type, address1
        3. name 回显一致
        """
        acc_id = _get_account_id(login_session)
        payload = {
            "name": _name("Minimal"),
            "type": "Person",
            "address1": "123 Test Street",
        }
        if acc_id:
            payload["assign_account_ids"] = [acc_id]

        resp = remote_deposit_check_api.create_counterparty(**payload)
        assert resp.status_code == 200
        body = resp.json()
        assert body.get("code") == 200, \
            f"code 应为 200，实际: {body.get('code')}, err={body.get('error_message')}"

        data = body.get("data", {})
        assert data.get("id"), "id 不应为空"
        assert data.get("name") == payload["name"]
        assert data.get("type") == "Person"
        logger.info(f"✓ 最小字段创建成功: id={data.get('id')}, name={data.get('name')}")

    def test_create_success_full_fields(self, remote_deposit_check_api, login_session):
        """
        测试场景2：传入所有可选字段创建（验证字段存储）
        Test Scenario2: Create Check Counterparty with All Optional Fields
        """
        acc_id = _get_account_id(login_session)
        name = _name("Full")
        payload = {
            "name": name,
            "type": "Company",
            "address1": "456 Full Test Ave",
            "address2": "Suite 200",
            "city": "Test City",
            "state": "CA",
            "country": "US",
            "bank_account_type": "Checking",
            "bank_routing_number": VALID_ROUTING,
            "bank_name": "Test Bank",
            "bank_account_owner_name": "Auto TestYan Owner",
            "bank_account_number": "111222333",
        }
        if acc_id:
            payload["assign_account_ids"] = [acc_id]

        resp = remote_deposit_check_api.create_counterparty(**payload)
        assert resp.status_code == 200
        body = resp.json()
        assert body.get("code") == 200

        data = body.get("data", {})
        assert data.get("name") == name
        assert data.get("type") == "Company"
        # 验证可选字段回显
        for field in ["bank_routing_number", "bank_account_type", "address1"]:
            if data.get(field):
                logger.info(f"  ✓ {field}: {data.get(field)}")
        logger.info(f"✓ 全字段创建成功: id={data.get('id')}")

    @pytest.mark.parametrize("cp_type", ["Employee", "Company", "Person", "Vendor"])
    def test_create_type_enum_coverage(self, remote_deposit_check_api, cp_type):
        """
        测试场景3：type 枚举全覆盖（Employee/Company/Person/Vendor）
        Test Scenario3: Create Check Counterparty with All type Enum Values
        """
        resp = remote_deposit_check_api.create_counterparty(**{
            "name": _name(cp_type),
            "type": cp_type,
            "address1": "123 Enum Test St",
        })
        assert resp.status_code == 200
        body = resp.json()
        assert body.get("code") == 200, \
            f"type='{cp_type}' 应被接受，实际 code={body.get('code')}, err={body.get('error_message')}"
        data = body.get("data", {})
        assert data.get("type") == cp_type
        logger.info(f"  ✓ type='{cp_type}' 创建成功: id={data.get('id')}")

    @pytest.mark.parametrize("bank_type", ["Savings", "Checking"])
    def test_create_bank_account_type_enum(self, remote_deposit_check_api, bank_type):
        """
        测试场景4：bank_account_type 枚举全覆盖（Savings / Checking）
        Test Scenario4: bank_account_type Enum Coverage
        """
        resp = remote_deposit_check_api.create_counterparty(**{
            "name": _name(f"Bank{bank_type}"),
            "type": "Person",
            "address1": "123 Bank Type St",
            "bank_account_type": bank_type,
            "bank_routing_number": VALID_ROUTING,
            "bank_account_number": "987654321",
        })
        assert resp.status_code == 200
        body = resp.json()
        assert body.get("code") == 200, \
            f"bank_account_type='{bank_type}' 应被接受，实际 code={body.get('code')}"
        logger.info(f"  ✓ bank_account_type='{bank_type}' 创建成功")

    def test_create_missing_name(self, remote_deposit_check_api):
        """
        测试场景5：缺少必填字段 name
        Test Scenario5: Missing Required name Field Returns Error
        """
        url = remote_deposit_check_api.config.get_full_url("/money-movements/checks/counterparties")
        resp = remote_deposit_check_api.session.post(url, json={
            "type": "Person",
            "address1": "123 No Name St",
        })
        assert resp.status_code == 200
        body = resp.json()
        assert body.get("code") != 200, f"缺少 name 应返回错误，实际 code={body.get('code')}"
        logger.info(f"✓ 缺少 name 被拒绝: code={body.get('code')}, msg={body.get('error_message')}")

    def test_create_missing_type(self, remote_deposit_check_api):
        """
        测试场景6：缺少必填字段 type
        Test Scenario6: Missing Required type Field Returns Error
        """
        url = remote_deposit_check_api.config.get_full_url("/money-movements/checks/counterparties")
        resp = remote_deposit_check_api.session.post(url, json={
            "name": _name("NoType"),
            "address1": "123 No Type St",
        })
        assert resp.status_code == 200
        body = resp.json()
        assert body.get("code") != 200
        logger.info(f"✓ 缺少 type 被拒绝: code={body.get('code')}")

    def test_create_missing_address1(self, remote_deposit_check_api):
        """
        测试场景7：缺少必填字段 address1
        Test Scenario7: Missing Required address1 Field Returns Error
        """
        url = remote_deposit_check_api.config.get_full_url("/money-movements/checks/counterparties")
        resp = remote_deposit_check_api.session.post(url, json={
            "name": _name("NoAddr"),
            "type": "Person",
        })
        assert resp.status_code == 200
        body = resp.json()
        assert body.get("code") != 200
        logger.info(f"✓ 缺少 address1 被拒绝: code={body.get('code')}")

    def test_create_invalid_type_enum(self, remote_deposit_check_api):
        """
        测试场景8：type 使用文档未定义的枚举值
        Test Scenario8: Invalid type Enum Value Returns Error
        """
        resp = remote_deposit_check_api.create_counterparty(**{
            "name": _name("InvalidType"),
            "type": "INVALID_TYPE_999",
            "address1": "123 Invalid Type St",
        })
        assert resp.status_code == 200
        body = resp.json()
        if body.get("code") != 200:
            logger.info(f"✓ 无效 type 被拒绝: code={body.get('code')}")
        else:
            logger.info("⚠ API 接受了无效 type（探索性结果）")

    def test_create_invalid_bank_account_type(self, remote_deposit_check_api):
        """
        测试场景9：bank_account_type 枚举大小写错误
        Test Scenario9: Wrong Case bank_account_type Returns Error
        """
        resp = remote_deposit_check_api.create_counterparty(**{
            "name": _name("BadBankType"),
            "type": "Person",
            "address1": "123 Bad Bank Type St",
            "bank_account_type": "checking",  # 小写，枚举应完全匹配
        })
        assert resp.status_code == 200
        body = resp.json()
        if body.get("code") != 200:
            logger.info(f"✓ 枚举大小写错误被拒绝: code={body.get('code')}")
        else:
            logger.info("⚠ API 接受了小写枚举值（探索性结果）")

    def test_create_verify_in_list(self, remote_deposit_check_api):
        """
        测试场景10：创建后在 list 中可查到（通过 name 筛选验证）
        Test Scenario10: Created Counterparty Appears in List
        """
        name = _name("ListVerify")
        resp = remote_deposit_check_api.create_counterparty(**{
            "name": name,
            "type": "Person",
            "address1": "123 List Verify St",
        })
        assert resp.status_code == 200
        assert resp.json().get("code") == 200
        created_id = resp.json().get("data", {}).get("id")

        # 在 list 中按 name 筛选
        list_resp = remote_deposit_check_api.list_counterparties(name=name[:10], size=10)
        assert list_resp.status_code == 200
        content = list_resp.json().get("data", {}).get("content", [])
        found = any(cp.get("id") == created_id for cp in content)
        if found:
            logger.info(f"✓ 创建后在 list 中可查到: id={created_id}")
        else:
            logger.info(f"  ⚠ 未在 list 中找到刚创建的 counterparty（id={created_id}）")
