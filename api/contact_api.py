"""
Contact 相关 API 封装
遵循 API Object 模式，提供完整的 CRUD 接口
"""
import requests
from typing import Optional
from config.config import config


class ContactAPI:
    """
    Contact 管理 API 封装类
    """
    def __init__(self, session: Optional[requests.Session] = None):
        """
        初始化 ContactAPI
        
        Args:
            session: requests.Session 对象，如果传入则使用该 session 保持认证状态
        """
        self.base_url = config.base_url
        self.config = config
        # 如果传入了 session，则使用该 session 发送请求，保持 Auth 状态
        self.session = session or requests.Session()

    def list_contacts(
        self,
        name: Optional[str] = None,
        email: Optional[str] = None,
        status: Optional[str] = None,
        page: int = 0,
        size: int = 10,
        **kwargs
    ) -> requests.Response:
        """
        获取 Contacts 列表
        
        Args:
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
            response = contact_api.list_contacts()
            
            # 使用筛选条件
            response = contact_api.list_contacts(
                status="Active",
                page=0,
                size=20
            )
        """
        url = self.config.get_full_url("/contacts")
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

    def create_contact(self, contact_data: dict) -> requests.Response:
        """
        创建 Contact
        
        Args:
            contact_data: Contact 数据字典，必需字段：
                - account_id: 关联的 Profile Account ID
                - first_name: 名字
                - last_name: 姓氏
                - birth_date: 出生日期（YYYY-MM-DD）
                - email: 邮箱
                可选字段：
                - middle_name: 中间名
                - ssn_tin: 加密的 SSN/TIN
                - phone: 电话号码（E.164 格式）
                - 其他字段参见接口文档
                
        Returns:
            requests.Response: 响应对象
            
        Example:
            contact_data = {
                "account_id": "251212054045554351",
                "first_name": "John",
                "last_name": "Doe",
                "birth_date": "1990-01-01",
                "email": "john.doe@example.com",
                "ssn_tin": "encrypted_ssn_string"
            }
            response = contact_api.create_contact(contact_data)
        """
        url = self.config.get_full_url("/contacts")
        response = self.session.post(url, json=contact_data)
        return response

    def get_contact_detail(self, contact_id: str) -> requests.Response:
        """
        获取 Contact 详情
        
        Args:
            contact_id: Contact ID
            
        Returns:
            requests.Response: 响应对象
            
        Example:
            response = contact_api.get_contact_detail("1717780644733WluDa")
        """
        url = self.config.get_full_url(f"/contacts/{contact_id}")
        response = self.session.get(url)
        return response

    def update_contact(self, contact_id: str, update_data: dict) -> requests.Response:
        """
        更新 Contact 信息
        
        Args:
            contact_id: Contact ID
            update_data: 要更新的字段字典，可选字段：
                - first_name: 名字
                - last_name: 姓氏
                - birth_date: 出生日期
                - middle_name: 中间名
                - phone: 电话号码
                - mobile_phone: 手机号码
                - permanent_address: 永久地址
                - mailing_street: 邮寄地址
                - 其他字段参见接口文档
                
        Returns:
            requests.Response: 响应对象
            
        Example:
            update_data = {
                "first_name": "Jane",
                "phone": "+14155552671"
            }
            response = contact_api.update_contact("1717780644733WluDa", update_data)
        """
        url = self.config.get_full_url(f"/contacts/{contact_id}")
        response = self.session.put(url, json=update_data)
        return response

    def get_contact_ssn(self, contact_id: str, secret: str) -> requests.Response:
        """
        获取 Contact 的 SSN（加密）
        
        Args:
            contact_id: Contact ID
            secret: 加密的 AES Key（使用 RSA 加密，需要 URL 编码）
            
        Returns:
            requests.Response: 响应对象
            
        Example:
            secret = "encrypted_aes_key_string"
            response = contact_api.get_contact_ssn("1717780644733WluDa", secret)
        """
        url = self.config.get_full_url(f"/contacts/{contact_id}/ssn")
        params = {"secret": secret}
        response = self.session.get(url, params=params)
        return response

    def parse_list_response(self, response: requests.Response) -> dict:
        """
        解析 Contacts 列表响应
        
        Args:
            response: requests.Response 对象
            
        Returns:
            dict: 包含 content（Contacts 列表）、pageable（分页信息）等字段
            
        Example:
            response = contact_api.list_contacts()
            parsed = contact_api.parse_list_response(response)
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
