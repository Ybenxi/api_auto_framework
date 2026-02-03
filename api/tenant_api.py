"""
Tenant 相关 API 封装
遵循 API Object 模式，提供 Tenant 信息查询接口
"""
import requests
from typing import Optional
from config.config import config


class TenantAPI:
    """
    Tenant 管理 API 封装类
    """
    def __init__(self, session: Optional[requests.Session] = None):
        """
        初始化 TenantAPI
        
        Args:
            session: requests.Session 对象，如果传入则使用该 session 保持认证状态
        """
        self.base_url = config.base_url
        self.config = config
        # 如果传入了 session，则使用该 session 发送请求，保持 Auth 状态
        self.session = session or requests.Session()

    def get_current_tenant_info(self) -> requests.Response:
        """
        获取当前认证的 Tenant 信息
        
        Returns:
            requests.Response: 响应对象
            
        Example:
            response = tenant_api.get_current_tenant_info()
            tenant_info = response.json()
        """
        url = self.config.get_full_url("/tenants/info")
        response = self.session.get(url)
        return response

    def parse_tenant_response(self, response: requests.Response) -> dict:
        """
        解析 Tenant 响应
        
        Args:
            response: requests.Response 对象
            
        Returns:
            dict: 包含 Tenant 信息的字典
            
        Example:
            response = tenant_api.get_current_tenant_info()
            parsed = tenant_api.parse_tenant_response(response)
            tenant_id = parsed['data']['id']
        """
        if response.status_code != 200:
            return {
                "error": True,
                "status_code": response.status_code,
                "message": response.text
            }
        
        try:
            data = response.json()
            return {
                "error": False,
                "code": data.get("code"),
                "data": data.get("data", {})
            }
        except Exception as e:
            return {
                "error": True,
                "message": f"Failed to parse response: {str(e)}",
                "raw_response": response.text
            }
