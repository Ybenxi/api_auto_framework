"""
ACH Processing 相关 API 封装
提供ACH（自动清算所）转账功能，支持Credit和Debit
遵循 API Object 模式，提供灵活的参数化接口

⚠️ 关键业务逻辑：
first_party字段决定counterparty_id的来源：
1. first_party=true（第一方转账）：
   - counterparty_id填Bank Account的id（从list_bank_accounts获取）
   - 用于自己的不同银行账户间转账
   - UniFi会验证银行所有人信息
   
2. first_party=false（第三方转账）：
   - counterparty_id填ACH Counterparty的id（从list_counterparties获取）
   - 用于给其他人/公司转账
   - 使用已创建的counterparty

⚠️ 文档问题（45个）：
1. 响应格式不一致（7个接口无code包装层）
2. same_day截止时间不一致（3:00PM CT vs 3:45PM ET）
3. Batch File响应结构极其复杂（50+嵌套字段）且未定义
4. first_party概念说明不清
5. request_reason外部链接缺失

⚠️ 重要提醒：
- 所有Credit/Debit操作会真实扣款，不可撤销
- Same Day ACH有严格的截止时间（4个时间窗口）
- Reversal只能对已结算的交易操作
"""
import requests
from typing import Optional, Union, List
from config.config import config
from data.enums import (
    PaymentTransactionStatus,
    PaymentTransactionType,
    CounterpartyType,
    BankAccountType,
    AccountSubType
)
from utils.logger import logger


