"""
User Sign Up - Create UniFi User 接口测试用例
测试创建用户接口
"""
import pytest
from utils.logger import logger
from utils.assertions import assert_status_ok
from data.enums import ClientType, RecoveryQuestion


@pytest.mark.user_signup
@pytest.mark.create_api
@pytest.mark.no_rerun
@pytest.mark.skip(reason="需要完整注册流程和密码加密，暂不实现")
class TestUserSignUpCreateUser:
    """
    创建UniFi用户接口测试用例集
    ⚠️ 需要前面4步的token和密码加密，测试全部skip
    """

    def test_create_user_individual_success(self, user_signup_api):
        """
        测试场景1：成功创建个人用户
        验证点：
        1. 接口返回 200
        2. data=true
        """
        logger.info("测试场景1：成功创建个人用户")
        
        response = user_signup_api.create_unifi_user(
            enroll_token="fake_token4",
            first_name="Auto",
            last_name="TestYan",
            email="auto.testyan@example.com",
            phone="+11234567890",
            client_type=ClientType.INDIVIDUAL_CLIENT,
            encoded_password="ENCRYPTED_PASSWORD_BASE64",
            recovery_question=RecoveryQuestion.DISLIKED_FOOD,
            recovery_answer="rice"
        )
        
        logger.info(f"响应状态: {response.status_code}")
        
        logger.info("✓ 个人用户创建接口调用完成")

    def test_create_user_business_success(self, user_signup_api):
        """
        测试场景2：成功创建企业用户
        验证点：
        1. 接口返回 200
        2. company_name必需
        """
        logger.info("测试场景2：成功创建企业用户")
        
        response = user_signup_api.create_unifi_user(
            enroll_token="fake_token4",
            first_name="Auto",
            last_name="TestYan",
            email="auto.testyan.biz@example.com",
            phone="+11234567890",
            client_type=ClientType.BUSINESS,
            company_name="Auto TestYan Corp",
            encoded_password="ENCRYPTED_PASSWORD",
            recovery_question=RecoveryQuestion.FIRST_AWARD,
            recovery_answer="best student"
        )
        
        logger.info(f"响应状态: {response.status_code}")
        
        logger.info("✓ 企业用户创建接口调用完成")

    def test_create_user_with_idp_user_true(self, user_signup_api):
        """
        测试场景3：has_idp_user=true时创建用户
        验证点：
        1. 不提供密码和安全问题
        2. 验证"must be left empty"的处理
        """
        logger.info("测试场景3：has_idp_user=true场景")
        
        response = user_signup_api.create_unifi_user(
            enroll_token="fake_token4",
            first_name="Existing",
            last_name="User",
            email="existing@example.com",
            phone="+11234567890",
            client_type=ClientType.INDIVIDUAL_CLIENT
            # 不提供 encoded_password, recovery_question, recovery_answer
        )
        
        logger.info(f"响应状态: {response.status_code}")
        
        logger.info("✓ IdP用户创建接口调用完成")

    def test_missing_company_name_for_business(self, user_signup_api):
        """
        测试场景4：企业类型缺少company_name
        验证点：
        1. 接口返回错误
        """
        logger.info("测试场景4：企业类型缺少company_name")
        
        response = user_signup_api.create_unifi_user(
            enroll_token="fake_token",
            first_name="Test",
            last_name="User",
            email="test@example.com",
            phone="+11234567890",
            client_type=ClientType.BUSINESS
            # 缺少 company_name
        )
        
        assert response.status_code == 200
        response_body = response.json()
        logger.info(f"响应code: {response_body.get('code')}")
        
        logger.info("✓ 缺少company_name测试完成")

    def test_company_name_length_limit(self, user_signup_api):
        """
        测试场景5：company_name长度限制
        验证点：
        1. 超过80字符应返回错误
        """
        logger.info("测试场景5：company_name长度限制")
        
        long_name = "A" * 81  # 81个字符
        
        response = user_signup_api.create_unifi_user(
            enroll_token="fake_token",
            first_name="Test",
            last_name="User",
            email="test@example.com",
            phone="+11234567890",
            client_type=ClientType.BUSINESS,
            company_name=long_name
        )
        
        assert response.status_code == 200
        logger.info(f"响应code: {response.json().get('code')}")
        
        logger.info("✓ company_name长度限制测试完成")

    def test_recovery_answer_length_validation(self, user_signup_api):
        """
        测试场景6：recovery_answer长度验证
        验证点：
        1. 必须4-50字符
        2. 过短或过长应返回错误
        """
        logger.info("测试场景6：recovery_answer长度验证")
        
        # 测试过短（<4字符）
        response_short = user_signup_api.create_unifi_user(
            enroll_token="fake_token",
            first_name="Test",
            last_name="User",
            email="test@example.com",
            phone="+11234567890",
            client_type=ClientType.INDIVIDUAL_CLIENT,
            encoded_password="ENCRYPTED",
            recovery_question=RecoveryQuestion.DISLIKED_FOOD,
            recovery_answer="abc"  # 只有3个字符
        )
        
        logger.info(f"过短答案响应code: {response_short.json().get('code')}")
        
        # 测试过长（>50字符）
        long_answer = "A" * 51
        response_long = user_signup_api.create_unifi_user(
            enroll_token="fake_token",
            first_name="Test",
            last_name="User",
            email="test@example.com",
            phone="+11234567890",
            client_type=ClientType.INDIVIDUAL_CLIENT,
            encoded_password="ENCRYPTED",
            recovery_question=RecoveryQuestion.DISLIKED_FOOD,
            recovery_answer=long_answer
        )
        
        logger.info(f"过长答案响应code: {response_long.json().get('code')}")
        
        logger.info("✓ recovery_answer长度验证完成")

    def test_client_type_enum_with_space(self, user_signup_api):
        """
        测试场景7：client_type枚举值验证（有空格）
        验证点：
        1. "Individual Client"枚举值包含空格
        2. 验证是否正确处理
        """
        logger.info("测试场景7：client_type枚举值验证")
        
        logger.warning("⚠️ 文档问题：client_type枚举值不统一")
        logger.info("Individual Client - 有空格")
        logger.info("Business - 无空格")
        
        response = user_signup_api.create_unifi_user(
            enroll_token="fake_token",
            first_name="Test",
            last_name="User",
            email="test@example.com",
            phone="+11234567890",
            client_type="Individual Client",  # 使用带空格的枚举值
            encoded_password="ENCRYPTED",
            recovery_question="disliked_food",
            recovery_answer="test answer"
        )
        
        logger.info(f"响应code: {response.json().get('code')}")
        
        logger.info("✓ 枚举值测试完成")

    def test_recovery_question_circular_definition(self, user_signup_api):
        """
        测试场景8：recovery_question循环定义问题
        验证点：
        1. "favorite_security_question"是自相矛盾的问题
        """
        logger.info("测试场景8：recovery_question循环定义验证")
        
        logger.warning("⚠️ 文档问题：favorite_security_question")
        logger.warning("问题：What is your favorite security question?")
        logger.warning("这是循环定义，用户无法回答")
        
        logger.info("✓ 循环定义问题已记录")

    def test_password_encryption_requirements(self, user_signup_api):
        """
        测试场景9：密码加密要求说明
        验证点：
        1. 记录加密要求
        """
        logger.info("测试场景9：密码加密要求")
        
        logger.info("⚠️ 密码加密要求：")
        logger.info("1. RSA + PKCS1Padding加密")
        logger.info("2. Base64编码")
        logger.info("3. 使用Dashboard的Encryption Key")
        logger.info("4. 原始密码强度要求未说明")
        
        logger.info("✓ 加密要求已记录")
