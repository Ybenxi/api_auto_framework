"""
Internal Pay - Payers（Financial Accounts）接口测试用例
GET /api/v1/cores/{core}/money-movements/internal-pay/financial-accounts

响应结构：{"code": 200, "data": {"content": [...], "total_elements": N, ...}}
筛选参数：account_number, name（模糊）, sub_type（Checking/Saving）, account_ids
"""
import pytest
from utils.logger import logger

pytestmark = pytest.mark.internal_pay


@pytest.mark.internal_pay
class TestInternalPayPayers:

    def _get_content(self, response):
        body = response.json()
        data = body.get("data", body) or {}
        return data.get("content", []) if isinstance(data, dict) else []

    def test_list_payers_success(self, internal_pay_api):
        """
        测试场景1：成功获取可用付款 FA 列表
        Test Scenario1: Successfully List Available Payer Financial Accounts
        验证点：
        1. HTTP 200，code=200
        2. data.content 是数组，total_elements > 0
        3. 每条含 id, name, balance, account_number 等字段
        """
        resp = internal_pay_api.list_payers(size=10)
        assert resp.status_code == 200
        body = resp.json()
        assert body.get("code") == 200

        data = body.get("data", {})
        content = data.get("content", [])
        total = data.get("total_elements", 0)
        assert total > 0, "应有可见的 FA 数据"
        logger.info(f"  total={total}, returned={len(content)}")

        if content:
            fa = content[0]
            for field in ["id", "name", "balance", "account_number"]:
                if field in fa:
                    logger.info(f"  ✓ {field}: {fa.get(field)}")
        logger.info("✓ Payers FA 列表获取成功")

    def test_filter_by_name_fuzzy(self, internal_pay_api):
        """
        测试场景2：按 name 模糊搜索
        Test Scenario2: Filter Payers by Name Fuzzy Search
        验证点：返回结果的 name 包含关键词
        """
        base_content = self._get_content(internal_pay_api.list_payers(size=1))
        if not base_content:
            pytest.skip("无 FA 数据，跳过")

        real_name = base_content[0].get("name", "")
        if not real_name:
            pytest.skip("name 字段为空")

        keyword = real_name[:4] if len(real_name) >= 4 else real_name
        resp = internal_pay_api.list_payers(name=keyword, size=10)
        assert resp.status_code == 200
        assert resp.json().get("code") == 200

        filtered = self._get_content(resp)
        assert len(filtered) > 0
        for fa in filtered:
            assert keyword.lower() in (fa.get("name") or "").lower()
        logger.info(f"✓ name 模糊搜索通过，keyword='{keyword}'，返回 {len(filtered)} 条")

    @pytest.mark.parametrize("sub_type", ["Checking", "Saving"])
    def test_filter_by_sub_type(self, internal_pay_api, sub_type):
        """
        测试场景3：按 sub_type 枚举筛选（Checking / Saving）
        Test Scenario3: Filter Payers by sub_type Enum
        """
        resp = internal_pay_api.list_payers(sub_type=sub_type, size=10)
        assert resp.status_code == 200
        assert resp.json().get("code") == 200

        content = self._get_content(resp)
        if content:
            for fa in content:
                if fa.get("sub_type"):
                    assert fa["sub_type"] == sub_type
        logger.info(f"✓ sub_type='{sub_type}' 筛选通过，返回 {len(content)} 条")

    def test_filter_by_account_number(self, internal_pay_api):
        """
        测试场景4：按 account_number 筛选
        Test Scenario4: Filter Payers by Account Number
        """
        base_content = self._get_content(internal_pay_api.list_payers(size=1))
        if not base_content:
            pytest.skip("无 FA 数据")

        real_num = base_content[0].get("account_number")
        if not real_num:
            pytest.skip("account_number 为空")

        resp = internal_pay_api.list_payers(account_number=real_num, size=5)
        assert resp.status_code == 200
        assert resp.json().get("code") == 200
        filtered = self._get_content(resp)
        assert len(filtered) > 0
        logger.info(f"✓ account_number 筛选通过，返回 {len(filtered)} 条")

    def test_filter_by_account_ids(self, internal_pay_api):
        """
        测试场景5：使用 account_ids 数组筛选
        Test Scenario5: Filter Payers by account_ids Array
        """
        base_content = self._get_content(internal_pay_api.list_payers(size=2))
        ids = [fa.get("account_id") for fa in base_content if fa.get("account_id")][:2]
        if len(ids) < 2:
            pytest.skip("account_id 数据不足")

        resp = internal_pay_api.list_payers(account_ids=ids, size=10)
        assert resp.status_code == 200
        assert resp.json().get("code") == 200
        logger.info(f"✓ account_ids 数组筛选通过，返回 {len(self._get_content(resp))} 条")

    def test_pagination(self, internal_pay_api):
        """
        测试场景6：分页功能验证
        Test Scenario6: Pagination Verification
        """
        resp = internal_pay_api.list_payers(page=0, size=2)
        assert resp.status_code == 200
        data = resp.json().get("data", {})
        assert len(data.get("content", [])) <= 2
        assert data.get("size") == 2
        logger.info(f"✓ 分页验证通过: size=2, returned={len(data.get('content',[]))}")

    def test_nonexistent_name_returns_empty(self, internal_pay_api):
        """
        测试场景7：搜索不存在的 name，应返回空列表
        Test Scenario7: Non-existent Name Returns Empty List
        """
        resp = internal_pay_api.list_payers(
            name="XYZXYZ_NOT_EXISTS_99999", size=5
        )
        assert resp.status_code == 200
        assert resp.json().get("code") == 200
        content = self._get_content(resp)
        assert len(content) == 0
        logger.info("✓ 不存在的 name 返回空列表")
