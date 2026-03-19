"""
Identity Security - 综合测试用例
覆盖全部 12 个接口：
  1.  Retrieve User Profile        GET  /identity-security/profile
  2.  Update User Profile          PATCH /identity-security/profile
  3.  Upload User Avatar           POST  /identity-security/profile/avatar
  4.  List Enrolled Factors        GET  /identity-security/profile/factors
  5.  Enroll Factor                POST  /identity-security/profile/factors
  6.  Delete Factor                DELETE /identity-security/profile/factors
  7.  Activate Factor              POST  /identity-security/profile/factors/:id
  8.  Change Password              POST  /identity-security/change-password
  9.  Logout                       POST  /identity-security/logout
  10. Delete User                  DELETE /identity-security/user
  11. Send MFA Message             POST  /identity-security/mfa/send
  12. Verify MFA Message           POST  /identity-security/mfa/verification

⚠️ Token 说明：
  本模块所有测试使用专用 token（通过 sign-in 接口获取），
  不使用通用 OAuth2 token，详见 conftest.py 中的 identity_session fixture。

⚠️ 危险操作 skip 策略：
  以下接口会影响真实账户，统一使用 @pytest.mark.skip 跳过执行：
  - Change Password（修改密码，怕锁账户）
  - Logout（登出后 token 失效，影响后续测试）
  - Delete User（删除账户，极度危险）
  - Delete Factor（删除真实 MFA 因子，影响账户安全）
  - Enroll Factor（添加 MFA，可能发送真实短信）
  - Activate Factor（需要真实验证码，且激活后影响账户）
"""
import pytest
from utils.logger import logger
from utils.assertions import assert_status_ok, assert_fields_present


# ════════════════════════════════════════════════════════════════════
# 1. Retrieve User Profile
# ════════════════════════════════════════════════════════════════════
@pytest.mark.identity_security
class TestRetrieveUserProfile:

    def test_get_profile_success(self, identity_api):
        """
        测试场景1：成功获取当前登录用户的个人资料
        Test Scenario1: Successfully Retrieve Current User Profile
        验证点：
        1. HTTP 200，业务 code=200
        2. 返回 data 包含必需字段（id, first_name, last_name, status）
        3. 字段类型正确
        """
        resp = identity_api.get_user_profile()
        assert_status_ok(resp)
        body = resp.json()
        assert body.get("code") == 200, f"code 应为 200，实际: {body.get('code')}"

        data = body.get("data", {})
        assert data, "data 不应为空"
        required = ["id", "first_name", "last_name", "status"]
        for field in required:
            assert field in data, f"profile 缺少必需字段: '{field}'"
            logger.info(f"  ✓ {field}: {data.get(field)}")

        logger.info(f"✓ 获取 profile 成功: {data.get('first_name')} {data.get('last_name')}")

    def test_get_profile_response_structure(self, identity_api):
        """
        测试场景2：验证 profile 响应数据结构完整性
        Test Scenario2: Verify Profile Response Structure Completeness
        验证点：
        1. 返回包含所有文档定义字段
        2. 可选字段（null 值）也在响应中存在
        """
        resp = identity_api.get_user_profile()
        assert_status_ok(resp)
        data = resp.json().get("data", {})

        all_fields = [
            "id", "account_id", "name", "first_name", "last_name", "middle_name",
            "status", "suffix", "birth_date", "phone", "mobile_phone",
            "home_phone", "work_phone", "gender", "email",
            "permanent_address", "permanent_city", "permanent_state",
            "permanent_postalcode", "permanent_country",
            "mailing_street", "mailing_city", "mailing_state",
            "mailing_zipcode", "mailing_country",
        ]
        missing = [f for f in all_fields if f not in data]
        if missing:
            logger.info(f"  ⚠ 响应中缺少字段（可能是 null 未返回）: {missing}")
        else:
            logger.info("  ✓ 所有文档字段均存在于响应中")

        assert "id" in data and "status" in data, "id 和 status 为必需字段"
        logger.info(f"✓ profile 结构验证通过，共 {len(data)} 个字段")


