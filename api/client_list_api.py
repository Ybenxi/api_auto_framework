"""
Client List 相关 API 封装
提供客户列表的查询、创建、更新、导出等功能
遵循 API Object 模式，提供灵活的参数化接口

⚠️ 文档问题：
- 响应结构定义混乱（60+字段平铺）
- 嵌套层级关系不清晰
- 类型定义混乱（string vs int）
- 分页字段命名不一致（驼峰vs下划线）
"""
import requests
from typing import Optional, Union, List
from config.config import config
from data.enums import OMSCategory
from utils.logger import logger


class ClientListAPI:
    """
    Client List 管理 API 封装类
    包含客户列表的查询、管理、导出等功能
    """
    def __init__(self, session: Optional[requests.Session] = None):
        """
        初始化 ClientListAPI
        
        Args:
            session: requests.Session 对象，如果传入则使用该 session 保持认证状态
        """
        self.base_url = config.base_url
        self.config = config
        self.session = session or requests.Session()

    # ==================== 客户列表查询接口 ====================
    
    def list_clients(
        self,
        oms_category: Optional[Union[str, OMSCategory]] = None,
        account_name: Optional[str] = None,
        account_id: Optional[str] = None,
        sub_account_name: Optional[str] = None,
        financial_account_name: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        page: int = 0,
        size: int = 10,
        **kwargs
    ) -> requests.Response:
        """
        获取客户列表
        
        Args:
            oms_category: OMS分类（Equity/Mutual Fund/Crypto Currency等）
            account_name: Account名称，用于筛选
            account_id: Account ID，用于筛选
            sub_account_name: Sub Account名称，用于筛选
            financial_account_name: Financial Account名称，用于筛选
            start_date: 开始日期（YYYY-MM-DD）
            end_date: 结束日期（YYYY-MM-DD）
            page: 页码，默认为 0
            size: 每页大小，默认为 10
            **kwargs: 其他可选参数
            
        Returns:
            requests.Response: 响应对象
            
        Note:
            ⚠️ 文档问题：响应结构60+字段平铺，嵌套关系不清晰
        """
        url = self.config.get_full_url("/client-lists")
        params = {"page": page, "size": size}
        
        if oms_category is not None:
            params["oms_category"] = str(oms_category) if isinstance(oms_category, OMSCategory) else oms_category
        if account_name is not None:
            params["account_name"] = account_name
        if account_id is not None:
            params["account_id"] = account_id
        if sub_account_name is not None:
            params["sub_account_name"] = sub_account_name
        if financial_account_name is not None:
            params["financial_account_name"] = financial_account_name
        if start_date is not None:
            params["start_date"] = start_date
        if end_date is not None:
            params["end_date"] = end_date
        
        params.update(kwargs)
        logger.debug(f"请求客户列表: {params}")
        
        response = self.session.get(url, params=params)
        logger.debug(f"响应状态: {response.status_code}")
        
        return response

    def get_client_detail(self, client_id: str) -> requests.Response:
        """
        获取客户详情
        
        Args:
            client_id: 客户ID
            
        Returns:
            requests.Response: 响应对象
        """
        url = self.config.get_full_url(f"/client-lists/{client_id}")
        logger.debug(f"请求客户详情: {client_id}")
        
        response = self.session.get(url)
        logger.debug(f"响应状态: {response.status_code}")
        
        return response

    # ==================== 客户管理接口 ====================
    
    def create_client(self, client_data: dict) -> requests.Response:
        """
        创建客户
        
        Args:
            client_data: 客户数据字典，包含：
                - account_id: (required) Account ID
                - sub_account_id: (可选) Sub Account ID
                - financial_account_id: (可选) Financial Account ID
                - oms_category: (required) OMS分类
                - 其他客户相关字段
                
        Returns:
            requests.Response: 响应对象
            
        Note:
            ⚠️ 文档问题：字段定义混乱，具体必需字段不明确
        """
        url = self.config.get_full_url("/client-lists")
        logger.debug(f"创建客户: {client_data.get('account_name', 'Unknown')}")
        
        response = self.session.post(url, json=client_data)
        logger.debug(f"响应状态: {response.status_code}")
        
        return response

    def update_client(self, client_id: str, update_data: dict) -> requests.Response:
        """
        更新客户信息
        
        Args:
            client_id: 客户ID
            update_data: 要更新的数据
            
        Returns:
            requests.Response: 响应对象
        """
        url = self.config.get_full_url(f"/client-lists/{client_id}")
        logger.debug(f"更新客户: {client_id}")
        
        response = self.session.patch(url, json=update_data)
        logger.debug(f"响应状态: {response.status_code}")
        
        return response

    def delete_client(self, client_id: str) -> requests.Response:
        """
        删除客户
        
        Args:
            client_id: 客户ID
            
        Returns:
            requests.Response: 响应对象
            
        Note:
            ⚠️ 破坏性操作
        """
        url = self.config.get_full_url(f"/client-lists/{client_id}")
        logger.debug(f"删除客户: {client_id}")
        
        response = self.session.delete(url)
        logger.debug(f"响应状态: {response.status_code}")
        
        return response

    # ==================== 导出和统计接口 ====================
    
    def export_clients(
        self,
        oms_category: Optional[Union[str, OMSCategory]] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        **kwargs
    ) -> requests.Response:
        """
        导出客户列表
        
        Args:
            oms_category: OMS分类，用于筛选
            start_date: 开始日期（YYYY-MM-DD）
            end_date: 结束日期（YYYY-MM-DD）
            **kwargs: 其他可选参数
            
        Returns:
            requests.Response: 响应对象（可能是文件流）
            
        Note:
            ⚠️ 文档问题：Export接口URL示例错误
        """
        url = self.config.get_full_url("/client-lists/export")
        params = {}
        
        if oms_category is not None:
            params["oms_category"] = str(oms_category) if isinstance(oms_category, OMSCategory) else oms_category
        if start_date is not None:
            params["start_date"] = start_date
        if end_date is not None:
            params["end_date"] = end_date
        
        params.update(kwargs)
        logger.debug(f"导出客户列表: {params}")
        
        response = self.session.get(url, params=params)
        logger.debug(f"响应状态: {response.status_code}")
        
        return response

    def get_historical_chart(
        self,
        oms_category: Optional[Union[str, OMSCategory]] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        **kwargs
    ) -> requests.Response:
        """
        获取历史图表数据
        
        Args:
            oms_category: OMS分类，用于筛选
            start_date: 开始日期（YYYY-MM-DD）
            end_date: 结束日期（YYYY-MM-DD）
            **kwargs: 其他可选参数
            
        Returns:
            requests.Response: 响应对象
            
        Note:
            ⚠️ 文档问题：Historical Chart响应结构缺失
        """
        url = self.config.get_full_url("/client-lists/historical-chart")
        params = {}
        
        if oms_category is not None:
            params["oms_category"] = str(oms_category) if isinstance(oms_category, OMSCategory) else oms_category
        if start_date is not None:
            params["start_date"] = start_date
        if end_date is not None:
            params["end_date"] = end_date
        
        params.update(kwargs)
        logger.debug(f"请求历史图表: {params}")
        
        response = self.session.get(url, params=params)
        logger.debug(f"响应状态: {response.status_code}")
        
        return response

    def get_client_statistics(
        self,
        oms_category: Optional[Union[str, OMSCategory]] = None,
        **kwargs
    ) -> requests.Response:
        """
        获取客户统计信息
        
        Args:
            oms_category: OMS分类，用于筛选
            **kwargs: 其他可选参数
            
        Returns:
            requests.Response: 响应对象
        """
        url = self.config.get_full_url("/client-lists/statistics")
        params = {}
        
        if oms_category is not None:
            params["oms_category"] = str(oms_category) if isinstance(oms_category, OMSCategory) else oms_category
        
        params.update(kwargs)
        logger.debug(f"请求客户统计: {params}")
        
        response = self.session.get(url, params=params)
        logger.debug(f"响应状态: {response.status_code}")
        
        return response

    # ==================== 辅助方法 ====================
    
    def parse_list_response(self, response: requests.Response) -> dict:
        """
        解析列表响应
        
        Args:
            response: requests.Response 对象
            
        Returns:
            dict: 包含 error, content, pageable 等字段
            
        Note:
            需要兼容响应结构混乱的情况
        """
        if response.status_code != 200:
            return {
                "error": True,
                "status_code": response.status_code,
                "message": response.text
            }
        
        try:
            data = response.json()
            # 检查是否有code包装层
            if "code" in data and data["code"] != 200:
                return {
                    "error": True,
                    "code": data["code"],
                    "message": data.get("error_message", "Unknown error")
                }
            
            # 提取实际数据
            content_data = data.get("data", data)
            
            return {
                "error": False,
                "content": content_data.get("content", []),
                "pageable": content_data.get("pageable", {}),
                "total_elements": content_data.get("total_elements", content_data.get("totalElements", 0)),
                "total_pages": content_data.get("total_pages", content_data.get("totalPages", 0)),
                "size": content_data.get("size", 0),
                "number": content_data.get("number", 0),
                "first": content_data.get("first", False),
                "last": content_data.get("last", False),
                "empty": content_data.get("empty", True)
            }
        except Exception as e:
            logger.error(f"解析响应失败: {e}", exc_info=True)
            return {
                "error": True,
                "message": f"Failed to parse response: {str(e)}",
                "raw_response": response.text
            }

    def parse_detail_response(self, response: requests.Response) -> dict:
        """
        解析详情响应
        
        Args:
            response: requests.Response 对象
            
        Returns:
            dict: 包含 error 标识和客户详情数据
        """
        if response.status_code != 200:
            return {
                "error": True,
                "status_code": response.status_code,
                "message": response.text
            }
        
        try:
            data = response.json()
            # 检查code字段
            if "code" in data and data["code"] != 200:
                return {
                    "error": True,
                    "code": data["code"],
                    "message": data.get("error_message", "Unknown error")
                }
            
            return {
                "error": False,
                "data": data.get("data", data)
            }
        except Exception as e:
            logger.error(f"解析响应失败: {e}", exc_info=True)
            return {
                "error": True,
                "message": f"Failed to parse response: {str(e)}",
                "raw_response": response.text
            }
