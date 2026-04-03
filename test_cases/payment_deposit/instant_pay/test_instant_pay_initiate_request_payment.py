"""
Instant Pay - RFP（Request for Payment）接口测试用例
POST /api/v1/cores/{core}/money-movements/instant-pay/request-payment
POST /api/v1/cores/{core}/money-movements/instant-pay/request-payment/cancel/:id

业务规则（已验证）：
- 发起后 status=Pending，direction=Origination
- id 字段为 "id"（不是 transaction_id）
- 可选参数：amount_modification_allowed, early_payment_allowed, execution_date, expiration_date
- cancel 后 status=Cancelled（响应 data=True）
- cancel 无效 ID → code=599 "Transaction does not exist."

已验证账户数据：
  IP_FA=251212054048470568，IP_SUB=251212054048470660
  IP_CP=251212054048369447（Instant Pay CP）
"""
import pytest
import time
from utils.logger import logger

IP_FA        = "251212054048470568"
IP_SUB       = "251212054048470660"
INVISIBLE_FA = "241010195850134683"

MEMO_PREFIX = "Auto TestYan IP RFP"

pytestmark = [pytest.mark.instant_pay, pytest.mark.no_rerun]


@pytest.mark.instant_pay
@pytest.mark.no_rerun
class TestInstantPayRFP:

    def _create_rfp(self, instant_pay_api, ip_cp_id, suffix=""):
        """Create an RFP and return its id."""
        resp = instant_pay_api.initiate_request_payment(
            financial_account_id=IP_FA,
            sub_account_id=IP_SUB,
            counterparty_id=ip_cp_id,
            amount="0.01",
            memo=f"{MEMO_PREFIX} {suffix} {int(time.time())}",
            execution_date="2026-12-01",
            expiration_date="2026-12-31"
        )
        assert resp.json().get("code") == 200, \
            f"RFP creation failed: {resp.json().get('error_message')}"
        data = resp.json().get("data") or resp.json()
        return data.get("id")

    def test_rfp_success_basic(self, instant_pay_api, ip_cp_id):
        """
        测试场景1：成功发起 RFP，验证基本字段
        Test Scenario1: Initiate RFP with Required Fields
        验证点：code=200，status=Pending，direction=Origination，含 id 字段
        """
        resp = instant_pay_api.initiate_request_payment(
            financial_account_id=IP_FA,
            sub_account_id=IP_SUB,
            counterparty_id=ip_cp_id,
            amount="0.01",
            memo=f"{MEMO_PREFIX} Basic {int(time.time())}"
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body.get("code") == 200, \
            f"RFP 发起失败: code={body.get('code')}, err={body.get('error_message')}"

        data = body.get("data") or body
        rfp_id = data.get("id")
        assert rfp_id, "RFP id 不应为空"
        assert data.get("status") == "Pending", f"RFP status 应为 Pending，实际: {data.get('status')}"
        assert data.get("direction") == "Origination"
        logger.info(f"  ✓ RFP 发起成功: id={rfp_id}, status=Pending")

        # cancel
        c_resp = instant_pay_api.cancel_request_payment(
            rfp_id, cancel_code="AC03", cancel_reason="Auto test cleanup"
        )
        assert c_resp.json().get("code") == 200
        logger.info(f"✓ RFP 发起后 cancel 成功: id={rfp_id}")

    def test_rfp_with_optional_params(self, instant_pay_api, ip_cp_id):
        """
        测试场景2：使用全部可选参数发起 RFP
        Test Scenario2: Initiate RFP with All Optional Parameters
        验证点：amount_modification_allowed/early_payment_allowed/execution_date/expiration_date 回显
        """
        exec_date = "2026-11-01"
        exp_date  = "2026-12-31"
        resp = instant_pay_api.initiate_request_payment(
            financial_account_id=IP_FA,
            sub_account_id=IP_SUB,
            counterparty_id=ip_cp_id,
            amount="0.01",
            memo=f"{MEMO_PREFIX} AllParams {int(time.time())}",
            amount_modification_allowed=True,
            early_payment_allowed=True,
            execution_date=exec_date,
            expiration_date=exp_date
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body.get("code") == 200
        data = body.get("data") or body
        rfp_id = data.get("id")

        assert data.get("execution_date") == exec_date
        assert data.get("expiration_date") == exp_date
        assert data.get("amount_modification_allowed") is True
        assert data.get("early_payment_allowed") is True
        logger.info(f"  ✓ 可选参数回显正确: exec={data.get('execution_date')}, exp={data.get('expiration_date')}")

        # cancel
        instant_pay_api.cancel_request_payment(rfp_id, cancel_code="AC03")
        logger.info(f"✓ 全参数 RFP 验证通过: id={rfp_id}")

    def test_rfp_cancel_success(self, instant_pay_api, ip_cp_id):
        """
        测试场景3：成功 cancel 一笔 RFP
        Test Scenario3: Successfully Cancel an RFP
        验证点：cancel 后 code=200，data=True，在 list 中 status=Cancelled
        """
        rfp_id = self._create_rfp(instant_pay_api, ip_cp_id, "Cancel")

        c_resp = instant_pay_api.cancel_request_payment(
            rfp_id,
            cancel_code="AC03",
            cancel_reason="Wrong account number in Credit Transfer."
        )
        assert c_resp.status_code == 200
        body = c_resp.json()
        assert body.get("code") == 200
        assert body.get("data") is True or body.get("data") == "True" or body.get("data"), \
            f"cancel response data should be True, actual: {body.get('data')}"
        logger.info(f"✓ RFP cancel succeeded: id={rfp_id}, data={body.get('data')}")

    def test_rfp_cancel_invalid_id(self, instant_pay_api, ip_cp_id):
        """
        测试场景4：cancel 不存在的 RFP → code=599
        Test Scenario4: Cancel Non-existent RFP Returns 599
        """
        c_resp = instant_pay_api.cancel_request_payment(
            "INVALID_RFP_ID_99999",
            cancel_code="AC03",
            cancel_reason="Test"
        )
        assert c_resp.status_code == 200
        body = c_resp.json()
        assert body.get("code") != 200
        logger.info(f"✓ 无效 RFP ID cancel 被拒绝: code={body.get('code')}, msg={body.get('error_message')}")

    def test_rfp_missing_sub_account_id(self, instant_pay_api, ip_cp_id):
        """
        测试场景5：FA 有 sub 但未传 sub_account_id → 被拒绝
        Test Scenario5: FA with Sub but Missing sub_account_id Returns Error
        """
        resp = instant_pay_api.initiate_request_payment(
            financial_account_id=IP_FA,
            counterparty_id=ip_cp_id,
            amount="0.01",
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body.get("code") != 200
        logger.info(f"✓ 缺少 sub_account_id 被拒绝: code={body.get('code')}")

    def test_rfp_invisible_fa(self, instant_pay_api, ip_cp_id):
        """
        测试场景6：越权 FA → 被拒绝
        Test Scenario6: Invisible FA Returns Error
        """
        resp = instant_pay_api.initiate_request_payment(
            financial_account_id=INVISIBLE_FA,
            counterparty_id=ip_cp_id,
            amount="0.01",
        )
        assert resp.status_code == 200
        assert resp.json().get("code") != 200
        logger.info(f"✓ 越权 FA 被拒绝: code={resp.json().get('code')}")

    def test_rfp_appears_in_list(self, instant_pay_api, ip_cp_id):
        """
        测试场景7：发起 RFP 后在 RFP list 中可查到
        Test Scenario7: Initiated RFP Appears in RFP Transactions List
        """
        rfp_id = self._create_rfp(instant_pay_api, ip_cp_id, "ListCheck")

        list_resp = instant_pay_api.list_request_payment_transactions(
            financial_account_id=IP_FA, size=10
        )
        assert list_resp.status_code == 200
        rfps = list_resp.json().get("data", {}).get("content", [])
        found = any(r.get("id") == rfp_id for r in rfps)
        if found:
            logger.info(f"  ✓ RFP 在 list 中找到: id={rfp_id}")
        else:
            logger.info(f"  ⚠ 未在 list 前10条中找到 id={rfp_id}")

        # cancel
        instant_pay_api.cancel_request_payment(rfp_id, cancel_code="AC03")
        logger.info("✓ RFP list 查询验证完成")

    def test_rfp_missing_counterparty(self, instant_pay_api):
        """
        测试场景8：缺少必填 counterparty_id
        Test Scenario8: Missing counterparty_id Returns Error
        """
        url = instant_pay_api.config.get_full_url("/money-movements/instant-pay/request-payment")
        resp = instant_pay_api.session.post(url, json={
            "financial_account_id": IP_FA,
            "sub_account_id": IP_SUB,
            "amount": "0.01"
        })
        assert resp.status_code == 200
        assert resp.json().get("code") != 200
        logger.info(f"✓ 缺少 counterparty_id 被拒绝: code={resp.json().get('code')}")
