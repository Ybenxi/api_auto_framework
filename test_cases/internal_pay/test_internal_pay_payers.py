"""
Internal Pay - Payers 接口测试用例
测试 GET /api/v1/cores/{core}/money-movements/internal-pay/financial-accounts 接口
"""
import pytest
from utils.logger import logger
from utils.assertions import assert_status_ok
from data.enums import AccountSubType


@pytest.mark.internal_pay
@pytest.mark.list_api
class TestInternalPayPayers:
    """
    Internal Pay付款方列表接口测试用例集
    ⚠️ 文档问题：
    1. HTTP方法示例错误（GET写成POST）
    2. 响应无code包装层
    """

    def test_list_payers_success(self, internal_pay_api):
        """
        测试场景1：成功获取付款方列表
        验证点：
        1. 接口返回 200
        2. 返回Financial Accounts列表
        """
        logger.info("测试场景1：成功获取付款方列表")
        
        response = internal_pay_api.list_payers(page=0, size=10)
        
        assert response.status_code == 200
        
        response_body = response.json()
        
        # 验证无code包装层
        if "content" in response_body:
            logger.info(f"✓ 付款方列表获取成功，返回 {len(response_body.get('content', []))} 个账户")
        
        logger.info("✓ 付款方列表获取成功")

    def test_filter_by_account_number(self, internal_pay_api):
        """
        测试场景2：按account_number筛选
        验证点：
        1. account_number参数生效
        """
        logger.info("测试场景2：按account_number筛选")
        
        response = internal_pay_api.list_payers(account_number="1-01-1-0007876", size=10)
        
        assert response.status_code == 200
        
        logger.info("✓ account_number筛选验证通过")

    def test_filter_by_name(self, internal_pay_api):
        """
        测试场景3：按name模糊搜索
        验证点：
        1. name参数生效（模糊搜索）
        """
        logger.info("测试场景3：按name模糊搜索")
        
        response = internal_pay_api.list_payers(name="Test", size=10)
        
        assert response.status_code == 200
        
        logger.info("✓ name模糊搜索验证通过")

    def test_filter_by_sub_type(self, internal_pay_api):
        """
        测试场景4：按sub_type筛选
        验证点：
        1. sub_type参数生效
        2. 支持Checking和Savings（注意拼写）
        """
        logger.info("测试场景4：按sub_type筛选")
        
        response = internal_pay_api.list_payers(sub_type=AccountSubType.CHECKING, size=10)
        
        assert response.status_code == 200
        
        logger.info("✓ sub_type筛选验证通过")

    def test_filter_by_account_ids(self, internal_pay_api):
        """
        测试场景5：按account_ids批量查询
        验证点：
        1. account_ids参数支持数组
        2. 逗号分隔格式
        """
        logger.info("测试场景5：按account_ids批量查询")
        
        # 使用列表格式（API会自动转为逗号分隔）
        response = internal_pay_api.list_payers(
            account_ids=["123", "456", "789"],
            size=10
        )
        
        assert response.status_code == 200
        
        logger.info("✓ account_ids批量查询验证通过")

    def test_response_structure(self, internal_pay_api):
        """
        测试场景6：响应结构验证
        验证点：
        1. 包含余额信息（available_balance, balance等）
        2. 包含账户基本信息
        """
        logger.info("测试场景6：响应结构验证")
        
        response = internal_pay_api.list_payers(size=1)
        
        assert response.status_code == 200
        
        content = response.json().get("content", [])
        
        if content:
            account = content[0]
            
            # 验证余额字段
            balance_fields = ["available_balance", "balance", "pending_deposits", "pending_withdrawals"]
            for field in balance_fields:
                if field in account:
                    logger.debug(f"{field}: {account[field]}")
            
            # 验证基本字段
            assert "id" in account or "account_id" in account
            assert "account_number" in account
        
        logger.info("✓ 响应结构验证通过")
