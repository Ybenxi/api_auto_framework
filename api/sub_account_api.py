"""
Sub Account 相关 API 封装
遵循 API Object 模式，提供完整的 CRUD 接口
"""
import requests
from typing import Optional, List
from config.config import config


class SubAccountAPI:
    """
    Sub Account 管理 API 封装类
    """
    def __init__(self, session: Optional[requests.Session] = None):
        """
        初始化 SubAccountAPI
        
        Args:
            session: requests.Session 对象，如果传入则使用该 session 保持认证状态
        """
        self.base_url = config.base_url
        self.config = config
        self.session = session or requests.Session()

    def list_sub_accounts(
        self,
        name: Optional[str] = None,
        status: Optional[str] = None,
        financial_account_id: Optional[str] = None,
        page: int = 0,
        size: int = 10,
        **kwargs
    ) -> requests.Response:
        """
        获取 Sub Accounts 列表
        
        Args:
            name: Sub Account 名称，用于筛选
            status: Sub Account 状态（Open/Closed/Pending）
            financial_account_id: 关联的 Financial Account ID
            page: 页码，默认为 0
            size: 每页大小，默认为 10
            **kwargs: 其他可选参数
            
        Returns:
            requests.Response: 响应对象
        """
        url = self.config.get_full_url("/sub-accounts")
        params = {"page": page, "size": size}
        
        if name is not None:
            params["name"] = name
        if status is not None:
            params["status"] = status
        if financial_account_id is not None:
            params["financial_account_id"] = financial_account_id
        
        params.update(kwargs)
        
        response = self.session.get(url, params=params)
        return response

    def create_sub_account(self, sub_account_data: dict) -> requests.Response:
        """
        创建 Sub Account
        
        Args:
            sub_account_data: Sub Account 数据字典，必需字段：
                - financial_account_id: 关联的 Financial Account ID
                - name: Sub Account 名称
                可选字段：
                - description: 描述
                - account_identifier: 账户标识符
                
        Returns:
            requests.Response: 响应对象
        """
        url = self.config.get_full_url("/sub-accounts")
        response = self.session.post(url, json=sub_account_data)
        return response

    def get_sub_account_detail(self, sub_account_id: str) -> requests.Response:
        """
        获取 Sub Account 详情
        
        Args:
            sub_account_id: Sub Account ID
            
        Returns:
            requests.Response: 响应对象
        """
        url = self.config.get_full_url(f"/sub-accounts/{sub_account_id}")
        response = self.session.get(url)
        return response

    def get_related_transactions(
        self,
        sub_account_id: str,
        status: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        transaction_type: Optional[str] = None,
        payment_type: Optional[str] = None,
        transaction_id: Optional[str] = None,
        page: int = 0,
        size: int = 10,
        **kwargs
    ) -> requests.Response:
        """
        获取 Sub Account 相关的 Money Movement Transactions
        
        Args:
            sub_account_id: Sub Account ID
            status: 交易状态
            start_date: 开始日期
            end_date: 结束日期
            transaction_type: 交易类型（Credit/Debit）
            payment_type: 支付类型
            transaction_id: 交易 ID
            page: 页码
            size: 每页大小
            
        Returns:
            requests.Response: 响应对象
        """
        url = self.config.get_full_url(f"/sub-accounts/{sub_account_id}/transactions")
        params = {"page": page, "size": size}
        
        if status is not None:
            params["status"] = status
        if start_date is not None:
            params["start_date"] = start_date
        if end_date is not None:
            params["end_date"] = end_date
        if transaction_type is not None:
            params["transaction_type"] = transaction_type
        if payment_type is not None:
            params["payment_type"] = payment_type
        if transaction_id is not None:
            params["transaction_id"] = transaction_id
        
        params.update(kwargs)
        
        response = self.session.get(url, params=params)
        return response

    def get_related_positions(
        self,
        sub_account_id: str,
        symbol: Optional[str] = None,
        cusip: Optional[str] = None,
        page: int = 0,
        size: int = 10,
        **kwargs
    ) -> requests.Response:
        """
        获取 Sub Account 相关的持仓（Holdings/Positions）
        
        Args:
            sub_account_id: Sub Account ID
            symbol: 证券代码
            cusip: CUSIP 编号
            page: 页码
            size: 每页大小
            
        Returns:
            requests.Response: 响应对象
        """
        url = self.config.get_full_url(f"/sub-accounts/{sub_account_id}/holdings")
        params = {"page": page, "size": size}
        
        if symbol is not None:
            params["symbol"] = symbol
        if cusip is not None:
            params["cusip"] = cusip
        
        params.update(kwargs)
        
        response = self.session.get(url, params=params)
        return response

    def get_related_fbo_accounts(
        self,
        sub_account_id: str,
        status: Optional[str] = None,
        page: int = 0,
        size: int = 10,
        **kwargs
    ) -> requests.Response:
        """
        获取 Sub Account 相关的 FBO Accounts
        
        Args:
            sub_account_id: Sub Account ID
            status: FBO Account 状态
            page: 页码
            size: 每页大小
            
        Returns:
            requests.Response: 响应对象
        """
        url = self.config.get_full_url(f"/sub-accounts/{sub_account_id}/fbo-accounts")
        params = {"page": page, "size": size}
        
        if status is not None:
            params["status"] = status
        
        params.update(kwargs)
        
        response = self.session.get(url, params=params)
        return response

    def parse_list_response(self, response: requests.Response) -> dict:
        """
        解析 Sub Accounts 列表响应
        
        Args:
            response: requests.Response 对象
            
        Returns:
            dict: 包含 content、pageable 等字段
        """
        if response.status_code != 200:
            return {
                "error": True,
                "status_code": response.status_code,
                "message": response.text
            }
        
        try:
            data = response.json()
            if "data" in data:
                content_data = data["data"]
            else:
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
        解析 Sub Account 详情响应
        
        Args:
            response: requests.Response 对象
            
        Returns:
            dict: Sub Account 详情数据
        """
        if response.status_code != 200:
            return {
                "error": True,
                "status_code": response.status_code,
                "message": response.text
            }
        
        try:
            data = response.json()
            if "data" in data:
                return {"error": False, **data["data"]}
            else:
                return {"error": False, **data}
        except Exception as e:
            return {
                "error": True,
                "message": f"Failed to parse response: {str(e)}",
                "raw_response": response.text
            }
