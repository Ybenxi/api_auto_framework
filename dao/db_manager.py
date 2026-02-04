"""
数据库连接管理器
基于 SQLAlchemy 实现单例模式连接池
"""
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from contextlib import contextmanager
from typing import List, Dict, Any, Optional
from utils.logger import logger


class DBManager:
    """
    数据库管理器（单例模式）
    提供统一的数据库操作接口
    """
    _instance = None
    _engine = None
    _session_factory = None

    def __new__(cls, *args, **kwargs):
        """单例模式：确保全局只有一个实例"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, db_config: Optional[Dict[str, Any]] = None):
        """
        初始化数据库连接
        
        Args:
            db_config: 数据库配置字典，包含 host, port, user, password, database
        """
        # 避免重复初始化
        if self._engine is not None:
            return
        
        if db_config is None:
            logger.warning("未提供数据库配置，DBManager 初始化跳过")
            return
        
        try:
            # 构建连接字符串（PostgreSQL）
            db_url = (
                f"postgresql+psycopg2://{db_config['user']}:{db_config['password']}"
                f"@{db_config['host']}:{db_config['port']}/{db_config['database']}"
            )
            
            # 创建引擎（带连接池）
            self._engine = create_engine(
                db_url,
                poolclass=QueuePool,
                pool_size=5,  # 连接池大小
                max_overflow=10,  # 最大溢出连接数
                pool_timeout=30,  # 连接超时时间（秒）
                pool_recycle=3600,  # 连接回收时间（秒）
                echo=False  # 不打印 SQL 日志
            )
            
            # 创建会话工厂
            self._session_factory = sessionmaker(bind=self._engine)
            
            logger.info(f"数据库连接池初始化成功: {db_config['host']}:{db_config['port']}/{db_config['database']}")
        
        except Exception as e:
            logger.error(f"数据库连接池初始化失败: {e}", exc_info=True)
            raise

    @contextmanager
    def get_session(self) -> Session:
        """
        获取数据库会话（上下文管理器）
        
        Usage:
            with db_manager.get_session() as session:
                result = session.execute(...)
        """
        if self._session_factory is None:
            raise RuntimeError("数据库未初始化，无法获取 session")
        
        session = self._session_factory()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"数据库操作失败，已回滚: {e}", exc_info=True)
            raise
        finally:
            session.close()

    def execute_query(self, sql: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        执行查询语句
        
        Args:
            sql: SQL 查询语句
            params: 查询参数（可选）
        
        Returns:
            查询结果列表（字典格式）
        """
        if self._engine is None:
            logger.warning("数据库未初始化，跳过查询")
            return []
        
        try:
            with self.get_session() as session:
                result = session.execute(text(sql), params or {})
                rows = result.fetchall()
                
                # 转换为字典列表
                columns = result.keys()
                data = [dict(zip(columns, row)) for row in rows]
                
                logger.debug(f"查询成功，返回 {len(data)} 行数据")
                return data
        
        except Exception as e:
            logger.error(f"查询失败: {sql}, 参数: {params}, 错误: {e}", exc_info=True)
            raise

    def execute_update(self, sql: str, params: Optional[Dict[str, Any]] = None) -> int:
        """
        执行更新/删除语句
        
        Args:
            sql: SQL 更新/删除语句
            params: 查询参数（可选）
        
        Returns:
            受影响的行数
        """
        if self._engine is None:
            logger.warning("数据库未初始化，跳过更新")
            return 0
        
        try:
            with self.get_session() as session:
                result = session.execute(text(sql), params or {})
                affected_rows = result.rowcount
                
                logger.debug(f"更新成功，影响 {affected_rows} 行")
                return affected_rows
        
        except Exception as e:
            logger.error(f"更新失败: {sql}, 参数: {params}, 错误: {e}", exc_info=True)
            raise

    def close_connection(self):
        """
        关闭数据库连接池
        """
        if self._engine is not None:
            self._engine.dispose()
            logger.info("数据库连接池已关闭")
            self._engine = None
            self._session_factory = None

    def __del__(self):
        """析构函数：确保连接被关闭"""
        self.close_connection()
