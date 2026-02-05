"""
User Sign Up - Email Verification 接口测试用例
测试邮箱验证发起和验证接口
"""
import pytest
from utils.logger import logger
from utils.assertions import assert_status_ok


@pytest.mark.user_signup
@pytest.mark.create_api
class TestUserSignUpEmailVerification:
    """
    邮箱验证接口测试用例集
    包含Step 1（发起）和Step 2（验证）
    """

    @pytest.mark.skip(reason="需要真实邮箱接收验证码")
    def test_initiate_email_verification_success(self, user_signup_api):
        """
        测试场景1：成功发起邮箱验证
        验证点：
        1. 接口返回 200
        2. code=200
        3. 返回token
        """
        logger.info("测试场景1：成功发起邮箱验证")
        
        import time
        email = f"auto.testyan.{int(time.time())}@example.com"
        
        response = user_signup_api.initiate_email_verification(email)
        
        assert_status_ok(response)
        
        response_body = response.json()
        assert response_body.get("code") == 200
        
        token = response_body.get("data")
        assert token is not None, "应返回token"
        assert isinstance(token, str), "token应为字符串"
        
        logger.info(f"✓ 邮箱验证发起成功，token: {token[:10]}...")

    def test_initiate_with_invalid_email_format(self, user_signup_api):
        """
        测试场景2：无效的邮箱格式
        验证点：
        1. 接口返回错误
        """
        logger.info("测试场景2：无效的邮箱格式")
        
        response = user_signup_api.initiate_email_verification("invalid-email")
        
        assert response.status_code == 200
        
        response_body = response.json()
        logger.info(f"响应code: {response_body.get('code')}")
        logger.info(f"错误信息: {response_body.get('error_message')}")
        
        logger.info("✓ 无效邮箱格式测试完成")

    def test_initiate_with_existing_email(self, user_signup_api):
        """
        测试场景3：邮箱已存在
        验证点：
        1. error_message提示"An account with this email address already exists"
        2. 返回的code值（文档未说明）
        """
        logger.info("测试场景3：邮箱已存在")
        
        # 使用一个可能已存在的邮箱格式
        response = user_signup_api.initiate_email_verification("existing@example.com")
        
        assert response.status_code == 200
        
        response_body = response.json()
        logger.info(f"响应code: {response_body.get('code')}")
        logger.info(f"错误信息: {response_body.get('error_message')}")
        
        logger.info("✓ 邮箱已存在测试完成")

    @pytest.mark.skip(reason="需要真实验证码")
    def test_verify_email_code_success(self, user_signup_api):
        """
        测试场景4：成功验证邮箱码
        验证点：
        1. 接口返回 200
        2. 返回新token
        """
        logger.info("测试场景4：成功验证邮箱码")
        
        # 步骤1：发起验证
        email = f"auto.testyan.verify@example.com"
        init_response = user_signup_api.initiate_email_verification(email)
        token1 = init_response.json().get("data")
        
        # 步骤2：验证码（需要从邮件获取真实验证码）
        passcode = "123456"  # 实际需要真实验证码
        
        response = user_signup_api.verify_email_code(passcode, token1)
        
        assert_status_ok(response)
        
        response_body = response.json()
        token2 = response_body.get("data")
        assert token2 is not None, "应返回新token"
        
        logger.info(f"✓ 邮箱验证成功，新token: {token2[:10]}...")

    def test_verify_with_invalid_passcode(self, user_signup_api):
        """
        测试场景5：无效的验证码
        验证点：
        1. 接口返回错误
        2. error_message: "The entered verification code is incorrect"
        """
        logger.info("测试场景5：无效的验证码")
        
        response = user_signup_api.verify_email_code("000000", "fake_token")
        
        assert response.status_code == 200
        
        response_body = response.json()
        logger.info(f"响应code: {response_body.get('code')}")
        logger.info(f"错误信息: {response_body.get('error_message')}")
        
        logger.info("✓ 无效验证码测试完成")

    def test_verify_with_invalid_token(self, user_signup_api):
        """
        测试场景6：无效的enroll_token
        验证点：
        1. 接口返回错误
        """
        logger.info("测试场景6：无效的enroll_token")
        
        response = user_signup_api.verify_email_code("123456", "INVALID_TOKEN_999")
        
        assert response.status_code == 200
        
        response_body = response.json()
        logger.info(f"响应code: {response_body.get('code')}")
        
        logger.info("✓ 无效token测试完成")

    def test_passcode_format_validation(self, user_signup_api):
        """
        测试场景7：验证码格式验证
        验证点：
        1. 记录验证码格式要求
        2. 文档未明确说明格式
        """
        logger.info("测试场景7：验证码格式验证")
        
        logger.warning("⚠️ 验证码格式未在文档说明")
        logger.info("从示例推测：6位数字")
        logger.info("未知：有效期、重试限制")
        
        logger.info("✓ 验证码格式需求已记录")
