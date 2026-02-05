"""
Remote Deposit Check 相关 API 封装
提供远程支票存款功能：扫描、识别、存款
遵循 API Object 模式，提供灵活的参数化接口

⚠️ 文档问题（45个）：
1. HTTP方法错误（多处）
2. 响应格式不一致（7个接口无code包装层）
3. Scan响应使用success字段（独特格式）
4. Scan→Deposit流程说明不清晰
5. 大量响应字段未在Properties定义
6. Download应该用GET不是POST

⚠️ 重要提醒：
- Scan Check需要上传支票图片（multipart/form-data）
- Submit Deposit会真实入账，不可撤销
- 必须先Scan获取item_identifier，再Deposit
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


class RemoteDepositCheckAPI:
    """
    Remote Deposit Check API 封装类
    提供远程支票存款的完整流程
    
    流程：Scan → Submit Deposit → (可选)Update → Download
    """
    def __init__(self, session: Optional[requests.Session] = None):
        """
        初始化 RemoteDepositCheckAPI
        
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
        transaction_type: Optional[Union[str, PaymentTransactionType]] = None,
        status: Optional[Union[str, PaymentTransactionStatus]] = None,
        page: int = 0,
        size: int = 10,
        **kwargs
    ) -> requests.Response:
        """
        获取支票交易列表
        
        Args:
            transaction_id: 交易ID
            financial_account_id: Financial Account ID
            counterparty_id: 对手方ID
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
            2. 响应中有15+个字段未在Properties定义
        """
        url = self.config.get_full_url("/money-movements/checks/transactions")
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
        if transaction_type is not None:
            params["transaction_type"] = str(transaction_type) if isinstance(transaction_type, PaymentTransactionType) else transaction_type
        if status is not None:
            params["status"] = str(status) if isinstance(status, PaymentTransactionStatus) else status
        
        params.update(kwargs)
        logger.debug(f"请求Check交易列表: {params}")
        
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
        获取可用于支票存款的Financial Accounts列表
        
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
            ⚠️ 文档问题：
            1. 接口描述错误（说ACH应为Check）
            2. HTTP方法示例错误（GET写成POST）
            3. 响应无code包装层
        """
        url = self.config.get_full_url("/money-movements/checks/financial-accounts")
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
        logger.debug(f"请求Check可用账户列表: {params}")
        
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
        获取支票对手方列表
        
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
            ⚠️ 文档问题：响应字段未在Properties定义
        """
        url = self.config.get_full_url("/money-movements/checks/counterparties")
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
        logger.debug(f"请求Check对手方列表: {params}")
        
        response = self.session.get(url, params=params)
        logger.debug(f"响应状态: {response.status_code}")
        
        return response

    # ==================== 对手方管理接口 ====================
    
    def create_counterparty(
        self,
        name: str,
        type: Union[str, CounterpartyType],
        address1: str,
        assign_account_ids: Optional[List[str]] = None,
        address2: Optional[str] = None,
        state: Optional[str] = None,
        country: Optional[str] = None,
        city: Optional[str] = None,
        bank_account_type: Optional[Union[str, BankAccountType]] = None,
        bank_routing_number: Optional[str] = None,
        bank_name: Optional[str] = None,
        bank_account_owner_name: Optional[str] = None,
        bank_account_number: Optional[str] = None,
        **kwargs
    ) -> requests.Response:
        """
        创建支票对手方
        
        Args:
            name: 对手方名称（必需）
            type: 对手方类型（必需）
            address1: 地址1（必需）
            assign_account_ids: 分配的账户ID列表
            address2: 地址2
            state: 州
            country: 国家
            city: 城市
            bank_account_type: 银行账户类型
            bank_routing_number: 路由号
            bank_name: 银行名称
            bank_account_owner_name: 账户所有人姓名
            bank_account_number: 银行账号
            
        Returns:
            requests.Response: 响应对象
            
        Note:
            ⚠️ 文档问题：
            1. address1标记为required
            2. 其他字段（如bank相关）未标记required或optional
            3. 响应无code包装层
        """
        url = self.config.get_full_url("/money-movements/checks/counterparties")
        
        payload = {
            "name": name,
            "type": str(type) if isinstance(type, CounterpartyType) else type,
            "address1": address1
        }
        
        if assign_account_ids is not None:
            payload["assign_account_ids"] = assign_account_ids
        if address2 is not None:
            payload["address2"] = address2
        if state is not None:
            payload["state"] = state
        if country is not None:
            payload["country"] = country
        if city is not None:
            payload["city"] = city
        if bank_account_type is not None:
            payload["bank_account_type"] = str(bank_account_type) if isinstance(bank_account_type, BankAccountType) else bank_account_type
        if bank_routing_number is not None:
            payload["bank_routing_number"] = bank_routing_number
        if bank_name is not None:
            payload["bank_name"] = bank_name
        if bank_account_owner_name is not None:
            payload["bank_account_owner_name"] = bank_account_owner_name
        if bank_account_number is not None:
            payload["bank_account_number"] = bank_account_number
        
        payload.update(kwargs)
        logger.debug(f"创建Check对手方: name={name}, type={type}")
        
        response = self.session.post(url, json=payload)
        logger.debug(f"响应状态: {response.status_code}")
        
        return response

    # ==================== 支票处理流程 ====================
    
    def scan_check(
        self,
        front_check_image_path: str,
        back_check_image_path: str,
        financial_account_id: str,
        amount: str
    ) -> requests.Response:
        """
        扫描支票（Step 1）
        上传支票正反面图片，系统自动OCR识别routing和account number
        
        Args:
            front_check_image_path: 支票正面图片路径
            back_check_image_path: 支票背面图片路径
            financial_account_id: Financial Account ID（必需）
            amount: 金额（必需）
            
        Returns:
            requests.Response: 响应对象（特殊格式），包含：
                - success: boolean（不是code！）
                - item_identifier: UUID（用于下一步deposit）
                - routing_number: OCR识别的路由号
                - account_number: OCR识别的账号
                
        Note:
            ⚠️ 重要：
            1. 需要multipart/form-data文件上传
            2. 响应格式特殊：使用success字段而不是code
            3. item_identifier必须保存用于deposit
            
            ⚠️ 文件要求：
            - 支持格式：jpeg, png, pdf, tiff
            - 大小限制：未说明
            - 分辨率要求：未说明
        """
        url = self.config.get_full_url("/money-movements/checks/scan")
        
        try:
            files = {
                'front_check_image': open(front_check_image_path, 'rb'),
                'back_check_image': open(back_check_image_path, 'rb')
            }
            data = {
                'financial_account_id': financial_account_id,
                'amount': amount
            }
            
            logger.debug(f"扫描支票: amount={amount}, account={financial_account_id}")
            
            response = self.session.post(url, files=files, data=data)
            logger.debug(f"响应状态: {response.status_code}")
            
            return response
        except FileNotFoundError as e:
            logger.error(f"文件不存在: {e}")
            raise
        except Exception as e:
            logger.error(f"扫描支票失败: {e}", exc_info=True)
            raise

    def submit_deposit(
        self,
        financial_account_id: str,
        amount: str,
        item_identifier: str,
        routing_number: str,
        account_number: str,
        check_date: str,
        counterparty_id: Optional[str] = None,
        memo: Optional[str] = None,
        schedule_date: Optional[str] = None,
        **kwargs
    ) -> requests.Response:
        """
        提交支票存款（Step 2）
        使用Scan返回的item_identifier创建存款交易
        
        Args:
            financial_account_id: Financial Account ID（必需）
            amount: 金额（必需）
            item_identifier: Scan返回的项目标识符（必需）
            routing_number: Scan返回的路由号（必需，可修正）
            account_number: Scan返回的账号（必需，可修正）
            check_date: 支票日期（必需，YYYY-MM-DD）
            counterparty_id: 对手方ID（条件必需：high-risk账户时）
            memo: 备注
            schedule_date: 计划日期（YYYY-MM-DD，今天或未来）
            
        Returns:
            requests.Response: 响应对象
            
        Note:
            ⚠️⚠️⚠️ 真实存款操作，会实际入账，不可撤销
            
            ⚠️ 依赖关系：
            - 必须先调用scan_check()获取item_identifier
            - routing_number和account_number来自scan结果
            - 如果OCR识别错误，可以在此处修正
            
            ⚠️ 文档问题：
            1. 响应无code包装层
            2. amount示例类型不一致（定义string，示例number）
            3. counterparty_id条件说明混乱
        """
        url = self.config.get_full_url("/money-movements/checks/deposit")
        
        payload = {
            "financial_account_id": financial_account_id,
            "amount": amount,
            "item_identifier": item_identifier,
            "routing_number": routing_number,
            "account_number": account_number,
            "check_date": check_date
        }
        
        if counterparty_id is not None:
            payload["counterparty_id"] = counterparty_id
        if memo is not None:
            payload["memo"] = memo
        if schedule_date is not None:
            payload["schedule_date"] = schedule_date
        
        payload.update(kwargs)
        logger.warning(f"⚠️⚠️⚠️ 提交支票存款: {amount} to {financial_account_id}")
        logger.warning("这是真实存款操作，会实际入账，不可撤销！")
        
        response = self.session.post(url, json=payload)
        logger.debug(f"响应状态: {response.status_code}")
        
        return response

    def update_deposit(
        self,
        transaction_id: str,
        account_number: str,
        routing_number: str
    ) -> requests.Response:
        """
        更新支票存款的routing和account number
        用于修正OCR识别错误
        
        Args:
            transaction_id: 交易ID（必需）
            account_number: 修正后的账号（必需）
            routing_number: 修正后的路由号（必需）
            
        Returns:
            requests.Response: 响应对象，包含：
                - code: 业务状态码
                - data: boolean（true表示更新成功）
                
        Note:
            ⚠️ 重要限制：
            - 只能修改routing_number和account_number
            - 不能修改amount、memo等其他字段
            - 一旦approved就不能修改
            
            ⚠️ 文档问题：
            1. 状态限制说明不清（哪些status可以修改？）
            2. 响应过于简单（不返回更新后的详情）
        """
        url = self.config.get_full_url(f"/money-movements/checks/deposit/{transaction_id}")
        
        payload = {
            "account_number": account_number,
            "routing_number": routing_number
        }
        
        logger.debug(f"更新Check存款: transaction={transaction_id}")
        
        response = self.session.patch(url, json=payload)
        logger.debug(f"响应状态: {response.status_code}")
        
        return response

    def download_check_image(self, transaction_id: str) -> requests.Response:
        """
        下载支票图片
        
        Args:
            transaction_id: 交易ID（必需）
            
        Returns:
            requests.Response: 响应对象，包含：
                - front_check_image_url: 正面图片URL
                - back_check_image_url: 背面图片URL
                
        Note:
            ⚠️ 文档问题：
            1. HTTP方法错误（应该用GET不是POST）
            2. 示例中URL为null（说明缺失）
            3. 响应无code包装层
        """
        url = self.config.get_full_url(f"/money-movements/checks/download/{transaction_id}")
        
        logger.debug(f"下载Check图片: transaction={transaction_id}")
        
        # 虽然文档说POST，但下载应该用GET更合理
        # 这里按文档实现POST，但标注问题
        response = self.session.post(url)
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
        计算支票交易费用
        
        Args:
            financial_account_id: Financial Account ID（必需）
            amount: 交易金额（必需）
            same_day: 是否当天处理（默认false）
            
        Returns:
            requests.Response: 响应对象
            
        Note:
            ⚠️ 文档问题：HTTP方法示例错误（POST写成GET）
        """
        url = self.config.get_full_url("/money-movements/checks/fee")
        
        payload = {
            "financial_account_id": financial_account_id,
            "amount": amount,
            "same_day": same_day
        }
        
        payload.update(kwargs)
        logger.debug(f"计算Check费用: amount={amount}")
        
        response = self.session.post(url, json=payload)
        logger.debug(f"响应状态: {response.status_code}")
        
        return response

    # ==================== 辅助方法 ====================
    
    def complete_deposit_flow(
        self,
        front_image_path: str,
        back_image_path: str,
        financial_account_id: str,
        amount: str,
        check_date: str,
        memo: Optional[str] = None,
        schedule_date: Optional[str] = None
    ) -> dict:
        """
        完整的支票存款流程（辅助方法）
        自动执行Scan → Deposit两步流程
        
        Args:
            front_image_path: 支票正面图片路径
            back_image_path: 支票背面图片路径
            financial_account_id: Financial Account ID
            amount: 金额
            check_date: 支票日期
            memo: 备注
            schedule_date: 计划日期
            
        Returns:
            dict: 包含每步结果和最终状态
            
        Note:
            ⚠️ 这会执行真实的存款操作
            测试时建议skip或使用测试账户
        """
        result = {"steps": [], "success": False}
        
        # Step 1: Scan Check
        logger.info("Step 1: 扫描支票...")
        scan_response = self.scan_check(
            front_image_path, 
            back_image_path, 
            financial_account_id, 
            amount
        )
        result["steps"].append({"step": "scan", "response": scan_response})
        
        if scan_response.status_code != 200:
            result["error"] = "Scan failed"
            return result
        
        scan_data = scan_response.json()
        if not scan_data.get("success"):
            result["error"] = "Scan not successful"
            return result
        
        # 获取scan结果
        item_identifier = scan_data.get("item_identifier")
        routing_number = scan_data.get("routing_number")
        account_number = scan_data.get("account_number")
        
        result["scan_result"] = {
            "item_identifier": item_identifier,
            "routing_number": routing_number,
            "account_number": account_number
        }
        
        # Step 2: Submit Deposit
        logger.info("Step 2: 提交存款...")
        deposit_response = self.submit_deposit(
            financial_account_id=financial_account_id,
            amount=amount,
            item_identifier=item_identifier,
            routing_number=routing_number,
            account_number=account_number,
            check_date=check_date,
            memo=memo,
            schedule_date=schedule_date
        )
        result["steps"].append({"step": "deposit", "response": deposit_response})
        
        if deposit_response.status_code == 200:
            result["success"] = True
            result["deposit_result"] = deposit_response.json()
        
        return result

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
    
    def parse_scan_response(self, response: requests.Response) -> dict:
        """
        解析Scan响应（特殊格式：使用success字段）
        """
        if response.status_code != 200:
            return {"error": True, "status_code": response.status_code}
        
        try:
            data = response.json()
            return {
                "error": not data.get("success", False),
                "success": data.get("success", False),
                "item_identifier": data.get("item_identifier"),
                "routing_number": data.get("routing_number"),
                "account_number": data.get("account_number")
            }
        except Exception as e:
            logger.error(f"解析Scan响应失败: {e}", exc_info=True)
            return {"error": True, "message": str(e)}
