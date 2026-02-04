"""
Account Opening 相关 API 封装
包含企业和个人账户开户申请、文档上传、申请查询等功能
遵循 API Object 模式，提供灵活的参数化接口
"""
import requests
from typing import Optional, List, Dict, Any
from config.config import config


class AccountOpeningAPI:
    """
    Account Opening 管理 API 封装类
    """
    def __init__(self, session: Optional[requests.Session] = None):
        """
        初始化 AccountOpeningAPI
        
        Args:
            session: requests.Session 对象，如果传入则使用该 session 保持认证状态
        """
        self.base_url = config.base_url
        self.config = config
        self.session = session or requests.Session()

    # ==================== 申请提交相关接口 ====================
    
    def submit_corporate_application_json(self, application_data: dict) -> requests.Response:
        """
        提交企业账户开户申请（JSON 格式）
        
        Args:
            application_data: 申请数据字典，必需字段包括：
                - name: 企业账户名称 (required)
                - business_email: 企业邮箱 (required)
                - country_incorporated: 注册国家 (required, ISO 3166)
                - date_of_adoption: 成立日期 (required, yyyy-MM-dd)
                - business_status: 运营状态 (required, Operating/Non-Operating)
                - tax_id: 税号 (required)
                - permanent_address: 永久地址对象 (required)
                - mailing_address: 邮寄地址对象 (required)
                - primary_contact: 主要联系人对象 (required)
                
                条件必需字段：
                - state_incorporated: 如果 country_incorporated 是 'United States'
                - corporation_taxed_as: 如果 business_entity_type 是 'Corporation'
                - llc_taxed_as: 如果 business_entity_type 是 'LLC'
                - international_entity_type: 如果 business_entity_type 是 'International'
                - member_name, member_ticker_symbol: 如果 related_member 是 true
                - employee_info: 如果 related_exchange_employee 是 true
                - additional_info: 如果 country_incorporated 不是 'United States'
                
        Returns:
            requests.Response: 响应对象
            
        Example:
            application_data = {
                "name": "Example Corporate Account",
                "business_email": "corporate@example.com",
                "country_incorporated": "US",
                "date_of_adoption": "2010-05-20",
                "business_status": "Operating",
                "tax_id": "13-3456789",
                "permanent_address": {...},
                "mailing_address": {...},
                "primary_contact": {...}
            }
            response = account_opening_api.submit_corporate_application_json(application_data)
        """
        url = self.config.get_full_url("/accounts/applications/corporate-clients")
        response = self.session.post(url, json=application_data)
        return response

    def submit_individual_application(self, application_data: dict) -> requests.Response:
        """
        提交个人账户开户申请
        
        Args:
            application_data: 申请数据字典，必需字段包括：
                - first_name: 名 (required)
                - last_name: 姓 (required)
                - birthdate: 生日 (required, yyyy-MM-dd)
                - email: 邮箱 (required)
                - citizenship: 国籍 (required, ISO 3166)
                - permanent_address: 永久地址对象 (required)
                - phone: 电话 (required, E.164 format)
                
                条件必需字段（如果 citizenship 是 'United States'）：
                - ssn: 加密的 SSN (required)
                - identification_type: 身份证件类型 (required)
                - identification_type_number: 证件号码 (required)
                
                条件必需字段（如果 citizenship 不是 'United States'）：
                - immigration_status: 移民状态 (required)
                - government_document_type: 政府文件类型 (required)
                - gov_id_number: 证件号码 (required)
                - gov_id_country: 证件签发国 (required)
                
                条件必需字段（如果 employment_status 是 'Employed'）：
                - employer_info: 雇主信息对象 (required)
                
                条件必需字段（如果 employer_info.current_employer 是 null）：
                - income_source: 收入来源 (required)
                
        Returns:
            requests.Response: 响应对象
            
        Example:
            application_data = {
                "first_name": "John",
                "last_name": "Doe",
                "birthdate": "1990-01-01",
                "email": "john@example.com",
                "citizenship": "US",
                "permanent_address": {...},
                "phone": "+14155552671",
                "ssn": "encrypted_ssn_string",
                "identification_type": "U.S. Drivers License",
                "identification_type_number": "D1234567"
            }
            response = account_opening_api.submit_individual_application(application_data)
        """
        url = self.config.get_full_url("/accounts/applications/individual-clients")
        response = self.session.post(url, json=application_data)
        return response

    def submit_corporate_application_formdata(self, form_data: dict, files: Optional[List] = None) -> requests.Response:
        """
        提交企业账户开户申请（multipart/form-data 格式，支持文件上传）
        
        Args:
            form_data: 表单数据字典
            files: 文件列表（可选）
            
        Returns:
            requests.Response: 响应对象
            
        Example:
            form_data = {
                "name": "Example LLC",
                "business_email": "business@example.com",
                "business_entity_type": "LLC",
                "entity_type": "Bank",
                "tax_id": "12341232",
                "permanent_address": "123 Main St",
                "permanent_city": "New York",
                "permanent_state": "NY",
                "permanent_postalcode": "10001",
                "permanent_country": "US"
            }
            response = account_opening_api.submit_corporate_application_formdata(form_data)
        """
        url = self.config.get_full_url("/accounts/applications/corporate-clients")
        
        if files:
            # 如果有文件，使用 multipart/form-data
            response = self.session.post(url, data=form_data, files=files)
        else:
            # 没有文件，只发送表单数据
            response = self.session.post(url, data=form_data)
        
        return response

    # ==================== 文档管理相关接口 ====================
    
    def upload_supplemental_documents(
        self,
        application_id: str,
        file_paths: List[str]
    ) -> requests.Response:
        """
        上传补充文档
        
        Args:
            application_id: 申请 ID
            file_paths: 文件路径列表
            
        Returns:
            requests.Response: 响应对象
            
        Example:
            file_paths = ["/path/to/doc1.pdf", "/path/to/doc2.pdf"]
            response = account_opening_api.upload_supplemental_documents(
                "application_id_123",
                file_paths
            )
        """
        url = self.config.get_full_url(f"/accounts/applications/{application_id}/files")
        
        # 准备文件
        files = []
        for file_path in file_paths:
            files.append(('files', open(file_path, 'rb')))
        
        try:
            response = self.session.post(url, files=files)
            return response
        finally:
            # 关闭所有文件
            for _, file_obj in files:
                file_obj.close()

    def list_application_documents(
        self,
        application_id: str,
        name: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        page: int = 0,
        size: int = 10,
        **kwargs
    ) -> requests.Response:
        """
        列出申请的文档列表
        
        Args:
            application_id: 申请 ID
            name: 文档名称，支持模糊搜索
            start_date: 开始日期 (yyyy-MM-dd)
            end_date: 结束日期 (yyyy-MM-dd)
            page: 页码
            size: 每页大小
            **kwargs: 其他可选参数
            
        Returns:
            requests.Response: 响应对象
            
        Example:
            response = account_opening_api.list_application_documents(
                "application_id_123",
                start_date="2025-01-01",
                end_date="2025-01-31"
            )
        """
        url = self.config.get_full_url(f"/accounts/applications/{application_id}/files")
        
        params = {"page": page, "size": size}
        
        if name is not None:
            params["name"] = name
        if start_date is not None:
            params["start_date"] = start_date
        if end_date is not None:
            params["end_date"] = end_date
        
        params.update(kwargs)
        response = self.session.get(url, params=params)
        return response

    # ==================== 申请查询相关接口 ====================
    
    def get_application_detail(self, application_id: str) -> requests.Response:
        """
        获取申请详情
        
        Args:
            application_id: 申请 ID
            
        Returns:
            requests.Response: 响应对象
            
        Example:
            response = account_opening_api.get_application_detail("application_id_123")
            if response.status_code == 200:
                application = response.json()
                print(f"Status: {application['status']}")
        """
        url = self.config.get_full_url(f"/accounts/applications/{application_id}")
        response = self.session.get(url)
        return response

    def list_applications(
        self,
        page: int = 0,
        size: int = 10,
        **kwargs
    ) -> requests.Response:
        """
        列出所有账户开户申请
        
        Args:
            page: 页码
            size: 每页大小
            **kwargs: 其他可选参数
            
        Returns:
            requests.Response: 响应对象
            
        Example:
            response = account_opening_api.list_applications(page=0, size=20)
        """
        url = self.config.get_full_url("/accounts/applications")
        params = {"page": page, "size": size}
        params.update(kwargs)
        response = self.session.get(url, params=params)
        return response

    # ==================== 响应解析辅助方法 ====================
    
    def parse_list_response(self, response: requests.Response) -> dict:
        """
        解析列表响应（申请列表、文档列表）
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
