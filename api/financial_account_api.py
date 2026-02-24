"""
Financial Account 相关 API 封装
遵循 API Object 模式，提供完整的 CRUD 接口
"""
import requests
from typing import Optional, List
from config.config import config


class FinancialAccountAPI:
    """
    Financial Account 管理 API 封装类
    """
    def __init__(self, session: Optional[requests.Session] = None):
        """
        初始化 FinancialAccountAPI
        
        Args:
            session: requests.Session 对象，如果传入则使用该 session 保持认证状态
        """
        self.base_url = config.base_url
        self.config = config
        self.session = session or requests.Session()

    def list_financial_accounts(
        self,
        account_number: Optional[str] = None,
        name: Optional[str] = None,
        status: Optional[str] = None,
        source: Optional[str] = None,
        account_ids: Optional[List[str]] = None,
        record_type: Optional[str] = None,
        page: int = 0,
        size: int = 10,
        **kwargs
    ) -> requests.Response:
        """
        获取 Financial Accounts 列表
        
        Args:
            account_number: 账户编号，用于筛选
            name: 账户名称，用于筛选
            status: 账户状态，用于筛选
            source: 账户来源（Managed/Illiquid/Unmanaged）
            account_ids: 账户 ID 数组
            record_type: 记录类型（Investment_Account/Bank_Account/Managed_Solutions/Corporate_Retirement/Trust）
            page: 页码，默认为 0
            size: 每页大小，默认为 10
            **kwargs: 其他可选参数
            
        Returns:
            requests.Response: 响应对象
        """
        url = self.config.get_full_url("/financial-accounts")
        params = {"page": page, "size": size}
        
        if account_number is not None:
            params["account_number"] = account_number
        if name is not None:
            params["name"] = name
        if status is not None:
            params["status"] = status
        if source is not None:
            params["source"] = source
        if account_ids is not None:
            # 使用重复key格式：account_ids=id1&account_ids=id2
            # requests 传入列表时自动生成重复key格式
            params["account_ids"] = account_ids
        if record_type is not None:
            params["record_type"] = record_type
        
        params.update(kwargs)
        
        response = self.session.get(url, params=params)
        return response

    def get_financial_account_detail(self, financial_account_id: str) -> requests.Response:
        """
        获取 Financial Account 详情
        
        Args:
            financial_account_id: Financial Account ID
            
        Returns:
            requests.Response: 响应对象
        """
        url = self.config.get_full_url(f"/financial-accounts/{financial_account_id}")
        response = self.session.get(url)
        return response

    def get_related_transactions(
        self,
        financial_account_id: str,
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
        获取 Financial Account 相关的 Money Movement Transactions
        
        Args:
            financial_account_id: Financial Account ID
            status: 交易状态（Reviewing/Cancelled/Completed/Failed/Processing）
            start_date: 开始日期
            end_date: 结束日期
            transaction_type: 交易类型（Credit/Debit）
            payment_type: 支付类型（ACH/Wire/Check/Internal_Pay/Instant_Pay/Account_Transfer）
            transaction_id: 交易 ID
            page: 页码
            size: 每页大小
            
        Returns:
            requests.Response: 响应对象
        """
        url = self.config.get_full_url(f"/financial-accounts/{financial_account_id}/transactions")
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

    def get_related_sub_accounts(
        self,
        financial_account_id: str,
        name: Optional[str] = None,
        status: Optional[str] = None,
        page: int = 0,
        size: int = 10,
        **kwargs
    ) -> requests.Response:
        """
        获取 Financial Account 相关的 Sub Accounts
        
        Args:
            financial_account_id: Financial Account ID
            name: Sub Account 名称
            status: Sub Account 状态
            page: 页码
            size: 每页大小
            
        Returns:
            requests.Response: 响应对象
        """
        url = self.config.get_full_url(f"/financial-accounts/{financial_account_id}/sub-accounts")
        params = {"page": page, "size": size}
        
        if name is not None:
            params["name"] = name
        if status is not None:
            params["status"] = status
        
        params.update(kwargs)
        
        response = self.session.get(url, params=params)
        return response

    def get_payment_detail(self, financial_account_id: str) -> requests.Response:
        """
        获取 Financial Account 的支付详情（真实账号和路由号）
        
        Args:
            financial_account_id: Financial Account ID
            
        Returns:
            requests.Response: 响应对象
        """
        url = self.config.get_full_url(f"/financial-accounts/{financial_account_id}/detail")
        response = self.session.get(url)
        return response

    def get_related_positions(
        self,
        financial_account_id: str,
        symbol: Optional[str] = None,
        cusip: Optional[str] = None,
        page: int = 0,
        size: int = 10,
        **kwargs
    ) -> requests.Response:
        """
        获取 Financial Account 相关的持仓（Holdings/Positions）
        
        Args:
            financial_account_id: Financial Account ID
            symbol: 证券代码
            cusip: CUSIP 编号
            page: 页码
            size: 每页大小
            
        Returns:
            requests.Response: 响应对象
        """
        url = self.config.get_full_url(f"/financial-accounts/{financial_account_id}/holdings")
        params = {"page": page, "size": size}
        
        if symbol is not None:
            params["symbol"] = symbol
        if cusip is not None:
            params["cusip"] = cusip
        
        params.update(kwargs)
        
        response = self.session.get(url, params=params)
        return response

    def get_settled_transactions(
        self,
        financial_account_id: str,
        begin_date: Optional[str] = None,
        end_date: Optional[str] = None,
        security: Optional[str] = None,
        page: int = 0,
        size: int = 10,
        **kwargs
    ) -> requests.Response:
        """
        获取 Financial Account 相关的已结算交易
        
        Args:
            financial_account_id: Financial Account ID
            begin_date: 开始日期
            end_date: 结束日期
            security: 证券名称/代码/CUSIP 模糊查询
            page: 页码
            size: 每页大小
            
        Returns:
            requests.Response: 响应对象
        """
        url = self.config.get_full_url(f"/financial-accounts/{financial_account_id}/settled-transactions")
        params = {"page": page, "size": size}
        
        if begin_date is not None:
            params["begin_date"] = begin_date
        if end_date is not None:
            params["end_date"] = end_date
        if security is not None:
            params["security"] = security
        
        params.update(kwargs)
        
        response = self.session.get(url, params=params)
        return response

    def parse_list_response(self, response: requests.Response) -> dict:
        """
        解析 Financial Accounts 列表响应
        
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
        解析 Financial Account 详情响应
        
        Args:
            response: requests.Response 对象
            
        Returns:
            dict: Financial Account 详情数据
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
