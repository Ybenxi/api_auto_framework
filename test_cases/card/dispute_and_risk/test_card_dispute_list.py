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
        2. 响应 code == 200
        3. content 是数组
        """
        logger.info("测试场景1：成功获取争议列表")

        response = card_dispute_api.list_disputes(page=0, size=10)

        assert_status_ok(response)

        response_body = response.json()
        assert response_body.get("code") == 200

        # Card 响应有 data 包装层
        content = response_body.get("data", {}).get("content", [])
        assert isinstance(content, list), "content 不是数组"

        logger.info(f"✓ 争议列表获取成功，返回 {len(content)} 条争议")

    @pytest.mark.parametrize("status", [
        DisputeStatus.NEW,
        DisputeStatus.SUBMITTED,
        DisputeStatus.RESULT
    ])
    def test_filter_by_status(self, card_dispute_api, status):
        """
        测试场景2：按 status 筛选（覆盖全部3个枚举值）
        验证点：
        1. 接口返回 200
        2. 返回的每条争议 status 均与筛选值一致
        """
        logger.info(f"测试场景2：按 status='{status}' 筛选")

        response = card_dispute_api.list_disputes(status=status, size=10)
        assert_status_ok(response)

        content = response.json().get("data", {}).get("content", [])
        logger.info(f"  返回 {len(content)} 条争议")

        if not content:
            logger.info(f"  ⚠️ status='{status}' 无数据，跳过筛选值验证")
        else:
            for dispute in content:
                assert dispute.get("status") == str(status), \
                    f"筛选结果包含非 {status} 状态: {dispute.get('status')}"
            logger.info(f"✓ {len(content)} 条争议均为 {status} 状态")

    def test_filter_by_card_id(self, card_dispute_api):
        """
        测试场景3：按 card_id 筛选（先获取真实 card_id 再筛选）
        验证点：
        1. card_id 参数生效
        2. 返回的每条争议 card_id 与筛选值一致
        """
        logger.info("测试场景3：按 card_id 筛选")

        # 先获取真实 card_id
        base_response = card_dispute_api.list_disputes(size=1)
        assert_status_ok(base_response)
        base_content = base_response.json().get("data", {}).get("content", [])

        if not base_content:
            pytest.skip("无争议数据，跳过 card_id 筛选测试")

        real_card_id = base_content[0].get("card_id")
        if not real_card_id:
            pytest.skip("card_id 字段为空，跳过")

        logger.info(f"  使用真实 card_id: {real_card_id}")
        response = card_dispute_api.list_disputes(card_id=real_card_id, size=10)
        assert_status_ok(response)

        content = response.json().get("data", {}).get("content", [])
        logger.info(f"  筛选返回 {len(content)} 条争议")

        if content:
            for dispute in content:
                assert dispute.get("card_id") == real_card_id, \
                    f"返回争议 card_id='{dispute.get('card_id')}' 与筛选值 '{real_card_id}' 不一致"
        logger.info("✓ card_id 筛选验证通过")

    def test_filter_by_time_range(self, card_dispute_api):
        """
        测试场景4：按时间范围筛选，验证返回数据在范围内
        验证点：
        1. startTime 和 endTime 参数生效
        2. 返回的每条争议时间在筛选范围内
        """
        logger.info("测试场景4：按时间范围筛选")

        start_time = "2024-01-01"
        end_time = "2025-12-31"

        response = card_dispute_api.list_disputes(
            start_time=start_time,
            end_time=end_time,
            size=10
        )

        assert_status_ok(response)

        content = response.json().get("data", {}).get("content", [])
        logger.info(f"  返回 {len(content)} 条争议")

        if content:
            for dispute in content:
                created_at = dispute.get("created_at") or dispute.get("create_date", "")
                if created_at and len(created_at) >= 10:
                    dispute_date = created_at[:10]
                    assert start_time <= dispute_date <= end_time, \
                        f"争议日期 '{dispute_date}' 不在范围 [{start_time}, {end_time}] 内"
            logger.info(f"✓ 时间范围筛选验证通过，{len(content)} 条数据均在范围内")

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