class ACHProcessingAPI:
    """
    ACH Processing API 封装类
    提供ACH转账的完整功能
    
    核心特性：
    - Credit（付款）和Debit（收款）
    - First Party（第一方）和Third Party（第三方）
    - Same Day ACH（当天处理）
    - Reversal（冲正/撤销）
    - Batch File Upload（批量上传）
    """
    def __init__(self, session: Optional[requests.Session] = None):
        """
        初始化 ACHProcessingAPI
        
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
        sub_account_id: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        transaction_type: Optional[Union[str, PaymentTransactionType]] = None,
        status: Optional[Union[str, PaymentTransactionStatus]] = None,
        page: int = 0,
        size: int = 10,
        **kwargs
    ) -> requests.Response:
        """
        获取ACH交易列表
        
        Args:
            transaction_id: 交易ID
            financial_account_id: Financial Account ID
            counterparty_id: 对手方ID（注意：可能是bank info id或counterparty id）
            sub_account_id: Sub Account ID
            start_date: 开始日期（UTC，YYYY-MM-DD）
            end_date: 结束日期（UTC，YYYY-MM-DD）
            transaction_type: 交易类型（Credit或Debit）
            status: 交易状态
            page: 页码
            size: 每页大小
            
        Returns:
            requests.Response: 响应对象
            
        Note:
            ⚠️ 文档问题：
            1. 响应无code包装层
            2. 响应中有13+个字段未在Properties定义
        """
        url = self.config.get_full_url("/money-movements/ach/transactions")
        params = {"page": page, "size": size}
        
        if transaction_id is not None:
            params["transaction_id"] = transaction_id
        if financial_account_id is not None:
            params["financial_account_id"] = financial_account_id
        if counterparty_id is not None:
            params["counterparty_id"] = counterparty_id
        if sub_account_id is not None:
            params["sub_account_id"] = sub_account_id
        if start_date is not None:
            params["start_date"] = start_date
        if end_date is not None:
            params["end_date"] = end_date
        if transaction_type is not None:
            params["transaction_type"] = str(transaction_type) if isinstance(transaction_type, PaymentTransactionType) else transaction_type
        if status is not None:
            params["status"] = str(status) if isinstance(status, PaymentTransactionStatus) else status
        
        params.update(kwargs)
        logger.debug(f"请求ACH交易列表: {params}")
        
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
        获取可用于ACH的Financial Accounts列表
        
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
        url = self.config.get_full_url("/money-movements/ach/financial-accounts")
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
        logger.debug(f"请求ACH可用账户列表: {params}")
        
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
        获取ACH对手方列表（第三方）
        
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
            ⚠️ 重要：这里返回的是第三方counterparty
            用于first_party=false的场景
            
            ⚠️ 文档问题：响应无code包装层
        """
        url = self.config.get_full_url("/money-movements/ach/counterparties")
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
        logger.debug(f"请求ACH对手方列表: {params}")
        
        response = self.session.get(url, params=params)
        logger.debug(f"响应状态: {response.status_code}")
        
        return response

    def list_bank_accounts(
        self,
        financial_account_id: Optional[str] = None,
        account_ids: Optional[str] = None,
        page: int = 0,
        size: int = 10,
        **kwargs
    ) -> requests.Response:
        """
        获取第一方银行账户列表（First Party）
        
        Args:
            financial_account_id: Financial Account ID
            account_ids: 账户ID（注意：此接口是string不是array）
            page: 页码
            size: 每页大小
            
        Returns:
            requests.Response: 响应对象
            
        Note:
            ⚠️⚠️⚠️ 关键业务逻辑：
            这里返回的是第一方银行账户（First Party Bank Accounts）
            用于first_party=true的场景
            
            使用场景：
            - 自己的不同银行账户间转账
            - counterparty_id填这里返回的bank account id
            
            ⚠️ 文档问题：
            1. 响应所有字段未在Properties定义
            2. account_ids参数类型是string（其他接口是array）
        """
        url = self.config.get_full_url("/money-movements/ach/bank-accounts")
        params = {"page": page, "size": size}
        
        if financial_account_id is not None:
            params["financial_account_id"] = financial_account_id
        if account_ids is not None:
            params["account_ids"] = account_ids
        
        params.update(kwargs)
        logger.debug(f"请求ACH第一方银行账户列表: {params}")
        
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
        创建ACH对手方（第三方）
        
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
            ⚠️ 重要：这里创建的是第三方counterparty
            用于first_party=false的转账场景
            
            ⚠️ 文档问题：响应无code包装层
        """
        url = self.config.get_full_url("/money-movements/ach/counterparties")
        
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
        logger.debug(f"创建ACH对手方（第三方）: name={name}, type={type}")
        
        response = self.session.post(url, json=payload)
        logger.debug(f"响应状态: {response.status_code}")
        
        return response

    # ==================== 转账接口 ====================
    
    def initiate_credit(
        self,
        amount: str,
        financial_account_id: str,
        counterparty_id: str,
        first_party: bool = False,
        sub_account_id: Optional[str] = None,
        memo: Optional[str] = None,
        schedule_date: Optional[str] = None,
        same_day: bool = False,
        **kwargs
    ) -> requests.Response:
        """
        发起ACH Credit转账（付款）
        
        Args:
            amount: 转账金额（必需）
            financial_account_id: Financial Account ID（必需）
            counterparty_id: 对手方ID（必需，来源取决于first_party）
            first_party: 是否第一方转账（默认false）
            sub_account_id: Sub Account ID（条件必需）
            memo: 备注（最多80字符）
            schedule_date: 计划日期（YYYY-MM-DD，今天或未来）
            same_day: 是否当天处理（默认false）
            
        Returns:
            requests.Response: 响应对象
            
        Note:
            ⚠️⚠️⚠️ 真实转账操作，会实际扣款，不可撤销
            
            ⚠️⚠️⚠️ 关键业务逻辑：
            
            如果 first_party=true（第一方转账）：
            - counterparty_id应该填Bank Account的id
            - 从list_bank_accounts()接口获取
            - 用于自己的不同银行账户间转账
            - UniFi会验证银行所有人信息
            
            如果 first_party=false（第三方转账）：
            - counterparty_id应该填ACH Counterparty的id
            - 从list_counterparties()接口获取
            - 用于给其他人/公司转账
            
            ⚠️ Same Day ACH截止时间（UniFi Deadline）：
            - 9:45 AM ET - Same Day
            - 3:45 PM ET - Same Day
            - 6:45 PM ET - Next Day
            - 9:45 PM ET - Next Day
            
            ⚠️ 文档问题：
            1. 响应无code包装层
            2. same_day截止时间说明不一致
        """
        url = self.config.get_full_url("/money-movements/ach/credit")
        
        payload = {
            "amount": amount,
            "financial_account_id": financial_account_id,
            "counterparty_id": counterparty_id,
            "first_party": first_party,
            "same_day": same_day
        }
        
        if sub_account_id is not None:
            payload["sub_account_id"] = sub_account_id
        if memo is not None:
            payload["memo"] = memo
        if schedule_date is not None:
            payload["schedule_date"] = schedule_date
        
        payload.update(kwargs)
        
        party_type = "第一方（First Party）" if first_party else "第三方（Third Party）"
        logger.warning(f"⚠️⚠️⚠️ 发起ACH Credit: {amount} from {financial_account_id}")
        logger.warning(f"转账类型: {party_type}")
        logger.warning(f"Same Day: {same_day}")
        logger.warning("这是真实转账操作，会实际扣款，不可撤销！")
        
        response = self.session.post(url, json=payload)
        logger.debug(f"响应状态: {response.status_code}")
        
        return response

    def initiate_debit(
        self,
        amount: str,
        financial_account_id: str,
        counterparty_id: str,
        first_party: bool = False,
        sub_account_id: Optional[str] = None,
        memo: Optional[str] = None,
        schedule_date: Optional[str] = None,
        same_day: bool = False,
        **kwargs
    ) -> requests.Response:
        """
        发起ACH Debit转账（收款/拉款）
        
        Args:
            amount: 收款金额（必需）
            financial_account_id: 收款Financial Account ID（必需）
            counterparty_id: 付款方ID（必需，来源取决于first_party）
            first_party: 是否第一方转账（默认false）
            sub_account_id: Sub Account ID（条件必需）
            memo: 备注（最多80字符）
            schedule_date: 计划日期（YYYY-MM-DD）
            same_day: 是否当天处理（默认false）
            
        Returns:
            requests.Response: 响应对象
            
        Note:
            ⚠️⚠️⚠️ 真实收款操作，会从对方账户拉款
            
            ⚠️⚠️⚠️ 关键业务逻辑：
            first_party字段决定counterparty_id来源（同Credit）
            
            如果 first_party=true：
            - counterparty_id = Bank Account的id
            - 从list_bank_accounts()获取
            
            如果 first_party=false：
            - counterparty_id = ACH Counterparty的id
            - 从list_counterparties()获取
            
            ⚠️ 文档问题：响应无code包装层
        """
        url = self.config.get_full_url("/money-movements/ach/debit")
        
        payload = {
            "amount": amount,
            "financial_account_id": financial_account_id,
            "counterparty_id": counterparty_id,
            "first_party": first_party,
            "same_day": same_day
        }
        
        if sub_account_id is not None:
            payload["sub_account_id"] = sub_account_id
        if memo is not None:
            payload["memo"] = memo
        if schedule_date is not None:
            payload["schedule_date"] = schedule_date
        
        payload.update(kwargs)
        
        party_type = "第一方（First Party）" if first_party else "第三方（Third Party）"
        logger.warning(f"⚠️⚠️⚠️ 发起ACH Debit: {amount} to {financial_account_id}")
        logger.warning(f"转账类型: {party_type}")
        logger.warning("这是真实收款操作，会从对方拉款，不可撤销！")
        
        response = self.session.post(url, json=payload)
        logger.debug(f"响应状态: {response.status_code}")
        
        return response

    # ==================== 交易操作接口 ====================
    
    def cancel_transaction(self, transaction_id: str) -> requests.Response:
        """
        取消ACH交易
        
        Args:
            transaction_id: 交易ID（必需）
            
        Returns:
            requests.Response: 响应对象
            
        Note:
            ⚠️ 重要限制：
            - 只能取消尚未发送到FRB的交易
            - 一旦发送到Federal Reserve Bank就不能取消
            - 取消时间窗口不明确
            
            ⚠️ 文档问题：限制说明不够清晰
        """
        url = self.config.get_full_url(f"/money-movements/ach/{transaction_id}/cancel")
        
        logger.warning(f"⚠️ 取消ACH交易: {transaction_id}")
        logger.warning("只能取消尚未发送到FRB的交易")
        
        response = self.session.post(url)
        logger.debug(f"响应状态: {response.status_code}")
        
        return response

    def initiate_reversal(
        self,
        transaction_id: str,
        request_reason: str,
        description: Optional[str] = None,
        reversal_file_path: Optional[str] = None
    ) -> requests.Response:
        """
        发起ACH冲正/撤销
        
        Args:
            transaction_id: 已结算的交易ID（必需）
            request_reason: 冲正原因（必需，值未知）
            description: 描述
            reversal_file_path: 附件文件路径
            
        Returns:
            requests.Response: 响应对象，包含：
                - code: 业务状态码
                - data:
                    - transaction_reversal_id: 冲正交易ID
                    - reversal_status: 冲正状态
                    
        Note:
            ⚠️ 重要限制：
            - 只能对已结算（settled）的交易操作
            - 有时间限制（文档未说明）
            
            ⚠️ 文档问题：
            1. request_reason可能值未知（外部链接缺失）
            2. reversal_file是否必需未说明
            3. 支持什么文件格式未说明
            4. Reversal时间限制未说明
        """
        url = self.config.get_full_url("/money-movements/ach/reversal")
        
        # 如果有文件，使用multipart
        if reversal_file_path:
            try:
                files = {'reversal_file': open(reversal_file_path, 'rb')}
                data = {
                    'transaction_id': transaction_id,
                    'request_reason': request_reason
                }
                if description:
                    data['description'] = description
                
                logger.warning(f"⚠️ 发起ACH Reversal（带文件）: transaction={transaction_id}")
                
                response = self.session.post(url, files=files, data=data)
            except FileNotFoundError:
                logger.error(f"文件不存在: {reversal_file_path}")
                raise
        else:
            payload = {
                "transaction_id": transaction_id,
                "request_reason": request_reason
            }
            if description:
                payload["description"] = description
            
            logger.warning(f"⚠️ 发起ACH Reversal: transaction={transaction_id}, reason={request_reason}")
            
            response = self.session.post(url, json=payload)
        
        logger.debug(f"响应状态: {response.status_code}")
        
        return response

    def get_reversal_detail(self, transaction_reversal_id: str) -> requests.Response:
        """
        获取冲正请求详情
        
        Args:
            transaction_reversal_id: 冲正交易ID（必需）
            
        Returns:
            requests.Response: 响应对象
            
        Note:
            ⚠️ 文档问题：
            1. JSON格式错误（缺少逗号）
            2. 响应包含原交易的完整信息（未说明）
        """
        url = self.config.get_full_url(f"/money-movements/ach/reversal/{transaction_reversal_id}/detail")
        
        logger.debug(f"请求ACH Reversal详情: {transaction_reversal_id}")
        
        response = self.session.get(url)
        logger.debug(f"响应状态: {response.status_code}")
        
        return response

    # ==================== 批量上传接口 ====================
    
    def upload_batch_file(self, file_path: str) -> requests.Response:
        """
        上传ACH批量文件
        
        Args:
            file_path: ACH批量文件路径
            
        Returns:
            requests.Response: 响应对象（极其复杂的嵌套结构）
            
        Note:
            ⚠️ 重要限制：
            - 每个文件最多500笔交易（性能考虑）
            - 文件格式：NACHA标准（推测）
            
            ⚠️⚠️⚠️ 文档问题严重：
            1. 文件格式未说明（NACHA? CSV?）
            2. 响应结构极其复杂（50+嵌套字段）
            3. 所有响应字段未在Properties定义
            4. error字段嵌套在4个不同位置
            5. 使用success_flag而不是code
            
            响应结构：
            - file_header（13个字段）
            - batch_list数组
              - batch_header（14个字段）
              - entry_detail_list数组（14个字段/每笔）
              - batch_control（10个字段）
            - file_controler（9个字段，拼写错误）
            
            ⚠️ 测试建议：
            由于文件格式和响应极其复杂，大部分测试skip
        """
        url = self.config.get_full_url("/money-movements/ach/batch-file")
        
        try:
            files = {'file': open(file_path, 'rb')}
            
            logger.warning(f"⚠️ 上传ACH批量文件: {file_path}")
            logger.warning("每个文件最多500笔交易")
            
            response = self.session.post(url, files=files)
            logger.debug(f"响应状态: {response.status_code}")
            
            return response
        except FileNotFoundError:
            logger.error(f"文件不存在: {file_path}")
            raise
        except Exception as e:
            logger.error(f"上传批量文件失败: {e}", exc_info=True)
            raise

    # ==================== 费用接口 ====================
    
    def quote_transaction_fee(
        self,
        financial_account_id: str,
        amount: str,
        transaction_type: Union[str, PaymentTransactionType],
        same_day: bool = False,
        first_party: bool = False,
        **kwargs
    ) -> requests.Response:
        """
        计算ACH交易费用
        
        Args:
            financial_account_id: Financial Account ID（必需）
            amount: 交易金额（必需）
            transaction_type: 交易类型（必需，Credit或Debit）
            same_day: 是否当天处理（默认false）
            first_party: 是否第一方转账（默认false）
            
        Returns:
            requests.Response: 响应对象
            
        Note:
            ⚠️ 费用影响因素：
            - transaction_type（Credit vs Debit）
            - same_day（当天处理可能费用更高）
            - first_party（第一方vs第三方可能费用不同）
            
            ⚠️ 文档问题：
            参数标记为required但有默认值（矛盾）
        """
        url = self.config.get_full_url("/money-movements/ach/fee")
        
        payload = {
            "financial_account_id": financial_account_id,
            "amount": amount,
            "transaction_type": str(transaction_type) if isinstance(transaction_type, PaymentTransactionType) else transaction_type,
            "same_day": same_day,
            "first_party": first_party
        }
        
        payload.update(kwargs)
        logger.debug(f"计算ACH费用: amount={amount}, type={transaction_type}, same_day={same_day}, first_party={first_party}")
        
        response = self.session.post(url, json=payload)
        logger.debug(f"响应状态: {response.status_code}")
        
        return response

    # ==================== 辅助方法 ====================
    
    def parse_list_response(self, response: requests.Response) -> dict:
        """解析列表响应（兼容无code包装层）"""
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
        except Exception as e:
            logger.error(f"解析失败: {e}", exc_info=True)
            return {"error": True, "message": str(e)}
