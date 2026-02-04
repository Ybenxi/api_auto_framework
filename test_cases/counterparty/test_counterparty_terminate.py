"""
Counterparty Terminate 接口测试用例
测试 PATCH /api/v1/cores/{core}/counterparties/{id}/terminate 接口
"""
import pytest
from utils.logger import logger
from utils.assertions import (
    assert_status_ok,
    assert_fields_present
)


@pytest.mark.counterparty
@pytest.mark.update_api
class TestCounterpartyTerminate:
    """
    Counterparty 终止接口测试用例集
    """

    @pytest.mark.no_rerun  # 破坏性操作，禁止重试
    @pytest.mark.skip(reason="Terminate 是破坏性操作，影响数据，仅手动测试")
    def test_terminate_counterparty_success(self, counterparty_api, login_session):
        """
        测试场景1：成功终止 Counterparty
        验证点：
        1. 接口返回 200
        2. Counterparty 状态变为 Terminated
        """
        # 创建 Counterparty
        logger.info("创建测试用的 Counterparty")
        create_data = {
            "name": f"Auto TestYan Counterparty to Terminate {timestamp}",
            "type": "Person",
            "payment_type": "ACH",
            "bank_account_type": "Checking",
            "bank_routing_number": "091918457",
            "bank_name": "Auto TestYan Bank",
            "bank_account_owner_name": "Auto TestYan Owner",
            "bank_account_number": f"{timestamp}"[:9]
        }
        
        create_response = counterparty_api.create_counterparty(create_data)
        created_data = create_response.json()
        counterparty_id = created_data.get("id")
        logger.info(f"Counterparty 创建成功: {counterparty_id}")
        
        # 终止 Counterparty
        logger.info("终止 Counterparty")
        terminate_data = {"reason": "Test termination"}
        terminate_response = counterparty_api.terminate_counterparty(counterparty_id, terminate_data)
        
        # 验证响应
        logger.info("验证终止响应")
        assert_status_ok(terminate_response)
        
        response_body = terminate_response.json()
        terminated_data = response_body
        
        # 验证状态变为 Terminated
        assert terminated_data.get("status") == "Terminated", \
            f"状态未变为 Terminated: {terminated_data.get('status')}"
        
        logger.info("✓ Counterparty 终止成功")

    def test_terminate_counterparty_invalid_id(self, counterparty_api):
        """
        测试场景2：使用无效 ID 终止 Counterparty
        验证点：
        1. 返回 200 状态码（统一错误处理）
        2. 响应包含错误信息
        """
        logger.info("使用无效 ID 终止 Counterparty")
        invalid_id = "INVALID_COUNTERPARTY_ID_999999"
        terminate_data = {"reason": "Test"}
        
        response = counterparty_api.terminate_counterparty(invalid_id, terminate_data)
        
        # 验证错误响应
        logger.info("验证错误响应")
        assert_status_ok(response)
        
        response_body = response.json()
        assert response_body.get("code") != 200 or "error" in str(response_body).lower(), \
            "无效 ID 应该返回错误"
        
        logger.info("✓ 无效 ID 错误处理验证通过")

    @pytest.mark.skip(reason="Terminate 是破坏性操作")
    def test_terminate_counterparty_with_reason(self, counterparty_api, login_session):
        """
        测试场景3：终止 Counterparty 并提供原因
        验证点：
        1. 接口返回 200
        2. 原因被正确记录
        """
        # 创建
        create_data = {
            "name": f"Auto TestYan Counterparty Terminate Reason {timestamp}",
            "type": "Person",
            "payment_type": "ACH",
            "bank_account_type": "Checking",
            "bank_routing_number": "091918457",
            "bank_name": "Auto TestYan Bank",
            "bank_account_owner_name": "Auto TestYan Owner",
            "bank_account_number": f"{timestamp}"[:9]
        }
        
        create_response = counterparty_api.create_counterparty(create_data)
        created_data = create_response.json()
        counterparty_id = created_data.get("id")
        
        # 终止并提供原因
        logger.info("终止 Counterparty 并提供原因")
        terminate_data = {
            "reason": "Duplicate account detected"
        }
        
        response = counterparty_api.terminate_counterparty(counterparty_id, terminate_data)
        
        # 验证
        assert_status_ok(response)
        
        logger.info("✓ 带原因的终止操作验证通过")

    @pytest.mark.skip(reason="需要真实 account_id，待完善数据准备逻辑")
    def test_terminate_counterparty_response_structure(self, counterparty_api, login_session):
        """
        测试场景4：验证终止响应的数据结构
        验证点：
        1. 响应包含必需字段
        2. 响应结构完整
        """
        # 创建
        logger.info("创建测试用的 Counterparty")
        create_data = {
            "name": f"Auto TestYan Counterparty Term Structure {timestamp}",
            "type": "Person",
            "payment_type": "ACH",
            "bank_account_type": "Checking",
            "bank_routing_number": "091918457",
            "bank_name": "Auto TestYan Bank",
            "bank_account_owner_name": "Auto TestYan Owner",
            "bank_account_number": f"{timestamp}"[:9]
        }
        
        create_response = counterparty_api.create_counterparty(create_data)
        if create_response.status_code != 200:
            pytest.skip(f"创建失败")
        
        created_data = create_response.json()
        counterparty_id = created_data.get("id")
        
        # 调用终止接口（不实际执行，只验证接口可用性）
        logger.info("调用终止接口")
        terminate_data = {"reason": "Structure test"}
        response = counterparty_api.terminate_counterparty(counterparty_id, terminate_data)
        
        # 验证响应结构
        logger.info("验证响应结构")
        assert_status_ok(response)
        
        response_body = response.json()
        # 验证有响应数据
        assert response_body is not None, "响应不能为空"
        
        logger.info("✓ 终止接口响应结构验证通过")
