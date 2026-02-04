"""
Statement 相关 API 封装
遵循 API Object 模式，提供灵活的参数化接口
"""
import requests
from typing import Optional
from config.config import config


class StatementAPI:
    """
    Statement 管理 API 封装类
    """
    def __init__(self, session: Optional[requests.Session] = None):
        """
        初始化 StatementAPI
        
        Args:
            session: requests.Session 对象，如果传入则使用该 session 保持认证状态
        """
        self.base_url = config.base_url
        self.config = config
        self.session = session or requests.Session()

    def list_statements(
        self,
        financial_account_id: Optional[str] = None,
        year: Optional[str] = None,
        month: Optional[str] = None,
        page: int = 0,
        size: int = 10,
        **kwargs
    ) -> requests.Response:
        """
        获取 Statements 列表
        
        Args:
            financial_account_id: Financial Account ID，用于筛选
            year: 年份，用于筛选
            month: 月份，用于筛选
            page: 页码，默认为 0
            size: 每页大小，默认为 10
            **kwargs: 其他额外的查询参数
            
        Returns:
            requests.Response: 响应对象
            
        Example:
            # 基础查询
            response = statement_api.list_statements()
            
            # 按 Financial Account ID 筛选
            response = statement_api.list_statements(
                financial_account_id="1039475067069548"
            )
            
            # 按年月筛选
            response = statement_api.list_statements(
                year="2024",
                month="3"
            )
        """
        url = self.config.get_full_url("/statements")
        
        # 构建查询参数字典
        params = {
            "page": page,
            "size": size
        }
        
        # 添加可选参数（仅当值不为 None 时）
        if financial_account_id is not None:
            params["financial_account_id"] = financial_account_id
        if year is not None:
            params["year"] = year
        if month is not None:
            params["month"] = month
        
        # 添加其他额外参数
        params.update(kwargs)
        
        # 使用 session 发送 GET 请求
        response = self.session.get(url, params=params)
        
        return response

    def download_statement_file(self, statement_id: str) -> requests.Response:
        """
        下载 Statement 文件（返回 base64 编码的文件）
        
        Args:
            statement_id: Statement ID
            
        Returns:
            requests.Response: 响应对象，包含 base64 编码的文件内容
            
        Example:
            response = statement_api.download_statement_file("038x13")
            if response.status_code == 200:
                base64_file = response.json()
                print(f"File downloaded: {len(base64_file)} bytes")
        """
        url = self.config.get_full_url(f"/statements/{statement_id}")
        response = self.session.get(url)
        return response

    def parse_list_response(self, response: requests.Response) -> dict:
        """
        解析 Statements 列表响应，提取关键信息
        
        Args:
            response: requests.Response 对象
            
        Returns:
            dict: 包含 content（Statements 列表）、pageable（分页信息）、total_elements 等字段
            
        Example:
            response = statement_api.list_statements()
            parsed = statement_api.parse_list_response(response)
            statements = parsed['content']
            total = parsed['total_elements']
        """
        if response.status_code != 200:
            return {
                "error": True,
                "status_code": response.status_code,
                "message": response.text
            }
        
        try:
            data = response.json()
            # 兼容不同的响应结构
            if "data" in data:
                # 如果响应有 data 包装层
                content_data = data["data"]
            else:
                # 如果响应直接是数据
                content_data = data
            
            return {
                "error": False,
                "content": content_data.get("content", []),
                "pageable": content_data.get("pageable", {}),
                "total_elements": content_data.get("total_elements", 0),
                "total_pages": content_data.get("total_pages", 0),
                "size": content_data.get("size", 0),
                "number": content_data.get("number", 0),
                "first": content_data.get("first", False),
                "last": content_data.get("last", False),
                "empty": content_data.get("empty", True)
            }
        except Exception as e:
            return {
                "error": True,
                "message": f"Failed to parse response: {str(e)}",
                "raw_response": response.text
            }
