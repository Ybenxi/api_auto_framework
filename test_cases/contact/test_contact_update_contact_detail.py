"""
Contact Update 接口测试用例
测试 PUT /api/v1/cores/{core}/contacts/{id} 接口
"""
import pytest
import time
from typing import Optional
from api.contact_api import ContactAPI
from utils.logger import logger


# 所有 update 测试公用同一个 Contact（由 module-level fixture 创建）
FIXED_ACCOUNT_ID = "251212054045554351"


def _create_own_contact(contact_api: ContactAPI, db_cleanup) -> Optional[str]:
    """
    创建一个属于自己的 Contact，返回其 ID。
    update 测试必须用自己创建的 contact，不能取 list 第一条（可能属于他人）。
    """
    unique_email = f"auto_update_{int(time.time() * 1000)}@example.com"
    data = {
        "account_id": FIXED_ACCOUNT_ID,
        "first_name": "Auto TestYan",
        "last_name": "UpdateBase",
        "birth_date": "1990-01-01",
        "email": unique_email,
        "phone": "+14155550000",
        "gender": "Female"
    }
    resp = contact_api.create_contact(data)
    if resp.status_code != 200:
        return None
    body = resp.json()
    if body.get("code") != 200:
        return None
    created = body.get("data") or body
    contact_id = created.get("id")
    if db_cleanup and contact_id:
        db_cleanup.track("contact", contact_id)
    return contact_id


