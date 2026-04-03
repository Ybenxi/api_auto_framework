"""
多环境、多 Core 配置管理类
通过环境变量 ENV 切换环境（DEV/UAT），通过 CORE 切换业务核心
支持从 .env 文件加载配置
"""
import os
import base64
from pathlib import Path
from dotenv import load_dotenv
from data.enums import CoreType

# 加载 .env 文件（如果存在）
env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)


class Config:
    """
    多环境、多 Core 配置管理类
    - ENV: 环境变量，控制 DEV/UAT 环境切换
    - CORE: Core 变量，控制不同业务核心的 API 路径
    """
    ENV = os.getenv("ENV", "DEV").upper()
    CORE = os.getenv("CORE", CoreType.AUSTIN_CAPITAL.value)

    # 环境基础配置（默认值，可被 .env 覆盖）
    BASE_CONFIG = {
        "DEV": {
            "base_url": os.getenv("BASE_URL", "https://api-dev.accelerationcloud.info"),
            "db_config": {
                "host": os.getenv("DB_HOST", "localhost"),
                "port": int(os.getenv("DB_PORT", "5432")),
                "user": os.getenv("DB_USER", "dev_user"),
                "password": os.getenv("DB_PASSWORD", "dev_password"),
                "database": os.getenv("DB_NAME", "dev_db")
            },
            "auth": {
                "tenant_id": os.getenv("TENANT_ID", "1713381612826DC8Ww"),
                "user_id": os.getenv("USER_ID", "1713381666843PfKuz"),
                "basic_auth": os.getenv("BASIC_AUTH", "TTZ6dFNrMVRrVXlubkgrWFZCOVhndnl6dVhoRkgvQUlvZ29LSzhoTHFrVT06UTVwSi9kNnROUDBiT2h1WVZXcnpRaGdqdUxaZG03Y2VsTEhGTmxRZHNhZW5vemM3Y1pROHZBMElScFZlWEZmVUV1TTRXZXJvakhsNC84VmIzZkdLS3NFMnRKMDBTSWtjbzlmQlRMU2U1TWs9")
            }
        },
        "UAT": {
            "base_url": os.getenv("BASE_URL", "https://api-uat.accelerationcloud.info"),
            "db_config": {
                "host": os.getenv("DB_HOST", "uat-db.host"),
                "port": int(os.getenv("DB_PORT", "5432")),
                "user": os.getenv("DB_USER", "uat_user"),
                "password": os.getenv("DB_PASSWORD", "uat_password"),
                "database": os.getenv("DB_NAME", "uat_db")
            },
            "auth": {
                "tenant_id": os.getenv("TENANT_ID", "uat_tenant_id"),
                "user_id": os.getenv("USER_ID", "uat_user_id"),
                "basic_auth": os.getenv("BASIC_AUTH", "uat_basic_auth_string")
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
        auth = dict(self.current_config["auth"])
        # 新模型兼容：account_id/client_id/secret/core/encryption_key
        account_id = os.getenv("ACCOUNT_ID", auth.get("account_id", auth.get("tenant_id", "")))
        client_id = os.getenv("CLIENT_ID", auth.get("client_id", ""))
        client_secret = os.getenv("CLIENT_SECRET", auth.get("secret", ""))
        encryption_key = os.getenv("ENCRYPTION_KEY", auth.get("encryption_key", ""))

        auth["account_id"] = account_id
        auth["tenant_id"] = account_id or auth.get("tenant_id", "")
        auth["client_id"] = client_id
        auth["secret"] = client_secret
        auth["encryption_key"] = encryption_key

        basic_auth = os.getenv("BASIC_AUTH", auth.get("basic_auth", ""))
        if (not basic_auth) and client_id and client_secret:
            basic_auth = base64.b64encode(f"{client_id}:{client_secret}".encode("utf-8")).decode("utf-8")
        auth["basic_auth"] = basic_auth
        auth["user_id"] = os.getenv("USER_ID", auth.get("user_id", ""))
        return auth

    @property
    def core(self):
        """获取当前 Core"""
        return os.getenv("CORE", self.CORE)
    
    def get_env(self) -> str:
        """获取当前环境标识"""
        return self.ENV

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
    
    def get_db_config(self, key: str, default: str = None) -> str:
        """
        获取数据库配置项
        
        Args:
            key: 配置键名（如 "DB_HOST", "DB_PORT" 等）
            default: 默认值
        
        Returns:
            配置值
        
        Example:
            config.get_db_config("DB_HOST")
            # 返回: "fta-database-dev.cda9xsygtbs2.us-east-1.rds.amazonaws.com"
        """
        # 映射环境变量名到 db_config 字典的键
        key_mapping = {
            "DB_HOST": "host",
            "DB_PORT": "port",
            "DB_USER": "user",
            "DB_PASSWORD": "password",
            "DB_NAME": "database"
        }
        
        db_key = key_mapping.get(key)
        if db_key:
            value = self.db_config.get(db_key, default)
            return str(value) if value is not None else default
        
        return default


# 全局配置实例
config = Config()
