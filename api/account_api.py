"""
账户相关 API 封装
遵循 API Object 模式，提供灵活的参数化接口
"""
import requests
from typing import Optional, Union
from config.config import config
from data.enums import BusinessEntityType, AccountStatus


class AccountAPI:
    """
    账户管理 API 封装类
    """
    def __init__(self, session: Optional[requests.Session] = None):
        """
        初始化 AccountAPI
        
        Args:
            session: requests.Session 对象，如果传入则使用该 session 保持认证状态
        """
        self.base_url = config.base_url
        self.config = config
        # 如果传入了 session，则使用该 session 发送请求，保持 Auth 状态
        self.session = session or requests.Session()

    def list_accounts(
        self,
        account_number: Optional[str] = None,
        name: Optional[str] = None,
        email: Optional[str] = None,
        status: Optional[Union[str, AccountStatus]] = None,
        tax_id: Optional[str] = None,
        business_entity_type: Optional[Union[str, BusinessEntityType]] = None,
        page: int = 0,
        size: int = 10,
        **kwargs
    ) -> requests.Response:
        """
        获取账户列表
        
        Args:
            account_number: 账户编号，用于筛选
            name: 业务账户名称，用于筛选
            email: 账户邮箱，用于筛选
            status: 账户状态，可以是字符串或 AccountStatus 枚举
            tax_id: 税务 ID，用于筛选
            business_entity_type: 业务实体类型，可以是字符串或 BusinessEntityType 枚举
            page: 页码，默认为 0
            size: 每页大小，默认为 10
            **kwargs: 其他额外的查询参数
            
        Returns:
            requests.Response: 响应对象
            
        Example:
            # 基础查询
            response = account_api.list_accounts()
            
            # 使用枚举类型筛选
            response = account_api.list_accounts(
                business_entity_type=BusinessEntityType.LLC,
                status=AccountStatus.ACTIVE
            )
            
            # 使用字符串筛选
            response = account_api.list_accounts(name="Example", page=1, size=20)
        """
        # 使用 config 的方法构建完整 URL
        url = self.config.get_full_url("/accounts")
        
        # 构建查询参数字典
        params = {
            "page": page,
            "size": size
        }
        
        # 添加可选参数（仅当值不为 None 时）
        if account_number is not None:
            params["account_number"] = account_number
        if name is not None:
            params["name"] = name
        if email is not None:
            params["email"] = email
        if status is not None:
            # 如果是枚举类型，取其值；否则直接使用字符串
            params["status"] = str(status) if isinstance(status, AccountStatus) else status
        if tax_id is not None:
            params["tax_id"] = tax_id
        if business_entity_type is not None:
            # 如果是枚举类型，取其值；否则直接使用字符串
            params["business_entity_type"] = str(business_entity_type) if isinstance(
                business_entity_type, BusinessEntityType
            ) else business_entity_type
        
        # 添加其他额外参数
        params.update(kwargs)
        
        # 使用 session 发送 GET 请求
        response = self.session.get(url, params=params)
        
        return response

    def get_account_detail(self, account_id: str) -> requests.Response:
        """
        根据 ID 获取单个账户详情
        
        Args:
            account_id: 账户 ID
            
        Returns:
            requests.Response: 响应对象
            
        Example:
            response = account_api.get_account_detail("ac3d45sa")
            if response.status_code == 200:
                account = response.json()
                print(f"Account: {account['account_name']}")
        """
        # 使用 config 的方法构建完整 URL
        url = self.config.get_full_url(f"/accounts/{account_id}")
        response = self.session.get(url)
        return response

    def parse_list_response(self, response: requests.Response) -> dict:
        """
        解析账户列表响应，提取关键信息
        
        Args:
            response: requests.Response 对象
            
        Returns:
            dict: 包含 content（账户列表）、pageable（分页信息）、total_elements 等字段
            
        Example:
            response = account_api.list_accounts()
            parsed = account_api.parse_list_response(response)
            accounts = parsed['content']
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
        解析账户详情响应
        
        Args:
            response: requests.Response 对象
            
        Returns:
            dict: 包含 error 标识和账户详情数据
            
        Example:
            response = account_api.get_account_detail("ac3d45sa")
            parsed = account_api.parse_detail_response(response)
            if not parsed['error']:
                account = parsed['data']
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
                account_data = data["data"]
            else:
                # 如果响应直接是账户数据
                account_data = data
            
            return {
                "error": False,
                "data": account_data
            }
        except Exception as e:
            return {
                "error": True,
                "message": f"Failed to parse response: {str(e)}",
                "raw_response": response.text
            }

    def update_account(self, account_id: str, update_data: dict) -> requests.Response:
        """
        更新账户信息
        
        Args:
            account_id: 账户 ID
            update_data: 更新数据字典，可包含以下字段：
                - mailing_street: 邮寄地址街道
                - mailing_city: 邮寄地址城市
                - mailing_state: 邮寄地址州
                - mailing_postalcode: 邮寄地址邮编
                - mailing_country: 邮寄地址国家（ISO 3166 标准）
                - register_street: 注册地址街道
                - register_city: 注册地址城市
                - register_state: 注册地址州
                - register_postalcode: 注册地址邮编
                - register_country: 注册地址国家（ISO 3166 标准）
            
        Returns:
            requests.Response: 响应对象
            
        Example:
            update_data = {
                "mailing_city": "New York",
                "mailing_state": "NY"
            }
            response = account_api.update_account("ac3d45sa", update_data)
            if response.status_code == 200:
                updated_account = response.json()
                print(f"Updated: {updated_account['mailing_city']}")
        """
        url = self.config.get_full_url(f"/accounts/{account_id}")
        response = self.session.put(url, json=update_data)
        return response

    def get_financial_accounts(
        self,
        account_id: str,
        account_number: Optional[str] = None,
        name: Optional[str] = None,
        status: Optional[str] = None,
        page: int = 0,
        size: int = 10,
        **kwargs
    ) -> requests.Response:
        """
        获取指定账户关联的 Financial Accounts
        
        Args:
            account_id: Profile Account ID
            account_number: Financial Account 编号，用于筛选
            name: Financial Account 名称，用于筛选
            status: Financial Account 状态，用于筛选
            page: 页码，默认为 0
            size: 每页大小，默认为 10
            **kwargs: 其他额外的查询参数
            
        Returns:
            requests.Response: 响应对象
            
        Example:
            # 获取账户的所有 Financial Accounts
            response = account_api.get_financial_accounts("WAz8eIbvDR60rouK")
            
            # 使用筛选条件
            response = account_api.get_financial_accounts(
                "WAz8eIbvDR60rouK",
                status="Pending",
                page=0,
                size=20
            )
        """
        url = self.config.get_full_url(f"/accounts/{account_id}/financial-accounts")
        
        # 构建查询参数
        params = {
            "page": page,
            "size": size
        }
        
        # 添加可选参数
        if account_number is not None:
            params["account_number"] = account_number
        if name is not None:
            params["name"] = name
        if status is not None:
            params["status"] = status
        
        # 添加其他额外参数
        params.update(kwargs)
        
        response = self.session.get(url, params=params)
        return response

    def parse_financial_accounts_response(self, response: requests.Response) -> dict:
        """
        解析 Financial Accounts 列表响应
        
        Args:
            response: requests.Response 对象
            
        Returns:
            dict: 包含 content（Financial Accounts 列表）、pageable（分页信息）等字段
            
        Example:
            response = account_api.get_financial_accounts("WAz8eIbvDR60rouK")
            parsed = account_api.parse_financial_accounts_response(response)
            financial_accounts = parsed['content']
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

    def get_account_contacts(
        self,
        account_id: str,
        name: Optional[str] = None,
        email: Optional[str] = None,
        status: Optional[str] = None,
        page: int = 0,
        size: int = 10,
        **kwargs
    ) -> requests.Response:
        """
        获取指定账户关联的 Contacts
        
        Args:
            account_id: Profile Account ID
            name: Contact 姓名，用于筛选
            email: Contact 邮箱，用于筛选
            status: Contact 状态，用于筛选
            page: 页码，默认为 0
            size: 每页大小，默认为 10
            **kwargs: 其他可选参数
            
        Returns:
            requests.Response: 响应对象
            
        Example:
            # 获取所有 Contacts
            response = account_api.get_account_contacts("1717780644697YVO0G")
            
            # 使用筛选条件
            response = account_api.get_account_contacts(
                "1717780644697YVO0G",
                status="Active",
                page=0,
                size=20
            )
        """
        url = self.config.get_full_url(f"/accounts/{account_id}/contacts")
        params = {"page": page, "size": size}
        
        # 添加可选参数
        if name is not None:
            params["name"] = name
        if email is not None:
            params["email"] = email
        if status is not None:
            params["status"] = status
        
        # 添加其他自定义参数
        params.update(kwargs)
        
        response = self.session.get(url, params=params)
        return response

    def parse_contacts_response(self, response: requests.Response) -> dict:
        """
        解析 Contacts 列表响应
        
        Args:
            response: requests.Response 对象
            
        Returns:
            dict: 包含 content（Contacts 列表）、pageable（分页信息）等字段
            
        Example:
            response = account_api.get_account_contacts("1717780644697YVO0G")
            parsed = account_api.parse_contacts_response(response)
            contacts = parsed['content']
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

    def get_settled_transactions(
        self,
        account_id: str,
        begin_date: Optional[str] = None,
        end_date: Optional[str] = None,
        security: Optional[str] = None,
        page: int = 0,
        size: int = 10,
        **kwargs
    ) -> requests.Response:
        """
        获取指定账户的 Settled Transactions
        
        Args:
            account_id: Profile Account ID
            begin_date: 开始日期（settle_date），格式：YYYY-MM-DD
            end_date: 结束日期（settle_date），格式：YYYY-MM-DD
            security: 证券模糊查询（security name, symbol 或 CUSIP）
            page: 页码，默认为 0
            size: 每页大小，默认为 10
            **kwargs: 其他可选参数
            
        Returns:
            requests.Response: 响应对象
            
        Example:
            # 获取所有 Settled Transactions
            response = account_api.get_settled_transactions("1717780644697YVO0G")
            
            # 使用日期范围筛选
            response = account_api.get_settled_transactions(
                "1717780644697YVO0G",
                begin_date="2024-01-01",
                end_date="2024-12-31"
            )
            
            # 使用证券筛选
            response = account_api.get_settled_transactions(
                "1717780644697YVO0G",
                security="AAPL"
            )
        """
        url = self.config.get_full_url(f"/accounts/{account_id}/settled-transactions")
        params = {"page": page, "size": size}
        
        # 添加可选参数
        if begin_date is not None:
            params["begin_date"] = begin_date
        if end_date is not None:
            params["end_date"] = end_date
        if security is not None:
            params["security"] = security
        
        # 添加其他自定义参数
        params.update(kwargs)
        
        response = self.session.get(url, params=params)
        return response

    def parse_transactions_response(self, response: requests.Response) -> dict:
        """
        解析 Settled Transactions 列表响应
        
        Args:
            response: requests.Response 对象
            
        Returns:
            dict: 包含 content（Transactions 列表）、pageable（分页信息）等字段
            
        Example:
            response = account_api.get_settled_transactions("1717780644697YVO0G")
            parsed = account_api.parse_transactions_response(response)
            transactions = parsed['content']
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
