"""
Counterparty Update 接口测试用例
测试 PATCH /api/v1/cores/{core}/counterparties/{id} 接口
"""
import pytest
import time
from api.account_api import AccountAPI
from utils.logger import logger
from utils.assertions import (
    assert_status_ok,
    assert_fields_present
)


def create_test_counterparty(counterparty_api, login_session, name_suffix="Test"):
    """
    辅助函数：创建测试用的 Counterparty
    
    Returns:
        tuple: (counterparty_id, response_body) 或 (None, None) 如果失败
    """
    # 获取真实 account_id
    account_api = AccountAPI(session=login_session)
    account_response = account_api.list_accounts(page=0, size=1)
    
    if account_response.status_code != 200:
        return None, None
    
    account_data = account_response.json().get("data", {})
    accounts = account_data.get("content", [])
    
    if len(accounts) == 0:
        return None, None
    
    account_id = accounts[0]["id"]
    
    # 创建 Counterparty
    timestamp = int(time.time())
    counterparty_data = {
        "name": f"Auto TestYan Counterparty {name_suffix} {timestamp}",
        "type": "Person",
        "payment_type": "ACH",
        "bank_account_type": "Checking",
        "bank_routing_number": "091918457",
        "bank_name": "Auto TestYan Bank",
        "bank_account_owner_name": "Auto TestYan Owner",
        "bank_account_number": f"{timestamp}"[:9],
        "assign_account_ids": [account_id]
    }
    
    response = counterparty_api.create_counterparty(counterparty_data)
    
    if response.status_code != 200:
        return None, None
    
    response_body = response.json()
    return response_body.get("id"), response_body


