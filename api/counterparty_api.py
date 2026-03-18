"""
Counterparty Management 相关 API 封装
遵循 API Object 模式，提供交易对手方管理接口
"""
import requests
from typing import Optional, List, Dict
from config.config import config


class CounterpartyAPI:
    """
    Counterparty 管理 API 封装类
    """
    def __init__(self, session: Optional[requests.Session] = None):
        """
        初始化 CounterpartyAPI
        
        Args:
            session: requests.Session 对象，如果传入则使用该 session 保持认证状态
        """
        self.base_url = config.base_url
        self.config = config
        # 如果传入了 session，则使用该 session 发送请求，保持 Auth 状态
        self.session = session or requests.Session()

    # ==================== Counterparty 相关接口 ====================
    
    def list_counterparties(
        self,
        name: Optional[str] = None,
        bank_account_owner_name: Optional[str] = None,
        status: Optional[str] = None,
        payment_type: Optional[str] = None,
        account_ids: Optional[List[str]] = None,
        page: int = 0,
        size: int = 10,
        **kwargs
    ) -> requests.Response:
        """
        获取 Counterparties 列表
        
        Args:
            name: Counterparty 名称
            bank_account_owner_name: 银行账户所有者名称
            status: 状态（Pending, Approved, Rejected, Terminated）
            payment_type: 支付类型（ACH, Check, Wire, International_Wire）
            account_ids: 账户 ID 列表
            page: 页码
            size: 每页大小
            **kwargs: 其他可选参数
            
        Returns:
            requests.Response: 响应对象
        """
        url = self.config.get_full_url("/counterparties")
        params = {"page": page, "size": size}
        
        if name is not None:
            params["name"] = name
        if bank_account_owner_name is not None:
            params["bank_account_owner_name"] = bank_account_owner_name
        if status is not None:
            params["status"] = status
        if payment_type is not None:
            params["payment_type"] = payment_type
        if account_ids:
            params["account_ids"] = account_ids
        
        params.update(kwargs)
        response = self.session.get(url, params=params)
        return response

    def create_counterparty(self, counterparty_data: dict) -> requests.Response:
        """
        创建 Counterparty
        
        Args:
            counterparty_data: Counterparty 数据字典，必需字段：
                - name: 名称（必需）
                - type: 类型（Person, Company, Vendor, Employee）（必需）
                - payment_type: 支付类型（ACH, Check, Wire, International_Wire, Stablecoin）（必需）
                
        Returns:
            requests.Response: 响应对象
        """
        url = self.config.get_full_url("/counterparties")
        response = self.session.post(url, json=counterparty_data)
        return response

    def get_counterparty_detail(self, counterparty_id: str) -> requests.Response:
        """
        获取 Counterparty 详情

        Args:
            counterparty_id: Counterparty ID

        Returns:
            requests.Response: 响应对象
        """
        url = self.config.get_full_url(f"/counterparties/{counterparty_id}")
        response = self.session.get(url)
        return response

    def update_counterparty(self, counterparty_id: str, update_data: dict) -> requests.Response:
        """
        更新 Counterparty 信息
        
        Args:
            counterparty_id: Counterparty ID
            update_data: 要更新的数据
            
        Returns:
            requests.Response: 响应对象
        """
        url = self.config.get_full_url(f"/counterparties/{counterparty_id}")
        response = self.session.patch(url, json=update_data)
        return response

    def get_counterparty_mfa(self, counterparty_id: str) -> requests.Response:
        """
        获取 Counterparty Record Owner 的 MFA 信息
        
        Args:
            counterparty_id: Counterparty ID
            
        Returns:
            requests.Response: 响应对象
        """
        # 注意：这是 v2 接口，使用不同的 URL 构建方式
        url = f"{self.base_url}/api/v2/cores/{self.config.core}/counterparties/{counterparty_id}/mfa"
        response = self.session.get(url)
        return response

    def send_counterparty_mfa(self, counterparty_id: str, verification_method: str) -> requests.Response:
        """
        发送 Counterparty Record Owner 的 MFA 验证码
        
        Args:
            counterparty_id: Counterparty ID
            verification_method: 验证方式（Email, Phone）
            
        Returns:
            requests.Response: 响应对象
        """
        # 注意：这是 v2 接口
        url = f"{self.base_url}/api/v2/cores/{self.config.core}/counterparties/{counterparty_id}/mfa/send"
        data = {"verification_method": verification_method}
        response = self.session.post(url, json=data)
        return response

    def verify_counterparty_mfa(
        self,
        counterparty_id: str,
        verification_code: str,
        verification_method: str
    ) -> requests.Response:
        """
        验证 Counterparty Record Owner 的 MFA 验证码
        
        Args:
            counterparty_id: Counterparty ID
            verification_code: 验证码
            verification_method: 验证方式（Email, Phone）
            
        Returns:
            requests.Response: 响应对象
        """
        # 注意：这是 v2 接口
        url = f"{self.base_url}/api/v2/cores/{self.config.core}/counterparties/{counterparty_id}/mfa/verify"
        data = {
            "verification_code": verification_code,
            "verification_method": verification_method
        }
        response = self.session.post(url, json=data)
        return response

    def create_counterparty_with_mfa(self, counterparty_data: dict) -> requests.Response:
        """
        使用 MFA 创建 Counterparty（V2 接口）
        
        Args:
            counterparty_data: Counterparty 数据字典，包含 access_token
            
        Returns:
            requests.Response: 响应对象
        """
        # 注意：这是 v2 接口
        url = f"{self.base_url}/api/v2/cores/{self.config.core}/counterparties"
        response = self.session.post(url, json=counterparty_data)
        return response

    def update_counterparty_with_mfa(
        self,
        counterparty_id: str,
        update_data: dict
    ) -> requests.Response:
        """
        使用 MFA 更新 Counterparty（V2 接口）
        
        Args:
            counterparty_id: Counterparty ID
            update_data: 要更新的数据，包含 access_token
            
        Returns:
            requests.Response: 响应对象
        """
        # 注意：这是 v2 接口
        url = f"{self.base_url}/api/v2/cores/{self.config.core}/counterparties/{counterparty_id}"
        response = self.session.patch(url, json=update_data)
        return response

    def list_counterparty_transactions(
        self,
        counterparty_id: str,
        financial_account_id: Optional[str] = None,
        sub_account_id: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        transaction_type: Optional[str] = None,
        status: Optional[str] = None,
        page: int = 0,
        size: int = 10,
        **kwargs
    ) -> requests.Response:
        """
        获取 Counterparty 相关交易列表
        
        Args:
            counterparty_id: Counterparty ID
            financial_account_id: Financial Account ID
            sub_account_id: Sub Account ID
            start_date: 开始日期
            end_date: 结束日期
            transaction_type: 交易类型（Credit, Debit）
            status: 状态
            page: 页码
            size: 每页大小
            **kwargs: 其他可选参数
            
        Returns:
            requests.Response: 响应对象
        """
        url = self.config.get_full_url(f"/counterparties/{counterparty_id}/transactions")
        params = {"page": page, "size": size}
        
        if financial_account_id is not None:
            params["financial_account_id"] = financial_account_id
        if sub_account_id is not None:
            params["sub_account_id"] = sub_account_id
        if start_date is not None:
            params["start_date"] = start_date
        if end_date is not None:
            params["end_date"] = end_date
        if transaction_type is not None:
            params["transaction_type"] = transaction_type
        if status is not None:
            params["status"] = status
        
        params.update(kwargs)
        response = self.session.get(url, params=params)
        return response

    def terminate_counterparty(
        self,
        counterparty_id: str,
        account_ids: List[str]
    ) -> requests.Response:
        """
        终止 Counterparty
        
        Args:
            counterparty_id: Counterparty ID
            account_ids: 账户 ID 列表
            
        Returns:
            requests.Response: 响应对象
        """
        url = self.config.get_full_url(f"/counterparties/{counterparty_id}/terminate")
        data = {"account_ids": account_ids}
        response = self.session.patch(url, json=data)
        return response

    # ==================== Counterparty Group 相关接口 ====================
    
    def list_counterparty_groups(
        self,
        name: Optional[str] = None,
        page: int = 0,
        size: int = 10,
        **kwargs
    ) -> requests.Response:
        """
        获取 Counterparty Groups 列表
        
        Args:
            name: Group 名称
            page: 页码
            size: 每页大小
            **kwargs: 其他可选参数
            
        Returns:
            requests.Response: 响应对象
        """
        url = self.config.get_full_url("/counterparty-groups")
        params = {"page": page, "size": size}
        
        if name is not None:
            params["name"] = name
        
        params.update(kwargs)
        response = self.session.get(url, params=params)
        return response

    def create_counterparty_group(self, name: str) -> requests.Response:
        """
        创建 Counterparty Group
        
        Args:
            name: Group 名称
            
        Returns:
            requests.Response: 响应对象
        """
        url = self.config.get_full_url("/counterparty-groups")
        data = {"name": name}
        response = self.session.post(url, json=data)
        return response

    def update_counterparty_group(self, group_id: str, name: str) -> requests.Response:
        """
        更新 Counterparty Group
        
        Args:
            group_id: Group ID
            name: 新的 Group 名称
            
        Returns:
            requests.Response: 响应对象
        """
        url = self.config.get_full_url(f"/counterparty-groups/{group_id}")
        data = {"name": name}
        response = self.session.patch(url, json=data)
        return response

    def delete_counterparty_group(self, group_id: str) -> requests.Response:
        """
        删除 Counterparty Group
        
        Args:
            group_id: Group ID
            
        Returns:
            requests.Response: 响应对象
        """
        url = self.config.get_full_url(f"/counterparty-groups/{group_id}")
        response = self.session.delete(url)
        return response

    def list_group_counterparties(
        self,
        group_id: str,
        page: int = 0,
        size: int = 10,
        **kwargs
    ) -> requests.Response:
        """
        获取 Group 下的 Counterparties 列表
        
        Args:
            group_id: Group ID
            page: 页码
            size: 每页大小
            **kwargs: 其他可选参数
            
        Returns:
            requests.Response: 响应对象
        """
        url = self.config.get_full_url(f"/counterparty-groups/{group_id}/counterparties")
        params = {"page": page, "size": size}
        params.update(kwargs)
        response = self.session.get(url, params=params)
        return response

    def add_counterparties_to_group(
        self,
        group_id: str,
        counterparty_ids: List[str]
    ) -> requests.Response:
        """
        添加 Counterparties 到 Group
        
        Args:
            group_id: Group ID
            counterparty_ids: Counterparty ID 列表
            
        Returns:
            requests.Response: 响应对象
        """
        url = self.config.get_full_url(f"/counterparty-groups/{group_id}/counterparty")
        data = {"counterparty_ids": counterparty_ids}
        response = self.session.post(url, json=data)
        return response

    def remove_counterparty_from_group(
        self,
        group_id: str,
        counterparty_id: str
    ) -> requests.Response:
        """
        从 Group 中移除 Counterparty
        
        Args:
            group_id: Group ID
            counterparty_id: Counterparty ID
            
        Returns:
            requests.Response: 响应对象
        """
        url = self.config.get_full_url(f"/counterparty-groups/{group_id}/counterparty")
        data = {"counterparty_id": counterparty_id}
        response = self.session.delete(url, json=data)
        return response

    # ==================== 辅助方法 ====================
    
    def parse_list_response(self, response: requests.Response) -> dict:
        """
        解析列表响应（分页）
        
        Args:
            response: requests.Response 对象
            
        Returns:
            dict: 包含 content（列表）、pageable（分页信息）等字段
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
