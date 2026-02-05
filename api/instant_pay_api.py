"""
Instant Pay 相关 API 封装
提供实时支付和结算服务（Federal Reserve FedNow）
遵循 API Object 模式，提供灵活的参数化接口

⚠️ 文档问题（45个）：
1. 响应格式不一致（7个接口无code包装层）
2. Cancel/Reject/Return概念混淆
3. payment-request vs request-payment URL不一致
4. cancel_code/return_code/reject_code外部链接缺失
5. 大量响应字段未在Properties定义
6. Request Payment专有字段完全未定义

⚠️ 重要提醒：
- 所有payment和request-payment操作会真实扣款/收款
- 20秒超时限制（Payment Timeout Clock）
- Cancel/Return/Reject操作需要特定的code（值未知）
"""
import requests
from typing import Optional, Union, List
from config.config import config
from data.enums import (
    PaymentTransactionStatus,
    PaymentTransactionType,
    RequestPaymentStatus,
    CounterpartyType,
    BankAccountType,
    AccountSubType,
    WireDirection
)
from utils.logger import logger


class InstantPayAPI:
    """
    Instant Pay API 封装类
    提供FedNow实时支付服务（24/7, 秒级结算）
    
    ⚠️ 重要：
    - Payment Timeout Clock：20秒内必须完成或失败
    - 所有payment操作会真实扣款
    - Request Payment功能支持收款请求
    """
    def __init__(self, session: Optional[requests.Session] = None):
        """
        初始化 InstantPayAPI
        
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
        获取Instant Pay交易列表
        
        Args:
            transaction_id: 交易ID
            financial_account_id: Financial Account ID
            counterparty_id: 对手方ID
            start_date: 开始日期（UTC，YYYY-MM-DD）
            end_date: 结束日期（UTC，YYYY-MM-DD）
            status: 交易状态
            transaction_type: 交易类型（Credit或Debit）
            page: 页码
            size: 每页大小
            
        Returns:
            requests.Response: 响应对象
            
        Note:
            ⚠️ 文档问题：
            1. 响应无code包装层
            2. 响应中有14+个字段未在Properties定义
        """
        url = self.config.get_full_url("/money-movements/instant-pay/transactions")
        params = {"page": page, "size": size}
        
        if transaction_id is not None:
            params["transaction_id"] = transaction_id
        if financial_account_id is not None:
            params["financial_account_id"] = financial_account_id
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
        logger.debug(f"请求Instant Pay交易列表: {params}")
        
        response = self.session.get(url, params=params)
        logger.debug(f"响应状态: {response.status_code}")
        
        return response

    def list_request_payment_transactions(
        self,
        financial_account_id: Optional[str] = None,
        counterparty_id: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        status: Optional[Union[str, RequestPaymentStatus]] = None,
        direction: Optional[Union[str, WireDirection]] = None,
        page: int = 0,
        size: int = 10,
        **kwargs
    ) -> requests.Response:
        """
        获取Instant Pay请求付款列表
        
        Args:
            financial_account_id: Financial Account ID
            counterparty_id: 对手方ID
            start_date: 开始日期
            end_date: 结束日期
            status: 请求付款状态（Pending/Paid_In_Full等）
            direction: 方向（Origination/Incoming）
            page: 页码
            size: 每页大小
            
        Returns:
            requests.Response: 响应对象
            
        Note:
            ⚠️ 重要：
            1. 此接口有code包装层（与List Transactions不同）
            2. status枚举值完全不同（Paid_In_Full等）
        """
        url = self.config.get_full_url("/money-movements/instant-pay/request-payment/transactions")
        params = {"page": page, "size": size}
        
        if financial_account_id is not None:
            params["financial_account_id"] = financial_account_id
        if counterparty_id is not None:
            params["counterparty_id"] = counterparty_id
        if start_date is not None:
            params["start_date"] = start_date
        if end_date is not None:
            params["end_date"] = end_date
        if status is not None:
            params["status"] = str(status) if isinstance(status, RequestPaymentStatus) else status
        if direction is not None:
            params["direction"] = str(direction) if isinstance(direction, WireDirection) else direction
        
        params.update(kwargs)
        logger.debug(f"请求Request Payment列表: {params}")
        
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
        获取可用于Instant Pay的Financial Accounts列表
        
        Args:
            account_number: 账号
            name: 账户名称（模糊搜索）
            sub_type: 账户子类型
            account_ids: 账户ID数组
            page: 页码
            size: 每页大小
            
        Returns:
            requests.Response: 响应对象
            
        Note:
            ⚠️ 文档问题：响应无code包装层
        """
        url = self.config.get_full_url("/money-movements/instant-pay/financial-accounts")
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
        logger.debug(f"请求Instant Pay可用账户列表: {params}")
        
        response = self.session.get(url, params=params)
        logger.debug(f"响应状态: {response.status_code}")
        
        return response

    def list_counterparties(
        self,
        financial_account_id: Optional[str] = None,
        account_ids: Optional[Union[List[str], str]] = None,
        name: Optional[str] = None,
        bank_account_owner_name: Optional[str] = None,
        page: int = 0,
        size: int = 10,
        **kwargs
    ) -> requests.Response:
        """
        获取Instant Pay对手方列表
        
        Args:
            financial_account_id: Financial Account ID
            account_ids: 账户ID数组
            name: 对手方名称
            bank_account_owner_name: 银行账户所有人名称
            page: 页码
            size: 每页大小
            
        Returns:
            requests.Response: 响应对象
            
        Note:
            ⚠️ 文档问题：
            1. 响应无code包装层
            2. List说明逻辑混乱
        """
        url = self.config.get_full_url("/money-movements/instant-pay/counterparties")
        params = {"page": page, "size": size}
        
        if financial_account_id is not None:
            params["financial_account_id"] = financial_account_id
        if account_ids is not None:
            if isinstance(account_ids, list):
                params["account_ids"] = ",".join(account_ids)
            else:
                params["account_ids"] = account_ids
        if name is not None:
            params["name"] = name
        if bank_account_owner_name is not None:
            params["bank_account_owner_name"] = bank_account_owner_name
        
        params.update(kwargs)
        logger.debug(f"请求Instant Pay对手方列表: {params}")
        
        response = self.session.get(url, params=params)
        logger.debug(f"响应状态: {response.status_code}")
        
        return response

    # ==================== 对手方管理接口 ====================
    
    def create_counterparty(
        self,
        name: str,
        type: Union[str, CounterpartyType],
        bank_account_type: Union[str, BankAccountType],
        bank_routing_number: str,
        bank_name: str,
        bank_account_owner_name: str,
        bank_account_number: str,
        assign_account_ids: Optional[List[str]] = None,
        **kwargs
    ) -> requests.Response:
        """
        创建Instant Pay对手方
        
        Args:
            name: 对手方名称（必需）
            type: 对手方类型（必需）
            bank_account_type: 银行账户类型（必需）
            bank_routing_number: 路由号（必需）
            bank_name: 银行名称（必需）
            bank_account_owner_name: 账户所有人姓名（必需）
            bank_account_number: 银行账号（必需）
            assign_account_ids: 分配的账户ID列表
            
        Returns:
            requests.Response: 响应对象
            
        Note:
            ⚠️ 文档问题：响应无code包装层
        """
        url = self.config.get_full_url("/money-movements/instant-pay/counterparties")
        
        payload = {
            "name": name,
            "type": str(type) if isinstance(type, CounterpartyType) else type,
            "bank_account_type": str(bank_account_type) if isinstance(bank_account_type, BankAccountType) else bank_account_type,
            "bank_routing_number": bank_routing_number,
            "bank_name": bank_name,
            "bank_account_owner_name": bank_account_owner_name,
            "bank_account_number": bank_account_number
        }
        
        if assign_account_ids is not None:
            payload["assign_account_ids"] = assign_account_ids
        
        payload.update(kwargs)
        logger.debug(f"创建Instant Pay对手方: name={name}, type={type}")
        
        response = self.session.post(url, json=payload)
        logger.debug(f"响应状态: {response.status_code}")
        
        return response

    # ==================== 支付接口 ====================
    
    def initiate_payment(
        self,
        amount: str,
        financial_account_id: str,
        counterparty_id: str,
        sub_account_id: Optional[str] = None,
        memo: Optional[str] = None,
        link: Optional[str] = None,
        structured_content: Optional[str] = None,
        **kwargs
    ) -> requests.Response:
        """
        发起Instant Pay支付
        
        Args:
            amount: 转账金额（必需）
            financial_account_id: Financial Account ID（必需）
            counterparty_id: 对手方ID（必需）
            sub_account_id: Sub Account ID（条件必需）
            memo: 备注（最多80字符）
            link: 请求链接
            structured_content: 结构化内容（XML格式，用途不明）
            
        Returns:
            requests.Response: 响应对象
            
        Note:
            ⚠️⚠️⚠️ 真实支付操作，会实际扣款，不可撤销
            ⚠️ 20秒超时：必须在20秒内完成或失败
            
            ⚠️ 文档问题：
            1. URL路径示例错误（缺少/money-movements）
            2. 响应无code包装层
            3. structured_content说明不清
        """
        url = self.config.get_full_url("/money-movements/instant-pay/payment")
        
        payload = {
            "amount": amount,
            "financial_account_id": financial_account_id,
            "counterparty_id": counterparty_id
        }
        
        if sub_account_id is not None:
            payload["sub_account_id"] = sub_account_id
        if memo is not None:
            payload["memo"] = memo
        if link is not None:
            payload["link"] = link
        if structured_content is not None:
            payload["structured_content"] = structured_content
        
        payload.update(kwargs)
        logger.warning(f"⚠️⚠️⚠️ 发起Instant Pay: {amount} from {financial_account_id} to {counterparty_id}")
        logger.warning("真实支付操作！20秒超时限制！不可撤销！")
        
        response = self.session.post(url, json=payload)
        logger.debug(f"响应状态: {response.status_code}")
        
        return response

    def initiate_request_payment(
        self,
        amount: str,
        financial_account_id: str,
        counterparty_id: str,
        sub_account_id: Optional[str] = None,
        memo: Optional[str] = None,
        amount_modification_allowed: bool = False,
        early_payment_allowed: bool = False,
        execution_date: Optional[str] = None,
        expiration_date: Optional[str] = None,
        **kwargs
    ) -> requests.Response:
        """
        发起Instant Pay收款请求（RFP - Request For Payment）
        
        Args:
            amount: 收款金额（必需）
            financial_account_id: 收款Financial Account ID（必需）
            counterparty_id: 付款方对手方ID（必需）
            sub_account_id: Sub Account ID（条件必需）
            memo: 备注（最多80字符）
            amount_modification_allowed: 是否允许付款方修改金额（默认false）
            early_payment_allowed: 是否允许提前支付（默认false）
            execution_date: 执行日期（默认当天，YYYY-MM-DD）
            expiration_date: 过期日期（默认1年后，YYYY-MM-DD）
            
        Returns:
            requests.Response: 响应对象
            
        Note:
            ⚠️ 这是请求收款（pull），不是发送（push）
            
            ⚠️ 文档问题：
            1. 响应无code包装层
            2. amount_modification_allowed逻辑未详细说明
            3. early_payment_allowed的"early"定义不明
        """
        url = self.config.get_full_url("/money-movements/instant-pay/request-payment")
        
        payload = {
            "amount": amount,
            "financial_account_id": financial_account_id,
            "counterparty_id": counterparty_id,
            "amount_modification_allowed": amount_modification_allowed,
            "early_payment_allowed": early_payment_allowed
        }
        
        if sub_account_id is not None:
            payload["sub_account_id"] = sub_account_id
        if memo is not None:
            payload["memo"] = memo
        if execution_date is not None:
            payload["execution_date"] = execution_date
        if expiration_date is not None:
            payload["expiration_date"] = expiration_date
        
        payload.update(kwargs)
        logger.warning(f"⚠️ 发起Instant Pay收款请求: {amount} to {financial_account_id} from {counterparty_id}")
        
        response = self.session.post(url, json=payload)
        logger.debug(f"响应状态: {response.status_code}")
        
        return response

    # ==================== Request Payment操作接口 ====================
    
    def cancel_request_payment(
        self,
        rfp_id: str,
        cancel_code: str,
        cancel_reason: Optional[str] = None
    ) -> requests.Response:
        """
        取消请求付款
        
        Args:
            rfp_id: Request For Payment ID（必需）
            cancel_code: 取消原因代码（必需，值未知）
            cancel_reason: 取消原因描述
            
        Returns:
            requests.Response: 响应对象
            
        Note:
            ⚠️ 文档问题：
            1. cancel_code的可能值未知（外部链接缺失）
            2. 示例只有AC03，不知道还有哪些
        """
        url = self.config.get_full_url(f"/money-movements/instant-pay/request-payment/cancel/{rfp_id}")
        
        payload = {"cancel_code": cancel_code}
        
        if cancel_reason is not None:
            payload["cancel_reason"] = cancel_reason
        
        logger.debug(f"取消Request Payment: id={rfp_id}, code={cancel_code}")
        
        response = self.session.post(url, json=payload)
        logger.debug(f"响应状态: {response.status_code}")
        
        return response

    def approve_payment_request(
        self,
        rfp_id: str,
        sub_account_id: Optional[str] = None,
        memo: Optional[str] = None
    ) -> requests.Response:
        """
        批准收到的付款请求
        
        Args:
            rfp_id: Request For Payment ID（必需）
            sub_account_id: Sub Account ID（条件必需）
            memo: 备注
            
        Returns:
            requests.Response: 响应对象
            
        Note:
            ⚠️ 批准后会实际付款
        """
        url = self.config.get_full_url(f"/money-movements/instant-pay/payment-request/approve/{rfp_id}")
        
        payload = {}
        
        if sub_account_id is not None:
            payload["sub_account_id"] = sub_account_id
        if memo is not None:
            payload["memo"] = memo
        
        logger.warning(f"⚠️ 批准付款请求: id={rfp_id}（会实际付款）")
        
        response = self.session.post(url, json=payload)
        logger.debug(f"响应状态: {response.status_code}")
        
        return response

    def reject_payment_request(
        self,
        rfp_id: str,
        reject_code: str,
        reject_reason: Optional[str] = None
    ) -> requests.Response:
        """
        拒绝收到的付款请求
        
        Args:
            rfp_id: Request For Payment ID（必需）
            reject_code: 拒绝原因代码（必需，值未知）
            reject_reason: 拒绝原因描述
            
        Returns:
            requests.Response: 响应对象
            
        Note:
            ⚠️ 文档问题：reject_code可能值未知（外部链接缺失）
        """
        url = self.config.get_full_url(f"/money-movements/instant-pay/payment-request/reject/{rfp_id}")
        
        payload = {"reject_code": reject_code}
        
        if reject_reason is not None:
            payload["reject_reason"] = reject_reason
        
        logger.debug(f"拒绝付款请求: id={rfp_id}, code={reject_code}")
        
        response = self.session.post(url, json=payload)
        logger.debug(f"响应状态: {response.status_code}")
        
        return response

    # ==================== Return相关接口 ====================
    
    def return_payment(
        self,
        transaction_id: str,
        return_code: str,
        return_reason: Optional[str] = None
    ) -> requests.Response:
        """
        退款支付
        
        Args:
            transaction_id: 交易ID（必需）
            return_code: 退款原因代码（必需，值未知）
            return_reason: 退款原因描述
            
        Returns:
            requests.Response: 响应对象
            
        Note:
            ⚠️ 重要：交易必须已结算才能退款
            ⚠️ 文档问题：return_code可能值未知
        """
        url = self.config.get_full_url(f"/money-movements/instant-pay/return-payment/{transaction_id}")
        
        payload = {"return_code": return_code}
        
        if return_reason is not None:
            payload["return_reason"] = return_reason
        
        logger.warning(f"⚠️ 退款支付: transaction={transaction_id}, code={return_code}")
        
        response = self.session.post(url, json=payload)
        logger.debug(f"响应状态: {response.status_code}")
        
        return response

    def return_request(
        self,
        transaction_id: str,
        return_code: str,
        return_reason: Optional[str] = None
    ) -> requests.Response:
        """
        退款请求
        
        Args:
            transaction_id: 交易ID（必需）
            return_code: 退款原因代码（必需）
            return_reason: 退款原因描述
            
        Returns:
            requests.Response: 响应对象
            
        Note:
            ⚠️ 文档问题：
            1. Return Payment vs Return Request的区别未说明
            2. return_code可能值未知
        """
        url = self.config.get_full_url(f"/money-movements/instant-pay/return-request/{transaction_id}")
        
        payload = {"return_code": return_code}
        
        if return_reason is not None:
            payload["return_reason"] = return_reason
        
        logger.debug(f"退款请求: transaction={transaction_id}, code={return_code}")
        
        response = self.session.post(url, json=payload)
        logger.debug(f"响应状态: {response.status_code}")
        
        return response

    def approve_return_request(self, return_request_id: str) -> requests.Response:
        """
        批准退款请求
        
        Args:
            return_request_id: Return Request ID（必需）
            
        Returns:
            requests.Response: 响应对象
            
        Note:
            ⚠️ 批准后会实际退款
            ⚠️ 文档问题：无请求体参数
        """
        url = self.config.get_full_url(f"/money-movements/instant-pay/return-request/approve/{return_request_id}")
        
        logger.warning(f"⚠️ 批准退款请求: id={return_request_id}（会实际退款）")
        
        response = self.session.post(url)
        logger.debug(f"响应状态: {response.status_code}")
        
        return response

    def reject_return_request(
        self,
        return_request_id: str,
        reject_code: str,
        reject_reason: Optional[str] = None
    ) -> requests.Response:
        """
        拒绝退款请求
        
        Args:
            return_request_id: Return Request ID（必需）
            reject_code: 拒绝原因代码（必需）
            reject_reason: 拒绝原因描述
            
        Returns:
            requests.Response: 响应对象
            
        Note:
            ⚠️ 文档问题：
            1. URL示例完全错误（/payment-request应为/return-request）
            2. reject_code可能值未知
        """
        url = self.config.get_full_url(f"/money-movements/instant-pay/return-request/reject/{return_request_id}")
        
        payload = {"reject_code": reject_code}
        
        if reject_reason is not None:
            payload["reject_reason"] = reject_reason
        
        logger.debug(f"拒绝退款请求: id={return_request_id}, code={reject_code}")
        
        response = self.session.post(url, json=payload)
        logger.debug(f"响应状态: {response.status_code}")
        
        return response

    # ==================== 费用接口 ====================
    
    def quote_transaction_fee(
        self,
        financial_account_id: str,
        amount: str,
        same_day: bool = False,
        **kwargs
    ) -> requests.Response:
        """
        计算Instant Pay交易费用
        
        Args:
            financial_account_id: Financial Account ID（必需）
            amount: 交易金额（必需）
            same_day: 是否当天处理（默认false）
            
        Returns:
            requests.Response: 响应对象
            
        Note:
            ⚠️ 文档问题：HTTP方法示例错误（POST写成GET）
        """
        url = self.config.get_full_url("/money-movements/instant-pay/fee")
        
        payload = {
            "financial_account_id": financial_account_id,
            "amount": amount,
            "same_day": same_day
        }
        
        payload.update(kwargs)
        logger.debug(f"计算Instant Pay费用: amount={amount}")
        
        response = self.session.post(url, json=payload)
        logger.debug(f"响应状态: {response.status_code}")
        
        return response

    # ==================== 辅助方法 ====================
    
    def parse_list_response(self, response: requests.Response, has_code_wrapper: bool = False) -> dict:
        """
        解析列表响应
        兼容有无code包装层两种格式
        
        Args:
            response: requests.Response 对象
            has_code_wrapper: 是否有code包装层（List Request Payment有，其他没有）
            
        Returns:
            dict: 包含 error, content, pageable 等字段
        """
        if response.status_code != 200:
            return {"error": True, "status_code": response.status_code}
        
        try:
            data = response.json()
            
            # 格式1：有code包装层（List Request Payment）
            if has_code_wrapper and "code" in data:
                if data["code"] != 200:
                    return {"error": True, "code": data["code"]}
                content_data = data.get("data", {})
                return {
                    "error": False,
                    "content": content_data.get("content", []),
                    "pageable": content_data.get("pageable", {}),
                    "total_elements": content_data.get("total_elements", 0)
                }
            # 格式2：无code包装层（其他List接口）
            elif "content" in data:
                return {
                    "error": False,
                    "content": data.get("content", []),
                    "pageable": data.get("pageable", {}),
                    "total_elements": data.get("total_elements", 0),
                    "no_code_wrapper": True
                }
        except Exception as e:
            logger.error(f"解析失败: {e}", exc_info=True)
            return {"error": True, "message": str(e)}
