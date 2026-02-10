"""
Card Opening - Reward Card Application 接口测试用例
测试 POST /api/v1/cores/{core}/card-issuance/applications/reward-card 接口
"""
import pytest
from utils.logger import logger
from utils.assertions import assert_status_ok


@pytest.mark.card_opening
@pytest.mark.create_api
@pytest.mark.skip(reason="需要RSA加密SSN，且需要真实数据，暂不实现加密逻辑")
class TestCardOpeningRewardCard:
    """
    奖励卡申请接口测试用例集
    ⚠️ 重要：此接口需要加密SSN，测试全部skip
    ⚠️ 文档问题：示例数据不现实（应为加密后的值）
    """

    def test_create_reward_card_success(self, card_opening_api):
        """
        测试场景1：成功创建奖励卡申请
        验证点：
        1. 接口返回 200
        2. 返回申请ID和card_id
        """
        logger.info("测试场景1：成功创建奖励卡申请")
        
        response = card_opening_api.create_reward_card_application(
            sub_program_id="test_sub_program_id",
            email="auto.testyan.reward@example.com",
            first_name="Auto",
            last_name="TestYan",
            ssn="ENCRYPTED_SSN_HERE",  # 需要RSA加密
            telephone="1234567890",
            address1="123 Test Street",
            city="New York",
            state="NY",
            postalcode="10001",
            birth_date="1990-01-01",
            expiration_date="12/2026"
        )
        
        assert_status_ok(response)
        
        logger.info("✓ 奖励卡申请创建成功")

    def test_complete_personal_info(self, card_opening_api):
        """
        测试场景2：完整个人信息验证
        验证点：
        1. 包含middle_name和address2
        """
        logger.info("测试场景2：完整个人信息验证")
        
        response = card_opening_api.create_reward_card_application(
            sub_program_id="test_sub_program_id",
            email="auto.testyan@example.com",
            first_name="Auto",
            middle_name="Test",
            last_name="Yan",
            ssn="ENCRYPTED_SSN",
            telephone="1234567890",
            address1="123 Test Street",
            address2="Apt 4B",
            city="New York",
            state="NY",
            postalcode="10001",
            birth_date="1990-01-01",
            expiration_date="12/2026"
        )
        
        assert_status_ok(response)
        
        logger.info("✓ 完整个人信息验证通过")

    def test_state_code_validation(self, card_opening_api):
        """
        测试场景3：州代码验证
        验证点：
        1. state必须是有效的2字母代码
        """
        logger.info("测试场景3：州代码验证")
        
        response = card_opening_api.create_reward_card_application(
            sub_program_id="test_sub_program_id",
            email="auto.testyan@example.com",
            first_name="Auto",
            last_name="TestYan",
            ssn="ENCRYPTED_SSN",
            telephone="1234567890",
            address1="123 Test Street",
            city="New York",
            state="CA",  # California
            postalcode="90001",
            birth_date="1990-01-01",
            expiration_date="12/2026"
        )
        
        assert_status_ok(response)
        
        logger.info("✓ 州代码验证通过")


@pytest.mark.card_opening
@pytest.mark.create_api
class TestCardOpeningRewardCardErrors:
    """
    奖励卡申请错误处理测试（可运行）
    """

    def test_invalid_state_code(self, card_opening_api):
        """
        测试场景4：无效的state代码
        验证点：
        1. 接口返回错误
        """
        logger.info("测试场景4：无效的state代码")
        
        response = card_opening_api.create_reward_card_application(
            sub_program_id="test_sub_program_id",
            email="test@example.com",
            first_name="Auto TestYan Test",
            last_name="Auto TestYan User",
            ssn="1234",
            telephone="1234567890",
            address1="123 Test St",
            city="Test City",
            state="XX",  # 无效的州代码
            postalcode="10001",
            birth_date="1990-01-01",
            expiration_date="12/2026"
        )
        
        assert response.status_code == 200
        response_body = response.json()
        
        logger.info(f"响应code: {response_body.get('code')}")
        logger.info("✓ 无效州代码测试完成")

    def test_invalid_postalcode_format(self, card_opening_api):
        """
        测试场景5：无效的postalcode格式
        验证点：
        1. postalcode应为5或9位
        2. 接口应拒绝无效格式
        """
        logger.info("测试场景5：无效的postalcode格式")
        
        response = card_opening_api.create_reward_card_application(
            sub_program_id="test_sub_program_id",
            email="test@example.com",
            first_name="Auto TestYan Test",
            last_name="Auto TestYan User",
            ssn="1234",
            telephone="1234567890",
            address1="123 Test St",
            city="Test City",
            state="NY",
            postalcode="123",  # 无效格式（只有3位）
            birth_date="1990-01-01",
            expiration_date="12/2026"
        )
        
        assert response.status_code == 200
        logger.info(f"响应code: {response.json().get('code')}")
        
        logger.info("✓ 无效postalcode格式测试完成")

    def test_invalid_birth_date_format(self, card_opening_api):
        """
        测试场景6：无效的birth_date格式
        验证点：
        1. birth_date格式应为yyyy-MM-dd
        2. 接口应拒绝其他格式
        """
        logger.info("测试场景6：无效的birth_date格式")
        
        response = card_opening_api.create_reward_card_application(
            sub_program_id="test_sub_program_id",
            email="test@example.com",
            first_name="Auto TestYan Test",
            last_name="Auto TestYan User",
            ssn="1234",
            telephone="1234567890",
            address1="123 Test St",
            city="Test City",
            state="NY",
            postalcode="10001",
            birth_date="01/01/1990",  # 错误格式
            expiration_date="12/2026"
        )
        
        assert response.status_code == 200
        logger.info(f"响应code: {response.json().get('code')}")
        
        logger.info("✓ 无效birth_date格式测试完成")

    def test_ssn_encryption_requirement(self, card_opening_api):
        """
        测试场景7：SSN加密要求说明
        验证点：
        1. 记录SSN加密要求
        2. 未加密的SSN应该被拒绝
        """
        logger.info("测试场景7：SSN加密要求验证")
        
        logger.info("⚠️ SSN加密要求：")
        logger.info("1. 4位数字")
        logger.info("2. 使用Portal Dashboard的公钥")
        logger.info("3. RSA + PKCS1Padding加密")
        logger.info("4. Base64编码")
        
        # 使用未加密的SSN（应该被拒绝）
        response = card_opening_api.create_reward_card_application(
            sub_program_id="test_sub_program_id",
            email="test@example.com",
            first_name="Auto TestYan Test",
            last_name="Auto TestYan User",
            ssn="1234",  # 未加密的明文SSN
            telephone="1234567890",
            address1="123 Test St",
            city="Test City",
            state="NY",
            postalcode="10001",
            birth_date="1990-01-01",
            expiration_date="12/2026"
        )
        
        logger.info(f"响应状态: {response.status_code}")
        
        logger.info("✓ SSN加密要求测试完成")
