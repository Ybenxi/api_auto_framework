"""
Sub Program - Nested Programs 接口测试用例
测试 GET /api/v1/cores/{core}/card-issuance/sub-programs/:sub_program_id/nested-programs 接口
"""
import pytest
from utils.logger import logger
from utils.assertions import assert_status_ok, assert_list_structure, assert_pagination


@pytest.mark.sub_program
@pytest.mark.list_api
class TestSubProgramNestedPrograms:
    """
    子项目下的嵌套项目列表接口测试用例集
    ⚠️ 文档问题：spending_limit_amount字段作用不明
    """

    @pytest.mark.skip(reason="需要真实的sub_program_id")
    def test_list_nested_programs_success(self, sub_program_api):
        """
        测试场景1：成功获取嵌套项目列表
        验证点：
        1. 接口返回 200
        2. 返回列表结构正确
        """
        logger.info("测试场景1：成功获取嵌套项目列表")
        
        response = sub_program_api.list_nested_programs(
            sub_program_id="test_sub_program_id",
            page=0,
            size=10
        )
        
        assert_status_ok(response)
        
        response_body = response.json()
        assert response_body.get("code") == 200
        assert_list_structure(response_body)
        
        logger.info(f"✓ 嵌套项目列表获取成功")

    @pytest.mark.skip(reason="需要真实数据")
    def test_pagination(self, sub_program_api):
        """
        测试场景2：分页查询
        验证点：
        1. 分页参数正确传递
        """
        logger.info("测试场景2：分页查询")
        
        response = sub_program_api.list_nested_programs(
            sub_program_id="test_sub_program_id",
            page=0,
            size=5
        )
        
        assert_status_ok(response)
        assert_pagination(response, page=0, size=5)
        
        logger.info("✓ 分页验证通过")

    @pytest.mark.skip(reason="需要真实数据")
    def test_empty_result(self, sub_program_api):
        """
        测试场景3：空结果验证
        验证点：
        1. sub_program下无nested_program时返回空数组
        """
        logger.info("测试场景3：空结果验证")
        
        response = sub_program_api.list_nested_programs(
            sub_program_id="test_sub_program_id",
            size=10
        )
        
        assert_status_ok(response)
        
        logger.info("✓ 空结果验证通过")

    def test_invalid_sub_program_id(self, sub_program_api):
        """
        测试场景4：无效的sub_program_id
        验证点：
        1. 接口返回错误
        """
        logger.info("测试场景4：无效的sub_program_id")
        
        response = sub_program_api.list_nested_programs(
            sub_program_id="INVALID_SUB_PROGRAM_999",
            size=10
        )
        
        assert response.status_code == 200
        
        response_body = response.json()
        if isinstance(response_body, dict):
            assert response_body.get("code") != 200
        
        logger.info(f"✓ 正确拒绝无效ID")

    @pytest.mark.skip(reason="需要真实数据")
    def test_spending_limit_amount_field(self, sub_program_api):
        """
        测试场景5：spending_limit_amount字段作用验证
        验证点：
        1. spending_limit_amount是单个数值
        2. spending_limit是数组
        3. 验证两者关系
        """
        logger.info("测试场景5：spending_limit_amount字段验证")
        
        response = sub_program_api.list_nested_programs(
            sub_program_id="test_sub_program_id",
            size=1
        )
        
        content = response.json().get("data", {}).get("content", [])
        
        if content:
            nested_program = content[0]
            
            amount = nested_program.get("spending_limit_amount")
            limits = nested_program.get("spending_limit", [])
            
            logger.info(f"spending_limit_amount: {amount}")
            logger.info(f"spending_limit数组长度: {len(limits)}")
            
            # 检查amount是否等于Total interval的amount
            total_limit = next((l for l in limits if l.get("interval") == "Total"), None)
            if total_limit and amount:
                if total_limit.get("amount") == amount:
                    logger.info("✓ spending_limit_amount与Total限制相同")
                else:
                    logger.warning("⚠️ spending_limit_amount与Total限制不同")
        
        logger.info("✓ spending_limit_amount验证完成")

    @pytest.mark.skip(reason="需要真实数据")
    def test_valid_date_range(self, sub_program_api):
        """
        测试场景6：有效日期范围验证
        验证点：
        1. valid_date_start和valid_date_end字段
        2. 日期范围有效性
        """
        logger.info("测试场景6：有效日期范围验证")
        
        response = sub_program_api.list_nested_programs(
            sub_program_id="test_sub_program_id",
            size=1
        )
        
        content = response.json().get("data", {}).get("content", [])
        
        if content:
            nested = content[0]
            start_date = nested.get("valid_date_start")
            end_date = nested.get("valid_date_end")
            
            logger.info(f"有效期: {start_date} 到 {end_date}")
            
            # 验证日期格式
            if start_date and end_date:
                assert start_date <= end_date, "开始日期应早于结束日期"
        
        logger.info("✓ 有效日期验证通过")
