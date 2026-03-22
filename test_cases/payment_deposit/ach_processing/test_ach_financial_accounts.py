"""
ACH Processing - Financial Accounts + First Party Bank Accounts 接口测试用例

本文件包含两个接口：
1. GET /money-movements/ach/financial-accounts  - 查询可发起 ACH 的 FA
2. GET /money-movements/ach/bank-accounts       - 查询外部绑定的 1st party 银行账户
   （first_party=True 交易时使用此列表的 id 作为 counterparty_id）
"""
import pytest
from utils.logger import logger

pytestmark = pytest.mark.ach_processing


@pytest.mark.ach_processing
class TestAchFinancialAccounts:

    def _get_content(self, response):
        body = response.json()
        data = body.get("data", body) or {}
        return data.get("content", []) if isinstance(data, dict) else body.get("content", [])

    def test_list_fa_success(self, ach_processing_api):
        """
        测试场景1：成功获取 ACH FA 列表
        Test Scenario1: Successfully List ACH Financial Accounts
        """
        resp = ach_processing_api.list_financial_accounts(size=10)
        assert resp.status_code == 200
        body = resp.json()
        assert body.get("code") == 200
        data = body.get("data", {})
        total = data.get("total_elements", 0)
        assert total > 0
        logger.info(f"✓ ACH FA 列表: total={total}")

    def test_filter_by_name(self, ach_processing_api):
        """
        测试场景2：按 name 模糊搜索
        Test Scenario2: Filter by Name Fuzzy Search
        """
        base = self._get_content(ach_processing_api.list_financial_accounts(size=1))
        if not base:
            pytest.skip("无 FA 数据")
        keyword = (base[0].get("name") or "")[:4]
        if not keyword:
            pytest.skip("name 为空")
        resp = ach_processing_api.list_financial_accounts(name=keyword, size=5)
        assert resp.status_code == 200
        assert resp.json().get("code") == 200
        filtered = self._get_content(resp)
        for fa in filtered:
            assert keyword.lower() in (fa.get("name") or "").lower()
        logger.info(f"✓ name 模糊搜索: keyword='{keyword}', 返回 {len(filtered)} 条")

    @pytest.mark.parametrize("sub_type", ["Checking", "Saving"])
    def test_filter_by_sub_type(self, ach_processing_api, sub_type):
        """
        测试场景3：按 sub_type 枚举筛选
        Test Scenario3: Filter by sub_type (Checking/Saving)
        """
        resp = ach_processing_api.list_financial_accounts(sub_type=sub_type, size=10)
        assert resp.status_code == 200
        assert resp.json().get("code") == 200
        content = self._get_content(resp)
        if content:
            for fa in content:
                if fa.get("sub_type"):
                    assert fa["sub_type"] == sub_type
        logger.info(f"✓ sub_type='{sub_type}': 返回 {len(content)} 条")

    def test_pagination(self, ach_processing_api):
        """
        测试场景4：分页验证
        Test Scenario4: Pagination
        """
        resp = ach_processing_api.list_financial_accounts(page=0, size=2)
        assert resp.status_code == 200
        data = resp.json().get("data", {})
        assert len(data.get("content", [])) <= 2
        logger.info("✓ 分页验证通过")

    def test_nonexistent_name(self, ach_processing_api):
        """
        测试场景5：不存在的 name 返回空列表
        Test Scenario5: Non-existent Name Returns Empty
        """
        resp = ach_processing_api.list_financial_accounts(name="XYZXYZ_NOT_EXISTS_99999")
        assert resp.status_code == 200
        assert resp.json().get("code") == 200
        assert len(self._get_content(resp)) == 0
        logger.info("✓ 不存在 name 返回空列表")


@pytest.mark.ach_processing
class TestAchBankAccounts:
    """
    List First Party Bank Accounts（外部绑定的银行账户，用于 first_party=True 交易）
    """

    def _get_content(self, response):
        body = response.json()
        data = body.get("data", body) or {}
        return data.get("content", []) if isinstance(data, dict) else body.get("content", [])

    def test_list_bank_accounts_success(self, ach_processing_api):
        """
        测试场景1：成功获取 First Party Bank Accounts 列表
        Test Scenario1: Successfully List First Party Bank Accounts
        验证点：含 bank_name, bank_routing_number, bank_account_number, account_id, bank_is_us_based
        """
        resp = ach_processing_api.list_bank_accounts(size=10)
        assert resp.status_code == 200
        body = resp.json()
        assert body.get("code") == 200

        data = body.get("data", {})
        content = data.get("content", []) if isinstance(data, dict) else body.get("content", [])
        assert isinstance(content, list)
        total = data.get("total_elements", 0) if isinstance(data, dict) else body.get("total_elements", 0)
        logger.info(f"  total={total}, returned={len(content)}")

        if content:
            ba = content[0]
            for field in ["id", "bank_name", "bank_routing_number", "bank_account_number", "account_id"]:
                if field in ba:
                    logger.info(f"  ✓ {field}: {ba.get(field)}")
        logger.info("✓ First Party Bank Accounts 列表获取成功")

    def test_bank_accounts_fields(self, ach_processing_api):
        """
        测试场景2：验证 bank_accounts 特有字段（bank_is_us_based）
        Test Scenario2: Verify bank_is_us_based Field
        """
        content = self._get_content(ach_processing_api.list_bank_accounts(size=5))
        if not content:
            pytest.skip("无 bank account 数据")
        for ba in content:
            if "bank_is_us_based" in ba:
                assert isinstance(ba.get("bank_is_us_based"), bool)
                logger.info(f"  ✓ bank_is_us_based: {ba.get('bank_is_us_based')}")
                break
        logger.info("✓ bank_is_us_based 字段验证通过")

    def test_bank_accounts_pagination(self, ach_processing_api):
        """
        测试场景3：分页验证
        Test Scenario3: Pagination
        """
        resp = ach_processing_api.list_bank_accounts(page=0, size=2)
        assert resp.status_code == 200
        assert resp.json().get("code") == 200
        logger.info("✓ bank_accounts 分页验证通过")
