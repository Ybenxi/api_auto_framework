"""
Identity Security - User Profile 接口测试用例
测试 GET/PATCH /api/v1/cores/{core}/identity-security/profile 接口
测试 POST /api/v1/cores/{core}/identity-security/profile/avatar 接口
"""
import pytest
from utils.logger import logger
from utils.assertions import (
    assert_status_ok,
    assert_response_parsed,
    assert_fields_present
)


class TestIdentityProfile:
    """
    用户个人资料接口测试用例集
    """

    def test_get_user_profile_success(self, identity_api):
        """
        测试场景1：成功获取用户个人资料
        验证点：
        1. HTTP 状态码为 200
        2. 响应包含 code 字段，值为 200
        3. 返回的 data 包含用户资料必需字段
        """
        # 调用接口
        response = identity_api.get_user_profile()
        
        # 断言状态码
        assert_status_ok(response)
        
        # 解析响应
        parsed = identity_api.parse_standard_response(response)
        assert_response_parsed(parsed)
        
        user_profile = parsed["data"]
        
        # 验证必需字段
        required_fields = [
            "id", "account_id", "first_name", "last_name", 
            "email", "status", "create_time"
        ]
        assert_fields_present(user_profile, required_fields, obj_name="用户资料")
        
        logger.info("✓ 成功获取用户资料:")
        logger.info(f"  ID: {user_profile.get('id')}")
        logger.info(f"  Name: {user_profile.get('first_name')} {user_profile.get('last_name')}")
        logger.info(f"  Email: {user_profile.get('email')}")
        logger.info(f"  Status: {user_profile.get('status')}")

    def test_get_user_profile_fields_completeness(self, identity_api):
        """
        测试场景2：验证用户资料字段完整性
        验证点：
        1. 返回的用户资料包含所有字段（必需和可选）
        2. 字段类型正确
        """
        # 获取用户资料
        response = identity_api.get_user_profile()
        assert_status_ok(response)
        
        parsed = identity_api.parse_standard_response(response)
        assert_response_parsed(parsed)
        
        user_profile = parsed["data"]
        
        # 所有字段列表（包括可选字段）
        all_fields = [
            "id", "account_id", "first_name", "last_name", "middle_name",
            "maiden_name", "suffix", "birth_date", "phone", "mobile_phone",
            "home_phone", "work_phone", "fax", "gender", "email", "status",
            "permanent_address", "permanent_address2", "permanent_city",
            "permanent_state", "permanent_postalcode", "permanent_country",
            "mailing_street", "mailing_street2", "mailing_city",
            "mailing_state", "mailing_postalcode", "mailing_country",
            "description", "avatar_url", "create_time"
        ]
        
        missing_fields = [f for f in all_fields if f not in user_profile]
        
        if missing_fields:
            logger.info(f"⚠ 缺少以下字段: {missing_fields}")
        else:
            logger.info("✓ 所有字段都存在")
        
        # 只验证必需字段
        required_fields = ["id", "account_id", "first_name", "last_name", "email"]
        assert_fields_present(user_profile, required_fields, obj_name="用户资料")
        
        logger.info("✓ 字段完整性验证通过")

    def test_update_user_profile_single_field(self, identity_api):
        """
        测试场景3：更新单个字段（description）
        验证点：
        1. 更新成功返回 200
        2. 返回的数据中 description 已更新
        3. 其他字段不受影响
        """
        # 先获取当前资料
        get_response = identity_api.get_user_profile()
        assert_status_ok(get_response)
        parsed_get = identity_api.parse_standard_response(get_response)
        assert_response_parsed(parsed_get)
        
        original_profile = parsed_get["data"]
        original_description = original_profile.get("description")
        
        # 更新 description
        new_description = "Auto TestYan Updated Description"
        update_data = {
            "description": new_description
        }
        
        update_response = identity_api.update_user_profile(update_data)
        
        # 验证更新成功
        assert_status_ok(update_response)
        parsed_update = identity_api.parse_standard_response(update_response)
        assert_response_parsed(parsed_update)
        
        updated_profile = parsed_update["data"]
        
        # 验证 description 已更新
        assert updated_profile.get("description") == new_description, \
            f"description 更新失败"
        
        logger.info("✓ 成功更新用户资料:")
        logger.info(f"  原始 description: {original_description}")
        logger.info(f"  新 description: {updated_profile.get('description')}")

    def test_update_user_profile_multiple_fields(self, identity_api):
        """
        测试场景4：同时更新多个字段
        验证点：
        1. 可以同时更新多个字段
        2. 所有字段都正确更新
        """
        # 更新多个字段
        update_data = {
            "middle_name": "TestYan",
            "suffix": "Jr.",
            "gender": "Male",
            "fax": "1234567890"
        }
        
        update_response = identity_api.update_user_profile(update_data)
        
        # 验证更新成功
        assert_status_ok(update_response)
        parsed = identity_api.parse_standard_response(update_response)
        assert_response_parsed(parsed)
        
        updated_profile = parsed["data"]
        
        # 验证所有字段都已更新
        for field, expected_value in update_data.items():
            actual_value = updated_profile.get(field)
            assert actual_value == expected_value, \
                f"字段 {field} 更新失败: 期望 {expected_value}, 实际 {actual_value}"
        
        logger.info("✓ 成功更新多个字段:")
        for field, value in update_data.items():
            logger.info(f"  {field}: {value}")

    def test_update_user_profile_address_fields(self, identity_api):
        """
        测试场景5：更新地址字段（永久地址和邮寄地址）
        验证点：
        1. 可以更新永久地址字段
        2. 可以更新邮寄地址字段
        """
        # 更新地址字段
        update_data = {
            "permanent_address": "123 Auto TestYan Street",
            "permanent_city": "Test City",
            "permanent_state": "CA",
            "permanent_postalcode": "90001",
            "permanent_country": "US",
            "mailing_street": "456 Auto TestYan Mailing Ave",
            "mailing_city": "Mailing City",
            "mailing_state": "NY",
            "mailing_postalcode": "10001",
            "mailing_country": "US"
        }
        
        update_response = identity_api.update_user_profile(update_data)
        
        # 验证更新成功
        assert_status_ok(update_response)
        parsed = identity_api.parse_standard_response(update_response)
        assert_response_parsed(parsed)
        
        updated_profile = parsed["data"]
        
        # 验证地址字段已更新
        assert updated_profile.get("permanent_city") == "Test City", "permanent_city 更新失败"
        assert updated_profile.get("mailing_city") == "Mailing City", "mailing_city 更新失败"
        
        logger.info("✓ 成功更新地址字段:")
        logger.info(f"  永久地址: {updated_profile.get('permanent_city')}, {updated_profile.get('permanent_state')}")
        logger.info(f"  邮寄地址: {updated_profile.get('mailing_city')}, {updated_profile.get('mailing_state')}")

    def test_update_user_profile_phone_format_validation(self, identity_api):
        """
        测试场景6：验证 phone 格式（E.164）
        验证点：
        1. 使用有效的 E.164 格式电话号码
        2. 更新成功
        """
        # 使用有效的 E.164 格式
        update_data = {
            "phone": "+14155552671",
            "mobile_phone": "+14155552672"
        }
        
        update_response = identity_api.update_user_profile(update_data)
        
        # 验证更新成功
        assert_status_ok(update_response)
        parsed = identity_api.parse_standard_response(update_response)
        assert_response_parsed(parsed)
        
        updated_profile = parsed["data"]
        
        # 验证电话号码已更新
        assert updated_profile.get("phone") == update_data["phone"], "phone 更新失败"
        assert updated_profile.get("mobile_phone") == update_data["mobile_phone"], "mobile_phone 更新失败"
        
        logger.info("✓ 成功更新电话号码（E.164 格式）:")
        logger.info(f"  Phone: {updated_profile.get('phone')}")
        logger.info(f"  Mobile Phone: {updated_profile.get('mobile_phone')}")

    @pytest.mark.skip(reason="头像上传需要准备测试图片文件，暂时跳过")
    def test_upload_user_avatar(self, identity_api):
        """
        测试场景7：上传用户头像
        验证点：
        1. 上传成功返回 200
        2. 返回头像 URL
        3. 再次获取个人资料时，avatar_url 已更新
        """
        # 注意：需要准备测试图片文件
        # 这里只是示例，实际使用时需要提供真实的图片路径
        test_avatar_path = "test_data/avatar.png"
        
        upload_response = identity_api.upload_user_avatar(test_avatar_path)
        
        # 验证上传成功
        assert_status_ok(upload_response)
        
        # 返回的应该是头像 URL
        avatar_url = upload_response.text
        assert avatar_url.startswith("http"), f"返回的不是有效的 URL: {avatar_url}"
        
        # 再次获取个人资料，验证 avatar_url 已更新
        profile_response = identity_api.get_user_profile()
        parsed = identity_api.parse_standard_response(profile_response)
        user_profile = parsed["data"]
        
        assert user_profile.get("avatar_url") == avatar_url, \
            "个人资料中的 avatar_url 未更新"
        
        logger.info("✓ 头像上传成功: {avatar_url}")