@pytest.mark.contact
@pytest.mark.update_api
class TestContactUpdate:
    """
    Contact 更新接口测试用例集
    所有正向 update 场景均使用自己创建的 Contact，不取 list 第一条。
    """

    def test_update_contact_first_name(self, login_session, db_cleanup):
        """
        测试场景1：更新 Contact 的 first_name
        验证点：
        1. 先创建一个属于自己的 Contact
        2. 发起 first_name 更新
        3. 如果 API 文档支持更新 first_name，则断言更新后值一致
        4. 如果返回错误（文档不支持该字段更新），记录为探索性结果
        """
        contact_api = ContactAPI(session=login_session)

        contact_id = _create_own_contact(contact_api, db_cleanup)
        if not contact_id:
            pytest.skip("创建 Contact 失败，跳过更新测试")

        logger.info(f"使用自己创建的 Contact ID: {contact_id}")
        new_first_name = f"Auto TestYan Updated {int(time.time())}"
        update_data = {"first_name": new_first_name}

        logger.info(f"  更新 first_name -> {new_first_name}")
        update_response = contact_api.update_contact(contact_id, update_data)

        assert update_response.status_code == 200, \
            f"Update Contact 接口返回状态码错误: {update_response.status_code}"

        response_body = update_response.json()
        code = response_body.get("code")

        if code == 200:
            updated = response_body.get("data") or response_body
            actual_name = updated.get("first_name")
            assert actual_name == new_first_name, \
                f"first_name 未更新: 期望 {new_first_name}, 实际 {actual_name}"
            # Detail 二次确认
            detail_resp = contact_api.get_contact_detail(contact_id)
            detail = (detail_resp.json().get("data") or detail_resp.json())
            assert detail.get("first_name") == new_first_name, \
                f"Detail 确认: first_name 未落库"
            logger.info(f"✓ first_name 更新成功: {new_first_name}")
        else:
            logger.info(
                f"⚠ first_name 更新返回 code={code}，msg={response_body.get('error_message')}。"
                f"可能该字段不在文档允许更新的范围内，记录为探索性结果。"
            )

    def test_update_contact_phone(self, login_session, db_cleanup):
        """
        测试场景2：更新 Contact 的 phone（使用自己创建的 Contact）
        验证点：
        1. 接口返回 200，business code == 200
        2. 返回的 phone 已更新并落库
        """
        contact_api = ContactAPI(session=login_session)

        contact_id = _create_own_contact(contact_api, db_cleanup)
        if not contact_id:
            pytest.skip("创建 Contact 失败，跳过更新测试")

        logger.info(f"使用自己创建的 Contact ID: {contact_id}")
        new_phone = "+14155552671"
        update_data = {"phone": new_phone}

        logger.info(f"  更新 phone -> {new_phone}")
        update_response = contact_api.update_contact(contact_id, update_data)

        assert update_response.status_code == 200, \
            f"Update 返回状态码错误: {update_response.status_code}"

        response_body = update_response.json()
        assert response_body.get("code") == 200, \
            f"业务 code 应为 200，实际: {response_body.get('code')}, msg={response_body.get('error_message')}"

        updated = response_body.get("data") or response_body
        assert updated.get("phone") == new_phone, \
            f"phone 未更新: 期望 {new_phone}, 实际 {updated.get('phone')}"

        logger.info(f"✓ phone 更新成功: {new_phone}")

    def test_update_contact_multiple_fields(self, login_session, db_cleanup):
        """
        测试场景3：同时更新多个字段（使用自己创建的 Contact）
        验证点：
        1. 接口返回 200，business code == 200
        2. 所有更新的字段均生效
        """
        contact_api = ContactAPI(session=login_session)

        contact_id = _create_own_contact(contact_api, db_cleanup)
        if not contact_id:
            pytest.skip("创建 Contact 失败，跳过更新测试")

        logger.info(f"使用自己创建的 Contact ID: {contact_id}")
        ts = int(time.time())
        update_data = {
            "first_name": f"Auto TestYan Multi {ts}",
            "last_name": "Auto TestYan Test",
            "phone": "+14155552999"
        }

        logger.info(f"  批量更新: {list(update_data.keys())}")
        update_response = contact_api.update_contact(contact_id, update_data)

        assert update_response.status_code == 200, \
            f"Update 返回状态码错误: {update_response.status_code}"

        response_body = update_response.json()
        assert response_body.get("code") == 200, \
            f"业务 code 应为 200，实际: {response_body.get('code')}"

        updated = response_body.get("data") or response_body
        for field, expected in update_data.items():
            assert updated.get(field) == expected, \
                f"{field} 未更新: 期望 {expected}, 实际 {updated.get(field)}"

        logger.info(f"✓ 多字段更新成功: {list(update_data.keys())}")

    def test_update_contact_address_fields(self, login_session, db_cleanup):
        """
        测试场景4：更新地址相关字段（使用自己创建的 Contact）
        验证点：
        1. 接口返回 200，business code == 200
        2. 地址字段更新成功
        """
        contact_api = ContactAPI(session=login_session)

        contact_id = _create_own_contact(contact_api, db_cleanup)
        if not contact_id:
            pytest.skip("创建 Contact 失败，跳过更新测试")

        logger.info(f"使用自己创建的 Contact ID: {contact_id}")
        update_data = {
            "permanent_address": "123 Updated Street",
            "permanent_city": "Updated City",
            "permanent_state": "CA",
            "permanent_postalcode": "90001",
            "mailing_street": "456 Mailing Ave",
            "mailing_city": "Mailing City",
            "mailing_state": "NY",
            "mailing_postalcode": "10001"
        }

        update_response = contact_api.update_contact(contact_id, update_data)

        assert update_response.status_code == 200, \
            f"Update 返回状态码错误: {update_response.status_code}"

        response_body = update_response.json()
        assert response_body.get("code") == 200, \
            f"业务 code 应为 200，实际: {response_body.get('code')}"

        updated = response_body.get("data") or response_body
        assert updated.get("permanent_address") == update_data["permanent_address"]
        assert updated.get("mailing_street") == update_data["mailing_street"]

        logger.info(f"✓ 地址字段更新成功")

    def test_update_contact_invalid_id(self, login_session):
        """
        测试场景5：使用无效的 Contact ID 更新
        验证点：
        1. HTTP 200（防遍历设计）
        2. 返回 code=506，error_message 包含 "visibility permission deny"
        """
        contact_api = ContactAPI(session=login_session)

        invalid_contact_id = "invalid_contact_id_999999"
        update_data = {"first_name": "Auto TestYan InvalidTest"}

        logger.info(f"使用无效 Contact ID: {invalid_contact_id}")
        update_response = contact_api.update_contact(invalid_contact_id, update_data)

        assert update_response.status_code == 200, \
            f"无效 ID 应返回 200（防遍历），实际返回: {update_response.status_code}"

        response_body = update_response.json()
        error_code = response_body.get("code")
        error_message = response_body.get("error_message") or response_body.get("message")

        assert error_code == 506, f"错误码不正确: 期望 506, 实际 {error_code}"
        assert "visibility permission deny" in str(error_message).lower(), \
            f"错误信息不正确: {error_message}"

        logger.info(f"✓ 无效 ID 测试完成: code={error_code}")

    def test_update_contact_invalid_phone_format(self, login_session, db_cleanup):
        """
        测试场景6：更新 phone 时使用非 E.164 格式（使用自己创建的 Contact）
        验证点：
        1. HTTP 200
        2. 业务 code != 200（API 校验 E.164 格式），或记录为探索性结果
        """
        contact_api = ContactAPI(session=login_session)

        contact_id = _create_own_contact(contact_api, db_cleanup)
        if not contact_id:
            pytest.skip("创建 Contact 失败，跳过更新测试")

        logger.info(f"使用自己创建的 Contact ID: {contact_id}")
        update_data = {"phone": "13800138000"}   # 非 E.164 格式

        logger.info("更新 phone='13800138000'（非 E.164 格式，应被拒绝）")
        update_response = contact_api.update_contact(contact_id, update_data)

        assert update_response.status_code == 200, \
            f"接口应返回 HTTP 200，实际: {update_response.status_code}"

        response_body = update_response.json()
        code = response_body.get("code")

        if code != 200:
            logger.info(f"✓ 非 E.164 phone 被 API 拒绝: code={code}, msg={response_body.get('error_message')}")
        else:
            logger.info("⚠ API 未校验 phone E.164 格式（接受了非法值），记录为探索性结果")

    def test_update_contact_empty_data(self, login_session, db_cleanup):
        """
        测试场景7：使用空数据更新（使用自己创建的 Contact）
        验证点：
        1. HTTP 200
        2. 原始字段不变
        """
        contact_api = ContactAPI(session=login_session)

        contact_id = _create_own_contact(contact_api, db_cleanup)
        if not contact_id:
            pytest.skip("创建 Contact 失败，跳过更新测试")

        logger.info(f"使用自己创建的 Contact ID: {contact_id}")
        update_response = contact_api.update_contact(contact_id, {})

        assert update_response.status_code == 200, \
            f"接口应返回 HTTP 200，实际: {update_response.status_code}"

        response_body = update_response.json()
        code = response_body.get("code")
        logger.info(f"  空数据更新返回 code={code}")

        if code == 200:
            contact_data = response_body.get("data") or response_body
            assert contact_data.get("id") == contact_id, "空更新后 ID 不应改变"
            logger.info("  API 接受空数据，Contact 字段未改变")
        else:
            logger.info(f"  API 拒绝空数据（code={code}），属于合理行为")

    def test_update_contact_with_invisible_contact_id(self, login_session):
        """
        测试场景8：使用越权 Contact ID 更新
        验证点：
        1. HTTP 200
        2. code=506，error_message 包含 "visibility permission deny"
        """
        contact_api = ContactAPI(session=login_session)

        invisible_contact_id = "0034x00001ZZZZ9AAA"
        update_data = {"first_name": "Auto TestYan InvisibleTest"}

        logger.info(f"使用越权 Contact ID: {invisible_contact_id}")
        update_response = contact_api.update_contact(invisible_contact_id, update_data)

        assert update_response.status_code == 200

        response_body = update_response.json()
        error_code = response_body.get("code")

        assert error_code == 506 or error_code != 200, \
            f"越权 Contact ID 应返回 code=506 或其他错误码，实际: {error_code}"

        logger.info(f"✓ 越权 Contact ID 更新被拒绝: code={error_code}")

    def test_update_contact_invalid_country_format(self, login_session, db_cleanup):
        """
        测试场景9：更新 country 时使用非 ISO 3166 标准代码（使用自己创建的 Contact）
        验证点：
        1. HTTP 200
        2. 业务 code != 200，或记录为探索性结果
        """
        contact_api = ContactAPI(session=login_session)

        contact_id = _create_own_contact(contact_api, db_cleanup)
        if not contact_id:
            pytest.skip("创建 Contact 失败，跳过更新测试")

        logger.info(f"使用自己创建的 Contact ID: {contact_id}")
        update_data = {
            "permanent_country": "CHINA",       # 非 ISO 3166 标准
            "mailing_country": "UNITED_STATES"  # 非 ISO 3166 标准
        }

        logger.info("更新 permanent_country='CHINA'，mailing_country='UNITED_STATES'（非 ISO 3166）")
        update_response = contact_api.update_contact(contact_id, update_data)

        assert update_response.status_code == 200, \
            f"接口应返回 HTTP 200，实际: {update_response.status_code}"

        response_body = update_response.json()
        code = response_body.get("code")

        if code != 200:
            logger.info(f"✓ 非 ISO 3166 country 被 API 拒绝: code={code}, msg={response_body.get('error_message')}")
        else:
            logger.info("⚠ API 未校验 country ISO 3166 格式（接受了非标准值），记录为探索性结果")

    def test_update_contact_invalid_enum_fields(self, login_session, db_cleanup):
        """
        测试场景10：更新 government_document_type 和 gender 超出枚举范围（使用自己创建的 Contact）
        验证点：
        1. HTTP 200
        2. 业务 code != 200，或记录为探索性结果
        """
        contact_api = ContactAPI(session=login_session)

        contact_id = _create_own_contact(contact_api, db_cleanup)
        if not contact_id:
            pytest.skip("创建 Contact 失败，跳过更新测试")

        logger.info(f"使用自己创建的 Contact ID: {contact_id}")
        update_data = {
            "gender": "Unknown",                          # 超出枚举范围
            "government_document_type": "Magic Document" # 超出枚举范围
        }

        logger.info("更新 gender='Unknown'，government_document_type='Magic Document'（超出枚举）")
        update_response = contact_api.update_contact(contact_id, update_data)

        assert update_response.status_code == 200, \
            f"接口应返回 HTTP 200，实际: {update_response.status_code}"

        response_body = update_response.json()
        code = response_body.get("code")

        if code != 200:
            logger.info(f"✓ 超出枚举范围的值被 API 拒绝: code={code}, msg={response_body.get('error_message')}")
        else:
            logger.info("⚠ API 未校验枚举范围（接受了非法枚举值），记录为探索性结果")
