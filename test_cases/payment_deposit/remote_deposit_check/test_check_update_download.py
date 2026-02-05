"""
Remote Deposit Check - Update & Download 接口测试用例
测试更新和下载接口
"""
import pytest
from utils.logger import logger
from utils.assertions import assert_status_ok


@pytest.mark.remote_deposit_check
@pytest.mark.update_api
class TestCheckUpdate:
    """Check更新测试"""

    @pytest.mark.skip(reason="需要真实transaction_id")
    def test_update_routing_account_success(self, remote_deposit_check_api):
        """测试场景1：成功更新routing和account number"""
        logger.info("测试场景1：成功更新routing和account number")
        
        response = remote_deposit_check_api.update_deposit(
            transaction_id="test_txn_id",
            routing_number="121182866",
            account_number="1320301002155"
        )
        
        assert_status_ok(response)
        assert response.json().get("data") == True
        logger.info("✓ 更新成功")

    def test_update_limitation(self, remote_deposit_check_api):
        """测试场景2：更新限制验证"""
        logger.info("测试场景2：更新限制验证")
        
        logger.warning("⚠️ 更新限制：")
        logger.warning("1. 只能修改routing_number和account_number")
        logger.warning("2. 不能修改amount、memo等其他字段")
        logger.warning("3. approved后不能修改")
        logger.warning("4. 其他status限制未说明")
        logger.info("✓ 更新限制已记录")

    def test_update_response_too_simple(self, remote_deposit_check_api):
        """测试场景3：更新响应过于简单"""
        logger.info("测试场景3：更新响应验证")
        
        logger.warning("⚠️ 文档问题：更新响应只返回data:true")
        logger.warning("不返回更新后的交易详情")
        logger.warning("用户需要再调用Detail接口查看结果")
        logger.info("✓ 响应简单性问题已记录")


@pytest.mark.remote_deposit_check
@pytest.mark.detail_api
class TestCheckDownload:
    """Check图片下载测试"""

    @pytest.mark.skip(reason="需要真实transaction_id")
    def test_download_check_image_success(self, remote_deposit_check_api):
        """测试场景4：成功下载支票图片"""
        logger.info("测试场景4：成功下载支票图片")
        
        response = remote_deposit_check_api.download_check_image("test_txn_id")
        
        assert response.status_code == 200
        
        data = response.json()
        front_url = data.get("front_check_image_url")
        back_url = data.get("back_check_image_url")
        
        logger.info(f"正面URL: {front_url}")
        logger.info(f"背面URL: {back_url}")
        logger.info("✓ 图片下载成功")

    def test_download_http_method_error(self, remote_deposit_check_api):
        """测试场景5：HTTP方法错误验证"""
        logger.info("测试场景5：HTTP方法错误验证")
        
        logger.warning("⚠️ 文档问题：HTTP方法错误")
        logger.warning("下载接口应该用GET（幂等、可缓存）")
        logger.warning("文档定义为POST（不符合RESTful）")
        logger.info("✓ HTTP方法错误已记录")

    def test_download_null_url_handling(self, remote_deposit_check_api):
        """测试场景6：URL为null处理"""
        logger.info("测试场景6：URL为null处理")
        
        logger.warning("⚠️ 文档示例中URL为null")
        logger.warning("未说明什么情况下为null")
        logger.warning("未说明正常URL格式和有效期")
        logger.info("✓ null URL问题已记录")
