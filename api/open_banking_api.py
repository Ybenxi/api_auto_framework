"""
Open Banking 相关 API 封装
遵循 API Object 模式，提供开放银行功能接口
"""
import requests
from typing import Optional
from config.config import config


class OpenBankingAPI:
    """
    Open Banking 管理 API 封装类
    """
    def __init__(self, session: Optional[requests.Session] = None):
        """
        初始化 OpenBankingAPI
        
        Args:
            session: requests.Session 对象，如果传入则使用该 session 保持认证状态
        """
        self.base_url = config.base_url
        self.config = config
        # 如果传入了 session，则使用该 session 发送请求，保持 Auth 状态
        self.session = session or requests.Session()

    def list_authorized_accounts(
        self,
        name: Optional[str] = None,
        **kwargs
    ) -> requests.Response:
        """
        获取授权账户列表
        
        Args:
            name: 账户名称，用于筛选
            **kwargs: 其他可选参数
            
        Returns:
            requests.Response: 响应对象
            
        Example:
            # 获取所有授权账户
            response = open_banking_api.list_authorized_accounts()
            
            # 使用名称筛选
            response = open_banking_api.list_authorized_accounts(name="haif")
        """
        url = self.config.get_full_url("/open-banking/accounts/authorized-accounts")
        params = {}
        
        # 添加可选参数
        if name is not None:
            params["name"] = name
        
        # 添加其他自定义参数
        params.update(kwargs)
        
        response = self.session.get(url, params=params)
        return response

    def create_open_banking_connect_link(
        self,
        redirect_url: str,
        account_id: str
    ) -> requests.Response:
        """
        创建 Open Banking 连接链接
        允许客户登录其金融机构并授权 UniFi 平台链接其账户
        
        Args:
            redirect_url: 重定向 URL（必需）
            account_id: 账户 ID（必需）
            
        Returns:
            requests.Response: 响应对象
            
        Example:
            response = open_banking_api.create_open_banking_connect_link(
                redirect_url="https://www.fintech.com",
                account_id="xxx"
            )
        """
        url = self.config.get_full_url("/open-banking/connections/manage/open-banking")
        data = {
            "redirect_url": redirect_url,
            "account_id": account_id
        }
        response = self.session.post(url, json=data)
        return response

    def create_bank_account_connect_link(
        self,
        redirect_url: str,
        account_id: str
    ) -> requests.Response:
        """
        创建银行账户连接链接
        允许客户登录其金融机构并连接银行账户
        
        Args:
            redirect_url: 重定向 URL（必需）
            account_id: 账户 ID（必需）
            
        Returns:
            requests.Response: 响应对象
            
        Example:
            response = open_banking_api.create_bank_account_connect_link(
                redirect_url="https://www.fintech.com",
                account_id="xxx"
            )
        """
        url = self.config.get_full_url("/open-banking/connections/manage/banks")
        data = {
            "redirect_url": redirect_url,
            "account_id": account_id
        }
        response = self.session.post(url, json=data)
        return response

    def list_connected_external_accounts(
        self,
        account_id: str
    ) -> requests.Response:
        """
        获取已连接的外部账户列表
        列出通过 Connect Embed UI 连接的所有外部账户
        
        Args:
            account_id: 已连接的账户 ID
            
        Returns:
            requests.Response: 响应对象
            
        Example:
            response = open_banking_api.list_connected_external_accounts(
                account_id="xxx"
            )
        """
        url = self.config.get_full_url("/open-banking/accounts")
        params = {"account_id": account_id}
        response = self.session.get(url, params=params)
        return response

    def list_account_transactions(
        self,
        financial_account_id: str
    ) -> requests.Response:
        """
        获取账户交易列表
        列出已连接的外部账户交易记录
        
        Args:
            financial_account_id: UniFi 金融账户 ID
            
        Returns:
            requests.Response: 响应对象
            
        Example:
            response = open_banking_api.list_account_transactions(
                financial_account_id="xxx"
            )
        """
        url = self.config.get_full_url(f"/open-banking/accounts/{financial_account_id}/transactions")
        response = self.session.get(url)
        return response

    def parse_list_response(self, response: requests.Response) -> dict:
        """
        解析列表响应
        
        Args:
            response: requests.Response 对象
            
        Returns:
            dict: 包含 data（列表）和其他字段
            
        Example:
            response = open_banking_api.list_authorized_accounts()
            parsed = open_banking_api.parse_list_response(response)
            accounts = parsed['data']
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
                "error_message": data.get("error_message"),
                "data": data.get("data", [])
            }
        except Exception as e:
            return {
                "error": True,
                "message": f"Failed to parse response: {str(e)}",
                "raw_response": response.text
            }