@pytest.mark.counterparty
@pytest.mark.update_api
class TestCounterpartyUpdate:
    """
    Counterparty 更新接口测试用例集
    """

    @pytest.mark.skip(reason="需要真实 account_id，待完善数据准备逻辑")
    def test_update_counterparty_single_field(self, counterparty_api, login_session):
        """
        测试场景1：成功更新 Counterparty 单个字段
        验证点：
        1. 接口返回 200
        2. 更新的字段值正确反映
        3. 其他字段保持不变
        """
        # 1. 创建测试用的 Counterparty
        logger.info("创建测试用的 Counterparty")
        counterparty_id, created_data = create_test_counterparty(
            counterparty_api, login_session, "Original"
        )
        
        if not counterparty_id:
            pytest.skip("创建 Counterparty 失败")
        
        original_name = created_data.get("name")
        logger.info(f"Counterparty 创建成功: {counterparty_id}")
        
        # 2. 更新名称字段
        logger.info("更新 Counterparty 名称")
        update_data = {
            "name": "Auto TestYan Counterparty Updated"
        }
        
        update_response = counterparty_api.update_counterparty(counterparty_id, update_data)
        
        # 3. 验证响应
        logger.info("验证更新响应")
        assert_status_ok(update_response)
        
        response_body = update_response.json()
        updated_data = response_body
        
        # 验证字段更新成功
        assert updated_data.get("name") == "Auto TestYan Counterparty Updated", \
            f"名称未更新: {updated_data.get('name')}"
        
        logger.info("✓ 单字段更新验证通过:")
        logger.info(f"  原名称: {original_name}")
        logger.info(f"  新名称: {updated_data.get('name')}")

    @pytest.mark.skip(reason="需要真实 account_id，待完善数据准备逻辑")
    def test_update_counterparty_multiple_fields(self, counterparty_api, login_session):
        """
        测试场景2：同时更新 Counterparty 多个字段
        验证点：
        1. 接口返回 200
        2. 所有更新的字段值都正确
        """
        # 1. 先创建一个 Counterparty（使用完整必需字段）
        logger.info("创建测试用的 Counterparty")
        import time
        timestamp = int(time.time())
        create_data = {
            "name": f"Auto TestYan Counterparty Multi {timestamp}",
            "type": "Person",
            "payment_type": "ACH",
            "bank_account_type": "Savings",
            "bank_routing_number": "091918457",
            "bank_name": "Auto TestYan Bank",
            "bank_account_owner_name": "Auto TestYan Owner",
            "bank_account_number": f"{timestamp+1}"[:9]
        }
        
        create_response = counterparty_api.create_counterparty(create_data)
        if create_response.status_code != 200:
            pytest.skip(f"创建 Counterparty 失败")
        
        created_data = create_response.json()
        counterparty_id = created_data.get("id")
        logger.info(f"Counterparty 创建成功: {counterparty_id}")
        
        # 2. 同时更新多个字段
        logger.info("同时更新 name 和 ach_account_number")
        update_data = {
            "name": "Auto TestYan Counterparty Multi Updated",
            "ach_account_number": "1111222233"
        }
        
        update_response = counterparty_api.update_counterparty(counterparty_id, update_data)
        
        # 3. 验证响应
        logger.info("验证更新响应")
        assert_status_ok(update_response)
        
        response_body = update_response.json()
        updated_data = response_body
        
        # 验证所有字段
        assert updated_data.get("name") == "Auto TestYan Counterparty Multi Updated"
        assert updated_data.get("ach_account_number") == "1111222233"
        
        logger.info("✓ 多字段更新验证通过")

    def test_update_counterparty_invalid_id(self, counterparty_api):
        """
        测试场景3：使用无效的 counterparty_id 更新
        验证点：
        1. 返回 200 状态码（统一错误处理）
        2. 响应体包含错误信息或 code != 200
        """
        logger.info("使用无效 ID 更新 Counterparty")
        invalid_id = "INVALID_COUNTERPARTY_ID_999999"
        update_data = {"name": "Updated Name"}
        
        response = counterparty_api.update_counterparty(invalid_id, update_data)
        
        logger.info("验证错误响应")
        assert_status_ok(response)
        
        response_body = response.json()
        assert response_body.get("code") != 200 or "error" in str(response_body).lower(), \
            "无效 ID 应该返回错误"
        
        logger.info("✓ 无效 ID 错误处理验证通过")

    @pytest.mark.skip(reason="需要真实 account_id，待完善数据准备逻辑")
    def test_update_counterparty_payment_type_change(self, counterparty_api, login_session):
        """
        测试场景4：更新 Counterparty 的支付类型（ACH -> Wire）
        验证点：
        1. 接口返回 200
        2. payment_type 更新成功
        3. Wire 相关字段生效
        """
        # 1. 创建 ACH 类型的 Counterparty
        logger.info("创建 ACH 类型的 Counterparty")
        create_data = {
            "name": f"Auto TestYan Counterparty ACH to Wire {timestamp}",
            "type": "Person",
            "payment_type": "ACH",
            "bank_account_type": "Checking",
            "bank_routing_number": "091918457",
            "bank_name": "Auto TestYan Bank",
            "bank_account_owner_name": "Auto TestYan Owner",
            "bank_account_number": f"{timestamp}"[:9]
        }
        
        create_response = counterparty_api.create_counterparty(create_data)
        if create_response.status_code != 200:
            pytest.skip(f"创建失败")
        
        created_data = create_response.json()
        counterparty_id = created_data.get("id")
        logger.info(f"ACH Counterparty 创建成功: {counterparty_id}")
        
        # 2. 更新为 Wire 类型
        logger.info("更新支付类型为 Wire")
        update_data = {
            "payment_type": "Wire",
            "wire_account_number": "9999888877",
            "wire_routing_number": "026009593",
            "wire_beneficiary_name": "Auto TestYan Wire Recipient"
        }
        
        update_response = counterparty_api.update_counterparty(counterparty_id, update_data)
        
        # 3. 验证响应
        logger.info("验证支付类型更新")
        assert_status_ok(update_response)
        
        response_body = update_response.json()
        updated_data = response_body
        
        assert updated_data.get("payment_type") == "Wire", \
            f"支付类型未更新: {updated_data.get('payment_type')}"
        
        logger.info("✓ 支付类型更新验证通过")
        logger.info(f"  原类型: ACH")
        logger.info(f"  新类型: Wire")

    @pytest.mark.skip(reason="需要真实 account_id，待完善数据准备逻辑")
    def test_update_counterparty_missing_required_field(self, counterparty_api, login_session):
        """
        测试场景5：更新时缺少必需字段（边界情况）
        验证点：
        1. 接口能处理空的更新数据
        2. 或返回适当的错误信息
        """
        # 先创建一个 Counterparty
        logger.info("创建测试用的 Counterparty")
        create_data = {
            "name": f"Auto TestYan Counterparty Edge {timestamp}",
            "type": "Person",
            "payment_type": "ACH",
            "bank_account_type": "Checking",
            "bank_routing_number": "091918457",
            "bank_name": "Auto TestYan Bank",
            "bank_account_owner_name": "Auto TestYan Owner",
            "bank_account_number": f"{timestamp}"[:9]
        }
        
        create_response = counterparty_api.create_counterparty(create_data)
        if create_response.status_code != 200:
            pytest.skip(f"创建失败")
        
        created_data = create_response.json()
        counterparty_id = created_data.get("id")
        
        # 尝试用空数据更新
        logger.info("使用空数据更新")
        update_data = {}
        
        update_response = counterparty_api.update_counterparty(counterparty_id, update_data)
        
        # 验证响应（可能成功也可能失败，取决于 API 设计）
        logger.info("验证 API 对空更新数据的处理")
        logger.info(f"  状态码: {update_response.status_code}")
        
        # API 应该要么接受（返回200），要么拒绝（返回错误）
        assert update_response.status_code in [200, 400, 422], \
            f"状态码应该是 200/400/422，实际: {update_response.status_code}"
        
        logger.info("✓ 空更新数据处理验证完成")

    @pytest.mark.skip(reason="需要真实 account_id，待完善数据准备逻辑")
    def test_update_counterparty_response_structure(self, counterparty_api, login_session):
        """
        测试场景6：验证更新响应的数据结构
        验证点：
        1. 响应包含必需字段
        2. 响应结构完整
        """
        # 创建并更新
        logger.info("创建测试用的 Counterparty")
        create_data = {
            "name": f"Auto TestYan Counterparty Structure {timestamp}",
            "type": "Person",
            "payment_type": "ACH",
            "bank_account_type": "Checking",
            "bank_routing_number": "091918457",
            "bank_name": "Auto TestYan Bank",
            "bank_account_owner_name": "Auto TestYan Owner",
            "bank_account_number": f"{timestamp}"[:9]
        }
        
        create_response = counterparty_api.create_counterparty(create_data)
        if create_response.status_code != 200:
            pytest.skip(f"创建失败")
        
        created_data = create_response.json()
        counterparty_id = created_data.get("id")
        
        # 更新
        logger.info("更新 Counterparty")
        update_data = {"name": "Auto TestYan Counterparty Structure Updated"}
        update_response = counterparty_api.update_counterparty(counterparty_id, update_data)
        
        # 验证响应结构
        logger.info("验证响应结构")
        assert_status_ok(update_response)
        
        response_body = update_response.json()
        updated_data = response_body
        
        # 验证必需字段
        required_fields = ["id", "name", "payment_type", "status"]
        assert_fields_present(updated_data, required_fields, "更新响应")
        
        logger.info("✓ 响应结构验证通过")
        logger.info(f"  包含字段: {', '.join(required_fields)}")

    def test_update_counterparty_with_invisible_id(self, counterparty_api):
        """
        测试场景7：使用越权 Counterparty ID 更新 → 返回 506 或其他错误
        验证点：
        1. 使用越权 Counterparty ID：241010195849717901（Chaolong actc ach 11）
        2. 服务器返回 200
        3. code=506 或 code!=200，data 为 null
        """
        invisible_cp_id = "241010195849717901"  # Chaolong actc ach 11
        update_data = {"name": "Auto TestYan InvisibleUpdate"}

        logger.info(f"使用越权 Counterparty ID 更新: {invisible_cp_id}")
        update_response = counterparty_api.update_counterparty(invisible_cp_id, update_data)

        assert update_response.status_code == 200

        response_body = update_response.json()
        error_code = response_body.get("code")

        assert error_code != 200, \
            f"越权 Counterparty ID 应返回错误码，实际: {error_code}"

        logger.info(f"✓ 越权 Counterparty ID 更新被拒绝: code={error_code}")
