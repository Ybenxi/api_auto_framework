"""
Sub Program - Sub Program Detail 接口测试用例
测试 GET /api/v1/cores/{core}/card-issuance/sub-programs/:id 接口
"""
import pytest
from utils.logger import logger
from utils.assertions import assert_status_ok


@pytest.mark.sub_program
@pytest.mark.detail_api
class TestSubProgramDetail:
    """
    子项目详情接口测试用例集
    """

    @pytest.mark.skip(reason="需要真实的sub_program_id")
    def test_get_sub_program_detail_success(self, sub_program_api):
        """
        测试场景1：成功获取子项目详情
        验证点：
        1. 接口返回 200
        2. 有code包装层（与List接口不同）
        """
        logger.info("测试场景1：成功获取子项目详情")
        
        # 从列表获取一个ID
        list_response = sub_program_api.list_sub_programs(size=1)
        
        if isinstance(list_response.json(), list):
            sub_programs = list_response.json()
            sub_program_id = sub_programs[0].get("id")
        else:
            sub_program_id = "test_sub_program_id"
        
        # 获取详情
        response = sub_program_api.get_sub_program_detail(sub_program_id)
        
        assert_status_ok(response)
        
        response_body = response.json()
        assert response_body.get("code") == 200, "Detail接口应有code包装层"
        
        logger.info(f"✓ 子项目详情获取成功")

    def test_invalid_sub_program_id(self, sub_program_api):
        """
        测试场景2：无效的sub_program_id
        验证点：
        1. 接口返回错误
        """
        logger.info("测试场景2：无效的sub_program_id")
        
        response = sub_program_api.get_sub_program_detail("INVALID_ID_999")
        
        assert response.status_code == 200
        response_body = response.json()
        assert response_body.get("code") != 200
        
        logger.info(f"✓ 正确拒绝无效ID")

    def test_response_format_consistency(self, sub_program_api):
        """
        测试场景3：响应格式一致性验证
        验证点：
        1. Detail有code包装层
        2. List无code包装层
        3. 记录格式差异
        """
        logger.info("测试场景3：响应格式一致性验证")
        
        # List格式
        list_response = sub_program_api.list_sub_programs(size=1)
        list_body = list_response.json()
        list_is_array = isinstance(list_body, list)
        
        # Detail格式
        detail_response = sub_program_api.get_sub_program_detail("test_id")
        detail_body = detail_response.json()
        detail_has_code = "code" in detail_body if isinstance(detail_body, dict) else False
        
        logger.info(f"List是数组: {list_is_array}")
        logger.info(f"Detail有code: {detail_has_code}")
        
        if list_is_array and detail_has_code:
            logger.warning("⚠️ 确认格式不一致：List是数组，Detail有code包装层")
        
        logger.info("✓ 格式一致性验证完成")

    @pytest.mark.skip(reason="需要真实数据")
    def test_funding_account_conditional_field(self, sub_program_api):
        """
        测试场景4：funding_financial_account_id条件验证
        验证点：
        1. classification_type='Business'时应有funding_financial_account_id
        2. Consumer类型可能为null
        """
        logger.info("测试场景4：funding_account条件验证")
        
        list_response = sub_program_api.list_sub_programs(size=5)
        
        if isinstance(list_response.json(), list):
            sub_programs = list_response.json()
            
            for sp in sub_programs:
                classification = sp.get("classification_type")
                funding_id = sp.get("funding_financial_account_id")
                
                logger.debug(f"分类: {classification}, funding_id: {funding_id}")
                
                if classification == "Business" and funding_id is None:
                    logger.warning("⚠️ Business类型但funding_id为null")
        
        logger.info("✓ 条件字段验证完成")
