"""
User Sign Up 相关 API 封装
提供用户注册的完整流程：邮箱验证、短信验证、创建账户
遵循 API Object 模式，提供灵活的参数化接口

⚠️ 文档问题：
1. token流转链说明不清晰（5步流程）
2. has_idp_user描述不完整
3. 条件必需字段规则不清（"must be left empty"含义不明）
4. client_type枚举值有空格（Individual Client）
5. password加密说明不够详细
"""
import requests
from typing import Optional, Union
from config.config import config
from data.enums import ClientType, RecoveryQuestion
from utils.logger import logger


class UserSignUpAPI:
    """
    User Sign Up API 封装类
    包含用户注册的完整流程：邮箱验证、短信验证、创建账户
    
    注册流程：
    1. initiate_email_verification() → 获取token1
    2. verify_email_code(token1) → 获取token2
    3. send_sms_verification(token2) → 获取token3
    4. verify_sms_code(token3) → 获取token4 + has_idp_user
    5. create_unifi_user(token4) → 创建用户
    """
    def __init__(self, client_id: str, session: Optional[requests.Session] = None):
        """
        初始化 UserSignUpAPI
        
        Args:
            client_id: Client ID（必需，用于Header）
            session: requests.Session 对象
            
        Note:
            ⚠️ 此模块需要Client-Id header，与其他模块不同
        """
        self.base_url = config.base_url
        self.config = config
        self.session = session or requests.Session()
        self.client_id = client_id
        
        # 设置默认headers
        self.session.headers.update({
            "Client-Id": self.client_id
        })

    # ==================== 邮箱验证流程 ====================
    
    def initiate_email_verification(self, email: str) -> requests.Response:
        """
        发起邮箱验证（Step 1）
        发送验证码到指定邮箱
        
        Args:
            email: 邮箱地址
            
        Returns:
            requests.Response: 响应对象，包含：
                - code: 业务状态码
                - data: token（用于下一步verify_email）
                - error_message: 错误信息（如邮箱已存在）
                
        Note:
            ⚠️ 文档问题：
            1. 邮箱已存在时的处理未说明
            2. data返回的token应明确说明是enroll_token
        """
        url = self.config.get_full_url("/user/auth/sign-up/email")
        
        payload = {"email": email}
        logger.debug(f"发起邮箱验证: {email}")
        
        response = self.session.post(url, json=payload)
        logger.debug(f"响应状态: {response.status_code}")
        
        return response

    def verify_email_code(self, passcode: str, enroll_token: str) -> requests.Response:
        """
        验证邮箱验证码（Step 2）
        
        Args:
            passcode: 验证码（用户从邮件中获取）
            enroll_token: Step 1返回的token
            
        Returns:
            requests.Response: 响应对象，包含：
                - code: 业务状态码
                - data: 新token（用于send_sms）
                
        Note:
            ⚠️ 验证码格式未说明（示例是6位数字）
        """
        url = self.config.get_full_url("/user/auth/sign-up/email/verification")
        
        payload = {
            "passcode": passcode,
            "enroll_token": enroll_token
        }
        logger.debug(f"验证邮箱验证码: passcode={passcode}")
        
        response = self.session.post(url, json=payload)
        logger.debug(f"响应状态: {response.status_code}")
        
        return response

    # ==================== 短信验证流程 ====================
    
    def send_sms_verification(self, phone: str, enroll_token: str) -> requests.Response:
        """
        发送短信验证码（Step 3）
        
        Args:
            phone: 手机号码（E.164格式，仅支持美国号码）
            enroll_token: Step 2返回的token
            
        Returns:
            requests.Response: 响应对象，包含：
                - code: 业务状态码
                - data: token（用于verify_sms）
                
        Note:
            ⚠️ 文档问题：
            1. 示例+11234567890应为+1234567890
            2. 仅支持美国号码，但未说明其他国家如何处理
        """
        url = self.config.get_full_url("/user/auth/sign-up/sms")
        
        payload = {
            "phone": phone,
            "enroll_token": enroll_token
        }
        logger.debug(f"发送短信验证码: {phone}")
        
        response = self.session.post(url, json=payload)
        logger.debug(f"响应状态: {response.status_code}")
        
        return response

    def verify_sms_code(self, passcode: str, enroll_token: str) -> requests.Response:
        """
        验证短信验证码（Step 4）
        
        Args:
            passcode: 验证码（用户从短信中获取）
            enroll_token: Step 3返回的token
            
        Returns:
            requests.Response: 响应对象，包含：
                - code: 业务状态码
                - data: 对象，包含：
                    - enroll_token: 新token（用于create_user）
                    - has_idp_user: 用户是否已存在于IdP
                    - client_type: 客户类型
                    - company_name: 公司名称
                    - first_name: 名
                    - last_name: 姓
                    
        Note:
            ⚠️ 重要：has_idp_user决定Step 5是否需要密码和安全问题
            - has_idp_user=true: 不需要密码和安全问题
            - has_idp_user=false: 需要密码和安全问题
        """
        url = self.config.get_full_url("/user/auth/sign-up/sms/verification")
        
        payload = {
            "passcode": passcode,
            "enroll_token": enroll_token
        }
        logger.debug(f"验证短信验证码: passcode={passcode}")
        
        response = self.session.post(url, json=payload)
        logger.debug(f"响应状态: {response.status_code}")
        
        return response

    # ==================== 创建用户 ====================
    
    def create_unifi_user(
        self,
        enroll_token: str,
        last_name: str,
        first_name: str,
        email: str,
        phone: str,
        client_type: Union[str, ClientType],
        company_name: Optional[str] = None,
        encoded_password: Optional[str] = None,
        recovery_question: Optional[Union[str, RecoveryQuestion]] = None,
        recovery_answer: Optional[str] = None,
        **kwargs
    ) -> requests.Response:
        """
        创建UniFi用户（Step 5）
        
        Args:
            enroll_token: Step 4返回的token
            last_name: 姓（必需）
            first_name: 名（必需）
            email: 邮箱（必需）
            phone: 手机号（必需）
            client_type: 客户类型（Individual Client或Business）
            company_name: 公司名称（client_type=Business时必需，最多80字符）
            encoded_password: RSA加密的密码（has_idp_user=false时必需）
            recovery_question: 安全问题（has_idp_user=false时必需）
            recovery_answer: 安全答案（has_idp_user=false时必需，4-50字符）
            **kwargs: 其他可选参数
            
        Returns:
            requests.Response: 响应对象，包含：
                - code: 业务状态码
                - data: boolean（true表示创建成功）
                
        Note:
            ⚠️ 条件必需字段规则：
            1. company_name: client_type='Business'时必需
            2. encoded_password, recovery_question, recovery_answer: 
               has_idp_user=false时必需，true时"must be left empty"
            
            ⚠️ 加密要求：
            - 密码需要RSA + PKCS1Padding加密
            - Base64编码
            - 测试建议skip（需要加密实现）
        """
        url = self.config.get_full_url("/user/auth/sign-up/unifi-user")
        
        payload = {
            "enroll_token": enroll_token,
            "last_name": last_name,
            "first_name": first_name,
            "email": email,
            "phone": phone,
            "client_type": str(client_type) if isinstance(client_type, ClientType) else client_type
        }
        
        if company_name is not None:
            payload["company_name"] = company_name
        if encoded_password is not None:
            payload["encoded_password"] = encoded_password
        if recovery_question is not None:
            payload["recovery_question"] = str(recovery_question) if isinstance(recovery_question, RecoveryQuestion) else recovery_question
        if recovery_answer is not None:
            payload["recovery_answer"] = recovery_answer
        
        payload.update(kwargs)
        logger.debug(f"创建UniFi用户: email={email}, client_type={client_type}")
        
        response = self.session.post(url, json=payload)
        logger.debug(f"响应状态: {response.status_code}")
        
        return response

    # ==================== 辅助方法 ====================
    
    def complete_signup_flow(
        self,
        email: str,
        phone: str,
        email_passcode: str,
        sms_passcode: str,
        first_name: str,
        last_name: str,
        client_type: Union[str, ClientType],
        company_name: Optional[str] = None,
        encoded_password: Optional[str] = None,
        recovery_question: Optional[Union[str, RecoveryQuestion]] = None,
        recovery_answer: Optional[str] = None
    ) -> dict:
        """
        完整的注册流程（辅助方法）
        自动执行5个步骤
        
        Args:
            email: 邮箱地址
            phone: 手机号码
            email_passcode: 邮箱验证码
            sms_passcode: 短信验证码
            first_name: 名
            last_name: 姓
            client_type: 客户类型
            company_name: 公司名称（Business类型时必需）
            encoded_password: 加密密码（has_idp_user=false时必需）
            recovery_question: 安全问题（has_idp_user=false时必需）
            recovery_answer: 安全答案（has_idp_user=false时必需）
            
        Returns:
            dict: 包含每个步骤的响应和最终结果
            
        Note:
            此方法用于完整流程测试，实际测试时大部分会skip
        """
        result = {"steps": [], "success": False}
        
        # Step 1: 发起邮箱验证
        step1 = self.initiate_email_verification(email)
        result["steps"].append({"step": 1, "response": step1})
        if step1.status_code != 200 or step1.json().get("code") != 200:
            return result
        
        token1 = step1.json().get("data")
        
        # Step 2: 验证邮箱码
        step2 = self.verify_email_code(email_passcode, token1)
        result["steps"].append({"step": 2, "response": step2})
        if step2.status_code != 200 or step2.json().get("code") != 200:
            return result
        
        token2 = step2.json().get("data")
        
        # Step 3: 发送短信验证
        step3 = self.send_sms_verification(phone, token2)
        result["steps"].append({"step": 3, "response": step3})
        if step3.status_code != 200 or step3.json().get("code") != 200:
            return result
        
        token3 = step3.json().get("data")
        
        # Step 4: 验证短信码
        step4 = self.verify_sms_code(sms_passcode, token3)
        result["steps"].append({"step": 4, "response": step4})
        if step4.status_code != 200 or step4.json().get("code") != 200:
            return result
        
        step4_data = step4.json().get("data", {})
        token4 = step4_data.get("enroll_token")
        has_idp_user = step4_data.get("has_idp_user", False)
        
        result["has_idp_user"] = has_idp_user
        
        # Step 5: 创建用户
        step5 = self.create_unifi_user(
            enroll_token=token4,
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            client_type=client_type,
            company_name=company_name,
            encoded_password=encoded_password if not has_idp_user else None,
            recovery_question=recovery_question if not has_idp_user else None,
            recovery_answer=recovery_answer if not has_idp_user else None
        )
        result["steps"].append({"step": 5, "response": step5})
        
        if step5.status_code == 200 and step5.json().get("code") == 200:
            result["success"] = True
        
        return result
