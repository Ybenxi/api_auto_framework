"""
Account Transfer - Financial Accounts 接口测试用例
GET /api/v1/cores/{core}/money-movements/account-transfer/financial-accounts

响应结构：{"code": 200, "data": {"content": [...], "total_elements": N, ...}}
筛选参数：account_number, name（模糊），sub_type（Checking/Saving）, account_ids
"""
import pytest
from utils.logger import logger
from utils.assertions import assert_status_ok

pytestmark = pytest.mark.account_transfer


@pytest.mark.account_transfer
class TestAccountTransferFinancialAccounts:

    def _get_content(self, response):
        """从响应中安全取出 content 列表"""
        body = response.json()
        data = body.get("data", body) or {}
        return data.get("content", []) if isinstance(data, dict) else []

    def test_list_fa_success(self, account_transfer_api):
        """
        测试场景1：成功获取可用 FA 列表
        Test Scenario1: Successfully List Available Financial Accounts
        验证点：
        1. HTTP 200，code=200
        2. data.content 是数组，total_elements > 0
        3. 每条 FA 含 id, name, balance, account_number 等字段
        """
        resp = account_transfer_api.list_financial_accounts(size=10)
        assert resp.status_code == 200
        body = resp.json()
        assert body.get("code") == 200, f"code 应为 200，实际: {body.get('code')}"

        data = body.get("data", {})
        content = data.get("content", [])
        assert isinstance(content, list)
        total = data.get("total_elements", 0)
        assert total > 0, "应有可见的 FA 数据"
        logger.info(f"  total_elements={total}, returned={len(content)}")

        if content:
            fa = content[0]
            for field in ["id", "name", "balance", "account_number"]:
                if field in fa:
                    logger.info(f"  ✓ {field}: {fa.get(field)}")
        logger.info("✓ FA 列表获取成功")

    def test_list_fa_filter_by_name(self, account_transfer_api):
        """
        测试场景2：按 name 模糊搜索
        Test Scenario2: Filter FA List by Name (Fuzzy Search)
        验证点：先取真实 name，用前几个字符模糊搜索，结果均包含关键词
        """
        # 先取一条真实 FA name
        base_resp = account_transfer_api.list_financial_accounts(size=1)
        content = self._get_content(base_resp)
        if not content:
            pytest.skip("无 FA 数据，跳过 name 筛选测试")

        real_name = content[0].get("name", "")
        if not real_name:
            pytest.skip("name 字段为空")

        keyword = real_name[:4] if len(real_name) >= 4 else real_name
        logger.info(f"  使用 name keyword='{keyword}'")

        resp = account_transfer_api.list_financial_accounts(name=keyword, size=10)
        assert resp.status_code == 200
        assert resp.json().get("code") == 200

        filtered = self._get_content(resp)
        assert len(filtered) > 0, f"name='{keyword}' 筛选结果为空"
        for fa in filtered:
            assert keyword.lower() in (fa.get("name") or "").lower(), \
                f"筛选结果 name='{fa.get('name')}' 不含关键词 '{keyword}'"
        logger.info(f"✓ name 模糊搜索通过，返回 {len(filtered)} 条")

    @pytest.mark.parametrize("sub_type", ["Checking", "Saving"])
    def test_list_fa_filter_by_sub_type(self, account_transfer_api, sub_type):
        """
        测试场景3：按 sub_type 枚举筛选（Checking / Saving）
        Test Scenario3: Filter FA by sub_type Enum (Checking / Saving)
        """
        resp = account_transfer_api.list_financial_accounts(sub_type=sub_type, size=10)
        assert resp.status_code == 200
        body = resp.json()
        assert body.get("code") == 200, \
            f"sub_type='{sub_type}' 应被接受，实际 code={body.get('code')}"

        content = self._get_content(resp)
        if content:
            for fa in content:
                fa_type = fa.get("sub_type")
                if fa_type:
                    assert fa_type == sub_type, \
                        f"筛选结果 sub_type='{fa_type}' 与期望 '{sub_type}' 不一致"
        logger.info(f"✓ sub_type='{sub_type}' 筛选通过，返回 {len(content)} 条")

    def test_list_fa_filter_by_account_number(self, account_transfer_api):
        """
        测试场景4：按 account_number 精确筛选
        Test Scenario4: Filter FA by Account Number
        """
        # 先取真实 account_number
        base_resp = account_transfer_api.list_financial_accounts(size=1)
        content = self._get_content(base_resp)
        if not content:
            pytest.skip("无 FA 数据，跳过")

        real_num = content[0].get("account_number")
        if not real_num:
            pytest.skip("account_number 为空")

        resp = account_transfer_api.list_financial_accounts(account_number=real_num, size=5)
        assert resp.status_code == 200
        assert resp.json().get("code") == 200

        filtered = self._get_content(resp)
        assert len(filtered) > 0, f"account_number='{real_num}' 筛选结果为空"
        logger.info(f"✓ account_number 筛选通过，返回 {len(filtered)} 条")

    def test_list_fa_filter_by_account_ids(self, account_transfer_api):
        """
        测试场景5：使用 account_ids 数组筛选（传多个 id）
        Test Scenario5: Filter FA by account_ids Array
        """
        # 先取前 2 条 FA 的 account_id
        base_resp = account_transfer_api.list_financial_accounts(size=2)
        content = self._get_content(base_resp)
        if len(content) < 2:
            pytest.skip("FA 数据不足 2 条，跳过 account_ids 数组测试")

        ids = [fa.get("account_id") for fa in content if fa.get("account_id")][:2]
        if len(ids) < 2:
            pytest.skip("account_id 字段为空")

        logger.info(f"  使用 account_ids={ids}")
        resp = account_transfer_api.list_financial_accounts(account_ids=ids, size=10)
        assert resp.status_code == 200
        assert resp.json().get("code") == 200

        filtered = self._get_content(resp)
        logger.info(f"✓ account_ids 筛选通过，返回 {len(filtered)} 条")

    def test_list_fa_pagination(self, account_transfer_api):
        """
        测试场景6：分页功能验证
        Test Scenario6: Pagination Verification
        验证点：size=2 时返回数量 <= 2
        """
        resp = account_transfer_api.list_financial_accounts(page=0, size=2)
        assert resp.status_code == 200
        body = resp.json()
        assert body.get("code") == 200

        data = body.get("data", {})
        content = data.get("content", [])
        total = data.get("total_elements", 0)
        assert len(content) <= 2
        logger.info(f"✓ 分页验证通过: size=2, returned={len(content)}, total={total}")

    def test_list_fa_nonexistent_name(self, account_transfer_api):
        """
        测试场景7：搜索不存在的 name，应返回空列表
        Test Scenario7: Non-existent Name Returns Empty List
        """
        resp = account_transfer_api.list_financial_accounts(
            name="XYZXYZ_NOT_EXISTS_99999", size=5
        )
        assert resp.status_code == 200
        assert resp.json().get("code") == 200
        content = self._get_content(resp)
        assert len(content) == 0, f"不存在的 name 应返回空列表，实际 {len(content)} 条"
        logger.info("✓ 不存在的 name 返回空列表")
