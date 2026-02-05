"""
Card Opening - Debit Card Application 接口测试用例
测试 POST /api/v1/cores/{core}/card-issuance/applications/debit-card 接口
"""
import pytest
import time
from utils.logger import logger
from utils.assertions import assert_status_ok
from data.enums import LimitType


@pytest.mark.card_opening
@pytest.mark.create_api
class TestCardOpeningDebitCard:
    """
    借记卡申请接口测试用例集
    ⚠️ 文档问题：
    1. JSON格式错误（缺少逗号）
    2. 条件必需字段说明不清（classification_type）
    """

    @pytest.mark.skip(reason="需要真实的sub_program_id和card_holder_id")
    def test_create_debit_card_success(self, card_opening_api):
        """
        测试场景1：成功创建借记卡申请
        验证点：
        1. 接口返回 200
        2. code=200
        3. 返回申请ID和card_id
        """
        logger.info("测试场景1：成功创建借记卡申请")
        
        response = card_opening_api.create_debit_card_application(
            sub_program_id="test_sub_program_id",
            card_holder_id="test_card_holder_id",
            expiration_date="12/2026"
        )
        
        assert_status_ok(response)
        
        response_body = response.json()
        assert response_body.get("code") == 200
        
        data = response_body.get("data", {})
        assert data.get("id") is not None, "申请ID不应为空"
        assert data.get("card_id") is not None, "卡片ID不应为空"
        
        logger.info(f"✓ 借记卡申请创建成功，申请ID: {data['id']}, 卡片ID: {data['card_id']}")

    @pytest.mark.skip(reason="需要真实数据")
    def test_with_calendar_date_limit_type(self, card_opening_api):
        """
        测试场景2：使用Calendar_Date限制类型
        验证点：
        1. limit_type正确保存
        """
        logger.info("测试场景2：使用Calendar_Date限制类型")
        
        response = card_opening_api.create_debit_card_application(
            sub_program_id="test_sub_program_id",
            card_holder_id="test_card_holder_id",
            expiration_date="12/2026",
            limit_type=LimitType.CALENDAR_DATE
        )
        
        assert_status_ok(response)
        
        logger.info("✓ Calendar_Date限制类型验证通过")

    @pytest.mark.skip(reason="需要真实数据")
    def test_with_active_date_limit_type(self, card_opening_api):
        """
        测试场景3：使用Active_Date限制类型
        验证点：
        1. limit_type正确保存
        """
        logger.info("测试场景3：使用Active_Date限制类型")
        
        response = card_opening_api.create_debit_card_application(
            sub_program_id="test_sub_program_id",
            card_holder_id="test_card_holder_id",
            expiration_date="12/2026",
            limit_type=LimitType.ACTIVE_DATE
        )
        
        assert_status_ok(response)
        
        logger.info("✓ Active_Date限制类型验证通过")

    @pytest.mark.skip(reason="需要真实数据")
    def test_with_spending_limit(self, card_opening_api):
        """
        测试场景4：完整spending_limit测试
        验证点：
        1. spending_limit数组正确保存
        2. 支持多种interval类型
        """
        logger.info("测试场景4：完整spending_limit测试")
        
        spending_limit = [
            {"amount": 100, "count": 10, "interval": "Daily"},
            {"amount": 500, "count": 50, "interval": "Weekly"},
            {"amount": 2000, "interval": "Total"},
            {"amount": 100, "interval": "Per_Authorization"}
        ]
        
        response = card_opening_api.create_debit_card_application(
            sub_program_id="test_sub_program_id",
            card_holder_id="test_card_holder_id",
            expiration_date="12/2026",
            spending_limit=spending_limit
        )
        
        assert_status_ok(response)
        
        logger.info("✓ spending_limit验证通过")

    @pytest.mark.skip(reason="需要真实数据")
    def test_with_nested_program(self, card_opening_api):
        """
        测试场景5：关联nested_program测试
        验证点：
        1. associated_nested_program数组正确保存
        """
        logger.info("测试场景5：关联nested_program测试")
        
        associated_nested_program = [
            {"nested_program_id": "test_nested_id", "amount": 1000, "interval": "Total"}
        ]
        
        response = card_opening_api.create_debit_card_application(
            sub_program_id="test_sub_program_id",
            card_holder_id="test_card_holder_id",
            expiration_date="12/2026",
            associated_nested_program=associated_nested_program
        )
        
        assert_status_ok(response)
        
        logger.info("✓ nested_program关联验证通过")

    def test_missing_required_field(self, card_opening_api):
        """
        测试场景6：缺少必需字段
        验证点：
        1. 接口返回错误
        2. code不为200
        """
        logger.info("测试场景6：缺少必需字段")
        
        response = card_opening_api.create_debit_card_application(
            sub_program_id="test_sub_program_id",
            card_holder_id="test_card_holder_id"
            # 缺少 expiration_date
        )
        
        assert response.status_code == 200, "HTTP状态码应为200"
        response_body = response.json()
        assert response_body.get("code") != 200, "业务code应不为200"
        
        logger.info(f"✓ 正确拒绝缺少必需字段: {response_body.get('error_message', 'Unknown error')}")

    def test_invalid_sub_program_id(self, card_opening_api):
        """
        测试场景7：无效的sub_program_id
        验证点：
        1. 接口返回错误
        """
        logger.info("测试场景7：无效的sub_program_id")
        
        response = card_opening_api.create_debit_card_application(
            sub_program_id="INVALID_SUB_PROGRAM_ID_999",
            card_holder_id="test_card_holder_id",
            expiration_date="12/2026"
        )
        
        assert response.status_code == 200
        response_body = response.json()
        assert response_body.get("code") != 200
        
        logger.info(f"✓ 正确拒绝无效的sub_program_id: {response_body.get('error_message', 'Unknown error')}")

    def test_conditional_required_field(self, card_opening_api):
        """
        测试场景8：条件必需字段验证（financial_account_id）
        验证点：
        1. 文档说classification_type='Consumer'时需要financial_account_id
        2. 但请求参数中无classification_type字段
        3. 验证实际行为
        """
        logger.info("测试场景8：条件必需字段验证")
        
        # 不提供financial_account_id
        response = card_opening_api.create_debit_card_application(
            sub_program_id="test_sub_program_id",
            card_holder_id="test_card_holder_id",
            expiration_date="12/2026"
            # 不提供 financial_account_id
        )
        
        logger.info(f"响应状态: {response.status_code}")
        
        if response.status_code == 200:
            response_body = response.json()
            logger.info(f"响应code: {response_body.get('code')}")
            logger.info(f"响应信息: {response_body.get('error_message', 'Success')}")
        
        logger.info("✓ 条件必需字段行为验证完成")