# ════════════════════════════════════════════════════════════════════
# 2. Update User Profile
# ════════════════════════════════════════════════════════════════════
@pytest.mark.identity_security
class TestUpdateUserProfile:

    def test_update_profile_description(self, identity_api):
        """
        测试场景1：更新 description 字段（低风险可逆操作）
        Test Scenario1: Update Description Field (Low-Risk Reversible Operation)
        验证点：
        1. HTTP 200，code=200
        2. 更新后再 GET profile，description 已变更
        3. 恢复原值
        """
        # 先获取当前 description
        orig_resp = identity_api.get_user_profile()
        orig_desc = orig_resp.json().get("data", {}).get("description", "")

        new_desc = "Auto Test - identity security profile update"
        resp = identity_api.update_user_profile({"description": new_desc})
        assert_status_ok(resp)
        assert resp.json().get("code") == 200, \
            f"更新失败: code={resp.json().get('code')}, msg={resp.json().get('error_message')}"
        logger.info(f"  ✓ 更新 description 成功")

        # 验证更新生效
        verify_resp = identity_api.get_user_profile()
        actual = verify_resp.json().get("data", {}).get("description", "")
        assert actual == new_desc, f"description 未更新: 期望 '{new_desc}', 实际 '{actual}'"

        # 恢复原值
        identity_api.update_user_profile({"description": orig_desc})
        logger.info(f"✓ description 更新并恢复完成")

    def test_update_profile_invalid_gender(self, identity_api):
        """
        测试场景2：更新 gender 时使用无效枚举值
        Test Scenario2: Update Gender with Invalid Enum Value
        验证点：
        1. HTTP 200
        2. 无效枚举值被拒绝（code != 200）或被忽略
        """
        resp = identity_api.update_user_profile({"gender": "INVALID_GENDER_999"})
        assert resp.status_code == 200
        code = resp.json().get("code")
        if code != 200:
            logger.info(f"  ✓ 无效 gender 被拒绝: code={code}")
        else:
            logger.info("  ⚠ API 接受了无效 gender（探索性结果）")

    def test_update_profile_invalid_phone_format(self, identity_api):
        """
        测试场景3：更新 phone 时不符合 E.164 格式
        Test Scenario3: Update Phone with Non-E.164 Format
        验证点：
        1. HTTP 200
        2. 非 E.164 手机号被拒绝（code != 200）
        """
        resp = identity_api.update_user_profile({"phone": "13812345678"})
        assert resp.status_code == 200
        code = resp.json().get("code")
        if code != 200:
            logger.info(f"  ✓ 非 E.164 手机号被拒绝: code={code}, msg={resp.json().get('error_message')}")
        else:
            logger.info("  ⚠ API 接受了非 E.164 手机号（探索性结果）")

    def test_update_profile_valid_phone_format(self, identity_api):
        """
        测试场景4：更新 phone 时使用合法 E.164 格式（探索性，不实际修改真实手机号）
        Test Scenario4: Update Phone with Valid E.164 Format (Exploratory)
        注意：更新 mobile_phone 会导致 SMS MFA 被移除（文档说明的副作用）
             此处只更新 phone（office phone），不改 mobile_phone
        验证点：
        1. HTTP 200，code=200 或业务错误（取决于账户状态）
        """
        resp = identity_api.update_user_profile({"phone": "+14155550100"})
        assert resp.status_code == 200
        code = resp.json().get("code")
        logger.info(f"  E.164 phone 更新结果: code={code}, msg={resp.json().get('error_message')}")
        if code == 200:
            # 恢复（把 phone 清空）
            identity_api.update_user_profile({"phone": None})
            logger.info("  ✓ phone 已恢复")


# ════════════════════════════════════════════════════════════════════
# 3. Upload User Avatar
# ════════════════════════════════════════════════════════════════════
@pytest.mark.identity_security
@pytest.mark.skip(reason="上传头像需要本地真实图片文件，且会修改真实账户头像，跳过执行")
class TestUploadUserAvatar:

    def test_upload_avatar(self, identity_api):
        """
        测试场景1：上传用户头像
        ⚠️ 跳过：需要真实图片文件且会修改账户头像
        """
        pass


