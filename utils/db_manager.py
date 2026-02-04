import psycopg2
from config.config import config
from utils.logger import logger

class DBManager:
    """
    PostgreSQL 数据库管理类
    提供连接建立、查询执行和连接关闭功能
    """
    def __init__(self):
        self.conn_info = config.db_config
        self.connection = None
        self.cursor = None

    def connect(self):
        """建立数据库连接"""
        try:
            self.connection = psycopg2.connect(
                host=self.conn_info["host"],
                port=self.conn_info["port"],
                user=self.conn_info["user"],
                password=self.conn_info["password"],
                database=self.conn_info["database"]
            )
            self.cursor = self.connection.cursor()
            logger.info("Successfully connected to the database.")
        except Exception as e:
            logger.info(f"Error connecting to database: {e}")
            raise

    def execute_query(self, sql, params=None):
        """执行 SQL 查询并返回结果"""
        if not self.cursor:
            self.connect()
        try:
            self.cursor.execute(sql, params)
            if sql.strip().upper().startswith("SELECT"):
                return self.cursor.fetchall()
            self.connection.commit()
            return self.cursor.rowcount
        except Exception as e:
            self.connection.rollback()
            logger.info(f"Error executing query: {e}")
            raise

    def close(self):
        """关闭数据库连接和游标"""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
            logger.info("Database connection closed.")

# 单例模式，方便全局调用
db = DBManager()
