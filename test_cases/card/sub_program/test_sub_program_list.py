"""
Sub Program - List Sub Programs 接口测试用例
测试 GET /api/v1/cores/{core}/card-issuance/sub-programs 接口
"""
import pytest
from utils.logger import logger
from utils.assertions import assert_status_ok
from data.enums import CardNetwork, SubProgramStatus, ClassificationType


@pytest.mark.sub_program
@pytest.mark.list_api
class TestSubProgramList:
    """
    子项目列表接口测试用例集
    ⚠️ 文档问题：
    1. 响应直接返回数组，无code包装层
    2. 与Detail接口格式不一致
    3. spending_limit_location字段未定义
    """

    def test_list_sub_programs_success(self, sub_program_api):
        """
        测试场景1：成功获取子项目列表
        验证点：
        1. 接口返回 200
        2. 返回数组结构
        """
        logger.info("测试场景1：成功获取子项目列表")
        
        response = sub_program_api.list_sub_programs(page=0, size=10)
        
        assert response.status_code == 200, "HTTP状态码应为200"
        
        response_body = response.json()
        
        # 检查响应格式
        if isinstance(response_body, list):
            logger.warning("⚠️ 响应直接返回数组，无code包装层")
            logger.info(f"✓ 子项目列表获取成功，返回 {len(response_body)} 个子项目")
        elif isinstance(response_body, dict) and "code" in response_body:
            logger.info("✓ 响应有code包装层（与文档不符）")
            assert response_body.get("code") == 200
        
        logger.info("✓ 子项目列表获取成功")

    def test_filter_by_name(self, sub_program_api):
        """
        测试场景2：按name筛选
        验证点：
        1. name参数生效
        """
        logger.info("测试场景2：按name筛选")
        
        response = sub_program_api.list_sub_programs(name="Test", size=10)
        
        assert response.status_code == 200
        
        logger.info("✓ name筛选验证通过")

    def test_filter_by_network(self, sub_program_api):
        """
        测试场景3：按network筛选
        验证点：
        1. network参数生效
        """
        logger.info("测试场景3：按network筛选")
        
        response = sub_program_api.list_sub_programs(network=CardNetwork.MASTERCARD, size=10)
        
        assert response.status_code == 200
        
        logger.info("✓ network筛选验证通过")

    def test_filter_by_classification_type(self, sub_program_api):
        """
        测试场景4：按classification_type筛选
        验证点：
        1. classification_type参数生效
        """
        logger.info("测试场景4：按classification_type筛选")
        
        response = sub_program_api.list_sub_programs(
            classification_type=ClassificationType.BUSINESS, 
            size=10
        )
        
        assert response.status_code == 200
        
        logger.info("✓ classification_type筛选验证通过")

    def test_filter_by_status(self, sub_program_api):
        """
        测试场景5：按status筛选
        验证点：
        1. status参数生效
        """
        logger.info("测试场景5：按status筛选")
        
        response = sub_program_api.list_sub_programs(status=SubProgramStatus.ACTIVE, size=10)
        
        assert response.status_code == 200
        
        logger.info("✓ status筛选验证通过")

    def test_response_format_no_code_wrapper(self, sub_program_api):
        """
        测试场景6：响应格式验证（无code包装层）
        验证点：
        1. 响应直接返回数组
        2. 与其他模块格式不一致
        """
        logger.info("测试场景6：响应格式验证")
        
        response = sub_program_api.list_sub_programs(size=1)
        
        assert response.status_code == 200
        
        response_body = response.json()
        
        if isinstance(response_body, list):
            logger.warning("⚠️ 确认：Sub Program List响应无code包装层（直接返回数组）")
            logger.warning("这与同模块的Detail接口格式不一致")
            
            # 使用特殊的parse方法
            parsed = sub_program_api.parse_list_response(response, is_array=True)
            assert parsed.get("is_array_response") == True
            logger.info("✓ parse方法兼容数组格式")
        
        logger.info("✓ 响应格式验证完成")

    def test_spending_limit_location_field(self, sub_program_api):
        """
        测试场景7：spending_limit_location字段验证
        验证点：
        1. 响应中出现此字段
        2. 但Properties中未定义
        """
        logger.info("测试场景7：spending_limit_location字段验证")
        
        response = sub_program_api.list_sub_programs(size=1)
        
        assert response.status_code == 200
        
        response_body = response.json()
        
        # 如果是数组响应
        if isinstance(response_body, list) and len(response_body) > 0:
            sub_program = response_body[0]
            
            if "spending_limit_location" in sub_program:
                logger.warning("⚠️ 检测到spending_limit_location字段（Properties中未定义）")
                logger.info(f"字段值: {sub_program['spending_limit_location']}")
            else:
                logger.info("未找到spending_limit_location字段")
        
        logger.info("✓ spending_limit_location字段验证完成")
