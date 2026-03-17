"""
日志系统配置模块
基于 loguru 实现双输出：控制台（INFO）+ 文件（DEBUG）
与 pytest capture 完全兼容
"""
import sys
import os
from loguru import logger
from pathlib import Path


# 移除默认的 logger 配置
logger.remove()

# 获取项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
LOGS_DIR = PROJECT_ROOT / "logs"

# 确保 logs 目录存在
LOGS_DIR.mkdir(exist_ok=True)

# 配置1: 控制台输出（INFO 级别，彩色格式）
logger.add(
    sys.stderr,  # 使用 stderr 以兼容 pytest capture
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="INFO",
    colorize=True,
    backtrace=False,
    diagnose=False
)

# 配置2: 文件输出（DEBUG 级别，按天切割）
logger.add(
    str(LOGS_DIR / "test_{time:YYYY-MM-DD}.log"),
    format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - {message}",
    level="DEBUG",
    rotation="00:00",  # 每天0点切割
    retention="90 days",  # 保留90天
    compression="zip",  # 压缩旧日志
    encoding="utf-8",
    backtrace=True,
    diagnose=True
)

# 导出全局 logger 实例
__all__ = ["logger"]