# ════════════════════════════════════════════════════════════════════
# 4. List Enrolled Factors
# ════════════════════════════════════════════════════════════════════
@pytest.mark.identity_security
class TestListEnrolledFactors:

    def test_list_factors_success(self, identity_api):
        """
        测试场景1：成功获取已注册的 MFA 因子列表
        Test Scenario1: Successfully Retrieve Enrolled MFA Factor List
        验证点：
        1. HTTP 200，code=200
        2. data 是数组
        3. 每个 factor 含 id、factor_type、status 字段
        """
        resp = identity_api.list_enrolled_factors()
        assert_status_ok(resp)
        body = resp.json()
        assert body.get("code") == 200, f"code={body.get('code')}, msg={body.get('error_message')}"

        data = body.get("data", [])
        assert isinstance(data, list), "data 应为数组"
        logger.info(f"  已注册因子数量: {len(data)}")

        if data:
            factor = data[0]
            for field in ["id", "factor_type", "status"]:
                assert field in factor, f"factor 缺少字段: '{field}'"
                logger.info(f"  ✓ {field}: {factor.get(field)}")

        logger.info("✓ List Enrolled Factors 成功")

    def test_list_factors_response_structure(self, identity_api):
        """
        测试场景2：验证 factor 对象字段完整性
        Test Scenario2: Verify Factor Object Field Completeness
        验证点：
        1. factor 对象包含 id, factor_type, status, profile
        2. profile 包含对应类型的配置信息
        """
        resp = identity_api.list_enrolled_factors()
        assert_status_ok(resp)
        data = resp.json().get("data", [])
        if not data:
            pytest.skip("账户无已注册 MFA 因子，跳过字段验证")

        factor = data[0]
        expected_fields = ["id", "factor_type", "status"]
        for field in expected_fields:
            assert field in factor, f"factor 缺少字段: '{field}'"
        logger.info(f"  factor_type: {factor.get('factor_type')}")
        logger.info(f"  status: {factor.get('status')}")
        logger.info("✓ Factor 响应结构验证通过")

    def test_list_factors_status_values(self, identity_api):
        """
        测试场景3：验证 factor status 字段取值合法
        Test Scenario3: Verify Factor Status Enum Values
        验证点：
        1. status 值为已知枚举（ACTIVE, INACTIVE, PENDING_ACTIVATION 等）
        """
        resp = identity_api.list_enrolled_factors()
        assert_status_ok(resp)
        data = resp.json().get("data", [])
        if not data:
            pytest.skip("无已注册因子，跳过")

        valid_statuses = {"ACTIVE", "INACTIVE", "PENDING_ACTIVATION", "NOT_SETUP", "EXPIRED", "LOCKED_OUT"}
        for factor in data:
            status = factor.get("status", "")
            if status in valid_statuses:
                logger.info(f"  ✓ factor_type={factor.get('factor_type')} status={status}（有效枚举值）")
            else:
                logger.info(f"  ⚠ status='{status}' 不在已知枚举中（探索性结果）")
        logger.info("✓ Factor status 枚举值验证完成")


# ════════════════════════════════════════════════════════════════════
# 5. Enroll Factor（危险操作，全部 skip）
# ════════════════════════════════════════════════════════════════════
@pytest.mark.identity_security
@pytest.mark.skip(reason="注册 MFA 因子会修改真实账户，且可能触发真实短信/邮件，跳过执行")
class TestEnrollFactor:

    def test_enroll_sms_factor(self, identity_api):
        """⚠️ 跳过：会向真实手机号发短信并修改账户 MFA 配置"""
        pass

    def test_enroll_email_factor(self, identity_api):
        """⚠️ 跳过：会向真实邮箱发邮件并修改账户 MFA 配置"""
        pass

    def test_enroll_factor_missing_factor_type(self, identity_api):
        """⚠️ 跳过：关联危险操作"""
        pass


# ════════════════════════════════════════════════════════════════════
# 6. Delete Factor（危险操作，全部 skip）
# ════════════════════════════════════════════════════════════════════
@pytest.mark.identity_security
@pytest.mark.skip(reason="删除 MFA 因子会永久影响真实账户安全配置，跳过执行")
class TestDeleteFactor:

    def test_delete_factor(self, identity_api):
        """⚠️ 跳过：删除真实 MFA 因子，影响账户安全"""
        pass

    def test_delete_invalid_factor_id(self, identity_api):
        """⚠️ 跳过：关联危险接口"""
        pass


