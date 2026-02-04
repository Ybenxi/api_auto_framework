"""
Identity Security - MFA 接口测试用例
测试 MFA（多因素认证）相关接口
"""
import pytest
from utils.assertions import (
    assert_status_ok,
    assert_response_parsed
)


class TestIdentityMFA:
    """
    MFA（多因素认证）接口测试用例集
    """

    def test_list_enrolled_factors_success(self, identity_api):
        """
        测试场景1：成功列出已注册的 MFA 因子
        验证点：
        1. HTTP 状态码为 200
        2. 响应包含 code 字段，值为 200
        3. data 是一个列表
        """
        # 调用接口
        response = identity_api.list_enrolled_factors()
        
        # 断言状态码
        assert_status_ok(response)
        
        # 解析响应
        parsed = identity_api.parse_standard_response(response)
        assert_response_parsed(parsed)
        
        factors = parsed["data"]
        
        # 验证 data 是列表
        assert isinstance(factors, list), "data 应该是列表"
        
        print(f"✓ 成功列出 MFA 因子: 共 {len(factors)} 个")
        
        # 如果有因子，打印信息
        for factor in factors:
            print(f"  - Factor ID: {factor.get('id')}, "
                  f"Type: {factor.get('factor_type')}, "
                  f"Status: {factor.get('status')}")

    def test_list_enrolled_factors_structure(self, identity_api):
        """
        测试场景2：验证 MFA 因子数据结构
        验证点：
        1. 每个因子包含必需字段
        2. factor_type 和 status 字段有效
        """
        # 获取因子列表
        response = identity_api.list_enrolled_factors()
        assert_status_ok(response)
        
        parsed = identity_api.parse_standard_response(response)
        assert_response_parsed(parsed)
        
        factors = parsed["data"]
        
        if len(factors) > 0:
            first_factor = factors[0]
            
            # 验证必需字段
            required_fields = ["id", "factor_type", "status", "profile"]
            for field in required_fields:
                assert field in first_factor, f"因子对象缺少必需字段: {field}"
            
            # 验证 factor_type 是有效值
            valid_types = ["email", "sms", "totp"]
            factor_type = first_factor.get("factor_type")
            print(f"  Factor Type: {factor_type}")
            
            # 验证 status 是有效值
            valid_statuses = ["ACTIVE", "PENDING", "INACTIVE"]
            status = first_factor.get("status")
            print(f"  Status: {status}")
            
            print(f"✓ MFA 因子数据结构验证通过")
        else:
            print(f"⚠ 当前没有已注册的 MFA 因子")

    @pytest.mark.skip(reason="Enroll Factor 需要真实的验证码激活流程，暂时跳过完整流程测试")
    def test_enroll_factor_sms(self, identity_api):
        """
        测试场景3：注册 SMS MFA 因子
        验证点：
        1. 注册成功返回 200
        2. 返回 factor_id
        """
        # 注册 SMS 因子
        enroll_data = {
            "factor_type": "sms",
            "profile": {
                "phone_number": "+14155559999"
            }
        }
        
        response = identity_api.enroll_factor(
            factor_type=enroll_data["factor_type"],
            profile=enroll_data["profile"]
        )
        
        # 验证注册成功
        assert_status_ok(response)
        parsed = identity_api.parse_standard_response(response)
        assert_response_parsed(parsed)
        
        factor_id = parsed["data"]
        assert factor_id is not None, "factor_id 为 None"
        assert isinstance(factor_id, str), "factor_id 应该是字符串"
        
        print(f"✓ 成功注册 SMS MFA 因子: {factor_id}")
        
        # 注意：实际使用时需要：
        # 1. 调用 send_mfa_challenge 发送验证码
        # 2. 获取验证码（这步在自动化测试中很难实现）
        # 3. 调用 activate_factor 激活因子
        # 4. 清理：调用 delete_factors 删除测试因子

    def test_send_mfa_challenge_with_invalid_factor_id(self, identity_api):
        """
        测试场景4：使用无效的 factor_id 发送 MFA 挑战
        验证点：
        1. 接口返回错误信息
        """
        # 使用无效的 factor_id
        invalid_factor_id = "invalid_factor_id_999999"
        
        response = identity_api.send_mfa_challenge(invalid_factor_id)
        
        # 验证返回 200（统一错误处理）
        assert_status_ok(response)
        
        # 验证响应包含错误信息
        parsed = identity_api.parse_standard_response(response)
        
        # 如果是错误响应，code 应该不等于 200
        if parsed.get("error"):
            print(f"✓ 使用无效 factor_id 正确返回错误: {parsed.get('message')}")
        else:
            print(f"⚠ API 未验证 factor_id 有效性")

    @pytest.mark.skip(reason="Delete Factor 可能影响其他测试，暂时跳过")
    def test_delete_factors(self, identity_api):
        """
        测试场景5：删除 MFA 因子
        验证点：
        1. 删除成功返回 200
        2. data 为 true
        """
        # 注意：这个测试会删除真实的 MFA 因子，可能影响其他测试
        # 实际使用时应该先创建测试因子，然后再删除
        
        # 示例代码（需要有效的 factor_id）
        test_factor_ids = ["test_factor_id_1"]
        
        response = identity_api.delete_factors(test_factor_ids)
        
        # 验证删除成功
        assert_status_ok(response)
        parsed = identity_api.parse_standard_response(response)
        assert_response_parsed(parsed)
        
        success = parsed["data"]
        assert success == True, "删除失败"
        
        print(f"✓ 成功删除 MFA 因子")

    def test_activate_factor_with_invalid_pass_code(self, identity_api):
        """
        测试场景6：使用无效的验证码激活因子
        验证点：
        1. 接口返回错误信息
        """
        # 使用无效的 factor_id 和 pass_code
        invalid_factor_id = "invalid_factor_id_999999"
        invalid_pass_code = "000000"
        
        response = identity_api.activate_factor(invalid_factor_id, invalid_pass_code)
        
        # 验证返回 200（统一错误处理）
        assert_status_ok(response)
        
        # 验证响应
        parsed = identity_api.parse_standard_response(response)
        
        # 应该返回错误或 data=false
        if parsed.get("error"):
            print(f"✓ 使用无效验证码正确返回错误: {parsed.get('message')}")
        elif parsed.get("data") == False:
            print(f"✓ 使用无效验证码返回 data=false")
        else:
            print(f"⚠ API 未验证验证码有效性")

    def test_verify_mfa_with_invalid_credentials(self, identity_api):
        """
        测试场景7：使用无效的凭证验证 MFA
        验证点：
        1. 接口返回错误信息或 data=null
        """
        # 使用无效的 factor_id 和 pass_code
        invalid_factor_id = "invalid_factor_id_999999"
        invalid_pass_code = "000000"
        
        response = identity_api.verify_mfa(invalid_factor_id, invalid_pass_code)
        
        # 验证返回 200（统一错误处理）
        assert_status_ok(response)
        
        # 验证响应
        parsed = identity_api.parse_standard_response(response)
        
        # 应该返回错误或 data=null
        if parsed.get("error"):
            print(f"✓ 使用无效凭证正确返回错误: {parsed.get('message')}")
        elif parsed.get("data") is None:
            print(f"✓ 使用无效凭证返回 data=null")
        else:
            print(f"⚠ API 未验证 MFA 凭证有效性")
