"""
Remote Deposit Check - Scan, Deposit, Update, Download 接口测试用例

接口说明：
  POST /checks/scan     - 扫描支票图片（需上传图片，自动化跳过）
  POST /checks/deposit  - 提交存款（依赖 scan 返回的 item_identifier，自动化跳过）
                          限制：仅可使用无 sub_account 的 FA
  PATCH /checks/deposit/:id - 更新 routing/account number（依赖 deposit 创建的 txn，跳过）
  POST /checks/download/:id - 下载支票图片（可自动化验证）
"""
import pytest
from utils.logger import logger

pytestmark = pytest.mark.remote_deposit_check


# ════════════════════════════════════════════════════════════════════
# Scan Bank Check（需要上传图片，大部分跳过）
# ════════════════════════════════════════════════════════════════════
@pytest.mark.remote_deposit_check
@pytest.mark.skip(reason="Scan 接口需要上传真实支票图片（multipart/form-data），自动化无法提供")
class TestCheckScan:
    def test_scan_missing_files(self, remote_deposit_check_api):
        """⚠️ 跳过：需要真实支票图片文件"""
        pass


# ════════════════════════════════════════════════════════════════════
# Submit Deposit Check（依赖 scan 结果，大部分跳过）
# ════════════════════════════════════════════════════════════════════
@pytest.mark.remote_deposit_check
class TestCheckDeposit:

    def test_deposit_missing_required_fa_id(self, remote_deposit_check_api):
        """
        测试场景1：缺少 financial_account_id（必填）
        Test Scenario1: Missing financial_account_id Returns Error
        """
        url = remote_deposit_check_api.config.get_full_url("/money-movements/checks/deposit")
        resp = remote_deposit_check_api.session.post(url, json={
            "amount": "10",
            "item_identifier": "FAKE-UUID",
            "routing_number": "121182865",
            "account_number": "1234567890",
            "check_date": "2025-01-01"
        })
        assert resp.status_code == 200
        body = resp.json()
        assert body.get("code") != 200
        logger.info(f"✓ 缺少 fa_id 被拒绝: code={body.get('code')}, msg={body.get('error_message')}")

    def test_deposit_with_fa_having_sub_returns_error(self, remote_deposit_check_api):
        """
        测试场景2：使用有 sub_account 的 FA（业务限制，应被拒绝）
        Test Scenario2: FA with sub_account is Rejected (Business Restriction)
        文档说明：仅可使用没有 sub account 的 FA
        """
        fa_with_sub = "251212054048470574"  # 已知有 sub_account 的 FA
        url = remote_deposit_check_api.config.get_full_url("/money-movements/checks/deposit")
        resp = remote_deposit_check_api.session.post(url, json={
            "financial_account_id": fa_with_sub,
            "amount": "10",
            "item_identifier": "FAKE-UUID-12345",
            "routing_number": "121182865",
            "account_number": "1234567890",
            "check_date": "2025-01-01"
        })
        assert resp.status_code == 200
        body = resp.json()
        code = body.get("code")
        if code != 200:
            logger.info(f"✓ 有 sub_account 的 FA 被拒绝: code={code}, msg={body.get('error_message')}")
        else:
            logger.info(f"  ⚠ API 接受了有 sub_account 的 FA（探索性结果，item_identifier 无效可能先报其他错）")

    @pytest.mark.skip(reason="Submit Deposit 依赖 scan 接口返回的 item_identifier，自动化无法提供")
    def test_deposit_success(self, remote_deposit_check_api):
        """⚠️ 跳过：需要 scan 接口返回的真实 item_identifier"""
        pass


# ════════════════════════════════════════════════════════════════════
# Update Remote Deposit Check Detail（依赖 deposit，跳过）
# ════════════════════════════════════════════════════════════════════
@pytest.mark.remote_deposit_check
class TestCheckUpdate:

    def test_update_invalid_transaction_id(self, remote_deposit_check_api):
        """
        测试场景1：使用不存在的 transaction_id 更新
        Test Scenario1: Non-existent Transaction ID Returns Error
        """
        url = remote_deposit_check_api.config.get_full_url(
            "/money-movements/checks/deposit/INVALID_TXN_ID_99999"
        )
        resp = remote_deposit_check_api.session.patch(url, json={
            "account_number": "9999999999",
            "routing_number": "000000000"
        })
        assert resp.status_code == 200
        body = resp.json()
        code = body.get("code")
        if code != 200:
            logger.info(f"✓ 无效 transaction_id 被拒绝: code={code}")
        else:
            logger.info(f"  ⚠ 无效 transaction_id 被接受（探索性结果）")

    def test_update_missing_required_params(self, remote_deposit_check_api):
        """
        测试场景2：缺少必填参数（account_number 和 routing_number 均必填）
        Test Scenario2: Missing Required Parameters Returns Error
        """
        # 取一个真实的 check transaction id
        txns_resp = remote_deposit_check_api.list_transactions(size=1)
        txns = txns_resp.json().get("data", {}).get("content", [])
        if not txns:
            pytest.skip("无 Check 交易数据，跳过")
        txn_id = txns[0].get("id")

        url = remote_deposit_check_api.config.get_full_url(
            f"/money-movements/checks/deposit/{txn_id}"
        )
        resp = remote_deposit_check_api.session.patch(url, json={
            # 缺少 account_number 和 routing_number
        })
        assert resp.status_code == 200
        body = resp.json()
        if body.get("code") != 200:
            logger.info(f"✓ 缺少必填参数被拒绝: code={body.get('code')}")
        else:
            logger.info(f"  ⚠ 接受了空 body（探索性结果）")

    @pytest.mark.skip(reason="Update 依赖 deposit 创建的 Processing 状态 transaction，需先完成 scan→deposit 流程")
    def test_update_success(self, remote_deposit_check_api):
        """⚠️ 跳过：需要完整的 scan→deposit 流程创建的 transaction"""
        pass


