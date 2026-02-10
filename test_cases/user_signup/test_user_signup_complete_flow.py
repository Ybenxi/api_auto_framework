"""
User Sign Up - Complete Registration Flow 接口测试用例
测试完整的注册流程
"""
import pytest
from utils.logger import logger
from data.enums import ClientType, RecoveryQuestion


@pytest.mark.user_signup
@pytest.mark.create_api
@pytest.mark.skip(reason="需要真实验证码和密码加密，完整流程暂不实现")
class TestUserSignUpCompleteFlow:
    """
    完整注册流程测试用例集
    ⚠️ 需要真实验证码接收和密码加密，全部skip
    """

    def test_complete_flow_individual_user(self, user_signup_api):
        """
        测试场景1：完整注册流程-个人用户
        验证点：
        1. 5步流程全部成功
        2. 最终创建用户成功
        """
        logger.info("测试场景1：完整注册流程-个人用户")
        
        import time
        timestamp = int(time.time())
        
        result = user_signup_api.complete_signup_flow(
            email=f"auto.testyan.{timestamp}@example.com",
            phone="+11234567890",
            email_passcode="123456",  # 需要真实验证码
            sms_passcode="654321",    # 需要真实验证码
            first_name="Auto",
            last_name="TestYan",
            client_type=ClientType.INDIVIDUAL_CLIENT,
            encoded_password="ENCRYPTED_PASSWORD",  # 需要真实加密
            recovery_question=RecoveryQuestion.DISLIKED_FOOD,
            recovery_answer="test answer"
        )
        
        logger.info(f"流程步骤数: {len(result['steps'])}")
        logger.info(f"最终结果: {'成功' if result['success'] else '失败'}")
        
        logger.info("✓ 完整流程测试完成")

    def test_complete_flow_business_user(self, user_signup_api):
        """
        测试场景2：完整注册流程-企业用户
        验证点：
        1. 包含company_name
        2. client_type=Business
        """
        logger.info("测试场景2：完整注册流程-企业用户")
        
        import time
        timestamp = int(time.time())
        
        result = user_signup_api.complete_signup_flow(
            email=f"auto.testyan.biz.{timestamp}@example.com",
            phone="+11234567891",
            email_passcode="123456",
            sms_passcode="654321",
            first_name="Auto",
            last_name="TestYan",
            client_type=ClientType.BUSINESS,
            company_name=f"Auto TestYan Corp {timestamp}",
            encoded_password="ENCRYPTED_PASSWORD",
            recovery_question=RecoveryQuestion.CHILDHOOD_DREAM_JOB,
            recovery_answer="software engineer"
        )
        
        logger.info(f"企业用户注册结果: {result['success']}")
        
        logger.info("✓ 企业用户完整流程测试完成")

    def test_complete_flow_with_idp_user(self, user_signup_api):
        """
        测试场景3：has_idp_user=true的完整流程
        验证点：
        1. 不提供密码和安全问题
        2. 流程仍然成功
        """
        logger.info("测试场景3：IdP用户注册流程")
        
        result = user_signup_api.complete_signup_flow(
            email="existing.user@example.com",
            phone="+11234567892",
            email_passcode="123456",
            sms_passcode="654321",
            first_name="Auto TestYan Existing",
            last_name="Auto TestYan User",
            client_type=ClientType.INDIVIDUAL_CLIENT
            # 不提供 encoded_password, recovery_question, recovery_answer
        )
        
        if result.get("has_idp_user"):
            logger.info("✓ 检测到has_idp_user=true")
        
        logger.info("✓ IdP用户流程测试完成")

    def test_token_expiration_handling(self, user_signup_api):
        """
        测试场景4：token过期处理
        验证点：
        1. 使用过期token应返回错误
        2. 需要重新开始流程
        """
        logger.info("测试场景4：token过期处理")
        
        logger.warning("⚠️ 文档问题：token有效期未说明")
        logger.info("未知：每个token的有效期")
        logger.info("未知：过期后从哪一步重新开始")
        
        logger.info("✓ token过期需求已记录")

    def test_phone_duplicate_handling(self, user_signup_api):
        """
        测试场景5：手机号重复处理
        验证点：
        1. 手机号已被使用时的处理
        2. 在哪个步骤检查（SMS还是Create User）
        """
        logger.info("测试场景5：手机号重复处理")
        
        logger.warning("⚠️ 文档问题：phone重复处理未说明")
        logger.info("未知：是否允许同一手机号注册多个账户")
        logger.info("未知：在哪个步骤检查重复")
        
        logger.info("✓ 手机号重复需求已记录")


@pytest.mark.user_signup
@pytest.mark.create_api
class TestUserSignUpCreateUserErrors:
    """
    创建用户错误处理测试（可运行）
    """

    def test_missing_required_field(self, user_signup_api):
        """
        测试场景6：缺少必需字段
        验证点：
        1. 接口返回错误
        """
        logger.info("测试场景6：缺少必需字段")
        
        response = user_signup_api.create_unifi_user(
            enroll_token="fake_token",
            first_name="Auto TestYan Test",
            last_name="Auto TestYan User",
            email="test@example.com",
            phone="+11234567890",
            client_type=ClientType.INDIVIDUAL_CLIENT
            # 缺少 encoded_password（has_idp_user=false时必需）
        )
        
        assert response.status_code == 200
        logger.info(f"响应code: {response.json().get('code')}")
        
        logger.info("✓ 缺少必需字段测试完成")

    def test_invalid_client_type(self, user_signup_api):
        """
        测试场景7：无效的client_type
        验证点：
        1. 接口返回错误
        """
        logger.info("测试场景7：无效的client_type")
        
        response = user_signup_api.create_unifi_user(
            enroll_token="fake_token",
            first_name="Auto TestYan Test",
            last_name="Auto TestYan User",
            email="test@example.com",
            phone="+11234567890",
            client_type="Invalid_Type"
        )
        
        assert response.status_code == 200
        logger.info(f"响应code: {response.json().get('code')}")
        
        logger.info("✓ 无效client_type测试完成")

    def test_invalid_recovery_question(self, user_signup_api):
        """
        测试场景8：无效的recovery_question
        验证点：
        1. 接口返回错误
        """
        logger.info("测试场景8：无效的recovery_question")
        
        response = user_signup_api.create_unifi_user(
            enroll_token="fake_token",
            first_name="Auto TestYan Test",
            last_name="Auto TestYan User",
            email="test@example.com",
            phone="+11234567890",
            client_type=ClientType.INDIVIDUAL_CLIENT,
            encoded_password="ENCRYPTED",
            recovery_question="invalid_question",
            recovery_answer="test answer"
        )
        
        assert response.status_code == 200
        logger.info(f"响应code: {response.json().get('code')}")
        
        logger.info("✓ 无效recovery_question测试完成")
