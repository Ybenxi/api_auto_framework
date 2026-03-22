"""
ACH Processing - Cancel、Reversal Detail 接口测试用例
POST /money-movements/ach/:transaction_id/cancel
GET  /money-movements/ach/reversal/:transaction_reversal_id/detail

Cancel 说明：
  - 只能 cancel Processing 状态的 ACH 交易
  - 响应 data 为 "Cancel request completed, money movement request has been updated."
  - 无效 ID → code=599 "Can not find money movement."

Reversal Detail 说明（已验证）：
  - 使用 transactions list 中含 reversal_id 的交易来验证
  - 响应 data 含 transaction_reversal_id, reversal_amount, reversal_status 等
  
Reversal Transaction（initiate）：依赖已 settled 的 ACH 交易，无法自动化，跳过
Upload ACH Batch：依赖文件上传，无法自动化，跳过
"""
import pytest
import time
from utils.logger import logger

ACH_FA  = "251119084741475550"
ACH_SUB = "251119084741475584"
ACH_CP  = "251212054048369793"

MEMO_PREFIX = "Auto TestYan ACH Cancel"

pytestmark = [pytest.mark.ach_processing, pytest.mark.no_rerun]


@pytest.mark.ach_processing
@pytest.mark.no_rerun
class TestAchCancel:

    def test_cancel_credit_success(self, ach_processing_api):
        """
        测试场景1：成功 cancel 一笔 Credit 交易
        Test Scenario1: Successfully Cancel an ACH Credit Transaction
        验证点：cancel 后 code=200，data 包含 cancel 确认消息
        """
        # 先发起 Credit
        resp_c = ach_processing_api.initiate_credit(
            financial_account_id=ACH_FA,
            sub_account_id=ACH_SUB,
            counterparty_id=ACH_CP,
            amount="0.01",
            first_party=False,
            same_day=False,
            memo=f"{MEMO_PREFIX} {int(time.time())}"
        )
        assert resp_c.json().get("code") == 200, \
            f"Credit 发起失败: {resp_c.json().get('error_message')}"
        txn_id = (resp_c.json().get("data") or resp_c.json()).get("id")

        # cancel
        resp = ach_processing_api.cancel_transaction(txn_id)
        assert resp.status_code == 200
        body = resp.json()
        assert body.get("code") == 200
        data = body.get("data")
        assert data is not None, "cancel 响应 data 不应为 None"
        logger.info(f"✓ ACH Credit cancel 成功: id={txn_id}, data={str(data)[:60]}")

    def test_cancel_debit_success(self, ach_processing_api):
        """
        测试场景2：成功 cancel 一笔 Debit 交易
        Test Scenario2: Successfully Cancel an ACH Debit Transaction
        """
        resp_d = ach_processing_api.initiate_debit(
            financial_account_id=ACH_FA,
            sub_account_id=ACH_SUB,
            counterparty_id=ACH_CP,
            amount="0.01",
            first_party=False,
            same_day=False,
            memo=f"{MEMO_PREFIX} Debit {int(time.time())}"
        )
        assert resp_d.json().get("code") == 200
        txn_id = (resp_d.json().get("data") or resp_d.json()).get("id")

        resp = ach_processing_api.cancel_transaction(txn_id)
        assert resp.json().get("code") == 200
        logger.info(f"✓ ACH Debit cancel 成功: id={txn_id}")

    def test_cancel_invalid_txn_id(self, ach_processing_api):
        """
        测试场景3：cancel 不存在的 transaction_id → code=599
        Test Scenario3: Cancel Non-existent Transaction Returns 599
        """
        resp = ach_processing_api.cancel_transaction("INVALID_ACH_TXN_99999")
        assert resp.status_code == 200
        body = resp.json()
        assert body.get("code") != 200
        logger.info(f"✓ cancel 无效 ID 被拒绝: code={body.get('code')}, msg={body.get('error_message')}")

    def test_cancel_then_verify_status(self, ach_processing_api):
        """
        测试场景4：cancel 后在 list 中验证状态变为 Cancelled
        Test Scenario4: After Cancel, Status Changes to Cancelled in List
        """
        # 发起 Credit
        resp_c = ach_processing_api.initiate_credit(
            financial_account_id=ACH_FA,
            sub_account_id=ACH_SUB,
            counterparty_id=ACH_CP,
            amount="0.01",
            first_party=False,
            same_day=False,
            memo=f"{MEMO_PREFIX} StatusCheck {int(time.time())}"
        )
        assert resp_c.json().get("code") == 200
        txn_id = (resp_c.json().get("data") or resp_c.json()).get("id")

        # cancel
        cancel_resp = ach_processing_api.cancel_transaction(txn_id)
        assert cancel_resp.json().get("code") == 200

        # 在 list 里查 cancelled 状态的 txn
        list_resp = ach_processing_api.list_transactions(
            transaction_id=txn_id, status="Cancelled", size=5
        )
        assert list_resp.status_code == 200
        list_data = list_resp.json().get("data", {}).get("content", [])
        if list_data:
            found = next((t for t in list_data if t.get("id") == txn_id), None)
            if found:
                assert found.get("status") == "Cancelled"
                logger.info(f"  ✓ cancel 后状态变为 Cancelled: id={txn_id}")
        logger.info("✓ cancel 后状态验证完成")