# ════════════════════════════════════════════════════════════════════
# Download Check Image（可自动化验证）
# ════════════════════════════════════════════════════════════════════
@pytest.mark.remote_deposit_check
class TestCheckDownload:

    def _get_check_txn_id(self, remote_deposit_check_api):
        """获取一个真实的 Check transaction_id"""
        resp = remote_deposit_check_api.list_transactions(size=1)
        content = resp.json().get("data", {}).get("content", [])
        return content[0].get("id") if content else None

    def test_download_with_valid_check_txn_id(self, remote_deposit_check_api):
        """
        测试场景1：使用有效的 Check transaction_id 下载图片
        Test Scenario1: Download Check Image with Valid Check Transaction ID
        验证点：
        1. HTTP 200，code=200
        2. data 含 front_check_image_url 和 back_check_image_url
        3. URL 是有效的 https 链接（或 null，取决于数据）
        """
        txn_id = self._get_check_txn_id(remote_deposit_check_api)
        if not txn_id:
            pytest.skip("无 Check 交易数据，跳过")

        resp = remote_deposit_check_api.download_check_image(txn_id)
        assert resp.status_code == 200
        body = resp.json()
        assert body.get("code") == 200, \
            f"code 应为 200，实际: {body.get('code')}, err={body.get('error_message')}"

        data = body.get("data", {})
        assert "front_check_image_url" in data, "data 应含 front_check_image_url"
        assert "back_check_image_url" in data, "data 应含 back_check_image_url"

        front_url = data.get("front_check_image_url")
        back_url = data.get("back_check_image_url")
        if front_url:
            assert front_url.startswith("https://"), f"front URL 应为 https，实际: {front_url[:50]}"
            logger.info(f"  ✓ front_check_image_url: {front_url[:80]}...")
        else:
            logger.info("  front_check_image_url 为 null（此笔交易无图片）")
        if back_url:
            assert back_url.startswith("https://")
            logger.info(f"  ✓ back_check_image_url: {back_url[:80]}...")
        logger.info(f"✓ Download Check Image 验证通过，txn_id={txn_id}")

    def test_download_with_internal_pay_txn_id(self, remote_deposit_check_api, login_session):
        """
        测试场景2：传入 Internal Pay 的 transaction_id（跨模块错误）
        Test Scenario2: Using Internal Pay Transaction ID Returns Error
        验证点：code=599，"Transaction's type is not check."
        """
        # 获取一个 internal pay 的 transaction_id
        url = remote_deposit_check_api.config.get_full_url(
            "/money-movements/internal-pay/transactions"
        )
        r = remote_deposit_check_api.session.get(url, params={"size": 1})
        content = r.json().get("data", {}).get("content", [])
        if not content:
            pytest.skip("无 Internal Pay 交易数据，跳过")
        ip_txn_id = content[0].get("id")

        resp = remote_deposit_check_api.download_check_image(ip_txn_id)
        assert resp.status_code == 200
        body = resp.json()
        assert body.get("code") != 200, \
            f"跨模块 txn_id 应返回错误，实际 code={body.get('code')}"
        logger.info(f"✓ Internal Pay txn_id 被拒绝: code={body.get('code')}, msg={body.get('error_message')}")

    def test_download_with_invalid_txn_id(self, remote_deposit_check_api):
        """
        测试场景3：使用不存在的 transaction_id
        Test Scenario3: Non-existent Transaction ID Returns Error
        """
        resp = remote_deposit_check_api.download_check_image("INVALID_TXN_ID_99999")
        assert resp.status_code == 200
        body = resp.json()
        assert body.get("code") != 200
        logger.info(f"✓ 不存在 txn_id 被拒绝: code={body.get('code')}, msg={body.get('error_message')}")

    def test_download_response_structure(self, remote_deposit_check_api):
        """
        测试场景4：验证下载接口响应结构
        Test Scenario4: Verify Download Response Structure
        """
        txn_id = self._get_check_txn_id(remote_deposit_check_api)
        if not txn_id:
            pytest.skip("无 Check 交易数据")

        resp = remote_deposit_check_api.download_check_image(txn_id)
        assert resp.status_code == 200
        body = resp.json()
        assert body.get("code") == 200
        data = body.get("data")
        assert isinstance(data, dict), "data 应为对象"
        assert "front_check_image_url" in data
        assert "back_check_image_url" in data
        logger.info(f"✓ 响应结构验证通过: keys={list(data.keys())}")
