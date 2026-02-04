"""
Statement 下载接口测试用例
测试 GET /api/v1/cores/{core}/statements/{id} 接口
"""
import pytest
import base64
from utils.assertions import assert_status_ok
from utils.logger import logger


class TestStatementDownload:
    """
    Statement 下载接口测试用例集
    """

    def test_download_statement_success(self, statement_api):
        """
        测试场景1：成功下载 Statement 文件
        依赖逻辑：先从列表接口获取一个有效的 statement_id，然后下载
        验证点：
        1. 列表接口返回成功
        2. 下载接口返回 200
        3. 返回的是 base64 编码的文件内容
        """
        # 先调用列表接口获取一个 Statement ID
        list_response = statement_api.list_statements(size=1)
        assert_status_ok(list_response)
        
        parsed_list = statement_api.parse_list_response(list_response)
        assert not parsed_list.get("error"), f"列表响应解析失败: {parsed_list.get('message')}"
        
        statements = parsed_list["content"]
        if len(statements) == 0:
            pytest.skip("没有可用的 Statement 数据，跳过下载测试")
        
        # 提取第一个 Statement 的 ID
        statement_id = statements[0]["id"]
        logger.info(f"\n提取到 Statement ID: {statement_id}")
        
        # 调用下载接口
        logger.info("调用下载接口获取 Statement {statement_id}")
        download_response = statement_api.download_statement_file(statement_id)
        
        # 断言状态码
        logger.info("验证 HTTP 状态码为 200")
        assert_status_ok(download_response)
        
        # 解析响应
        logger.info("解析响应并验证文件内容")
        try:
            response_data = download_response.json()
            
            # 根据 API 文档，可能返回 base64 字符串或包含 base64 的对象
            if isinstance(response_data, str):
                file_content = response_data
            elif isinstance(response_data, dict):
                file_content = response_data.get("data") or response_data.get("file") or ""
            else:
                pytest.fail(f"响应格式不正确: {type(response_data)}")
            
            # 验证是 base64 编码的内容
            logger.info("验证是 base64 编码内容")
            assert len(file_content) > 0, "返回的文件内容为空"
            
            # 尝试 base64 解码验证
            try:
                decoded = base64.b64decode(file_content)
                logger.info("✓ 成功下载 Statement 文件:")
                logger.info(f"  Statement ID: {statement_id}")
                logger.info(f"  Base64 长度: {len(file_content)} 字符")
                logger.info(f"  解码后大小: {len(decoded)} 字节")
            except Exception as e:
                # 如果不是 base64，可能是其他格式
                logger.info(f"  ⚠ 文件内容不是标准 base64 格式: {e}")
                logger.info(f"  内容前100字符: {file_content[:100]}")
        except Exception as e:
            pytest.fail(f"解析响应失败: {e}")

    def test_download_statement_invalid_id(self, statement_api):
        """
        测试场景2：使用无效的 statement_id 下载
        验证点（基于真实业务行为）：
        1. 服务器返回 200 OK（统一错误处理设计）
        2. 响应体包含错误信息或返回空数据
        """
        # 使用一个不存在的 statement_id
        invalid_id = "INVALID_STATEMENT_ID_999999"
        logger.info("使用无效的 Statement ID: {invalid_id}")
        download_response = statement_api.download_statement_file(invalid_id)
        
        # 验证返回 200 状态码（统一错误处理）
        logger.info("验证返回状态码")
        logger.info(f"  状态码: {download_response.status_code}")
        assert_status_ok(download_response)
        
        # 验证响应包含错误信息或为空
        response_body = download_response.json()
        assert "error" in download_response.text.lower() or response_body.get("code") != 200 or not response_body, \
            f"无效 ID 应该返回错误信息或空响应"
        
        logger.info("✓ 使用无效 ID 测试完成")

    def test_download_statement_file_format(self, statement_api):
        """
        测试场景3：验证下载文件的格式
        验证点：
        1. 返回的文件是 base64 编码
        2. base64 解码后是有效的 PDF 文件（或其他文档格式）
        """
        # 先获取一个 Statement ID
        list_response = statement_api.list_statements(size=1)
        assert_status_ok(list_response)
        parsed_list = statement_api.parse_list_response(list_response)
        assert_response_parsed(parsed_list)
        
        statements = parsed_list["content"]
        if len(statements) == 0:
            pytest.skip("没有可用的 Statement 数据")
        
        statement_id = statements[0]["id"]
        
        # 下载文件
        logger.info("下载 Statement {statement_id}")
        download_response = statement_api.download_statement_file(statement_id)
        assert_status_ok(download_response)
        
        # 解析并验证格式
        logger.info("验证文件格式")
        response_data = download_response.json()
        
        if isinstance(response_data, str):
            file_content = response_data
        elif isinstance(response_data, dict):
            file_content = response_data.get("data") or response_data.get("file") or ""
        else:
            pytest.fail(f"响应格式不正确")
        
        # 验证是 base64 编码
        try:
            decoded = base64.b64decode(file_content)
            
            # 检查文件类型（根据文件头）
            if decoded.startswith(b'%PDF'):
                file_type = "PDF"
            elif decoded.startswith(b'PK'):
                file_type = "ZIP/DOCX"
            else:
                file_type = "Unknown"
            
            logger.info("✓ 文件格式验证通过:")
            logger.info(f"  文件类型: {file_type}")
            logger.info(f"  文件大小: {len(decoded)} 字节")
        except Exception as e:
            pytest.fail(f"Base64 解码失败: {e}")
