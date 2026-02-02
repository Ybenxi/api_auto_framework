"""
多环境、多 Core 配置管理类
通过环境变量 ENV 切换环境（DEV/UAT），通过 CORE 切换业务核心
"""
import os
from data.enums import CoreType


class Config:
    """
    多环境、多 Core 配置管理类
    - ENV: 环境变量，控制 DEV/UAT 环境切换
    - CORE: Core 变量，控制不同业务核心的 API 路径
    """
    ENV = os.getenv("ENV", "DEV").upper()
    CORE = os.getenv("CORE", CoreType.AUSTIN_CAPITAL.value)

    # 环境基础配置
    BASE_CONFIG = {
        "DEV": {
            "base_url": "https://api-dev.accelerationcloud.info",
            "db_config": {
                "host": "localhost",
                "port": 5432,
                "user": "dev_user",
                "password": "dev_password",
                "database": "dev_db"
            },
            "auth": {
                "tenant_id": "1713381612826DC8Ww",
                "user_id": "1713381666843PfKuz",
                "basic_auth": "TTZ6dFNrMVRrVXlubkgrWFZCOVhndnl6dVhoRkgvQUlvZ29LSzhoTHFrVT06UTVwSi9kNnROUDBiT2h1WVZXcnpRaGdqdUxaZG03Y2VsTEhGTmxRZHNhZW5vemM3Y1pROHZBMElScFZlWEZmVUV1TTRXZXJvakhsNC84VmIzZkdLS3NFMnRKMDBTSWtjbzlmQlRMU2U1TWs9"
            }
        },
        "UAT": {
            "base_url": "https://api-uat.accelerationcloud.info",
            "db_config": {
                "host": "uat-db.host",
                "port": 5432,
                "user": "uat_user",
                "password": "uat_password",
                "database": "uat_db"
            },
            "auth": {
                "tenant_id": "uat_tenant_id",
                "user_id": "uat_user_id",
                "basic_auth": "uat_basic_auth_string"
            }
        }
    }

    @property
    def current_config(self):
        """获取当前环境的配置"""
        return self.BASE_CONFIG.get(self.ENV, self.BASE_CONFIG["DEV"])

    @property
    def base_url(self):
        """获取基础 URL"""
        return self.current_config["base_url"]

    @property
    def db_config(self):
        """获取数据库配置"""
        return self.current_config["db_config"]

    @property
    def auth_data(self):
        """获取认证配置"""
        return self.current_config["auth"]

    @property
    def core(self):
        """获取当前 Core"""
        return self.CORE

    def get_api_path(self, endpoint: str) -> str:
        """
        构建完整的 API 路径
        
        Args:
            endpoint: 接口端点，例如 "/accounts" 或 "/accounts/{id}"
            
        Returns:
            str: 完整的 API 路径，例如 "/api/v1/cores/actc/accounts"
            
        Example:
            config.get_api_path("/accounts")
            # 返回: "/api/v1/cores/actc/accounts"
        """
        # 移除 endpoint 开头的斜杠（如果有）
        endpoint = endpoint.lstrip("/")
        return f"/api/v1/cores/{self.core}/{endpoint}"

    def get_full_url(self, endpoint: str) -> str:
        """
        构建完整的 URL（包含域名）
        
        Args:
            endpoint: 接口端点，例如 "/accounts"
            
        Returns:
            str: 完整的 URL
            
        Example:
            config.get_full_url("/accounts")
            # 返回: "https://api-dev.accelerationcloud.info/api/v1/cores/actc/accounts"
        """
        api_path = self.get_api_path(endpoint)
        return f"{self.base_url}{api_path}"


# 全局配置实例
config = Config()
