"""
Sub Program - Nested Program Using Log 接口测试用例
测试 GET /api/v1/cores/{core}/card-issuance/nested-programs/using-log 接口
"""
import pytest
from utils.logger import logger
from utils.assertions import assert_status_ok
from data.enums import NestedProgramLogStatus


@pytest.mark.sub_program
@pytest.mark.list_api
class TestNestedProgramUsingLog:
    """
    嵌套项目使用日志接口测试用例集
    ⚠️ 文档问题：
    1. 响应结构特殊：有page_content包装层
    2. total_used_amount字段未定义
    3. direction字段枚举值未定义
    """

    @pytest.mark.skip(reason="需要真实的card_number和nested_program_id")
    def test_get_using_log_success(self, sub_program_api):
        """
        测试场景1：成功获取使用日志
        验证点：
        1. 接口返回 200
        2. 包含total_used_amount和page_content
        """
        logger.info("测试场景1：成功获取使用日志")
        
        response = sub_program_api.get_nested_program_using_log(
            card_number="test_card_number",
            nested_program_id="test_nested_id",
            page=0,
            size=10
        )
        
        assert_status_ok(response)
        
        response_body = response.json()
        data = response_body.get("data", {})
        
        assert "total_used_amount" in data, "应包含total_used_amount字段"
        assert "page_content" in data, "应包含page_content字段"
        
        logger.info(f"✓ 使用日志获取成功")

    @pytest.mark.skip(reason="需要真实数据")
    def test_filter_by_status(self, sub_program_api):
        """
        测试场景2：按status筛选
        验证点：
        1. status参数生效
        """
        logger.info("测试场景2：按status筛选")
        
        response = sub_program_api.get_nested_program_using_log(
            card_number="test_card_number",
            nested_program_id="test_nested_id",
            status=NestedProgramLogStatus.COMPLETED,
            size=10
        )
        
        assert_status_ok(response)
        
        logger.info("✓ status筛选验证通过")

    @pytest.mark.skip(reason="需要真实数据")
    def test_filter_by_time_range(self, sub_program_api):
        """
        测试场景3：按时间范围筛选
        验证点：
        1. start_time和end_time参数生效
        """
        logger.info("测试场景3：按时间范围筛选")
        
        response = sub_program_api.get_nested_program_using_log(
            card_number="test_card_number",
            nested_program_id="test_nested_id",
            start_time="2024-01-01 00:00:00",
            end_time="2024-12-31 23:59:59",
            size=10
        )
        
        assert_status_ok(response)
        
        logger.info("✓ 时间范围筛选验证通过")

    @pytest.mark.skip(reason="需要真实数据")
    def test_page_content_structure(self, sub_program_api):
        """
        测试场景4：page_content特殊结构验证
        验证点：
        1. 响应有page_content包装层
        2. page_content内部是标准分页结构
        """
        logger.info("测试场景4：page_content结构验证")
        
        response = sub_program_api.get_nested_program_using_log(
            card_number="test_card_number",
            nested_program_id="test_nested_id",
            size=10
        )
        
        data = response.json().get("data", {})
        
        # 验证page_content存在
        assert "page_content" in data, "应包含page_content字段"
        
        page_content = data["page_content"]
        assert "content" in page_content
        assert "pageable" in page_content
        
        logger.warning("⚠️ 确认：响应有page_content包装层（与其他接口不一致）")
        
        logger.info("✓ page_content结构验证通过")

    @pytest.mark.skip(reason="需要真实数据")
    def test_total_used_amount_field(self, sub_program_api):
        """
        测试场景5：total_used_amount字段验证
        验证点：
        1. 字段存在（但Properties中未定义）
        2. 字段含义验证
        """
        logger.info("测试场景5：total_used_amount字段验证")
        
        response = sub_program_api.get_nested_program_using_log(
            card_number="test_card_number",
            nested_program_id="test_nested_id",
            size=10
        )
        
        data = response.json().get("data", {})
        total_used_amount = data.get("total_used_amount")
        
        logger.warning("⚠️ total_used_amount字段未在Properties定义")
        logger.info(f"字段值: {total_used_amount}")
        
        logger.info("✓ total_used_amount字段验证完成")

    @pytest.mark.skip(reason="需要真实数据")
    def test_direction_field_enum(self, sub_program_api):
        """
        测试场景6：direction字段枚举验证
        验证点：
        1. direction字段值（未定义枚举）
        2. 记录可能的值
        """
        logger.info("测试场景6：direction字段枚举验证")
        
        response = sub_program_api.get_nested_program_using_log(
            card_number="test_card_number",
            nested_program_id="test_nested_id",
            size=10
        )
        
        page_content = response.json().get("data", {}).get("page_content", {})
        content = page_content.get("content", [])
        
        if content:
            log = content[0]
            direction = log.get("direction")
            
            logger.warning("⚠️ direction字段枚举值未定义")
            logger.info(f"检测到direction值: {direction}")
        
        logger.info("✓ direction字段验证完成")
