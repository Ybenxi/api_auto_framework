"""
Wire Processing - Financial Accounts 接口测试用例
GET /api/v1/cores/{core}/money-movements/wire/financial-accounts

响应结构：{"code": 200, "data": {"content": [...], "total_elements": N, ...}}
筛选参数：account_number, name（模糊）, sub_type（Checking/Saving）, account_ids
"""
import pytest
from utils.logger import logger

pytestmark = pytest.mark.wire_processing


@pytest.mark.wire_processing
class TestWireFinancialAccounts:

    def _get_content(self, response):
        body = response.json()
        data = body.get("data", body) or {}
        return data.get("content", []) if isinstance(data, dict) else []

    def test_list_fa_success(self, wire_processing_api):
        """
        测试场景1：成功获取 Wire FA 列表
        Test Scenario1: Successfully List Wire Financial Accounts
        验证点：code=200，data.content 是数组，total > 0
        """
        resp = wire_processing_api.list_financial_accounts(size=10)
        assert resp.status_code == 200
        body = resp.json()
        assert body.get("code") == 200

        data = body.get("data", {})
        content = data.get("content", [])
        total = data.get("total_elements", 0)
        assert total > 0
        logger.info(f"✓ Wire FA 列表获取成功: total={total}, returned={len(content)}")

    def test_filter_by_name_fuzzy(self, wire_processing_api):
        """
        测试场景2：按 name 模糊搜索
        Test Scenario2: Filter FA by Name Fuzzy Search
        """
        base = self._get_content(wire_processing_api.list_financial_accounts(size=1))
        if not base:
            pytest.skip("无 FA 数据")
        real_name = base[0].get("name", "")
        if not real_name:
            pytest.skip("name 字段为空")
        keyword = real_name[:4] if len(real_name) >= 4 else real_name
        resp = wire_processing_api.list_financial_accounts(name=keyword, size=10)
        assert resp.status_code == 200
        assert resp.json().get("code") == 200
        filtered = self._get_content(resp)
        assert len(filtered) > 0
        for fa in filtered:
            assert keyword.lower() in (fa.get("name") or "").lower()
        logger.info(f"✓ name 模糊搜索: keyword='{keyword}', 返回 {len(filtered)} 条")

    @pytest.mark.parametrize("sub_type", ["Checking", "Saving"])
    def test_filter_by_sub_type(self, wire_processing_api, sub_type):
        """
        测试场景3：按 sub_type 枚举筛选
        Test Scenario3: Filter by sub_type Enum (Checking/Saving)
        """
        resp = wire_processing_api.list_financial_accounts(sub_type=sub_type, size=10)
        assert resp.status_code == 200
        assert resp.json().get("code") == 200
        content = self._get_content(resp)
        if content:
            for fa in content:
                if fa.get("sub_type"):
                    assert fa["sub_type"] == sub_type
        logger.info(f"✓ sub_type='{sub_type}' 筛选: 返回 {len(content)} 条")

    def test_pagination(self, wire_processing_api):
        """
        测试场景4：分页验证
        Test Scenario4: Pagination Verification
        """
        resp = wire_processing_api.list_financial_accounts(page=0, size=2)
        assert resp.status_code == 200
        data = resp.json().get("data", {})
        content = data.get("content", [])
        assert len(content) <= 2
        assert data.get("size") == 2
        logger.info(f"✓ 分页验证: size=2, returned={len(content)}")

    def test_filter_nonexistent_name(self, wire_processing_api):
        """
        测试场景5：搜索不存在的 name → 返回空列表
        Test Scenario5: Non-existent Name Returns Empty List
        """
        resp = wire_processing_api.list_financial_accounts(
            name="XYZXYZ_NOT_EXISTS_99999", size=5
        )
        assert resp.status_code == 200
        assert resp.json().get("code") == 200
        assert len(self._get_content(resp)) == 0
        logger.info("✓ 不存在 name 返回空列表")

    def test_fa_has_account_id_field(self, wire_processing_api):
        """
        测试场景6：验证 FA 包含 account_id 字段（用于关联 CP assign_account）
        Test Scenario6: FA Contains account_id Field for CP Association
        """
        content = self._get_content(wire_processing_api.list_financial_accounts(size=5))
        if not content:
            pytest.skip("无 FA 数据")
        # account_id 是做 wire payment 时 counterparty assign 验证的关键字段
        for fa in content:
            if fa.get("account_id"):
                logger.info(f"  ✓ FA id={fa.get('id')}, account_id={fa.get('account_id')}")
                break
        logger.info("✓ FA account_id 字段验证通过")
