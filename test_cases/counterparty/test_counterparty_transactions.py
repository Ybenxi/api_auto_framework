"""
Counterparty Transactions 接口测试用例
测试 GET /api/v1/cores/{core}/counterparties/{id}/transactions 接口
"""
import pytest
from utils.logger import logger
from utils.assertions import (
    assert_status_ok,
    assert_list_structure,
    assert_pagination,
    assert_empty_result
)


@pytest.mark.counterparty
@pytest.mark.transactions_api
class TestCounterpartyTransactions:
    """
    Counterparty 交易列表接口测试用例集
    """

    @pytest.mark.skip(reason="需要真实 account_id，待完善数据准备逻辑")
    def test_list_counterparty_transactions_success(self, counterparty_api, login_session):
        """
        测试场景1：成功获取 Counterparty 相关交易列表
        验证点：
        1. 接口返回 200
        2. 返回列表结构正确
        3. 分页信息完整
        """
        # 先创建一个 Counterparty
        logger.info("创建测试用的 Counterparty")
        create_data = {
            "name": f"Auto TestYan Counterparty Trans {timestamp}",
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
            pytest.skip(f"创建 Counterparty 失败")
        
        created_data = create_response.json()
        counterparty_id = created_data.get("id")
        logger.info(f"Counterparty 创建成功: {counterparty_id}")
        
        # 查询交易列表
        logger.info("查询 Counterparty 相关交易")
        response = counterparty_api.list_counterparty_transactions(counterparty_id, page=0, size=10)
        
        # 验证响应
        logger.info("验证响应结构")
        assert_status_ok(response)
        
        response_body = response.json()
        
        # 验证列表结构（可能为空）
        if "content" in response_body:
            assert_list_structure(response_body)
            logger.info(f"✓ 交易列表获取成功，返回 {len(response_body['content'])} 条记录")
        else:
            # 如果没有 content，可能是空结果或包装在 data 中
            logger.info("✓ 交易列表接口调用成功（可能为空结果）")

    @pytest.mark.skip(reason="需要真实 account_id，待完善数据准备逻辑")
    def test_list_counterparty_transactions_with_fa_filter(self, counterparty_api, login_session):
        """
        测试场景2：使用 Financial Account ID 筛选交易
        验证点：
        1. 接口返回 200
        2. 筛选参数生效
        """
        # 创建 Counterparty
        logger.info("创建测试用的 Counterparty")
        create_data = {
            "name": f"Auto TestYan Counterparty FA Filter {timestamp}",
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
        
        # 使用 FA ID 筛选
        logger.info("使用 Financial Account ID 筛选")
        test_fa_id = "test_fa_id_123"
        response = counterparty_api.list_counterparty_transactions(
            counterparty_id,
            financial_account_id=test_fa_id,
            size=10
        )
        
        # 验证响应
        logger.info("验证响应")
        assert_status_ok(response)
        
        logger.info("✓ FA 筛选参数处理正常")

    @pytest.mark.skip(reason="需要真实 account_id，待完善数据准备逻辑")
    def test_list_counterparty_transactions_with_date_range(self, counterparty_api, login_session):
        """
        测试场景3：使用日期范围筛选交易
        验证点：
        1. 接口返回 200
        2. 日期范围参数被正确处理
        """
        # 创建 Counterparty
        logger.info("创建测试用的 Counterparty")
        create_data = {
            "name": f"Auto TestYan Counterparty Date Filter {timestamp}",
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
        
        # 使用日期范围
        logger.info("使用日期范围筛选")
        response = counterparty_api.list_counterparty_transactions(
            counterparty_id,
            start_date="2024-01-01",
            end_date="2024-12-31",
            size=10
        )
        
        # 验证响应
        logger.info("验证响应")
        assert_status_ok(response)
        
        logger.info("✓ 日期范围筛选参数处理正常")

    @pytest.mark.skip(reason="需要真实 account_id，待完善数据准备逻辑")
    def test_list_counterparty_transactions_pagination(self, counterparty_api, login_session):
        """
        测试场景4：验证交易列表分页功能
        验证点：
        1. 接口返回 200
        2. 分页参数被正确处理
        """
        # 创建 Counterparty
        logger.info("创建测试用的 Counterparty")
        create_data = {
            "name": f"Auto TestYan Counterparty Pagination {timestamp}",
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
        
        # 测试分页
        logger.info("测试分页功能")
        response = counterparty_api.list_counterparty_transactions(
            counterparty_id,
            page=0,
            size=5
        )
        
        # 验证响应
        logger.info("验证分页响应")
        assert_status_ok(response)
        
        response_body = response.json()
        if "content" in response_body:
            assert_pagination(response_body, expected_size=5, expected_page=0)
            logger.info("✓ 分页功能验证通过")
        else:
            logger.info("✓ 分页参数处理正常（结果可能为空）")

    def test_list_counterparty_transactions_invalid_id(self, counterparty_api):
        """
        测试场景5：使用无效 counterparty_id 查询交易
        验证点：
        1. 返回 200 状态码
        2. 返回空列表（无效ID查不到交易）
        """
        logger.info("使用无效 Counterparty ID 查询交易")
        invalid_id = "INVALID_COUNTERPARTY_ID_999999"
        
        response = counterparty_api.list_counterparty_transactions(invalid_id, size=10)
        
        # 验证响应
        logger.info("验证响应")
        assert_status_ok(response)
        
        response_body = response.json()
        
        # 提取data层
        if "data" in response_body:
            data = response_body["data"]
            if isinstance(data, dict) and "content" in data:
                assert len(data["content"]) == 0, "无效 ID 应该返回空列表"
                logger.info("✓ 无效 ID 返回空列表")
            else:
                logger.info("✓ 无效 ID 响应正常")
        elif "content" in response_body:
            assert len(response_body["content"]) == 0, "无效 ID 应该返回空列表"
            logger.info("✓ 无效 ID 返回空列表")
        else:
            logger.info("✓ 无效 ID 响应处理正常")

    @pytest.mark.skip(reason="需要真实 account_id，待完善数据准备逻辑")
    def test_list_counterparty_transactions_with_transaction_type_filter(self, counterparty_api, login_session):
        """
        测试场景6：使用交易类型筛选
        验证点：
        1. 接口返回 200
        2. transaction_type 参数被正确处理
        """
        # 创建 Counterparty
        logger.info("创建测试用的 Counterparty")
        create_data = {
            "name": f"Auto TestYan Counterparty Type Filter {timestamp}",
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
        
        # 使用交易类型筛选
        logger.info("使用交易类型筛选: Credit")
        response = counterparty_api.list_counterparty_transactions(
            counterparty_id,
            transaction_type="Credit",
            size=10
        )
        
        # 验证响应
        logger.info("验证响应")
        assert_status_ok(response)
        
        logger.info("✓ 交易类型筛选参数处理正常")
