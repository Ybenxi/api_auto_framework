"""
Wire Processing 相关 API 封装
提供国内和国际电汇转账功能
遵循 API Object 模式，提供灵活的参数化接口

⚠️ 文档问题（45个）：
1. HTTP方法示例错误（2处）
2. URL路径不一致（2处）
3. 响应格式不一致（7个接口无code包装层）
4. Create Counterparty条件必需字段规则极其复杂且说明混乱
5. 大量响应字段未在Properties定义（40+个）
6. Wire vs International Wire接口完全重复但分两个接口

⚠️ 重要提醒：
- 所有payment接口会真实扣款，不可撤销
- Create Counterparty参数极其复杂，有多层条件必需逻辑
- 测试时必须使用专门的测试账户
"""
import requests
from typing import Optional, Union, List
from config.config import config
from data.enums import (
    PaymentTransactionStatus, 
    PaymentTransactionType,
    WirePaymentType,
    CounterpartyType,
    BankAccountType,
    AccountSubType
)
from utils.logger import logger


class WireProcessingAPI:
    """
    Wire Processing API 封装类
    提供电汇转账的完整功能：查询、创建对手方、发起转账
    
    ⚠️ 重要：此模块包含真实转账操作，会实际扣款
    """
    def __init__(self, session: Optional[requests.Session] = None):
        """
        初始化 WireProcessingAPI
        
        Args:
            session: requests.Session 对象
        """
        self.base_url = config.base_url
        self.config = config
        self.session = session or requests.Session()

    # ==================== 查询接口 ====================
    
    def list_transactions(
        self,
        transaction_id: Optional[str] = None,
        financial_account_id: Optional[str] = None,
        payment_type: Optional[Union[str, WirePaymentType]] = None,
        counterparty_id: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        status: Optional[Union[str, PaymentTransactionStatus]] = None,
        transaction_type: Optional[Union[str, PaymentTransactionType]] = None,
        page: int = 0,
        size: int = 10,
        **kwargs
    ) -> requests.Response:
        """
        获取电汇交易列表
        
        Args:
            transaction_id: 交易ID
            financial_account_id: Financial Account ID
            payment_type: 支付类型（Wire或International_Wire）
            counterparty_id: 对手方ID
            start_date: 开始日期（UTC，格式YYYY-MM-DD）
            end_date: 结束日期（UTC，格式YYYY-MM-DD）
            status: 交易状态
            transaction_type: 交易类型（Credit或Debit）
            page: 页码
            size: 每页大小
            
        Returns:
            requests.Response: 响应对象
            
        Note:
            ⚠️ 文档问题：
            1. 响应无code包装层
            2. 响应中有12+个字段未在Properties定义
        """
        url = self.config.get_full_url("/money-movements/wire/transactions")
        params = {"page": page, "size": size}
        
        if transaction_id is not None:
            params["transaction_id"] = transaction_id
        if financial_account_id is not None:
            params["financial_account_id"] = financial_account_id
        if payment_type is not None:
            params["payment_type"] = str(payment_type) if isinstance(payment_type, WirePaymentType) else payment_type
        if counterparty_id is not None:
            params["counterparty_id"] = counterparty_id
        if start_date is not None:
            params["start_date"] = start_date
        if end_date is not None:
            params["end_date"] = end_date
        if status is not None:
            params["status"] = str(status) if isinstance(status, PaymentTransactionStatus) else status
        if transaction_type is not None:
            params["transaction_type"] = str(transaction_type) if isinstance(transaction_type, PaymentTransactionType) else transaction_type
        
        params.update(kwargs)
        logger.debug(f"请求Wire交易列表: {params}")
        
        response = self.session.get(url, params=params)
        logger.debug(f"响应状态: {response.status_code}")
        
        return response

    def list_financial_accounts(
        self,
        account_number: Optional[str] = None,
        name: Optional[str] = None,
        sub_type: Optional[Union[str, AccountSubType]] = None,
        account_ids: Optional[Union[List[str], str]] = None,
        page: int = 0,
        size: int = 10,
        **kwargs
    ) -> requests.Response:
        """
        获取可用于电汇的Financial Accounts列表
        
        Args:
            account_number: 账号
            name: 账户名称（模糊搜索）
            sub_type: 账户子类型
            account_ids: 账户ID数组或逗号分隔字符串
            page: 页码
            size: 每页大小
            
        Returns:
            requests.Response: 响应对象
            
        Note:
            ⚠️ 文档问题：
            1. HTTP方法示例错误（GET写成POST）
            2. 响应无code包装层
        """
        url = self.config.get_full_url("/money-movements/wire/financial-accounts")
        params = {"page": page, "size": size}
        
        if account_number is not None:
            params["account_number"] = account_number
        if name is not None:
            params["name"] = name
        if sub_type is not None:
            params["sub_type"] = str(sub_type) if isinstance(sub_type, AccountSubType) else sub_type
        if account_ids is not None:
            if isinstance(account_ids, list):
                params["account_ids"] = ",".join(account_ids)
            else:
                params["account_ids"] = account_ids
        
        params.update(kwargs)
        logger.debug(f"请求Wire可用账户列表: {params}")
        
        response = self.session.get(url, params=params)
        logger.debug(f"响应状态: {response.status_code}")
        
        return response

    def list_counterparties(
        self,
        financial_account_id: Optional[str] = None,
        account_ids: Optional[Union[List[str], str]] = None,
        payment_type: Optional[Union[str, WirePaymentType]] = None,
        name: Optional[str] = None,
        bank_account_owner_name: Optional[str] = None,
        page: int = 0,
        size: int = 10,
        **kwargs
    ) -> requests.Response:
        """
        获取电汇对手方列表
        
        Args:
            financial_account_id: Financial Account ID
            account_ids: 账户ID数组
            payment_type: 支付类型（Wire或International_Wire）
            name: 对手方名称
            bank_account_owner_name: 银行账户所有人名称
            page: 页码
            size: 每页大小
            
        Returns:
            requests.Response: 响应对象
            
        Note:
            ⚠️ 文档问题：
            1. 响应无code包装层
            2. 响应中有40+个字段未在Properties定义
            3. List说明逻辑混乱
        """
        url = self.config.get_full_url("/money-movements/wire/counterparties")
        params = {"page": page, "size": size}
        
        if financial_account_id is not None:
            params["financial_account_id"] = financial_account_id
        if account_ids is not None:
            if isinstance(account_ids, list):
                params["account_ids"] = ",".join(account_ids)
            else:
                params["account_ids"] = account_ids
        if payment_type is not None:
            params["payment_type"] = str(payment_type) if isinstance(payment_type, WirePaymentType) else payment_type
        if name is not None:
            params["name"] = name
        if bank_account_owner_name is not None:
            params["bank_account_owner_name"] = bank_account_owner_name
        
        params.update(kwargs)
        logger.debug(f"请求Wire对手方列表: {params}")
        
        response = self.session.get(url, params=params)
        logger.debug(f"响应状态: {response.status_code}")
        
        return response

    # ==================== 对手方管理接口 ====================
    
    def create_counterparty(
        self,
        name: str,
        type: Union[str, CounterpartyType],
        bank_account_type: Union[str, BankAccountType],
        bank_account_owner_name: str,
        bank_account_number: str,
        payment_type: Optional[Union[str, WirePaymentType]] = None,
        # Wire类型条件必需
        bank_routing_number: Optional[str] = None,
        # International_Wire类型条件必需
        country: Optional[str] = None,
        address1: Optional[str] = None,
        address2: Optional[str] = None,
        city: Optional[str] = None,
        state: Optional[str] = None,
        zip_code: Optional[str] = None,
        bank_country: Optional[str] = None,
        swift_code: Optional[str] = None,
        bank_name: Optional[str] = None,
        bank_address: Optional[str] = None,
        bank_city: Optional[str] = None,
        bank_state: Optional[str] = None,
        bank_zip_code: Optional[str] = None,
        phone_number: Optional[str] = None,
        # Intermediary Bank (第一组) - 条件必需
        intermediary_financial_institution: Optional[str] = None,
        intermediary_bank_routing_number: Optional[str] = None,
        intermediary_bank_address1: Optional[str] = None,
        intermediary_bank_address2: Optional[str] = None,
        intermediary_bank_city: Optional[str] = None,
        intermediary_bank_state: Optional[str] = None,
        intermediary_bank_zip_code: Optional[str] = None,
        intermediary_bank_country: Optional[str] = None,
        # Intermediary Bank 2 (第二组) - 条件必需
        intermediary_bank2_institution: Optional[str] = None,
        intermediary_bank2_routing_number: Optional[str] = None,
        intermediary_bank2_swift_code: Optional[str] = None,
        intermediary_bank2_address1: Optional[str] = None,
        intermediary_bank2_address2: Optional[str] = None,
        intermediary_bank2_city: Optional[str] = None,
        intermediary_bank2_state: Optional[str] = None,
        intermediary_bank2_zip_code: Optional[str] = None,
        intermediary_bank2_country: Optional[str] = None,
        # 账户分配
        assign_account_ids: Optional[List[str]] = None,
        **kwargs
    ) -> requests.Response:
        """
        创建电汇对手方
        
        ⚠️⚠️⚠️ 极其复杂的条件必需字段逻辑 ⚠️⚠️⚠️
        
        Args:
            name: 对手方名称（必需）
            type: 对手方类型（必需，Employee/Company/Person/Vendor）
            bank_account_type: 银行账户类型（必需，Savings/Checking）
            bank_account_owner_name: 账户所有人姓名（必需）
            bank_account_number: 银行账号（必需）
            
            payment_type: 支付类型（Wire或International_Wire，默认Wire）
            
            === Wire类型条件必需字段 ===
            bank_routing_number: 路由号（payment_type=Wire时必需）
            
            === International_Wire类型条件必需字段 ===
            country: 国家（必需）
            address1: 地址1（必需）
            city: 城市（必需）
            state: 州（必需）
            zip_code: 邮编（必需）
            bank_country: 银行国家（必需）
            swift_code: SWIFT代码（必需，8或11字符）
            bank_name: 银行名称（必需）
            bank_address: 银行地址（必需）
            bank_city: 银行城市（必需）
            bank_state: 银行州（必需）
            bank_zip_code: 银行邮编（必需）
            
            === Intermediary Bank条件必需字段（第一组）===
            如果提供了任何intermediary bank字段，则以下字段必需：
            - intermediary_financial_institution（必需）
            - intermediary_bank_routing_number（必需）
            - intermediary_bank_city（必需）
            - intermediary_bank_state（必需）
            - intermediary_bank_country（必需）
            
            === Intermediary Bank2条件必需字段（第二组）===
            如果提供了任何intermediary bank2字段，则以下字段必需：
            - intermediary_bank2_institution（必需）
            - intermediary_bank2_routing_number 或 intermediary_bank2_swift_code（至少一个）
            - intermediary_bank2_city（必需）
            - intermediary_bank2_state（必需）
            - intermediary_bank2_country（必需）
            
            === 其他可选字段 ===
            address2, phone_number, assign_account_ids等
            
        Returns:
            requests.Response: 响应对象
            
        Note:
            ⚠️ 文档问题：
            1. 条件必需字段规则极其复杂
            2. "if any value is provided"触发逻辑不明确
            3. 响应无code包装层
            4. 40+个字段未在Properties定义
            5. intermediary_bank2_swift_code条件说明可能错误
            
            ⚠️ 测试建议：
            由于参数极其复杂，大部分测试场景skip
            只测试基础Wire类型和错误处理
        """
        url = self.config.get_full_url("/money-movements/wire/counterparties")
        
        payload = {
            "name": name,
            "type": str(type) if isinstance(type, CounterpartyType) else type,
            "bank_account_type": str(bank_account_type) if isinstance(bank_account_type, BankAccountType) else bank_account_type,
            "bank_account_owner_name": bank_account_owner_name,
            "bank_account_number": bank_account_number
        }
        
        if payment_type is not None:
            payload["payment_type"] = str(payment_type) if isinstance(payment_type, WirePaymentType) else payment_type
        if bank_routing_number is not None:
            payload["bank_routing_number"] = bank_routing_number
        if country is not None:
            payload["country"] = country
        if address1 is not None:
            payload["address1"] = address1
        if address2 is not None:
            payload["address2"] = address2
        if city is not None:
            payload["city"] = city
        if state is not None:
            payload["state"] = state
        if zip_code is not None:
            payload["zip_code"] = zip_code
        if bank_country is not None:
            payload["bank_country"] = bank_country
        if swift_code is not None:
            payload["swift_code"] = swift_code
        if bank_name is not None:
            payload["bank_name"] = bank_name
        if bank_address is not None:
            payload["bank_address"] = bank_address
        if bank_city is not None:
            payload["bank_city"] = bank_city
        if bank_state is not None:
            payload["bank_state"] = bank_state
        if bank_zip_code is not None:
            payload["bank_zip_code"] = bank_zip_code
        if phone_number is not None:
            payload["phone_number"] = phone_number
        
        # Intermediary Bank第一组
        if intermediary_financial_institution is not None:
            payload["intermediary_financial_institution"] = intermediary_financial_institution
        if intermediary_bank_routing_number is not None:
            payload["intermediary_bank_routing_number"] = intermediary_bank_routing_number
        if intermediary_bank_address1 is not None:
            payload["intermediary_bank_address1"] = intermediary_bank_address1
        if intermediary_bank_address2 is not None:
            payload["intermediary_bank_address2"] = intermediary_bank_address2
        if intermediary_bank_city is not None:
            payload["intermediary_bank_city"] = intermediary_bank_city
        if intermediary_bank_state is not None:
            payload["intermediary_bank_state"] = intermediary_bank_state
        if intermediary_bank_zip_code is not None:
            payload["intermediary_bank_zip_code"] = intermediary_bank_zip_code
        if intermediary_bank_country is not None:
            payload["intermediary_bank_country"] = intermediary_bank_country
        
        # Intermediary Bank2第二组
        if intermediary_bank2_institution is not None:
            payload["intermediary_bank2_institution"] = intermediary_bank2_institution
        if intermediary_bank2_routing_number is not None:
            payload["intermediary_bank2_routing_number"] = intermediary_bank2_routing_number
        if intermediary_bank2_swift_code is not None:
            payload["intermediary_bank2_swift_code"] = intermediary_bank2_swift_code
        if intermediary_bank2_address1 is not None:
            payload["intermediary_bank2_address1"] = intermediary_bank2_address1
        if intermediary_bank2_address2 is not None:
            payload["intermediary_bank2_address2"] = intermediary_bank2_address2
        if intermediary_bank2_city is not None:
            payload["intermediary_bank2_city"] = intermediary_bank2_city
        if intermediary_bank2_state is not None:
            payload["intermediary_bank2_state"] = intermediary_bank2_state
        if intermediary_bank2_zip_code is not None:
            payload["intermediary_bank2_zip_code"] = intermediary_bank2_zip_code
        if intermediary_bank2_country is not None:
            payload["intermediary_bank2_country"] = intermediary_bank2_country
        
        if assign_account_ids is not None:
            payload["assign_account_ids"] = assign_account_ids
        
        payload.update(kwargs)
        logger.debug(f"创建Wire对手方: name={name}, type={type}, payment_type={payment_type}")
        
        response = self.session.post(url, json=payload)
        logger.debug(f"响应状态: {response.status_code}")
        
        return response

    # ==================== 转账接口 ====================
    
    def initiate_wire_payment(
        self,
        amount: str,
        financial_account_id: str,
        counterparty_id: str,
        memo: Optional[str] = None,
        sub_account_id: Optional[str] = None,
        schedule_date: Optional[str] = None,
        **kwargs
    ) -> requests.Response:
        """
        发起国内电汇
        
        Args:
            amount: 转账金额（必需）
            financial_account_id: Financial Account ID（必需）
            counterparty_id: 对手方ID（必需）
            memo: 备注（最多210字符）
            sub_account_id: Sub Account ID（条件必需）
            schedule_date: 计划日期（YYYY-MM-DD，今天或未来）
            
        Returns:
            requests.Response: 响应对象
            
        Note:
            ⚠️⚠️⚠️ 真实转账操作，会实际扣款，不可撤销
            
            ⚠️ 文档问题：
            1. URL路径示例错误（缺少/money-movements）
            2. Content-Type矛盾（说text/plain但用JSON）
            3. 响应无code包装层
        """
        url = self.config.get_full_url("/money-movements/wire/payment")
        
        payload = {
            "amount": amount,
            "financial_account_id": financial_account_id,
            "counterparty_id": counterparty_id
        }
        
        if memo is not None:
            payload["memo"] = memo
        if sub_account_id is not None:
            payload["sub_account_id"] = sub_account_id
        if schedule_date is not None:
            payload["schedule_date"] = schedule_date
        
        payload.update(kwargs)
        logger.warning(f"⚠️⚠️⚠️ 发起国内电汇: {amount} from {financial_account_id} to counterparty {counterparty_id}")
        logger.warning("这是真实转账操作，会实际扣款，不可撤销！")
        
        response = self.session.post(url, json=payload)
        logger.debug(f"响应状态: {response.status_code}")
        
        return response

    def initiate_international_wire_payment(
        self,
        amount: str,
        financial_account_id: str,
        counterparty_id: str,
        memo: Optional[str] = None,
        sub_account_id: Optional[str] = None,
        schedule_date: Optional[str] = None,
        **kwargs
    ) -> requests.Response:
        """
        发起国际电汇
        
        Args:
            amount: 转账金额（必需）
            financial_account_id: Financial Account ID（必需）
            counterparty_id: 对手方ID（必需）
            memo: 备注（最多210字符）
            sub_account_id: Sub Account ID（条件必需）
            schedule_date: 计划日期（YYYY-MM-DD）
            
        Returns:
            requests.Response: 响应对象
            
        Note:
            ⚠️⚠️⚠️ 真实转账操作，会实际扣款，不可撤销
            
            ⚠️ 文档问题：
            1. URL路径示例错误（缺少/money-movements）
            2. 接口与Wire Payment完全重复，为何分两个接口？
            3. 响应无code包装层
        """
        url = self.config.get_full_url("/money-movements/international-wire/payment")
        
        payload = {
            "amount": amount,
            "financial_account_id": financial_account_id,
            "counterparty_id": counterparty_id
        }
        
        if memo is not None:
            payload["memo"] = memo
        if sub_account_id is not None:
            payload["sub_account_id"] = sub_account_id
        if schedule_date is not None:
            payload["schedule_date"] = schedule_date
        
        payload.update(kwargs)
        logger.warning(f"⚠️⚠️⚠️ 发起国际电汇: {amount} from {financial_account_id} to counterparty {counterparty_id}")
        logger.warning("这是真实转账操作，会实际扣款，不可撤销！")
        
        response = self.session.post(url, json=payload)
        logger.debug(f"响应状态: {response.status_code}")
        
        return response

    def request_wire_payment(
        self,
        amount: str,
        financial_account_id: str,
        counterparty_id: str,
        memo: Optional[str] = None,
        sub_account_id: Optional[str] = None,
        **kwargs
    ) -> requests.Response:
        """
        发起电汇收款请求
        
        Args:
            amount: 收款金额（必需）
            financial_account_id: 收款Financial Account ID（必需）
            counterparty_id: 付款方对手方ID（必需）
            memo: 备注（最多140字符，注意：比Wire Payment短）
            sub_account_id: Sub Account ID（条件必需）
            
        Returns:
            requests.Response: 响应对象
            
        Note:
            ⚠️ 重要：这是请求收款（pull），不是发送（push）
            UniFi会向对方银行发起拉款请求
            
            ⚠️ 文档问题：
            1. 功能描述不清（与Instant Pay关系？）
            2. 响应无code包装层
            3. 响应有record_owner字段（未定义）
        """
        url = self.config.get_full_url("/money-movements/wire/request-payment")
        
        payload = {
            "amount": amount,
            "financial_account_id": financial_account_id,
            "counterparty_id": counterparty_id
        }
        
        if memo is not None:
            payload["memo"] = memo
        if sub_account_id is not None:
            payload["sub_account_id"] = sub_account_id
        
        payload.update(kwargs)
        logger.warning(f"⚠️ 发起电汇收款请求: {amount} to {financial_account_id} from counterparty {counterparty_id}")
        
        response = self.session.post(url, json=payload)
        logger.debug(f"响应状态: {response.status_code}")
        
        return response

    # ==================== 费用接口 ====================
    
    def quote_transaction_fee(
        self,
        financial_account_id: str,
        amount: str,
        payment_type: Optional[Union[str, WirePaymentType]] = None,
        same_day: bool = False,
        **kwargs
    ) -> requests.Response:
        """
        计算电汇交易费用
        
        Args:
            financial_account_id: Financial Account ID（必需）
            amount: 交易金额（必需）
            payment_type: 支付类型（默认Wire）
            same_day: 是否当天处理（默认false，可能影响费用）
            
        Returns:
            requests.Response: 响应对象，包含：
                - code: 业务状态码
                - data: 费用信息
                    - fee: 费用金额
                    - same_day: 是否当天
                    
        Note:
            ⚠️ 文档问题：HTTP方法示例错误（POST写成GET）
        """
        url = self.config.get_full_url("/money-movements/wire/fee")
        
        payload = {
            "financial_account_id": financial_account_id,
            "amount": amount,
            "same_day": same_day
        }
        
        if payment_type is not None:
            payload["payment_type"] = str(payment_type) if isinstance(payment_type, WirePaymentType) else payment_type
        
        payload.update(kwargs)
        logger.debug(f"计算Wire费用: amount={amount}, payment_type={payment_type}")
        
        response = self.session.post(url, json=payload)
        logger.debug(f"响应状态: {response.status_code}")
        
        return response

    # ==================== 辅助方法 ====================
    
    def parse_list_response(self, response: requests.Response) -> dict:
        """
        解析列表响应（兼容无code包装层）
        """
        if response.status_code != 200:
            return {"error": True, "status_code": response.status_code}
        
        try:
            data = response.json()
            if isinstance(data, dict) and "content" in data:
                return {
                    "error": False,
                    "content": data.get("content", []),
                    "pageable": data.get("pageable", {}),
                    "total_elements": data.get("total_elements", 0),
                    "no_code_wrapper": True
                }
            elif isinstance(data, dict) and "code" in data:
                if data["code"] != 200:
                    return {"error": True, "code": data["code"]}
                content_data = data.get("data", {})
                return {
                    "error": False,
                    "content": content_data.get("content", []),
                    "pageable": content_data.get("pageable", {})
                }
        except Exception as e:
            logger.error(f"解析响应失败: {e}", exc_info=True)
            return {"error": True, "message": str(e)}