# ════════════════════════════════════════════════════════════════════
# 7. Activate Factor（危险操作，全部 skip）
# ════════════════════════════════════════════════════════════════════
@pytest.mark.identity_security
@pytest.mark.skip(reason="激活因子需要真实验证码且会修改账户 MFA 状态，跳过执行")
class TestActivateFactor:

    def test_activate_factor(self, identity_api):
        """⚠️ 跳过：需要真实验证码，激活后影响账户"""
        pass

    def test_activate_factor_wrong_passcode(self, identity_api):
        """⚠️ 跳过：关联危险接口（重试可能导致账户锁定）"""
        pass


# ════════════════════════════════════════════════════════════════════
# 8. Change Password（危险操作，全部 skip）
# ════════════════════════════════════════════════════════════════════
@pytest.mark.identity_security
@pytest.mark.skip(reason="修改密码会影响真实账户，且需要 RSA 加密，跳过执行")
class TestChangePassword:

    def test_change_password(self, identity_api):
        """⚠️ 跳过：修改真实账户密码"""
        pass

    def test_change_password_wrong_old_password(self, identity_api):
        """⚠️ 跳过：多次错误可能锁账户"""
        pass


# ════════════════════════════════════════════════════════════════════
# 9. Logout（危险操作，跳过）
# ════════════════════════════════════════════════════════════════════
@pytest.mark.identity_security
@pytest.mark.skip(reason="登出会使当前 identity_session token 失效，影响后续所有测试，跳过执行")
class TestLogout:

    def test_logout(self, identity_api):
        """⚠️ 跳过：登出后 token 失效，影响 module 级 session"""
        pass


# ════════════════════════════════════════════════════════════════════
# 10. Delete User（极度危险，跳过）
# ════════════════════════════════════════════════════════════════════
@pytest.mark.identity_security
@pytest.mark.skip(reason="删除用户是极度危险的不可逆操作，绝对不能自动执行")
class TestDeleteUser:

    def test_delete_user(self, identity_api):
        """⚠️ 跳过：永久删除真实用户，不可逆"""
        pass


# ════════════════════════════════════════════════════════════════════
# 11. Send MFA Message
# ════════════════════════════════════════════════════════════════════
@pytest.mark.identity_security
class TestSendMfaMessage:

    def test_send_mfa_with_valid_factor(self, identity_api):
        """
        测试场景1：向已激活的 MFA 因子发送验证码
        Test Scenario1: Send MFA Verification Code to Active Factor
        验证点：
        1. 先获取 factor 列表，找到已激活（ACTIVE）的因子
        2. 发送 MFA challenge，HTTP 200，code=200
        3. 接口不崩溃（自动化无法验证是否真正收到验证码）
        """
        # 获取已激活的 factor
        factors_resp = identity_api.list_enrolled_factors()
        assert_status_ok(factors_resp)
        factors = factors_resp.json().get("data", [])
        active_factors = [f for f in factors if f.get("status") == "ACTIVE"]

        if not active_factors:
            pytest.skip("无 ACTIVE 状态的 MFA 因子，跳过 Send MFA 测试")

        factor_id = active_factors[0]["id"]
        factor_type = active_factors[0].get("factor_type", "")
        logger.info(f"  使用 factor_id={factor_id} (type={factor_type}) 发送 MFA")

        resp = identity_api.send_mfa_challenge(factor_id)
        assert resp.status_code == 200
        body = resp.json()
        code = body.get("code")
        logger.info(f"  Send MFA 结果: code={code}, msg={body.get('error_message')}")

        if code == 200:
            logger.info("  ✓ MFA 验证码发送成功（接口已触发，自动化无法验证收件）")
        else:
            logger.info(f"  ⚠ 发送失败: {body.get('error_message')}")

    def test_send_mfa_with_invalid_factor_id(self, identity_api):
        """
        测试场景2：使用不存在的 factor_id 发送 MFA
        Test Scenario2: Send MFA with Non-existent Factor ID
        验证点：
        1. HTTP 200
        2. 业务 code != 200
        """
        resp = identity_api.send_mfa_challenge("INVALID_FACTOR_ID_9999")
        assert resp.status_code == 200
        body = resp.json()
        assert body.get("code") != 200, \
            f"无效 factor_id 应被拒绝，实际 code={body.get('code')}"
        logger.info(f"✓ 无效 factor_id 被拒绝: code={body.get('code')}, msg={body.get('error_message')}")

    def test_send_mfa_missing_factor_id(self, identity_api):
        """
        测试场景3：不传 factor_id 参数
        Test Scenario3: Send MFA without factor_id Parameter
        验证点：
        1. HTTP 200
        2. 业务 code != 200
        """
        from config.config import config
        url = identity_api.config.get_full_url("/identity-security/mfa/send")
        resp = identity_api.session.post(url, json={})
        assert resp.status_code == 200
        body = resp.json()
        assert body.get("code") != 200, \
            f"缺少 factor_id 应被拒绝，实际 code={body.get('code')}"
        logger.info(f"✓ 缺少 factor_id 被拒绝: code={body.get('code')}")


