"""
Remote Deposit Check - Financial Accounts 接口测试用例
GET /api/v1/cores/{core}/money-movements/checks/financial-accounts

响应结构：{"code": 200, "data": {"content": [...], "total_elements": N, ...}}
筛选参数：account_number, name（模糊）, sub_type（Checking/Saving）, account_ids
"""
import pytest
from utils.logger import logger

pytestmark = pytest.mark.remote_deposit_check


@pytest.mark.remote_deposit_check
class TestCheckFinancialAccounts:

    def _get_content(self, response):
        body = response.json()
        data = body.get("data", body) or {}
        return data.get("content", []) if isinstance(data, dict) else []

    def test_list_fa_success(self, remote_deposit_check_api):
        """
        测试场景1：成功获取可用 FA 列表
        Test Scenario1: Successfully List Available Financial Accounts
        验证点：
        1. HTTP 200，code=200
        2. data.content 是数组，total_elements > 0
        """
        resp = remote_deposit_check_api.list_financial_accounts(size=10)
        assert resp.status_code == 200
        body = resp.json()
        assert body.get("code") == 200

        data = body.get("data", {})
        content = data.get("content", [])
        total = data.get("total_elements", 0)
        assert total > 0
        logger.info(f"  total={total}, returned={len(content)}")
        if content:
            fa = content[0]
            for field in ["id", "name", "balance"]:
                if field in fa:
                    logger.info(f"  ✓ {field}: {fa.get(field)}")
        logger.info("✓ FA 列表获取成功")

    def test_filter_by_name_fuzzy(self, remote_deposit_check_api):
        """
        测试场景2：按 name 模糊搜索
        Test Scenario2: Filter FA by Name Fuzzy Search
        """
        base = self._get_content(remote_deposit_check_api.list_financial_accounts(size=1))
        if not base:
            pytest.skip("无 FA 数据")
        real_name = base[0].get("name", "")
        if not real_name:
            pytest.skip("name 字段为空")
        keyword = real_name[:4] if len(real_name) >= 4 else real_name
        resp = remote_deposit_check_api.list_financial_accounts(name=keyword, size=10)
        assert resp.status_code == 200
        assert resp.json().get("code") == 200
        filtered = self._get_content(resp)
        assert len(filtered) > 0
        for fa in filtered:
            assert keyword.lower() in (fa.get("name") or "").lower()
        logger.info(f"✓ name 模糊搜索通过，keyword='{keyword}'，返回 {len(filtered)} 条")

    @pytest.mark.parametrize("sub_type", ["Checking", "Saving"])
    def test_filter_by_sub_type(self, remote_deposit_check_api, sub_type):
        """
        测试场景3：按 sub_type 枚举筛选（Checking / Saving）
        Test Scenario3: Filter FA by sub_type Enum
        """
        resp = remote_deposit_check_api.list_financial_accounts(sub_type=sub_type, size=10)
        assert resp.status_code == 200
        assert resp.json().get("code") == 200
        content = self._get_content(resp)
        if content:
            for fa in content:
                if fa.get("sub_type"):
                    assert fa["sub_type"] == sub_type
        logger.info(f"✓ sub_type='{sub_type}' 筛选通过，返回 {len(content)} 条")

    def test_filter_by_account_number(self, remote_deposit_check_api):
        """
        测试场景4：按 account_number 筛选
        Test Scenario4: Filter FA by Account Number
        """
        base = self._get_content(remote_deposit_check_api.list_financial_accounts(size=1))
        if not base:
            pytest.skip("无 FA 数据")
        real_num = base[0].get("account_number")
        if not real_num:
            pytest.skip("account_number 为空")
        resp = remote_deposit_check_api.list_financial_accounts(account_number=real_num, size=5)
        assert resp.status_code == 200
        assert resp.json().get("code") == 200
        filtered = self._get_content(resp)
        assert len(filtered) > 0
        logger.info(f"✓ account_number 筛选通过，返回 {len(filtered)} 条")

    def test_pagination(self, remote_deposit_check_api):
        """
        测试场景5：分页验证
        Test Scenario5: Pagination Verification
        """
        resp = remote_deposit_check_api.list_financial_accounts(page=0, size=2)
        assert resp.status_code == 200
        data = resp.json().get("data", {})
        content = data.get("content", [])
        assert len(content) <= 2
        assert data.get("size") == 2
        logger.info(f"✓ 分页验证通过: size=2, returned={len(content)}")

    def test_nonexistent_name_returns_empty(self, remote_deposit_check_api):
        """
        测试场景6：搜索不存在的 name，返回空列表
        Test Scenario6: Non-existent Name Returns Empty List
        """
        resp = remote_deposit_check_api.list_financial_accounts(
            name="XYZXYZ_NOT_EXISTS_99999", size=5
        )
        assert resp.status_code == 200
        assert resp.json().get("code") == 200
        content = self._get_content(resp)
        assert len(content) == 0
        logger.info("✓ 不存在的 name 返回空列表")
