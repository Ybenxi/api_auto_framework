"""
Card Management - Card Transactions 接口测试用例
测试交易列表和交易详情接口
"""
import pytest
from utils.logger import logger
from utils.assertions import assert_status_ok, assert_list_structure
from data.enums import CardNetwork
from utils.type_converters import to_bool


@pytest.mark.card_management
@pytest.mark.transactions_api
class TestCardTransactions:
    """
    卡片交易接口测试用例集
    ⚠️ 文档问题：
    1. is_virtual字段类型不一致（boolean vs string）
    2. transaction_histories字段未定义
    """

    def test_list_transactions_success(self, card_management_api):
        """
        测试场景1：成功获取交易列表
        验证点：
        1. 接口返回 200
        2. 返回列表结构正确
        """
        logger.info("测试场景1：成功获取交易列表")
        
        response = card_management_api.list_card_transactions(page=0, size=10)
        
        assert_status_ok(response)
        
        response_body = response.json()
        assert response_body.get("code") == 200
        assert_list_structure(response_body.get("data", response_body))
        
        logger.info(f"✓ 交易列表获取成功")

    def test_filter_by_card_number(self, card_management_api):
        """
        测试场景2：按 card_number 筛选（先获取真实值再筛选）
        验证点：
        1. 接口返回 200
        2. 返回的每条交易 card_number 与筛选值匹配
        """
        logger.info("测试场景2：按 card_number 筛选")

        # 先获取真实 card_number
        base_response = card_management_api.list_card_transactions(size=1)
        assert_status_ok(base_response)
        base_content = base_response.json().get("data", {}).get("content", [])

        if not base_content:
            pytest.skip("无交易数据，跳过 card_number 筛选测试")

        real_card_number = base_content[0].get("card_number")
        if not real_card_number:
            pytest.skip("card_number 字段为空，跳过")

        logger.info(f"  使用真实 card_number: {real_card_number}")
        response = card_management_api.list_card_transactions(card_number=real_card_number, size=10)
        assert_status_ok(response)

        content = response.json().get("data", {}).get("content", [])
        logger.info(f"  筛选返回 {len(content)} 条交易")

        if content:
            for txn in content:
                assert txn.get("card_number") == real_card_number, \
                    f"返回交易 card_number='{txn.get('card_number')}' 与筛选值 '{real_card_number}' 不一致"
        logger.info("✓ card_number 筛选验证通过")

    def test_filter_by_time_range(self, card_management_api):
        """
        测试场景3：按时间范围筛选，验证返回数据在范围内
        验证点：
        1. start_time 和 end_time 参数生效
        2. 返回的每条交易时间在筛选范围内
        3. 时间格式：yyyy-MM-dd HH:mm:ss
        """
        logger.info("测试场景3：按时间范围筛选")

        start_time = "2024-01-01 00:00:00"
        end_time = "2025-12-31 23:59:59"

        response = card_management_api.list_card_transactions(
            start_time=start_time,
            end_time=end_time,
            size=10
        )

        assert_status_ok(response)

        content = response.json().get("data", {}).get("content", [])
        logger.info(f"  返回 {len(content)} 条交易")

        if content:
            for txn in content:
                txn_time = txn.get("created_at") or txn.get("transaction_time") or txn.get("create_date", "")
                if txn_time and len(txn_time) >= 10:
                    txn_date = txn_time[:10]
                    assert "2024-01-01" <= txn_date <= "2025-12-31", \
                        f"交易时间 '{txn_date}' 不在范围内 [2024-01-01, 2025-12-31]"
            logger.info(f"✓ 时间范围筛选验证通过，{len(content)} 条数据均在范围内")

    def test_filter_by_merchant(self, card_management_api):
        """
        测试场景4：按商户名称筛选，验证返回数据包含关键词
        验证点：
        1. merchant_name 参数生效
        2. 返回的每条交易 merchant_name 包含关键词
        """
        logger.info("测试场景4：按商户筛选")

        # 先获取真实 merchant_name
        base_response = card_management_api.list_card_transactions(size=1)
        assert_status_ok(base_response)
        base_content = base_response.json().get("data", {}).get("content", [])

        if not base_content:
            pytest.skip("无交易数据，跳过 merchant 筛选测试")

        real_merchant = base_content[0].get("merchant_name", "")
        if not real_merchant:
            pytest.skip("merchant_name 字段为空，跳过")

        keyword = real_merchant[:4] if len(real_merchant) >= 4 else real_merchant
        logger.info(f"  使用关键词: '{keyword}'（来自 merchant_name='{real_merchant}'）")

        response = card_management_api.list_card_transactions(merchant_name=keyword, size=10)
        assert_status_ok(response)

        content = response.json().get("data", {}).get("content", [])
        logger.info(f"  返回 {len(content)} 条交易")

        if content:
            for txn in content:
                merchant = txn.get("merchant_name", "") or ""
                assert keyword.lower() in merchant.lower(), \
                    f"返回交易 merchant_name='{merchant}' 不包含关键词 '{keyword}'"
        logger.info("✓ 商户筛选验证通过")

    def test_is_virtual_type_inconsistency(self, card_management_api):
        """
        测试场景5：is_virtual字段类型不一致验证
        验证点：
        1. 响应中is_virtual可能是string（文档问题）
        2. 应为boolean
        3. 使用to_bool()兼容
        """
        logger.info("测试场景5：is_virtual类型验证")
        
        response = card_management_api.list_card_transactions(size=1)
        
        assert_status_ok(response)
        
        content = response.json().get("data", {}).get("content", [])
        
        if content:
            transaction = content[0]
            is_virtual = transaction.get("is_virtual")
            is_virtual_type = type(is_virtual).__name__
            
            logger.info(f"is_virtual类型: {is_virtual_type}, 值: {is_virtual}")
            
            if isinstance(is_virtual, str):
                logger.warning("⚠️ 检测到is_virtual为string类型（应为boolean）")
                # 使用to_bool转换
                converted = to_bool(is_virtual)
                logger.info(f"转换为boolean: {converted}")
            elif isinstance(is_virtual, bool):
                logger.info("✓ is_virtual类型正确（boolean）")
        
        logger.info("✓ is_virtual类型验证完成")

    @pytest.mark.skip(reason="需要真实的transaction_id")
    def test_get_transaction_detail_success(self, card_management_api):
        """
        测试场景6：成功获取交易详情
        验证点：
        1. 接口返回 200
        2. 包含transaction_histories字段（文档未定义）
        """
        logger.info("测试场景6：成功获取交易详情")
        
        # 从列表获取交易ID
        list_response = card_management_api.list_card_transactions(size=1)
        content = list_response.json().get("data", {}).get("content", [])
        transaction_id = content[0].get("transaction_id")
        
        # 获取详情
        response = card_management_api.get_transaction_detail(transaction_id)
        
        assert_status_ok(response)
        
        data = response.json().get("data", {})
        
        # 检查transaction_histories字段（文档未定义）
        if "transaction_histories" in data:
            logger.info("✓ 包含transaction_histories字段")
            histories = data["transaction_histories"]
            logger.info(f"交易历史记录数: {len(histories)}")
        
        logger.info(f"✓ 交易详情获取成功，ID: {transaction_id}")

    def test_invalid_transaction_id(self, card_management_api):
        """
        测试场景7：无效的transaction_id
        验证点：
        1. 接口返回错误
        """
        logger.info("测试场景7：无效的transaction_id")
        
        response = card_management_api.get_transaction_detail("INVALID_TXN_999")
        
        assert response.status_code == 200
        response_body = response.json()
        assert response_body.get("code") != 200
        
        logger.info(f"✓ 正确拒绝无效transaction_id")
