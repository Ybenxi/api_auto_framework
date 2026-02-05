"""
Card Management 相关 API 封装
提供卡片管理的完整功能：查询、激活、锁定、更新、交易查询等
遵循 API Object 模式，提供灵活的参数化接口

⚠️ 文档问题：
1. is_virtual字段类型不一致（boolean vs string）
2. amount字段类型不一致（string vs number）
3. expiration_date格式不一致（MM/YYYY vs yyyy-MM-dd）
4. Update Card Holder vs Update Card说明不清
5. PIN加密说明不够详细
"""
import requests
from typing import Optional, Union
from config.config import config
from data.enums import CardNetwork, CardType, CardStatus, ReplaceReason
from utils.logger import logger


class CardManagementAPI:
    """
    Card Management API 封装类
    包含卡片的查询、激活、锁定、更新、交易查询等完整功能
    """
    def __init__(self, session: Optional[requests.Session] = None):
        """
        初始化 CardManagementAPI
        
        Args:
            session: requests.Session 对象，如果传入则使用该 session 保持认证状态
        """
        self.base_url = config.base_url
        self.config = config
        self.session = session or requests.Session()

    # ==================== 持卡人查询接口 ====================
    
    def list_card_holders(
        self,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        id: Optional[str] = None,
        page: int = 0,
        size: int = 10,
        **kwargs
    ) -> requests.Response:
        """
        获取持卡人列表
        
        Args:
            first_name: 持卡人名
            last_name: 持卡人姓
            id: 持卡人ID
            page: 页码，默认为 0
            size: 每页大小，默认为 10
            **kwargs: 其他可选参数
            
        Returns:
            requests.Response: 响应对象
            
        Note:
            ⚠️ 文档问题：响应中有"country:"字段名拼写错误（多余冒号）
        """
        url = self.config.get_full_url("/card-issuance/card-holders")
        params = {"page": page, "size": size}
        
        if first_name is not None:
            params["first_name"] = first_name
        if last_name is not None:
            params["last_name"] = last_name
        if id is not None:
            params["id"] = id
        
        params.update(kwargs)
        logger.debug(f"请求持卡人列表: {params}")
        
        response = self.session.get(url, params=params)
        logger.debug(f"响应状态: {response.status_code}")
        
        return response

    # ==================== 卡片查询接口 ====================
    
    def list_cards(
        self,
        card_number: Optional[str] = None,
        network: Optional[Union[str, CardNetwork]] = None,
        card_type: Optional[Union[str, CardType]] = None,
        card_status: Optional[Union[str, CardStatus]] = None,
        is_virtual: Optional[bool] = None,
        financial_account_id: Optional[str] = None,
        card_holder_id: Optional[str] = None,
        page: int = 0,
        size: int = 10,
        **kwargs
    ) -> requests.Response:
        """
        获取卡片列表
        
        Args:
            card_number: 卡号（tokenized）或card ID
            network: 卡片网络（Visa/Mastercard）
            card_type: 卡片类型
            card_status: 卡片状态
            is_virtual: 是否虚拟卡
            financial_account_id: Financial Account ID
            card_holder_id: 持卡人ID
            page: 页码，默认为 0
            size: 每页大小，默认为 10
            **kwargs: 其他可选参数
            
        Returns:
            requests.Response: 响应对象
        """
        url = self.config.get_full_url("/card-issuance/cards")
        params = {"page": page, "size": size}
        
        if card_number is not None:
            params["card_number"] = card_number
        if network is not None:
            params["network"] = str(network) if isinstance(network, CardNetwork) else network
        if card_type is not None:
            params["card_type"] = str(card_type) if isinstance(card_type, CardType) else card_type
        if card_status is not None:
            params["card_status"] = str(card_status) if isinstance(card_status, CardStatus) else card_status
        if is_virtual is not None:
            params["is_virtual"] = is_virtual
        if financial_account_id is not None:
            params["financial_account_id"] = financial_account_id
        if card_holder_id is not None:
            params["card_holder_id"] = card_holder_id
        
        params.update(kwargs)
        logger.debug(f"请求卡片列表: {params}")
        
        response = self.session.get(url, params=params)
        logger.debug(f"响应状态: {response.status_code}")
        
        return response

    def get_card_detail(self, card_number: str) -> requests.Response:
        """
        获取卡片详情
        
        Args:
            card_number: 卡号（tokenized）或card ID
            
        Returns:
            requests.Response: 响应对象
        """
        url = self.config.get_full_url(f"/card-issuance/cards/{card_number}")
        logger.debug(f"请求卡片详情: {card_number}")
        
        response = self.session.get(url)
        logger.debug(f"响应状态: {response.status_code}")
        
        return response

    def get_card_remaining_usage(
        self,
        card_number: str,
        nested_program_id: Optional[str] = None
    ) -> requests.Response:
        """
        获取卡片剩余可用额度
        返回当前时间间隔内的可用限额
        
        Args:
            card_number: 卡号（tokenized）或card ID
            nested_program_id: 嵌套项目ID（可选）
            
        Returns:
            requests.Response: 响应对象，包含：
                - id: 卡片ID
                - spending_limit: 剩余消费限制数组
                - associated_nested_program: 关联嵌套项目的剩余额度
        """
        url = self.config.get_full_url(f"/card-issuance/cards/{card_number}/remaining-usage")
        params = {}
        
        if nested_program_id is not None:
            params["nested_program_id"] = nested_program_id
        
        logger.debug(f"请求卡片剩余额度: {card_number}")
        
        response = self.session.get(url, params=params)
        logger.debug(f"响应状态: {response.status_code}")
        
        return response

    # ==================== 交易查询接口 ====================
    
    def list_card_transactions(
        self,
        card_number: Optional[str] = None,
        transaction_id: Optional[str] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        customer: Optional[str] = None,
        network: Optional[Union[str, CardNetwork]] = None,
        is_virtual: Optional[bool] = None,
        merchant_id: Optional[str] = None,
        merchant_name: Optional[str] = None,
        status: Optional[str] = None,
        page: int = 0,
        size: int = 10,
        **kwargs
    ) -> requests.Response:
        """
        获取卡片交易列表
        
        Args:
            card_number: 卡号或card ID
            transaction_id: 交易ID
            start_time: 开始时间（UTC，格式 yyyy-MM-dd HH:mm:ss）
            end_time: 结束时间（UTC，格式 yyyy-MM-dd HH:mm:ss）
            customer: 持卡人姓名
            network: 卡片网络
            is_virtual: 是否虚拟卡
            merchant_id: 商户ID
            merchant_name: 商户名称
            status: 交易状态
            page: 页码，默认为 0
            size: 每页大小，默认为 10
            **kwargs: 其他可选参数
            
        Returns:
            requests.Response: 响应对象
            
        Note:
            ⚠️ 文档问题：响应中is_virtual是string类型（应为boolean）
        """
        url = self.config.get_full_url("/card-issuance/cards/transactions")
        params = {"page": page, "size": size}
        
        if card_number is not None:
            params["card_number"] = card_number
        if transaction_id is not None:
            params["transaction_id"] = transaction_id
        if start_time is not None:
            params["start_time"] = start_time
        if end_time is not None:
            params["end_time"] = end_time
        if customer is not None:
            params["customer"] = customer
        if network is not None:
            params["network"] = str(network) if isinstance(network, CardNetwork) else network
        if is_virtual is not None:
            params["is_virtual"] = is_virtual
        if merchant_id is not None:
            params["merchant_id"] = merchant_id
        if merchant_name is not None:
            params["merchant_name"] = merchant_name
        if status is not None:
            params["status"] = status
        
        params.update(kwargs)
        logger.debug(f"请求交易列表: {params}")
        
        response = self.session.get(url, params=params)
        logger.debug(f"响应状态: {response.status_code}")
        
        return response

    def get_transaction_detail(self, transaction_id: str) -> requests.Response:
        """
        获取交易详情
        
        Args:
            transaction_id: 交易ID
            
        Returns:
            requests.Response: 响应对象
            
        Note:
            ⚠️ 文档问题：
            1. JSON格式错误（缺少逗号）
            2. transaction_histories字段未在Properties定义
        """
        url = self.config.get_full_url(f"/card-issuance/cards/transactions/{transaction_id}")
        logger.debug(f"请求交易详情: {transaction_id}")
        
        response = self.session.get(url)
        logger.debug(f"响应状态: {response.status_code}")
        
        return response

    # ==================== 卡片操作接口 ====================
    
    def activate_card(self, card_number: str, encrypted_pin: str) -> requests.Response:
        """
        激活卡片
        
        Args:
            card_number: 卡号或card ID
            encrypted_pin: RSA加密后的PIN（Base64编码）
            
        Returns:
            requests.Response: 响应对象
            
        Note:
            ⚠️ 重要：PIN加密要求
            1. 必须是4位数字
            2. 使用Portal Dashboard的公钥
            3. RSA + PKCS1Padding加密
            4. Base64编码
            
            测试建议：由于加密复杂，建议skip此类测试
        """
        url = self.config.get_full_url(f"/card-issuance/cards/{card_number}/activate")
        
        payload = {"pin": encrypted_pin}
        logger.debug(f"激活卡片: {card_number}")
        
        response = self.session.patch(url, json=payload)
        logger.debug(f"响应状态: {response.status_code}")
        
        return response

    def block_card(self, card_number: str) -> requests.Response:
        """
        锁定卡片
        
        Args:
            card_number: 卡号或card ID
            
        Returns:
            requests.Response: 响应对象
            
        Note:
            ⚠️ 破坏性操作：锁定卡片会影响持卡人使用
        """
        url = self.config.get_full_url(f"/card-issuance/cards/{card_number}/block")
        logger.debug(f"锁定卡片: {card_number}")
        
        response = self.session.patch(url)
        logger.debug(f"响应状态: {response.status_code}")
        
        return response

    def unblock_card(self, card_number: str) -> requests.Response:
        """
        解锁卡片
        
        Args:
            card_number: 卡号或card ID
            
        Returns:
            requests.Response: 响应对象
        """
        url = self.config.get_full_url(f"/card-issuance/cards/{card_number}/unblock")
        logger.debug(f"解锁卡片: {card_number}")
        
        response = self.session.patch(url)
        logger.debug(f"响应状态: {response.status_code}")
        
        return response

    def change_card_pin(self, card_number: str, encrypted_new_pin: str) -> requests.Response:
        """
        更改卡片PIN
        
        Args:
            card_number: 卡号或card ID
            encrypted_new_pin: RSA加密后的新PIN（Base64编码）
            
        Returns:
            requests.Response: 响应对象
            
        Note:
            ⚠️ PIN加密要求同activate_card()
            测试建议：skip此类测试
        """
        url = self.config.get_full_url(f"/card-issuance/cards/{card_number}/change-pin")
        
        payload = {"new_pin": encrypted_new_pin}
        logger.debug(f"更改卡片PIN: {card_number}")
        
        response = self.session.patch(url, json=payload)
        logger.debug(f"响应状态: {response.status_code}")
        
        return response

    def replace_card(
        self,
        card_number: str,
        reason: Union[str, ReplaceReason],
        mailing_name: str,
        address1: str,
        city: str,
        state: str,
        zip: str,
        country: str,
        expiration_date: str,
        address2: Optional[str] = None,
        **kwargs
    ) -> requests.Response:
        """
        替换卡片（仅适用于实体卡）
        
        Args:
            card_number: 卡号或card ID
            reason: 替换原因（Reissued/Lost）
            mailing_name: 持卡人姓名
            address1: 地址1（必需）
            city: 城市（必需）
            state: 州代码（必需）
            zip: 邮编（必需）
            country: 国家（必需）
            expiration_date: 过期日期（必需，格式 yyyy-MM-dd）
            address2: 地址2（可选）
            **kwargs: 其他可选参数
            
        Returns:
            requests.Response: 响应对象
            
        Note:
            ⚠️ 文档问题：expiration_date格式冲突
            - Card Properties定义：MM/yyyy
            - Replace接口要求：yyyy-MM-dd
            这是不合理的，建议统一格式
            
            ⚠️ 破坏性操作：替换卡片不可逆
        """
        url = self.config.get_full_url(f"/card-issuance/cards/{card_number}/replace")
        
        payload = {
            "reason": str(reason) if isinstance(reason, ReplaceReason) else reason,
            "mailing_name": mailing_name,
            "address1": address1,
            "city": city,
            "state": state,
            "zip": zip,
            "country": country,
            "expiration_date": expiration_date
        }
        
        if address2 is not None:
            payload["address2"] = address2
        
        payload.update(kwargs)
        logger.debug(f"替换卡片: {card_number}, 原因: {reason}")
        
        response = self.session.patch(url, json=payload)
        logger.debug(f"响应状态: {response.status_code}")
        
        return response

    def update_card_holder_info(
        self,
        card_number: str,
        first_name: str,
        last_name: str,
        address1: str,
        city: str,
        state: str,
        zip: str,
        country: str,
        middle_name: Optional[str] = None,
        address2: Optional[str] = None,
        **kwargs
    ) -> requests.Response:
        """
        更新持卡人信息
        
        Args:
            card_number: 卡号或card ID
            first_name: 名（必需）
            last_name: 姓（必需）
            address1: 地址1（必需）
            city: 城市（必需）
            state: 州代码（必需）
            zip: 邮编（必需）
            country: 国家（必需）
            middle_name: 中间名（可选）
            address2: 地址2（可选）
            **kwargs: 其他可选参数
            
        Returns:
            requests.Response: 响应对象
            
        Note:
            ⚠️ 重要：此接口会更新持卡人名下所有卡片的地址信息
            与update_card()的区别：
            - update_card_holder_info: 更新所有关联卡片
            - update_card: 只更新当前卡片
        """
        url = self.config.get_full_url(f"/card-issuance/cards/{card_number}/card-holder")
        
        payload = {
            "first_name": first_name,
            "last_name": last_name,
            "address1": address1,
            "city": city,
            "state": state,
            "zip": zip,
            "country": country
        }
        
        if middle_name is not None:
            payload["middle_name"] = middle_name
        if address2 is not None:
            payload["address2"] = address2
        
        payload.update(kwargs)
        logger.debug(f"更新持卡人信息: {card_number}")
        
        response = self.session.put(url, json=payload)
        logger.debug(f"响应状态: {response.status_code}")
        
        return response

    def update_card_info(
        self,
        card_number: str,
        first_name: str,
        last_name: str,
        address1: str,
        city: str,
        state: str,
        zip: str,
        country: str,
        middle_name: Optional[str] = None,
        address2: Optional[str] = None,
        **kwargs
    ) -> requests.Response:
        """
        更新卡片信息
        
        Args:
            card_number: 卡号或card ID
            first_name: 名（必需）
            last_name: 姓（必需）
            address1: 地址1（必需）
            city: 城市（必需）
            state: 州代码（必需）
            zip: 邮编（必需）
            country: 国家（必需）
            middle_name: 中间名（可选）
            address2: 地址2（可选）
            **kwargs: 其他可选参数
            
        Returns:
            requests.Response: 响应对象
            
        Note:
            ⚠️ 重要：此接口只更新当前卡片的地址信息
            与update_card_holder_info()的区别：
            - update_card_holder_info: 更新所有关联卡片
            - update_card: 只更新当前卡片
        """
        url = self.config.get_full_url(f"/card-issuance/cards/{card_number}")
        
        payload = {
            "first_name": first_name,
            "last_name": last_name,
            "address1": address1,
            "city": city,
            "state": state,
            "zip": zip,
            "country": country
        }
        
        if middle_name is not None:
            payload["middle_name"] = middle_name
        if address2 is not None:
            payload["address2"] = address2
        
        payload.update(kwargs)
        logger.debug(f"更新卡片信息: {card_number}")
        
        response = self.session.put(url, json=payload)
        logger.debug(f"响应状态: {response.status_code}")
        
        return response

    def generate_iframe_token(self, card_number: str) -> requests.Response:
        """
        生成iFrame Token
        用于打开iFrame展示卡片信息
        
        Args:
            card_number: 卡号或card ID
            
        Returns:
            requests.Response: 响应对象，包含：
                - code: 业务状态码
                - data.token: 生成的token（Base64编码）
                
        Note:
            ⚠️ Token过期规则：
            - 生成后5分钟过期
            - 或使用一次后过期
            - 不可重复使用
        """
        url = self.config.get_full_url("/card-issuance/cards/token")
        
        payload = {"card_number": card_number}
        logger.debug(f"生成iFrame Token: {card_number}")
        
        response = self.session.post(url, json=payload)
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
