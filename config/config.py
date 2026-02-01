import os

class Config:
    """
    多环境配置管理类
    通过环境变量 ENV 切换环境，默认为 DEV
    """
    ENV = os.getenv("ENV", "DEV").upper()

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
        return self.current_config["base_url"]

    @property
    def db_config(self):
        return self.current_config["db_config"]

    @property
    def auth_data(self):
        return self.current_config["auth"]

# 全局配置实例
config = Config()
