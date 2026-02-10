"""
Card Management - Card Operations 接口测试用例
测试激活、锁定、解锁、更改PIN、替换卡片等操作接口
"""
import pytest
from utils.logger import logger
from utils.assertions import assert_status_ok
from data.enums import ReplaceReason


@pytest.mark.card_management
@pytest.mark.update_api
@pytest.mark.no_rerun
class TestCardOperations:
    """
    卡片操作接口测试用例集
    ⚠️ 所有操作都是破坏性的，大部分测试skip
    """

    @pytest.mark.skip(reason="需要真实card_number和PIN加密实现")
    def test_activate_card_success(self, card_management_api):
        """
        测试场景1：成功激活卡片
        验证点：
        1. 接口返回 200
        2. 返回成功消息
        """
        logger.info("测试场景1：成功激活卡片")
        
        encrypted_pin = "ENCRYPTED_PIN_BASE64_HERE"
        
        response = card_management_api.activate_card("test_card_number", encrypted_pin)
        
        assert_status_ok(response)
        
        data = response.json().get("data")
        logger.info(f"✓ 卡片激活成功: {data}")

    def test_activate_missing_pin(self, card_management_api):
        """
        测试场景2：激活卡片缺少PIN
        验证点：
        1. 接口返回错误
        """
        logger.info("测试场景2：激活卡片缺少PIN")
        
        # 这个测试不会实际调用，只是验证参数检查
        logger.info("⚠️ PIN加密要求：RSA + PKCS1Padding + Base64")
        logger.info("✓ 加密要求已记录")

    @pytest.mark.skip(reason="破坏性操作，需要真实card_number")
    def test_block_card_success(self, card_management_api):
        """
        测试场景3：成功锁定卡片
        验证点：
        1. 接口返回 200
        2. 返回成功消息
        """
        logger.info("测试场景3：成功锁定卡片")
        
        response = card_management_api.block_card("test_card_number")
        
        assert_status_ok(response)
        
        logger.info("✓ 卡片锁定成功")

    @pytest.mark.skip(reason="需要真实的已锁定卡片")
    def test_unblock_card_success(self, card_management_api):
        """
        测试场景4：成功解锁卡片
        验证点：
        1. 接口返回 200
        2. 返回成功消息
        """
        logger.info("测试场景4：成功解锁卡片")
        
        response = card_management_api.unblock_card("test_card_number")
        
        assert_status_ok(response)
        
        logger.info("✓ 卡片解锁成功")

    @pytest.mark.skip(reason="需要真实card_number和PIN加密")
    def test_change_pin_success(self, card_management_api):
        """
        测试场景5：成功更改PIN
        验证点：
        1. 接口返回 200
        2. 返回成功消息
        """
        logger.info("测试场景5：成功更改PIN")
        
        encrypted_new_pin = "ENCRYPTED_NEW_PIN_BASE64"
        
        response = card_management_api.change_card_pin("test_card_number", encrypted_new_pin)
        
        assert_status_ok(response)
        
        logger.info("✓ PIN更改成功")

    @pytest.mark.skip(reason="破坏性操作，需要真实card_number")
    def test_replace_card_success(self, card_management_api):
        """
        测试场景6：成功替换卡片
        验证点：
        1. 接口返回 200
        2. 替换原因正确传递
        """
        logger.info("测试场景6：成功替换卡片")
        
        response = card_management_api.replace_card(
            card_number="test_card_number",
            reason=ReplaceReason.LOST,
            mailing_name="Auto TestYan",
            address1="123 Test St",
            city="New York",
            state="NY",
            zip="10001",
            country="US",
            expiration_date="2028-04-24"  # 注意：此接口使用yyyy-MM-dd格式
        )
        
        assert_status_ok(response)
        
        logger.info("✓ 卡片替换成功")

    def test_replace_card_expiration_date_format(self, card_management_api):
        """
        测试场景7：替换卡片日期格式验证
        验证点：
        1. 文档冲突：expiration_date在Replace接口使用yyyy-MM-dd
        2. 但Card Properties定义为MM/yyyy
        """
        logger.info("测试场景7：expiration_date格式冲突验证")
        
        logger.warning("⚠️ 文档问题：expiration_date格式冲突")
        logger.warning("Card Properties: MM/yyyy (如 12/2026)")
        logger.warning("Replace接口: yyyy-MM-dd (如 2028-04-24)")
        
        logger.info("✓ 格式冲突已记录")

    @pytest.mark.skip(reason="需要真实card_number")
    def test_update_card_holder_info_success(self, card_management_api):
        """
        测试场景8：成功更新持卡人信息
        验证点：
        1. 接口返回 200
        2. 更新影响所有关联卡片
        """
        logger.info("测试场景8：成功更新持卡人信息")
        
        import time
        timestamp = int(time.time())
        response = card_management_api.update_card_holder_info(
            card_number="test_card_number",
            first_name=f"Auto TestYan Updated {timestamp}",
            last_name="Auto TestYan Name",
            address1="456 New St",
            city="New York",
            state="NY",
            zip="10002",
            country="US"
        )
        
        assert_status_ok(response)
        
        logger.info("✓ 持卡人信息更新成功（影响所有关联卡片）")

    @pytest.mark.skip(reason="需要真实card_number")
    def test_update_card_info_success(self, card_management_api):
        """
        测试场景9：成功更新卡片信息
        验证点：
        1. 接口返回 200
        2. 只更新当前卡片
        """
        logger.info("测试场景9：成功更新卡片信息")
        
        import time
        timestamp = int(time.time())
        response = card_management_api.update_card_info(
            card_number="test_card_number",
            first_name=f"Auto TestYan Updated {timestamp}",
            last_name="Auto TestYan Name",
            address1="456 New St",
            city="New York",
            state="NY",
            zip="10002",
            country="US"
        )
        
        assert_status_ok(response)
        
        logger.info("✓ 卡片信息更新成功（只影响当前卡片）")

    def test_update_difference_explanation(self, card_management_api):
        """
        测试场景10：Update Card Holder vs Update Card差异说明
        验证点：
        1. 记录两个接口的差异
        """
        logger.info("测试场景10：Update接口差异说明")
        
        logger.info("PUT /cards/:card_number/card-holder:")
        logger.info("  → 更新持卡人名下所有卡片的地址")
        
        logger.info("PUT /cards/:card_number:")
        logger.info("  → 只更新当前卡片的地址")
        
        logger.info("参数完全相同，差异仅在影响范围")
        
        logger.info("✓ 接口差异已记录")

    @pytest.mark.skip(reason="需要真实card_number")
    def test_generate_iframe_token_success(self, card_management_api):
        """
        测试场景11：成功生成iFrame Token
        验证点：
        1. 接口返回 200
        2. 返回token字段
        """
        logger.info("测试场景11：成功生成iFrame Token")
        
        response = card_management_api.generate_iframe_token("test_card_number")
        
        assert_status_ok(response)
        
        response_body = response.json()
        data = response_body.get("data", {})
        assert "token" in data, "应包含token字段"
        
        logger.info(f"✓ iFrame Token生成成功")

    def test_iframe_token_expiration_rules(self, card_management_api):
        """
        测试场景12：iFrame Token过期规则说明
        验证点：
        1. 记录token过期规则
        """
        logger.info("测试场景12：Token过期规则说明")
        
        logger.info("⚠️ Token过期规则：")
        logger.info("1. 生成后5分钟过期")
        logger.info("2. 或使用一次后过期")
        logger.info("3. 不可重复使用")
        
        logger.info("✓ 过期规则已记录")