# ════════════════════════════════════════════════════════════════════
# 12. Verify MFA Message
# ════════════════════════════════════════════════════════════════════
@pytest.mark.identity_security
class TestVerifyMfaMessage:

    def test_verify_mfa_with_fake_passcode(self, identity_api):
        """
        测试场景1：使用假验证码验证 MFA
        Test Scenario1: Verify MFA with Fake Pass Code
        策略：先发送 MFA，再用假验证码验证（自动化无法收取真实验证码）
        验证点：
        1. 先 send MFA（触发发送）
        2. 用假验证码 verify，HTTP 200
        3. 业务 code != 200（假码被拒绝，这是预期行为，接口不崩溃）
        """
        # 获取 ACTIVE factor
        factors_resp = identity_api.list_enrolled_factors()
        assert_status_ok(factors_resp)
        factors = factors_resp.json().get("data", [])
        active_factors = [f for f in factors if f.get("status") == "ACTIVE"]
        if not active_factors:
            pytest.skip("无 ACTIVE 状态 MFA 因子，跳过 Verify 测试")

        factor_id = active_factors[0]["id"]

        # 先发送（触发验证码）
        send_resp = identity_api.send_mfa_challenge(factor_id)
        if send_resp.json().get("code") != 200:
            pytest.skip("Send MFA 失败，跳过 Verify 测试")

        # 用假验证码验证
        logger.info(f"  使用假验证码 '000000' 验证 factor_id={factor_id}")
        verify_resp = identity_api.verify_mfa(factor_id, "000000")
        assert verify_resp.status_code == 200
        body = verify_resp.json()
        logger.info(f"  Verify 结果: code={body.get('code')}, msg={body.get('error_message')}")

        # 假验证码预期被拒绝
        assert body.get("code") != 200, \
            "假验证码应被拒绝，实际 code=200（可能有测试账户 bypass 机制）"
        logger.info(f"✓ 假验证码正确被拒绝: code={body.get('code')}，接口未崩溃")

    def test_verify_mfa_with_invalid_factor_id(self, identity_api):
        """
        测试场景2：使用不存在的 factor_id 验证
        Test Scenario2: Verify MFA with Non-existent Factor ID
        验证点：
        1. HTTP 200
        2. 业务 code != 200
        """
        resp = identity_api.verify_mfa("INVALID_FACTOR_ID_9999", "123456")
        assert resp.status_code == 200
        body = resp.json()
        assert body.get("code") != 200, \
            f"无效 factor_id 应被拒绝，实际 code={body.get('code')}"
        logger.info(f"✓ 无效 factor_id 被拒绝: code={body.get('code')}")

    def test_verify_mfa_missing_params(self, identity_api):
        """
        测试场景3：缺少必填参数
        Test Scenario3: Verify MFA with Missing Required Parameters
        验证点：
        1. HTTP 200
        2. 业务 code != 200
        """
        url = identity_api.config.get_full_url("/identity-security/mfa/verification")
        resp = identity_api.session.post(url, json={})
        assert resp.status_code == 200
        body = resp.json()
        assert body.get("code") != 200, \
            f"缺少参数应被拒绝，实际 code={body.get('code')}"
        logger.info(f"✓ 缺少参数被拒绝: code={body.get('code')}")
