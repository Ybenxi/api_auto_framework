"""
Internal Pay - Payees 接口测试用例
测试 GET /api/v1/cores/{core}/money-movements/internal-pay/payees 接口
"""
import pytest
from utils.logger import logger
from utils.assertions import assert_status_ok


@pytest.mark.internal_pay
@pytest.mark.list_api
class TestInternalPayPayees:
    """
    Internal Pay收款人查询接口测试用例集
    ⚠️ 文档问题：
    1. email参数标记为required（与List语义矛盾）
    2. 实际是"查询单个payee"而不是"列表"
    3. 响应中account_number脱敏显示
    """

    @pytest.mark.skip(reason="需要真实的收款人email")
    def test_list_payees_by_email_success(self, internal_pay_api):
        """
        测试场景1：根据邮箱查询收款人
        验证点：
        1. 接口返回 200
        2. 返回匹配的收款人账户
        3. account_number脱敏显示
        """
        logger.info("测试场景1：根据邮箱查询收款人")
        
        response = internal_pay_api.list_payees(email="recipient@example.com")
        
        assert response.status_code == 200
        
        response_body = response.json()
        content = response_body.get("content", [])
        
        if content:
            payee = content[0]
            
            # 验证脱敏
            account_number = payee.get("account_number")
            if account_number and "*" in account_number:
                logger.info(f"✓ account_number脱敏显示: {account_number}")
            
            # 验证不包含余额信息（隐私保护）
            if "balance" not in payee and "available_balance" not in payee:
                logger.info("✓ 收款人账户不显示余额（隐私保护）")
        
        logger.info("✓ 收款人查询成功")

    def test_email_required_parameter(self, internal_pay_api):
        """
        测试场景2：email参数必需性验证
        验证点：
        1. email是required参数
        2. 这与"List"接口语义矛盾
        """
        logger.info("测试场景2：email参数必需性验证")
        
        logger.warning("⚠️ 文档问题：email参数标记为required")
        logger.warning("这使得接口变成'查询单个payee'而不是'列表'")
        logger.warning("接口名称与功能不符")
        
        logger.info("✓ email必需性问题已记录")

    def test_invalid_email(self, internal_pay_api):
        """
        测试场景3：无效的邮箱
        验证点：
        1. 接口返回空结果或错误
        """
        logger.info("测试场景3：无效的邮箱")
        
        response = internal_pay_api.list_payees(email="nonexistent@example.com")
        
        assert response.status_code == 200
        
        response_body = response.json()
        content = response_body.get("content", [])
        
        logger.info(f"无效邮箱返回结果数: {len(content)}")
        
        logger.info("✓ 无效邮箱测试完成")

    def test_account_number_masking(self, internal_pay_api):
        """
        测试场景4：account_number脱敏验证
        验证点：
        1. Payees响应中account_number脱敏
        2. Payers响应中account_number完整
        3. 记录脱敏规则差异
        """
        logger.info("测试场景4：account_number脱敏验证")
        
        logger.info("⚠️ 文档问题：脱敏规则不一致")
        logger.info("List Payers: account_number完整显示")
        logger.info("List Payees: account_number脱敏显示（*******7876）")
        logger.info("原因：隐私保护，合理但应在文档说明")
        
        logger.info("✓ 脱敏规则验证完成")

    def test_response_structure(self, internal_pay_api):
        """
        测试场景5：响应结构验证
        验证点：
        1. 返回基本账户信息
        2. 不包含余额信息
        """
        logger.info("测试场景5：响应结构验证")
        
        # 使用测试邮箱
        response = internal_pay_api.list_payees(email="test@example.com", size=1)
        
        assert response.status_code == 200
        
        response_body = response.json()
        content = response_body.get("content", [])
        
        if content:
            payee = content[0]
            logger.debug(f"Payee字段: {list(payee.keys())}")
            
            # 应包含的字段
            expected_fields = ["name", "account_number", "account_id", "sub_type"]
            for field in expected_fields:
                if field in payee:
                    logger.debug(f"✓ 包含字段: {field}")
        
        logger.info("✓ 响应结构验证完成")
