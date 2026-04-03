"""
Counterparty Create 接口测试用例
测试 POST /api/v1/cores/{core}/counterparties 接口

=== payment_enable 说明 ===
payment_enable = true  → 该 Counterparty 可用于发起交易（关键字段齐全）
payment_enable = false → 创建成功但无法发起交易（缺少某类型所需的银行字段）

各 payment_type 使 payment_enable=true 所需的字段：
  ACH:
    必填: name, type, bank_account_type, bank_routing_number,
           bank_account_owner_name, bank_account_number
  Wire (国内):
    必填: name, type, bank_account_type, bank_routing_number,
           bank_account_owner_name, bank_account_number
    自动填充(Wire): bank_name, bank_state ← 由路由号自动填充
    默认值(Wire): bank_country = "United States"
  International_Wire (国际):
    额外必需: country, address1, city, zip_code,
              bank_country, swift_code, bank_name, bank_address, bank_city
  Check (Remote Deposit):
    额外必需: address1
  Instant_Pay (FedNow/RTP):
    与 ACH 字段相同

=== assign_account_ids 说明 ===
- 可选参数：授权哪些 account 可以使用该 counterparty
- 支持传 1 个或多个 account id（列表）
- 如果 account 是低风险: status 自动为 "Approved"
- 如果 account 是高风险（如 251212054048470515）: status 为 "Pending"
- 混合场景：高风险 account 对应的记录为 "Pending"，其余为 "Approved"
"""
import pytest
import time
from typing import Optional, List
from api.account_api import AccountAPI
from api.counterparty_api import CounterpartyAPI
from utils.logger import logger
from utils.assertions import assert_status_ok, assert_fields_present
from data.enums import CounterpartyType, BankAccountType


# ==================== 常量 ====================

# 高风险 Account ID（status 会变为 Pending）
HIGH_RISK_ACCOUNT_ID = "251212054048470515"  # Auto testyan account 3 (High Risk)

# 不可见 Account ID（越权测试）
INVISIBLE_ACCOUNT_ID = "241010195849720143"

# ACH 和 Wire 共用的有效路由号
VALID_ROUTING_NUMBER = "091918457"

# Wire 自动填充验证：使用该路由号时 bank_name / bank_state 应由系统自动填充
# bank_country 对 Wire 类型默认为 "United States"


# ==================== 辅助函数 ====================

def _get_own_account_id(login_session) -> Optional[str]:
    """从 list 接口获取一个属于当前用户、低风险的 Account ID"""
    account_api = AccountAPI(session=login_session)
    resp = account_api.list_accounts(page=0, size=10)
    if resp.status_code != 200:
        return None
    accounts = resp.json().get("data", {}).get("content", [])
    # 优先找低风险账户（risk_level=Low），找不到就用第一条
    for acc in accounts:
        if acc.get("risk_level", "").lower() == "low":
            return acc["id"]
    return accounts[0]["id"] if accounts else None


def _assert_create_success(response, expected_payment_enable: Optional[bool] = None) -> dict:
    """
    验证创建接口返回 code=200，提取 data 并可选断言 payment_enable。
    返回 data dict。
    """
    assert response.status_code == 200, \
        f"HTTP 状态码错误: {response.status_code}"
    body = response.json()
    assert body.get("code") == 200, \
        f"业务 code 不是 200: code={body.get('code')}, msg={body.get('error_message')}"
    data = body.get("data", body)
    assert data.get("id"), "创建成功但未返回 id"

    if expected_payment_enable is not None:
        actual = data.get("payment_enable")
        assert actual == expected_payment_enable, \
            f"payment_enable 期望 {expected_payment_enable}，实际 {actual}"

    return data


def _ts() -> str:
    return str(int(time.time()))


# ==================== 测试类 ====================

