"""
Identity Security 相关 API 封装
包含用户个人资料、MFA、密码修改、登出等安全功能
"""
import requests
from typing import Optional, List, Dict, Any
from config.config import config


class IdentitySecurityAPI:
    """
    Identity Security 管理 API 封装类
    包含用户个人资料管理、MFA管理、安全操作等
    """
    def __init__(self, session: Optional[requests.Session] = None):
        """
        初始化 IdentitySecurityAPI
        
        Args:
            session: requests.Session 对象，如果传入则使用该 session 保持认证状态
        """
        self.base_url = config.base_url
        self.config = config
        self.session = session or requests.Session()

    # ==================== Profile 相关 ====================
    
    def get_user_profile(self) -> requests.Response:
        """
        获取当前用户的个人资料
        
        Returns:
            requests.Response: 响应对象
            
        Example:
            response = identity_api.get_user_profile()
            if response.status_code == 200:
                profile = response.json()['data']
                print(f"User: {profile['first_name']} {profile['last_name']}")
        """
        url = self.config.get_full_url("/identity-security/profile")
        response = self.session.get(url)
        return response

    def update_user_profile(self, profile_data: dict) -> requests.Response:
        """
        更新用户个人资料
        
        Args:
            profile_data: 更新数据字典，可包含以下字段：
                - first_name: 名
                - last_name: 姓
                - middle_name: 中间名
                - maiden_name: 娘家姓
                - suffix: 后缀
                - birth_date: 生日 (YYYY-MM-DD)
                - phone: 电话 (E.164格式)
                - mobile_phone: 手机 (E.164格式)
                - home_phone: 家庭电话
                - work_phone: 工作电话
                - fax: 传真
                - gender: 性别 (Male/Female)
                - permanent_address, permanent_city, permanent_state, etc.: 永久地址
                - mailing_street, mailing_city, mailing_state, etc.: 邮寄地址
                - description: 描述
                
        Returns:
            requests.Response: 响应对象
            
        Example:
            profile_data = {
                "first_name": "John",
                "last_name": "Doe",
                "phone": "+14155552671"
            }
            response = identity_api.update_user_profile(profile_data)
        """
        url = self.config.get_full_url("/identity-security/profile")
        response = self.session.patch(url, json=profile_data)
        return response

    def upload_user_avatar(self, file_path: str) -> requests.Response:
        """
        上传用户头像
        
        Args:
            file_path: 头像文件路径
            
        Returns:
            requests.Response: 响应对象，返回头像 URL
            
        Example:
            response = identity_api.upload_user_avatar("/path/to/avatar.png")
            if response.status_code == 200:
                avatar_url = response.text
                print(f"Avatar URL: {avatar_url}")
        """
        url = self.config.get_full_url("/identity-security/profile/avatar")
        with open(file_path, 'rb') as f:
            files = {'file': f}
            response = self.session.post(url, files=files)
        return response

    # ==================== MFA 相关 ====================
    
    def list_enrolled_factors(self) -> requests.Response:
        """
        列出当前账户已注册的 MFA 因子
        
        Returns:
            requests.Response: 响应对象
            
        Example:
            response = identity_api.list_enrolled_factors()
            if response.status_code == 200:
                factors = response.json()['data']
                for factor in factors:
                    print(f"Factor: {factor['factor_type']} - {factor['status']}")
        """
        url = self.config.get_full_url("/identity-security/profile/factors")
        response = self.session.get(url)
        return response

    def enroll_factor(self, factor_type: str, profile: dict) -> requests.Response:
        """
        注册新的 MFA 因子
        
        Args:
            factor_type: 因子类型 (如 "sms", "email")
            profile: 因子配置，如 {"phone_number": "+447911123456"}
            
        Returns:
            requests.Response: 响应对象，返回 factor_id
            
        Example:
            response = identity_api.enroll_factor(
                factor_type="sms",
                profile={"phone_number": "+14155552671"}
            )
            if response.status_code == 200:
                factor_id = response.json()['data']
                print(f"Factor ID: {factor_id}")
        """
        url = self.config.get_full_url("/identity-security/profile/factors")
        data = {
            "factor_type": factor_type,
            "profile": profile
        }
        response = self.session.post(url, json=data)
        return response

    def delete_factors(self, factor_ids: List[str]) -> requests.Response:
        """
        删除一个或多个 MFA 因子
        
        Args:
            factor_ids: 因子 ID 列表
            
        Returns:
            requests.Response: 响应对象
            
        Example:
            response = identity_api.delete_factors(["factor_id_1", "factor_id_2"])
            if response.status_code == 200:
                success = response.json()['data']
                print(f"Delete success: {success}")
        """
        url = self.config.get_full_url("/identity-security/profile/factors")
        data = [{"id": fid} for fid in factor_ids]
        response = self.session.delete(url, json=data)
        return response

    def activate_factor(self, factor_id: str, pass_code: str) -> requests.Response:
        """
        激活 MFA 因子（使用验证码）
        
        Args:
            factor_id: 因子 ID
            pass_code: 验证码
            
        Returns:
            requests.Response: 响应对象
            
        Example:
            response = identity_api.activate_factor("factor_id", "242143")
            if response.status_code == 200:
                success = response.json()['data']
                print(f"Activation success: {success}")
        """
        url = self.config.get_full_url(f"/identity-security/profile/factors/{factor_id}")
        data = {"pass_code": pass_code}
        response = self.session.post(url, json=data)
        return response

    def send_mfa_challenge(self, factor_id: str) -> requests.Response:
        """
        发送 MFA 验证挑战（发送验证码）
        
        Args:
            factor_id: 因子 ID
            
        Returns:
            requests.Response: 响应对象
            
        Example:
            response = identity_api.send_mfa_challenge("smsmcphx2yXep7Zkw1d7")
            if response.status_code == 200:
                print("验证码已发送")
        """
        url = self.config.get_full_url("/identity-security/mfa/send")
        data = {"factor_id": factor_id}
        response = self.session.post(url, json=data)
        return response

    def verify_mfa(self, factor_id: str, pass_code: str) -> requests.Response:
        """
        验证 MFA（验证码验证）
        
        Args:
            factor_id: 因子 ID
            pass_code: 验证码
            
        Returns:
            requests.Response: 响应对象
            
        Example:
            response = identity_api.verify_mfa("factor_id", "533997")
            if response.status_code == 200:
                print("MFA 验证成功")
        """
        url = self.config.get_full_url("/identity-security/mfa/verification")
        data = {
            "factor_id": factor_id,
            "pass_code": pass_code
        }
        response = self.session.post(url, json=data)
        return response

    # ==================== 安全操作 ====================
    
    def change_password(self, encoded_old_password: str, encoded_new_password: str) -> requests.Response:
        """
        修改密码
        
        Args:
            encoded_old_password: RSA 加密的旧密码（Base64编码）
            encoded_new_password: RSA 加密的新密码（Base64编码）
            
        Returns:
            requests.Response: 响应对象
            
        Example:
            response = identity_api.change_password(
                encoded_old_password="QqNLystn...",
                encoded_new_password="QqNLystn..."
            )
            if response.status_code == 200:
                success = response.json()['data']
                print(f"Password changed: {success}")
        """
        url = self.config.get_full_url("/identity-security/change-password")
        data = {
            "encoded_old_password": encoded_old_password,
            "encoded_new_password": encoded_new_password
        }
        response = self.session.post(url, json=data)
        return response

    def logout(self) -> requests.Response:
        """
        登出并清除 access token
        
        Returns:
            requests.Response: 响应对象
            
        Example:
            response = identity_api.logout()
            if response.status_code == 200:
                success = response.json()['data']
                print(f"Logout success: {success}")
        """
        url = self.config.get_full_url("/identity-security/logout")
        response = self.session.post(url)
        return response

    def delete_user(self) -> requests.Response:
        """
        删除当前用户
        
        ⚠️ 警告：这是破坏性操作，会永久删除用户数据
        
        Returns:
            requests.Response: 响应对象
            
        Example:
            response = identity_api.delete_user()
            if response.status_code == 200:
                success = response.json()['data']
                print(f"User deleted: {success}")
        """
        url = self.config.get_full_url("/identity-security/user")
        response = self.session.delete(url)
        return response

    # ==================== 响应解析辅助方法 ====================
    
    def parse_standard_response(self, response: requests.Response) -> dict:
        """
        解析标准响应格式 {code: 200, data: ...}
        
        Args:
            response: requests.Response 对象
            
        Returns:
            dict: 包含 error 标识和数据
            
        Example:
            response = identity_api.get_user_profile()
            parsed = identity_api.parse_standard_response(response)
            if not parsed['error']:
                user_data = parsed['data']
        """
        if response.status_code != 200:
            return {
                "error": True,
                "status_code": response.status_code,
                "message": response.text
            }
        
        try:
            body = response.json()
            
            # 检查业务错误码
            if body.get("code") != 200:
                return {
                    "error": True,
                    "code": body.get("code"),
                    "message": body.get("error_message", "Unknown error")
                }
            
            return {
                "error": False,
                "code": body.get("code"),
                "data": body.get("data")
            }
        except Exception as e:
            return {
                "error": True,
                "message": f"Failed to parse response: {str(e)}",
                "raw_response": response.text
            }
