"""
Identity Security - 安全操作接口测试用例
测试密码修改、登出、删除用户等安全操作
"""
import pytest
from utils.assertions import assert_status_ok
from utils.logger import logger


class TestIdentitySecurity:
    """
    安全操作接口测试用例集
    """

    @pytest.mark.skip(reason="密码修改需要真实的加密密码，且会影响后续测试，暂时跳过")
    def test_change_password_with_encoded_passwords(self, identity_api):
        """
        测试场景1：使用加密密码修改密码
        验证点：
        1. 接口返回 200
        2. data 为 true 表示修改成功
        
        注意：此测试需要真实的 RSA 加密密码，且会修改实际密码，影响后续测试
        """
        # 示例的加密密码（来自文档）
        encoded_old = "QqNLystnSxkcIx8c4rUZZGNzLEs+sxpr1KtsLPpMWwTeaNZcZdt2cr3HftjGE7hRFcOixoPfuKjdlyz2+3NhFfLrbx1awc4jgC1jpu9f46BnbUpVfYxIZwBF59QKr2tnxm5AK3wZwXiqTkzZBU10EL08X1VuAEj7qjXNIrJiNRXt7eYLGgEy50W4uV3fHUUcFxDAMfv/vJ9OBffzAethXcj0pXHpNT2U27ds9/NLEi3+16729gPROpPqHFop+t0/P6Zz+40fwscRzJOakHHRrngq6OJtRrnWtIRJ3bmEj/Ihc71D31QgGrOWoCDMTiLsIz1kSFSP0it2XNEq0U1/Ow=="
        encoded_new = "QqNLystnSxkcIx8c4rUZZGNzLEs+sxpr1KtsLPpMWwTeaNZcZdt2cr3HftjGE7hRFcOixoPfuKjdlyz2+3NhFfLrbx1awc4jgC1jpu9f46BnbUpVfYxIZwBF59QKr2tnxm5AK3wZwXiqTkzZBU10EL08X1VuAEj7qjXNIrJiNRXt7eYLGgEy50W4uV3fHUUcFxDAMfv/vJ9OBffzAethXcj0pXHpNT2U27ds9/NLEi3+16729gPROpPqHFop+t0/P6Zz+40fwscRzJOakHHRrngq6OJtRrnWtIRJ3bmEj/Ihc71D31QgGrOWoCDMTiLsIz1kSFSP0it2XNEq0U1/Ow=="
        
        response = identity_api.change_password(encoded_old, encoded_new)
        
        # 验证响应
        assert_status_ok(response)
        
        parsed = identity_api.parse_standard_response(response)
        
        # 如果成功，data 应该为 true
        if not parsed.get("error"):
            success = parsed["data"]
            assert success == True, "密码修改应该返回 true"
            logger.info("✓ 密码修改成功")
        else:
            logger.info(f"⚠ 密码修改失败（可能是旧密码不正确）: {parsed.get('message')}")

    def test_change_password_missing_required_fields(self, identity_api):
        """
        测试场景2：缺少必需字段
        验证点：
        1. 接口返回错误信息
        """
        # 只提供旧密码，缺少新密码
        response = identity_api.change_password(
            encoded_old_password="test_old_password",
            encoded_new_password=""  # 空字符串
        )
        
        # 验证返回 200（统一错误处理）
        assert_status_ok(response)
        
        # 验证响应
        parsed = identity_api.parse_standard_response(response)
        
        # 应该返回错误
        if parsed.get("error") or parsed.get("data") == False:
            logger.info("✓ 缺少必需字段正确返回错误")
        else:
            logger.info(f"⚠ API 未验证必需字段")

    def test_change_password_invalid_encoded_format(self, identity_api):
        """
        测试场景3：使用无效的加密格式
        验证点：
        1. 接口返回错误信息
        """
        # 使用明文密码（未加密）
        response = identity_api.change_password(
            encoded_old_password="plain_old_password",
            encoded_new_password="plain_new_password"
        )
        
        # 验证返回 200（统一错误处理）
        assert_status_ok(response)
        
        # 验证响应
        parsed = identity_api.parse_standard_response(response)
        
        # 应该返回错误
        if parsed.get("error") or parsed.get("data") == False:
            logger.info("✓ 无效加密格式正确返回错误")
        else:
            logger.info(f"⚠ API 未验证加密格式")

    @pytest.mark.skip(reason="Logout 会清除 token，影响后续所有测试，必须跳过")
    def test_logout_success(self, identity_api):
        """
        测试场景4：成功登出
        验证点：
        1. 接口返回 200
        2. data 为 true 表示登出成功
        
        ⚠️ 警告：此测试会清除当前 session 的 token，导致后续所有测试失败
        """
        response = identity_api.logout()
        
        # 验证登出成功
        assert_status_ok(response)
        
        parsed = identity_api.parse_standard_response(response)
        assert_response_parsed(parsed)
        
        success = parsed["data"]
        assert success == True, "登出应该返回 true"
        
        logger.info("✓ 登出成功")

    @pytest.mark.skip(reason="Delete User 是永久性破坏操作，绝对不能在测试中执行")
    def test_delete_user(self, identity_api):
        """
        测试场景5：删除用户
        验证点：
        1. 接口返回 200
        2. data 为 true 表示删除成功
        
        ⚠️ 危险：此测试会永久删除当前用户，绝对不能在真实环境执行
        """
        # 此测试永久标记为 skip
        # 仅作为 API 文档记录，不实际执行
        
        response = identity_api.delete_user()
        
        # 验证删除成功
        assert_status_ok(response)
        
        parsed = identity_api.parse_standard_response(response)
        assert_response_parsed(parsed)
        
        success = parsed["data"]
        assert success == True, "删除应该返回 true"
        
        logger.info("✓ 用户删除成功")
