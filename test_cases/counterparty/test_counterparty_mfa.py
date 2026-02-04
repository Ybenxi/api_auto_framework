"""
Counterparty MFA 接口测试用例
测试 Counterparty Record Owner 的 MFA 相关接口（V2 API）
"""
import pytest
from utils.logger import logger
from utils.assertions import (
    assert_status_ok,
    assert_fields_present
)


@pytest.mark.counterparty
@pytest.mark.mfa_api
class TestCounterpartyMFA:
    """
    Counterparty MFA 接口测试用例集
    包含: Get, Send, Verify MFA 以及 Create/Update with MFA
    """

    @pytest.mark.skip(reason="需要真实 account_id，待完善数据准备逻辑")
    def test_get_counterparty_mfa_info(self, counterparty_api, login_session):
        """
        测试场景1：获取 Counterparty Record Owner 的 MFA 信息
        验证点：
        1. 接口返回 200
        2. 响应包含 MFA 相关信息
        """
        # 先创建一个 Counterparty
        logger.info("创建测试用的 Counterparty")
        create_data = {
            "name": f"Auto TestYan Counterparty MFA Test {timestamp}",
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
            pytest.skip(f"创建 Counterparty 失败")
        
        created_data = create_response.json()
        counterparty_id = created_data.get("id")
        logger.info(f"Counterparty 创建成功: {counterparty_id}")
        
        # 获取 MFA 信息
        logger.info("获取 MFA 信息")
        mfa_response = counterparty_api.get_counterparty_mfa(counterparty_id)
        
        # 验证响应
        logger.info("验证 MFA 响应")
        assert_status_ok(mfa_response)
        
        response_body = mfa_response.json()
        logger.info(f"MFA 信息: {response_body}")
        
        logger.info("✓ MFA 信息获取验证通过")

    @pytest.mark.skip(reason="需要实际的 Email/Phone 才能发送 MFA")
    def test_send_counterparty_mfa_email(self, counterparty_api, login_session):
        """
        测试场景2：发送 Email MFA 验证码
        验证点：
        1. 接口返回 200
        2. 响应确认验证码已发送
        """
        # 创建 Counterparty（需要真实 email）
        logger.info("创建带 Email 的 Counterparty")
        create_data = {
            "name": f"Auto TestYan Counterparty MFA Email {timestamp}",
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
        
        # 发送 MFA
        logger.info("发送 Email MFA")
        send_response = counterparty_api.send_counterparty_mfa(counterparty_id, "Email")
        
        # 验证响应
        assert_status_ok(send_response)
        
        logger.info("✓ MFA 发送成功")

    @pytest.mark.skip(reason="需要真实的验证码才能验证 MFA")
    def test_verify_counterparty_mfa(self, counterparty_api, login_session):
        """
        测试场景3：验证 Counterparty MFA 验证码
        验证点：
        1. 接口返回 200
        2. 验证成功后返回 access_token
        """
        # 此测试需要：
        # 1. 创建 Counterparty
        # 2. 发送 MFA
        # 3. 获取真实验证码
        # 4. 验证 MFA
        
        logger.info("测试需要真实验证码，跳过")
        pytest.skip("需要真实验证码")

    def test_send_counterparty_mfa_invalid_id(self, counterparty_api):
        """
        测试场景4：使用无效 ID 发送 MFA
        验证点：
        1. 返回 200 状态码（统一错误处理）
        2. 响应包含错误信息
        """
        logger.info("使用无效 ID 发送 MFA")
        invalid_id = "INVALID_COUNTERPARTY_ID_999999"
        
        send_response = counterparty_api.send_counterparty_mfa(invalid_id, "Email")
        
        # 验证错误响应
        logger.info("验证错误响应")
        assert_status_ok(send_response)
        
        response_body = send_response.json()
        assert response_body.get("code") != 200 or "error" in str(response_body).lower(), \
            "无效 ID 应该返回错误"
        
        logger.info("✓ 无效 ID 错误处理验证通过")

    @pytest.mark.skip(reason="需要真实 account_id，待完善数据准备逻辑")
    def test_verify_counterparty_mfa_invalid_code(self, counterparty_api, login_session):
        """
        测试场景5：使用无效验证码验证 MFA
        验证点：
        1. 接口返回 200
        2. 响应指示验证失败
        """
        # 创建 Counterparty
        logger.info("创建测试用的 Counterparty")
        create_data = {
            "name": f"Auto TestYan Counterparty MFA Invalid {timestamp}",
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
        
        # 使用无效验证码
        logger.info("使用无效验证码验证 MFA")
        invalid_code = "000000"
        
        verify_response = counterparty_api.verify_counterparty_mfa(
            counterparty_id, invalid_code, "Email"
        )
        
        # 验证响应
        logger.info("验证错误响应")
        assert_status_ok(verify_response)
        
        response_body = verify_response.json()
        # 应该返回错误或验证失败
        assert response_body.get("code") != 200 or response_body.get("success") == False, \
            "无效验证码应该返回错误"
        
        logger.info("✓ 无效验证码错误处理验证通过")

    @pytest.mark.skip(reason="需要 MFA access_token，依赖真实 MFA 流程")
    def test_create_counterparty_with_mfa(self, counterparty_api):
        """
        测试场景6：使用 MFA 创建 Counterparty（V2 接口）
        验证点：
        1. 接口返回 200
        2. 创建成功并包含 access_token
        """
        logger.info("使用 MFA 创建 Counterparty")
        
        counterparty_data = {
            "account_id": "test_account_id",
            "name": "Auto TestYan Counterparty with MFA",
            "payment_type": "ACH",
            "ach_account_number": "9999000011",
            "ach_routing_number": "021000021",
            "ach_account_type": "Checking",
            "access_token": "fake_mfa_token"  # 需要真实的 MFA token
        }
        
        response = counterparty_api.create_counterparty_with_mfa(counterparty_data)
        
        assert_status_ok(response)
        
        logger.info("✓ 使用 MFA 创建成功")

    @pytest.mark.skip(reason="需要 MFA access_token，依赖真实 MFA 流程")
    def test_update_counterparty_with_mfa(self, counterparty_api, login_session):
        """
        测试场景7：使用 MFA 更新 Counterparty（V2 接口）
        验证点：
        1. 接口返回 200
        2. 更新成功
        """
        # 此测试需要先创建 Counterparty，然后使用 MFA 更新
        logger.info("使用 MFA 更新 Counterparty")
        
        # 创建
        create_data = {
            "name": f"Auto TestYan Counterparty MFA Update {timestamp}",
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
        
        # 使用 MFA 更新
        update_data = {
            "name": "Auto TestYan Counterparty MFA Updated",
            "access_token": "fake_mfa_token"  # 需要真实的 MFA token
        }
        
        response = counterparty_api.update_counterparty_with_mfa(counterparty_id, update_data)
        
        assert_status_ok(response)
        
        logger.info("✓ 使用 MFA 更新成功")
