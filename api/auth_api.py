import requests
from config.config import config

class AuthAPI:
    """
    登录认证 API 封装
    严格遵守 API Object 模式
    """
    def __init__(self):
        self.base_url = config.base_url
        self.auth_data = config.auth_data

    def get_token(self):
        """
        获取 OAuth2 Token
        注意：参数强制要求放在 URL Query 中
        """
        url = f"{self.base_url}/api/v1/auth/{self.auth_data['tenant_id']}/oauth2/token"
        
        # 定义查询参数
        params = {
            "grant_type": "client_credentials",
            "user_id": self.auth_data["user_id"],
            "Jmeter-Test": "Jmeter-Test"
        }
        
        # 定义请求头
        headers = {
            "Content-Type": "application/json; charset=utf-8",
            "Authorization": f"Basic {self.auth_data['basic_auth']}"
        }
        
        # 发送 POST 请求，参数通过 params 传递（即 URL Query）
        response = requests.post(url, params=params, headers=headers)
        
        # 返回响应对象
        return response

# 实例化
auth_api = AuthAPI()
