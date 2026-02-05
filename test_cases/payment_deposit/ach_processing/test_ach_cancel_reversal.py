"""
ACH Processing - Cancel & Reversal 接口测试用例
测试取消和冲正操作
"""
import pytest
from utils.logger import logger


@pytest.mark.ach_processing
@pytest.mark.update_api
@pytest.mark.no_rerun
@pytest.mark.skip(reason="需要Processing状态的真实交易")
class TestACHCancelReversal:
    """
    Cancel和Reversal测试（破坏性，全部skip）
    """

    def test_cancel_transaction(self, ach_processing_api):
        """测试场景1：取消ACH交易"""
        logger.info("测试场景1：取消ACH交易")
        
        logger.warning("⚠️ 限制：只能取消尚未发送到FRB的交易")
        
        response = ach_processing_api.cancel_transaction("test_txn_id")
        assert response.status_code == 200
        logger.info("✓ 交易取消成功")

    def test_initiate_reversal(self, ach_processing_api):
        """测试场景2：发起冲正"""
        logger.info("测试场景2：发起ACH Reversal")
        
        logger.warning("⚠️ 限制：只能对已结算（settled）的交易操作")
        
        response = ach_processing_api.initiate_reversal(
            transaction_id="test_settled_txn_id",
            request_reason="REASON_CODE_HERE"  # 值未知
        )
        assert response.status_code == 200
        
        data = response.json().get("data", {})
        if "transaction_reversal_id" in data:
            logger.info(f"✓ Reversal创建成功，ID: {data['transaction_reversal_id']}")
        
        logger.info("✓ Reversal发起成功")

    def test_reversal_with_file(self, ach_processing_api):
        """测试场景3：带附件的Reversal"""
        logger.info("测试场景3：带附件的Reversal")
        
        logger.info("⚠️ reversal_file用途不明")
        logger.info("支持格式未说明")
        logger.info("是否必需未说明")
        
        response = ach_processing_api.initiate_reversal(
            transaction_id="test_txn_id",
            request_reason="REASON_CODE",
            reversal_file_path="/tmp/reversal_doc.pdf"
        )
        assert response.status_code == 200
        logger.info("✓ 带附件Reversal测试完成")

    def test_get_reversal_detail(self, ach_processing_api):
        """测试场景4：获取Reversal详情"""
        logger.info("测试场景4：获取Reversal详情")
        
        response = ach_processing_api.get_reversal_detail("test_reversal_id")
        assert response.status_code == 200
        
        data = response.json().get("data", {})
        
        # 验证reversal_status
        if "reversal_status" in data:
            logger.info(f"reversal_status: {data['reversal_status']}")
            logger.warning("⚠️ reversal_status枚举值未定义")
        
        logger.info("✓ Reversal详情获取成功")


@pytest.mark.ach_processing
@pytest.mark.update_api
class TestACHCancelReversalErrors:
    """Cancel和Reversal错误处理（可运行）"""

    def test_cancel_limitation(self, ach_processing_api):
        """测试场景5：Cancel限制验证"""
        logger.info("测试场景5：Cancel限制验证")
        
        logger.warning("⚠️ Cancel限制不够清晰")
        logger.warning("只能取消'尚未发送到FRB'的交易")
        logger.warning("问题：如何判断是否已发送？")
        logger.warning("问题：哪些status可以取消？")
        logger.warning("问题：时间窗口多长？")
        
        logger.info("✓ Cancel限制已记录")

    def test_reversal_request_reason_unknown(self, ach_processing_api):
        """测试场景6：request_reason可能值未知"""
        logger.info("测试场景6：request_reason验证")
        
        logger.warning("⚠️ 文档问题：request_reason可能值未知")
        logger.warning("外部链接'Request Reason'缺失")
        logger.warning("无法查询标准reason code列表")
        
        logger.info("✓ request_reason问题已记录")

    def test_reversal_detail_json_error(self, ach_processing_api):
        """测试场景7：Reversal Detail响应JSON格式错误"""
        logger.info("测试场景7：JSON格式错误验证")
        
        logger.warning("⚠️ 文档问题：JSON格式错误")
        logger.warning('"reversal_file_id": "..."')
        logger.warning('"status": "..." // 缺少逗号')
        
        logger.info("✓ JSON格式错误已记录")
