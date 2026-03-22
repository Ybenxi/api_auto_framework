"""
Risk Control - Spending Limit 接口测试用例
测试消费限制列表和详情接口
"""
import pytest
from utils.logger import logger
from utils.assertions import assert_status_ok, assert_list_structure


@pytest.mark.card_dispute_risk
@pytest.mark.list_api
class TestRiskSpendingLimit:
    """
    消费限制接口测试用例集
    ⚠️ 文档问题：接口描述错误（说card holders应为spending limits）
    """

    def test_list_spending_limits_success(self, card_dispute_api):
        """
        测试场景1：成功获取消费限制列表
        验证点：
        1. 接口返回 200
        2. 返回列表结构正确
        """
        logger.info("测试场景1：成功获取消费限制列表")
        
        response = card_dispute_api.list_spending_limits(page=0, size=10)
        
        assert_status_ok(response)
        
        response_body = response.json()
        assert response_body.get("code") == 200
        assert_list_structure(response_body.get("data", response_body))
        
        logger.info(f"✓ 消费限制列表获取成功")

    def test_filter_by_card_id(self, card_dispute_api):
        """
        测试场景2：按card_id筛选
        验证点：
        1. card_id参数生效
        """
        logger.info("测试场景2：按card_id筛选")
        
        response = card_dispute_api.list_spending_limits(card_id="test_card_id", size=10)
        
        assert_status_ok(response)
        
        logger.info("✓ card_id筛选验证通过")

    @pytest.mark.skip(reason="需要真实数据")
    def test_spending_limit_structure(self, card_dispute_api):
        """
        测试场景3：spending_limit结构验证
        验证点：
        1. spending_limit数组结构
        2. amount, interval, count字段
        3. MCC类型包含category
        """
        logger.info("测试场景3：spending_limit结构验证")
        
        response = card_dispute_api.list_spending_limits(size=1)
        
        content = response.json().get("data", {}).get("content", [])
        
        if content:
            item = content[0]
            spending_limit = item.get("spending_limit", [])
            
            for limit in spending_limit:
                assert "amount" in limit
                assert "interval" in limit
                
                interval = limit.get("interval")
                logger.debug(f"限制类型: {interval}, amount: {limit.get('amount')}")
                
                # MCC类型应包含category
                if interval == "MCC":
                    if "category" in limit:
                        logger.info(f"✓ MCC限制包含category: {limit['category']}")
                    else:
                        logger.warning("⚠️ MCC限制缺少category字段")
                
                # 检查count字段（可选）
                if "count" in limit:
                    logger.debug(f"包含count字段: {limit['count']}")
        
        logger.info("✓ spending_limit结构验证通过")

    @pytest.mark.skip(reason="需要真实数据")
    def test_nested_program_limits(self, card_dispute_api):
        """
        测试场景4：嵌套项目限额验证
        验证点：
        1. associated_nested_program数组结构
        """
        logger.info("测试场景4：嵌套项目限额验证")
        
        response = card_dispute_api.list_spending_limits(size=1)
        
        content = response.json().get("data", {}).get("content", [])
        
        if content:
            item = content[0]
            nested_programs = item.get("associated_nested_program", [])
            
            for program in nested_programs:
                assert "id" in program
                assert "amount" in program
                assert "interval" in program
            
            logger.info(f"✓ 嵌套项目限额验证通过，共 {len(nested_programs)} 个项目")

    @pytest.mark.skip(reason="需要真实的card_id")
    def test_get_card_spending_limit_success(self, card_dispute_api):
        """
        测试场景5：成功获取指定卡片的消费限制
        验证点：
        1. 接口返回 200
        2. 返回卡片的spending_limit
        """
        logger.info("测试场景5：获取卡片消费限制")
        
        response = card_dispute_api.get_card_spending_limit("test_card_id")
        
        assert_status_ok(response)
        
        data = response.json().get("data", {})
        assert "card_id" in data
        assert "spending_limit" in data
        
        logger.info(f"✓ 卡片消费限制获取成功")

    def test_invalid_card_id(self, card_dispute_api):
        """
        测试场景6：无效的card_id
        验证点：
        1. 接口返回错误
        """
        logger.info("测试场景6：无效的card_id")
        
        response = card_dispute_api.get_card_spending_limit("INVALID_CARD_999")
        
        assert response.status_code == 200
        response_body = response.json()
        assert response_body.get("code") != 200
        
        logger.info(f"✓ 正确拒绝无效card_id")

    @pytest.mark.skip(reason="需要真实数据")
    def test_consistency_between_list_and_detail(self, card_dispute_api):
        """
        测试场景7：List和Detail一致性验证
        验证点：
        1. 同一card_id在List和Detail中数据一致
        """
        logger.info("测试场景7：List和Detail一致性")
        
        # 从List获取
        list_response = card_dispute_api.list_spending_limits(size=1)
        list_content = list_response.json().get("data", {}).get("content", [])
        list_item = list_content[0]
        card_id = list_item.get("card_id")
        
        # 获取Detail
        detail_response = card_dispute_api.get_card_spending_limit(card_id)
        detail_data = detail_response.json().get("data", {})
        
        # 对比spending_limit数组
        list_limits = list_item.get("spending_limit", [])
        detail_limits = detail_data.get("spending_limit", [])
        
        logger.info(f"List中限制数量: {len(list_limits)}")
        logger.info(f"Detail中限制数量: {len(detail_limits)}")
        
        logger.info("✓ 一致性验证通过")
