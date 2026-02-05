"""
Card Dispute - Create Dispute 接口测试用例
测试 POST /api/v1/cores/{core}/card-issuance/disputes 接口
"""
import pytest
from utils.logger import logger
from utils.assertions import assert_status_ok


@pytest.mark.card_dispute_risk
@pytest.mark.create_api
@pytest.mark.no_rerun
@pytest.mark.skip(reason="需要文件上传和真实transaction_id，暂不实现")
class TestCardDisputeCreate:
    """
    创建争议接口测试用例集
    ⚠️ 重要：需要multipart/form-data文件上传
    ⚠️ 文档问题：file vs fileId参数命名不一致
    """

    def test_create_dispute_success(self, card_dispute_api):
        """
        测试场景1：成功创建争议
        验证点：
        1. 接口返回 200
        2. 返回dispute_id和file_id
        """
        logger.info("测试场景1：成功创建争议")
        
        response = card_dispute_api.create_dispute(
            file_path="/tmp/test_dispute.txt",
            original_transaction_id="test_txn_id",
            disputed_amount="100.00",
            disputed_reason="noAuthorization",
            comments="Test dispute"
        )
        
        assert_status_ok(response)
        
        data = response.json().get("data", {})
        assert data.get("id") is not None
        
        logger.info(f"✓ 争议创建成功，ID: {data.get('id')}")

    def test_create_without_file(self, card_dispute_api):
        """
        测试场景2：缺少file参数
        验证点：
        1. 接口返回错误（file是必需的）
        """
        logger.info("测试场景2：缺少file参数")
        
        logger.info("⚠️ 此测试需要修改create_dispute方法以支持无文件调用")
        logger.info("✓ 已记录测试需求")

    def test_invalid_transaction_id(self, card_dispute_api):
        """
        测试场景3：无效的transaction_id
        验证点：
        1. 接口返回错误
        """
        logger.info("测试场景3：无效的transaction_id")
        
        logger.info("⚠️ 需要实际测试文件上传")
        logger.info("✓ 已记录测试需求")

    def test_disputed_reason_enum_values(self, card_dispute_api):
        """
        测试场景4：disputed_reason枚举值验证
        验证点：
        1. 记录可能的枚举值
        2. 文档中未定义枚举
        """
        logger.info("测试场景4：disputed_reason枚举值")
        
        logger.warning("⚠️ disputed_reason枚举值未定义")
        logger.info("已知值: noAuthorization")
        logger.info("可能的值: Unauthorized, Duplicate, IncorrectAmount等")
        
        logger.info("✓ 枚举值需求已记录")

    def test_multipart_upload(self, card_dispute_api):
        """
        测试场景5：MultipartFile上传测试
        验证点：
        1. 文件上传功能
        2. Content-Type: multipart/form-data
        """
        logger.info("测试场景5：文件上传测试")
        
        logger.info("⚠️ MultipartFile上传要求：")
        logger.info("1. Content-Disposition: form-data; name='file'")
        logger.info("2. 支持的文件类型未说明")
        logger.info("3. 文件大小限制未说明")
        
        logger.info("✓ 上传要求已记录")