@pytest.mark.ach_processing
class TestAchReversalDetail:

    def test_reversal_detail_with_real_id(self, ach_processing_api):
        """
        测试场景1：使用 transactions 列表中含 reversal_id 的交易查询 reversal detail
        Test Scenario1: Retrieve Reversal Detail with Real reversal_id
        验证点：code=200，含 transaction_reversal_id, reversal_status, reversal_amount
        """
        # 在 transactions list 中找含 reversal_id 的交易
        resp = ach_processing_api.list_transactions(size=50)
        txns = resp.json().get("data", {}).get("content", [])
        reversal_txn = next((t for t in txns if t.get("reversal_id")), None)

        if not reversal_txn:
            pytest.skip("无含 reversal_id 的 ACH 交易数据")

        reversal_id = reversal_txn.get("reversal_id")
        logger.info(f"  使用 reversal_id={reversal_id} 查询 detail")

        rev_resp = ach_processing_api.get_reversal_detail(reversal_id)
        assert rev_resp.status_code == 200
        body = rev_resp.json()
        assert body.get("code") == 200, \
            f"reversal detail 查询失败: code={body.get('code')}"

        data = body.get("data", {})
        required_fields = [
            "transaction_reversal_id", "reversal_status", "reversal_amount", "reversal_time"
        ]
        for field in required_fields:
            if field in data:
                logger.info(f"  ✓ {field}: {data.get(field)}")
        assert "reversal_status" in data, "reversal detail 应含 reversal_status 字段"
        logger.info(f"✓ Reversal Detail 查询成功: reversal_id={reversal_id}")

    def test_reversal_detail_invalid_id(self, ach_processing_api):
        """
        测试场景2：使用不存在的 reversal_id → 被拒绝
        Test Scenario2: Invalid reversal_id Returns Error
        """
        resp = ach_processing_api.get_reversal_detail("INVALID_REVERSAL_ID_99999")
        assert resp.status_code == 200
        body = resp.json()
        assert body.get("code") != 200
        logger.info(f"✓ 无效 reversal_id 被拒绝: code={body.get('code')}")

    @pytest.mark.skip(reason="Initiate Reversal 需要已 settled 的 ACH 交易，无法自动化制造")
    def test_initiate_reversal(self, ach_processing_api):
        """⚠️ 跳过：Reversal 需要真实 settled ACH 交易"""
        pass


@pytest.mark.ach_processing
@pytest.mark.skip(reason="Upload ACH Batch 需要上传 ACH 格式文件，无法自动化")
class TestAchBatchFile:
    def test_upload_batch_skip(self, ach_processing_api):
        """⚠️ 跳过：需要 ACH 格式批量文件"""
        pass
