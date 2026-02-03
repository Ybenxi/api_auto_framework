"""
FBO Account 相关 API 封装
遵循 API Object 模式，提供灵活的参数化接口
"""
import requests
from typing import Optional, Union
from config.config import config
from data.enums import FboAccountStatus


class FboAccountAPI:
    """
    FBO Account 管理 API 封装类
    """
    def __init__(self, session: Optional[requests.Session] = None):
        """
        初始化 FboAccountAPI
        
        Args:
            session: requests.Session 对象，如果传入则使用该 session 保持认证状态
        """
        self.base_url = config.base_url
        self.config = config
        self.session = session or requests.Session()

    def create_fbo_account(self, fbo_account_data: dict) -> requests.Response:
        """
        创建 FBO Account
        
        Args:
            fbo_account_data: FBO Account 数据字典，包含：
                - sub_account_id: (required) Sub Account ID
                - name: (required) FBO Account 名称
                
        Returns:
            requests.Response: 响应对象
            
        Example:
            fbo_data = {
                "sub_account_id": "1710955845682JJMu2",
                "name": "Checking-1-01-1-0000675"
            }
            response = fbo_api.create_fbo_account(fbo_data)
        """
        url = self.config.get_full_url("/fbo-accounts")
        response = self.session.post(url, json=fbo_account_data)
        return response

    def list_fbo_accounts(
        self,
        sub_account_id: Optional[str] = None,
        name: Optional[str] = None,
        status: Optional[Union[str, FboAccountStatus]] = None,
        page: int = 0,
        size: int = 10,
        **kwargs
    ) -> requests.Response:
        """
        获取 FBO Accounts 列表
        
        Args:
            sub_account_id: Sub Account ID，用于筛选
            name: FBO Account 名称，用于筛选
            status: FBO Account 状态，可以是字符串或 FboAccountStatus 枚举
            page: 页码，默认为 0
            size: 每页大小，默认为 10
            **kwargs: 其他额外的查询参数
            
        Returns:
            requests.Response: 响应对象
            
        Example:
            # 基础查询
            response = fbo_api.list_fbo_accounts()
            
            # 使用枚举类型筛选
            response = fbo_api.list_fbo_accounts(
                status=FboAccountStatus.OPEN,
                page=0,
                size=20
            )
        """
        url = self.config.get_full_url("/fbo-accounts")
        
        # 构建查询参数字典
        params = {
            "page": page,
            "size": size
        }
        
        # 添加可选参数（仅当值不为 None 时）
        if sub_account_id is not None:
            params["sub_account_id"] = sub_account_id
        if name is not None:
            params["name"] = name
        if status is not None:
            # 如果是枚举类型，取其值；否则直接使用字符串
            params["status"] = str(status) if isinstance(status, FboAccountStatus) else status
        
        # 添加其他额外参数
        params.update(kwargs)
        
        # 使用 session 发送 GET 请求
        response = self.session.get(url, params=params)
        
        return response

    def get_fbo_account_detail(self, fbo_account_id: str) -> requests.Response:
        """
        根据 ID 获取单个 FBO Account 详情
        
        Args:
            fbo_account_id: FBO Account ID
            
        Returns:
            requests.Response: 响应对象
            
        Example:
            response = fbo_api.get_fbo_account_detail("17109558473329kd42")
            if response.status_code == 200:
                fbo_account = response.json()
                print(f"FBO Account: {fbo_account['name']}")
        """
        url = self.config.get_full_url(f"/fbo-accounts/{fbo_account_id}")
        response = self.session.get(url)
        return response

    def parse_list_response(self, response: requests.Response) -> dict:
        """
        解析 FBO Accounts 列表响应，提取关键信息
        
        Args:
            response: requests.Response 对象
            
        Returns:
            dict: 包含 content（FBO Accounts 列表）、pageable（分页信息）、total_elements 等字段
            
        Example:
            response = fbo_api.list_fbo_accounts()
            parsed = fbo_api.parse_list_response(response)
            fbo_accounts = parsed['content']
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

    def parse_detail_response(self, response: requests.Response) -> dict:
        """
        解析 FBO Account 详情响应
        
        Args:
            response: requests.Response 对象
            
        Returns:
            dict: 包含 error 标识和 FBO Account 详情数据
            
        Example:
            response = fbo_api.get_fbo_account_detail("17109558473329kd42")
            parsed = fbo_api.parse_detail_response(response)
            if not parsed['error']:
                fbo_account = parsed['data']
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
                fbo_data = data["data"]
            else:
                # 如果响应直接是 FBO Account 数据
                fbo_data = data
            
            return {
                "error": False,
                "data": fbo_data
            }
        except Exception as e:
            return {
                "error": True,
                "message": f"Failed to parse response: {str(e)}",
                "raw_response": response.text
            }