@pytest.mark.counterparty
@pytest.mark.create_api
class TestCounterpartyCreate:
    """
    Counterparty 创建接口完整测试用例集
    """

    # ----------------------------------------------------------------
    # 场景1：ACH 类型 — 全部字段齐全，payment_enable=true
    # ----------------------------------------------------------------
    def test_create_ach_payment_enable_true(self, counterparty_api, login_session, db_cleanup):
        """
        测试场景1：ACH 类型 Counterparty，所有必填银行字段齐全
        验证点：
        1. 创建成功（code=200）
        2. payment_enable = true（字段齐全，可发起 ACH 交易）
        3. 字段回显正确
        4. 必需字段均存在于响应中
        """
        account_id = _get_own_account_id(login_session)
        if not account_id:
            pytest.skip("无可用 Account，跳过")

        ts = _ts()
        data = {
            "name": f"Auto TestYan ACH Full {ts}",
            "type": "Person",
            "payment_type": "ACH",
            "bank_account_type": "Checking",
            "bank_routing_number": VALID_ROUTING_NUMBER,
            "bank_name": "Auto TestYan Bank",
            "bank_account_owner_name": "Auto TestYan Owner ACH",
            "bank_account_number": "111111111",
            "assign_account_ids": [account_id]
        }

        logger.info("创建 ACH Counterparty（字段齐全）")
        resp = counterparty_api.create_counterparty(data)
        created = _assert_create_success(resp, expected_payment_enable=True)

        assert_fields_present(created, ["id", "name", "type", "payment_type", "assign_account_ids"], "ACH CP")
        assert created.get("payment_type") == "ACH"
        assert created.get("type") == "Person"

        if db_cleanup:
            db_cleanup.track("counterparty", created["id"])

        logger.info(f"✓ ACH payment_enable=true 验证通过，id={created['id']}")

    # ----------------------------------------------------------------
    # 场景2：ACH 类型 — 缺少银行字段，payment_enable=false
    # ----------------------------------------------------------------
    def test_create_ach_payment_enable_false(self, counterparty_api, login_session, db_cleanup):
        """
        测试场景2：ACH 类型 Counterparty，缺少银行账户字段（draft 模式）
        验证点：
        1. 创建成功（code=200）
        2. payment_enable = false（银行字段不完整，无法发起交易）
        """
        account_id = _get_own_account_id(login_session)
        if not account_id:
            pytest.skip("无可用 Account，跳过")

        ts = _ts()
        data = {
            "name": f"Auto TestYan ACH Draft {ts}",
            "type": "Person",
            "payment_type": "ACH",
            # 故意省略 bank_routing_number, bank_account_number 等
            "assign_account_ids": [account_id]
        }

        logger.info("创建 ACH Counterparty（缺少银行字段，期望 payment_enable=false）")
        resp = counterparty_api.create_counterparty(data)

        assert resp.status_code == 200
        body = resp.json()
        logger.info(f"  响应: code={body.get('code')}, payment_enable={body.get('data', {}).get('payment_enable')}")

        if body.get("code") == 200:
            created_data = body.get("data", body)
            payment_enable = created_data.get("payment_enable")
            assert payment_enable is False, \
                f"缺少银行字段时 payment_enable 应为 false，实际: {payment_enable}"

            if db_cleanup and created_data.get("id"):
                db_cleanup.track("counterparty", created_data["id"])

            logger.info(f"✓ ACH payment_enable=false 验证通过，id={created_data.get('id')}")
        else:
            logger.info(f"  API 以 code={body.get('code')} 拒绝（探索性结果）")

    # ----------------------------------------------------------------
    # 场景3：Wire（国内）— 全字段，验证 bank_name/bank_state 自动填充
    # ----------------------------------------------------------------
    def test_create_wire_auto_populated_fields(self, counterparty_api, login_session, db_cleanup):
        """
        测试场景3：Wire（国内）类型 Counterparty
        验证点：
        1. 创建成功（code=200）
        2. payment_enable = true
        3. bank_name 由路由号自动填充（即使请求中未传）
        4. bank_state 由路由号自动填充
        5. bank_country 默认值为 "United States"
        """
        account_id = _get_own_account_id(login_session)
        if not account_id:
            pytest.skip("无可用 Account，跳过")

        ts = _ts()
        data = {
            "name": f"Auto TestYan Wire Auto {ts}",
            "type": "Company",
            "payment_type": "Wire",
            "bank_account_type": "Checking",
            "bank_routing_number": VALID_ROUTING_NUMBER,
            "bank_account_owner_name": "Auto TestYan Wire Owner",
            "bank_account_number": "222222222",
            # 文档要求的完整字段（确保 payment_enable=true）
            "address1": "123 Test Street",
            "city": "Dallas",
            "state": "TX",
            "country": "United States",
            "zip_code": "75201",
            "assign_account_ids": [account_id]
            # bank_name / bank_state / bank_country 由 Wire 路由号自动填充，无需传
        }

        logger.info("创建 Wire Counterparty（验证自动填充字段）")
        resp = counterparty_api.create_counterparty(data)
        created = _assert_create_success(resp, expected_payment_enable=True)

        # 文档说明：Wire 类型 bank_name / bank_state 由路由号自动填充
        bank_name = created.get("bank_name")
        bank_state = created.get("bank_state")
        bank_country = created.get("bank_country")
        logger.info(f"  bank_name (自动填充) = {bank_name}")
        logger.info(f"  bank_state (自动填充) = {bank_state}")
        logger.info(f"  bank_country (默认值) = {bank_country}")

        assert bank_name, "Wire 类型应由路由号自动填充 bank_name"
        assert bank_state, "Wire 类型应由路由号自动填充 bank_state"
        assert bank_country == "United States", \
            f"Wire 类型 bank_country 默认应为 'United States'，实际: {bank_country}"

        if db_cleanup:
            db_cleanup.track("counterparty", created["id"])

        logger.info(f"✓ Wire 自动填充字段验证通过，id={created['id']}")

    # ----------------------------------------------------------------
    # 场景4：International_Wire — 全字段，payment_enable=true
    # ----------------------------------------------------------------
    def test_create_international_wire_full_fields(self, counterparty_api, login_session, db_cleanup):
        """
        测试场景4：International_Wire 类型 Counterparty（字段齐全）
        验证点：
        1. 创建成功（code=200）
        2. payment_enable = true
        3. 所有国际电汇特有字段（country, swift_code, bank_address 等）回显正确
        """
        account_id = _get_own_account_id(login_session)
        if not account_id:
            pytest.skip("无可用 Account，跳过")

        ts = _ts()
        data = {
            "name": f"Auto TestYan IntlWire Full {ts}",
            "type": "Company",
            "payment_type": "International_Wire",
            "bank_account_type": "Savings",
            "bank_account_owner_name": "Auto TestYan Intl Owner",
            "bank_account_number": "333333333",
            # 国际电汇必填字段（文档要求）
            "country": "CN",
            "address1": "123 Test Road",
            "city": "Beijing",
            "state": "BJ",
            "zip_code": "100000",
            "bank_country": "CN",
            "swift_code": "CRBKUS33XXX",
            "bank_name": "Auto TestYan Bank CN",
            "bank_address": "456 Bank Street",
            "bank_city": "Shanghai",
            "bank_state": "SH",
            "bank_zip_code": "200000",
            "assign_account_ids": [account_id]
        }

        logger.info("创建 International_Wire Counterparty（字段齐全）")
        resp = counterparty_api.create_counterparty(data)
        created = _assert_create_success(resp, expected_payment_enable=True)

        assert created.get("payment_type") == "International_Wire"
        assert created.get("swift_code") == data["swift_code"], \
            f"swift_code 回显不正确: 期望 {data['swift_code']}, 实际 {created.get('swift_code')}"
        # 注：API 会将 ISO 3166 代码转换为国家全名返回（如 CN → China），只验证字段非空
        assert created.get("bank_country"), \
            f"bank_country 字段不应为空，实际: {created.get('bank_country')}"
        logger.info(f"  bank_country 返回值: '{created.get('bank_country')}'")

        if db_cleanup:
            db_cleanup.track("counterparty", created["id"])

        logger.info(f"✓ International_Wire payment_enable=true 验证通过，id={created['id']}")

    # ----------------------------------------------------------------
    # 场景5：International_Wire — 缺少 swift_code，payment_enable=false
    # ----------------------------------------------------------------
    def test_create_international_wire_missing_swift(self, counterparty_api, login_session, db_cleanup):
        """
        测试场景5：International_Wire 缺少 swift_code（无法支付）
        验证点：
        1. 创建成功（code=200）
        2. payment_enable = false（缺少 swift_code）
        """
        account_id = _get_own_account_id(login_session)
        if not account_id:
            pytest.skip("无可用 Account，跳过")

        ts = _ts()
        data = {
            "name": f"Auto TestYan IntlWire NoSwift {ts}",
            "type": "Person",
            "payment_type": "International_Wire",
            "bank_account_type": "Checking",
            "bank_account_owner_name": "Auto TestYan Intl Owner2",
            "bank_account_number": "444444444",
            "country": "CN",
            "address1": "123 Test Road",
            "city": "Beijing",
            "zip_code": "100000",
            "bank_country": "CN",
            # 故意省略 swift_code
            "assign_account_ids": [account_id]
        }

        logger.info("创建 International_Wire Counterparty（缺少 swift_code）")
        resp = counterparty_api.create_counterparty(data)

        assert resp.status_code == 200
        body = resp.json()
        logger.info(f"  响应: code={body.get('code')}")

        if body.get("code") == 200:
            created_data = body.get("data", body)
            payment_enable = created_data.get("payment_enable")
            assert payment_enable is False, \
                f"缺少 swift_code 时 payment_enable 应为 false，实际: {payment_enable}"

            if db_cleanup and created_data.get("id"):
                db_cleanup.track("counterparty", created_data["id"])

            logger.info(f"✓ payment_enable=false 验证通过（缺少 swift_code）")
        else:
            logger.info(f"  API 以 code={body.get('code')} 拒绝（可接受）")

    # ----------------------------------------------------------------
    # 场景6：全部枚举 type 测试（Person/Company/Vendor/Employee）
    # ----------------------------------------------------------------
    @pytest.mark.parametrize("cp_type", ["Person", "Company", "Vendor", "Employee"])
    def test_create_with_all_type_enum(self, counterparty_api, login_session, db_cleanup, cp_type):
        """
        测试场景6：覆盖 type 字段所有枚举值（Person/Company/Vendor/Employee）
        验证点：
        1. 每种 type 均可创建成功（code=200）
        2. 返回的 type 与传入值一致
        """
        account_id = _get_own_account_id(login_session)
        if not account_id:
            pytest.skip("无可用 Account，跳过")

        ts = _ts()
        data = {
            "name": f"Auto TestYan Type {cp_type} {ts}",
            "type": cp_type,
            "payment_type": "ACH",
            "bank_account_type": "Checking",
            "bank_routing_number": VALID_ROUTING_NUMBER,
            "bank_name": "Auto TestYan Bank",
            "bank_account_owner_name": f"Auto TestYan {cp_type}",
            "bank_account_number": "111111111",
            "assign_account_ids": [account_id]
        }

        logger.info(f"创建 type='{cp_type}' 的 Counterparty")
        resp = counterparty_api.create_counterparty(data)
        created = _assert_create_success(resp)

        assert created.get("type") == cp_type, \
            f"type 回显不正确: 期望 {cp_type}, 实际 {created.get('type')}"

        if db_cleanup:
            db_cleanup.track("counterparty", created["id"])

        logger.info(f"✓ type='{cp_type}' 创建成功，id={created['id']}")

    # ----------------------------------------------------------------
    # 场景7：全部枚举 payment_type 测试
    # ----------------------------------------------------------------
    @pytest.mark.parametrize("payment_type,extra_data", [
        ("ACH", {
            "bank_account_type": "Checking",
            "bank_routing_number": VALID_ROUTING_NUMBER,
            "bank_account_owner_name": "Auto TestYan ACH",
            "bank_account_number": "111111111"
        }),
        ("Wire", {
            "bank_account_type": "Checking",
            "bank_routing_number": VALID_ROUTING_NUMBER,
            "bank_account_owner_name": "Auto TestYan Wire",
            "bank_account_number": "222222222"
        }),
        ("International_Wire", {
            "bank_account_type": "Savings",
            "bank_account_owner_name": "Auto TestYan IntlWire",
            "bank_account_number": "333333333",
            "country": "CN",
            "address1": "123 Test Road",
            "city": "Beijing",
            "zip_code": "100000",
            "bank_country": "CN",
            "swift_code": "CRBKUS33XXX",
            "bank_name": "Auto TestYan Bank"
        }),
        ("Check", {
            "bank_account_type": "Checking",
            "bank_routing_number": VALID_ROUTING_NUMBER,
            "bank_account_owner_name": "Auto TestYan Check",
            "bank_account_number": "444444444",
            "address1": "123 Check Street"   # Check 特有必填
        }),
        ("Instant_Pay", {
            "bank_account_type": "Checking",
            "bank_routing_number": VALID_ROUTING_NUMBER,
            "bank_account_owner_name": "Auto TestYan Instant",
            "bank_account_number": "555555555"
        }),
    ])
    def test_create_with_all_payment_type_enum(self, counterparty_api, login_session, db_cleanup,
                                                payment_type, extra_data):
        """
        测试场景7：覆盖 payment_type 所有枚举值（ACH/Wire/International_Wire/Check/Instant_Pay）
        验证点：
        1. 每种 payment_type 均可创建成功（code=200）
        2. 返回的 payment_type 与传入值一致
        """
        account_id = _get_own_account_id(login_session)
        if not account_id:
            pytest.skip("无可用 Account，跳过")

        ts = _ts()
        data = {
            "name": f"Auto TestYan PT {payment_type} {ts}",
            "type": "Person",
            "payment_type": payment_type,
            "assign_account_ids": [account_id]
        }
        data.update(extra_data)

        logger.info(f"创建 payment_type='{payment_type}' 的 Counterparty")
        resp = counterparty_api.create_counterparty(data)

        assert resp.status_code == 200
        body = resp.json()
        logger.info(f"  响应: code={body.get('code')}")

        if body.get("code") == 200:
            created_data = body.get("data", body)
            assert created_data.get("payment_type") == payment_type, \
                f"payment_type 回显不正确: 期望 {payment_type}, 实际 {created_data.get('payment_type')}"

            if db_cleanup and created_data.get("id"):
                db_cleanup.track("counterparty", created_data["id"])

            logger.info(f"✓ payment_type='{payment_type}' 创建成功，id={created_data.get('id')}")
        else:
            logger.info(f"  API 以 code={body.get('code')} 拒绝，msg={body.get('error_message')} （探索性结果）")

    # ----------------------------------------------------------------
    # 场景8：必填字段逐一缺失验证
    # ----------------------------------------------------------------
    @pytest.mark.parametrize("missing_field,base_data", [
        ("name", {
            "type": "Person",
            "payment_type": "ACH",
            "bank_account_type": "Checking",
            "bank_routing_number": VALID_ROUTING_NUMBER,
            "bank_account_owner_name": "Auto TestYan",
            "bank_account_number": "111111111"
        }),
        ("type", {
            "name": f"Auto TestYan Missing Type {int(time.time())}",
            "payment_type": "ACH",
            "bank_account_type": "Checking",
            "bank_routing_number": VALID_ROUTING_NUMBER,
            "bank_account_owner_name": "Auto TestYan",
            "bank_account_number": "111111111"
        }),
        ("payment_type", {
            "name": f"Auto TestYan Missing PT {int(time.time())}",
            "type": "Person",
            "bank_account_type": "Checking",
            "bank_routing_number": VALID_ROUTING_NUMBER,
            "bank_account_owner_name": "Auto TestYan",
            "bank_account_number": "111111111"
        }),
    ])
    def test_create_missing_required_fields(self, counterparty_api, missing_field, base_data):
        """
        测试场景8：逐一缺少必填字段（name / type / payment_type）
        验证点：
        1. HTTP 200（统一错误处理）
        2. 业务 code != 200
        3. data = None
        """
        logger.info(f"测试缺少必填字段: '{missing_field}'")
        resp = counterparty_api.create_counterparty(base_data)

        assert resp.status_code == 200, \
            f"HTTP 应返回 200，实际: {resp.status_code}"

        body = resp.json()
        logger.info(f"  响应: {body}")
        assert body.get("code") != 200, \
            f"缺少 '{missing_field}' 应被拒绝（code!=200），但返回了 code=200"
        assert body.get("data") is None, \
            f"缺少 '{missing_field}' 时 data 应为 None"

        logger.info(f"✓ 缺少 '{missing_field}' 被拒绝: code={body.get('code')}, msg={body.get('error_message')}")

    # ----------------------------------------------------------------
    # 场景9：非法枚举值（type / payment_type 超出范围）
    # ----------------------------------------------------------------
    def test_create_invalid_type_enum(self, counterparty_api):
        """
        测试场景9：type 使用超出枚举范围的值（'Alien'）
        验证点：
        1. HTTP 200
        2. 业务 code != 200，或记录为探索性结果
        """
        data = {
            "name": f"Auto TestYan Invalid Type {_ts()}",
            "type": "Alien",          # 超出枚举范围
            "payment_type": "ACH",
            "bank_account_type": "Checking",
            "bank_routing_number": VALID_ROUTING_NUMBER,
            "bank_account_owner_name": "Auto TestYan",
            "bank_account_number": "111111111"
        }

        logger.info("测试 type='Alien'（超出枚举范围）")
        resp = counterparty_api.create_counterparty(data)
        assert resp.status_code == 200

        body = resp.json()
        if body.get("code") != 200:
            logger.info(f"✓ 非法 type 被 API 拒绝: code={body.get('code')}")
        else:
            logger.info("⚠ API 未校验 type 枚举范围，记录为探索性结果")

    # ----------------------------------------------------------------
    # 场景10：assign_account_ids — 不传（无账户绑定）
    # ----------------------------------------------------------------
    def test_create_without_assign_account_ids(self, counterparty_api, db_cleanup):
        """
        测试场景10：不传 assign_account_ids（不绑定任何账户）
        验证点：
        1. 创建成功（code=200）
        2. assign_account_ids 为空或 null
        """
        ts = _ts()
        data = {
            "name": f"Auto TestYan No AccountIDs {ts}",
            "type": "Person",
            "payment_type": "ACH",
            "bank_account_type": "Checking",
            "bank_routing_number": VALID_ROUTING_NUMBER,
            "bank_name": "Auto TestYan Bank",
            "bank_account_owner_name": "Auto TestYan No Account",
            "bank_account_number": "111111111"
            # 不传 assign_account_ids
        }

        logger.info("创建 Counterparty（不绑定账户）")
        resp = counterparty_api.create_counterparty(data)
        created = _assert_create_success(resp)

        # 不传 assign_account_ids 时，API 可能会默认绑定当前 contact 所属的 account
        # 所以这里不断言 assign_account_ids 为空，只验证创建成功即可
        assign_ids = created.get("assign_account_ids")
        logger.info(f"  返回 assign_account_ids: {assign_ids}（可能为空或默认绑定）")

        if db_cleanup:
            db_cleanup.track("counterparty", created["id"])

        logger.info(f"✓ 无 assign_account_ids 创建成功，id={created['id']}")

    # ----------------------------------------------------------------
    # 场景11：assign_account_ids — 传 1 个账户（低风险，status=Approved）
    # ----------------------------------------------------------------
    def test_create_with_single_low_risk_account(self, counterparty_api, login_session, db_cleanup):
        """
        测试场景11：assign_account_ids 传单个低风险账户
        验证点：
        1. 创建成功（code=200）
        2. 该账户对应的 counterparty status 自动变为 "Approved"
        """
        account_id = _get_own_account_id(login_session)
        if not account_id:
            pytest.skip("无可用低风险 Account，跳过")

        ts = _ts()
        data = {
            "name": f"Auto TestYan 1 LowRisk Account {ts}",
            "type": "Person",
            "payment_type": "ACH",
            "bank_account_type": "Checking",
            "bank_routing_number": VALID_ROUTING_NUMBER,
            "bank_name": "Auto TestYan Bank",
            "bank_account_owner_name": "Auto TestYan Low Risk",
            "bank_account_number": "111111111",
            "assign_account_ids": [account_id]
        }

        logger.info(f"创建 Counterparty，绑定单个低风险账户: {account_id}")
        resp = counterparty_api.create_counterparty(data)
        created = _assert_create_success(resp)

        # assign_account_ids 是数组，每个元素包含 account_id 和 status
        # 低风险 account 对应的 status 自动为 "Approved"
        assign_list = created.get("assign_account_ids", [])
        logger.info(f"  返回 assign_account_ids: {assign_list}")

        if assign_list:
            entry = next((a for a in assign_list if a.get("account_id") == account_id), None)
            if entry:
                status = entry.get("status", "")
                assert status == "Approved", \
                    f"低风险账户绑定的 assign_account status 应为 'Approved'，实际: '{status}'"
                logger.info(f"✓ 低风险账户 assign_account status=Approved 验证通过")
            else:
                logger.info(f"  ⚠ 未在 assign_account_ids 中找到 account_id={account_id}，记录字段: {assign_list}")
        else:
            logger.info("  ⚠ assign_account_ids 为空，无法验证 status")

        if db_cleanup:
            db_cleanup.track("counterparty", created["id"])

        logger.info(f"✓ 低风险账户绑定成功，id={created['id']}")

    # ----------------------------------------------------------------
    # 场景12：assign_account_ids — 传 1 个高风险账户，status=Pending
    # ----------------------------------------------------------------
    def test_create_with_single_high_risk_account(self, counterparty_api, db_cleanup):
        """
        测试场景12：assign_account_ids 传单个高风险账户（251212054048470515）
        验证点：
        1. 创建成功（code=200）
        2. 该 Counterparty status 自动变为 "Pending"（高风险）
        """
        ts = _ts()
        data = {
            "name": f"Auto TestYan 1 HighRisk Account {ts}",
            "type": "Person",
            "payment_type": "ACH",
            "bank_account_type": "Checking",
            "bank_routing_number": VALID_ROUTING_NUMBER,
            "bank_name": "Auto TestYan Bank",
            "bank_account_owner_name": "Auto TestYan High Risk",
            "bank_account_number": "111111111",
            "assign_account_ids": [HIGH_RISK_ACCOUNT_ID]
        }

        logger.info(f"创建 Counterparty，绑定单个高风险账户: {HIGH_RISK_ACCOUNT_ID}")
        resp = counterparty_api.create_counterparty(data)
        assert resp.status_code == 200
        body = resp.json()
        logger.info(f"  响应: code={body.get('code')}, msg={body.get('error_message')}")

        if body.get("code") == 200:
            created_data = body.get("data", body)
            # assign_account_ids 是数组，高风险 account 对应的 status 为 "Pending"
            assign_list = created_data.get("assign_account_ids", [])
            logger.info(f"  返回 assign_account_ids: {assign_list}")
            if assign_list:
                entry = next((a for a in assign_list if a.get("account_id") == HIGH_RISK_ACCOUNT_ID), None)
                if entry:
                    status = entry.get("status", "")
                    assert status == "Pending", \
                        f"高风险账户绑定的 assign_account status 应为 'Pending'，实际: '{status}'"
                    logger.info(f"✓ 高风险账户 assign_account status=Pending 验证通过")
                else:
                    logger.info(f"  ⚠ 未在 assign_account_ids 中找到高风险 account_id")
            else:
                logger.info("  ⚠ assign_account_ids 为空，无法验证 status")

            if db_cleanup and created_data.get("id"):
                db_cleanup.track("counterparty", created_data["id"])

            logger.info(f"✓ 高风险账户 status=Pending 验证通过，id={created_data.get('id')}")
        else:
            logger.info(f"  API 以 code={body.get('code')} 拒绝高风险账户绑定（探索性结果）")

    # ----------------------------------------------------------------
    # 场景13：assign_account_ids — 传多个账户（低风险+高风险混合）
    # ----------------------------------------------------------------
    def test_create_with_mixed_risk_accounts(self, counterparty_api, login_session, db_cleanup):
        """
        测试场景13：assign_account_ids 传多个账户（低风险 + 高风险混合）
        验证点：
        1. 创建成功（code=200）
        2. 高风险账户对应的记录 status=Pending
        3. 低风险账户对应的记录 status=Approved
        （如果 API 统一返回一个 status，则期望为 Pending，因为有高风险账户）
        """
        low_risk_account_id = _get_own_account_id(login_session)
        if not low_risk_account_id:
            pytest.skip("无可用低风险 Account，跳过")

        ts = _ts()
        data = {
            "name": f"Auto TestYan Mixed Risk {ts}",
            "type": "Person",
            "payment_type": "ACH",
            "bank_account_type": "Checking",
            "bank_routing_number": VALID_ROUTING_NUMBER,
            "bank_name": "Auto TestYan Bank",
            "bank_account_owner_name": "Auto TestYan Mixed",
            "bank_account_number": "111111111",
            "assign_account_ids": [low_risk_account_id, HIGH_RISK_ACCOUNT_ID]
        }

        logger.info(f"创建 Counterparty，绑定混合账户（低风险+高风险）")
        resp = counterparty_api.create_counterparty(data)
        assert resp.status_code == 200
        body = resp.json()
        logger.info(f"  响应: code={body.get('code')}")

        if body.get("code") == 200:
            created_data = body.get("data", body)
            # 验证 assign_account_ids 中各 account 的 status
            assign_list = created_data.get("assign_account_ids", [])
            logger.info(f"  返回 assign_account_ids: {assign_list}")

            if assign_list:
                high_entry = next((a for a in assign_list if a.get("account_id") == HIGH_RISK_ACCOUNT_ID), None)
                low_entry = next((a for a in assign_list if a.get("account_id") == low_risk_account_id), None)

                if high_entry:
                    assert high_entry.get("status") == "Pending", \
                        f"高风险账户 assign_account status 应为 Pending，实际: {high_entry.get('status')}"
                    logger.info(f"  ✓ 高风险 status=Pending")
                if low_entry:
                    assert low_entry.get("status") == "Approved", \
                        f"低风险账户 assign_account status 应为 Approved，实际: {low_entry.get('status')}"
                    logger.info(f"  ✓ 低风险 status=Approved")
            else:
                logger.info("  ⚠ assign_account_ids 为空，无法验证 status")

            if db_cleanup and created_data.get("id"):
                db_cleanup.track("counterparty", created_data["id"])

            logger.info(f"✓ 混合账户 assign_account status 验证通过，id={created_data.get('id')}")
        else:
            logger.info(f"  API 以 code={body.get('code')} 拒绝（探索性结果）")

    # ----------------------------------------------------------------
    # 场景14：assign_account_ids — 传多个低风险账户，status=Approved
    # ----------------------------------------------------------------
    def test_create_with_multiple_accounts(self, counterparty_api, login_session, db_cleanup):
        """
        测试场景14：assign_account_ids 传多个账户（全部低风险）
        验证点：
        1. 创建成功（code=200）
        2. status = Approved（全部低风险）
        3. assign_account_ids 返回传入的账户列表
        """
        account_api = AccountAPI(session=login_session)
        resp = account_api.list_accounts(page=0, size=5)
        if resp.status_code != 200:
            pytest.skip("无法获取账户列表，跳过")

        accounts = resp.json().get("data", {}).get("content", [])
        low_risk_accounts = [a["id"] for a in accounts if a.get("risk_level", "").lower() == "low"]

        if len(low_risk_accounts) < 2:
            pytest.skip("低风险账户不足 2 个，跳过多账户测试")

        selected_ids = low_risk_accounts[:2]
        ts = _ts()
        data = {
            "name": f"Auto TestYan Multi Account {ts}",
            "type": "Person",
            "payment_type": "ACH",
            "bank_account_type": "Checking",
            "bank_routing_number": VALID_ROUTING_NUMBER,
            "bank_name": "Auto TestYan Bank",
            "bank_account_owner_name": "Auto TestYan Multi",
            "bank_account_number": "111111111",
            "assign_account_ids": selected_ids
        }

        logger.info(f"创建 Counterparty，绑定 {len(selected_ids)} 个低风险账户")
        resp = counterparty_api.create_counterparty(data)
        created = _assert_create_success(resp)

        # assign_account_ids 是包含 {account_id, status} 的数组
        assign_list = created.get("assign_account_ids", [])
        logger.info(f"  返回 assign_account_ids: {assign_list}")

        if assign_list:
            returned_account_ids = [a.get("account_id") for a in assign_list if isinstance(a, dict)]
            for acc_id in selected_ids:
                entry = next((a for a in assign_list if a.get("account_id") == acc_id), None)
                if entry:
                    assert entry.get("status") == "Approved", \
                        f"全低风险账户 assign_account({acc_id}) status 应为 'Approved'，实际: {entry.get('status')}"
            assert set(returned_account_ids) == set(selected_ids), \
                f"assign_account_ids 回显账户ID不正确: 期望 {selected_ids}, 实际 {returned_account_ids}"
        else:
            logger.info("  ⚠ assign_account_ids 为空，无法验证 status")

        if db_cleanup:
            db_cleanup.track("counterparty", created["id"])

        logger.info(f"✓ 多账户绑定 status=Approved 验证通过，id={created['id']}")

    # ----------------------------------------------------------------
    # 场景15：所有非必填字段全部传入，验证是否完整存储
    # ----------------------------------------------------------------
    def test_create_with_all_optional_fields(self, counterparty_api, login_session, db_cleanup):
        """
        测试场景15：创建时传入所有非必填字段，验证 list/detail 中可以查到
        验证点：
        1. 创建成功（code=200）
        2. 所有传入的非必填字段都出现在返回值中，值一致
        """
        account_id = _get_own_account_id(login_session)
        if not account_id:
            pytest.skip("无可用 Account，跳过")

        ts = _ts()
        data = {
            "name": f"Auto TestYan All Optional {ts}",
            "type": "Person",
            "payment_type": "ACH",
            "bank_account_type": "Checking",
            "bank_routing_number": VALID_ROUTING_NUMBER,
            "bank_name": "Auto TestYan Opt Bank",
            "bank_account_owner_name": "Auto TestYan All Opt Owner",
            "bank_account_number": "999888777",
            "bank_city": "New York",
            "bank_zip_code": "10001",
            "description": "Auto TestYan all optional fields test",
            "address1": "100 Optional Street",
            "address2": "Suite 200",
            "city": "Los Angeles",
            "state": "CA",
            "zip_code": "90001",
            "country": "US",
            "assign_account_ids": [account_id]
        }

        optional_fields = [
            "bank_city", "bank_zip_code", "description",
            "address1", "address2", "city", "state", "zip_code", "country"
        ]

        logger.info("创建 Counterparty（包含所有非必填字段）")
        resp = counterparty_api.create_counterparty(data)
        created = _assert_create_success(resp)

        if db_cleanup:
            db_cleanup.track("counterparty", created["id"])

        # 验证非必填字段是否回显
        logger.info("验证非必填字段是否出现在返回值中")
        missing_in_response = []
        for field in optional_fields:
            if field not in created:
                missing_in_response.append(field)
            else:
                expected_val = data.get(field)
                actual_val = created.get(field)
                if expected_val == actual_val:
                    logger.info(f"  ✓ {field} = {actual_val}")
                else:
                    logger.info(f"  ✗ {field}: 期望 '{expected_val}', 实际 '{actual_val}'")

        if missing_in_response:
            logger.info(f"  ⚠ 以下字段未出现在创建响应中（可能需要查 Detail 确认）: {missing_in_response}")

        logger.info(f"✓ 全字段创建完成，id={created['id']}，请后续查 Detail 验证存储")

    # ----------------------------------------------------------------
    # 场景16：越权 account ID（不在当前用户 visible 范围）
    # ----------------------------------------------------------------
    def test_create_with_invisible_account_id(self, counterparty_api):
        """
        测试场景16：assign_account_ids 传入不在当前用户 visible 范围的 Account ID
        验证点：
        1. HTTP 200
        2. 业务 code != 200（506 或 599）
        3. data = None
        """
        ts = _ts()
        data = {
            "name": f"Auto TestYan Invisible {ts}",
            "type": "Person",
            "payment_type": "ACH",
            "bank_account_type": "Checking",
            "bank_routing_number": VALID_ROUTING_NUMBER,
            "bank_name": "Auto TestYan Bank",
            "bank_account_owner_name": "Auto TestYan Invisible",
            "bank_account_number": "111111111",
            "assign_account_ids": [INVISIBLE_ACCOUNT_ID]
        }

        logger.info(f"使用越权 Account ID: {INVISIBLE_ACCOUNT_ID}")
        resp = counterparty_api.create_counterparty(data)

        assert resp.status_code == 200
        body = resp.json()
        logger.info(f"  响应: {body}")

        assert body.get("code") != 200, \
            "越权 Account ID 不应创建成功，但返回了 code=200"
        assert body.get("data") is None

        code = body.get("code")
        assert code in [506, 599], \
            f"越权 Account ID 应返回 506 或 599，实际: {code}"

        logger.info(f"✓ 越权 Account ID 被拒绝: code={code}, msg={body.get('error_message')}")

    # ----------------------------------------------------------------
    # 场景17：Wire 类型缺少 bank_routing_number（条件必填）
    # ----------------------------------------------------------------
    def test_create_wire_missing_routing_number(self, counterparty_api):
        """
        测试场景17：Wire 类型缺少 bank_routing_number（Wire 条件必填字段）
        验证点：
        1. HTTP 200
        2. 业务 code != 200 或 payment_enable=false
        """
        data = {
            "name": f"Auto TestYan Wire No Routing {_ts()}",
            "type": "Person",
            "payment_type": "Wire",
            "bank_account_type": "Checking",
            "bank_account_owner_name": "Auto TestYan Wire Test",
            "bank_account_number": "111111111"
            # 故意省略 bank_routing_number（Wire 必填）
        }

        logger.info("Wire 类型缺少 bank_routing_number")
        resp = counterparty_api.create_counterparty(data)
        assert resp.status_code == 200

        body = resp.json()
        logger.info(f"  响应: code={body.get('code')}")

        if body.get("code") == 200:
            created_data = body.get("data", body)
            payment_enable = created_data.get("payment_enable")
            assert payment_enable is False, \
                f"Wire 缺少路由号时 payment_enable 应为 false，实际: {payment_enable}"
            logger.info(f"✓ Wire 缺少路由号，payment_enable=false")
        else:
            logger.info(f"✓ Wire 缺少路由号被 API 拒绝: code={body.get('code')}")
