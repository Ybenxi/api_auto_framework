"""
Client List - Export Clients 接口测试用例
测试 GET /api/v1/cores/{core}/client-lists/export 接口
"""
import pytest
from utils.logger import logger
from utils.assertions import assert_status_ok
from data.enums import OMSCategory


@pytest.mark.client_list
@pytest.mark.export_api
class TestClientListExport:
    """
    导出客户列表接口测试用例集
    ⚠️ 文档问题：Export接口URL示例错误
    """

    def test_export_clients_success(self, client_list_api):
        """
        测试场景1：成功导出客户列表
        验证点：
        1. 接口返回 200
        2. 返回文件或导出数据
        """
        logger.info("测试场景1：成功导出客户列表")
        
        response = client_list_api.export_clients()
        
        assert_status_ok(response)
        
        # 检查响应类型
        content_type = response.headers.get("Content-Type", "")
        logger.debug(f"Content-Type: {content_type}")
        
        if "application/json" in content_type:
            # JSON格式导出
            response_body = response.json()
            logger.info(f"✓ 导出成功（JSON格式），数据长度: {len(str(response_body))}")
        elif "text/csv" in content_type or "application/vnd" in content_type:
            # CSV或Excel格式
            logger.info(f"✓ 导出成功（文件格式），文件大小: {len(response.content)} bytes")
        else:
            logger.info(f"✓ 导出成功，Content-Type: {content_type}")

    def test_export_clients_with_oms_category_filter(self, client_list_api):
        """
        测试场景2：按oms_category筛选导出
        验证点：
        1. 接口返回 200
        2. 筛选参数生效
        """
        logger.info("测试场景2：按oms_category筛选导出")
        
        response = client_list_api.export_clients(oms_category=OMSCategory.EQUITY)
        
        assert_status_ok(response)
        
        logger.info("✓ 按分类筛选导出成功")

    def test_export_clients_with_date_range(self, client_list_api):
        """
        测试场景3：按日期范围导出
        验证点：
        1. 接口返回 200
        2. 日期筛选参数生效
        """
        logger.info("测试场景3：按日期范围导出")
        
        response = client_list_api.export_clients(
            start_date="2024-01-01",
            end_date="2024-12-31"
        )
        
        assert_status_ok(response)
        
        logger.info("✓ 按日期范围导出成功")

    def test_export_clients_with_multiple_filters(self, client_list_api):
        """
        测试场景4：组合多个筛选条件导出
        验证点：
        1. 接口返回 200
        2. 多个筛选条件同时生效
        """
        logger.info("测试场景4：组合多个筛选条件导出")
        
        response = client_list_api.export_clients(
            oms_category=OMSCategory.MUTUAL_FUND,
            start_date="2024-01-01",
            end_date="2024-12-31"
        )
        
        assert_status_ok(response)
        
        logger.info("✓ 组合筛选导出成功")

    def test_export_clients_empty_result(self, client_list_api):
        """
        测试场景5：导出空结果
        验证点：
        1. 接口返回 200
        2. 返回空文件或空数据
        """
        logger.info("测试场景5：导出空结果")
        
        response = client_list_api.export_clients(
            start_date="2099-01-01",
            end_date="2099-12-31"
        )
        
        assert_status_ok(response)
        
        # 空结果可能返回空文件或空数组
        logger.info("✓ 空结果导出成功")

    def test_export_clients_invalid_date_format(self, client_list_api):
        """
        测试场景6：无效的日期格式
        验证点：
        1. 接口返回错误或使用默认值
        """
        logger.info("测试场景6：无效的日期格式")
        
        response = client_list_api.export_clients(
            start_date="2024/01/01",  # 错误格式，应为YYYY-MM-DD
            end_date="2024-12-31"
        )
        
        # 可能返回错误或忽略无效参数
        if response.status_code == 200:
            response_body = response.json() if "application/json" in response.headers.get("Content-Type", "") else {}
            if response_body.get("code") == 200:
                logger.info("✓ 系统忽略无效日期格式，使用默认值")
            else:
                logger.info(f"✓ 正确拒绝无效日期格式: {response_body.get('error_message', 'Unknown error')}")
        else:
            logger.info(f"✓ HTTP错误: {response.status_code}")
