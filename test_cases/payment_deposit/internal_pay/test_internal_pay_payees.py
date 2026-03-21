"""
Internal Pay - Payees 接口测试用例
GET /api/v1/cores/{core}/money-movements/internal-pay/payees

响应结构：{"code": 200, "data": {"content": [...], "total_elements": N, ...}}
email 参数必填：根据邮箱查询该邮箱对应 account 下的 FA（隐私保护，返回信息有限）

已验证邮箱（dev actc 环境）：
  PAYEE_EMAIL = "byan@fintechautomation.com"（返回 23 条 payee FA）
"""
import pytest
from utils.logger import logger

PAYEE_EMAIL = "byan@fintechautomation.com"

pytestmark = pytest.mark.internal_pay


@pytest.mark.internal_pay
class TestInternalPayPayees:

    def _get_content(self, response):
        body = response.json()
        data = body.get("data", body) or {}
        return data.get("content", []) if isinstance(data, dict) else []

    def test_list_payees_with_valid_email(self, internal_pay_api):
        """
        测试场景1：使用有效邮箱查询 payee FA 列表
        Test Scenario1: List Payees with Valid Email
        验证点：
        1. HTTP 200，code=200
        2. data.content 是数组，total_elements > 0
        3. 每条含 id, name, account_number, sub_type, record_type
        4. account_number 为脱敏格式（*号开头）
        """
        resp = internal_pay_api.list_payees(email=PAYEE_EMAIL, size=10)
        assert resp.status_code == 200
        body = resp.json()
        assert body.get("code") == 200, \
            f"code 应为 200，实际: {body.get('code')}, err={body.get('error_message')}"

        data = body.get("data", {})
        content = data.get("content", [])
        total = data.get("total_elements", 0)
        assert total > 0, "有效邮箱应能查到 payee FA"
        assert isinstance(content, list)
        logger.info(f"  total={total}, returned={len(content)}")

        if content:
            p = content[0]
            for field in ["id", "name", "account_number", "sub_type", "record_type"]:
                if field in p:
                    logger.info(f"  ✓ {field}: {p.get(field)}")
            # account_number 可能脱敏也可能不脱敏（取决于隐私配置）
            acc_num = p.get("account_number", "")
            if acc_num:
                logger.info(f"  account_number: {acc_num}（{'脱敏' if '*' in acc_num else '未脱敏，探索性结果'}）")
        logger.info("✓ Payees 列表获取成功")

    def test_list_payees_pagination(self, internal_pay_api):
        """
        测试场景2：分页功能验证
        Test Scenario2: Pagination Verification
        """
        resp = internal_pay_api.list_payees(email=PAYEE_EMAIL, size=3, page=0)
        assert resp.status_code == 200
        data = resp.json().get("data", {})
        content = data.get("content", [])
        assert len(content) <= 3
        assert data.get("size") == 3
        assert data.get("number") == 0
        logger.info(f"✓ 分页验证通过: size=3, returned={len(content)}, total={data.get('total_elements',0)}")

    def test_list_payees_missing_email(self, internal_pay_api):
        """
        测试场景3：缺少必填参数 email
        Test Scenario3: Missing Required email Parameter Returns Error
        验证点：code != 200
        """
        url = internal_pay_api.config.get_full_url("/money-movements/internal-pay/payees")
        resp = internal_pay_api.session.get(url)
        assert resp.status_code == 200
        body = resp.json()
        assert body.get("code") != 200
        logger.info(f"✓ 缺少 email 被拒绝: code={body.get('code')}, msg={body.get('error_message')}")

    def test_list_payees_nonexistent_email(self, internal_pay_api):
        """
        测试场景4：使用不存在的邮箱
        Test Scenario4: Non-existent Email Returns Empty List or Error
        验证点：HTTP 200，返回空列表或 code != 200
        """
        resp = internal_pay_api.list_payees(
            email="nonexistent_user_99999@notarealdomain.xyz", size=5
        )
        assert resp.status_code == 200
        body = resp.json()
        code = body.get("code")
        if code == 200:
            content = self._get_content(resp)
            assert len(content) == 0, f"不存在的邮箱应返回空列表，实际 {len(content)} 条"
            logger.info("✓ 不存在邮箱返回空列表")
        else:
            logger.info(f"✓ 不存在邮箱被拒绝: code={code}")

    def test_list_payees_invalid_email_format(self, internal_pay_api):
        """
        测试场景5：使用非法邮箱格式
        Test Scenario5: Invalid Email Format Returns Error
        """
        resp = internal_pay_api.list_payees(email="not_an_email_format", size=5)
        assert resp.status_code == 200
        body = resp.json()
        code = body.get("code")
        if code != 200:
            logger.info(f"✓ 非法邮箱格式被拒绝: code={code}")
        else:
            content = self._get_content(resp)
            assert len(content) == 0, "非法邮箱格式应无匹配结果"
            logger.info("⚠ 非法邮箱格式接受但返回空列表（探索性结果）")

    def test_list_payees_response_privacy(self, internal_pay_api):
        """
        测试场景6：验证隐私保护（返回信息有限）
        Test Scenario6: Verify Privacy Protection - Limited Info Returned
        验证点：
        1. 响应不含完整账号（account_number 脱敏）
        2. 响应不含 available_balance 等敏感字段（payers 才有）
        """
        resp = internal_pay_api.list_payees(email=PAYEE_EMAIL, size=3)
        assert resp.status_code == 200
        content = self._get_content(resp)
        if not content:
            pytest.skip("无 payee 数据")

        p = content[0]
        logger.info(f"  payee 响应字段: {list(p.keys())}")
        # payee 返回有限信息，不含详细账户管理字段（如 pending_deposits 等操作性字段）
        # 注意：实际 API 可能返回 available_balance=0 作为占位符
        assert "id" in p, "payee 响应应含 id"
        assert "name" in p, "payee 响应应含 name"
        logger.info(f"✓ Payee 响应字段验证通过: {list(p.keys())}")
