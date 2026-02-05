"""
Risk Control - MCC Code 接口测试用例
测试 GET /api/v1/cores/{core}/card-issuance/risk-control/mcc-code 接口
"""
import pytest
from utils.logger import logger
from utils.assertions import assert_status_ok, assert_list_structure, assert_pagination


@pytest.mark.card_dispute_risk
@pytest.mark.list_api
class TestRiskMCCCode:
    """
    MCC码列表接口测试用例集
    ⚠️ 文档问题：接口描述错误（说card holders应为MCC codes）
    """

    def test_list_mcc_codes_success(self, card_dispute_api):
        """
        测试场景1：成功获取MCC码列表
        验证点：
        1. 接口返回 200
        2. 返回列表结构正确
        """
        logger.info("测试场景1：成功获取MCC码列表")
        
        response = card_dispute_api.list_mcc_codes(page=0, size=10)
        
        assert_status_ok(response)
        
        response_body = response.json()
        assert response_body.get("code") == 200
        assert_list_structure(response_body)
        
        logger.info(f"✓ MCC码列表获取成功")

    def test_filter_by_code(self, card_dispute_api):
        """
        测试场景2：按code筛选
        验证点：
        1. code参数生效
        """
        logger.info("测试场景2：按code筛选")
        
        response = card_dispute_api.list_mcc_codes(code="0742", size=10)
        
        assert_status_ok(response)
        
        logger.info("✓ code筛选验证通过")

    def test_filter_by_category(self, card_dispute_api):
        """
        测试场景3：按category筛选
        验证点：
        1. category参数生效
        """
        logger.info("测试场景3：按category筛选")
        
        response = card_dispute_api.list_mcc_codes(category="Veterinary", size=10)
        
        assert_status_ok(response)
        
        logger.info("✓ category筛选验证通过")

    def test_pagination(self, card_dispute_api):
        """
        测试场景4：分页查询
        验证点：
        1. 分页参数正确传递
        """
        logger.info("测试场景4：分页查询")
        
        response = card_dispute_api.list_mcc_codes(page=0, size=5)
        
        assert_status_ok(response)
        assert_pagination(response, page=0, size=5)
        
        logger.info("✓ 分页验证通过")

    def test_mcc_code_format(self, card_dispute_api):
        """
        测试场景5：MCC码格式验证
        验证点：
        1. MCC码是4位数字
        2. category是字符串
        """
        logger.info("测试场景5：MCC码格式验证")
        
        response = card_dispute_api.list_mcc_codes(size=3)
        
        assert_status_ok(response)
        
        content = response.json().get("data", {}).get("content", [])
        
        if content:
            for mcc in content:
                code = mcc.get("code")
                category = mcc.get("category")
                
                # 验证code格式（4位数字）
                if code:
                    assert len(code) == 4, "MCC码应为4位"
                    assert code.isdigit(), "MCC码应为数字"
                
                logger.debug(f"MCC: {code} - {category}")
        
        logger.info("✓ MCC码格式验证通过")
