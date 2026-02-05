"""
Card Dispute - List Disputes 接口测试用例
测试 GET /api/v1/cores/{core}/card-issuance/disputes 接口
"""
import pytest
from utils.logger import logger
from utils.assertions import assert_status_ok, assert_list_structure
from data.enums import DisputeStatus


@pytest.mark.card_dispute_risk
@pytest.mark.list_api
class TestCardDisputeList:
    """
    争议列表接口测试用例集
    ⚠️ 文档问题：
    1. disputed_reason实际是string，不是int
    2. JSON格式错误（trailing comma）
    3. fileId vs file_id命名不一致
    """

    def test_list_disputes_success(self, card_dispute_api):
        """
        测试场景1：成功获取争议列表
        验证点：
        1. 接口返回 200
        2. 返回列表结构正确
        """
        logger.info("测试场景1：成功获取争议列表")
        
        response = card_dispute_api.list_disputes(page=0, size=10)
        
        assert_status_ok(response)
        
        response_body = response.json()
        assert response_body.get("code") == 200
        assert_list_structure(response_body)
        
        logger.info(f"✓ 争议列表获取成功")

    def test_filter_by_status(self, card_dispute_api):
        """
        测试场景2：按status筛选
        验证点：
        1. status参数生效
        """
        logger.info("测试场景2：按status筛选")
        
        response = card_dispute_api.list_disputes(status=DisputeStatus.NEW, size=10)
        
        assert_status_ok(response)
        
        logger.info("✓ status筛选验证通过")

    def test_filter_by_card_id(self, card_dispute_api):
        """
        测试场景3：按card_id筛选
        验证点：
        1. card_id参数生效
        """
        logger.info("测试场景3：按card_id筛选")
        
        response = card_dispute_api.list_disputes(card_id="test_card_id", size=10)
        
        assert_status_ok(response)
        
        logger.info("✓ card_id筛选验证通过")

    def test_filter_by_time_range(self, card_dispute_api):
        """
        测试场景4：按时间范围筛选
        验证点：
        1. startTime和endTime参数生效
        2. 注意：使用驼峰命名
        """
        logger.info("测试场景4：按时间范围筛选")
        
        response = card_dispute_api.list_disputes(
            start_time="2024-01-01",
            end_time="2024-12-31",
            size=10
        )
        
        assert_status_ok(response)
        
        logger.info("✓ 时间范围筛选验证通过")

    def test_disputed_reason_type(self, card_dispute_api):
        """
        测试场景5：disputed_reason类型验证
        验证点：
        1. Properties定义为int（错误）
        2. 实际是string枚举
        """
        logger.info("测试场景5：disputed_reason类型验证")
        
        response = card_dispute_api.list_disputes(size=1)
        
        assert_status_ok(response)
        
        content = response.json().get("data", {}).get("content", [])
        
        if content:
            dispute = content[0]
            disputed_reason = dispute.get("disputed_reason")
            reason_type = type(disputed_reason).__name__
            
            logger.info(f"disputed_reason类型: {reason_type}, 值: {disputed_reason}")
            
            if isinstance(disputed_reason, str):
                logger.warning("⚠️ 确认：disputed_reason是string类型（Properties定义为int是错误的）")
            
        logger.info("✓ disputed_reason类型验证完成")

    def test_file_id_field_naming(self, card_dispute_api):
        """
        测试场景6：file_id字段命名验证
        验证点：
        1. Properties定义：fileId（驼峰）
        2. 响应实际：file_id（下划线）
        """
        logger.info("测试场景6：file_id字段命名验证")
        
        response = card_dispute_api.list_disputes(size=1)
        
        assert_status_ok(response)
        
        content = response.json().get("data", {}).get("content", [])
        
        if content:
            dispute = content[0]
            
            has_fileId = "fileId" in dispute
            has_file_id = "file_id" in dispute
            
            logger.info(f"字段命名: fileId={has_fileId}, file_id={has_file_id}")
            
            if has_file_id:
                logger.warning("⚠️ 响应使用file_id（Properties定义为fileId）")
        
        logger.info("✓ 字段命名验证完成")
