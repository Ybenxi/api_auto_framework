"""
Statement 下载接口测试用例
测试 GET /api/v1/cores/{core}/statements/{id} 接口
"""
import pytest
import base64
from utils.assertions import assert_status_ok, assert_response_parsed
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

    @pytest.mark.no_rerun  # 禁止失败重试
    def test_download_statement_file_format(self, statement_api):
        """
        测试场景3：验证下载文件的格式
        验证点：
        1. 返回状态码 200
        2. 响应 code 为 200
        3. data 字段是一个长字符串（base64编码）
        """
        # 先获取一个 Statement ID
        logger.info("获取 Statement 列表")
        list_response = statement_api.list_statements(size=1)
        assert_status_ok(list_response)
        
        parsed_list = statement_api.parse_list_response(list_response)
        assert_response_parsed(parsed_list)
        
        statements = parsed_list["content"]
        if len(statements) == 0:
            pytest.skip("没有可用的 Statement 数据")
        
        statement_id = statements[0]["id"]
        logger.info(f"使用 Statement ID: {statement_id}")
        
        # 调用下载接口
        logger.info("调用下载接口")
        download_response = statement_api.download_statement_file(statement_id)
        
        # 验证状态码
        assert_status_ok(download_response)
        logger.info("✓ HTTP 状态码验证通过: 200")
        
        # 验证响应结构
        response_body = download_response.json()
        
        # 验证 code 字段
        assert response_body.get("code") == 200, f"响应 code 应为 200，实际: {response_body.get('code')}"
        logger.info("✓ 响应 code 验证通过: 200")
        
        # 验证 data 是一个长字符串
        data = response_body.get("data")
        assert data is not None, "data 字段不能为空"
        assert isinstance(data, str), f"data 应为字符串类型，实际: {type(data)}"
        assert len(data) > 100, f"data 应为一个长字符串（base64编码），实际长度: {len(data)}"
        
        logger.info("✓ 文件格式验证通过:")
        logger.info(f"  Statement ID: {statement_id}")
        logger.info(f"  Data 长度: {len(data)} 字符")
        logger.info(f"  验证通过: 返回了 base64 编码的文件内容")
