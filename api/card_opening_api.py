"""
Card Opening 相关 API 封装
提供借记卡和奖励卡申请的创建和查询功能
遵循 API Object 模式，提供灵活的参数化接口

⚠️ 文档问题：
1. JSON格式错误（缺少逗号，至少6处）
2. 示例数据不现实（Reward Card）
3. 条件必需字段说明不清（classification_type）
4. birth_date vs birthdate命名不一致
5. Detail接口响应无code包装层（格式不一致）
"""
import requests
from typing import Optional, Union, List
from config.config import config
from data.enums import LimitType
from utils.logger import logger


class CardOpeningAPI:
    """
    Card Opening API 封装类
    包含借记卡和奖励卡申请的创建、查询功能
    """
    def __init__(self, session: Optional[requests.Session] = None):
        """
        初始化 CardOpeningAPI
        
        Args:
            session: requests.Session 对象，如果传入则使用该 session 保持认证状态
        """
        self.base_url = config.base_url
        self.config = config
        self.session = session or requests.Session()

    # ==================== 创建申请接口 ====================
    
    def create_debit_card_application(
        self,
        sub_program_id: str,
        card_holder_id: str,
        expiration_date: str,
        limit_type: Optional[Union[str, LimitType]] = None,
        financial_account_id: Optional[str] = None,
        spending_limit: Optional[List[dict]] = None,
        associated_nested_program: Optional[List[dict]] = None,
        location: Optional[List[str]] = None,
        nested_program_only: Optional[bool] = None,
        **kwargs
    ) -> requests.Response:
        """
        提交借记卡申请
        
        Args:
            sub_program_id: 子项目ID（必需）
            card_holder_id: 持卡人ID（必需）
            expiration_date: 过期日期，格式 MM/YYYY（必需）
            limit_type: 限制类型（Calendar_Date或Active_Date）
            financial_account_id: Financial Account ID（条件必需）
            spending_limit: 消费限制数组
            associated_nested_program: 关联的嵌套项目数组
            location: 国家代码列表（ISO 3166）
            nested_program_only: 是否仅限嵌套项目商户
            **kwargs: 其他可选参数
            
        Returns:
            requests.Response: 响应对象，包含：
                - code: 业务状态码
                - data: 申请数据
                    - id: 申请ID
                    - status: 申请状态（approved等）
                    - card_id: 生成的卡片ID
                    
        Note:
            ⚠️ 文档问题：
            1. financial_account_id条件必需（classification_type='Consumer'时）
            2. 但请求参数中没有classification_type字段，逻辑不清
            3. JSON格式错误（缺少逗号）
        """
        url = self.config.get_full_url("/card-issuance/applications/debit-card")
        
        payload = {
            "sub_program_id": sub_program_id,
            "card_holder_id": card_holder_id,
            "expiration_date": expiration_date
        }
        
        if limit_type is not None:
            payload["limit_type"] = str(limit_type) if isinstance(limit_type, LimitType) else limit_type
        if financial_account_id is not None:
            payload["financial_account_id"] = financial_account_id
        if spending_limit is not None:
            payload["spending_limit"] = spending_limit
        if associated_nested_program is not None:
            payload["associated_nested_program"] = associated_nested_program
        if location is not None:
            payload["location"] = location
        if nested_program_only is not None:
            payload["nested_program_only"] = nested_program_only
        
        payload.update(kwargs)
        logger.debug(f"创建借记卡申请: card_holder={card_holder_id}")
        
        response = self.session.post(url, json=payload)
        logger.debug(f"响应状态: {response.status_code}")
        
        return response

    def create_reward_card_application(
        self,
        sub_program_id: str,
        email: str,
        first_name: str,
        last_name: str,
        ssn: str,
        telephone: str,
        address1: str,
        city: str,
        state: str,
        postalcode: str,
        birth_date: str,
        expiration_date: str,
        middle_name: Optional[str] = None,
        address2: Optional[str] = None,
        limit_type: Optional[Union[str, LimitType]] = None,
        spending_limit: Optional[List[dict]] = None,
        associated_nested_program: Optional[List[dict]] = None,
        location: Optional[List[str]] = None,
        nested_program_only: Optional[bool] = None,
        **kwargs
    ) -> requests.Response:
        """
        提交奖励卡申请（通过持卡人信息）
        
        Args:
            sub_program_id: 子项目ID（必需）
            email: 持卡人邮箱（必需）
            first_name: 名（必需）
            last_name: 姓（必需）
            ssn: SSN（必需，4位数字，需要RSA加密）
            telephone: 电话号码（必需，无短横线）
            address1: 地址1（必需）
            city: 城市（必需）
            state: 州代码（必需，2字母）
            postalcode: 邮编（必需，5或9位）
            birth_date: 出生日期（必需，格式 yyyy-MM-dd）
            expiration_date: 过期日期（必需，格式 MM/YYYY）
            middle_name: 中间名（可选）
            address2: 地址2（可选）
            limit_type: 限制类型
            spending_limit: 消费限制数组
            associated_nested_program: 关联的嵌套项目
            location: 国家代码列表
            nested_program_only: 是否仅限嵌套项目
            **kwargs: 其他可选参数
            
        Returns:
            requests.Response: 响应对象
            
        Note:
            ⚠️ 重要：
            1. SSN必须加密（RSA + PKCS1Padding）
            2. state必须是有效的2字母州代码
            3. 测试时建议skip（需要加密实现）
            
            ⚠️ 文档问题：
            1. 示例数据不现实（"example ssn"应为加密后的值）
            2. JSON格式错误（缺少逗号）
        """
        url = self.config.get_full_url("/card-issuance/applications/reward-card")
        
        payload = {
            "sub_program_id": sub_program_id,
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
            "ssn": ssn,
            "telephone": telephone,
            "address1": address1,
            "city": city,
            "state": state,
            "postalcode": postalcode,
            "birth_date": birth_date,
            "expiration_date": expiration_date
        }
        
        if middle_name is not None:
            payload["middle_name"] = middle_name
        if address2 is not None:
            payload["address2"] = address2
        if limit_type is not None:
            payload["limit_type"] = str(limit_type) if isinstance(limit_type, LimitType) else limit_type
        if spending_limit is not None:
            payload["spending_limit"] = spending_limit
        if associated_nested_program is not None:
            payload["associated_nested_program"] = associated_nested_program
        if location is not None:
            payload["location"] = location
        if nested_program_only is not None:
            payload["nested_program_only"] = nested_program_only
        
        payload.update(kwargs)
        logger.debug(f"创建奖励卡申请: email={email}")
        
        response = self.session.post(url, json=payload)
        logger.debug(f"响应状态: {response.status_code}")
        
        return response

    # ==================== 查询申请接口 ====================
    
    def list_applications(
        self,
        status: Optional[str] = None,
        page: int = 0,
        size: int = 10,
        **kwargs
    ) -> requests.Response:
        """
        获取卡片申请列表
        
        Args:
            status: 申请状态（approved等）
            page: 页码，默认为 0
            size: 每页大小，默认为 10
            **kwargs: 其他可选参数
            
        Returns:
            requests.Response: 响应对象，包含：
                - code: 业务状态码
                - data: 分页数据
                    - content: 申请列表
                    - pageable: 分页信息
        """
        url = self.config.get_full_url("/card-issuance/applications")
        params = {"page": page, "size": size}
        
        if status is not None:
            params["status"] = status
        
        params.update(kwargs)
        logger.debug(f"请求申请列表: {params}")
        
        response = self.session.get(url, params=params)
        logger.debug(f"响应状态: {response.status_code}")
        
        return response

    def get_application_detail(self, application_id: str) -> requests.Response:
        """
        获取申请详情
        
        Args:
            application_id: 申请ID
            
        Returns:
            requests.Response: 响应对象
            
        Note:
            ⚠️ 文档问题：
            Detail接口响应无code包装层，与其他接口格式不一致
            - List和Create: {"code": 200, "data": {...}}
            - Detail: {"id": "...", "status": "...", ...}
        """
        url = self.config.get_full_url(f"/card-issuance/applications/{application_id}")
        logger.debug(f"请求申请详情: {application_id}")
        
        response = self.session.get(url)
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
            
            content_data = data.get("data", data)
            
            return {
                "error": False,
                "content": content_data.get("content", []),
                "pageable": content_data.get("pageable", {}),
                "total_elements": content_data.get("total_elements", 0),
                "total_pages": content_data.get("total_pages", 0)
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
        兼容有无code包装层两种格式
        
        Args:
            response: requests.Response 对象
            
        Returns:
            dict: 包含 error 标识和详情数据
        """
        if response.status_code != 200:
            return {
                "error": True,
                "status_code": response.status_code,
                "message": response.text
            }
        
        try:
            data = response.json()
            
            # 检查是否有code字段（标准格式）
            if "code" in data:
                if data["code"] != 200:
                    return {
                        "error": True,
                        "code": data["code"],
                        "message": data.get("error_message", "Unknown error")
                    }
                return {
                    "error": False,
                    "data": data.get("data", {})
                }
            else:
                # 无code包装层（Detail接口的特殊情况）
                return {
                    "error": False,
                    "data": data,
                    "no_code_wrapper": True
                }
        except Exception as e:
            logger.error(f"解析响应失败: {e}", exc_info=True)
            return {
                "error": True,
                "message": f"Failed to parse response: {str(e)}",
                "raw_response": response.text
            }
